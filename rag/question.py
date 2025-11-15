from openai import OpenAI
from dotenv import load_dotenv
import os
from typing import List
from rag.prompt_template import QUESTION_PROMPT, NORMALIZE_PROMPT, COMPARE_PROMPT
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

llm = OpenAI()


############################
# 문장 분류
############################
def classify_question(user_question: str) -> str:
    prompt = QUESTION_PROMPT.replace("{QUESTION}", user_question)
    res = llm.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )

    t = res.choices[0].message.content.strip().lower()

    if "yes" in t:
        return "yesno"
    if "ood" in t:
        return "ood"
    return "info"

############################
# 문장의 긍부정 감지
############################

def detect_question_polarity(q: str) -> str:
    neg = ["않", "안 ", "아니", "없", "없어", "없나요", "불안정하지", "나쁘지"]
    return "negative" if any(n in q for n in neg) else "positive"

def detect_fact_polarity(f: str) -> str:
    neg = ["않", "안 ", "없", "아니", "불안정", "지원하지 않"]
    return "negative" if any(n in f for n in neg) else "positive"

def yesno_answer(user_question: str, answer: str) -> str:
    """
    LLM에게 먼저 질문의 '의도 주장'을 정규화시키고,
    이후 FACT와 비교하여 맞습니다/아닙니다를 결정하는 방식.
    """

    fact = answer.strip()
    normalize_prompt = NORMALIZE_PROMPT.replace("{QUESTION}", user_question)

    claim = llm.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": normalize_prompt}],
        temperature=0.0
    ).choices[0].message.content.strip()

    # FACT와 claim 비교
    compare_prompt = COMPARE_PROMPT.replace("{CLAIM}", claim).replace("{FACT}", fact)
    result = llm.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": compare_prompt}],
        temperature=0.0
    ).choices[0].message.content.strip()

    return result