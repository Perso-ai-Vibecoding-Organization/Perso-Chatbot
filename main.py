from dotenv import load_dotenv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

from rag.query import generate_answer

while True:
    q = input("\n질문: ")
    if q == "exit":
        break

    print("\n답변:\n", generate_answer(q))