import yfinance as yf
from src.core.openai_client import get_openai_client
from src.rag.retriever import retrieve_finance_context

client = get_openai_client()

def get_stock_news(ticker: str, max_news: int = 5) -> list:
    """Fetch recent news headlines for a stock using yFinance."""
    try:
        stock = yf.Ticker(ticker)
        news  = stock.news or []
        results = []
        for item in news[:max_news]:
            content = item.get("content", {})
            results.append({
                "title":     content.get("title", "No title"),
                "summary":   content.get("summary", ""),
                "publisher": content.get("provider", {}).get("displayName", "Unknown"),
                "url":       content.get("canonicalUrl", {}).get("url", ""),
            })
        return results
    except Exception as e:
        return [{"title": f"Error fetching news: {str(e)}",
                 "summary": "", "publisher": "", "url": ""}]


def news_synthesizer_agent(ticker: str) -> str:
    """
    Fetches recent news for a stock, enriches with RAG context,
    and generates a beginner-friendly synthesis using GPT.
    """
    news_items  = get_stock_news(ticker)
    rag_docs    = retrieve_finance_context("how does company news affect stock prices investing", top_k=2)
    rag_context = " ".join([d["text"] for d in rag_docs if "text" in d])

    news_text = ""
    for i, item in enumerate(news_items, 1):
        news_text += f"{i}. {item['title']}\n"
        if item["summary"]:
            news_text += f"   Summary: {item['summary'][:200]}\n"
        news_text += f"   Source: {item['publisher']}\n\n"

    if not news_text.strip():
        news_text = "No recent news found for this ticker."

    prompt = f"""
You are a financial education assistant helping beginner investors
understand recent news about a company and its potential market impact.

RECENT NEWS FOR {ticker.upper()}:
{news_text}

EDUCATIONAL CONTEXT:
{rag_context[:500] if rag_context else "Focus on general principles of how news affects stocks."}

Please provide:
1. A 2-3 sentence plain-English summary of the overall news sentiment (positive/negative/neutral)
2. For each headline: one sentence explaining what it could mean for investors
3. What type of news tends to move stock prices most (educational insight)
4. One key lesson about not making investment decisions based on news alone
5. Suggested follow-up questions a beginner should research

Always end with: "This is for educational purposes only and not financial advice."
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )
    return response.choices[0].message.content