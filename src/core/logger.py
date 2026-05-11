"""
Centralized logging utility for AI Finance Assistant.
"""

import os
from datetime import datetime


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
    
    # Build extra fields string
    extras = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
    extras_str = f" | {extras}" if extras else ""
    
    print(f"[{timestamp}] [{level}] [{category}] {message}{extras_str}")


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