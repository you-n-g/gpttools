"""Settings Module."""
import logging
from logging import getLevelName
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Project specific settings."""

    logging_level: Optional[str] = getLevelName(logging.INFO)

    class Config:
        """Config for settings."""

        env_prefix = "GPTTOOLS_"


class GlobalSettings(BaseSettings):
    """System level settings."""

    ci: bool = False


class OpenAI(BaseSettings):
    """System level settings."""

    max_retry: int = 120
    retry_sleep: int = 5
    temperature: float = 0.9  # TODO: it is not being used.
    max_tokens: int = 800

    api_model: str = "gpt-35-turbo"
    api_type: str = "azure"
    api_version: str = "2023-03-15-preview"
    api_key: str = None
    api_base: str = None

    class Config:
        env_prefix = "OPENAI_"


_env_file = None
if Path(".env").exists():
    _env_file = ".env"
    logging.warning("loading environtment file from .env")

#: Instance for project specific settings.
settings = Settings(_env_file=_env_file)

#: Instance for system level settings.
global_settings = GlobalSettings(_env_file=_env_file)

OPENAI_SETTINGS = OpenAI(_env_file=_env_file)
