FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

WORKDIR /app

COPY services/zh_dictionary/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/zh_dictionary/src/ ./src/
COPY configs/ ./configs/
COPY shared/ ./shared/

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]