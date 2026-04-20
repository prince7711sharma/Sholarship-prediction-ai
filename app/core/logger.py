import logging
import sys
from datetime import datetime


class ColorFormatter(logging.Formatter):
    """Custom formatter with color-coded console output."""

    COLORS = {
        "DEBUG": "\033[36m",      # Cyan
        "INFO": "\033[32m",       # Green
        "WARNING": "\033[33m",    # Yellow
        "ERROR": "\033[31m",      # Red
        "CRITICAL": "\033[1;31m", # Bold Red
    }
    RESET = "\033[0m"
    ICONS = {
        "DEBUG": "🔍",
        "INFO": "✅",
        "WARNING": "⚠️",
        "ERROR": "❌",
        "CRITICAL": "🔥",
    }

    def format(self, record):
        color = self.COLORS.get(record.levelname, self.RESET)
        icon = self.ICONS.get(record.levelname, "")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = super().format(record)
        return f"{color}{icon} [{timestamp}] [{record.levelname}] {record.name} → {record.getMessage()}{self.RESET}"


def get_logger(name: str) -> logging.Logger:
    """Create a named logger with color-coded console output."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        # Console handler with colors
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(ColorFormatter())
        logger.addHandler(console_handler)

        # File handler for persistent logs
        try:
            file_handler = logging.FileHandler("scholarship_api.log", encoding="utf-8")
            file_handler.setLevel(logging.INFO)
            file_formatter = logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        except Exception:
            pass  # File logging is optional

    return logger
