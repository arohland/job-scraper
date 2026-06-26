import logging
import sys
from pathlib import Path

LOG_FILE = Path("jobscraper.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ]
)

# Force stdout to utf-8 on Windows so German characters don't crash the logger
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
