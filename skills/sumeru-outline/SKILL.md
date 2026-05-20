---
name: sumeru-outline
description: 小说大纲、世界观、人设设计与创意架构。用户要写小说大纲、设计主角/配角/反派、做世界观设定、搭剧情框架、分卷大纲、章节细纲、人物卡、爽点排布、反套路设计、惊喜反转、情绪曲线或梳理小说剧情时必须使用本技能。
type: skill
---

## 网文大纲设计

### 触发关键词
帮我写个小说大纲、设计主角人设、做世界观设定、搭小说剧情框架、写分卷细纲、给我设计小说人物、做个玄幻世界观、帮我梳理小说剧情、小说人物设定、写小说分章大纲、爽点排布规划、做小说人设卡、构建小说世界、小说大纲生成、写完整章节细纲、生成全本细纲、所有章节细纲

### 核心功能
1. 世界观设定：世界背景、力量体系、社会规则、地理设定
2. 人物设定：主角、配角、反派的人物画像、性格、成长线
3. 剧情框架：主线故事、支线剧情、关键节点、高潮安排
4. 分卷大纲：按卷划分剧情阶段，明确每卷核心冲突与目标
5. 爽点排布：规划关键爽点、转折点、悬念点的位置
6. 强制合规检查：基于AI推理检测所有名称，识别可能的真实人名/地名，避免侵权风险

### 独立调用自举
如果用户直接调用 `sumeru-outline`，先执行 AGENTS.md 的"断点恢复与独立调用自举"：
- 定位项目根目录，读取或生成 `.sumeru/project.json`、`.sumeru/status.json`。
- 若已有 `docs/requirements.md` 或 `.sumeru/topic/options.json`，复用既有选题和需求。
- 若缺少 `ideas/` 或 `docs/creative-strategy.md`，先生成最小创意策略和创意库存。
- 大纲完成后生成或刷新 `outlines/chapters.json`；长篇项目同步拆分为 `outlines/chapters.index.json` 与 `outlines/chapters/*.json`。
- 更新 `.sumeru/status.json`、`.sumeru/cache/project-brief.md`、`world-brief.md`、`character-brief.md`、`creative-brief.md`。

### 按模式输出
- `short/light`：输出 `outline.md`，包含高概念、人物、三幕/五段式结构、核心反转、情绪曲线、结尾余味；不强制生成章节 JSON。
- `medium/standard`：输出 `docs/outline.md`、`docs/characters.md`、`docs/creative-strategy.md`、`outlines/chapters.md`；章节简纲可用 Markdown 表格承载。
- `long/full`：输出完整 `docs/architecture.md`、`docs/world.md`、`docs/characters.md`、`docs/plot.md`、`docs/creative-strategy.md`、`outlines/chapters.json`，必要时拆分 `outlines/chapters.index.json` 与 `outlines/chapters/*.json`。

### 输入优先级
1. 用户明确给出的题材、篇幅、风格、禁忌内容和目标平台优先级最高。
2. `.sumeru/project.json` 和 `docs/requirements.md` 中已有的稳定配置优先复用，不重复询问。
3. 若存在 `.sumeru/topic/options.json` 且用户要求复用选题，优先继承推荐选题的核心概念、金手指、卖点和受众定位。
4. 若用户提供参考作品，只抽象学习节奏、类型结构和情绪价值，不复用具体角色、设定、组织、地名、桥段和专有名词。
5. 对缺失信息采用合理默认值，但必须在 `docs/requirements.md` 的"待确认问题"和大纲的"大纲假设"部分列出。

### 项目化输出要求
- `docs/requirements.md`：创作需求、目标平台、受众、篇幅、禁忌内容、参考风格和待确认问题。
- `docs/architecture.md`：故事架构，包含主线目标、终局冲突、成长系统、冲突系统、爽点密度、信息揭示节奏。
- `docs/world.md`：世界观、力量体系、社会结构、地理与组织。
- `docs/characters.md`：人物设定卡、人物关系、成长弧线和语言风格。
- `docs/plot.md`：主线、支线、分卷规划、关键高潮、伏笔规划。
- `docs/creative-strategy.md`：高概念、类型混血、反套路策略、惊喜反转、情绪差异化、读者记忆点。
- `docs/style-guide.md`：若不存在则创建，包含叙述视角、句式、对话、爽点写法、禁用表达和平台偏好。
- `docs/glossary.md`：若不存在则创建，记录术语、人物、地点、组织、功法、道具和禁止变体。
- `outlines/chapters.json`：章节任务卡主文件。每章必须包含 `purpose`、`events`、`outputs`、`acceptanceCriteria`。
- `.sumeru/outline/chapter-outlines.json`：兼容旧流程的副本。

### 创意架构要求
- **高概念锁定**：从 `ideas/concept-pitches.md` 或本次生成的 pitch 中选择主 pitch，写入 `docs/creative-strategy.md`。
- **类型混血控制**：说明主类型承诺和嫁接类型的边界。
- **反套路策略**：列出本书最容易俗套的 5 个桥段，并给出替代写法。
- **卷级惊喜**：每卷至少设计 1-3 个"意外但合理"的反转。
- **情绪曲线**：规划每卷主导情绪和相邻章节情绪差异。
- **角色主动性压力测试**：主角、反派、重要配角都必须有独立欲望、私心和会改变局势的主动选择。
- **读者记忆点**：每卷至少设计 2 个可截图传播的名场面、台词或局势反转。

### 章节细纲要素（必填）
每章细纲包含：章节编号、标题、建议字数、核心事件、出场人物、剧情推进、本章爽点/悬念、伏笔埋设、与前后章关联、场景地点、POV视角、情绪基调、章节目的、创意目标、规避套路、情绪节拍、读者记忆点、惊喜反转、输入/输出状态、验收标准。

### 子Agent并行细纲生成
当章节数大于3章且项目模式为 `medium/standard` 或 `long/full` 时，支持子Agent并行生成细纲。每个子Agent最多负责3章，按卷分配优先。

### 合规约束规则
1. **人名约束**：禁止使用真实人名（历史人物、公众人物、知名IP角色名），鼓励原创虚构姓名。
2. **地名约束**：禁止使用真实地名（国家名、城市名、山脉名等），架空历史类需做足够虚构化改编。
3. **自动检查**：大纲生成时基于AI推理识别可能的真实人名/地名，发现疑似时自动提示并提供3个以上虚构替换方案。

### 数据持久化
**用户可见输出**：
- `小说大纲_世界观设定.md`：完整世界观设定
- `小说大纲_剧情框架.md`：主线+支线剧情大纲+分卷规划
- `小说大纲_章节细纲.md`：完整的章节细纲

**中间数据（`.sumeru/outline/`）**：
- `world.json`：世界观设定
- `characters.json`：结构化人物设定卡
- `plot-outline.json`：剧情大纲数据
- `chapter-outlines.json`：完整章节细纲数据

### 与其他 Skill 配合
- **前置**：可读取 `sumeru-topic` 的 `options.json`（通过"复用已有选题数据"）
- **后续**：生成的数据可供 `sumeru-write`、`sumeru-review` 使用

### 全局约束引用
- 子Agent并行处理规则：见 AGENTS.md "子Agent并行处理规则"
- 职责边界：见 AGENTS.md "子Agent职责边界规则"
- 状态标记格式：见 AGENTS.md "子Agent输出状态标记"
- Context Pack 格式：见 AGENTS.md "Context Pack 格式"
- 独立调用自举：见 AGENTS.md "断点恢复与独立调用自举"
- 项目配置 Schema：见 AGENTS.md "项目配置 Schema"
