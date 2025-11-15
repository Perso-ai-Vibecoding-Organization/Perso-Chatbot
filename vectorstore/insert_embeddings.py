import json
import sys
from qdrant_client import QdrantClient
from qdrant_client.http import models
from dotenv import load_dotenv
import os
import uuid

# 프로젝트 루트를 Python 경로에 추가
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

# 환경 변수 로드
load_dotenv(os.path.join(BASE_DIR, ".env"))

from embeddings.embedding_utils import embed_text
from data_preprocess.preprocess import load_qna

COLLECTION_NAME = "perso_faq"

# Qdrant Cloud 연결
client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
    timeout=60
)

def insert_data():
    qna_json_path = os.path.join(BASE_DIR, "data_preprocess", "qna.json")
    data = load_qna(qna_json_path)

    ids = []
    payloads = []
    vec_question = []
    vec_qa = []

    for item in data:
        q_vec = embed_text(item["question"])
        qa_vec = embed_text(item["qa_text"])

        ids.append(str(uuid.uuid4()))
        payloads.append({
            "id": item["id"],
            "question": item["question"],
            "answer": item["answer"],
            "qa_text": item["qa_text"]
        })
        vec_question.append(q_vec)
        vec_qa.append(qa_vec)

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=models.Batch(
            ids=ids,
            payloads=payloads,
            vectors={
                "vec_question": vec_question,
                "vec_qa": vec_qa
            }
        )
    )
    print("데이터 삽입 완료")

if __name__ == "__main__":
    insert_data()