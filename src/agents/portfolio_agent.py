import pandas as pd

from src.core.openai_client import get_openai_client
from src.utils.market_data import get_current_price

client = get_openai_client()

PORTFOLIO_PATH = "/content/drive/MyDrive/ai_finance_assistant/src/data/demo_portfolio.csv"


def load_portfolio():
    df = pd.read_csv(PORTFOLIO_PATH)

    # Ensure correct data types
    df["shares"] = df["shares"].astype(float)
    df["avg_buy_price"] = df["avg_buy_price"].astype(float)

    return df


def analyze_portfolio():
    """
    Analyze demo portfolio using live market prices.
    """

    df = load_portfolio()

    current_prices = []
    current_values = []
    gains_losses = []

    for _, row in df.iterrows():
        ticker = row["ticker"]
        shares = float(row["shares"])
        avg_buy_price = float(row["avg_buy_price"])

        current_price = get_current_price(ticker)
        current_value = shares * current_price
        cost_basis = shares * avg_buy_price
        gain_loss = current_value - cost_basis

        current_prices.append(current_price)
        current_values.append(current_value)
        gains_losses.append(gain_loss)

    df["current_price"] = current_prices
    df["current_value"] = current_values
    df["gain_loss"] = gains_losses

    total_value = df["current_value"].sum()
    df["allocation_percent"] = (df["current_value"] / total_value) * 100

    portfolio_summary = df.to_string(index=False)

    prompt = f"""
You are a financial education assistant.

Analyze this simulated demo portfolio for educational purposes only.

Portfolio:
{portfolio_summary}

Rules:
- Do not give personalized financial advice.
- Do not directly tell the user to buy or sell.
- Explain concentration, diversification, and risk in beginner-friendly language.
- Mention this is a simulated portfolio.
- Add a short disclaimer.

Answer:
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a careful financial education assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    return df, response.choices[0].message.content