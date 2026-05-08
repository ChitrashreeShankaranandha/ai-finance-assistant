"""
MCP Server for AI Finance Assistant.
Exposes finance tools to Claude Desktop via Model Context Protocol.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import asyncio
import yfinance as yf
from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

load_dotenv()

# ── Initialize MCP Server ─────────────────────────────────────
server = Server("ai-finance-assistant")


# ── List Available Tools ──────────────────────────────────────
@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_stock_info",
            description="Get real-time stock price and key metrics for any company. Input company name or ticker symbol.",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol or company name (e.g. AAPL, Tesla, Microsoft)"
                    }
                },
                "required": ["ticker"]
            }
        ),
        Tool(
            name="analyze_portfolio",
            description="Analyze the demo investment portfolio with live market prices and return holdings summary.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="calculate_goal",
            description="Calculate if a user is on track for a financial goal using compound interest math.",
            inputSchema={
                "type": "object",
                "properties": {
                    "goal_name":             {"type": "string",  "description": "Name of the financial goal"},
                    "goal_amount":           {"type": "number",  "description": "Target amount in dollars"},
                    "current_savings":       {"type": "number",  "description": "Current savings in dollars"},
                    "monthly_contribution":  {"type": "number",  "description": "Monthly contribution in dollars"},
                    "annual_return_pct":     {"type": "number",  "description": "Expected annual return percentage"},
                    "years":                 {"type": "integer", "description": "Number of years to invest"}
                },
                "required": ["goal_name", "goal_amount", "current_savings",
                             "monthly_contribution", "annual_return_pct", "years"]
            }
        ),
        Tool(
            name="get_stock_news",
            description="Get latest financial news headlines for a stock with AI synthesis.",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol or company name"
                    }
                },
                "required": ["ticker"]
            }
        ),
        Tool(
            name="answer_finance_question",
            description="Answer any general finance or investing question using RAG knowledge base.",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "Finance or investing question to answer"
                    }
                },
                "required": ["question"]
            }
        ),
    ]


# ── Tool Handlers ─────────────────────────────────────────────
@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:

    # ── Tool 1: Stock Info ────────────────────────────────────
    if name == "get_stock_info":
        try:
            from src.agents.market_analysis_agent import get_stock_snapshot, market_analysis_agent

            # Resolve company name to ticker
            search = yf.Search(arguments["ticker"])
            if search.quotes:
                resolved = search.quotes[0]["symbol"]
            else:
                resolved = arguments["ticker"].upper()

            snapshot = get_stock_snapshot(resolved)
            if "error" in snapshot:
                return [TextContent(type="text", text=f"Error: {snapshot['error']}")]

            analysis = market_analysis_agent(resolved)
            result = f"""
📊 **{snapshot['company_name']} ({resolved})**
- Current Price:  ${snapshot['current_price']}
- Change:         {snapshot['change_pct']}%
- Market Cap:     {snapshot['market_cap']}
- P/E Ratio:      {snapshot['pe_ratio']}
- 52W High:       ${snapshot['52w_high']}
- 52W Low:        ${snapshot['52w_low']}
- Sector:         {snapshot['sector']}

---
{analysis}
"""
            return [TextContent(type="text", text=result)]

        except Exception as e:
            return [TextContent(type="text", text=f"Error fetching stock info: {str(e)}")]

    # ── Tool 2: Portfolio Analysis ────────────────────────────
    elif name == "analyze_portfolio":
        try:
            from src.agents.portfolio_agent import analyze_portfolio
            df, analysis = analyze_portfolio()

            total_value = df["current_value"].sum()
            total_cost  = (df["shares"] * df["avg_buy_price"]).sum()
            total_gain  = df["gain_loss"].sum()
            holdings    = df[["ticker", "shares", "current_price",
                              "current_value", "gain_loss"]].to_string(index=False)

            result = f"""
💼 **Portfolio Summary**
Total Value:     ${total_value:,.2f}
Total Cost:      ${total_cost:,.2f}
Total Gain/Loss: ${total_gain:,.2f}

**Holdings:**
{holdings}

---
**AI Analysis:**
{analysis}
"""
            return [TextContent(type="text", text=result)]

        except Exception as e:
            return [TextContent(type="text", text=f"Error analyzing portfolio: {str(e)}")]

    # ── Tool 3: Goal Calculator ───────────────────────────────
    elif name == "calculate_goal":
        try:
            from src.agents.goal_planning_agent import calculate_goal_metrics, goal_planning_agent

            metrics = calculate_goal_metrics(
                arguments["goal_amount"],
                arguments["current_savings"],
                arguments["monthly_contribution"],
                arguments["annual_return_pct"],
                arguments["years"]
            )
            advice = goal_planning_agent(
                arguments["goal_name"],
                arguments["goal_amount"],
                arguments["current_savings"],
                arguments["monthly_contribution"],
                arguments["annual_return_pct"],
                arguments["years"],
                "moderate"
            )
            result = f"""
🎯 **Goal: {arguments['goal_name']}**
Target Amount:    ${metrics['goal_amount']:,.2f}
Projected Value:  ${metrics['projected_value']:,.2f}
On Track:         {'✅ YES' if metrics['on_track'] else '❌ NOT YET'}
Gap:              ${abs(metrics['gap']):,.2f} {'surplus' if metrics['on_track'] else 'shortfall'}
Required Monthly: ${metrics['required_monthly']:,.2f}

---
{advice}
"""
            return [TextContent(type="text", text=result)]

        except Exception as e:
            return [TextContent(type="text", text=f"Error calculating goal: {str(e)}")]

    # ── Tool 4: Stock News ────────────────────────────────────
    elif name == "get_stock_news":
        try:
            from src.agents.news_synthesizer_agent import get_stock_news, news_synthesizer_agent

            search = yf.Search(arguments["ticker"])
            if search.quotes:
                resolved = search.quotes[0]["symbol"]
                company  = search.quotes[0].get("longname", resolved)
            else:
                resolved = arguments["ticker"].upper()
                company  = resolved

            headlines    = get_stock_news(resolved)
            headline_text = "\n".join([
                f"{i+1}. {h['title']} ({h['publisher']})"
                for i, h in enumerate(headlines)
            ])
            synthesis = news_synthesizer_agent(resolved)

            result = f"""
📰 **Latest News: {company} ({resolved})**

**Headlines:**
{headline_text}

---
**AI Synthesis:**
{synthesis}
"""
            return [TextContent(type="text", text=result)]

        except Exception as e:
            return [TextContent(type="text", text=f"Error fetching news: {str(e)}")]

    # ── Tool 5: Finance Q&A ───────────────────────────────────
    elif name == "answer_finance_question":
        try:
            from src.workflow.finance_workflow import run_finance_assistant
            from src.core.security import security_check

            question   = arguments["question"]
            is_allowed, message = security_check(question)

            if not is_allowed:
                return [TextContent(type="text", text=message)]

            answer = run_finance_assistant(question)
            return [TextContent(type="text", text=answer)]

        except Exception as e:
            return [TextContent(type="text", text=f"Error answering question: {str(e)}")]

    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


# ── Run Server ────────────────────────────────────────────────
async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())