FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .

RUN pip uninstall -y qdrant-client || true
RUN pip install --no-cache-dir qdrant-client==1.16.0
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]