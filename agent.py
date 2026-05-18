"""Core agent logic for short drama script generation."""

import json
import logging
from typing import Any, Dict, List, Optional

from openai import OpenAI

from config import Config, config as default_config
from models import Character, Dialogue, Episode, Scene, Script
from prompts import (
    CHARACTERS_PROMPT,
    OUTLINE_PROMPT,
    POLISH_PROMPT,
    SCENE_PROMPT,
    SYSTEM_PROMPT,
)

logger = logging.getLogger(__name__)


class ScriptAgent:
    """Multi-step agent that generates a short drama script from a theme synopsis."""

    def __init__(self, cfg: Optional[Config] = None):
        self.cfg = cfg or default_config
        self._client: Optional[OpenAI] = None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @property
    def client(self) -> OpenAI:
        if self._client is None:
            if not self.cfg.openai_api_key:
                raise ValueError(
                    "OpenAI API key is not set. "
                    "Please set the OPENAI_API_KEY environment variable."
                )
            self._client = OpenAI(
                api_key=self.cfg.openai_api_key,
                base_url=self.cfg.openai_base_url,
            )
        return self._client

    def _chat(self, user_prompt: str, system_prompt: str = SYSTEM_PROMPT) -> str:
        """Send a chat completion request and return the raw text response."""
        response = self.client.chat.completions.create(
            model=self.cfg.model,
            temperature=self.cfg.temperature,
            max_tokens=self.cfg.max_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content.strip()

    @staticmethod
    def _parse_json(text: str) -> Any:
        """Parse JSON from model output, stripping any surrounding Markdown fences."""
        # Remove ```json ... ``` or ``` ... ``` wrappers if present
        if text.startswith("```"):
            lines = text.splitlines()
            # drop first and last fence lines
            inner = "\n".join(lines[1:] if lines[-1].strip() == "```" else lines[1:])
            inner = inner.rstrip("`").strip()
            text = inner
        return json.loads(text)

    # ------------------------------------------------------------------
    # Generation steps
    # ------------------------------------------------------------------

    def _generate_outline(
        self, theme: str, episode_count: int, language: str
    ) -> Dict[str, Any]:
        """Step 1: Generate story outline."""
        logger.info("Step 1/3 – Generating story outline …")
        prompt = OUTLINE_PROMPT.format(
            theme=theme,
            episode_count=episode_count,
            language=language,
        )
        raw = self._chat(prompt)
        return self._parse_json(raw)

    def _generate_characters(self, outline: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Step 2: Generate characters based on the outline."""
        logger.info("Step 2/3 – Generating characters …")
        prompt = CHARACTERS_PROMPT.format(
            title=outline["title"],
            genre=outline["genre"],
            logline=outline["logline"],
        )
        raw = self._chat(prompt)
        data = self._parse_json(raw)
        return data.get("characters", [])

    def _build_characters_desc(self, characters: List[Dict[str, Any]]) -> str:
        lines = []
        for c in characters:
            lines.append(
                f"- {c['name']}（{c.get('role', '')}）：{c.get('personality', '')}，{c.get('background', '')}"
            )
        return "\n".join(lines)

    def _generate_episode_scenes(
        self,
        outline: Dict[str, Any],
        episode: Dict[str, Any],
        characters: List[Dict[str, Any]],
        scene_count: int,
    ) -> List[Dict[str, Any]]:
        """Step 3: Generate scenes for a single episode."""
        logger.info(
            "Step 3/%d – Generating scenes for episode %d «%s» …",
            len(outline["episodes"]),
            episode["number"],
            episode["title"],
        )
        prompt = SCENE_PROMPT.format(
            episode_number=episode["number"],
            episode_title=episode["title"],
            title=outline["title"],
            genre=outline["genre"],
            episode_synopsis=episode["synopsis"],
            episode_hook=episode.get("hook", ""),
            characters_desc=self._build_characters_desc(characters),
            scene_count=scene_count,
        )
        raw = self._chat(prompt)
        data = self._parse_json(raw)
        return data.get("scenes", [])

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def generate(
        self,
        theme: str,
        episode_count: Optional[int] = None,
        scene_count: Optional[int] = None,
        language: Optional[str] = None,
        polish: bool = False,
        progress_callback=None,
    ) -> Script:
        """Generate a complete short drama script from a theme synopsis.

        Args:
            theme: The theme / synopsis provided by the user.
            episode_count: Number of episodes (defaults to config value).
            scene_count: Number of scenes per episode (defaults to config value).
            language: Output language code ("zh" or "en").
            polish: Whether to run an additional dialogue-polishing pass.
            progress_callback: Optional callable(step: str) called at each step.

        Returns:
            A fully populated Script object.
        """
        episode_count = episode_count or self.cfg.default_episode_count
        scene_count = scene_count or self.cfg.default_scene_count
        language = language or self.cfg.default_language

        def _progress(msg: str):
            logger.info(msg)
            if progress_callback:
                progress_callback(msg)

        # --- Step 1: outline ---
        _progress("正在生成故事大纲…")
        outline = self._generate_outline(theme, episode_count, language)

        # --- Step 2: characters ---
        _progress("正在创建人物角色…")
        raw_characters = self._generate_characters(outline)

        characters: List[Character] = [
            Character(
                name=c["name"],
                gender=c.get("gender", ""),
                age=c.get("age", ""),
                role=c.get("role", ""),
                personality=c.get("personality", ""),
                background=c.get("background", ""),
            )
            for c in raw_characters
        ]

        # --- Step 3: scenes per episode ---
        episodes: List[Episode] = []
        for ep_data in outline.get("episodes", []):
            _progress(f"正在编写第{ep_data['number']}集剧本…")
            raw_scenes = self._generate_episode_scenes(
                outline, ep_data, raw_characters, scene_count
            )

            scenes: List[Scene] = []
            for s in raw_scenes:
                dialogues: List[Dialogue] = [
                    Dialogue(
                        character=d["character"],
                        line=d["line"],
                        action=d.get("action"),
                    )
                    for d in s.get("dialogues", [])
                ]
                scenes.append(
                    Scene(
                        number=s["number"],
                        location=s["location"],
                        time_of_day=s.get("time_of_day", ""),
                        description=s.get("description", ""),
                        dialogues=dialogues,
                        notes=s.get("notes") or s.get("emotional_beat"),
                    )
                )

            episodes.append(
                Episode(
                    number=ep_data["number"],
                    title=ep_data["title"],
                    synopsis=ep_data["synopsis"],
                    scenes=scenes,
                )
            )

        script = Script(
            title=outline["title"],
            genre=outline["genre"],
            theme=theme,
            logline=outline["logline"],
            characters=characters,
            episodes=episodes,
            notes=outline.get("theme_summary"),
        )

        if polish:
            _progress("正在润色台词…")
            script = self._polish_script(script)

        _progress("剧本生成完成！")
        return script

    # ------------------------------------------------------------------
    # Polish pass
    # ------------------------------------------------------------------

    def _polish_script(self, script: Script) -> Script:
        """Run a polish pass on every scene's dialogues."""
        for episode in script.episodes:
            for scene in episode.scenes:
                if not scene.dialogues:
                    continue
                raw_dialogues = [
                    {
                        "character": d.character,
                        "action": d.action or "",
                        "line": d.line,
                    }
                    for d in scene.dialogues
                ]
                prompt = POLISH_PROMPT.format(
                    script_excerpt=json.dumps(raw_dialogues, ensure_ascii=False, indent=2)
                )
                try:
                    raw = self._chat(prompt)
                    polished = self._parse_json(raw)
                    if isinstance(polished, list):
                        scene.dialogues = [
                            Dialogue(
                                character=d["character"],
                                line=d["line"],
                                action=d.get("action") or None,
                            )
                            for d in polished
                        ]
                except Exception as exc:
                    logger.warning("Polish pass failed for scene %d: %s", scene.number, exc)
        return script
