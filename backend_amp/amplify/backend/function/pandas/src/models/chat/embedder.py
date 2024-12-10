import tiktoken
import numpy as np
from shared.helpers.openai import ADA_Client
from shared.db.chat import get_prompts_collection


class Embedder:
    def __init__(self, context: str) -> None:
        self.context = context
        self.token_limit = 8192
        self.collection = get_prompts_collection()
        self.ada_client = ADA_Client().get_ada_client()
        self.tokenizer = tiktoken.encoding_for_model("text-embedding-ada-002")

    def count_tokens(self, text: str) -> int:
        tokens = self.tokenizer.encode(text)
        return len(tokens)

    def split_text(self, text: str, max_tokens: int = 7500) -> list:
        chunks = []
        current_chunk = []
        words = text.split()

        for word in words:
            current_chunk.append(word)
            token_count = self.count_tokens(' '.join(current_chunk))
            if token_count > max_tokens:
                chunks.append(' '.join(current_chunk[:-1]))
                current_chunk = [word]

        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks

    def compute_embedding(self, text: str) -> list:
        token_count = self.count_tokens(text)
        if token_count > self.token_limit:
            raise ValueError(f"Limit crossed: {token_count} tokens")

        response = self.ada_client.embeddings.create(
            model="text-embedding-ada-002", input=text)
        return response.data[0].embedding

    def get_embedding(self, text: str) -> list:
        token_count = self.count_tokens(text)
        if token_count > self.token_limit:
            chunks = self.split_text(text)
            embeddings = []
            for chunk in chunks:
                embedding = self.compute_embedding(chunk)
                embeddings.append(embedding)

            combined_embedding = np.mean(embeddings, axis=0).tolist()
            return combined_embedding
        else:
            return self.compute_embedding(text)

    def store_embedding(self, prompt: str, embedding: list, response) -> None:
        document = {"embedding": embedding, "prompt": prompt}
        document['context'] = self.context
        document['response'] = response
        self.collection.insert_one(document)

    def get_most_similar_prompt(self, embedding: list) -> dict:
        query = {'context': self.context}
        all_embeddings = list(self.collection.find(query))
        if not all_embeddings:
            return None

        similarities = []
        for entry in all_embeddings:
            stored_embedding = entry['embedding']
            similarity = np.dot(embedding, stored_embedding) / \
                (np.linalg.norm(embedding) * np.linalg.norm(stored_embedding))
            similarities.append((entry, similarity))

        most_similar = max(
            similarities, key=lambda x: x[1]) if similarities else None
        print(most_similar[1])
        return most_similar[0] if most_similar and most_similar[1] > 0.99 else None
