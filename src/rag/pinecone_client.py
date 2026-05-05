from google.colab import userdata
from pinecone import Pinecone

INDEX_NAME = "ai-finance-assistant"

def get_pinecone_index():
    api_key = userdata.get("PineConeA")

    if not api_key:
        raise ValueError("Pinecone API key missing")

    pc = Pinecone(api_key=api_key)
    return pc.Index(INDEX_NAME)