import json
from pathlib import Path
from dotenv import dotenv_values
from .logger import get_logger

logger = get_logger(__name__)

def load_config(config_file: str = "config.json", env_file: str = ".env") -> dict:
    logger.info(f"Loading config from {config_file} and {env_file}")
    config = json.loads(Path(config_file).read_text())

    env_vars = dotenv_values(env_file)
    if "EMAIL_USERNAME" in env_vars and "EMAIL_PASSWORD" in env_vars:
        config["email"]["username"] = env_vars["EMAIL_USERNAME"]
        config["email"]["password"] = env_vars["EMAIL_PASSWORD"]
        logger.info("Loaded email credentials from .env")

    return config
