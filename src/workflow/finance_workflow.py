import os
from typing import TypedDict, Literal
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from src.agents.market_analysis_agent import market_analysis_agent
from src.agents.goal_planning_agent import goal_planning_agent
from src.agents.news_synthesizer_agent import news_synthesizer_agent
from src.agents.tax_education_agent import tax_education_agent
from src.agents.portfolio_agent import analyze_portfolio
from src.agents.portfolio_advisor_agent import portfolio_advisor_agent
from src.core.security import security_check, sanitize_input, validate_output
from src.core.logger import log_info, log_usage

load_dotenv()

# ── State: what gets passed between nodes ─────────────────────
class FinanceState(TypedDict):
    query:    str
    agent:    str
    response: str
    ticker:   str | None
    error:    str | None

# ── Router: decides which agent to call ──────────────────────
def router_node(state: FinanceState) -> FinanceState:
    """Uses GPT to classify the query and route to the right agent."""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    prompt = f"""
You are a routing assistant for an AI Finance Assistant.
Classify the user query into exactly one of these categories:

- market    → asking about a SPECIFIC STOCK with a ticker symbol (e.g. AAPL, Tesla, Microsoft)
- news      → asking about news or headlines for a SPECIFIC STOCK
- portfolio → asking about their portfolio, holdings, current investments
- advisor   → asking for portfolio advice, recommendations, diversification tips
- goal      → asking about financial goals, retirement, savings targets, how much to save
- tax       → asking about taxes, IRA, 401k, capital gains, tax strategies
- general   → ANY other finance question including commodities (gold, oil), 
               crypto, general concepts, or anything without a specific stock ticker

Important rules:
- Only use "market" if the query mentions a specific stock or company
- Gold, silver, oil, Bitcoin questions go to "general"
- If unsure, use "general"

User query: "{state['query']}"

Reply with ONLY the category word, nothing else.
"""
    result = llm.invoke(prompt)
    agent  = result.content.strip().lower()

    valid_agents = ["market", "news", "portfolio", "advisor", "goal", "tax", "general"]
    if agent not in valid_agents:
        agent = "general"

    return {**state, "agent": agent}


# ── Routing condition ─────────────────────────────────────────
def route_to_agent(state: FinanceState) -> Literal[
    "market_node", "news_node", "portfolio_node",
    "advisor_node", "goal_node", "tax_node", "general_node"
]:
    mapping = {
        "market":    "market_node",
        "news":      "news_node",
        "portfolio": "portfolio_node",
        "advisor":   "advisor_node",
        "goal":      "goal_node",
        "tax":       "tax_node",
        "general":   "general_node",
    }
    return mapping.get(state["agent"], "general_node")


# ── Agent Nodes ───────────────────────────────────────────────
def market_node(state: FinanceState) -> FinanceState:
    try:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        ticker = llm.invoke(f"""
Extract the stock ticker symbol from this query.
If no ticker is mentioned, return 'AAPL' as default.
Return ONLY the ticker symbol in uppercase, nothing else.
Query: "{state['query']}"
""").content.strip().upper()
        response = market_analysis_agent(ticker)
        return {**state, "response": response, "ticker": ticker}
    except Exception as e:
        return {**state, "response": f"Error in market analysis: {str(e)}", "error": str(e)}


def news_node(state: FinanceState) -> FinanceState:
    try:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        ticker = llm.invoke(f"""
Extract the stock ticker symbol from this query.
If no ticker is mentioned, return 'SPY' as default.
Return ONLY the ticker symbol in uppercase, nothing else.
Query: "{state['query']}"
""").content.strip().upper()
        response = news_synthesizer_agent(ticker)
        return {**state, "response": response, "ticker": ticker}
    except Exception as e:
        return {**state, "response": f"Error in news synthesis: {str(e)}", "error": str(e)}


def portfolio_node(state: FinanceState) -> FinanceState:
    try:
        _, response = analyze_portfolio()
        return {**state, "response": response}
    except Exception as e:
        return {**state, "response": f"Error analyzing portfolio: {str(e)}", "error": str(e)}


def advisor_node(state: FinanceState) -> FinanceState:
    try:
        response = portfolio_advisor_agent()
        return {**state, "response": response}
    except Exception as e:
        return {**state, "response": f"Error in portfolio advisor: {str(e)}", "error": str(e)}


def goal_node(state: FinanceState) -> FinanceState:
    try:
        response = goal_planning_agent(
            goal_name="Retirement Fund",
            goal_amount=1_000_000,
            current_savings=10_000,
            monthly_contribution=500,
            annual_return_pct=7.0,
            years=30,
            risk_profile="moderate"
        )
        return {**state, "response": response}
    except Exception as e:
        return {**state, "response": f"Error in goal planning: {str(e)}", "error": str(e)}


def tax_node(state: FinanceState) -> FinanceState:
    try:
        response = tax_education_agent(state["query"])
        return {**state, "response": response}
    except Exception as e:
        return {**state, "response": f"Error in tax education: {str(e)}", "error": str(e)}


def general_node(state: FinanceState) -> FinanceState:
    try:
        from src.rag.retriever import retrieve_finance_context
        from src.core.openai_client import get_openai_client
        client = get_openai_client()

        rag_docs = retrieve_finance_context(state["query"], top_k=3)
        context  = "\n".join([d.get("text", "") for d in rag_docs])

        prompt = f"""
You are a financial education assistant helping beginner investors.

QUESTION: {state['query']}

RELEVANT KNOWLEDGE:
{context[:1000]}

Provide a clear, beginner-friendly answer.
End with: "This is for educational purposes only and not financial advice."
"""
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return {**state, "response": response.choices[0].message.content}
    except Exception as e:
        return {**state, "response": f"Error in general Q&A: {str(e)}", "error": str(e)}


# ── Build the Graph ───────────────────────────────────────────
def build_finance_graph():
    graph = StateGraph(FinanceState)

    graph.add_node("router",         router_node)
    graph.add_node("market_node",    market_node)
    graph.add_node("news_node",      news_node)
    graph.add_node("portfolio_node", portfolio_node)
    graph.add_node("advisor_node",   advisor_node)
    graph.add_node("goal_node",      goal_node)
    graph.add_node("tax_node",       tax_node)
    graph.add_node("general_node",   general_node)

    graph.set_entry_point("router")
    graph.add_conditional_edges("router", route_to_agent)

    for node in ["market_node", "news_node", "portfolio_node",
                 "advisor_node", "goal_node", "tax_node", "general_node"]:
        graph.add_edge(node, END)

    return graph.compile()


# ── Main entry point ──────────────────────────────────────────
def run_finance_assistant(query: str, user_id: str = "default") -> str:
    """Single entry point with full security layer."""
    
    # ── Security Gate ─────────────────────────────────────────
    is_allowed, message = security_check(query, user_id)
    if not is_allowed:
        return message
    
    # ── Sanitize input ────────────────────────────────────────
    query = sanitize_input(query)

    # ── Logging ───────────────────────────────────────────────
    # print(f"[INFO] Querying OpenAI | agent routing for: '{query[:50]}'")
    log_info("workflow", "Querying OpenAI", query=query[:50])

    
    # ── Run the graph ─────────────────────────────────────────
    graph = build_finance_graph()
    initial_state: FinanceState = {
        "query":    query,
        "agent":    "",
        "response": "",
        "ticker":   None,
        "error":    None,
    }
    result = graph.invoke(initial_state)
    # print(f"[USAGE] agent={result['agent']} | query_length={len(query)}")
    log_usage("workflow", "Query processed", agent=result['agent'], query_length=str(len(query)))
    response = result["response"]
    
    # ── Validate output ───────────────────────────────────────
    is_safe, reason = validate_output(response)
    if not is_safe:
        return "I wasn't able to generate a safe response. Please try rephrasing your question."
    
    return response

