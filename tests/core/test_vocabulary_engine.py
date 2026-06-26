"""
Unit tests for VocabularyEngine (core layer).
Tests dictionary loading, lookup logic, and parsing.
"""

import sys
from pathlib import Path

# Add project root to path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

import pytest
from src.core.engines.vocabulary_engine import VocabularyEngine


class TestVocabularyEngine:
    """Test cases for VocabularyEngine core."""

    @classmethod
    def setup_class(cls):
        """Khởi tạo engine trước khi chạy test."""
        cls.engine = VocabularyEngine()

    def test_load_dict_success(self):
        """Test từ điển được load thành công."""
        assert hasattr(self.engine, 'entries')
        assert len(self.engine.entries) > 0
        assert isinstance(self.engine.entries, dict)

    def test_load_dict_has_common_words(self):
        """Test từ điển có các từ thông dụng."""
        common_words = ["你好", "世界", "中国", "学习", "中文"]
        for word in common_words:
            assert word in self.engine.entries, f"Word '{word}' not found in dictionary"

    def test_lookup_found_simplified(self):
        """Test tra từ giản thể có trong từ điển."""
        result = self.engine.lookup("你好")
        assert result is not None
        assert result["word"] == "你好"
        assert len(result["entries"]) > 0
        entry = result["entries"][0]
        assert "traditional" in entry
        assert "simplified" in entry
        assert "pinyin" in entry
        assert "meanings" in entry
        assert isinstance(entry["meanings"], list)

    def test_lookup_found_traditional(self):
        """Test tra từ phồn thể có trong từ điển."""
        result = self.engine.lookup("學習")
        if result:
            assert result["word"] == "學習"
            assert len(result["entries"]) > 0
            entry = result["entries"][0]
            assert "學" in entry["traditional"]

    def test_lookup_not_found(self):
        """Test tra từ không có trong từ điển."""
        result = self.engine.lookup("không_có_từ_này")
        assert result is None

    def test_lookup_empty_string(self):
        """Test tra từ rỗng."""
        with pytest.raises(ValueError, match="Word cannot be empty"):
            self.engine.lookup("")
        with pytest.raises(ValueError, match="Word cannot be empty"):
            self.engine.lookup("   ")

    def test_lookup_multi(self):
        """Test tra nhiều từ cùng lúc."""
        words = ["你好", "世界", "không_có_từ_này"]
        results = self.engine.lookup_multi(words)

        assert len(results) == 3
        assert results["你好"] is not None
        assert results["世界"] is not None
        assert results["không_có_từ_này"] is None

    def test_lookup_multi_empty_list(self):
        """Test tra batch với danh sách rỗng."""
        results = self.engine.lookup_multi([])
        assert results == {}

    def test_entry_structure(self):
        """Test cấu trúc dữ liệu của mỗi entry."""
        result = self.engine.lookup("中文")
        if result:
            entry = result["entries"][0]
            assert "traditional" in entry
            assert "simplified" in entry
            assert "pinyin" in entry
            assert "meanings" in entry
            assert isinstance(entry["meanings"], list)
            # Pinyin có thể chứa số 1-5 hoặc thanh điệu
            assert any(c.isdigit() for c in entry["pinyin"]) or any(c in "āáǎàēéěè" for c in entry["pinyin"])

    def test_get_available_models(self):
        """Test lấy danh sách model có sẵn."""
        models = self.engine.get_available_models()
        # Ít nhất có model 'cedict'
        assert "cedict" in models
        assert isinstance(models, list)