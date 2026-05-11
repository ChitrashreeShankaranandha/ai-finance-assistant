"""
Centralized logging utility for AI Finance Assistant.
Logs to console and persists to Hugging Face Dataset.
"""

import os
import json
from datetime import datetime

HF_DATASET_REPO = "ChitrashreeShankaranandha/ai-finance-assistant-logs"


def _save_to_hf(log_entry: dict):
    """Append log entry to HF Dataset as daily JSONL file."""
    HF_TOKEN = os.getenv("HF_TOKEN")
    if not HF_TOKEN:
        return

    try:
        from huggingface_hub import HfApi
        api = HfApi(token=HF_TOKEN)

        date_str  = datetime.now().strftime("%Y-%m-%d")
        filename  = f"logs/{date_str}.jsonl"
        log_line  = json.dumps(log_entry) + "\n"

        try:
            existing_path = api.hf_hub_download(
                repo_id=HF_DATASET_REPO,
                filename=filename,
                repo_type="dataset",
                token=HF_TOKEN
            )
            with open(existing_path, "r") as f:
                existing_content = f.read()
        except Exception:
            existing_content = ""

        new_content = existing_content + log_line
        api.upload_file(
            path_or_fileobj=new_content.encode(),
            path_in_repo=filename,
            repo_id=HF_DATASET_REPO,
            repo_type="dataset",
            token=HF_TOKEN
        )
    except Exception as e:
        print(f"[WARNING] Could not save log to HF Dataset: {type(e).__name__}: {str(e)}")


def log(level: str, category: str, message: str, **kwargs):
    """
    Centralized logger for the AI Finance Assistant.

    Args:
        level:    INFO, USAGE, SECURITY, TRADE, ERROR
        category: Component name (workflow, security, trading, app)
        message:  Log message
        **kwargs: Additional key-value pairs to log
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Build extra fields string for console
    extras     = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
    extras_str = f" | {extras}" if extras else ""

    # Always print to console
    print(f"[{timestamp}] [{level}] [{category}] {message}{extras_str}")

    # Save to HF Dataset
    log_entry = {
        "timestamp": timestamp,
        "level":     level,
        "category":  category,
        "message":   message,
        **kwargs
    }
    _save_to_hf(log_entry)


# ── Convenience functions ─────────────────────────────────────
def log_info(category: str, message: str, **kwargs):
    log("INFO", category, message, **kwargs)

def log_usage(category: str, message: str, **kwargs):
    log("USAGE", category, message, **kwargs)

def log_security(category: str, message: str, **kwargs):
    log("SECURITY", category, message, **kwargs)

def log_trade(category: str, message: str, **kwargs):
    log("TRADE", category, message, **kwargs)

def log_error(category: str, message: str, **kwargs):
    log("ERROR", category, message, **kwargs)