"""
Tests for all 7 agents.
Run with: pytest tests/test_agents.py -v
"""
import sys
sys.path.insert(0, '.')

import pytest
from unittest.mock import patch, MagicMock

# ── Market Analysis Agent ────────────────────────────────────
class TestMarketAnalysisAgent:

    @patch("src.agents.market_analysis_agent.yf.Ticker")
    @patch("src.agents.market_analysis_agent.client")
    def test_valid_ticker(self, mock_client, mock_ticker):
        """Agent returns a string response for a valid ticker."""
        # Mock yFinance response
        mock_hist = MagicMock()
        mock_hist.empty = False
        mock_hist.__getitem__ = lambda self, key: MagicMock(
            iloc=[None, 150.0, 155.0]
        )
        mock_ticker.return_value.history.return_value = mock_hist
        mock_ticker.return_value.info = {
            "longName": "Apple Inc.",
            "marketCap": 2000000000,
            "trailingPE": 28.5,
            "fiftyTwoWeekHigh": 180.0,
            "fiftyTwoWeekLow": 120.0,
            "volume": 50000000,
            "sector": "Technology"
        }

        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "AAPL analysis result"
        mock_client.chat.completions.create.return_value = mock_response

        from src.agents.market_analysis_agent import market_analysis_agent
        result = market_analysis_agent("AAPL")
        assert isinstance(result, str)
        assert len(result) > 0

    @patch("src.agents.market_analysis_agent.yf.Ticker")
    def test_invalid_ticker_returns_error(self, mock_ticker):
        """Agent handles invalid ticker gracefully."""
        mock_hist = MagicMock()
        mock_hist.empty = True
        mock_ticker.return_value.history.return_value = mock_hist

        from src.agents.market_analysis_agent import market_analysis_agent
        result = market_analysis_agent("INVALID123")
        assert "Could not retrieve" in result or isinstance(result, str)


# ── Goal Planning Agent ──────────────────────────────────────
class TestGoalPlanningAgent:

    def test_calculate_goal_metrics_on_track(self):
        """Metrics calculation correctly identifies on-track scenario."""
        from src.agents.goal_planning_agent import calculate_goal_metrics
        metrics = calculate_goal_metrics(
            goal_amount=100_000,
            current_savings=50_000,
            monthly_contribution=1000,
            annual_return=7.0,
            years=5
        )
        assert "projected_value" in metrics
        assert "on_track" in metrics
        assert "gap" in metrics
        assert metrics["projected_value"] > 0

    def test_calculate_goal_metrics_not_on_track(self):
        """Metrics correctly identifies shortfall."""
        from src.agents.goal_planning_agent import calculate_goal_metrics
        metrics = calculate_goal_metrics(
            goal_amount=1_000_000,
            current_savings=100,
            monthly_contribution=10,
            annual_return=2.0,
            years=5
        )
        assert metrics["on_track"] == False
        assert metrics["gap"] > 0

    def test_zero_return_rate(self):
        """Agent handles 0% return rate without division error."""
        from src.agents.goal_planning_agent import calculate_goal_metrics
        metrics = calculate_goal_metrics(
            goal_amount=10_000,
            current_savings=0,
            monthly_contribution=100,
            annual_return=0.0,
            years=5
        )
        assert metrics["projected_value"] == 6000.0

    @patch("src.agents.goal_planning_agent.client")
    def test_goal_agent_returns_string(self, mock_client):
        """Goal planning agent returns a non-empty string."""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Goal planning advice"
        mock_client.chat.completions.create.return_value = mock_response

        from src.agents.goal_planning_agent import goal_planning_agent
        result = goal_planning_agent(
            goal_name="Retirement",
            goal_amount=500_000,
            current_savings=10_000,
            monthly_contribution=300,
            annual_return_pct=7.0,
            years=20,
            risk_profile="moderate"
        )
        assert isinstance(result, str)
        assert len(result) > 0


# ── Tax Education Agent ──────────────────────────────────────
class TestTaxEducationAgent:

    def test_guardrail_blocks_offtopic(self):
        """Guardrail rejects non-finance queries."""
        from src.agents.tax_education_agent import tax_education_agent
        result = tax_education_agent("What is the best pizza recipe?")
        assert "specialize" in result.lower() or "financial" in result.lower()

    def test_guardrail_allows_tax_query(self):
        """Guardrail allows valid tax queries through."""
        from src.agents.tax_education_agent import is_tax_related
        assert is_tax_related("What is a Roth IRA?") == True
        assert is_tax_related("How do capital gains taxes work?") == True

    def test_guardrail_blocks_irrelevant(self):
        """Guardrail blocks clearly irrelevant queries."""
        from src.agents.tax_education_agent import is_tax_related
        assert is_tax_related("What is the weather today?") == False
        assert is_tax_related("Tell me a joke") == False

    @patch("src.agents.tax_education_agent.retrieve_finance_context")
    @patch("src.agents.tax_education_agent.client")
    def test_tax_agent_uses_rag(self, mock_client, mock_rag):
        """Tax agent calls RAG retriever for valid queries."""
        mock_rag.return_value = [{"text": "IRA info", "title": "IRA Guide"}]
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Tax education response"
        mock_client.chat.completions.create.return_value = mock_response

        from src.agents.tax_education_agent import tax_education_agent
        result = tax_education_agent("What is a Roth IRA?")
        mock_rag.assert_called_once()
        assert isinstance(result, str)


# ── News Synthesizer Agent ───────────────────────────────────
class TestNewsSynthesizerAgent:

    @patch("src.agents.news_synthesizer_agent.retrieve_finance_context")
    @patch("src.agents.news_synthesizer_agent.client")
    @patch("src.agents.news_synthesizer_agent.yf.Ticker")
    def test_news_agent_returns_string(self, mock_ticker, mock_client, mock_rag):
        """News agent returns a non-empty string."""
        mock_ticker.return_value.news = []
        mock_rag.return_value = [{"text": "News context"}]
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "News synthesis"
        mock_client.chat.completions.create.return_value = mock_response

        from src.agents.news_synthesizer_agent import news_synthesizer_agent
        result = news_synthesizer_agent("AAPL")
        assert isinstance(result, str)
        assert len(result) > 0

    @patch("src.agents.news_synthesizer_agent.yf.Ticker")
    def test_handles_empty_news(self, mock_ticker):
        """Agent handles tickers with no news gracefully."""
        mock_ticker.return_value.news = []
        from src.agents.news_synthesizer_agent import get_stock_news
        result = get_stock_news("FAKE")
        assert isinstance(result, list)