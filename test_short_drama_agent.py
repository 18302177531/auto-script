import unittest

from short_drama_agent import GenerationConfig, ShortDramaAgent


class ShortDramaAgentTests(unittest.TestCase):
    def test_generate_script_contains_core_sections(self) -> None:
        agent = ShortDramaAgent(GenerationConfig(episodes=1, scenes_per_episode=2))
        result = agent.generate_script(
            topic_outline="重生后女主联手律师复仇，揭开家族遗产骗局",
            characters=["女主", "律师", "反派"],
        )

        self.assertIn("【短剧标题】", result)
        self.assertIn("【主题概要】", result)
        self.assertIn("【主要角色】", result)
        self.assertIn("=== 第1集 ===", result)
        self.assertIn("[场景 1-1]", result)
        self.assertIn("[场景 1-2]", result)
        self.assertIn("【结尾钩子】", result)

    def test_generate_script_uses_default_characters(self) -> None:
        agent = ShortDramaAgent()
        result = agent.generate_script(topic_outline="小镇悬疑案件牵出旧日秘密")
        self.assertIn("主角、搭档、反派", result)

    def test_generate_script_rejects_empty_topic(self) -> None:
        agent = ShortDramaAgent()
        with self.assertRaises(ValueError):
            agent.generate_script(topic_outline="   ")


if __name__ == "__main__":
    unittest.main()
