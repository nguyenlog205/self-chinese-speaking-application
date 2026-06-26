from sqlalchemy import String, Integer, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from src.core.database.connection import Base

# Ví dụ định nghĩa một bảng lưu vết từ vựng học tập
class VocabularyLog(Base):
    __tablename__ = "vocabulary_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    word: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    pinyin: Mapped[str] = mapped_column(String(100), nullable=True)
    meaning: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)