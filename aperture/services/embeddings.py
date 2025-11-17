from typing import List, Dict, Any, Optional
from openai import OpenAI
import numpy as np
from config import settings
import json


class EmbeddingService:
    """Service for generating and managing embeddings for pattern discovery."""

    def __init__(self):
        if settings.openai_api_key:
            self.client = OpenAI(api_key=settings.openai_api_key)
        else:
            self.client = None

    async def generate_embedding(self, text: str, model: str = "text-embedding-3-small") -> List[float]:
        """
        Generate embedding for a text string.

        Args:
            text: Text to embed
            model: OpenAI embedding model to use

        Returns:
            List of floats representing the embedding
        """
        if not self.client:
            raise ValueError("OpenAI API key not configured")

        try:
            response = self.client.embeddings.create(
                model=model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            raise

    async def generate_embeddings_batch(
        self,
        texts: List[str],
        model: str = "text-embedding-3-small"
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in a single API call.

        Args:
            texts: List of texts to embed
            model: OpenAI embedding model to use

        Returns:
            List of embeddings
        """
        if not self.client:
            raise ValueError("OpenAI API key not configured")

        try:
            response = self.client.embeddings.create(
                model=model,
                input=texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            print(f"Error generating embeddings batch: {e}")
            raise

    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Similarity score between -1 and 1
        """
        v1 = np.array(vec1)
        v2 = np.array(vec2)

        dot_product = np.dot(v1, v2)
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)

        if norm_v1 == 0 or norm_v2 == 0:
            return 0.0

        return float(dot_product / (norm_v1 * norm_v2))

    async def find_similar(
        self,
        query_embedding: List[float],
        candidate_embeddings: List[Dict[str, Any]],
        top_k: int = 5,
        min_similarity: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Find most similar items to a query embedding.

        Args:
            query_embedding: The embedding to compare against
            candidate_embeddings: List of dicts with 'embedding' and other metadata
            top_k: Number of top results to return
            min_similarity: Minimum similarity threshold

        Returns:
            List of similar items with similarity scores
        """
        results = []

        for candidate in candidate_embeddings:
            similarity = self.cosine_similarity(query_embedding, candidate['embedding'])

            if similarity >= min_similarity:
                results.append({
                    **candidate,
                    'similarity': similarity
                })

        # Sort by similarity descending
        results.sort(key=lambda x: x['similarity'], reverse=True)

        return results[:top_k]

    async def cluster_embeddings(
        self,
        embeddings: List[Dict[str, Any]],
        n_clusters: int = 5,
        similarity_threshold: float = 0.75
    ) -> List[List[Dict[str, Any]]]:
        """
        Simple clustering of embeddings based on similarity.

        This is a basic implementation. For production, consider using
        proper clustering algorithms like K-means or DBSCAN.

        Args:
            embeddings: List of items with 'embedding' key
            n_clusters: Target number of clusters
            similarity_threshold: Minimum similarity to be in same cluster

        Returns:
            List of clusters (each cluster is a list of items)
        """
        if not embeddings:
            return []

        clusters = []
        assigned = set()

        for i, item in enumerate(embeddings):
            if i in assigned:
                continue

            # Start new cluster with this item
            cluster = [item]
            assigned.add(i)

            # Find similar items
            for j, other_item in enumerate(embeddings):
                if j in assigned or i == j:
                    continue

                similarity = self.cosine_similarity(
                    item['embedding'],
                    other_item['embedding']
                )

                if similarity >= similarity_threshold:
                    cluster.append(other_item)
                    assigned.add(j)

            clusters.append(cluster)

        return clusters


# Singleton instance
embedding_service = EmbeddingService()
