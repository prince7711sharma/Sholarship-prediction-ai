import os
from dotenv import load_dotenv

load_dotenv()

# ─── API Keys ─────────────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

# ─── LLM Config ──────────────────────────────────────────────────────
LLM_MODEL = "llama-3.3-70b-versatile"
LLM_TIMEOUT = 30
LLM_MAX_RETRIES = 1
LLM_TEMPERATURE = 0.7

# ─── Search Config ───────────────────────────────────────────────────
SEARCH_MAX_RESULTS = 3

# ─── App Config ──────────────────────────────────────────────────────
APP_NAME = "Scholarship Predictor AI"
APP_VERSION = "2.0.0"

# ─── Rate Limit Config ───────────────────────────────────────────────
RATE_LIMIT_MAX = 5           # max requests per window
RATE_LIMIT_WINDOW = 60       # window in seconds
