"""
Unit tests for embeddings service.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import sys
import os
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from services.embeddings import EmbeddingService


@pytest.mark.unit
class TestEmbeddingService:
    """Test suite for embedding service."""

    @pytest.fixture
    def embedding_service(self):
        """Create embedding service instance."""
        return EmbeddingService(api_key="test-key")

    @pytest.mark.asyncio
    async def test_generate_embedding(self, embedding_service):
        """Test generating embedding for text."""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.json.return_value = {
                "data": [{
                    "embedding": [0.1] * 1536
                }]
            }
            mock_response.status_code = 200
            mock_post.return_value = mock_response

            embedding = await embedding_service.generate_embedding("Test text")

            assert len(embedding) == 1536
            assert all(isinstance(x, float) for x in embedding)

    def test_cosine_similarity(self, embedding_service):
        """Test cosine similarity calculation."""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]
        vec3 = [0.0, 1.0, 0.0]

        # Identical vectors should have similarity 1.0
        similarity = embedding_service.cosine_similarity(vec1, vec2)
        assert abs(similarity - 1.0) < 0.001

        # Orthogonal vectors should have similarity 0.0
        similarity = embedding_service.cosine_similarity(vec1, vec3)
        assert abs(similarity - 0.0) < 0.001

    def test_cosine_similarity_opposite(self, embedding_service):
        """Test cosine similarity with opposite vectors."""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [-1.0, 0.0, 0.0]

        similarity = embedding_service.cosine_similarity(vec1, vec2)
        assert abs(similarity - (-1.0)) < 0.001

    @pytest.mark.asyncio
    async def test_find_similar(self, embedding_service):
        """Test finding similar embeddings."""
        query_embedding = [1.0, 0.0, 0.0]

        candidates = [
            {"id": "1", "embedding": [0.9, 0.1, 0.0], "text": "Similar 1"},
            {"id": "2", "embedding": [0.0, 1.0, 0.0], "text": "Different"},
            {"id": "3", "embedding": [0.95, 0.05, 0.0], "text": "Similar 2"},
        ]

        results = await embedding_service.find_similar(
            query_embedding,
            candidates,
            top_k=2,
            min_similarity=0.7
        )

        assert len(results) == 2
        # Results should be sorted by similarity (highest first)
        assert results[0]["id"] in ["1", "3"]

    @pytest.mark.asyncio
    async def test_find_similar_no_matches(self, embedding_service):
        """Test finding similar with no matches above threshold."""
        query_embedding = [1.0, 0.0, 0.0]

        candidates = [
            {"id": "1", "embedding": [0.0, 1.0, 0.0], "text": "Different 1"},
            {"id": "2", "embedding": [0.0, 0.0, 1.0], "text": "Different 2"},
        ]

        results = await embedding_service.find_similar(
            query_embedding,
            candidates,
            min_similarity=0.9
        )

        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_cluster_embeddings(self, embedding_service):
        """Test clustering embeddings."""
        # Create 3 distinct clusters
        embeddings = [
            {"id": f"cluster1_{i}", "embedding": [1.0 + (i * 0.1), 0.0, 0.0]}
            for i in range(5)
        ] + [
            {"id": f"cluster2_{i}", "embedding": [0.0, 1.0 + (i * 0.1), 0.0]}
            for i in range(5)
        ] + [
            {"id": f"cluster3_{i}", "embedding": [0.0, 0.0, 1.0 + (i * 0.1)]}
            for i in range(5)
        ]

        clusters = await embedding_service.cluster_embeddings(
            embeddings,
            n_clusters=3
        )

        assert len(clusters) == 3
        # Each cluster should have approximately 5 items
        cluster_sizes = [len(c["items"]) for c in clusters]
        assert all(size >= 3 for size in cluster_sizes)  # Allow some variance

    @pytest.mark.asyncio
    async def test_generate_embedding_error(self, embedding_service):
        """Test handling of API errors when generating embeddings."""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status_code = 429
            mock_response.json.return_value = {
                "error": {"message": "Rate limit exceeded"}
            }
            mock_post.return_value = mock_response

            with pytest.raises(Exception):
                await embedding_service.generate_embedding("Test text")

    @pytest.mark.asyncio
    async def test_generate_embedding_empty_text(self, embedding_service):
        """Test generating embedding for empty text."""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.json.return_value = {
                "data": [{"embedding": [0.0] * 1536}]
            }
            mock_response.status_code = 200
            mock_post.return_value = mock_response

            embedding = await embedding_service.generate_embedding("")

            assert len(embedding) == 1536

    @pytest.mark.asyncio
    async def test_generate_embedding_long_text(self, embedding_service):
        """Test generating embedding for very long text."""
        long_text = "word " * 10000  # Very long text

        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.json.return_value = {
                "data": [{"embedding": [0.1] * 1536}]
            }
            mock_response.status_code = 200
            mock_post.return_value = mock_response

            embedding = await embedding_service.generate_embedding(long_text)

            assert len(embedding) == 1536

    @pytest.mark.asyncio
    async def test_find_similar_empty_candidates(self, embedding_service):
        """Test finding similar with empty candidates list."""
        query_embedding = [1.0, 0.0, 0.0]
        candidates = []

        results = await embedding_service.find_similar(
            query_embedding,
            candidates
        )

        assert len(results) == 0

    def test_cosine_similarity_zero_vectors(self, embedding_service):
        """Test cosine similarity with zero vectors."""
        vec1 = [0.0, 0.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]

        # Should handle zero vector gracefully
        try:
            similarity = embedding_service.cosine_similarity(vec1, vec2)
            # If it doesn't raise, should return 0 or NaN
            assert similarity == 0.0 or np.isnan(similarity)
        except (ZeroDivisionError, ValueError):
            # It's acceptable to raise an error for zero vectors
            pass

    @pytest.mark.asyncio
    async def test_cluster_embeddings_single_cluster(self, embedding_service):
        """Test clustering with n_clusters=1."""
        embeddings = [
            {"id": f"item_{i}", "embedding": [i * 0.1, 0.0, 0.0]}
            for i in range(10)
        ]

        clusters = await embedding_service.cluster_embeddings(
            embeddings,
            n_clusters=1
        )

        assert len(clusters) == 1
        assert len(clusters[0]["items"]) == 10

    @pytest.mark.asyncio
    async def test_cluster_embeddings_more_clusters_than_items(self, embedding_service):
        """Test clustering when n_clusters > number of items."""
        embeddings = [
            {"id": f"item_{i}", "embedding": [i * 0.1, 0.0, 0.0]}
            for i in range(3)
        ]

        # Request more clusters than items
        clusters = await embedding_service.cluster_embeddings(
            embeddings,
            n_clusters=5
        )

        # Should return at most as many clusters as items
        assert len(clusters) <= 3
