from typing import List, Dict
from qdrant_client import QdrantClient
from qdrant_client.http import models
from openai import OpenAI
from dotenv import load_dotenv
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

from embeddings.embedding_utils import embed_text
from rag.prompt_template import SYSTEM_PROMPT

COLLECTION_NAME = "perso_faq"

client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)
llm = OpenAI()


def search_with_two_vectors(user_question: str, top_k: int = 5):
    """
    vec_question / vec_qa 각각 검색하고 가중합(final_score)로 재랭킹하는 함수
    """

    query_vec = embed_text(user_question)

    # 1) question 기준 검색
    hits_q = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=("vec_question", query_vec),
        limit=top_k
    )

    # 2) qa_text 기준 검색
    hits_qa = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=("vec_qa", query_vec),
        limit=top_k
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
    results = search_with_two_vectors(user_question, top_k=5)

    if not results:
        return "제공된 FAQ 데이터에서 관련 정보를 찾지 못했습니다."
    best = results[0]
    max_score = best["final_score"]

    # threshold 설정
    HIGH = 0.55   # 매우 유사 → LLM 없이 정답 반환
    MID  = 0.35   # 애매 → RAG 수행
    # 이하 → 관련 없음 판단

    # (1) 고확신: score >= 0.90
    if max_score >= HIGH:
        faq_ans = best["payload"]["answer"]
        faq_id = best["id"]
        return f"{faq_ans}\n\n(참고: FAQ #{faq_id})"

    # (2) 중간(0.80~0.89): RAG
    if max_score >= MID:
        # 상위 1~3개 context 사용
        top_contexts = results[:3]
        context = ""
        used_ids = []

        for item in top_contexts:
            context += item["payload"]["qa_text"] + "\n\n"
            used_ids.append(item["id"])

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"CONTEXT:\n{context}\n---\nUSER QUESTION:\n{user_question}"
            }
        ]

        completion = llm.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.0
        )

        answer = completion.choices[0].message.content
        return f"{answer}\n\n(참고: FAQ #{', '.join(used_ids)})"

    # (3) 저확신: 관련 없는 질문
    return (
        "제공된 Perso.ai/이스트소프트 FAQ 정보로는 정확한 답변을 찾지 못했습니다.\n"
        "다른 질문을 해주세요."
    )