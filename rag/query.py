from typing import List, Dict
from qdrant_client import QdrantClient
from qdrant_client.http import models
from openai import OpenAI
from dotenv import load_dotenv
from rag.question import classify_question, yesno_answer
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

from embeddings.embedding_utils import embed_text
from rag.prompt_template import SYSTEM_PROMPT

COLLECTION_NAME = "perso_faq"

client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
    prefer_grpc=False
)
llm = OpenAI()


def search_with_two_vectors(user_question: str, top_k: int = 5):
    """
    vec_question / vec_qa 각각 검색하고 가중합(final_score)로 재랭킹하는 함수
    """

    query_vec = embed_text(user_question)

    hits_q = client.search(
        collection_name=COLLECTION_NAME,
        vector=query_vec,
        limit=top_k,
        using="vec_question"
    )

    hits_qa = client.search(
        collection_name=COLLECTION_NAME,
        vector=query_vec,
        limit=top_k,
        using="vec_qa"
    )

    # 3) id 기준으로 묶기
    scores: Dict[str, Dict] = {}

    def add_hits(hits, score_key):
        for h in hits:
            pid = h.payload["id"]
            if pid not in scores:
                scores[pid] = {
                    "payload": h.payload,
                    "score_q": 0.0,
                    "score_qa": 0.0
                }
            scores[pid][score_key] = max(scores[pid][score_key], h.score)

    add_hits(hits_q, "score_q")
    add_hits(hits_qa, "score_qa")

    # 4) 가중합 계산
    results = []
    for pid, info in scores.items():
        final_score = 0.4 * info["score_q"] + 0.6 * info["score_qa"]
        results.append({
            "id": pid,
            "payload": info["payload"],
            "score_q": info["score_q"],
            "score_qa": info["score_qa"],
            "final_score": final_score
        })

    # 5) 최종 정렬
    results.sort(key=lambda x: x["final_score"], reverse=True)
    return results[:top_k]


def generate_answer(user_question: str):
    q_type = classify_question(user_question)

    if q_type == "ood":
        return "Perso.ai FAQ 범위를 벗어난 질문입니다."

    # 검색
    results = search_with_two_vectors(user_question, top_k=5)
    if not results:
        return "제공된 FAQ 데이터에서 관련 정보를 찾기 어렵습니다."

    best = results[0]
    payload = best["payload"]
    answer = payload["answer"]
    score = best["final_score"]

    # YES/NO 질문이면 무조건 yesno_answer 실행
    if q_type == "yesno":
        return yesno_answer(user_question, answer)

    # info 질문
    HIGH = 0.45
    MID = 0.25

    if score >= HIGH:
        return answer

    if score >= MID:
        context = "\n".join([r["payload"]["qa_text"] for r in results[:3]])
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"CONTEXT:\n{context}\n---\nQUESTION:\n{user_question}"}
        ]
        completion = llm.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.0
        )
        return completion.choices[0].message.content.strip()

    return "제공된 Perso.ai FAQ 정보로는 정확한 답변을 찾기 어렵습니다."