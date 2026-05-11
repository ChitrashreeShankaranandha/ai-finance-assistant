import pandas as pd
from src.utils.market_data import get_current_price
from src.core.logger import log_trade


DEFAULT_PORTFOLIO_PATH = "src/data/demo_portfolio.csv"


def load_portfolio(path: str = DEFAULT_PORTFOLIO_PATH):
    df = pd.read_csv(path)
    df["shares"]        = df["shares"].astype(float)
    df["avg_buy_price"] = df["avg_buy_price"].astype(float)
    return df


def save_portfolio(df, path: str = DEFAULT_PORTFOLIO_PATH):
    df["shares"]        = df["shares"].astype(float)
    df["avg_buy_price"] = df["avg_buy_price"].astype(float)
    df.to_csv(path, index=False)


def get_cash_balance(df):
    cash_row = df[df["ticker"] == "CASH"]
    if cash_row.empty:
        return 0.0
    return float(cash_row.iloc[0]["shares"])


def simulated_buy(ticker: str, shares: float, portfolio_path: str = DEFAULT_PORTFOLIO_PATH):
    ticker = ticker.upper()
    shares = float(shares)

    if ticker == "CASH":
        return "Cannot buy CASH."

    df            = load_portfolio(portfolio_path)
    current_price = get_current_price(ticker)
    total_cost    = current_price * shares
    cash_balance  = get_cash_balance(df)

    if total_cost > cash_balance:
        return (
            f"Simulated buy failed: not enough cash. "
            f"Required: ${total_cost:.2f}, Available: ${cash_balance:.2f}"
        )

    if ticker in df["ticker"].values:
        idx           = df.index[df["ticker"] == ticker][0]
        old_shares    = float(df.loc[idx, "shares"])
        old_avg_price = float(df.loc[idx, "avg_buy_price"])

        new_total_shares = old_shares + shares
        new_avg_price    = ((old_shares * old_avg_price) + total_cost) / new_total_shares

        df.loc[idx, "shares"]        = new_total_shares
        df.loc[idx, "avg_buy_price"] = new_avg_price
    else:
        new_row = pd.DataFrame([{
            "ticker":        ticker,
            "shares":        shares,
            "avg_buy_price": current_price
        }])
        df = pd.concat([df, new_row], ignore_index=True)

    cash_idx                      = df.index[df["ticker"] == "CASH"][0]
    df.loc[cash_idx, "shares"]    = cash_balance - total_cost
    save_portfolio(df, portfolio_path)

    # print(f"[TRADE] action=BUY | ticker={ticker} | shares={shares} | price={current_price:.2f} | total=${total_cost:.2f}")
    log_trade("trading", "Buy executed", ticker=ticker, shares=shares, price=f"${current_price:.2f}", total=f"${total_cost:.2f}")


    return (
        f"Simulated buy completed: Bought {shares} shares of {ticker} "
        f"at approximately ${current_price:.2f} per share. "
        f"Total cost: ${total_cost:.2f}"
    )


def simulated_sell(ticker: str, shares: float, portfolio_path: str = DEFAULT_PORTFOLIO_PATH):
    ticker = ticker.upper()
    shares = float(shares)

    if ticker == "CASH":
        return "Cannot sell CASH."

    df = load_portfolio(portfolio_path)

    if ticker not in df["ticker"].values:
        return f"Simulated sell failed: {ticker} is not in the portfolio."

    idx          = df.index[df["ticker"] == ticker][0]
    owned_shares = float(df.loc[idx, "shares"])

    if shares > owned_shares:
        return (
            f"Simulated sell failed: not enough shares. "
            f"Trying to sell {shares}, but only own {owned_shares}."
        )

    current_price = get_current_price(ticker)
    sale_value    = current_price * shares

    df.loc[idx, "shares"] = owned_shares - shares

    if float(df.loc[idx, "shares"]) == 0:
        df = df.drop(index=idx)

    cash_idx                   = df.index[df["ticker"] == "CASH"][0]
    cash_balance               = float(df.loc[cash_idx, "shares"])
    df.loc[cash_idx, "shares"] = cash_balance + sale_value

    save_portfolio(df, portfolio_path)

    # print(f"[TRADE] action=SELL | ticker={ticker} | shares={shares} | price={current_price:.2f} | value=${sale_value:.2f}")
    log_trade("trading", "Sell executed", ticker=ticker, shares=shares, price=f"${current_price:.2f}", value=f"${sale_value:.2f}")


    return (
        f"Simulated sell completed: Sold {shares} shares of {ticker} "
        f"at approximately ${current_price:.2f} per share. "
        f"Sale value: ${sale_value:.2f}"
    )