"""Utilities for formatting and exporting generated scripts."""

import json
from pathlib import Path
from typing import Union

from models import Script


# ------------------------------------------------------------------
# Text / human-readable format
# ------------------------------------------------------------------

def format_script_text(script: Script) -> str:
    """Return a nicely formatted plain-text version of the script."""
    lines = []

    lines.append("=" * 60)
    lines.append(f"  《{script.title}》")
    lines.append(f"  题材：{script.genre}")
    lines.append(f"  一句话简介：{script.logline}")
    if script.notes:
        lines.append(f"  主题：{script.notes}")
    lines.append("=" * 60)

    # Characters
    if script.characters:
        lines.append("\n【人物表】")
        for c in script.characters:
            lines.append(
                f"  {c.name}（{c.role}，{c.gender}，{c.age}）"
                f"\n    性格：{c.personality}"
                f"\n    背景：{c.background}"
            )

    # Episodes
    for ep in script.episodes:
        lines.append(f"\n{'─' * 60}")
        lines.append(f"第{ep.number}集  《{ep.title}》")
        lines.append(f"概要：{ep.synopsis}")
        lines.append("─" * 60)

        for scene in ep.scenes:
            lines.append(
                f"\n第{scene.number}场  {scene.location}  {scene.time_of_day}"
            )
            if scene.description:
                lines.append(f"  （{scene.description}）")
            if scene.notes:
                lines.append(f"  [情绪基调：{scene.notes}]")

            for d in scene.dialogues:
                if d.action:
                    lines.append(f"  {d.character}  [{d.action}]")
                    lines.append(f"  {d.character}：{d.line}")
                else:
                    lines.append(f"  {d.character}：{d.line}")

    lines.append("\n" + "=" * 60)
    lines.append("  END")
    lines.append("=" * 60)

    return "\n".join(lines)


# ------------------------------------------------------------------
# JSON export
# ------------------------------------------------------------------

def script_to_dict(script: Script) -> dict:
    """Serialize a Script to a plain Python dict (JSON-serializable)."""
    return {
        "title": script.title,
        "genre": script.genre,
        "theme": script.theme,
        "logline": script.logline,
        "notes": script.notes,
        "characters": [
            {
                "name": c.name,
                "gender": c.gender,
                "age": c.age,
                "role": c.role,
                "personality": c.personality,
                "background": c.background,
            }
            for c in script.characters
        ],
        "episodes": [
            {
                "number": ep.number,
                "title": ep.title,
                "synopsis": ep.synopsis,
                "scenes": [
                    {
                        "number": s.number,
                        "location": s.location,
                        "time_of_day": s.time_of_day,
                        "description": s.description,
                        "notes": s.notes,
                        "dialogues": [
                            {
                                "character": d.character,
                                "action": d.action,
                                "line": d.line,
                            }
                            for d in s.dialogues
                        ],
                    }
                    for s in ep.scenes
                ],
            }
            for ep in script.episodes
        ],
    }


def save_script_json(script: Script, path: Union[str, Path]) -> Path:
    """Save script as a JSON file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(script_to_dict(script), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return path


def save_script_text(script: Script, path: Union[str, Path]) -> Path:
    """Save script as a plain-text file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(format_script_text(script), encoding="utf-8")
    return path
