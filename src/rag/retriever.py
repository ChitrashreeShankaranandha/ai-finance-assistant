from src.rag.embedding import get_embedding
from src.rag.pinecone_client import get_pinecone_index


def retrieve_finance_context(user_query: str, top_k: int = 3):
    """
    Retrieves relevant finance education documents from Pinecone.
    """

    index = get_pinecone_index()

    query_embedding = get_embedding(user_query)

    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )

    retrieved_docs = []

    for match in results["matches"]:
        retrieved_docs.append({
            "title": match["metadata"]["title"],
            "category": match["metadata"]["category"],
            "text": match["metadata"]["text"],
            "score": match["score"]
        })

    return retrieved_docs