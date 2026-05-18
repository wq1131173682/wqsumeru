# AGENTS.md - 须弥写作 Skill 全局规则

## 项目定位

本仓库提供一组面向网文/小说创作的 AI Skill，覆盖选题、世界观与大纲、章节写作、剧情审查、文笔润色、完稿校验与平台导出。各 Skill 可以独立使用，也可以由 `sumeru-worldbuilder` 串联成完整创作流程。

## Skill 列表

```
skills/
├── sumeru-worldbuilder/  # 全流程编排
├── sumeru-topic/         # 选题策划
├── sumeru-outline/       # 大纲、世界观、人设、章节细纲
├── sumeru-write/         # 章节写作、续写、重写、扩写
├── sumeru-review/        # 剧情逻辑、时间线、OOC、伏笔审查
├── sumeru-polish/        # 文笔、节奏、爽点、对话润色
└── sumeru-finalize/      # 错别字、敏感词、排版、发布格式导出
```

每个 Skill 目录必须包含 `SKILL.md`，可按需包含 `scripts/` 和 `references/`。

## 数据与输出约定

- 中间数据统一写入当前创作项目的 `.sumeru/`，用于断点恢复、跨阶段复用和审查记录。
- 用户可直接阅读或发布的内容写入当前创作项目根目录，例如 `选题策划报告.md`、`docs/`、`outlines/`、`chapters/`、`reviews/`、`tests/`、`publish/`。
- 章节正文统一存放在 `chapters/`，文件名使用 `{三位章节号}-{章节标题}.md`，例如 `001-废柴觉醒.md`。
- 修改 `chapters/` 前必须先备份原文件到 `.sumeru/write/original/`，备份文件名应包含原章节名和时间戳，便于回滚。

## 小说项目标准目录

把一本小说当作一个长期开发项目维护。初始化新项目时，优先创建以下结构；已有项目缺少目录时按需补齐，不破坏用户已有文件。

项目结构必须按篇幅分层，不要让短篇承担长篇工程化成本。默认按 `projectMode` 和 `workflowLevel` 决定目录和流程复杂度。

| projectMode | workflowLevel | 适用范围 | 目标 |
|---|---|---|---|
| `short` | `light` | 1-10章，3万字以内，短篇/试写/单脑洞 | 快速产出，少文件，少状态 |
| `medium` | `standard` | 10-50章，3万-20万字，中篇/单卷故事 | 有结构但不过度工程化 |
| `long` | `full` | 50章以上，20万字以上，长篇/系列/多轮迭代 | 完整项目化、可断点、可测试、可发布 |

自动判断规则：

- `plannedChapters <= 10` 或 `plannedWords <= 30000`：默认 `short/light`。
- `plannedChapters <= 50` 或 `plannedWords <= 200000`：默认 `medium/standard`。
- `plannedChapters > 50` 或 `plannedWords > 200000`：默认 `long/full`。
- 用户显式指定“短篇模式/中篇模式/长篇工程模式”时，以用户指定为准。

`.sumeru/project.json` 必须记录：

```json
{
  "projectMode": "short|medium|long",
  "workflowLevel": "light|standard|full"
}
```

### short/light 结构

短篇优先灵感和完成度，不默认创建重型目录。

```
short-story/
├── README.md
├── story.md                  # 正文或合并稿
├── outline.md                # 简纲/三幕结构/五段式结构
├── review.md                 # 可选，一份综合审查
├── publish.md                # 可选，发布稿
└── .sumeru/
    ├── project.json
    ├── status.json
    └── cache/
        └── story-brief.md
```

short/light 默认不创建：`tests/`、`.sumeru/issues/`、`.sumeru/context-packs/`、复杂 `continuity/`、拆分章节任务卡。只有用户要求或内容扩展时再创建。

### medium/standard 结构

中篇保留结构和缓存，但避免完整长篇工程化。

```
novella-project/
├── README.md
├── NOVEL.md
├── docs/
│   ├── requirements.md
│   ├── outline.md
│   ├── characters.md
│   ├── style-guide.md
│   └── creative-strategy.md
├── outlines/
│   └── chapters.md           # 章节简纲，必要时升级为 JSON
├── chapters/
├── publish/
└── .sumeru/
    ├── project.json
    ├── status.json
    ├── issues.md             # 轻量问题清单
    └── cache/
```

medium/standard 可按需创建 `reviews/`、`tests/review-report.md`、`.sumeru/context-packs/`。只有章节超过 30、批量子Agent处理、或用户要求时，才拆分 `outlines/chapters.index.json` 和 `outlines/chapters/*.json`。

### long/full 结构

长篇启用完整工程化结构：

```
novel-project/
├── README.md                  # 项目说明：题材、目标平台、当前阶段、使用方式
├── NOVEL.md                   # 小说总控：一句话卖点、核心爽点、主线目标
├── docs/
│   ├── requirements.md        # 创作需求文档，类似产品需求文档
│   ├── architecture.md        # 故事架构：主线、冲突、成长、信息揭示节奏
│   ├── world.md               # 世界观设定
│   ├── characters.md          # 人物设定
│   ├── plot.md                # 主线/支线/分卷规划
│   ├── style-guide.md         # 文风规范、禁用表达、平台风格
│   └── glossary.md            # 术语、人物、地点、功法、组织命名表
├── outlines/
│   ├── chapters.json          # 章节任务卡，供写作和审查使用
│   └── volume-*.md            # 分卷细纲，可选
├── ideas/                     # AI 创意引擎：灵感、反转、爽点、场景碎片
├── chapters/                  # 正文，按 001-标题.md 命名
├── reviews/                   # 用户可读审查报告
├── tests/                     # 连贯性、字数、伏笔、格式等检查结果
├── drafts/                    # 试写、废稿、A/B 版本、重写草稿
├── publish/                   # 发布构建产物
└── .sumeru/
    ├── project.json           # 项目配置，所有 Skill 启动时优先读取
    ├── status.json            # 阶段状态、章节状态、最近操作
    ├── backlog.md             # 待办事项、待补设定、剧情坑
    ├── decisions.md           # 重要创作决策记录，类似 ADR
    ├── changelog.md           # 每轮改动记录
    ├── continuity/            # 连贯性状态库
    ├── issues/                # 结构化问题单
    ├── cache/                 # 稳定摘要缓存，降低重复读取成本
    ├── context-packs/         # 子Agent任务上下文包
    ├── snapshots/             # 关键阶段快照
    └── */                     # 各 Skill 私有中间数据
```

### 模式升级与降级

- `short -> medium`：当短篇扩写到 10 章以上，补齐 `docs/`、`outlines/`、`chapters/`、标准 cache。
- `medium -> long`：当中篇扩写到 50 章以上或需要长期断点/批量审查，补齐 `ideas/`、`tests/`、`.sumeru/issues/`、`.sumeru/context-packs/`、`.sumeru/continuity/`，并拆分章节任务卡。
- `long -> medium/short`：一般不自动降级；除非用户明确要求精简项目结构，只停止创建新增重型文件，不删除已有内容。
- 升级时追加记录到 `.sumeru/decisions.md` 和 `.sumeru/changelog.md`。

兼容规则：旧版 `.sumeru/outline/chapter-outlines.json` 仍可读取，但新项目应同步生成 `outlines/chapters.json`。二者同时存在时，以 `outlines/chapters.json` 作为章节任务卡主来源，并把 `.sumeru/outline/chapter-outlines.json` 作为兼容副本。

## 上下文预算与缓存策略

长篇项目必须控制 token、文件读取次数和子Agent调用成本。所有 Skill 默认采用“索引优先、摘要优先、任务包优先、原文按需”的加载方式。

### 文件加载层级

**L0 常驻配置层**：每次任务可读取，必须保持短小。

```
.sumeru/project.json
.sumeru/status.json
```

**L1 稳定摘要缓存层**：由 worldbuilder 或相关 skill 维护，优先读摘要而不是读原始大文件。

```
.sumeru/cache/project-brief.md
.sumeru/cache/world-brief.md
.sumeru/cache/character-brief.md
.sumeru/cache/style-brief.md
.sumeru/cache/creative-brief.md
.sumeru/cache/continuity-brief.md
.sumeru/cache/issue-brief.md
.sumeru/cache/latest-test-summary.md
```

**L2 任务上下文包**：每个子Agent优先只读取自己的 context pack。

```
.sumeru/context-packs/write-001-003.md
.sumeru/context-packs/review-001-003.md
.sumeru/context-packs/polish-001-003.md
.sumeru/context-packs/finalize-001-010.md
```

**L3 原始大文件层**：只有摘要和上下文包不足时才读取。

```
docs/*.md
ideas/*.md
outlines/**/*.json
chapters/*.md
tests/*.md
.sumeru/issues/*.md
```

### 读取预算规则

- 不要全文读取大型文件，除非文件很小或用户明确要求全文分析。
- `outlines/chapters.json` 超过 20 章时，不应作为常规写作输入全文读取，应拆分为 `outlines/chapters.index.json` 与 `outlines/chapters/*.json`。
- 单章/三章写作只读取目标章节任务卡、前 1 章摘要、后 1 章任务卡摘要、相关人物和术语摘要。
- 批量子Agent只读取 `.sumeru/context-packs/<task>-<range>.md`，不得自行全量扫描项目。
- `ideas/` 默认只读取 `ideas/active.md`、`ideas/index.json` 和任务相关条目，不读取 `ideas/discarded.md` 或 `ideas/archive/`。
- `tests/` 默认只读取 `.sumeru/cache/latest-test-summary.md`；需要定位问题时再读对应测试报告。
- `.sumeru/issues/` 默认只读取 `.sumeru/issues/index.json` 和 `.sumeru/cache/issue-brief.md`；需要修复时再读相关 issue 文件。
- 章节正文默认只读目标章节、前 1 章和必要的后续任务卡；全本 review 先用索引和摘要轻扫。

### 大文件拆分约定

章节任务卡可采用单文件或拆分文件。长篇项目优先拆分：

```
outlines/
├── chapters.index.json        # 章节编号、标题、卷、状态、目的、情绪节拍摘要
├── chapters/
│   ├── 001.json
│   ├── 002.json
│   └── 003.json
└── volumes/
    ├── 001.json
    └── 002.json
```

人物和设定可拆分：

```
docs/characters/
├── index.md
├── protagonist.md
├── main-cast.md
├── antagonists.md
└── minor/
```

创意库存可拆分：

```
ideas/
├── index.json
├── active.md
├── concept-pitches.md
├── trope-breaker.md
└── archive/
```

### Context Pack 格式

worldbuilder 调用批量子Agent前，应先生成 context pack。context pack 只包含完成该任务所需的最小上下文，建议控制在 1500-3000 中文字，复杂任务最多不超过 5000 中文字。

```markdown
# Context Pack: write 037-039

## Project Brief
题材、平台、字数范围、整体风格。

## Current Volume
本卷目标、当前冲突、卷级反转、阶段情绪。

## Relevant Characters
只列本组章节相关人物的当前状态、目标、关系和语言风格。

## Relevant World & Glossary
只列本组章节会用到的地点、组织、功法、道具、禁用变体。

## Continuity State
上一章结尾、关键道具状态、未回收伏笔、时间线位置。

## Creative Strategy
本组章节创意目标、要避开的套路、情绪节拍变化、读者记忆点。

## Chapter Cards
目标章节任务卡，包含 purpose、events、outputs、acceptanceCriteria、creativeGoal。

## Output Requirements
文件命名、状态更新、需要写回的 continuity/cache 文件。
```

### 缓存刷新规则

- 修改 `docs/world.md` 后刷新 `.sumeru/cache/world-brief.md`。
- 修改 `docs/characters.md` 或 `docs/characters/` 后刷新 `.sumeru/cache/character-brief.md`。
- 修改 `docs/style-guide.md` 后刷新 `.sumeru/cache/style-brief.md`。
- 修改 `docs/creative-strategy.md` 或 `ideas/active.md` 后刷新 `.sumeru/cache/creative-brief.md`。
- 写作、审查、润色修改章节后刷新 `.sumeru/cache/continuity-brief.md`。
- 审查生成 issue 后刷新 `.sumeru/cache/issue-brief.md` 和 `.sumeru/cache/latest-test-summary.md`。

## 断点恢复与独立调用自举

用户可能不通过 `sumeru-worldbuilder`，而是直接调用 `sumeru-write`、`sumeru-review`、`sumeru-polish` 或 `sumeru-finalize`。任何 Skill 单独启动时，都必须执行同一套自举流程，确保也能吃到项目结构、缓存、context pack 和状态机规则。

### 自举流程

1. **定位项目根目录**：从当前目录向上查找 `.sumeru/project.json`、`.sumeru/status.json`、`NOVEL.md`、`chapters/`、`outlines/`。找到任一组合即可视为候选项目根。
2. **识别项目版本**：若存在 `.sumeru/project.json`，按新协议执行；若只存在旧版 `.sumeru/outline/chapter-outlines.json` 或 `chapters/`，进入兼容模式。
3. **最小初始化**：缺少 `.sumeru/project.json` 时，根据已有文件生成最小配置；缺少 `.sumeru/status.json` 时，根据 `chapters/`、`outlines/`、`publish/` 推断阶段和章节状态。
4. **补齐目录**：按需创建 `.sumeru/cache/`、`.sumeru/context-packs/`、`.sumeru/issues/`、`.sumeru/continuity/`、`tests/`、`reviews/`。不要覆盖用户已有内容。
5. **迁移兼容输入**：若只有 `.sumeru/outline/chapter-outlines.json`，可以继续读取；长篇项目应生成 `outlines/chapters.index.json` 和 `outlines/chapters/*.json` 的拆分副本。
6. **刷新摘要缓存**：如果相关 cache 缺失或明显过期，先生成最小摘要，例如 `project-brief.md`、`style-brief.md`、`creative-brief.md`、`continuity-brief.md`。
7. **生成本次 context pack**：如果直接执行章节级任务且缺少对应 context pack，本 skill 应为当前范围生成临时 context pack，再执行任务。
8. **执行任务并回写状态**：任务完成后更新 `.sumeru/status.json`、相关 cache、issue/test/manifest 文件。
9. **记录变更**：把关键动作追加到 `.sumeru/changelog.md`；涉及创作决策时追加到 `.sumeru/decisions.md`。

### 最小配置推断

缺少 `.sumeru/project.json` 时，生成最小字段：

```json
{
  "schemaVersion": 1,
  "title": "未命名作品",
  "genre": "未确认",
  "targetPlatform": "未确认",
  "audience": "未确认",
  "plannedWords": null,
  "plannedChapters": null,
  "chapterWordRange": [2000, 3000],
  "style": "未确认",
  "tone": "未确认",
  "currentStage": "detected",
  "createdAt": "自动生成",
  "updatedAt": "自动生成",
  "inferred": true
}
```

缺少 `.sumeru/status.json` 时，根据文件推断：

- 有 `outlines/chapters.json` 或 `.sumeru/outline/chapter-outlines.json`：`outline` 至少为 `completed`。
- `chapters/` 有正文：对应章节状态至少为 `drafted`。
- `reviews/` 或 `.sumeru/issues/index.json` 存在：`review` 至少为 `completed` 或 `in_progress`。
- 有润色摘要或 polish 记录：相关章节至少为 `polished`。
- `publish/` 有产物：相关章节至少为 `exported`。

### 独立调用原则

- 单独调用 skill 时，不要求用户先运行 worldbuilder。
- 能从现有项目文件推断的信息，不重复询问用户。
- 缺少关键信息但不阻塞任务时，使用合理默认值并写入 `docs/requirements.md` 的“待确认问题”。
- 缺少关键信息且会影响输出正确性时，只问最少问题。
- 不因为缓存缺失而失败；缓存缺失时生成最小缓存。
- 不因为 context pack 缺失而全量读取项目；先生成当前任务的 context pack。
- 兼容旧项目，但新写入内容应遵守新项目结构。

## 项目配置 Schema

`.sumeru/project.json` 是全项目唯一配置源。Skill 不应反复向用户询问已写入配置的稳定信息。

```json
{
  "schemaVersion": 1,
  "title": "未命名作品",
  "genre": "玄幻",
  "targetPlatform": "番茄",
  "audience": "男频",
  "plannedWords": 800000,
  "plannedChapters": 300,
  "chapterWordRange": [2000, 3000],
  "style": "快节奏爽文",
  "tone": "热血",
  "currentStage": "outline",
  "createdAt": "2026-05-16T00:00:00Z",
  "updatedAt": "2026-05-16T00:00:00Z"
}
```

`.sumeru/status.json` 记录状态机和章节进度。

```json
{
  "currentStage": "write",
  "stages": {
    "init": "completed",
    "topic": "completed",
    "outline": "completed",
    "write": "in_progress",
    "review": "pending",
    "polish": "pending",
    "finalize": "pending"
  },
  "chapters": {
    "001": "finalized",
    "002": "polished",
    "003": "drafted"
  },
  "lastAction": "generated chapter 003"
}
```

阶段状态只能使用：`pending`、`in_progress`、`blocked`、`completed`、`skipped`。

章节状态只能使用：`planned`、`drafted`、`reviewed`、`fixed`、`polished`、`finalized`、`exported`。

## AI 创意引擎

工程化结构用于保证长篇不崩，创意引擎用于保证作品有新鲜感、记忆点和传播性。所有策划、大纲、写作、审查、润色阶段都应显式考虑创意，而不是只完成剧情功能。

初始化项目时创建 `ideas/` 目录：

```
ideas/
├── concept-pitches.md      # 高概念一句话与安利句
├── hooks.md                # 开篇钩子、章节钩子、卷末钩子
├── twists.md               # 意外但合理的反转库
├── cool-points.md          # 爽点库：打脸、升级、智斗、情绪释放等
├── character-seeds.md      # 人物种子、隐藏动机、角色缺陷
├── scene-fragments.md      # 场景碎片、画面记忆点、对白火花
├── emotional-beats.md      # 情绪节拍与情绪曲线变体
├── trope-breaker.md        # 套路规避、反套路替代方案
└── discarded.md            # 暂不使用但保留的创意
```

创意引擎必须服务故事，不应为了猎奇破坏类型承诺。创意选择遵循以下评分：

- 新鲜度：是否避免同质化套路。
- 爽感：是否提供清晰情绪价值。
- 合理性：是否符合已建立设定和伏笔。
- 可持续性：是否能支撑后续章节，而不是一次性噱头。
- 传播性：是否有一句话安利点或读者记忆点。
- 类型契合度：是否仍满足目标平台和目标读者期待。

### 高概念打磨
选题和大纲阶段必须形成至少 3 个高概念 pitch，并选择 1 个作为主 pitch。

高概念 pitch 格式：

```markdown
## Pitch A
- 一句话：一个只能靠失败升级的天才，被迫把所有胜利都伪装成失败。
- 类型混血：高武玄幻 + 反向升级系统 + 校园竞技
- 核心反差：越强越要装弱，越赢越危险
- 爽点来源：读者知道主角在赢，书中角色以为他在输
- 代价/限制：系统只承认公开失败，私下胜利不计入成长
- 传播句：别人都怕输，只有他怕赢得太明显。
```

### 创意变异
对常见设定至少做 5 个变异，再选用。变异方向包括：

- 反向规则：奖励变惩罚，外挂变负担，胜利变风险。
- 代价机制：每次获得力量都失去记忆、关系、身份、寿命、信用等。
- 视角错位：读者知道真相，角色误解；或角色知道，读者后知后觉。
- 类型嫁接：把不同类型的核心机制嫁接到当前题材。
- 情绪换轨：同一桥段从打脸爽改为智斗爽、心疼爽、反差爽、宿命感。

### 反套路检查
生成选题、大纲、章节前检查：

- 这个桥段是否太常见？
- 读者是否能提前猜到解决方式？
- 有没有比“反派嘲讽→主角打脸”更有记忆点的版本？
- 爽点是否来自角色选择和局势反转，而不只是战力碾压？
- 这个创意是否破坏类型读者期待？如果破坏，是否有足够收益？

### 意外但合理
每卷至少规划 1-3 个“意外但合理”的反转。反转必须包含公平线索：

```json
{
  "expectedDirection": "主角会在拍卖会上买下宝物",
  "surpriseTwist": "主角故意不买，让反派高价拍下，因为宝物只有在反派家族血脉中才会暴露缺陷",
  "fairClues": [
    "前文提到宝物会吸收血气",
    "前文提到反派家族修炼血系功法"
  ],
  "payoffChapter": 18
}
```

### 情绪差异化
连续章节不应只重复同一种爽点。`outlines/chapters.json` 应记录每章的 `emotionalBeat`，用于检查情绪疲劳。

常见情绪节拍：

- 压抑 → 反转 → 释放
- 困惑 → 恍然 → 暗爽
- 期待 → 失落 → 二次反转
- 轻松 → 危机 → 热血
- 心疼 → 守护 → 关系升温
- 怀疑 → 试探 → 信任建立

### 角色主动性压力测试
大纲和审查阶段必须检查主要角色是否只是剧情工具。对主角、反派、重要配角分别回答：

- 他/她此阶段最想要什么？
- 如果没有主线安排，他/她会主动做什么？
- 他/她的私心会如何干扰主线？
- 他/她有没有做出让局势改变的选择？
- 反派是否足够聪明，是否真的给主角制造了代价？

## 章节任务卡

章节不是单纯的文本生成任务，而是一个带输入、输出和验收标准的 feature。`outlines/chapters.json` 中每章应尽量包含：

```json
{
  "chapterNumber": 12,
  "chapterId": "012",
  "title": "拍卖会风波",
  "status": "planned",
  "purpose": "让主角第一次公开展现判断力并获得关键道具",
  "creativeGoal": "制造一次读者预期反转，并留下可传播的名场面",
  "tropeToAvoid": "反派嘲讽后主角直接加价打脸",
  "freshnessHook": "主角故意让反派拍下宝物，因为宝物会暴露反派家族弱点",
  "emotionalBeat": "压抑 → 困惑 → 恍然 → 暗爽",
  "readerMemoryPoint": "反派以为自己赢了，实际买下的是主角留给他的雷",
  "surpriseTwist": {
    "twist": "主角不竞拍真正宝物，而是竞拍能激活宝物缺陷的废料",
    "fairClues": ["废料与宝物来自同一矿脉", "主角前章发现残片会共鸣"]
  },
  "suggestedWords": "2500-3000",
  "inputs": {
    "previousState": "主角刚获得第一桶金",
    "requiredCharacters": ["林澈", "沈青鸢"],
    "requiredForeshadowing": ["黑色残片"]
  },
  "events": [
    "主角进入拍卖会",
    "反派抬价羞辱",
    "主角识破残片真实价值"
  ],
  "outputs": {
    "characterStateChanges": ["沈青鸢开始怀疑主角并非普通人"],
    "itemStateChanges": ["黑色残片归主角所有"],
    "foreshadowingAdded": ["残片来自上古遗迹"],
    "nextHooks": ["残片夜晚发热"]
  },
  "acceptanceCriteria": [
    "本章必须出现一次反派抬价打压",
    "主角不能暴露真正实力",
    "结尾必须留下残片异常的悬念"
  ]
}
```

`sumeru-write` 必须按 `acceptanceCriteria` 生成章节；`sumeru-review` 必须检查章节正文是否满足这些验收标准；`sumeru-polish` 不得破坏已满足的验收标准。

同时，`sumeru-write` 应尽量落实 `creativeGoal`、`freshnessHook`、`emotionalBeat` 和 `readerMemoryPoint`；`sumeru-review` 应检查套路重复、情绪重复和创意目标是否落地；`sumeru-polish` 应强化记忆点与情绪释放。

## Issue 与 Test 体系

剧情审查应像项目测试一样输出结构化结果。

- `.sumeru/issues/index.json`：所有问题的索引，字段包含 `id`、`type`、`severity`、`chapters`、`status`、`ownerSkill`。
- `.sumeru/issues/ISSUE-0001-*.md`：单个问题的可读说明，包含问题、证据、影响、建议修复、状态。
- `tests/continuity-report.md`：时间线、人物状态、物品状态、地点、信息边界检查。
- `tests/chapter-acceptance-report.md`：章节任务卡验收结果。
- `tests/foreshadowing-report.md`：伏笔新增、推进、回收、遗留状态。
- `tests/word-count-report.md`：章节字数检查。
- `tests/release-check-report.md`：发布前格式、敏感内容、TODO、缺章检查。

Issue 状态只能使用：`open`、`fixed`、`wontfix`、`needs-rewrite`、`needs-user-decision`。

## Build 与 Release

完稿导出视为 build/release 流程。

- build 前必须检查章节状态，默认只导出 `finalized` 或用户明确允许的章节。
- build 前必须检查是否存在 `TODO`、`FIXME`、未关闭的 `critical`/`major` issue、未回收关键伏笔。
- build 输出写入 `publish/`，并生成 `.sumeru/finalize/build-manifest.json`。
- release 报告应列出输入章节范围、平台格式、总字数、未解决风险和产物路径。

## 子Agent并行处理规则

所有涉及章节级批量操作的 Skill 必须遵守以下规则：

- 适用范围：章节写作、章节重写、剧情审查、轻量修复、内容润色、完稿校验、平台导出、章节细纲生成。
- **写正文必须走子agent，单章续写也必须走子agent，父agent绝不写正文。**
- 子agent并行数上限：**最多 5 个子agent同时运行**。
- 当处理章节数大于 3 章时，优先使用子Agent并行处理。
- 每个子Agent最多负责 3 个连续章节，不得把大批量章节交给单个子Agent。
- 所需Agent数 = `min(ceil(章节总数 / 3), 5)`。超过5章时，先启动5个Agent，完成后根据剩余章节再启动下一批。
- 分配策略按章节顺序连续分组，例如 1-3、4-6、7-9。
- 每个子Agent只接收完成任务所需的精简上下文，避免把全书正文塞入单个上下文。
- 汇总阶段必须检查章节数量、命名、顺序、上下文衔接和输出完整性。

此约束用于避免上下文溢出、章节质量下降和跨章状态混乱。

## 子Agent职责边界规则

**核心原则：子Agent只做"单一核心任务"，所有状态维护、文件写入、缓存刷新、汇总合并均由父Agent（调度器）统一处理。**

### 父Agent（调度器）职责

| 职责 | 说明 |
|------|------|
| 自举 & 环境准备 | 定位项目、读/生成 project.json、status.json、补齐目录 |
| Context pack 生成 | 集中生成 context pack，控制 1500-3000 中文字，分发给各子Agent |
| Cache 摘要读取 | 集中读取 L1 cache 摘要（project-brief、style-brief、creative-brief、continuity-brief 等），塞入 context pack |
| 任务卡读取 | 集中读取目标章节任务卡（outlines/chapters/*.json），仅提取本组章节所需字段 |
| 任务分发 | 启动 N 个子Agent，每个传入精简 context pack |
| 结果汇总 | 收集所有子Agent输出，检查完整性、顺序、命名 |
| 文件写入 | 统一写入输出文件（chapters/、outlines/、reviews/ 等），避免并发冲突 |
| 备份 | 修改前将原文件备份到 `.sumeru/write/original/` |
| 状态更新 | 统一更新 `.sumeru/status.json`（章节状态、阶段状态） |
| 缓存刷新 | 统一刷新相关 cache 摘要（continuity-brief、issue-brief、style-brief 等） |
| 日志记录 | 统一追加 `.sumeru/changelog.md`、`.sumeru/decisions.md` |
| Issue/测试汇总 | 合并各子Agent发现的问题，写入 `.sumeru/issues/` 和 `tests/` |

### 子Agent（执行器）职责

| 职责 | 说明 |
|------|------|
| 只读 context pack | 不读取任何额外文件，context pack 外的一切文件访问均视为违规 |
| 执行核心任务 | 根据 context pack 中的任务卡/审查标准/润色要求，完成单一核心任务 |
| 输出纯结果 | 输出纯文本结果（正文、审查结论、润色后文本、细纲），不包含状态更新指令 |
| 不碰状态 | 不更新 status.json、不写 changelog、不刷 cache、不写 issues |

### 各 Skill 子Agent职责明细

| Skill | 子Agent核心任务 | 子Agent输入 | 子Agent输出 | 父Agent后续处理 |
|-------|----------------|------------|------------|----------------|
| **sumeru-write** | 按任务卡写正文（**单章续写也走子agent**） | context pack（含任务卡、**前一章结尾**、人物/世界观摘要） | 纯正文文本 | 写入 chapters/、备份、更新 status、刷新 continuity cache、追加 ideas/scene-fragments |
| **sumeru-review** | 按任务卡审查章节 | context pack（含任务卡、正文、审查标准） | 审查结论（问题列表、严重程度、证据、建议） | 合并所有子Agent问题、写入 issues/、生成 tests/、制定 fix-plan |
| **sumeru-polish** | 按标准润色章节 | context pack（含正文、style-brief、creative-brief、审查问题） | 润色后正文 + diff 说明 | 写入 chapters/（覆盖原文）、备份、更新 status→polished、刷新 continuity cache |
| **sumeru-outline** | 生成章节细纲 | context pack（含世界观、人物、分卷大纲、上下文关联） | 章节细纲 JSON/Markdown | 合并所有子Agent细纲、校验一致性、写入 outlines/chapters.json、刷新 cache |

### Context Pack 精简规则

context pack 必须控制在 **1500-3000 中文字**，复杂任务最多不超过 5000 中文字。结构如下：

```markdown
# Context Pack: <task>-<range>

## Project Brief (1-2行)
题材、平台、字数范围、整体风格。

## Current Volume (1-2行)
本卷目标、当前冲突、卷级反转、阶段情绪。

## Relevant Characters (仅本组章节相关)
相关人物的当前状态、目标、关系、语言风格。

## Relevant World & Glossary (仅本组章节会用到的)
地点、组织、功法、道具、禁用变体。

## Continuity State (仅本组章节需要的)
上一章结尾、关键道具状态、未回收伏笔、时间线位置。

## Creative Strategy (仅本组章节需要的)
创意目标、要避开的套路、情绪节拍变化、读者记忆点。

## Chapter Cards (仅本组章节)
目标章节任务卡，包含 purpose、events、outputs、acceptanceCriteria、creativeGoal。

## Output Requirements (仅本组章节)
文件命名、状态更新需求（由父agent执行，子agent无需关心）。
```

**关键约束**：
- context pack 中不得包含全本正文、全本任务卡、全本 issues。
- 子Agent收到 context pack 后，**不得以任何理由读取 context pack 之外的文件**。
- 如果 context pack 信息不足导致任务无法完成，子Agent应明确说明缺失信息，由父Agent补充后重试。

## 修改边界

- `sumeru-review` 可以直接修复错别字、轻微逻辑补丁、字数不足补充、局部段落顺序等轻量问题。
- `sumeru-review` 不应直接大面积重写章节；严重剧情矛盾、设定崩坏、大面积 OOC 应写入 `.sumeru/review/fix-plan.json`，由 `sumeru-worldbuilder` 编排或用户手动调用 `sumeru-write` 处理。
- `sumeru-polish` 可以直接修改 `chapters/` 做文笔、节奏、对话、爽点优化，但不得改变主线事实、关键设定和角色关系，除非用户明确要求。
- `sumeru-finalize` 专注技术性校验和发布格式，不承担剧情重构和文风再创作。
- 下游 Skill 不直接调用上游 Skill；需要返工时输出结构化计划，由 `sumeru-worldbuilder` 或用户决定下一步。

## 质量检查

执行任一 Skill 后，应至少检查：

- 预期输出文件是否生成。
- `.sumeru/` 中的结构化数据是否与用户可见输出一致。
- 章节文件是否按三位编号排序且没有缺章、重章。
- 修改型 Skill 是否已生成备份和变更记录。
- 报告中是否区分已修复问题、待用户确认问题和需要重写的问题。

## 写作安全与原创性

- 避免直接复刻现实公众人物、真实组织、真实地名、知名 IP 角色和受版权保护的具体设定。
- 用户要求参考某作品时，只学习节奏、类型结构和读者情绪价值，不复用具体人物、世界观、桥段或专有名词。
- 涉及敏感、血腥、低俗、未成年人不当内容时，优先进行合规化改写并在报告中说明风险。
