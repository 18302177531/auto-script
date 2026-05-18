# auto-script 🎬

根据主题概要自动编写生成短剧剧本的智能体。

## 功能特性

- **多步骤生成**：故事大纲 → 人物角色 → 分场剧本（多集支持）
- **短剧风格优化**：符合抖音/快手短视频平台受众口味，高密度情节、强悬念设计
- **台词润色**：可选的额外润色 pass，使对白更生动有力
- **双界面**：命令行（CLI）+ Gradio 网页界面
- **多格式导出**：纯文本 `.txt` 与结构化 `.json`
- **兼容任意 OpenAI 兼容 API**：支持 OpenAI、Azure OpenAI、本地部署模型等

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 设置 API Key

```bash
export OPENAI_API_KEY="sk-..."
# 如使用其他兼容 API（如 Azure/本地模型），同时设置：
export OPENAI_BASE_URL="https://your-endpoint/v1"
export OPENAI_MODEL="gpt-4o"   # 默认 gpt-4o
```

### 3. 命令行使用

```bash
# 最简用法
python main.py --theme "一个外卖小哥意外发现自己是亿万富翁的私生子"

# 生成 3 集，每集 8 场，开启台词润色，保存到文件
python main.py \
  --theme "古代穿越：现代女医生穿越成太子妃，用现代医术逆天改命" \
  --episodes 3 \
  --scenes 8 \
  --polish \
  --output ./output/my_script

# 指定模型 / API key
python main.py --theme "都市爽剧：被渣男背叛的女主一夜逆袭成为集团总裁" \
               --model gpt-4o \
               --api-key sk-...
```

### 4. 网页界面

```bash
python main.py --web
```

浏览器访问 `http://localhost:7860`，填写参数后点击「开始生成剧本」。

## 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--theme` | 短剧主题概要（必填，CLI 模式） | — |
| `--episodes` | 生成集数 | `1` |
| `--scenes` | 每集场次数 | `8` |
| `--polish` | 启用台词润色（需额外 API 调用） | `False` |
| `--output` | 输出文件路径前缀（不含后缀） | 仅打印到终端 |
| `--lang` | 输出语言（`zh` / `en`） | `zh` |
| `--model` | 覆盖默认模型 | `gpt-4o` |
| `--api-key` | OpenAI API Key | 从环境变量读取 |
| `--base-url` | OpenAI 兼容 API Base URL | 官方 OpenAI |
| `--web` | 启动 Gradio 网页界面 | — |

## 项目结构

```
auto-script/
├── main.py          # 入口：CLI + 网页界面
├── agent.py         # 核心智能体（多步骤生成逻辑）
├── prompts.py       # Prompt 模板（大纲 / 角色 / 分场 / 润色）
├── models.py        # 数据模型（Script / Episode / Scene / Dialogue）
├── formatter.py     # 格式化与导出工具（TXT / JSON）
├── config.py        # 配置管理
├── requirements.txt
└── README.md
```

## 生成流程

```
用户输入主题
    │
    ▼
Step 1: 生成故事大纲（标题、题材、一句话钩子、分集概要）
    │
    ▼
Step 2: 创建人物角色（3-5 个主要角色，含性格与背景）
    │
    ▼
Step 3: 逐集生成分场剧本（场景描述 + 对白 + 动作指示）
    │
    ▼
（可选）Step 4: 台词润色
    │
    ▼
输出：结构化 Script 对象 / TXT 文件 / JSON 文件
```

## 环境变量

| 变量 | 说明 |
|------|------|
| `OPENAI_API_KEY` | OpenAI API Key（必填） |
| `OPENAI_BASE_URL` | API Base URL（选填，默认官方） |
| `OPENAI_MODEL` | 默认模型（选填，默认 `gpt-4o`） |