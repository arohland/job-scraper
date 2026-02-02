import json
from pathlib import Path
from dotenv import load_dotenv
from .logger import get_logger

logger = get_logger(__name__)

# project root = parent of job_watcher/
PROJECT_ROOT = Path(__file__).resolve().parents[1]

def load_config(filename: str = "config.json") -> dict:
    load_dotenv(PROJECT_ROOT / ".env")

    config_path = PROJECT_ROOT / filename
    logger.info(f"Loading config from {config_path}")

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r") as f:
        config = json.load(f)

    # inject secrets from env
    config["email"]["username"] = config["email"].get(
        "username"
    ) or __import__("os").getenv("EMAIL_USERNAME")
    config["email"]["password"] = config["email"].get(
        "password"
    ) or __import__("os").getenv("EMAIL_PASSWORD")

    return config
