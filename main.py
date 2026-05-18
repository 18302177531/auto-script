#!/usr/bin/env python3
"""
CLI entry point for the short drama script generation agent.

Usage examples:
    python main.py --theme "一个普通外卖小哥意外发现自己是亿万富翁的私生子" --episodes 3 --scenes 6
    python main.py --theme "古代穿越：现代女医生穿越成太子妃" --polish --output my_script
    python main.py --web   # launch Gradio web UI
"""

import argparse
import logging
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)


def run_cli(args: argparse.Namespace) -> None:
    from agent import ScriptAgent
    from config import config
    from formatter import format_script_text, save_script_json, save_script_text

    # Apply overrides
    if args.model:
        config.model = args.model
    if args.api_key:
        config.openai_api_key = args.api_key
    if args.base_url:
        config.openai_base_url = args.base_url

    agent = ScriptAgent(config)

    def on_progress(msg: str):
        print(f"  ► {msg}")

    print("\n🎬 正在生成短剧剧本，请稍候…\n")
    script = agent.generate(
        theme=args.theme,
        episode_count=args.episodes,
        scene_count=args.scenes,
        language=args.lang,
        polish=args.polish,
        progress_callback=on_progress,
    )

    # Print to console
    print("\n" + format_script_text(script))

    # Save outputs
    if args.output:
        base = Path(args.output)
        txt_path = save_script_text(script, base.with_suffix(".txt"))
        json_path = save_script_json(script, base.with_suffix(".json"))
        print(f"\n✅ 剧本已保存：\n   {txt_path}\n   {json_path}")


def run_web() -> None:
    """Launch a Gradio web interface."""
    try:
        import gradio as gr
    except ImportError:
        print(
            "❌ Gradio 未安装，请先执行：pip install gradio\n"
            "   或直接使用命令行：python main.py --theme '你的主题'"
        )
        sys.exit(1)

    from agent import ScriptAgent
    from config import config
    from formatter import format_script_text, save_script_json, save_script_text

    def generate_script(
        api_key: str,
        base_url: str,
        model: str,
        theme: str,
        episodes: int,
        scenes: int,
        polish: bool,
    ):
        if not api_key.strip():
            return "⚠️ 请先填写 OpenAI API Key", None, None

        if not theme.strip():
            return "⚠️ 请先输入短剧主题概要", None, None

        cfg = config.__class__()
        cfg.openai_api_key = api_key.strip()
        cfg.openai_base_url = base_url.strip() or config.openai_base_url
        cfg.model = model.strip() or config.model

        progress_log = []

        def on_progress(msg: str):
            progress_log.append(msg)

        try:
            agent = ScriptAgent(cfg)
            script = agent.generate(
                theme=theme,
                episode_count=episodes,
                scene_count=scenes,
                polish=polish,
                progress_callback=on_progress,
            )
        except Exception as exc:
            return f"❌ 生成失败：{exc}", None, None

        text_output = format_script_text(script)

        # Save temp files for download
        import json
        import tempfile

        tmp_txt = tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        )
        tmp_txt.write(text_output)
        tmp_txt.close()

        tmp_json = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        )
        from formatter import script_to_dict
        json.dump(script_to_dict(script), tmp_json, ensure_ascii=False, indent=2)
        tmp_json.close()

        return text_output, tmp_txt.name, tmp_json.name

    # ----- UI layout -----
    with gr.Blocks(title="短剧剧本生成智能体", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 🎬 短剧剧本生成智能体")
        gr.Markdown("输入主题概要，AI 自动生成完整短剧剧本（故事大纲 → 人物角色 → 分场剧本）")

        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### ⚙️ 配置")
                api_key_input = gr.Textbox(
                    label="OpenAI API Key",
                    placeholder="sk-…",
                    type="password",
                )
                base_url_input = gr.Textbox(
                    label="API Base URL（可选，默认 OpenAI 官方）",
                    placeholder="https://api.openai.com/v1",
                )
                model_input = gr.Textbox(
                    label="模型名称",
                    value="gpt-4o",
                )
                gr.Markdown("### 📝 剧本参数")
                theme_input = gr.Textbox(
                    label="主题概要 *",
                    placeholder="例：一个外卖小哥意外发现自己是亿万富翁的私生子，从此开始逆袭人生…",
                    lines=4,
                )
                with gr.Row():
                    episodes_input = gr.Slider(
                        label="集数", minimum=1, maximum=10, step=1, value=1
                    )
                    scenes_input = gr.Slider(
                        label="每集场次", minimum=3, maximum=15, step=1, value=8
                    )
                polish_input = gr.Checkbox(label="启用台词润色（耗时更长）", value=False)
                generate_btn = gr.Button("🚀 开始生成剧本", variant="primary")

            with gr.Column(scale=2):
                gr.Markdown("### 📄 生成结果")
                output_text = gr.Textbox(
                    label="剧本内容",
                    lines=40,
                    show_copy_button=True,
                )
                with gr.Row():
                    download_txt = gr.File(label="下载 TXT")
                    download_json = gr.File(label="下载 JSON")

        generate_btn.click(
            fn=generate_script,
            inputs=[
                api_key_input,
                base_url_input,
                model_input,
                theme_input,
                episodes_input,
                scenes_input,
                polish_input,
            ],
            outputs=[output_text, download_txt, download_json],
        )

    demo.launch(share=False)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="短剧剧本生成智能体",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--web", action="store_true", help="启动 Gradio Web 界面")
    mode.add_argument("--theme", type=str, help="短剧主题概要（命令行模式）")

    parser.add_argument("--episodes", type=int, default=1, help="集数（默认 1）")
    parser.add_argument("--scenes", type=int, default=8, help="每集场次数（默认 8）")
    parser.add_argument("--lang", type=str, default="zh", help="输出语言（zh/en，默认 zh）")
    parser.add_argument("--polish", action="store_true", help="启用台词润色（需额外 API 调用）")
    parser.add_argument("--output", type=str, default=None, help="输出文件路径前缀（不含后缀）")
    parser.add_argument("--model", type=str, default=None, help="覆盖默认模型")
    parser.add_argument("--api-key", type=str, default=None, help="OpenAI API Key")
    parser.add_argument("--base-url", type=str, default=None, help="OpenAI 兼容 API Base URL")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.web:
        run_web()
    elif args.theme:
        run_cli(args)
    else:
        parser.print_help()
        print(
            "\n💡 快速开始：\n"
            "   python main.py --theme '你的短剧主题' --episodes 2 --scenes 8\n"
            "   python main.py --web   # 启动网页界面\n"
        )


if __name__ == "__main__":
    main()
