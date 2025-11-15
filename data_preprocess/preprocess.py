import pandas as pd
import json
import os

def load_qna(json_path: str):
    """JSON 파일에서 QnA 데이터를 로드하는 함수"""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

if __name__ == "__main__":
    df = pd.read_excel("qna.xlsx", header=None)
    content_column = df.iloc[2:, 2].dropna()

    records = []
    current_question = None
    record_id = 1

    for content in content_column:
        content_str = str(content).strip()
        
        if content_str.startswith("Q."):
            current_question = content_str[2:].strip()  # "Q." 제거
        elif content_str.startswith("A.") and current_question:
            answer = content_str[2:].strip()  # "A." 제거
            # qa_text: 질문과 답변을 합친 텍스트 (벡터 검색용)
            qa_text = f"Q: {current_question}\nA: {answer}"
            records.append({
                "id": str(record_id),
                "question": current_question,
                "answer": answer,
                "qa_text": qa_text
            })
            record_id += 1
            current_question = None  # 다음 질문을 위해 초기화

    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, "qna.json")
    
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    
    print(f"총 {len(records)}개의 QnA 데이터를 생성했습니다.")
