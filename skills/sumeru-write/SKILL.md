---
name: sumeru-write
description: 小说章节内容创作与创意落地。用户要写一章小说、续写、扩写、重写、生成某个情节、按细纲写章节、批量生成章节、写开篇/高潮/过渡章，或要求"帮我写小说内容"时必须使用本技能。
type: skill
---

## 网文章节撰写

### 触发关键词
帮我写一章小说、续写接下来的内容、生成XX情节、批量写网文章节、扩写/重写这段内容、帮我写个XX情节、续写小说、把这段内容扩写、重写这一章、批量生成小说章节、写个开篇章节、写个高潮情节、小说内容生成、帮我写小说内容、网文章节生成、从细纲生成章节、按细纲写小说、批量生成所有章节、细纲驱动写作

### 核心功能
1. **基于完整细纲生成**：自动读取 `.sumeru/outline/chapter-outlines.json`，根据细纲批量生成章节
2. **智能细纲匹配**：支持按章节号、卷号、或全部章节进行生成
3. 自动适配网文节奏：开头抓眼球、中间有冲突、结尾留悬念
4. 保持人物性格、剧情逻辑的一致性
5. 支持自定义章节长度（默认4000-5000字/章）
6. 支持续写、修改、调整已有章节内容

### 独立调用自举
如果用户直接调用 `sumeru-write`，先执行 AGENTS.md 的"断点恢复与独立调用自举"：
- 定位项目根目录，读取或生成 `.sumeru/project.json`、`.sumeru/status.json`。
- 若缺少 `outlines/chapters.json`，尝试读取 `.sumeru/outline/chapter-outlines.json`；仍缺失时根据用户本次描述生成当前章节的临时任务卡。
- 若缺少 `.sumeru/cache/`，生成最小 `project-brief.md`、`style-brief.md`、`creative-brief.md`、`continuity-brief.md`。
- 若缺少当前范围的 `write-<range>.md` context pack，先生成临时 context pack 再写作。
- 根据 `chapters/` 已有文件推断续写位置，默认不覆盖已有章节。
- **写正文必须走子agent（即使是单章续写），父agent绝不写正文。**

### 按模式写作
- `short/light`：优先写入或续写 `story.md`；如用户指定章节，可写入 `chapters/`。不强制生成 context pack，除非内容很长或用户要求分章处理。
- `medium/standard`：按 `outlines/chapters.md` 或简化任务卡写入 `chapters/`；批量超过 3 章时可生成临时 context pack。
- `long/full`：必须使用拆分任务卡、cache 和 context pack；批量写作每个子Agent 1-3 章。

### 输入优先级
1. 用户本次明确要求（章节号、字数、风格、视角、必须出现/禁止出现的情节）优先级最高。
2. `.sumeru/context-packs/write-<range>.md` 是批量写作的首选输入。
3. `.sumeru/cache/project-brief.md`、`style-brief.md`、`creative-brief.md`、`continuity-brief.md` 是首选摘要输入。
4. `.sumeru/review/fix-plan.json` 中标记的重写要求优先于原细纲，用于返工章节。
5. `outlines/chapters/<id>.json` 或 `outlines/chapters.json` 中的目标章节任务卡是剧情依据。
6. `docs/creative-strategy.md`、`ideas/active.md` 和相关 ideas 条目用于保持创意策略。
7. `docs/style-guide.md`、`docs/glossary.md`、`docs/characters.md`、`docs/world.md` 仅在摘要不足时读取。
8. `.sumeru/project.json` 提供目标平台、章节字数范围和整体风格。
9. 已存在的 `chapters/` 内容用于续写和风格衔接。

### 低 Token 写作规则
- 如果存在 context pack，只读取 context pack、目标章节正文、必要的前一章结尾，不再读取全量 docs/outlines/ideas。
- `short/light` 不强制 context pack，优先读取 `outline.md`、`story.md` 和 `story-brief.md`。
- `medium/standard` 只在批量或上下文复杂时生成 context pack。
- 单章写作读取目标章节任务卡；三章批量读取三章任务卡和相邻章节摘要。
- 需要人物设定时优先读取 `character-brief.md`，不足时只读取相关人物文件或片段。
- 需要世界观时优先读取 `world-brief.md`，不足时只读取相关地点/组织/规则片段。

### 章节任务卡执行规则
- 每章先读取对应 `chapterId` 或 `chapterNumber` 的任务卡。
- 正文必须完成任务卡中的 `purpose`。
- 正文必须落实 `creativeGoal`、`freshnessHook`、`emotionalBeat`、`readerMemoryPoint`。
- 遇到 `tropeToAvoid` 时必须避开直给套路，选择替代写法。
- 若存在 `surpriseTwist`，必须提前埋下公平线索。
- 正文必须覆盖 `events` 中的关键事件。
- 正文必须落实 `outputs` 中的人物状态、道具状态、伏笔和下一章钩子。
- 正文必须满足全部 `acceptanceCriteria`。

### 创意落地检查
生成章节前先做 5 项自检：
1. 本章是否有读者能记住的一幕、一个选择或一句话。
2. 本章爽点是否和前 3 章重复；如重复，切换情绪类型或解决方式。
3. 主角是否通过选择推动局势，而不是被剧情推着走。
4. 反派或阻力是否足够聪明，是否让胜利付出代价。
5. 结尾钩子是否既承接本章输出，又诱导下一章点击。

### 细纲驱动批量生成
```
# 生成所有章节（读取细纲，自动并行）
/sumeru-write 全部章节

# 生成指定范围章节
/sumeru-write 第1-50章

# 生成特定卷的所有章节
/sumeru-write 第1卷

# 单章创作
/sumeru-write 第3章 "主角在拍卖会上获得神秘功法"

# 基于已有细纲生成
/sumeru-write 第3章 按细纲生成
```

### 章节文件命名规范
**强制格式：`{三位章节号}-{章节标题}.md`**
- 示例：`003-第一次解析.md`、`001-废物觉醒系统.md`
- ❌ 错误：`第3章-第一次解析.md`、`3-第一次解析.md`、`003_第一次解析.md`

### 数据持久化
**用户可见输出**：
- 生成的章节保存到 `chapters/` 下，严格遵循命名规范。
- 章节文件为纯净的正文内容，不含任何中间标记和元数据。

**中间数据（`.sumeru/write/`）**：
- `progress.json`：创作进度跟踪
- `chapter-meta.json`：每章元数据
- `character-state.json`：人物状态动态跟踪
- `used-outlines.json`：已使用的章节细纲记录
- `original/`：原始章节文件备份目录

### 与其他 Skill 配合
- **前置**：自动读取 `sumeru-outline` 的 `chapter-outlines.json`、`characters.json`、`world.json`
- **后续**：生成的章节数据可供 `sumeru-review`、`sumeru-polish`、`sumeru-finalize` 使用

### 全局约束引用
- 子Agent并行处理规则：见 AGENTS.md "子Agent并行处理规则"
- 职责边界：见 AGENTS.md "子Agent职责边界规则"
- 状态标记格式：见 AGENTS.md "子Agent输出状态标记"
- Context Pack 格式：见 AGENTS.md "Context Pack 格式"
- 独立调用自举：见 AGENTS.md "断点恢复与独立调用自举"
- 项目配置 Schema：见 AGENTS.md "项目配置 Schema"
