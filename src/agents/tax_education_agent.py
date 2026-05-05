from src.core.openai_client import get_openai_client
from src.rag.retriever import retrieve_finance_context

client = get_openai_client()

def is_tax_related(query: str) -> bool:
    """Basic guardrail: check if query is actually tax/finance related."""
    finance_keywords = [
        "tax", "invest", "retire", "401", "ira", "roth", "capital",
        "dividend", "income", "deduct", "account", "saving", "fund",
        "contribution", "withdrawal", "penalty", "bracket", "filing"
    ]
    return any(keyword in query.lower() for keyword in finance_keywords)


def tax_education_agent(query: str) -> str:
    """
    RAG-powered tax education agent.
    Uses Pinecone to retrieve relevant tax docs then GPT to explain them.
    Includes basic input guardrail.
    """
    if not is_tax_related(query):
        return (
            "I specialize in financial and tax education topics. "
            "Please ask me about taxes, retirement accounts, investment accounts, "
            "tax strategies, or related financial concepts."
        )

    rag_docs = retrieve_finance_context(query, top_k=3)

    context_parts = []
    sources = []
    for doc in rag_docs:
        if "text" in doc:
            context_parts.append(doc["text"].strip())
        if "title" in doc:
            sources.append(doc["title"])

    rag_context  = "\n\n".join(context_parts)
    sources_text = ", ".join(sources) if sources else "General financial knowledge"

    prompt = f"""
You are a financial education assistant specializing in tax concepts
for beginner investors. You explain complex tax topics in simple terms.

QUESTION: {query}

RELEVANT EDUCATIONAL CONTENT FROM KNOWLEDGE BASE:
{rag_context[:1000] if rag_context else "Use your general financial knowledge."}

SOURCES: {sources_text}

Please provide:
1. A clear beginner-friendly answer to the question
2. A concrete example with real numbers to illustrate the concept
3. One common mistake beginners make on this tax topic
4. One actionable tip they can apply today
5. Related tax topics they should also learn about

Never give personalized tax advice. Always recommend consulting a qualified
tax professional for personal situations.

End with: "This is for educational purposes only. Please consult a
qualified tax professional for advice specific to your situation."
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content