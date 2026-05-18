"""Configuration for the short drama script generation agent."""

import os
from dataclasses import dataclass, field


@dataclass
class Config:
    # LLM settings
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    openai_base_url: str = field(
        default_factory=lambda: os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    )
    model: str = field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o"))
    temperature: float = 0.85
    max_tokens: int = 4096

    # Script defaults
    default_episode_count: int = 1
    default_scene_count: int = 8
    default_language: str = "zh"  # zh = Chinese, en = English


# Singleton config instance
config = Config()
