import pandas as pd
import json


df = pd.read_excel("qna.xlsx", header=None)
content_column = df.iloc[2:, 2].dropna()

records = []
current_question = None
record_id = 1

for content in content_column:
    content_str = str(content).strip()
    
    if content_str.startswith("Q."):
        # 질문인 경우
        current_question = content_str[2:].strip()  # "Q." 제거
    elif content_str.startswith("A.") and current_question:
        # 답변인 경우 (이전에 질문이 있었을 때만)
        answer = content_str[2:].strip()  # "A." 제거
        records.append({
            "id": str(record_id),
            "question": current_question,
            "answer": answer
        })
        record_id += 1
        current_question = None  # 다음 질문을 위해 초기화

with open("qna.json", "w", encoding="utf-8") as f:
    json.dump(records, f, ensure_ascii=False, indent=2)