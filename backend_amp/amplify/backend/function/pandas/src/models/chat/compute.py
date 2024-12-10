from shared.models.interfaces import ChatInput as Input, Output
from shared.db.chat import get_histories_collection
from shared.helpers.openai import GPT_Client
from models.chat.embedder import Embedder
from shared.models.common import Common
from openai import RateLimitError
from datetime import datetime
import time


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.common = Common()
        self.embedder = Embedder(self.input.context)
        self.histories_collection = get_histories_collection()

        self.history_id = None
        self.now_date = self.get_now_date()
        self.message_history = self.determine_history()

    def get_now_date(self) -> datetime:
        now_date = Common.get_current_utc_time()
        now_date = now_date.replace(hour=0, minute=0, second=0, microsecond=0)
        return now_date

    def determine_history(self) -> list:
        query = {'phoneNumber': self.input.phoneNumber,
                 'createdAt': {'$gte': self.now_date}, 'context': self.input.context}
        history = self.histories_collection.find_one(query)
        if history:
            self.history_id = history['_id']
            return history['history']

        default_history = [
            {"role": "system", "content": "You are a helpful assistant."}]
        if self.input.system_message:
            default_history[0]['content'] = self.input.system_message
        return default_history

    def update_history(self, role: str, content: str) -> None:
        self.message_history.append({"role": role, "content": content})
        return self.message_history

    def save_history(self) -> None:
        query = {'phoneNumber': self.input.phoneNumber,
                 'createdAt': {'$gte': self.now_date}, 'context': self.input.context}
        update = {'$set': {'history': self.message_history}}
        if self.history_id:
            self.histories_collection.update_one(
                {'_id': self.history_id}, update)
        else:
            query['history'] = self.message_history
            self.histories_collection.insert_one(query)

    def get_gpt_response(self, format: dict = None) -> str:
        response = GPT_Client().get_gpt_client()
        while True:
            try:
                if format:
                    response = response.beta.chat.completions.parse(
                        model='gpt-4-turbo', messages=self.message_history, response_format=format)
                else:
                    response = response.chat.completions.create(
                        model='gpt-4-turbo', messages=self.message_history)
                break
            except RateLimitError:
                time.sleep(5)

        assistant_response = response.choices[0].message.content
        return assistant_response

    def compute(self) -> Output:
        self.update_history('user', self.input.prompt)

        if self.input.use_embedder == False:
            response = self.get_gpt_response(self.input.res_format)
        else:
            embedding = self.embedder.get_embedding(self.input.prompt)
            similar_entry = self.embedder.get_most_similar_prompt(
                embedding, self.input.context)
            if similar_entry:
                response = similar_entry['response']
            else:
                response = self.get_gpt_response(self.input.res_format)
                self.embedder.store_embedding(
                    self.input.prompt, embedding, response)

        self.update_history('assistant', response)
        self.save_history()

        return Output(
            output_details={
                'response': Common.jsonify(response),
                'history': Common.jsonify(self.message_history)
            }
        )
