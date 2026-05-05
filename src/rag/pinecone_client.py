import os
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

INDEX_NAME = "ai-finance-assistant"

def get_pinecone_index():
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        raise ValueError("PINECONE_API_KEY not found in .env file")
    pc = Pinecone(api_key=api_key)
    return pc.Index(INDEX_NAME)