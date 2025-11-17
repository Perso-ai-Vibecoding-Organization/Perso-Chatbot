FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir --upgrade qdrant-client==1.9.0

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]