import yfinance as yf

def get_current_price(ticker: str):
    ticker = ticker.upper()

    if ticker == "CASH":
        return 1.0

    stock = yf.Ticker(ticker)
    data = stock.history(period="1d")

    if data.empty:
        raise ValueError(f"No data for {ticker}")

    return float(data["Close"].iloc[-1])