import chromadb
from chromadb.config import Settings
import os
import requests


class FinancialSituationMemory:
    def __init__(self, name, config):
        # Use Google's embedding model
        self.embedding_model = "text-embedding-004"
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        
        self.chroma_client = chromadb.Client(Settings(allow_reset=True))
        self.situation_collection = self.chroma_client.create_collection(name=name)

    # def get_embedding(self, text):
    #     """Get Google embedding for a text"""
        
    #     url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.embedding_model}:embedContent"
    #     headers = {
    #         "Content-Type": "application/json",
    #     }
    #     params = {"key": self.api_key}
        
    #     data = {
    #         "content": {
    #             "parts": [{"text": text}]
    #         }
    #     }
        
    #     response = requests.post(url, headers=headers, params=params, json=data)
    #     response.raise_for_status()
        
    #     return response.json()["embedding"]["values"]


    def get_embedding(self, text: str):
        """Return a vector embedding for `text` using Google text-embedding-004."""
        print(f'self.embedding_model------------------------------->: {self.embedding_model}')
        # 1) Guard against empty input (prevents 400s)
        if not isinstance(text, str) or not text.strip():
            # choose: return zeros, or raise. Returning zeros keeps the pipeline flowing.
            return [0.0] * getattr(self, "dim", 768)  # adjust default dim if needed

        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.embedding_model}:embedContent"
        )
        headers = {"Content-Type": "application/json"}
        params = {"key": self.api_key}
        text = text[:9000]
        payload = {"content": {"parts": [{"text": text}]}}

        try:
            resp = requests.post(url, headers=headers, params=params, json=payload, timeout=20)
            resp.raise_for_status()
        except requests.HTTPError as e:
            # Bubble up with server message for easier debugging
            msg = getattr(e.response, "text", str(e))
            raise RuntimeError(f"Embedding API HTTP error: {msg}") from e
        except requests.RequestException as e:
            raise RuntimeError(f"Embedding API request failed: {e}") from e

        data = resp.json()
        # Expected shape: {"embedding": {"value": [float, ...]}}
        emb = (data.get("embedding") or {}).get("values")
        if not isinstance(emb, list):
            raise RuntimeError(f"Unexpected embedding response: {data}")

        return emb


    def add_situations(self, situations_and_advice):
        """Add financial situations and their corresponding advice. Parameter is a list of tuples (situation, rec)"""

        situations = []
        advice = []
        ids = []
        embeddings = []

        offset = self.situation_collection.count()

        for i, (situation, recommendation) in enumerate(situations_and_advice):
            situations.append(situation)
            advice.append(recommendation)
            ids.append(str(offset + i))
            embeddings.append(self.get_embedding(situation))

        self.situation_collection.add(
            documents=situations,
            metadatas=[{"recommendation": rec} for rec in advice],
            embeddings=embeddings,
            ids=ids,
        )

    def get_memories(self, current_situation, n_matches=1):
        """Find matching recommendations using Google embeddings"""
        query_embedding = self.get_embedding(current_situation)

        results = self.situation_collection.query(
            query_embeddings=[query_embedding],
            n_results=n_matches,
            include=["metadatas", "documents", "distances"],
        )

        matched_results = []
        for i in range(len(results["documents"][0])):
            matched_results.append(
                {
                    "matched_situation": results["documents"][0][i],
                    "recommendation": results["metadatas"][0][i]["recommendation"],
                    "similarity_score": 1 - results["distances"][0][i],
                }
            )

        return matched_results


if __name__ == "__main__":
    # Example usage
    matcher = FinancialSituationMemory()

    # Example data
    example_data = [
        (
            "High inflation rate with rising interest rates and declining consumer spending",
            "Consider defensive sectors like consumer staples and utilities. Review fixed-income portfolio duration.",
        ),
        (
            "Tech sector showing high volatility with increasing institutional selling pressure",
            "Reduce exposure to high-growth tech stocks. Look for value opportunities in established tech companies with strong cash flows.",
        ),
        (
            "Strong dollar affecting emerging markets with increasing forex volatility",
            "Hedge currency exposure in international positions. Consider reducing allocation to emerging market debt.",
        ),
        (
            "Market showing signs of sector rotation with rising yields",
            "Rebalance portfolio to maintain target allocations. Consider increasing exposure to sectors benefiting from higher rates.",
        ),
    ]

    # Add the example situations and recommendations
    matcher.add_situations(example_data)

    # Example query
    current_situation = """
    Market showing increased volatility in tech sector, with institutional investors 
    reducing positions and rising interest rates affecting growth stock valuations
    """

    try:
        recommendations = matcher.get_memories(current_situation, n_matches=2)

        for i, rec in enumerate(recommendations, 1):
            print(f"\nMatch {i}:")
            print(f"Similarity Score: {rec['similarity_score']:.2f}")
            print(f"Matched Situation: {rec['matched_situation']}")
            print(f"Recommendation: {rec['recommendation']}")

    except Exception as e:
        print(f"Error during recommendation: {str(e)}")
