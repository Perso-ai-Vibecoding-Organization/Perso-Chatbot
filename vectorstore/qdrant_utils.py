import os
from qdrant_client import QdrantClient
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))
client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

client.recreate_collection(
    collection_name="test_collection",
    vectors_config={
        "size": 1536,   # embedding dimension
        "distance": "Cosine"
    }
)