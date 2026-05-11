"""
Centralized logging utility for AI Finance Assistant.
Logs to console and persists to Hugging Face Dataset as session-based JSON.
"""

import os
import json
import uuid
from datetime import datetime

HF_DATASET_REPO = "ChitrashreeShankaranandha/ai-finance-assistant-logs"


def _get_session_id() -> str:
    """Get or create session ID from environment."""
    session_id = os.getenv("CURRENT_SESSION_ID")
    if not session_id:
        timestamp  = datetime.now().strftime("%H%M%S")
        unique_id  = str(uuid.uuid4())[:8]
        session_id = f"session_{timestamp}_{unique_id}"
        os.environ["CURRENT_SESSION_ID"] = session_id
    return session_id


def _new_session(session_id: str) -> dict:
    """Create a new session object."""
    return {
        "session_id":    session_id,
        "session_start": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "session_end":   None,
        "total_actions": 0,
        "events":        []
    }


def _get_session_data(session_id: str) -> dict:
    """Get existing session data from HF or create new."""
    HF_TOKEN = os.getenv("HF_TOKEN")
    if not HF_TOKEN:
        return _new_session(session_id)

    try:
        from huggingface_hub import HfApi
        api      = HfApi(token=HF_TOKEN)
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"sessions/{date_str}/{session_id}.json"

        existing_path = api.hf_hub_download(
            repo_id=HF_DATASET_REPO,
            filename=filename,
            repo_type="dataset",
            token=HF_TOKEN
        )
        with open(existing_path, "r") as f:
            return json.load(f)
    except Exception:
        return _new_session(session_id)


def _save_session_to_hf(session_data: dict):
    """Save/update session JSON to HF Dataset."""
    HF_TOKEN = os.getenv("HF_TOKEN")
    if not HF_TOKEN:
        return

    try:
        from huggingface_hub import HfApi
        api        = HfApi(token=HF_TOKEN)
        date_str   = datetime.now().strftime("%Y-%m-%d")
        session_id = session_data["session_id"]
        filename   = f"sessions/{date_str}/{session_id}.json"

        content = json.dumps(session_data, indent=2)
        api.upload_file(
            path_or_fileobj=content.encode(),
            path_in_repo=filename,
            repo_id=HF_DATASET_REPO,
            repo_type="dataset",
            token=HF_TOKEN
        )
    except Exception as e:
        print(f"[WARNING] Could not save session to HF Dataset: {str(e)}")


def log(level: str, category: str, message: str, **kwargs):
    """
    Centralized logger for the AI Finance Assistant.
    Buffers events per session and updates HF Dataset on every log call.
    """
    timestamp  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    session_id = _get_session_id()

    # Build extra fields string for console
    extras     = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
    extras_str = f" | {extras}" if extras else ""

    # Always print to console
    print(f"[{timestamp}] [{level}] [{category}] {message}{extras_str}")

    # Build event entry
    event = {
        "timestamp": timestamp,
        "level":     level,
        "category":  category,
        "message":   message,
        **kwargs
    }

    # Get current session data
    session_data = _get_session_data(session_id)

    # Append event and update session
    session_data["events"].append(event)
    session_data["total_actions"] = len(session_data["events"])
    session_data["session_end"]   = timestamp

    # Save updated session to HF
    _save_session_to_hf(session_data)


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