"""
Unit tests for Vocabulary API endpoints.
Uses FastAPI TestClient, mocks Service layer.
"""

import sys
from pathlib import Path
from unittest.mock import patch

root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


class TestVocabularyAPI:

    def test_lookup_word_success(self):
        response = client.get("/vocabulary/lookup/", params={"word": "你好"})
        assert response.status_code == 200
        data = response.json()
        assert data["word"] == "你好"
        assert data["found"] is True
        assert len(data["entries"]) > 0

    def test_lookup_word_not_found(self):
        response = client.get("/vocabulary/lookup/", params={"word": "không_có_từ_này"})
        assert response.status_code == 200
        data = response.json()
        assert data["word"] == "không_có_từ_này"
        assert data["found"] is False
        assert data["entries"] == []

    def test_lookup_word_empty(self):
        response = client.get("/vocabulary/lookup/", params={"word": ""})
        assert response.status_code == 400
        data = response.json()
        assert "Word cannot be empty" in data["detail"]

    def test_lookup_word_whitespace(self):
        response = client.get("/vocabulary/lookup/", params={"word": "   "})
        assert response.status_code == 400
        data = response.json()
        assert "Word cannot be empty" in data["detail"]

    def test_lookup_batch_success(self):
        response = client.post(
            "/vocabulary/lookup-batch/",
            json={"words": ["你好", "世界", "学习"]}
        )
        assert response.status_code == 200
        data = response.json()
        results = data["results"]
        assert len(results) == 3
        assert results[0]["found"] is True
        assert results[1]["found"] is True
        assert results[2]["found"] is True

    def test_lookup_batch_with_not_found(self):
        response = client.post(
            "/vocabulary/lookup-batch/",
            json={"words": ["你好", "không_có_từ_này"]}
        )
        assert response.status_code == 200
        data = response.json()
        results = data["results"]
        assert len(results) == 2
        assert results[0]["found"] is True
        assert results[1]["found"] is False
        assert results[1]["entries"] == []

    def test_lookup_batch_empty_list(self):
        response = client.post(
            "/vocabulary/lookup-batch/",
            json={"words": []}
        )
        assert response.status_code == 400
        data = response.json()
        assert "Words list cannot be empty" in data["detail"]

    def test_lookup_batch_missing_words_field(self):
        response = client.post(
            "/vocabulary/lookup-batch/",
            json={}
        )
        assert response.status_code == 400
        data = response.json()
        assert "Missing 'words' field" in data["detail"]

    @patch('src.api.vocabulary.get_service')
    def test_lookup_service_error_handling(self, mock_get_service):
        mock_service = mock_get_service.return_value
        mock_service.lookup.side_effect = Exception("Database connection failed")
        response = client.get("/vocabulary/lookup/", params={"word": "你好"})
        assert response.status_code == 500
        data = response.json()
        assert "Database connection failed" in data["detail"]

    @patch('src.api.vocabulary.get_service')
    def test_lookup_batch_service_error(self, mock_get_service):
        mock_service = mock_get_service.return_value
        mock_service.lookup_batch.side_effect = Exception("Service unavailable")
        response = client.post(
            "/vocabulary/lookup-batch/",
            json={"words": ["你好", "世界"]}
        )
        assert response.status_code == 500
        data = response.json()
        assert "Service unavailable" in data["detail"]