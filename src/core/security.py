"""
LLM Security Layer for AI Finance Assistant.
Protects against prompt injection, jailbreaks, and misuse.
"""

import re
import time
from collections import defaultdict


# ── Prompt Injection Patterns ─────────────────────────────────
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|above|all)\s+instructions",
    r"forget\s+(everything|all|previous)",
    r"you\s+are\s+now\s+a",
    r"act\s+as\s+(if\s+you\s+are|a)",
    r"pretend\s+(you\s+are|to\s+be)",
    r"disregard\s+(your|all|previous)",
    r"override\s+(your|all|previous)",
    r"system\s*prompt",
    r"jailbreak",
    r"dan\s+mode",
    r"developer\s+mode",
    r"do\s+anything\s+now",
    r"bypass\s+(your|all|safety)",
    r"reveal\s+(your|the)\s+(system|instructions|prompt)",
    r"what\s+are\s+your\s+instructions",
]

# ── Harmful Content Patterns ──────────────────────────────────
HARMFUL_PATTERNS = [
    r"how\s+to\s+(launder|steal|fraud|scam|manipulate\s+stock)",
    r"insider\s+trading",
    r"pump\s+and\s+dump",
    r"market\s+manipulation",
    r"ponzi\s+scheme\s+how",
    r"evade\s+tax",
    r"hide\s+money\s+from",
]

# ── Off-Topic Patterns ────────────────────────────────────────
OFF_TOPIC_PATTERNS = [
    r"\b(recipe|cooking|weather|sports|movie|music|game|dating)\b",
    r"\b(kill|hurt|harm|attack|weapon|drug|illegal)\b",
    r"\b(password|hack|crack|exploit|vulnerability)\b",
]

# ── Rate Limiter ──────────────────────────────────────────────
class RateLimiter:
    """Simple in-memory rate limiter: max requests per time window."""
    
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests   = max_requests
        self.window_seconds = window_seconds
        self.requests       = defaultdict(list)

    def is_allowed(self, user_id: str = "default") -> bool:
        now = time.time()
        # Remove requests outside the window
        self.requests[user_id] = [
            t for t in self.requests[user_id]
            if now - t < self.window_seconds
        ]
        if len(self.requests[user_id]) >= self.max_requests:
            return False
        self.requests[user_id].append(now)
        return True

    def requests_remaining(self, user_id: str = "default") -> int:
        now = time.time()
        self.requests[user_id] = [
            t for t in self.requests[user_id]
            if now - t < self.window_seconds
        ]
        return max(0, self.max_requests - len(self.requests[user_id]))


# ── Input Sanitizer ───────────────────────────────────────────
def sanitize_input(query: str) -> str:
    """Clean and normalize user input."""
    # Remove excessive whitespace
    query = re.sub(r'\s+', ' ', query).strip()
    
    # Remove null bytes and control characters
    query = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', query)
    
    # Truncate to max length
    if len(query) > 1000:
        query = query[:1000] + "..."
    
    return query


# ── Injection Detector ────────────────────────────────────────
def detect_prompt_injection(query: str) -> tuple[bool, str]:
    """
    Check if query contains prompt injection attempts.
    Returns (is_safe, reason).
    """
    query_lower = query.lower()
    
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, query_lower):
            return False, f"Prompt injection detected: '{pattern}'"
    
    return True, "clean"


# ── Harmful Content Detector ──────────────────────────────────
def detect_harmful_content(query: str) -> tuple[bool, str]:
    """
    Check if query asks for harmful financial information.
    Returns (is_safe, reason).
    """
    query_lower = query.lower()
    
    for pattern in HARMFUL_PATTERNS:
        if re.search(pattern, query_lower):
            return False, f"Harmful content detected"
    
    return True, "clean"


# ── Off-Topic Detector ────────────────────────────────────────
def detect_off_topic(query: str) -> tuple[bool, str]:
    """
    Check if query is completely off-topic for a finance assistant.
    Returns (is_relevant, reason).
    """
    query_lower = query.lower()
    
    # Check for finance keywords — if present, it's relevant
    finance_keywords = [
        "stock", "invest", "portfolio", "market", "fund", "bond",
        "tax", "retire", "saving", "budget", "money", "finance",
        "crypto", "etf", "dividend", "interest", "loan", "debt",
        "401k", "ira", "roth", "asset", "equity", "trading"
    ]
    
    if any(kw in query_lower for kw in finance_keywords):
        return True, "finance-related"
    
    for pattern in OFF_TOPIC_PATTERNS:
        if re.search(pattern, query_lower):
            return False, "off-topic query detected"
    
    # Allow ambiguous queries through (better to answer than block)
    return True, "allowed"


# ── Output Validator ──────────────────────────────────────────
def validate_output(response: str) -> tuple[bool, str]:
    """
    Validate that the LLM output is safe to return.
    Returns (is_safe, reason).
    """
    # Check response isn't empty
    if not response or len(response.strip()) < 10:
        return False, "Response too short or empty"
    
    # Check for leaked system prompt indicators
    leak_patterns = [
        r"my\s+system\s+prompt",
        r"my\s+instructions\s+are",
        r"i\s+am\s+instructed\s+to",
        r"as\s+an?\s+ai\s+language\s+model,\s+i\s+cannot",
    ]
    response_lower = response.lower()
    for pattern in leak_patterns:
        if re.search(pattern, response_lower):
            return False, "Potential system prompt leak detected"
    
    # Check for direct investment advice (too strong recommendations)
    advice_patterns = [
        r"you\s+should\s+(definitely|absolutely)\s+(buy|sell|invest)",
        r"guaranteed\s+(return|profit|gain)",
        r"(buy|sell)\s+immediately",
    ]
    for pattern in advice_patterns:
        if re.search(pattern, response_lower):
            return False, "Response contains direct investment advice"
    
    return True, "safe"


# ── Main Security Gate ────────────────────────────────────────
rate_limiter = RateLimiter(max_requests=10, window_seconds=60)

def security_check(query: str, user_id: str = "default") -> tuple[bool, str]:
    """
    Full security pipeline. Run this before every agent call.
    Returns (is_allowed, error_message).
    """
    # 1. Rate limiting
    if not rate_limiter.is_allowed(user_id):
        remaining = rate_limiter.requests_remaining(user_id)
        return False, f"Rate limit exceeded. Please wait before sending more requests."

    # 2. Sanitize input
    query = sanitize_input(query)

    # 3. Prompt injection check
    is_safe, reason = detect_prompt_injection(query)
    if not is_safe:
        return False, "⚠️ Your query contains patterns that look like prompt injection attempts. Please ask a genuine finance question."

    # 4. Harmful content check
    is_safe, reason = detect_harmful_content(query)
    if not is_safe:
        return False, "⚠️ I can't help with that request. I'm designed to provide financial education only."

    # 5. Off-topic check
    is_relevant, reason = detect_off_topic(query)
    if not is_relevant:
        return False, (
            "🤖 I'm specialized in financial education and can help you with:\n\n"
            "• 📈 Stock market analysis\n"
            "• 💼 Portfolio review and advice\n"
            "• 🎯 Financial goal planning\n"
            "• 💰 Tax education (IRA, 401k, capital gains)\n"
            "• 📰 Financial news synthesis\n"
            "• 📚 General investing concepts\n\n"
            "Please ask me something related to finance or investing!"
        )

    return True, "approved"