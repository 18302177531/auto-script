"""Data models for short drama script structure."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Character:
    name: str
    gender: str
    age: str
    role: str          # 主角 / 配角 / 反派 etc.
    personality: str
    background: str


@dataclass
class Dialogue:
    character: str
    line: str
    action: Optional[str] = None   # stage direction / action description


@dataclass
class Scene:
    number: int
    location: str
    time_of_day: str   # 白天 / 夜晚 / 黄昏 etc.
    description: str   # scene setting description
    dialogues: List[Dialogue] = field(default_factory=list)
    notes: Optional[str] = None    # director notes / emotional beat


@dataclass
class Episode:
    number: int
    title: str
    synopsis: str
    scenes: List[Scene] = field(default_factory=list)


@dataclass
class Script:
    title: str
    genre: str            # 都市 / 古装 / 甜宠 / 悬疑 etc.
    theme: str            # user-provided theme synopsis
    logline: str          # one-sentence hook
    characters: List[Character] = field(default_factory=list)
    episodes: List[Episode] = field(default_factory=list)
    notes: Optional[str] = None
