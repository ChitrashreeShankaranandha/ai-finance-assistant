from src.core.openai_client import get_openai_client

client = get_openai_client()

def get_embedding(text: str):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding