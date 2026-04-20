import os
from dotenv import load_dotenv

load_dotenv()

# ─── API Keys ─────────────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

# ─── LLM Config ──────────────────────────────────────────────────────
LLM_MODEL = "llama-3.1-8b-instant"
LLM_TIMEOUT = 30
LLM_MAX_RETRIES = 2
LLM_TEMPERATURE = 0.7

# ─── Search Config ───────────────────────────────────────────────────
SEARCH_MAX_RESULTS = 2


# ─── App Config ──────────────────────────────────────────────────────
APP_NAME = "Scholarship Predictor AI"
APP_VERSION = "2.0.0"

# ─── Rate Limit Config ───────────────────────────────────────────────
RATE_LIMIT_MAX = 25           # max requests per window
RATE_LIMIT_WINDOW = 60       # window in seconds

