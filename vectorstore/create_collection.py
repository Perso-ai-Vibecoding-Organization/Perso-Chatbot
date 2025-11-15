from qdrant_client.http import models
from qdrant_client import QdrantClient
from dotenv import load_dotenv
import os

# 환경 변수 로드
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

COLLECTION_NAME = "perso_faq"

# Qdrant Cloud 연결 (환경 변수 사용)
client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

def create_collection():
    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config={
            "vec_question": models.VectorParams(size=3072, distance=models.Distance.COSINE),
            "vec_qa": models.VectorParams(size=3072, distance=models.Distance.COSINE),
        }
    )

    print("Collection created:", COLLECTION_NAME)

if __name__ == "__main__":
    create_collection()