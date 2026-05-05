from src.agents.portfolio_agent import analyze_portfolio
from src.core.openai_client import get_openai_client

client = get_openai_client()


def portfolio_advisor_agent():
    """
    Gives educational suggestions based on portfolio analysis.
    Does NOT execute trades.
    """

    portfolio_df, basic_analysis = analyze_portfolio()

    portfolio_summary = portfolio_df.to_string(index=False)

    prompt = f"""
You are a financial education assistant.

Review this simulated portfolio and provide educational suggestions.

Portfolio:
{portfolio_summary}

Existing analysis:
{basic_analysis}

Rules:
- Do NOT give personalized financial advice.
- Do NOT directly say "buy" or "sell".
- Use wording like "you may consider reviewing..."
- Identify concentration risk.
- Identify diversification issues.
- Explain possible educational actions.
- Mention that actual trades require user confirmation.
- Add a short disclaimer.

Answer:
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a cautious financial education assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content