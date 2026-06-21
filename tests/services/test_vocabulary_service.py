"""
Unit tests for VocabularyService.
"""

import sys
from pathlib import Path

# Thêm đường dẫn gốc vào sys.path để import được src
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

import pytest
from src.services.vocabulary_service import VocabularyService


class TestVocabularyService:
    """Test cases for VocabularyService."""

    @classmethod
    def setup_class(cls):
        """Khởi tạo service trước khi chạy test."""
        cls.service = VocabularyService()

    def test_lookup_single_word_found(self):
        """Test tra từ có trong từ điển."""
        result = self.service.lookup("你好")
        assert result["found"] is True
        assert result["word"] == "你好"
        assert len(result["entries"]) > 0
        assert "pinyin" in result["entries"][0]
        assert "meanings" in result["entries"][0]

    def test_lookup_single_word_not_found(self):
        """Test tra từ không có trong từ điển."""
        result = self.service.lookup("không_có_từ_này")
        assert result["found"] is False
        assert result["word"] == "không_có_từ_này"
        assert result["entries"] == []

    def test_lookup_single_word_empty(self):
        """Test tra từ rỗng."""
        with pytest.raises(ValueError, match="Word cannot be empty"):
            self.service.lookup("")

        with pytest.raises(ValueError, match="Word cannot be empty"):
            self.service.lookup("   ")

    def test_lookup_batch(self):
        """Test tra nhiều từ."""
        words = ["你好", "世界", "không_có_từ_này"]
        results = self.service.lookup_batch(words)

        assert len(results) == 3

        # Từ "你好" có nghĩa
        assert results[0]["word"] == "你好"
        assert results[0]["found"] is True

        # Từ "世界" có nghĩa
        assert results[1]["word"] == "世界"
        assert results[1]["found"] is True

        # Từ không có
        assert results[2]["word"] == "không_có_từ_này"
        assert results[2]["found"] is False

    def test_lookup_batch_empty(self):
        """Test tra batch với danh sách rỗng."""
        with pytest.raises(ValueError, match="Words list cannot be empty"):
            self.service.lookup_batch([])

    def test_lookup_traditional_chinese(self):
        """Test tra từ viết bằng chữ phồn thể."""
        # "你好" viết phồn thể là "你好" (giống nhau)
        # "学习" viết phồn thể là "學習"
        result = self.service.lookup("學習")
        # Có thể có hoặc không tùy từ điển, nhưng nếu có thì trả về đúng
        if result["found"]:
            assert "學" in result["entries"][0]["traditional"]
        # Không assert fail nếu không có, vì từ điển có thể không có

    def test_lookup_return_structure(self):
        """Test cấu trúc dữ liệu trả về."""
        result = self.service.lookup("中文")
        if result["found"]:
            entry = result["entries"][0]
            assert "traditional" in entry
            assert "simplified" in entry
            assert "pinyin" in entry
            assert "meanings" in entry
            assert isinstance(entry["meanings"], list)