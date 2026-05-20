---
name: sumeru-polish
description: 小说内容润色优化与创意强化。用户要润色小说、改文笔、优化章节节奏、强化爽点、强化名场面、让对话自然、提升代入感、调整风格、把一章写得更爽或更细腻时必须使用本技能。
type: skill
---

## 网文内容润色

### 触发关键词
帮我润色这段小说、改下文笔、优化章节节奏、强化这个爽点、让对话更自然、把这段写得更爽、优化小说文笔、调整章节节奏、让对话更真实、帮我改下这段内容、润色小说、优化爽点、提升文笔、让这段更有代入感、小说内容优化、文笔润色

### 核心功能
1. **文笔优化**：精准用词、句式变化、感官描写、比喻具象、去除冗余
2. **节奏调整**：节奏收紧、压缩过渡情节、加快信息传递
3. **爽点强化**：前置铺垫、情绪递进、细节放大、收尾有力
4. **对话优化**：人设贴合、潜台词、节奏控制、口语化
5. **创意强化**：强化记忆点与情绪释放

### 独立调用自举
如果用户直接调用 `sumeru-polish`，先执行 AGENTS.md 的"断点恢复与独立调用自举"：
- 定位项目根目录，读取或生成 `.sumeru/project.json`、`.sumeru/status.json`。
- 根据用户指定范围或 `chapters/` 推断要润色的章节。
- 若缺少 review 输出，不阻塞润色；只基于正文、style cache 和用户要求润色，并在 `.sumeru/backlog.md` 记录"未经过 review"。
- 若缺少 `docs/style-guide.md` 或 `.sumeru/cache/style-brief.md`，根据项目配置和现有章节生成临时风格摘要。
- 若缺少当前范围的 `polish-<range>.md` context pack，先生成临时 context pack 再润色。

### 按模式润色
- `short/light`：优先润色 `story.md` 全文或用户指定片段，输出可直接发布的短篇稿。
- `medium/standard`：按章节或小范围润色，保留 `.sumeru/issues.md` 中的问题处理记录。
- `long/full`：按 context pack 分片润色，每个子Agent 1-3 章，生成 diff/summary 和状态更新。

### 低 Token 润色规则
- 如果存在 `.sumeru/context-packs/polish-<range>.md`，优先只读取 context pack 和目标章节正文。
- `short/light` 不强制 context pack，优先读取 `story.md`、`outline.md` 和 `story-brief.md`。
- `medium/standard` 只在批量或跨章节一致性复杂时生成 context pack。
- 风格依据优先读取 `.sumeru/cache/style-brief.md`，创意依据优先读取 `.sumeru/cache/creative-brief.md`。
- 审查问题优先读取 `.sumeru/cache/issue-brief.md` 和相关 issue。

### 润色边界
- 保留既有主线事实、人物关系、战力体系、伏笔状态和章节结尾钩子，除非用户明确要求重写剧情。
- 保留 `outlines/chapters.json` 中每章 `acceptanceCriteria` 已满足的内容。
- 强化但不篡改 `creativeGoal`、`emotionalBeat`、`readerMemoryPoint` 和 `freshnessHook`。
- 术语、人物名、地名、组织名、功法名必须遵守 `docs/glossary.md`，不得产生新变体。
- 文风、句式、禁用表达、平台偏好必须遵守 `docs/style-guide.md`。
- 发现剧情逻辑硬伤时记录到 `.sumeru/polish/logic-notes.json`，建议转交 `sumeru-review` 或 `sumeru-write`。

### 润色等级
| 等级 | 说明 | 保留比例 |
|------|------|----------|
| 轻度 | 优化句式表达，去除冗余表述，精炼用词，提升文字流畅度 | 80%以上原文 |
| 中度 | 重构段落结构，优化叙事视角，全面提升文笔质感 | 60%原文核心表达 |
| 深度 | 逐字打磨，雕琢细节，追求最佳阅读体验 | 保留核心情节脉络 |

### 风格适配选项
- **小白爽文**：短句为主，节奏明快，情绪直接，用词通俗易懂
- **精品文**：句式多变，文笔细腻，注重氛围营造，人物心理刻画深入
- **古风仙侠**：用词雅致，意境悠远，适当运用古典词汇和修辞手法
- **都市现实**：语言生活化，对话接地气，场景描写真实可感
- **悬疑推理**：语言凝练，节奏紧凑，信息密度适中，悬念感强
- **科幻未来**：科技感词汇准确，逻辑严密，世界观表述清晰

### 针对性优化
1. **节奏收紧**：删除无效铺垫、压缩过渡情节、加快信息传递、调整段落长度
2. **爽点强化**：前置铺垫、情绪递进、细节放大、收尾有力
3. **对话优化**：人设贴合、潜台词、节奏控制、口语化、对话标签优化
4. **文笔优化**：精准用词、句式变化、感官描写、比喻具象、去除冗余

### 子Agent并行润色
当润色章节数大于3章时，自动启用子Agent并行润色。每个子Agent最多负责3章，相邻章节分配给同一Agent。

### 具象标杆机制
父Agent在每个批次开始时，从已完成章节中自动提取3段"标杆段落"（场景描写、对话、情绪高潮），塞入 context pack。子Agent以此为标准润色。

### 数据持久化
**用户可见输出**：
- 润色结果直接替换 `chapters/` 中的原文件

**中间数据（`.sumeru/polish/`）**：
- `diff/`：修改对比文件，记录每处修改的位置、原文、修改后内容、修改原因
- `summary.json`：润色统计报告
- `style-config.json`：本次润色使用的风格、等级、重点参数配置
- `logic-notes.json`：发现的剧情逻辑硬伤记录

### 与其他 Skill 配合
- **前置**：读取 `sumeru-write` 和 `sumeru-review` 的输出
- **后续**：润色后的内容供 `sumeru-finalize` 使用

### 全局约束引用
- 子Agent并行处理规则：见 AGENTS.md "子Agent并行处理规则"
- 职责边界：见 AGENTS.md "子Agent职责边界规则"
- 状态标记格式：见 AGENTS.md "子Agent输出状态标记"
- Context Pack 格式：见 AGENTS.md "Context Pack 格式"
- 独立调用自举：见 AGENTS.md "断点恢复与独立调用自举"
- 项目配置 Schema：见 AGENTS.md "项目配置 Schema"
- 具象标杆机制：见 AGENTS.md "具象标杆（polish 专属）"
