from __future__ import annotations

import argparse
from dataclasses import dataclass


@dataclass
class GenerationConfig:
    episodes: int = 1
    scenes_per_episode: int = 3


class ShortDramaAgent:
    def __init__(self, config: GenerationConfig | None = None) -> None:
        self.config = config or GenerationConfig()

    def generate_script(self, topic_outline: str, characters: list[str] | None = None) -> str:
        topic_outline = topic_outline.strip()
        if not topic_outline:
            raise ValueError("topic_outline 不能为空")

        cast = [c.strip() for c in (characters or []) if c.strip()]
        if not cast:
            cast = ["主角", "搭档", "反派"]

        lines = [
            "【短剧标题】",
            f"《{self._title_from_topic(topic_outline)}》",
            "",
            "【主题概要】",
            topic_outline,
            "",
            "【主要角色】",
            "、".join(cast),
            "",
        ]

        for ep in range(1, self.config.episodes + 1):
            lines.append(f"=== 第{ep}集 ===")
            ep_goal = self._episode_goal(topic_outline, ep)
            lines.append(f"[本集推进] {ep_goal}")
            for scene in range(1, self.config.scenes_per_episode + 1):
                lines.extend(self._build_scene(ep, scene, cast, topic_outline))
            lines.append("")

        lines.append("【结尾钩子】")
        lines.append(self._hook(topic_outline))
        return "\n".join(lines)

    def _title_from_topic(self, topic: str) -> str:
        first = topic.split("，")[0].split("。")[0].strip()
        return first[:12] or "无名之局"

    def _episode_goal(self, topic: str, episode: int) -> str:
        beats = [
            f"建立冲突：围绕“{topic[:20]}”抛出关键矛盾。",
            "矛盾升级：主角行动受阻，关系与利益同时拉扯。",
            "反转出现：隐藏信息曝光，局势迅速改写。",
            "高潮收束：关键对决后留下新的悬念。",
        ]
        return beats[min(episode - 1, len(beats) - 1)]

    def _build_scene(self, episode: int, scene: int, cast: list[str], topic: str) -> list[str]:
        a = cast[(scene - 1) % len(cast)]
        b = cast[scene % len(cast)]
        return [
            f"[场景 {episode}-{scene}]",
            f"舞台提示：夜。地点切换至与“{topic[:16]}”相关的关键空间。",
            f"{a}：我们没有退路了，今晚必须把真相挖出来。",
            f"{b}：真相很贵，你准备好付代价了吗？",
            f"{a}：代价我来扛，但这一次我要改写结局。",
            "（镜头推进，气氛骤然紧张。）",
        ]

    def _hook(self, topic: str) -> str:
        return f"一通匿名电话打来：“关于‘{topic[:18]}’，你只知道了第一层。”"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="根据主题概要自动生成短剧剧本")
    parser.add_argument("--topic", type=str, help="主题概要")
    parser.add_argument("--characters", type=str, default="", help="角色名，使用逗号分隔")
    parser.add_argument("--episodes", type=int, default=1, help="集数，默认 1")
    parser.add_argument("--scenes", type=int, default=3, help="每集场景数，默认 3")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    topic = args.topic or input("请输入主题概要：").strip()
    chars = [c.strip() for c in args.characters.split(",")] if args.characters else []
    episodes = max(args.episodes, 1)
    scenes = max(args.scenes, 1)

    agent = ShortDramaAgent(GenerationConfig(episodes=episodes, scenes_per_episode=scenes))
    print(agent.generate_script(topic_outline=topic, characters=chars))


if __name__ == "__main__":
    main()
