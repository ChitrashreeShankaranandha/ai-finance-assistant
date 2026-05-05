
import yfinance as yf
from src.core.openai_client import get_openai_client

client = get_openai_client()

def get_stock_snapshot(ticker: str) -> dict:
    """Fetch real-time stock data from yFinance."""
    try:
        stock = yf.Ticker(ticker)
        info  = stock.info
        hist  = stock.history(period="5d")

        if hist.empty:
            return {"error": f"No data found for ticker {ticker}"}

        current_price = round(hist["Close"].iloc[-1], 2)
        prev_price    = round(hist["Close"].iloc[-2], 2)
        change_pct    = round(((current_price - prev_price) / prev_price) * 100, 2)

        return {
            "ticker":         ticker.upper(),
            "company_name":   info.get("longName", ticker),
            "current_price":  current_price,
            "previous_close": prev_price,
            "change_pct":     change_pct,
            "market_cap":     info.get("marketCap", "N/A"),
            "pe_ratio":       info.get("trailingPE", "N/A"),
            "52w_high":       info.get("fiftyTwoWeekHigh", "N/A"),
            "52w_low":        info.get("fiftyTwoWeekLow", "N/A"),
            "volume":         info.get("volume", "N/A"),
            "sector":         info.get("sector", "N/A"),
        }
    except Exception as e:
        return {"error": str(e)}


def market_analysis_agent(ticker: str) -> str:
    """Analyzes a stock and returns educational insights using GPT."""
    snapshot = get_stock_snapshot(ticker)

    if "error" in snapshot:
        return f"Could not retrieve data for {ticker}: {snapshot['error']}"

    prompt = f"""
You are a financial education assistant helping beginner investors
understand stock market data.

Here is current market data for {snapshot['company_name']} ({snapshot['ticker']}):
- Current Price:  ${snapshot['current_price']}
- Previous Close: ${snapshot['previous_close']}
- Price Change:   {snapshot['change_pct']}%
- Market Cap:     {snapshot['market_cap']}
- P/E Ratio:      {snapshot['pe_ratio']}
- 52-Week High:   ${snapshot['52w_high']}
- 52-Week Low:    ${snapshot['52w_low']}
- Volume:         {snapshot['volume']}
- Sector:         {snapshot['sector']}

Please provide:
1. A simple plain-English explanation of what this data means for a beginner
2. What the P/E ratio tells us about this stock valuation
3. Where the stock sits relative to its 52-week range (near high, low, or middle?)
4. One key educational takeaway for a beginner investor

Always end with: "This is for educational purposes only and not financial advice."
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content
