from src.data.finance_knowledge import finance_docs
from src.rag.embedding import get_embedding
from src.rag.pinecone_client import get_pinecone_index


def index_finance_data():
    """
    Converts finance knowledge documents into embeddings
    and uploads them to Pinecone.
    """

    index = get_pinecone_index()
    vectors = []

    for i, doc in enumerate(finance_docs):
        embedding = get_embedding(doc["text"])

        vectors.append({
            "id": f"finance-doc-{i}",
            "values": embedding,
            "metadata": {
                "title": doc["title"],
                "category": doc["category"],
                "text": doc["text"]
            }
        })

    index.upsert(vectors=vectors)

    return f"Uploaded {len(vectors)} finance documents to Pinecone."