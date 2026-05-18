---
name: sumeru-polish
description: 小说内容润色优化与创意强化。用户要润色小说、改文笔、优化章节节奏、强化爽点、强化名场面、让对话自然、提升代入感、调整风格、把一章写得更爽或更细腻时必须使用本技能。它优先读取 .sumeru/context-packs/polish-*.md、.sumeru/cache/style-brief.md、creative-brief.md、issue-brief.md、目标章节正文和相关任务卡，必要时才读取 docs/creative-strategy.md、docs/style-guide.md、docs/glossary.md、outlines/chapters.json、ideas/ 和 review issues；润色前备份，结果直接修改 chapters/。批量润色时每个子Agent最多负责3章。
type: skill
---

## 网文内容润色

### 触发关键词
帮我润色这段小说、改下文笔、优化章节节奏、强化这个爽点、让对话更自然、把这段写得更爽、优化小说文笔、调整章节节奏、让对话更真实、帮我改下这段内容、润色小说、优化爽点、提升文笔、让这段更有代入感、小说内容优化、文笔润色

### 核心功能

### 独立调用自举
如果用户直接调用 `sumeru-polish`，不要假设 worldbuilder 已运行。先执行 AGENTS.md 的“断点恢复与独立调用自举”：
- 定位项目根目录，读取或生成 `.sumeru/project.json`、`.sumeru/status.json`。
- 根据用户指定范围或 `chapters/` 推断要润色的章节。
- 若缺少 review 输出，不阻塞润色；只基于正文、style cache 和用户要求润色，并在 `.sumeru/backlog.md` 记录“未经过 review”。
- 若缺少 `docs/style-guide.md` 或 `.sumeru/cache/style-brief.md`，根据项目配置和现有章节生成临时风格摘要。
- 若缺少当前范围的 `polish-<range>.md` context pack，先生成临时 context pack 再润色。
- 润色完成后备份原文，更新 `.sumeru/status.json`、`.sumeru/polish/summary.json`、`.sumeru/cache/continuity-brief.md`。

### 按模式润色
- `short/light`：优先润色 `story.md` 全文或用户指定片段，输出可直接发布的短篇稿；不强制章节化。
- `medium/standard`：按章节或小范围润色，保留 `.sumeru/issues.md` 中的问题处理记录。
- `long/full`：按 context pack 分片润色，每个子Agent 1-3 章，生成 diff/summary 和状态更新。

### 低 Token 润色规则
- 如果存在 `.sumeru/context-packs/polish-<range>.md`，优先只读取 context pack 和目标章节正文。
- `short/light` 不强制 context pack，优先读取 `story.md`、`outline.md` 和 `story-brief.md`。
- `medium/standard` 只在批量或跨章节一致性复杂时生成 context pack。
- 风格依据优先读取 `.sumeru/cache/style-brief.md`，创意依据优先读取 `.sumeru/cache/creative-brief.md`。
- 审查问题优先读取 `.sumeru/cache/issue-brief.md` 和相关 issue，不全文读取所有 tests。
- 批量润色每个子Agent 1-3 章；不要让单个子Agent读取全本章节。
- 润色后只更新对应章节状态、diff/summary 和相关缓存摘要。

#### 润色边界
- 保留既有主线事实、人物关系、战力体系、伏笔状态和章节结尾钩子，除非用户明确要求重写剧情。
- 保留 `outlines/chapters.json` 中每章 `acceptanceCriteria` 已满足的内容，不为了文笔牺牲验收标准。
- 强化但不篡改 `creativeGoal`、`emotionalBeat`、`readerMemoryPoint` 和 `freshnessHook`。
- 术语、人物名、地名、组织名、功法名必须遵守 `docs/glossary.md`，不得产生新变体。
- 文风、句式、禁用表达、平台偏好必须遵守 `docs/style-guide.md`。
- 轻度润色以表达优化为主，不改变段落顺序和剧情信息。
- 中度润色可以调整段落组织、补充细节和强化情绪递进，但不新增会影响后文的重大设定。
- 深度润色可以重构场景呈现方式，但必须保持章节核心事件、人物动机和结尾指向一致。
- 发现剧情逻辑硬伤时不要在润色中擅自改主线，应记录到 `.sumeru/polish/logic-notes.json`，建议转交 `sumeru-review` 或 `sumeru-write`。

#### 润色等级
1. **轻度润色**：优化句式表达，去除冗余表述，精炼用词，提升文字流畅度，保留80%以上原文风格和表达方式
2. **中度润色**：重构段落结构，优化叙事视角，全面提升文笔质感，保留60%原文核心表达
3. **深度润色**：逐字打磨，雕琢细节，追求最佳阅读体验，保留核心情节脉络

#### 风格适配选项
- **小白爽文**：短句为主，节奏明快，情绪直接，用词通俗易懂
- **精品文**：句式多变，文笔细腻，注重氛围营造，人物心理刻画深入
- **古风仙侠**：用词雅致，意境悠远，适当运用古典词汇和修辞手法
- **都市现实**：语言生活化，对话接地气，场景描写真实可感
- **悬疑推理**：语言凝练，节奏紧凑，信息密度适中，悬念感强
- **科幻未来**：科技感词汇准确，逻辑严密，世界观表述清晰

#### 针对性优化
1. **节奏收紧**
   - 删除无效铺垫：去除与主线无关的场景描写、心理活动
   - 压缩过渡情节：将冗长的转场、交代性文字缩短30%-50%
   - 加快信息传递：采用对话、行动展现信息，减少大段叙述
   - 调整段落长度：将超长段落拆分为2-3行的短段落，提升阅读速度

2. **爽点强化**
   - **前置铺垫**：在爽点前300-500字设置期待感，通过反派挑衅、主角困境、他人质疑等方式铺垫
   - **情绪递进**：爽点爆发分三层：期待→紧张→释放，每一层情绪都要有具体描写
   - **细节放大**：主角行动、他人反应、环境变化三个维度同时描写，增强画面感
   - **收尾有力**：爽点后用100-200字总结效果，或留下新的钩子
   - **经典结构**：[压抑/挑衅]→[蓄力/准备]→[爆发/打脸]→[余波/影响]

3. **对话优化**
   - **人设贴合**：每句对话符合人物年龄、身份、性格，避免千人一面
   - **潜台词**：重要对话包含言外之意，通过语气、动作辅助表达
   - **节奏控制**：长段对话拆分为多轮，穿插动作、表情、心理描写
   - **信息传递**：通过对话自然交代背景、推动情节，避免生硬说明
   - **口语化**：减少书面语，多用真实生活中的表达习惯，但避免语病
   - **对话标签优化**：用具体动作代替"说"、"道"，如"挑眉道"、"冷哼一声"

4. **文笔优化**
   - **精准用词**：替换重复词汇、模糊表达，选用更准确的动词、形容词
   - **句式变化**：长短句结合，避免清一色的主谓宾结构
   - **感官描写**：调动视觉、听觉、嗅觉、触觉、味觉，增强代入感
   - **比喻具象**：用读者熟悉的事物作比，避免抽象、生僻的比喻
   - **去除冗余**：删除"非常"、"十分"、"很"等副词，用动词和名词表达程度

### 输出内容
- 润色后的完整章节内容（直接替换 `chapters/` 中的原文件）
- 润色修改说明：调整的地方与原因（按优化类型分类说明）
- 优化建议：后续内容写作提升方向，具体可操作的技巧

### 子Agent并行润色机制

当需要润色的章节数量大于3章时，自动启用子Agent并行润色模式。

**⚠️ 遵循全局约束：每个子Agent最多负责3个章节**（详见 AGENTS.md "子Agent并行处理规则"）
- 所需Agent数 = ceil(总章节数 / 3)
- 相邻章节分配给同一Agent，保持风格连贯性

**⚠️ 职责边界**
| 任务 | 父Agent（调度器） | 子Agent（执行器） |
|------|------------------|-------------------|
| 自举 & 环境准备 | ✅ 定位项目、读/生成 project.json、status.json | ❌ |
| Context pack 生成 | ✅ 集中生成，含正文+style-brief+issue-brief | ❌ |
| Cache 摘要读取 | ✅ 集中读取 style-brief、creative-brief、issue-brief | ❌ |
| 启动子Agent | ✅ 计算所需Agent数，分配章节 | ❌ |
| **章节润色** | ❌ | **✅ 唯一任务** |
| 写入 chapters/ | ✅ 汇总后统一写（修改前备份） | ❌ |
| 备份到 original/ | ✅ 写前备份 | ❌ |
| 生成 diff/summary | ✅ 汇总后统一生成 | ❌ |
| 更新 status.json | ✅ 汇总后统一更新 → polished | ❌ |
| 刷新 continuity cache | ✅ 汇总后统一刷新 | ❌ |

**调度逻辑**
```mermaid
flowchart LR
    A[批量润色任务] --> B[父Agent: 自举 & 读取章节列表]
    B --> C[父Agent: 读取 style-brief & issue-brief]
    D[父Agent: 计算Agent数 = min(ceil/总章/3/, 5)]
    C --> D
    D --> E[父Agent: 生成 context pack + 批次摘要 + 具象标杆]
    E --> F[父Agent: 启动N个并行子agent N≤5]
    F --> G[子Agent: 读取 context pack → 润色章节 → 输出润色后文本+diff说明+状态标记]
    G --> H{所有子Agent完成?}
    H -->|否| F
    H -->|是| I[父Agent: 提取状态标记 & 汇总润色结果]
    I --> J[父Agent: 备份原文 & 写入 chapters/]
    J --> K[父Agent: 生成 diff/summary & 更新 status → polished]
    K --> L[父Agent: 刷新 continuity cache]
    L --> M{还有剩余章节?}
    M -->|是| D
    M -->|否| N[完成]
```

**子Agent输入上下文（context pack）**：
- 润色等级与风格参数
- 负责章节的原始内容
- 风格摘要（仅本组章节相关的 style-brief 内容）
- 创意摘要（仅本组章节相关的 creative-brief 内容）
- 审查问题摘要（仅本组章节相关的 issue-brief 内容，作为重点优化方向）
- 对应章节任务卡的 `acceptanceCriteria`、`emotionalBeat`、`readerMemoryPoint`
- **Batch Summary（非第一批必填）**：前N批实际摘要（≤500字）
- **【可用缓存的键】**（子Agent可在输出中标记需要以下缓存内容，父Agent下一轮补充）：
  - `char:主角`（人物当前状态摘要，约200字）
  - `char:配角`（人物当前状态摘要，约200字）
  - `prev:actual`（上一章实际结尾，约200字）
- **【风格标杆】**（父Agent从已完成章节中自动提取3段标杆段落塞入）：
  - 场景描写标杆（摘自已完成章节）：原文 → 润色后
  - 对话场景标杆（摘自已完成章节）：原文 → 润色后
  - 情绪高潮标杆（摘自已完成章节）：原文 → 润色后

**子Agent输出**：
- 润色后的完整章节内容（纯文本）
- 润色修改说明：调整的地方与原因（按优化类型分类）
- 优化建议：后续内容写作提升方向
- **状态标记**：`<!-- SUMERU_STATUS: chapter=037, status=polished, ... -->`
- **不写入任何文件、不更新任何状态**

**章节分配规则**
- 按章节顺序连续分配（如Agent1负责第1-3章，Agent2负责第4-6章）
- 尾部不足3章的Agent按实际剩余章节数分配

**润色边界**
- 保留既有主线事实、人物关系、战力体系、伏笔状态和章节结尾钩子，除非用户明确要求重写剧情。
- 保留 `outlines/chapters.json` 中每章 `acceptanceCriteria` 已满足的内容，不为了文笔牺牲验收标准。
- 强化但不篡改 `creativeGoal`、`emotionalBeat`、`readerMemoryPoint` 和 `freshnessHook`。
- 术语、人物名、地名、组织名、功法名必须遵守 `docs/glossary.md`，不得产生新变体。
- 文风、句式、禁用表达、平台偏好必须遵守 `docs/style-guide.md`。
- 轻度润色以表达优化为主，不改变段落顺序和剧情信息。
- 中度润色可以调整段落组织、补充细节和强化情绪递进，但不新增会影响后文的重大设定。
- 深度润色可以重构场景呈现方式，但必须保持章节核心事件、人物动机和结尾指向一致。
- 发现剧情逻辑硬伤时不要在润色中擅自改主线，应记录到 `.sumeru/polish/logic-notes.json`，建议转交 `sumeru-review` 或 `sumeru-write`。

### 数据持久化
润色过程数据自动保存到 `.sumeru/polish/` 目录：
- `diff/`：修改对比文件，记录每处修改的位置、原文、修改后内容、修改原因
- `summary.json`：润色统计报告，包含修改数量、优化类型分布、字数变化
- `style-config.json`：本次润色使用的风格、等级、重点参数配置

#### 与其他 Skill 配合
- **前置 Skill**：读取 `sumeru-write` 和 `sumeru-review` 的输出
  - 从 `chapters/` 读取原始章节内容
  - 从 `.sumeru/issues/index.json`、`.sumeru/review/fix-plan.json` 和 `tests/*.md` 读取审查问题作为优化重点
- **后续 Skill**：润色后的内容供 `sumeru-finalize` 使用
  - 润色结果直接保存在 `chapters/` 目录，无需额外应用步骤
  - worldbuilder 编排 polish 时，润色结果自动生效

#### 数据复用
- 支持多轮润色，可基于上一轮润色结果继续优化
- 可导出diff文件用于人工审核修改内容
- 风格配置可复用，保持全本润色风格统一
