"""Configuration management for the competitive analysis tool."""

import json
from pathlib import Path

from pydantic import BaseModel

from .models import Competitor

CONFIG_DIR = Path.home() / ".competitive_analysis"
CONFIG_FILE = CONFIG_DIR / "config.json"


class Config(BaseModel):
    """Application configuration."""

    competitors: dict[str, Competitor] = {}
    default_output_dir: str = "./output"
    rate_limit_delay: float = 1.0  # seconds between requests


def ensure_config_dir() -> None:
    """Ensure the config directory exists."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> Config:
    """Load configuration from file."""
    ensure_config_dir()
    if CONFIG_FILE.exists():
        data = json.loads(CONFIG_FILE.read_text())
        return Config.model_validate(data)
    return Config()


def save_config(config: Config) -> None:
    """Save configuration to file."""
    ensure_config_dir()
    CONFIG_FILE.write_text(config.model_dump_json(indent=2))


def add_competitor(competitor: Competitor) -> None:
    """Add a competitor to the config."""
    config = load_config()
    config.competitors[competitor.name] = competitor
    save_config(config)


def get_competitor(name: str) -> Competitor | None:
    """Get a competitor by name."""
    config = load_config()
    return config.competitors.get(name)


def list_competitors() -> list[Competitor]:
    """List all tracked competitors."""
    config = load_config()
    return list(config.competitors.values())


def remove_competitor(name: str) -> bool:
    """Remove a competitor from tracking."""
    config = load_config()
    if name in config.competitors:
        del config.competitors[name]
        save_config(config)
        return True
    return False
