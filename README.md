# auto-script

一个根据“主题概要”自动生成中文短剧剧本的轻量智能体。

## 功能

- 输入主题概要（必填）
- 可选输入角色列表、集数、每集场景数
- 自动输出分集、分场景、含对白与舞台提示的短剧剧本

## 使用方式

```bash
python /home/runner/work/auto-script/auto-script/short_drama_agent.py \
  --topic "都市复仇，主角从外卖员逆袭揭露资本黑幕" \
  --characters "林川,苏曼,周董" \
  --episodes 2 \
  --scenes 2
```

或直接运行进入交互输入：

```bash
python /home/runner/work/auto-script/auto-script/short_drama_agent.py
```
