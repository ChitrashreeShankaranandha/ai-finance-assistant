# run_demo.py  ← manual demo
import sys
sys.path.insert(0, '.')

from src.workflow.finance_workflow import run_finance_assistant

queries = [
    "Analyze AAPL stock for me",
    "What is the latest news on Tesla?",
    "What is the difference between Roth IRA and 401k?",
    "What is dollar cost averaging?",
    "Am I on track for retirement?",
]

for query in queries:
    print(f"\n{'='*55}")
    print(f"Q: {query}")
    print(f"{'='*55}")
    result = run_finance_assistant(query)
    print(result[:400] + "...")