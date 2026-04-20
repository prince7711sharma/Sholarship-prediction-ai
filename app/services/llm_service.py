import time
from groq import Groq
from app.core.config import GROQ_API_KEY, LLM_MODEL, LLM_TIMEOUT, LLM_MAX_RETRIES, LLM_TEMPERATURE
from app.core.logger import get_logger

logger = get_logger("llm_service")

client = Groq(api_key=GROQ_API_KEY)


def get_llm_response(prompt: str, system_message: str = None) -> str:
    """
    Get a response from the Groq LLM with retry logic.
    Supports optional system message for better response control.
    """
    messages = []

    if system_message:
        messages.append({"role": "system", "content": system_message})

    messages.append({"role": "user", "content": prompt})

    last_error = None

    for attempt in range(LLM_MAX_RETRIES + 1):
        try:
            logger.info(f"Calling LLM (attempt {attempt + 1}/{LLM_MAX_RETRIES + 1}) — model: {LLM_MODEL}")
            start_time = time.time()

            res = client.chat.completions.create(
                model=LLM_MODEL,
                messages=messages,
                temperature=LLM_TEMPERATURE,
                max_tokens=2048,
                timeout=LLM_TIMEOUT
            )

            elapsed = round(time.time() - start_time, 2)
            content = res.choices[0].message.content

            if not content or len(content.strip()) < 10:
                logger.warning(f"LLM returned empty/short response on attempt {attempt + 1}")
                last_error = "Empty response from LLM"
                continue

            logger.info(f"LLM responded in {elapsed}s ({len(content)} chars)")
            return content

        except Exception as e:
            last_error = str(e)
            logger.error(f"LLM attempt {attempt + 1} failed: {last_error}")
            if attempt < LLM_MAX_RETRIES:
                wait_time = 2 ** attempt
                logger.info(f"Retrying in {wait_time}s...")
                time.sleep(wait_time)

    logger.error(f"All LLM attempts failed. Last error: {last_error}")
    return None