---
name: sumeru-write
description: 小说章节内容创作与创意落地。用户要写一章小说、续写、扩写、重写、生成某个情节、按细纲写章节、批量生成章节、写开篇/高潮/过渡章，或要求“帮我写小说内容”时必须使用本技能。它优先读取 .sumeru/context-packs/write-*.md 与 .sumeru/cache/*.md，必要时读取拆分后的 outlines/chapters/*.json、docs/creative-strategy.md、docs/style-guide.md、docs/glossary.md、docs/characters.md 和 docs/world.md，按 acceptanceCriteria 生成 chapters/ 下的正文文件，同时落实 creativeGoal、freshnessHook、emotionalBeat、readerMemoryPoint，并更新章节状态。批量生成时每个子Agent最多负责3章。
type: skill
---

## 网文章节撰写

### 触发关键词
帮我写一章小说、续写接下来的内容、生成XX情节、批量写网文章节、扩写/重写这段内容、帮我写个XX情节、续写小说、把这段内容扩写、重写这一章、批量生成小说章节、写个开篇章节、写个高潮情节、小说内容生成、帮我写小说内容、网文章节生成、从细纲生成章节、按细纲写小说、批量生成所有章节、细纲驱动写作

### 核心功能
1. **基于完整细纲生成**：自动读取 `.sumeru/outline/chapter-outlines.json`，根据细纲批量生成章节
2. **智能细纲匹配**：支持按章节号、卷号、或全部章节进行生成
3. 基于大纲和细纲生成完整章节内容
4. 自动适配网文节奏：开头抓眼球、中间有冲突、结尾留悬念
5. 保持人物性格、剧情逻辑的一致性
6. 支持自定义章节长度（默认4000-5000字/章）
7. 支持续写、修改、调整已有章节内容

### 独立调用自举
如果用户直接调用 `sumeru-write`，不要假设 worldbuilder 已运行。先执行 AGENTS.md 的“断点恢复与独立调用自举”：
- 定位项目根目录，读取或生成 `.sumeru/project.json`、`.sumeru/status.json`。
- 若缺少 `outlines/chapters.json`，尝试读取 `.sumeru/outline/chapter-outlines.json`；仍缺失时根据用户本次描述生成当前章节的临时任务卡。
- 若缺少 `.sumeru/cache/`，生成最小 `project-brief.md`、`style-brief.md`、`creative-brief.md`、`continuity-brief.md`。
- 若缺少当前范围的 `write-<range>.md` context pack，先生成临时 context pack 再写作。
- 根据 `chapters/` 已有文件推断续写位置，默认不覆盖已有章节。
- 写作完成后更新 `.sumeru/status.json`、continuity cache 和 `.sumeru/changelog.md`。

### 按模式写作
- `short/light`：优先写入或续写 `story.md`；如用户指定章节，可写入 `chapters/`。不强制生成 context pack，除非内容很长或用户要求分章处理。
- `medium/standard`：按 `outlines/chapters.md` 或简化任务卡写入 `chapters/`；批量超过 3 章时可生成临时 context pack。
- `long/full`：必须使用拆分任务卡、cache 和 context pack；批量写作每个子Agent 1-3 章。

### 输入优先级
1. 用户本次明确要求（章节号、字数、风格、视角、必须出现/禁止出现的情节）优先级最高。
2. `.sumeru/context-packs/write-<range>.md` 是批量写作的首选输入。
3. `.sumeru/cache/project-brief.md`、`style-brief.md`、`creative-brief.md`、`continuity-brief.md` 是首选摘要输入。
4. `.sumeru/review/fix-plan.json` 中标记的重写要求优先于原细纲，用于返工章节。
5. `outlines/chapters/<id>.json` 或 `outlines/chapters.json` 中的目标章节任务卡是剧情依据；长篇项目不要全文读取全本任务卡。
6. `docs/creative-strategy.md`、`ideas/active.md` 和相关 ideas 条目用于保持创意策略；不要读取 `ideas/discarded.md` 或 archive。
7. `docs/style-guide.md`、`docs/glossary.md`、`docs/characters.md`、`docs/world.md` 仅在摘要不足时读取。
8. `.sumeru/project.json` 提供目标平台、章节字数范围和整体风格。
9. 已存在的 `chapters/` 内容用于续写和风格衔接；不要覆盖用户已写章节，除非用户明确要求重写。

### 低 Token 写作规则
- 如果存在 context pack，只读取 context pack、目标章节正文、必要的前一章结尾，不再读取全量 docs/outlines/ideas。
- `short/light` 不强制 context pack，优先读取 `outline.md`、`story.md` 和 `story-brief.md`。
- `medium/standard` 只在批量或上下文复杂时生成 context pack。
- 单章写作读取目标章节任务卡；三章批量读取三章任务卡和相邻章节摘要。
- 需要人物设定时优先读取 `character-brief.md`，不足时只读取相关人物文件或片段。
- 需要世界观时优先读取 `world-brief.md`，不足时只读取相关地点/组织/规则片段。
- 写完后只刷新相关 continuity 摘要，不全量重写缓存。

### 章节任务卡执行规则
- 每章先读取对应 `chapterId` 或 `chapterNumber` 的任务卡。
- 正文必须完成任务卡中的 `purpose`。
- 正文必须落实任务卡中的 `creativeGoal`、`freshnessHook`、`emotionalBeat`、`readerMemoryPoint`；如果任务卡缺少这些字段，写作前先为本章补充简短创意方案。
- 遇到 `tropeToAvoid` 时必须避开直给套路，选择替代写法。
- 若存在 `surpriseTwist`，必须提前埋下公平线索，不能硬转折。
- 正文必须覆盖 `events` 中的关键事件，但可以调整呈现顺序以提升阅读体验。
- 正文必须落实 `outputs` 中的人物状态、道具状态、伏笔和下一章钩子。
- 正文必须满足全部 `acceptanceCriteria`；如无法满足，生成章节前先说明阻塞原因并写入 `.sumeru/backlog.md`。
- 章节生成后更新 `.sumeru/status.json` 中对应章节状态为 `drafted`。
- 章节生成后更新 `.sumeru/continuity/character-state.json`、`item-state.json`、`foreshadowing.json`、`timeline.json` 中与本章相关的变化。
- 章节生成后把实际完成的名场面、反转、情绪节拍追加到 `ideas/scene-fragments.md` 或 `ideas/emotional-beats.md`，供后续复用和避重。

### 创意落地检查
生成章节前先做 5 项自检：
1. 本章是否有读者能记住的一幕、一个选择或一句话。
2. 本章爽点是否和前 3 章重复；如重复，切换情绪类型或解决方式。
3. 主角是否通过选择推动局势，而不是被剧情推着走。
4. 反派或阻力是否足够聪明，是否让胜利付出代价。
5. 结尾钩子是否既承接本章输出，又诱导下一章点击。

### 续写规则

#### 续写模式
支持续写、重写、扩写、精简等多种模式

#### 续写注意事项
1. 保持人物性格一致性，不OOC（Out Of Character）
2. 保持前文设定的战力体系、世界观不崩坏
3. 伏笔回收要自然，不突兀
4. 语言风格与前文保持统一
5. 承接上文剧情，开启下文伏笔
6. 如已有章节内容不完整，优先补完

#### 多章生成
支持连续生成多章内容，自动按章节顺序生成

### 细纲驱动批量生成

#### 自动读取细纲模式
当 `.sumeru/outline/chapter-outlines.json` 存在时，自动启用细纲驱动模式：

```bash
# 生成所有章节（读取细纲，自动并行）
/sumeru-write 全部章节

# 生成指定范围章节
/sumeru-write 第1-50章

# 生成特定卷的所有章节
/sumeru-write 第1卷

# 生成特定章节
/sumeru-write 第3章,第5章,第10章

# 批量并行创作指定范围
/sumeru-write 第1-100章 批量并行
```

#### 细纲输入格式支持

支持直接传入单章细纲：

```bash
# 使用自然语言描述生成单章
/sumeru-write 第3章 "主角在拍卖会上获得神秘功法"

# 基于已有细纲生成
/sumeru-write 第3章 按细纲生成
```

#### 细纲数据结构验证

生成前自动验证细纲完整性：
- 检查必填字段是否存在
- 验证人物名称是否在characters.json中定义
- 检查场景地点是否在world.json中定义
- 提供缺失信息的补充建议
- 检查每章是否包含 `purpose`、`outputs`、`acceptanceCriteria`
- 检查每章是否包含 `creativeGoal`、`emotionalBeat`、`readerMemoryPoint`，缺失时自动补齐写作假设

#### 子agent并行批量写作（大量章节推荐）
当需要一次性生成大量章节（>3章）或使用细纲驱动模式时，自动启用子agent模式：

**⚠️ 遵循全局约束：每个子Agent最多负责3个章节**（详见 AGENTS.md "子Agent并行处理规则"）
- 所需Agent数 = ceil(总章节数 / 3)，调度器自动计算
- 相邻章节分配给同一Agent，保持上下文连贯性

**核心优势**
- ✅ **细纲隔离**：每个子agent只获取自己负责章节的细纲，避免上下文溢出
- ✅ **3章上限保障**：每个Agent最多3章，确保生成质量和一致性
- ✅ 上下文隔离：每个子agent不携带历史章节内容，彻底解决长上下文压缩/溢出问题
- ✅ 速度提升：多并行写作，速度是串行的N倍
- ✅ 错误隔离：单章生成失败不影响其他章节，自动重试失败章节
- ✅ 内存优化：子agent完成后自动销毁，释放内存资源
- ✅ 增量写入：每写完一章立即保存到`.sumeru/write/draft/`，无需等待全部完成
- ✅ **进度可视化**：实时显示已完成/进行中/待写章节状态

**调度逻辑（细纲驱动）**
```mermaid
flowchart LR
    A[批量写作任务] --> B[读取chapter-outlines.json]
    B --> C[验证细纲完整性]
    C --> D[创建任务队列，按每Agent最多3章分配]
    D --> E[计算所需Agent数 = ceil/总章数/3/]
    E --> F[启动N个并行子agent]
    F --> G[子Agent拉取任务 → 获取对应章节细纲 → 生成章节 → 保存文件]
    G --> H{队列是否为空?}
    H -->|否| G
    H -->|是| I[汇总进度，生成完成报告]
```

**章节分配规则**
- 按章节顺序连续分配，如Agent1负责第1-3章，Agent2负责第4-6章，以此类推
- 尾部不足3章的Agent按实际剩余章节数分配
- 相邻章节分配给同一Agent，以保持上下文连贯性

**子agent输入上下文**
- 完整章节内容，符合指定风格与节奏
- 下一章内容预告/思路建议
- 本章剧情关键点梳理
- 本章埋设的伏笔提示（可选）
- 人物成长/变化摘要（可选）

### 章节文件命名规范

**强制格式：`{三位章节号}-{章节标题}.md`**

| 规则 | 说明 | 示例 |
|------|------|------|
| 章节号 | 三位数字零填充 | `001`、`003`、`042`、`128` |
| 分隔符 | 英文短横线 `-` | `-` |
| 标题 | 章节标题原文，不含特殊字符 | `第一次解析`、`废物觉醒系统` |
| 扩展名 | `.md` | `.md` |

**命名示例：**
```
003-第一次解析.md
001-废物觉醒系统.md
042-时间线冲突.md
128-终极决战.md
```

**❌ 错误命名：**
```
第3章-第一次解析.md    # 不要加"第X章"前缀
3-第一次解析.md         # 章节号必须三位零填充
003_第一次解析.md       # 分隔符是短横线，不是下划线
003-第一次解析.txt      # 扩展名必须是.md
003第一次解析.md        # 必须有短横线分隔符
```

### 数据持久化
#### 正式输出（用户可见）
- 生成的章节默认保存到当前工作目录的 `chapters/` 下，严格遵循上述命名规范
- 章节文件为纯净的正文内容，不含任何中间标记和元数据，用户可直接阅读、编辑
- 支持自定义章节输出目录
- **批量生成进度报告**：`chapters/WRITE_PROGRESS.md`（实时更新）

#### 中间过程数据（仅系统内部使用）
所有中间状态、元数据、进度信息统一保存到 `.sumeru/write/` 目录：
- `progress.json`：创作进度跟踪，包含已完成章节、字数统计、各章节状态
- `chapter-meta.json`：每章元数据，包含核心事件、出场人物、爽点位置、伏笔记录
- `character-state.json`：人物状态动态跟踪，记录各时间点人物能力、关系、状态变化
- `used-outlines.json`：已使用的章节细纲记录，支持增量生成
- `original/`：原始章节文件备份目录。当 review 或 polish 修改 `chapters/` 文件时，原始章节文件会先自动备份到 `.sumeru/write/original/` 目录，确保可回滚

#### 与其他 Skill 配合
- **前置 Skill**：自动读取 `.sumeru/outline/` 目录的大纲数据
  - 使用 `characters.json` 保持人物性格一致性
  - 使用 `chapter-outlines.json` 中的**完整章节细纲**驱动批量生成
  - 使用 `world.json` 保持世界观设定一致性
- **后续 Skill**：生成的章节数据可供 `sumeru-review`、`sumeru-polish`、`sumeru-finalize` 使用

#### 断点恢复
- 每次任务启动时读取 `chapters/` 目录下已存在的章节文件和 `.sumeru/write/progress.json` 进度
- 读取 `.sumeru/outline/chapter-outlines.json` 获取完整细纲
- 从最新未完成章节继续，自动跳过已生成的章节
- 支持从指定章节恢复创作
- 支持只生成缺失的章节（增量模式）
