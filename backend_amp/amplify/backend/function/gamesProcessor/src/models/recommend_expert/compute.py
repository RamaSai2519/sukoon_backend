import time
import requests
import numpy as np
from models.common import Common
from openai import RateLimitError
from configs import CONFIG as config
from models.constants import OutputStatus
from helpers.openai import GPT_Client, ADA_Client
from models.recommend_expert.prompt import Prompt
from db.embeddings import get_recommendations_collection
from models.interfaces import RecommendExpertInput as Input, Output


class Compute:
    def __init__(self, input: Input) -> None:
        self.input = input
        self.common = Common()
        self.prompter = Prompt(input)
        self.gpt_client = GPT_Client().get_gpt_client()
        self.ada_client = ADA_Client().get_ada_client()
        self.embeddings_collection = get_recommendations_collection()
        self.message_history = [
            {"role": "system",
                "content": "You are a smart assistant who helps recommend an expert(sarathi) to the users who have come to Sukoon Unlimited(a platform for seniors, by seniors) where seniors connect with each other and have heartfelt conversations."}
        ]

    def compute_embedding(self, text: str) -> list:
        response = self.ada_client.embeddings.create(
            model="text-embedding-ada-002", input=text)
        return response.data[0].embedding

    def get_most_similar_prompt(self, embedding: list) -> dict:
        all_embeddings = list(self.embeddings_collection.find())
        if not all_embeddings:
            return None

        similarities = []
        for entry in all_embeddings:
            stored_embedding = entry['embedding']
            similarity = np.dot(embedding, stored_embedding) / (
                np.linalg.norm(embedding) *
                np.linalg.norm(stored_embedding)
            )
            similarities.append((entry, similarity))

        most_similar = max(
            similarities, key=lambda x: x[1]) if similarities else None
        return most_similar[0] if most_similar and most_similar[1] > 0.85 else None

    def store_embedding(self, prompt: str, embedding: list, response: dict) -> None:
        document = {"prompt": prompt, "embedding": embedding}
        document.update(response)
        self.embeddings_collection.insert_one(document)

    def chat(self, role: str, content: str) -> str:
        self.message_history.append({"role": role, "content": content})

        try:
            response = self.gpt_client.chat.completions.create(
                model="gpt-4-turbo", messages=self.message_history)
        except RateLimitError:
            time.sleep(5)
            response = self.gpt_client.chat.completions.create(
                model="gpt-4-turbo", messages=self.message_history)

        assistant_response = response.choices[0].message.content
        self.message_history.append(
            {"role": "assistant", "content": assistant_response})
        return assistant_response

    def get_expert(self, expert_id: str) -> dict:
        url = config.URL + '/actions/expert'
        params = {"expert_id": expert_id}
        response = requests.get(url, params=params)
        response = response.json()
        expert = response.get('output_details', None)
        return expert

    def compute(self) -> Output:
        prompt = self.prompter.personas_prompt()
        embedding = self.compute_embedding(prompt)
        similar_entry = self.get_most_similar_prompt(embedding)

        if similar_entry:
            expert_id = similar_entry['expert_id']
            expert = self.get_expert(expert_id)

            if expert:
                return Output(
                    output_details=expert,
                    output_status=OutputStatus.SUCCESS,
                    output_message="Successfully fetched expert from stored data"
                )
        else:
            response = self.chat("user", prompt)
            print(response, 'gpt_response')
            response_json = self.common.extract_json(response)
            expert_id = response_json.get("expert_id", None)

            if expert_id:
                expert = self.get_expert(expert_id)
                if expert:
                    self.store_embedding(prompt, embedding, response_json)

                    return Output(
                        output_details=expert,
                        output_status=OutputStatus.SUCCESS,
                        output_message="Successfully fetched expert"
                    )

        return Output(
            output_details={},
            output_status=OutputStatus.FAILURE,
            output_message="Expert not found"
        )
