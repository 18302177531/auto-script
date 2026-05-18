"""Prompt templates for the script generation agent."""

SYSTEM_PROMPT = """你是一位专业的短剧编剧，擅长创作引人入胜、节奏紧凑的短剧剧本。
你的剧本风格符合当下短视频平台（如抖音、快手）的受众口味：
- 开篇即高潮，前3秒抓住观众
- 情节反转多，悬念感强
- 人物性格鲜明，对白简练有力
- 情感张力足，爽感或虐感明显
- 场景描述清晰，易于拍摄落地

请严格按照要求的 JSON 格式输出，不要添加任何多余的文字或 Markdown 代码块标记。"""

OUTLINE_PROMPT = """根据以下主题概要，为短剧创作一个完整的故事大纲。

主题概要：{theme}
剧集数量：{episode_count}集
语言：{language}

请以 JSON 格式返回以下内容：
{{
  "title": "短剧标题",
  "genre": "题材类型（如：都市爽剧/古装甜宠/悬疑惊悚/霸总逆袭等）",
  "logline": "一句话故事钩子（吸引观众继续看的核心悬念）",
  "theme_summary": "核心主题总结",
  "episodes": [
    {{
      "number": 1,
      "title": "分集标题",
      "synopsis": "本集故事概要（100-150字）",
      "hook": "本集结尾悬念/反转点"
    }}
  ]
}}"""

CHARACTERS_PROMPT = """根据以下短剧大纲，创建主要人物角色。

剧名：{title}
题材：{genre}
故事概要：{logline}

请以 JSON 格式返回角色列表（3-5个主要角色）：
{{
  "characters": [
    {{
      "name": "角色姓名",
      "gender": "性别",
      "age": "年龄范围（如：25-30岁）",
      "role": "角色定位（主角/女主/反派/配角等）",
      "personality": "性格特点（3-4个关键词）",
      "background": "人物背景（50-80字）",
      "motivation": "核心动机（驱动其行动的根本原因）"
    }}
  ]
}}"""

SCENE_PROMPT = """根据以下信息，为短剧第{episode_number}集《{episode_title}》编写完整的分场剧本。

剧名：{title}
题材：{genre}
本集概要：{episode_synopsis}
结尾悬念：{episode_hook}

主要角色：
{characters_desc}

场景数量：{scene_count}场
要求：
- 每场戏对话简练有力，符合短剧节奏
- 对白口语化，有个性，避免书面语
- 每场戏都要有明确的情绪或信息推进
- 第一场必须立刻制造悬念或冲突
- 最后一场要留下下集的悬念（如非结局集）

请以 JSON 格式返回：
{{
  "scenes": [
    {{
      "number": 1,
      "location": "场景地点",
      "time_of_day": "时间（白天/夜晚/清晨/黄昏等）",
      "description": "场景描述（环境、氛围，30-50字）",
      "emotional_beat": "本场情绪基调（紧张/温馨/愤怒/惊喜等）",
      "dialogues": [
        {{
          "character": "角色名",
          "action": "动作/表情描述（可选）",
          "line": "台词"
        }}
      ],
      "notes": "导演提示（拍摄建议或特殊效果，可选）"
    }}
  ]
}}"""

POLISH_PROMPT = """请对以下短剧剧本的台词进行润色优化，使其更加生动、有冲击力。

原始剧本片段：
{script_excerpt}

优化要求：
1. 让对白更口语化、更有个性
2. 增强情感张力和冲突感
3. 添加适当的停顿、语气词让台词更自然
4. 保持角色性格一致性
5. 确保台词简短有力（短剧节奏）

请直接返回优化后的 JSON 格式台词列表，格式与输入相同。"""
