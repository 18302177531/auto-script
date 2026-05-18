"""Unit tests for script generation (no API key required – uses mocks)."""

import json
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# ---------------------------------------------------------------------------
# Stub the openai package so tests run without it installed
# ---------------------------------------------------------------------------
openai_stub = types.ModuleType("openai")

class _FakeClient:
    def __init__(self, **kwargs): pass
    class chat:
        class completions:
            @staticmethod
            def create(**kwargs):
                raise NotImplementedError("Use mocked _chat in tests")

openai_stub.OpenAI = _FakeClient
sys.modules.setdefault("openai", openai_stub)

# ---------------------------------------------------------------------------
# Now import project modules
# ---------------------------------------------------------------------------
from agent import ScriptAgent  # noqa: E402
from config import Config  # noqa: E402
from formatter import format_script_text, script_to_dict  # noqa: E402
from models import Character, Dialogue, Episode, Scene, Script  # noqa: E402
from prompts import OUTLINE_PROMPT, CHARACTERS_PROMPT, SCENE_PROMPT  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

OUTLINE_RESPONSE = {
    "title": "逆袭外卖哥",
    "genre": "都市爽剧",
    "logline": "外卖小哥一夜发现自己是豪门私生子，命运由此逆转。",
    "theme_summary": "草根逆袭，身份揭秘",
    "episodes": [
        {
            "number": 1,
            "title": "意外的身世",
            "synopsis": "陈浩送餐时捡到公文包，发现里面竟有自己的DNA报告…",
            "hook": "公文包的主人究竟是谁？"
        }
    ]
}

CHARACTERS_RESPONSE = {
    "characters": [
        {
            "name": "陈浩",
            "gender": "男",
            "age": "22岁",
            "role": "主角",
            "personality": "坚韧、正义",
            "background": "单亲家庭长大，靠送外卖为生。",
            "motivation": "寻找亲生父亲"
        }
    ]
}

SCENES_RESPONSE = {
    "scenes": [
        {
            "number": 1,
            "location": "写字楼大堂",
            "time_of_day": "白天",
            "description": "玻璃幕墙，阳光刺眼",
            "emotional_beat": "紧张",
            "dialogues": [
                {"character": "陈浩", "action": "挠头", "line": "这地方真豪。"},
                {"character": "保安", "action": None, "line": "外卖的？走侧门。"},
            ],
            "notes": "近景特写"
        }
    ]
}


def _make_agent_with_mock_chat(responses: list) -> ScriptAgent:
    """Return a ScriptAgent whose _chat method yields responses in order."""
    cfg = Config()
    cfg.openai_api_key = "test-key"
    agent = ScriptAgent(cfg)
    call_iter = iter(responses)

    def fake_chat(user_prompt, system_prompt=None):  # noqa: ARG001
        return json.dumps(next(call_iter), ensure_ascii=False)

    agent._chat = fake_chat  # type: ignore[method-assign]
    return agent


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestJSONParsing(unittest.TestCase):
    def test_parse_plain_json(self):
        data = ScriptAgent._parse_json('{"key": "value"}')
        self.assertEqual(data["key"], "value")

    def test_parse_fenced_json(self):
        fenced = "```json\n{\"key\": \"value\"}\n```"
        data = ScriptAgent._parse_json(fenced)
        self.assertEqual(data["key"], "value")

    def test_parse_fenced_no_lang(self):
        fenced = "```\n{\"key\": 1}\n```"
        data = ScriptAgent._parse_json(fenced)
        self.assertEqual(data["key"], 1)


class TestAgentGenerate(unittest.TestCase):
    def _run_generate(self, polish=False):
        responses = [OUTLINE_RESPONSE, CHARACTERS_RESPONSE, SCENES_RESPONSE]
        if polish:
            # polish pass returns same dialogues
            polished = [
                {"character": d["character"], "action": d.get("action"), "line": d["line"]}
                for d in SCENES_RESPONSE["scenes"][0]["dialogues"]
            ]
            responses.append(polished)
        agent = _make_agent_with_mock_chat(responses)
        return agent.generate(
            theme="外卖小哥逆袭",
            episode_count=1,
            scene_count=1,
            polish=polish,
        )

    def test_script_basic_structure(self):
        script = self._run_generate()
        self.assertIsInstance(script, Script)
        self.assertEqual(script.title, "逆袭外卖哥")
        self.assertEqual(script.genre, "都市爽剧")
        self.assertEqual(len(script.characters), 1)
        self.assertEqual(len(script.episodes), 1)

    def test_episode_and_scenes(self):
        script = self._run_generate()
        ep = script.episodes[0]
        self.assertEqual(ep.number, 1)
        self.assertEqual(ep.title, "意外的身世")
        self.assertEqual(len(ep.scenes), 1)

    def test_dialogues_parsed(self):
        script = self._run_generate()
        dialogues = script.episodes[0].scenes[0].dialogues
        self.assertEqual(len(dialogues), 2)
        self.assertEqual(dialogues[0].character, "陈浩")
        self.assertEqual(dialogues[0].action, "挠头")
        self.assertEqual(dialogues[1].character, "保安")
        self.assertIsNone(dialogues[1].action)

    def test_polish_pass(self):
        script = self._run_generate(polish=True)
        # Polished lines should still be present
        self.assertEqual(len(script.episodes[0].scenes[0].dialogues), 2)

    def test_missing_api_key_raises(self):
        cfg = Config()
        cfg.openai_api_key = ""
        agent = ScriptAgent(cfg)
        with self.assertRaises(ValueError, msg="Should raise when API key is empty"):
            _ = agent.client  # noqa: B018


class TestFormatter(unittest.TestCase):
    def _make_script(self) -> Script:
        return Script(
            title="测试剧",
            genre="都市",
            theme="测试主题",
            logline="测试钩子",
            characters=[
                Character("张三", "男", "25岁", "主角", "勇敢", "普通人")
            ],
            episodes=[
                Episode(
                    number=1,
                    title="第一集",
                    synopsis="开篇",
                    scenes=[
                        Scene(
                            number=1,
                            location="咖啡馆",
                            time_of_day="白天",
                            description="安静的咖啡馆",
                            dialogues=[
                                Dialogue("张三", "这里不错。", "微笑")
                            ],
                            notes="温馨",
                        )
                    ],
                )
            ],
        )

    def test_format_text_contains_title(self):
        script = self._make_script()
        text = format_script_text(script)
        self.assertIn("测试剧", text)
        self.assertIn("张三", text)
        self.assertIn("这里不错。", text)

    def test_script_to_dict_roundtrip(self):
        script = self._make_script()
        d = script_to_dict(script)
        self.assertEqual(d["title"], "测试剧")
        self.assertEqual(len(d["characters"]), 1)
        self.assertEqual(d["episodes"][0]["scenes"][0]["dialogues"][0]["line"], "这里不错。")

    def test_save_and_load_json(self):
        import tempfile
        from formatter import save_script_json
        script = self._make_script()
        with tempfile.TemporaryDirectory() as tmp:
            path = save_script_json(script, Path(tmp) / "test.json")
            loaded = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(loaded["title"], "测试剧")

    def test_save_and_load_text(self):
        import tempfile
        from formatter import save_script_text
        script = self._make_script()
        with tempfile.TemporaryDirectory() as tmp:
            path = save_script_text(script, Path(tmp) / "test.txt")
            content = path.read_text(encoding="utf-8")
        self.assertIn("测试剧", content)


class TestPrompts(unittest.TestCase):
    def test_outline_prompt_format(self):
        filled = OUTLINE_PROMPT.format(theme="测试", episode_count=2, language="zh")
        self.assertIn("测试", filled)
        self.assertIn("2集", filled)

    def test_characters_prompt_format(self):
        filled = CHARACTERS_PROMPT.format(title="T", genre="G", logline="L")
        self.assertIn("T", filled)

    def test_scene_prompt_format(self):
        filled = SCENE_PROMPT.format(
            episode_number=1,
            episode_title="EP1",
            title="T",
            genre="G",
            episode_synopsis="S",
            episode_hook="H",
            characters_desc="C",
            scene_count=5,
        )
        self.assertIn("EP1", filled)
        self.assertIn("5场", filled)


if __name__ == "__main__":
    unittest.main()
