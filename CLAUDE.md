# CLAUDE.md - 须弥写作当前协议

本仓库当前以 `AGENTS.md` 和 `skills/sumeru-rules/SKILL.md` 为准。此文件只保留 Claude Code 兼容入口，避免旧目录协议污染执行。

## 当前 Skill

```
skills/
├── sumeru-worldbuilder/
├── sumeru-topic/
├── sumeru-outline/
├── sumeru-write/
├── sumeru-write-core/
├── sumeru-review/
├── sumeru-polish/
├── sumeru-finalize/
└── sumeru-rules/
```

`sumeru-write-core` 是 `sumeru-write` 的通用写作规则，不是独立用户入口。写作只使用一种通用模式。

## Canonical 路径

新写入只使用当前轻量结构：

- `plan.md`：需求、设定、人物、风格、创意策略、术语
- `outline.md`：故事结构、主线、伏笔、分卷与章节规划摘要
- `outlines/chapters.json`：章节任务卡
- `chapters/` 或短篇 `story.md`：正文
- `.sumeru/issues.md`：问题清单
- `publish/`：发布产物

旧路径如 `docs/*`、`ideas/*`、`.sumeru/issues/index.json`、`.sumeru/outline/chapter-outlines.json` 只读兼容，不再作为新写入目标。

## 执行原则

- 默认 `quiet`，只输出进度、关键结果和必要警告。
- 默认最小消耗：只读当前任务必要上下文，不全量读取项目。
- 正文写作、审查修复、润色默认直接产出最终版本，修改前保留最小备份。
- 剧情统一优先：人物位置、道具状态、时间线、伏笔和战力必须与 continuity 一致。
- 发布导出必须剥离 `SUMERU_STATUS` 注释。
- 子Agent只读 context pack，只返回文本结果，不写项目文件。

详细规则见 `AGENTS.md` 与 `skills/sumeru-rules/SKILL.md`。
