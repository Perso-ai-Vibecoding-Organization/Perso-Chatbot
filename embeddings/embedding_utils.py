from openai import OpenAI
from dotenv import load_dotenv
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))
client = OpenAI()

EMBED_MODEL = "text-embedding-3-large"

def embed_text(text: str):
    response = client.embeddings.create(
        model=EMBED_MODEL,
        input=text
    )
    return response.data[0].embedding