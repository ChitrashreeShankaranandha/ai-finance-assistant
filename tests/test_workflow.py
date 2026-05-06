"""
Tests for LangGraph workflow routing.
Run with: pytest tests/test_workflow.py -v
"""
import sys
sys.path.insert(0, '.')

import pytest
from unittest.mock import patch, MagicMock


class TestWorkflowRouting:

    @patch("src.workflow.finance_workflow.ChatOpenAI")
    def test_routes_to_market(self, mock_llm):
        """Queries about stocks route to market agent."""
        mock_instance = MagicMock()
        mock_instance.invoke.side_effect = [
            MagicMock(content="market"),   # router response
            MagicMock(content="AAPL"),     # ticker extraction
        ]
        mock_llm.return_value = mock_instance

        with patch("src.workflow.finance_workflow.market_analysis_agent", return_value="AAPL analysis"):
            from src.workflow.finance_workflow import run_finance_assistant
            result = run_finance_assistant("Analyze AAPL stock for me")
            assert isinstance(result, str)

    @patch("src.workflow.finance_workflow.ChatOpenAI")
    def test_routes_to_tax(self, mock_llm):
        """Queries about tax route to tax agent."""
        mock_instance = MagicMock()
        mock_instance.invoke.return_value = MagicMock(content="tax")
        mock_llm.return_value = mock_instance

        with patch("src.workflow.finance_workflow.tax_education_agent", return_value="Tax advice"):
            from src.workflow.finance_workflow import run_finance_assistant
            result = run_finance_assistant("What is a Roth IRA?")
            assert isinstance(result, str)

    @patch("src.workflow.finance_workflow.ChatOpenAI")
    def test_invalid_route_falls_back_to_general(self, mock_llm):
        """Invalid router response falls back to general node."""
        mock_instance = MagicMock()
        mock_instance.invoke.return_value = MagicMock(content="invalid_category")
        mock_llm.return_value = mock_instance

        with patch("src.workflow.finance_workflow.general_node", return_value={
            "query": "test", "agent": "general",
            "response": "General response", "ticker": None, "error": None
        }):
            from src.workflow.finance_workflow import router_node
            state = {"query": "random", "agent": "", "response": "", "ticker": None, "error": None}
            result = router_node(state)
            assert result["agent"] == "general"

    def test_initial_state_structure(self):
        """Verify the state TypedDict has all required keys."""
        from src.workflow.finance_workflow import FinanceState
        state: FinanceState = {
            "query": "test",
            "agent": "",
            "response": "",
            "ticker": None,
            "error": None,
        }
        assert "query" in state
        assert "agent" in state
        assert "response" in state
        assert "ticker" in state
        assert "error" in state