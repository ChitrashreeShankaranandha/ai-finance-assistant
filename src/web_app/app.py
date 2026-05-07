"""
AI Finance Assistant - Streamlit Web Application
Multi-tab interface for the full finance assistant system.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# ── Page Config ───────────────────────────────────────────────
st.set_page_config(
    page_title="AI Finance Assistant",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
    .disclaimer {
        font-size: 0.8rem;
        color: #888;
        font-style: italic;
        padding: 0.5rem;
        border-left: 3px solid #1f77b4;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────
st.markdown('<div class="main-header">💰 AI Finance Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Democratizing Financial Literacy Through Intelligent AI</div>', unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/money--v1.png", width=80)
    st.title("Navigation")
    st.markdown("---")
    st.markdown("### 🔒 Security Status")
    st.success("✅ Security Layer Active")
    st.info("✅ RAG Knowledge Base Connected")
    st.info("✅ LangGraph Router Online")
    st.markdown("---")
    st.markdown("### ⚠️ Disclaimer")
    st.markdown("""
    <div class="disclaimer">
    This tool is for <b>educational purposes only</b> 
    and does not constitute financial advice. 
    Always consult a qualified financial advisor.
    </div>
    """, unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💬 Finance Chat",
    "📊 Portfolio",
    "📈 Market Analysis",
    "🎯 Goal Planner",
    "📰 News"
])


# ════════════════════════════════════════════════════════════════
# TAB 1: FINANCE CHAT
# ════════════════════════════════════════════════════════════════
with tab1:
    st.header("💬 Ask Anything About Finance")
    st.markdown("Chat with our AI — it automatically routes your question to the right specialist agent.")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "👋 Hello! I'm your AI Finance Assistant. Ask me anything about investing, stocks, taxes, retirement planning, or financial news!"}
        ]

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    if prompt := st.chat_input("Ask a finance question..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get response from LangGraph
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    from src.workflow.finance_workflow import run_finance_assistant
                    response = run_finance_assistant(prompt)
                except Exception as e:
                    response = f"Sorry, I encountered an error: {str(e)}"

            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

    # Quick question buttons
    st.markdown("---")
    st.markdown("**💡 Try asking:**")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("What is dollar cost averaging?"):
            st.session_state.messages.append({"role": "user", "content": "What is dollar cost averaging?"})
            st.rerun()
    with col2:
        if st.button("How do Roth IRAs work?"):
            st.session_state.messages.append({"role": "user", "content": "How do Roth IRAs work?"})
            st.rerun()
    with col3:
        if st.button("Explain diversification"):
            st.session_state.messages.append({"role": "user", "content": "Explain diversification"})
            st.rerun()


# ════════════════════════════════════════════════════════════════
# TAB 2: PORTFOLIO
# ════════════════════════════════════════════════════════════════
with tab2:
    st.header("📊 Portfolio Analysis & Trading")

    # ── Two column layout: Analysis | Trading ─────────────────
    left_col, right_col = st.columns([3, 2])

    with right_col:
        st.subheader("💹 Simulated Trading")
        st.caption("Practice buying and selling using your demo cash balance.")
        
        # Always show live cash balance
        try:
            import pandas as pd
            df_cash = pd.read_csv("src/data/demo_portfolio.csv")
            cash_row = df_cash[df_cash["ticker"] == "CASH"]
            if not cash_row.empty:
                cash_balance = float(cash_row.iloc[0]["shares"])
                st.metric("💵 Available Cash", f"${cash_balance:,.2f}")
        except Exception:
            pass

        trade_stock = st.text_input(
            "Stock to Buy/Sell",
            placeholder="e.g. Apple, Tesla, AAPL",
            key="trade_stock"
        ).strip()

        trade_shares = st.number_input(
            "Number of Shares",
            min_value=0.1,
            max_value=10000.0,
            value=1.0,
            step=0.1,
            key="trade_shares"
        )

        # Live price preview
        if trade_stock:
            try:
                import yfinance as yf
                search = yf.Search(trade_stock)
                if search.quotes:
                    preview_ticker  = search.quotes[0]["symbol"]
                    preview_company = search.quotes[0].get("longname", preview_ticker)
                    from src.utils.market_data import get_current_price
                    preview_price   = get_current_price(preview_ticker)
                    estimated_cost  = preview_price * trade_shares
                    st.info(f"🔍 **{preview_company}** ({preview_ticker})")
                    col_a, col_b = st.columns(2)
                    col_a.metric("Live Price",     f"${preview_price:.2f}")
                    col_b.metric("Estimated Cost", f"${estimated_cost:,.2f}")
            except Exception:
                pass

        buy_col, sell_col = st.columns(2)
        buy_btn  = buy_col.button("🟢 Buy",  type="primary", use_container_width=True)
        sell_btn = sell_col.button("🔴 Sell", use_container_width=True)

        if buy_btn or sell_btn:
            if not trade_stock:
                st.warning("Please enter a stock name or ticker.")
            else:
                try:
                    import yfinance as yf
                    search = yf.Search(trade_stock)
                    if search.quotes:
                        resolved = search.quotes[0]["symbol"]
                        company  = search.quotes[0].get("longname", resolved)
                    else:
                        st.error(f"Could not find stock: {trade_stock}")
                        st.stop()
                except Exception as e:
                    st.error(f"Lookup failed: {str(e)}")
                    st.stop()

                from src.agents.trading_agent import simulated_buy, simulated_sell

                with st.spinner(f"Processing trade for {company} ({resolved})..."):
                    if buy_btn:
                        result = simulated_buy(resolved, trade_shares)
                    else:
                        result = simulated_sell(resolved, trade_shares)

                if "completed" in result.lower():
                    st.success(f"✅ {result}")
                    st.info("🔄 Click 'Analyze Portfolio' to see updated holdings.")
                else:
                    st.error(f"❌ {result}")

    with left_col:
        st.subheader("📊 Portfolio Analysis")
        st.caption("View your holdings with live market prices and AI-powered insights.")
        analyze_btn = st.button("🔄 Analyze Portfolio", type="primary")

        if analyze_btn:
            with st.spinner("Fetching live prices and analyzing portfolio..."):
                try:
                    from src.agents.portfolio_agent import analyze_portfolio
                    df, analysis = analyze_portfolio()

                    # ── Cash balance ──────────────────────────
                    cash_row = df[df["ticker"] == "CASH"]
                    if not cash_row.empty:
                        cash_balance = float(cash_row.iloc[0]["shares"])
                        st.info(f"💵 Available Cash: **${cash_balance:,.2f}**")

                    # ── Metrics ───────────────────────────────
                    total_value    = df["current_value"].sum()
                    total_cost     = (df["shares"] * df["avg_buy_price"]).sum()
                    total_gain     = df["gain_loss"].sum()
                    total_gain_pct = ((total_value - total_cost) / total_cost) * 100

                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("💼 Total Value",     f"${total_value:,.2f}")
                    col2.metric("💵 Total Cost",      f"${total_cost:,.2f}")
                    col3.metric("📈 Total Gain/Loss", f"${total_gain:,.2f}",
                               delta=f"{total_gain_pct:.1f}%")
                    col4.metric("🏢 Holdings",        f"{len(df)} stocks")

                    st.markdown("---")

                    # ── Holdings Table + Pie Chart ────────────
                    tbl_col, pie_col = st.columns(2)

                    with tbl_col:
                        st.subheader("📋 Holdings")
                        display_df = df[["ticker", "shares", "avg_buy_price",
                                        "current_price", "current_value",
                                        "gain_loss", "allocation_percent"]].copy()
                        display_df.columns = ["Ticker", "Shares", "Avg Buy",
                                             "Current", "Value",
                                             "Gain/Loss", "Allocation %"]
                        display_df = display_df.round(2)
                        st.dataframe(display_df, use_container_width=True)

                    with pie_col:
                        st.subheader("🥧 Allocation")
                        fig = px.pie(
                            df, values="current_value", names="ticker",
                            color_discrete_sequence=px.colors.qualitative.Set3
                        )
                        fig.update_traces(textposition='inside',
                                         textinfo='percent+label')
                        st.plotly_chart(fig, use_container_width=True)

                    # ── Gain/Loss Bar Chart ───────────────────
                    st.subheader("📊 Gain/Loss by Stock")
                    colors = ["green" if x >= 0 else "red" for x in df["gain_loss"]]
                    fig2 = go.Figure(go.Bar(
                        x=df["ticker"], y=df["gain_loss"],
                        marker_color=colors,
                        text=[f"${x:,.2f}" for x in df["gain_loss"]],
                        textposition="outside"
                    ))
                    fig2.update_layout(
                        xaxis_title="Stock",
                        yaxis_title="Gain/Loss ($)",
                        showlegend=False
                    )
                    st.plotly_chart(fig2, use_container_width=True)

                    # ── AI Analysis ───────────────────────────
                    st.subheader("🤖 AI Portfolio Analysis")
                    st.markdown(analysis)

                except Exception as e:
                    st.error(f"Error analyzing portfolio: {str(e)}")
        else:
            st.info("👆 Click 'Analyze Portfolio' to load your holdings with live prices.")


# ════════════════════════════════════════════════════════════════
# TAB 3: MARKET ANALYSIS
# ════════════════════════════════════════════════════════════════
with tab3:
    st.header("📈 Market Analysis")
    st.markdown("Get real-time stock data and beginner-friendly analysis for any stock.")

    col1, col2 = st.columns([2, 1])
    with col1:
        ticker_input = st.text_input(
            "Enter Stock Ticker or Company Name",
            placeholder="e.g. Apple, Tesla, Microsoft, Google",
            max_chars=50
        ).strip()
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        analyze_btn = st.button("🔍 Analyze", type="primary")

    st.caption("💡 Tip: You can type a company name or ticker symbol")

    # Quick ticker buttons
    st.markdown("**Popular stocks:**")
    qcol1, qcol2, qcol3, qcol4, qcol5 = st.columns(5)
    if qcol1.button("Apple"):
        ticker_input = "Apple"
        analyze_btn  = True
    if qcol2.button("Microsoft"):
        ticker_input = "Microsoft"
        analyze_btn  = True
    if qcol3.button("Tesla"):
        ticker_input = "Tesla"
        analyze_btn  = True
    if qcol4.button("Google"):
        ticker_input = "Google"
        analyze_btn  = True
    if qcol5.button("Amazon"):
        ticker_input = "Amazon"
        analyze_btn  = True

    if analyze_btn and ticker_input:
        # ── Resolve company name to ticker ────────────────────
        with st.spinner("Looking up stock..."):
            try:
                import yfinance as yf
                search_results = yf.Search(ticker_input)
                quotes = search_results.quotes
                if quotes:
                    resolved_ticker = quotes[0]["symbol"]
                    company_name    = quotes[0].get("longname", resolved_ticker)
                    st.info(f"🔍 Found: **{company_name}** ({resolved_ticker})")
                else:
                    st.error(f"Could not find a stock for '{ticker_input}'. Please try a different name.")
                    st.stop()
            except Exception as e:
                st.error(f"Lookup failed: {str(e)}")
                st.stop()

        with st.spinner(f"Fetching live data for {resolved_ticker}..."):
            try:
                from src.agents.market_analysis_agent import get_stock_snapshot, market_analysis_agent

                snapshot = get_stock_snapshot(resolved_ticker)

                if "error" not in snapshot:
                    # ── Metrics ───────────────────────────────
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("💵 Price",     f"${snapshot['current_price']}",
                               delta=f"{snapshot['change_pct']}%")
                    col2.metric("📊 P/E Ratio", str(snapshot['pe_ratio']))
                    col3.metric("🔝 52W High",  f"${snapshot['52w_high']}")
                    col4.metric("🔻 52W Low",   f"${snapshot['52w_low']}")

                    # ── Price gauge chart ─────────────────────
                    st.subheader(f"📍 {snapshot['company_name']} — 52-Week Price Range")
                    try:
                        low  = float(snapshot['52w_low'])
                        high = float(snapshot['52w_high'])
                        curr = float(snapshot['current_price'])

                        fig = go.Figure(go.Indicator(
                            mode="gauge+number",
                            value=curr,
                            title={"text": f"{resolved_ticker} Price vs 52W Range"},
                            gauge={
                                "axis": {"range": [low, high]},
                                "bar":  {"color": "darkblue"},
                                "steps": [
                                    {"range": [low, low + (high-low)*0.33], "color": "lightcoral"},
                                    {"range": [low + (high-low)*0.33, low + (high-low)*0.66], "color": "lightyellow"},
                                    {"range": [low + (high-low)*0.66, high], "color": "lightgreen"},
                                ]
                            }
                        ))
                        st.plotly_chart(fig, use_container_width=True)
                    except Exception:
                        pass

                    # ── AI Analysis ───────────────────────────
                    st.subheader("🤖 AI Analysis")
                    analysis = market_analysis_agent(resolved_ticker)
                    st.markdown(analysis)

                else:
                    st.error(f"Could not fetch data: {snapshot['error']}")

            except Exception as e:
                st.error(f"Error: {str(e)}")


# ════════════════════════════════════════════════════════════════
# TAB 4: GOAL PLANNER
# ════════════════════════════════════════════════════════════════
with tab4:
    st.header("🎯 Financial Goal Planner")
    st.markdown("Calculate if you're on track for your financial goals.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📝 Your Goal Details")
        goal_name    = st.text_input("Goal Name", value="Retirement Fund")
        goal_amount  = st.number_input("Target Amount ($)", min_value=1000,
                                       max_value=10_000_000, value=1_000_000, step=10_000)
        current_savings = st.number_input("Current Savings ($)", min_value=0,
                                          max_value=10_000_000, value=10_000, step=1000)
        monthly_contribution = st.number_input("Monthly Contribution ($)", min_value=0,
                                               max_value=100_000, value=500, step=100)

    with col2:
            st.subheader("⚙️ Investment Settings")
            years = st.slider("Time Horizon (Years)", min_value=1, max_value=50, value=30)
            
            risk_profile = st.selectbox("Risk Profile",
                                        ["conservative", "moderate", "aggressive"],
                                        index=1)
            
            # Auto-set return based on risk profile
            risk_return_map = {
                "conservative": 4.5,
                "moderate":     7.0,
                "aggressive":   10.0,
            }
            default_return = risk_return_map[risk_profile]
            
            annual_return = st.slider(
                "Expected Annual Return (%)",
                min_value=1.0,
                max_value=15.0,
                value=default_return,  # ← changes with risk profile
                step=0.5
            )
            
            st.caption(f"💡 {risk_profile.capitalize()} investors typically expect {default_return}% annual return")

    if st.button("🚀 Calculate My Plan", type="primary"):
        with st.spinner("Calculating your financial plan..."):
            try:
                from src.agents.goal_planning_agent import calculate_goal_metrics, goal_planning_agent

                metrics = calculate_goal_metrics(
                    goal_amount, current_savings,
                    monthly_contribution, annual_return, years
                )

                # ── Results Metrics ───────────────────────────
                st.markdown("---")
                st.subheader("📊 Your Results")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("🎯 Target",    f"${metrics['goal_amount']:,.0f}")
                col2.metric("📈 Projected", f"${metrics['projected_value']:,.0f}")

                gap_label = "Surplus" if metrics["on_track"] else "Shortfall"
                col3.metric(f"{'✅' if metrics['on_track'] else '⚠️'} {gap_label}",
                           f"${abs(metrics['gap']):,.0f}")
                col4.metric("💰 Required Monthly", f"${metrics['required_monthly']:,.0f}")

                # ── On track banner ───────────────────────────
                if metrics["on_track"]:
                    st.success(f"🎉 You're ON TRACK for your {goal_name} goal!")
                else:
                    st.warning(f"⚠️ You're not yet on track. You need ${metrics['required_monthly']:,.0f}/month to hit your goal.")

                # ── Projection Chart ──────────────────────────
                st.subheader("📈 Savings Projection Over Time")
                monthly_rate = annual_return / 100 / 12
                projection_data = []
                for year in range(0, years + 1):
                    months = year * 12
                    fv_savings = current_savings * ((1 + monthly_rate) ** months)
                    if monthly_rate > 0:
                        fv_contrib = monthly_contribution * (
                            ((1 + monthly_rate) ** months - 1) / monthly_rate
                        )
                    else:
                        fv_contrib = monthly_contribution * months
                    projection_data.append({
                        "Year": year,
                        "Projected Value": round(fv_savings + fv_contrib, 2),
                        "Target": goal_amount
                    })

                proj_df = pd.DataFrame(projection_data)
                fig = px.line(proj_df, x="Year",
                             y=["Projected Value", "Target"],
                             color_discrete_map={
                                 "Projected Value": "#1f77b4",
                                 "Target": "#ff7f0e"
                             })
                fig.update_layout(yaxis_title="Amount ($)", xaxis_title="Years from Now")
                st.plotly_chart(fig, use_container_width=True)

                # ── AI Advice ─────────────────────────────────
                st.subheader("🤖 AI Financial Coach")
                advice = goal_planning_agent(
                    goal_name, goal_amount, current_savings,
                    monthly_contribution, annual_return, years, risk_profile
                )
                st.markdown(advice)

            except Exception as e:
                st.error(f"Error calculating plan: {str(e)}")


# ════════════════════════════════════════════════════════════════
# TAB 5: NEWS
# ════════════════════════════════════════════════════════════════
with tab5:
    st.header("📰 Financial News Synthesizer")
    st.markdown("Get AI-synthesized financial news for any stock.")

    news_ticker = st.text_input(
        "Enter Stock Ticker for News",
        placeholder="e.g. TSLA, AAPL, MSFT",
        max_chars=10
    ).upper()

    if st.button("📡 Get News", type="primary") and news_ticker:
        with st.spinner(f"Fetching latest news for {news_ticker}..."):
            try:
                from src.agents.news_synthesizer_agent import get_stock_news, news_synthesizer_agent

                # Show raw headlines first
                news_items = get_stock_news(news_ticker)
                if news_items:
                    st.subheader(f"📋 Latest Headlines for {news_ticker}")
                    for i, item in enumerate(news_items, 1):
                        with st.expander(f"{i}. {item['title']}"):
                            if item["summary"]:
                                st.write(item["summary"])
                            st.caption(f"Source: {item['publisher']}")
                            if item["url"]:
                                st.markdown(f"[Read more]({item['url']})")

                # AI synthesis
                st.subheader("🤖 AI News Synthesis")
                synthesis = news_synthesizer_agent(news_ticker)
                st.markdown(synthesis)

            except Exception as e:
                st.error(f"Error fetching news: {str(e)}")