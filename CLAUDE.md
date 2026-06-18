# CLAUDE.md - 须弥写作当前协议

本仓库以 `skills/sumeru-rules/SKILL.md` 为唯一全局约束源。

## 当前 Skill

```
skills/
├── sumeru-worldbuilder/
├── sumeru-topic/          # 选题策划（拆自 outline）
├── sumeru-outline/        # 大纲设计（拆自 outline）
├── sumeru-write/
├── sumeru-scan/           # 扫榜分析与竞品拆解
├── sumeru-review/
├── sumeru-polish/
├── sumeru-finalize/
├── sumeru-migrate/        # 旧项目迁移与规整
└── sumeru-rules/          # 全局约束（唯一来源）
```

## Canonical 路径

以 `skills/sumeru-rules/SKILL.md` 第三部分·Canonical 路径为准。概要如下：

### 用户可见文件（项目根目录）
- `NOVEL.md`：小说说明（名字、简介、类型、状态、进度）
- `plan.md`：需求、设定、人物、风格、创意策略、术语
- `outline.md`：故事结构、主线、伏笔、分卷与章节规划摘要
- `chapters/`：正文，按 001-标题.md 命名（短篇可用 `story.md`）
- `characters/`：人物卡（每人一文件）
- `world.md`：世界观手册（long/full 模式）
- `reviews/`：审查报告
- `tests/`：检查报告
- `publish/`：发布产物

### AI 内部数据（.sumeru/ 目录）
- `.sumeru/project.json`：项目配置
- `.sumeru/status.json`：阶段和章节状态
- `.sumeru/intro.md`：小说简介
- `.sumeru/issues.md`：问题清单
- `.sumeru/outlines/chapters.json`：章节任务卡
- `.sumeru/cache/`：摘要缓存
- `.sumeru/context-packs/`：子Agent上下文包
- `.sumeru/continuity/`：剧情一致性数据

## 执行原则

- 默认 `quiet`，只输出进度、关键结果和必要警告。
- 默认最小消耗：只读当前任务必要上下文，不全量读取项目。
- 正文写作、审查修复、润色默认直接产出最终版本，修改前保留最小备份。
- 剧情统一优先：人物位置、道具状态、时间线、伏笔和战力必须与 continuity 一致。
- 发布导出必须剥离 `SUMERU_STATUS` 注释。
- 子Agent只读 context pack，只返回文本结果，不写项目文件。

详细规则见 `skills/sumeru-rules/SKILL.md`。
