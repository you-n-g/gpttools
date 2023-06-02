"""Tests for settings."""
import os

from gpttools.settings import global_settings, settings


def test_settings() -> None:
    """Tests for settings."""
    assert settings.logging_level == os.getenv("GPTTOOLS_LOGGING_LEVEL", "INFO")
    assert str(global_settings.ci).lower() == os.getenv("CI", "False").lower()
