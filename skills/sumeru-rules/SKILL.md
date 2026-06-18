---
name: sumeru-rules
description: 须弥写作全局约束规则（唯一来源）
version: 1.2.4
type: skill
argument-hint: ""
disable-model-invocation: true
user-invocable: false
allowed-tools: Read
context: project
agent: build
---

# 须弥写作全局约束规则

所有须弥写作Skill 必须遵守以下规则。本文档是唯一全局约束源。
---

# 第一部分：系统架构
## 技能清单
| 技能| 职责 | 触发场景 | user-invocable |
|------|------|----------|----------------|
| `sumeru-worldbuilder` | 全流程统筹主管| "从零写小说、帮我写本XX类型小说"、初始化项目 | ✅|
| `sumeru-scan` | 扫榜分析与竞品拆解| "扫榜"、分析热榜"、拆解XX书"、市场调研" | ✅|
| `sumeru-topic` | 选题策划与创意架构| "不知道写什么、找热门题材、做选题分析" | ✅|
| `sumeru-outline` | 大纲设计（世界观/人物/分卷/章节细纲）| "写大纲、设计人物"、世界观设定 | ✅|
| `sumeru-write` | 章节内容创作 | "写第X章、续写"、扩写"、重写"、批量生成" | ✅|
| `sumeru-review` | 逻辑审查与创意疲劳检测| "检查bug"、时间线矛盾、人物OOC" | ✅|
| `sumeru-polish` | 文笔润色与创意强化| "润色"、改文笔、优化节奏"、强化爽点" | ✅|
| `sumeru-finalize` | 完稿校验与发布导出| "检查错别字"、检测敏感词"、导出平台格式" | ✅|
| `sumeru-migrate` | 旧项目迁移与规整 | "规整项目"、迁移旧项目、补齐缺失文件"、查缺补漏" | ✅|
| `sumeru-rules` | 全局约束规则（不直接调用）| —| ❌|

## 调用链路
```
用户需求 → worldbuilder → scan(可选,→trends.md + benchmarks/ + writing-guide.md)
                        → topic(→plan.md, 可读取trends.md)
                        → outline(→outline.md + chapters.json + characters/)
                        → intro.md + creative-anchors.md (worldbuilder 内置)
                        → write(→chapters/*.md, 子Agent并行, 可注入writing-guide.md)
                        → review(→issues.md + fix-plan.json, 子Agent并行审查)
                        → write(修复重写, 读 fix-plan.json)
                        → polish(→chapters/*.md, 子Agent并行润色)
                        → finalize(→publish/)
```

**独立调用**：每个 skill 都可以脱离 worldbuilder 单独启动，执行自举协议。
## 状态机

### 项目状态流转
```
init →scan(可选) →topic →outline →intro →anchor →write →review →fix →polish →finalize →build/release

> 旧项目需先执行 `sumeru-migrate` 完成迁移规整（参见 `sumeru-migrate/SKILL.md`），再进入 `init` 阶段。
```

### 章节状态流转
```
planned →drafted →reviewed →fixed →polished →finalized →exported
                              →                              │(反审未通过时回退)
                              └──────────────────
```

### 推进规则

| 阶段完成条件 | 说明 |
|-------------|------|
| `init` →`scan`(可选) | 用户触发扫榜，生成 `.sumeru/research/` 目录和报告 |
| `scan` →`topic` | 趋势报告已生成（可选，无scan也可直接进入topic） |
| `topic` →`outline` | `plan.md` 已写入，含选题方向和目标平可|
| `outline` →`anchor` | `outline.md`、`chapters.json`、`.sumeru/intro.md` 存在 |
| `anchor` →`write` | `.sumeru/creative-anchors.md` 存在，≥3 个锚点确认|
| `write` →`review` | 目标章节文件存在，状态`drafted`，无缺章 |
| `review` →`fix` | 问题写入 `issues.md`，重写项写入 `fix-plan.json` |
| `fix` →`polish` | 反审验证通过，章节状态`fixed` |
| `polish` →`finalize` | 章节状态`polished` |
| `finalize` →`build` | 技术校验通过，章节状态`finalized` |

### 状态字段语义对照

| 字段 | 所属 | 流转 | 含义 |
|------|------|------|------|
| `currentStage` | `status.json` | 单向推进 | 项目主流程阶段，参见§项目状态流转 |
| `chapterStatus.<n>` | `status.json` | 可回退 | 单章状态，参见§章节状态流转 |
| `migrationHandoff` | `status.json` | **只增不改** | 迁移接续标记（取值：`pending`/`confirmed`/`skipped`）；`sumeru-migrate` v1.3.0+ 写入，`sumeru-worldbuilder` 读取。Schema 详见 `sumeru-migrate/SKILL.md` §11.5；接续读取逻辑详见 `sumeru-worldbuilder/SKILL.md` §项目恢复与迁移接续协议 |

## 文件索引

### `.sumeru/`（中间数据）
| 文件/目录 | 内容 |
|-----------|------|
| `.sumeru/project.json` | 项目配置 |
| `.sumeru/status.json` | 阶段和章节状态|
| `.sumeru/intro.md` | 小说简介 |
| `.sumeru/creative-anchors.md` | 创意锚点 |
| `.sumeru/issues.md` | 问题清单 |
| `.sumeru/changelog.md` | 变更日志 |
| `.sumeru/decisions.md` | 决策记录 |
| `.sumeru/backlog.md` | 待办事项 |
| `.sumeru/cache/` | 各类摘要缓存（含 `cache/vol-N/` 分卷子目录） |
| `.sumeru/context-packs/` | 子Agent上下文包 |
| `.sumeru/continuity/` | 剧情一致性数据（旧版扁平格式）|
| `.sumeru/volumes/` | 分卷隔离数据：每卷独立 continuity/cache/status（150+章时启用）|
| `.sumeru/cross-volume/` | 跨卷依赖表、全局时间线主干、全局人物索引 |
| `.sumeru/research/` | 扫榜分析数据（trends.md、benchmarks/、writing-guide.md） |
| `.sumeru/topic/` | 选题阶段数据 |
| `.sumeru/write/` | 写作阶段数据 |
| `.sumeru/polish/` | 润色阶段数据 |
| `.sumeru/finalize/` | 完稿阶段数据 |

### 旧路径兼容（只读）
| 旧路径 | 新路径 | 说明 |
|--------|--------|------|
| `.sumeru/outline/chapter-outlines.json` | `outlines/chapters.json` | 章节任务单|
| `.sumeru/issues/index.json` | `.sumeru/issues.md` | 问题清单 |
| `docs/*`、`ideas/*` | `plan.md` | 需求设定 |

---

# 第二部分：子Agent并行处理规则

| 规则 | 说明 |
|------|------|
| **适用范围** | 章节写作、章节重写、剧情审查、轻量修复、内容润色、完稿校验、平台导出、章节细纲生成 |
| **核心原则** | 写正文必须走子agent，单章续写也必须走子agent，父agent绝不写正文|
| **并行上限** | 最大5 个子agent同时运行 |
| **分片约束** | 每个子Agent最多负责3 个连续章节|
| **计算公式** | 所需Agent数= `min(ceil(总章节数 / 3), 5)` |
| **分配策略** | 按章节顺序连续分组（1-3。-6。-9...）|
| **上下文约束** | 每个子Agent只接收完成任务所需的精简上下文|

## 批次间串行摘要
每批子Agent完成后，父Agent生成"实际摘要"（≤300字），作为下一批 context pack 的输入。context pack 中只保留最近3 批摘要，更早的合并为一行概述。
**摘要格式**（纯事实列表）：
```
## 批次摘要: 第-6章- 事件：主角觉醒系统001)、通过宗门考核(003)、击败外门弟存005)
- 人物：主角练气三层→五层，苏瑾轻伤恢复，赵无极首次出在- 道具：黑色残片归主角，回春丹消者构- 伏笔：v1黑衣人身从mentioned)，v2残片来历(active)
- 情绪：压抑→突破→暗爆```

**存储位置（< 150 章）**：`.sumeru/continuity/batch-summaries/batch-001.md`、`batch-002.md`...
**存储位置（≥ 150 章，分卷模式）**：`.sumeru/volumes/vol-N/continuity/batch-summaries/batch-001.md`...

> **卷边界重置**：卷切换时执行"软重置"——最后1批摘要 + 卷级总结（~500字）保留到新卷 batch-summaries 第一项，更早的摘要归档到 `vol-N-archived/`。

---

# 第三部分：子Agent职责边界

**核心原则**：子Agent直接写入本组正文章节文件，返回精简状态标记；父Agent负责备份、状态同步、缓存刷新和汇总。

## 父Agent职责

| 职责 | 说明 |
|------|------|
| 自举 & 环境准备 | 定位项目、读/生成 project.json、status.json、补齐目录 |
| Context pack 生成 | 集中生成 context pack，控制 1500-3000 中文字，分发给各子Agent |
| Cache 摘要读取 | 集中读取 L1 cache 摘要 |
| 任务卡读取 | 集中读取目标章节任务卡，仅提取本组章节所需字段 |
| 任务分发 | 启动 N 个子Agent，每个传入精简 context pack |
| 结果汇总 | 收集所有子Agent输出，检查完整性、顺序、命中 |
| 文件写入 & 备份 | 子Agent写入后，父Agent校验文件存在性、SUMERU_STATUS 标记完整性；将原文件备份到 `.sumeru/write/original/`，每章仅保留最新 1 份 |
| 状态更新 | 统一更新 `.sumeru/status.json`（章节状态、阶段状态） |
| 缓存刷新 | 统一刷新相关 cache 摘要 |
| 日志记录 | 统一追加 `.sumeru/changelog.md`、`.sumeru/decisions.md` |
| Issue/测试汇总 | 合并各子Agent发现的问题，写入 `.sumeru/issues.md` |

## 子Agent职责

| 职责 | 说明 |
|------|------|
| 只读 context pack | 不读取 context pack 外的任何文件（已有章节文件除外） |
| 执行核心任务 | 根据 context pack 完成任务单审查/润色要求 |
| 直接写入正文章节文件 | 正文写入 `chapters/*.md`，细纲写入 `outlines/chapters.json`，无需经父Agent透传 |
| 返回状态标记 | 只返回 `<!-- SUMERU_STATUS: ... -->`（不含正文），父Agent据此更新状态 |
| 不碰状态文件 | 不更新 status.json、changelog、cache、issues |

---

# 第四部分：Context Pack 格式与生成规则
**为减少同批次内容重复，context pack 拆为 2 个文件：**

| 文件 | 命名规则 | 大小 | 是否共享 |
|------|----------|------|----------|
| 共享上下文| `shared-{task}.md` | ~1500-2000 存| 同批次所有子Agent共用 |
| 本组任务单| `cards-{范围}.md` | ~300-500 存| 每子Agent独有 |

子Agent先读共享上下文，再读本组任务卡，两者合并作为完数context。
## 一、通用共享上下文格式
```markdown
# Shared Context: {task} (batch {N})

## Project Brief (1-2行
题材、平台、字数范围、整体风格。
## Current Volume (1-2行
本卷目标、当前冲突、卷级反转、阶段情绪。
## Relevant Characters (仅本卷相关
相关人物的当前状态、目标、关系、语言风格。
## Relevant World & Glossary (仅本卷会用到的
地点、组织、功法、道具、禁用变体。
## Continuity State
上一章结尾、关键道具状态、未回收伏笔、时间线位置。
## Creative Strategy
创意目标、要避开的套路、情绪节拍变化、读者记忆点。
## Batch Summary (仅非第一执
前N批实际摘要（≥00字）。
## Output Requirements
文件命名、状态更新需求（由父agent执行）。
## Opening & Style Diversity
- 同一批次各章开场方式必须不同- 同一批次各章结尾钩子句式必须不同
- 同一章内连续超过 5 句完整主谓宾结构 →必须插入破碎可口语短句
```

## 二、通用任务卡格式
```markdown
# Task Cards: {范围}

## Chapter Cards
### 第{N}章「标题。- purpose: ...
- events: ...（≥3个具体事件）
- openingHook: 本章开场方式（可执行的场景描述）- acceptanceCriteria: ...
- creativeGoal: ...
- emotionalBeat: ...

## 本章执行提醒 (≥材
具体可执行的过程提醒、```

## 三、各技能专用部则
各技能上下文格式已在对应 `SKILL.md` 中定义。父Agent生成 context pack 时按目标技能 `SKILL.md` 中的格式要求写入。

## 四、文件位置
所有 context pack 写入 `.sumeru/context-packs/`：
- `shared-{task}.md`：共享上下文
- `cards-{范围}.md`：本组任务卡

## 五、分卷数据源作用域规则（≥ 150 章时强制）

当项目章节数 ≥ 150（volumes/ 目录存在时），context pack 各字段的数据源必须按以下规则限定作用域：

| Context Pack 字段 | 数据源（非分卷模式） | 数据源（分卷模式） |
|---|---|---|
| Project Brief | `plan.md` | 同左（全书级不变） |
| Current Volume | `outline.md` 分卷章节 | `vol-N/outline.md` |
| Relevant Characters | `characters/` 全局 | `vol-N/characters/` + `cross-volume/master-characters.md` |
| Relevant World | `world.md` 全局 | `world.md` 全书规则 + `vol-N/world-addendum.md`（如有） |
| Continuity State | `.sumeru/continuity/` | `vol-N/continuity/state-current.json` |
| Batch Summary | `.sumeru/continuity/batch-summaries/` | `vol-N/continuity/batch-summaries/` |

**跨卷引用**：仅当 `outlines/chapters.json` 目标章节的 `protectedElements` 或伏笔涉及跨卷依赖表中注册的项时，才从 `cross-volume/dependency-table.md` 做一次额外查询。不预加载全量。

---

# 第五部分：子Agent输出状态标记
每个子Agent写入的章节文件首行必须包含状态标记（供重启恢复），同时向父Agent返回同一标记（供实时状态同步）。
## 格式

```markdown
<!-- SUMERU_STATUS: chapter=037, status=drafted, state_diff={"location_change":{"苏瑾":"北域冰原"},"state_change":{"苏瑾":"minor_injury"},"item_change":{"黑色残片":"acquired"}}, char_update={"苏瑾":{"status":"minor_injury","location":"北域冰原"},"主角":{"status":"healthy","buff":"龙血狂暴","remaining":"3大}}, plot_update={"foreshadowing":{"v3":"黑衣人身份暗示推过}}, batch=002, timestamp=2026-05-18T10:30:00Z -->
```

## 字段说明

| 字段 | 含义 | 格式 |
|------|------|------|
| `chapter` | 章节可| 字符为|
| `status` | 章节状态| `drafted` / `polished` / `finalized` |
| `state_diff` | 结构化状态变化| JSON 对象 |
| `char_update` | 人物当前状态| JSON 对象 |
| `plot_update` | 伏笔线推过| JSON 对象 |
| `batch` | 所属批次号 | 字符为|
| `timestamp` | 生成时间 | ISO 8601 |

## state_diff 分类

| 分类锁| 含义 | 示例 |
|--------|------|------|
| `location_change` | 人物位置变化 | `{"苏瑾":"北域冰原"}` |
| `state_change` | 人物健康状态变化| `{"苏瑾":"minor_injury"}` |
| `power_change` | 战力等级变化 | `{"主角":"练气五层"}` |
| `item_change` | 道具状态变化| `{"黑色残片":"acquired"}` |
| `foreshadow_change` | 伏笔状态变化| `{"v3":"mentioned"}` |
| `buff_change` | Buff状态变化| `{"主角":"龙血狂暴|3大}` |

各分类键可选，只包含本章有变化的分类。`state_diff` 必须是合法JSON 单行。
## 关键约束

- 状态标记必须在输出**第一行**
- 标记缺失、JSON 不合法、章节号不匹配时，不得更新状态文从
## 父Agent处理流程

1. 提取每章的`<!-- SUMERU_STATUS -->` 标记
2. 解析 `state_diff` 更新 `.sumeru/continuity/consistency-rules.json`
3. 解析 `char_update` 更新人物状态4. 就`status` 写入 `.sumeru/status.json`
5. 重启后扫提`chapters/*.md` 标记即可重建状态
---

# 第六部分：独立调用自举协议
任何 Skill 单独启动时必须执行：

1. **定位项目**：从当前目录向上查找 `.sumeru/project.json` / `plan.md` / `outline.md` / `chapters/` / `outlines/`
2. **识别版本**：存在`.sumeru/project.json` 按新协议，否则进入兼容模式
3. **最小初始化**：缺配置时根据已有文件生成最小配置
4. **补齐目录**：按需创建 `.sumeru/cache/` / `context-packs/` / `continuity/` / `issues.md`
5. **兼容输入**：旧版`.sumeru/outline/chapter-outlines.json` 只读兼容
6. **刷新缓存**：相关 cache 缺失或过期时生成最小摘要
7. **生成 context pack**：缺 context pack 时生成临时 pack
8. **执行并回写**：更新 `.sumeru/status.json`、cache、issue 文件
9. **记录变更**：追加到 `.sumeru/changelog.md` 和`.sumeru/decisions.md`

## Canonical 路径

| 类型 | 新写入路径 | 旧路径处理|
|------|------------|------------|
| 项目配置 | `.sumeru/project.json`、`.sumeru/status.json` | 无|
| 需求设定/创意 | `plan.md` | `docs/*`、`ideas/*` 只读兼容 |
| 大纲/任务单| `outline.md`、`outlines/chapters.json` | `.sumeru/outline/chapter-outlines.json` 只读兼容 |
| 简介 | `.sumeru/intro.md` | 无|
| 正文 | `chapters/` 或短篇 `story.md` | 无|
| 人物卡 | `characters/` 目录 | 无|
| 世界观 | `world.md` | 无|
| 问题清单 | `.sumeru/issues.md` | `.sumeru/issues/index.json` 只读兼容 |
| 审查摘要 | `reviews/review-report.md` | 按需生成 |
| 测试报告 | `tests/` | 按需生成 |
| 发布产物 | `publish/` | 无|
| 扫榜分析 | `.sumeru/research/`（trends.md、benchmarks/、writing-guide.md） | 无|

## 旧路径兼容策略
**原则**：旧路径只读兼容，新写入一律使用canonical 路径。
| 旧路径 | 兼容方式 | 迁移时机 |
|--------|----------|----------|
| `.sumeru/outline/chapter-outlines.json` | 读取时自动映射到 `outlines/chapters.json` | 下次写入时迁移|
| `.sumeru/issues/index.json` | 读取时自动映射到 `.sumeru/issues.md` | 下次写入时迁移|
| `docs/*`、`ideas/*` | 只读引用，不自动迁移 | 用户手动整理 |
| `docs/glossary.md` | 只读引用，映射到 `plan.md` 术语行| 用户手动整理 |
| `docs/style-guide.md` | 只读引用，映射到 `.sumeru/cache/style-brief.md` | 用户手动整理 |

**迁移规则**）1. 读取旧路径时，先检查canonical 路径是否存在
2. canonical 路径存在 →直接使用 canonical 路径
3. canonical 路径不存在+ 旧路径存在→读取旧路径，写入时使用canonical 路径
4. 两者都不存在→按新协议创建

## 独立调用原则

- 不要求先运行 worldbuilder
- 能从现有文件推断的信息不重复询问
- 缺信息但不阻塞任务时用合理默认值- 不因缓存/context pack 缺失而失责
---

# 第七部分：项目配置Schema

```json
{
  "schemaVersion": 1,
  "title": "未命名作品,
  "genre": "玄幻",
  "targetPlatform": "番茄",
  "audience": "男频",
  "plannedWords": 800000,
  "plannedChapters": 300,
  "chapterWordRange": [2000, 3000],
  "style": "快节奏爽文,
  "tone": "热血",
  "currentStage": "outline",
  "outputLevel": "quiet",
  "volumeCount": 0,
  "currentVolume": "",
  "volumes": {},
  "createdAt": "2026-05-16T00:00:00Z",
  "updatedAt": "2026-05-16T00:00:00Z"
}
```

**volumeCount**：分卷数。0 或缺失 = 扁平模式。≥ 2 时启用分卷隔离。
**currentVolume**：当前活跃卷 ID（如 `"vol-003"`）。扁平模式下为空字符串。
**volumes**：卷详情映射。格式见第十五部分·四。`volumes[vol-N].status` 取值：`planned` / `active` / `completed` / `archived`。

**阶段状态：** `pending` / `in_progress` / `blocked` / `completed` / `skipped`

**章节状态：** `planned` / `drafted` / `reviewed` / `fixed` / `polished` / `finalized` / `exported`

修复后经反审验证通过进入 `fixed`；润色发现逻辑硬伤时触发反审验证。
## consistency-rules.json 格式

由父Agent从每章的 SUMERU_STATUS 解析合并生成，位人`.sumeru/continuity/consistency-rules.json`）
```json
{
  "characters": {
    "苏瑾": { "status": "minor_injury", "location": "北域冰原" }
  },
  "items": {
    "黑色残片": "acquired"
  },
  "foreshadowing": {
    "v3": { "status": "mentioned", "last_mentioned": 42 }
  },
  "timeline": {
    "current_location": "北域冰原",
    "current_chapter": 42
  }
}
```

**更新规则** 每批次完成后，父Agent汇总本批所有子Agent的state_diff/char_update/plot_update，合并写入该文件。持续累积，不重置。

**分卷模式**：`consistency-rules.json` 按卷隔离存储于 `.sumeru/volumes/vol-N/continuity/consistency-rules.json`。
每卷独立累积，卷切换时通过 Phase B 的 state-start.json 继承前卷状态子集。

---

# 第八部分：各 Skill 子Agent职责明细
> 各技能核心职责见 §一·技能清单。子Agent I/O 详情见各 `SKILL.md`。

---

# 第九部分：修改边界
- `sumeru-review` 直接修复错别字、轻微逻辑补丁、字数不足，不大量重写- `sumeru-polish` 优化文笔/节奏/对话/爽点，不改变主线事实和角色关系- `sumeru-finalize` 专注技术校验和发布格式，不承担剧情重构
- 下游 Skill 不直接调用上游；需返工时输出结构化计划
- 正文修改默认产出最终版，修改前保留最小备份
---

# 第十部分：剧情统一门禁与反AI扫描

所有写作重写/润色必须先校验剧情事实再写入，写入后执行反AI扫描。
## 一、剧情统一检查项

父Agent写入前检查：

1. **承接检查**：本章必须承接上一章实际结局
2. **人物检查**：位置、伤势、战力、关系与 consistency-rules.json 一致
3. **道具检查**：归属、消耗、损坏状态一致
4. **时间线检查**：事件顺序不倒置；回忆/梦境/插叙显式标记
5. **伏笔检查**：已回收伏笔不重复激活；新伏笔记录 ID/首次章节/预期回收方向
6. **任务卡检查**：不违反 `protectedElements` 和 `acceptanceCriteria`

**处理规则**：critical/high 冲突→暂停写入，写 issue 等待仲裁；medium→允许草稿但标记待修复；low→自动修复或记入 changelog

## 二、父Agent校验流程

写作/润色完成后，父Agent必须执行以下校验）
```
1. 提取 SUMERU_STATUS 中的 state_diff、char_update、plot_update
2. 比对 consistency-rules.json、最近3 批摘要、上一章实际结尾对比检查：
   - 人物位置冲突（unique_location）   - 道具状态冲突（destroyed_item_used）   - 时间线倒置（timeline_order）   - 战力无因跳跃（power_level_consistency）   - 伤势无因恢复（character_state_regression）   - 已回收伏笔重复激活（foreshadowing_recycled）4. 发现 critical/high 冲突 →暂停写入，生成 issue
5. 校验通过 →更新 chapters/、status.json、continuity cache
```

## 三、反AI句式扫描

剧情校验通过后，父Agent对每批子Agent输出执行以下扫描。
**v1.2.2 修订**：扫描由"不阻塞"改为"分层处理"——水文硬指标命中即**自动触发 polish 轻量级 + fix-plan 标记**，不再等用户手动跑 polish。

### A. 扫描入口

```bash
python skills/sumeru-review/scripts/anti-ai-scan.py <chapters_dir> \
    [--outlines outlines/chapters.json] \
    [--output .sumeru/review] \
    [--quiet]
```

脚本实现 sumeru-review/SKILL.md §反 AI / 反水文扫描 中定义的 17 项检查 + 9 维反 AI 句式扫描（v1.2.3 新增 2 维：micro_arc + dialog_marker；v1.2.4 新增 1 维：dialog_emotion_commentary）。

### B. 9 维反 AI 句式扫描（v1.2.4 扩展，8→9 维；与脚本阈值同步）

| # | 扫描项| 阈值| 严重度 | 处理方式 |
|---|--------|------|--------|----------|
| 1 | **句式重复**：同一章内连续超过 5 句全部是完整主谓宾结构| 6+ 句| medium | polish 轻量级 + 标记 |
| 2 | **开场雷同**：本批相邻两章以相同/相似模式开场 | 8 字重复 | medium | 触发子Agent重写开场 |
| 3 | **结构重复**：连续 3 段都在推进剧情（无缓冲段）| 3 段| low | polish 轻量级 |
| 4 | **句子开头重复**：同一段内连续 3 句以同一主语开头 | 3 句| low | polish 轻量级 |
| 5 | **章间钩子雷同**：本批相邻章节结尾钩子使用了相同句式 | 8 字重复 | medium | 触发子Agent重写结尾 |
| 6 | **字数波动**：本批各章字数偏差超过±50% | 超出 | low | 标记补充 |
| 7 | **段间 micro-arc 模板**（v1.2.3 新增）：4 段结构指纹（A=推进/B=心理/C=描写/D=对话）出现 ≥ 2 次| 8+ 段章节 | medium | polish 中度 + 重排段落 |
| 8 | **对话标记词集中**（v1.2.3 新增）：单一标记词（"说"/"道"/"问道"等）占全部对话标记 ≥ 80% | 总标记 ≥ 5 | medium | polish 中度 + 替换标记词 |
| 9 | **对话后旁白解说**（v1.2.4 新增）：对话已表达情绪（愤怒/悲伤/冷漠等），紧接的叙述又用散文"翻译"同一情绪——如"你给我滚！"他愤怒地说 / "我不知道怎么办……"她的话语里满是无奈 | ≥ 3 处 | medium | polish 中度：删除情绪旁白解说，保留对话本身；若情绪暗示不足则改为动作细节 |

### C. 水文硬指标（v1.2.2 新增，v1.2.3 扩展黑名单，v1.2.4 编号顺延；与脚本同步）

| # | 扫描项 | 阈值 | 严重度 | 处理方式 |
|---|--------|------|--------|----------|
| 10 | 对话占比 | < 5% | medium | polish 中度 + 补对话 |
| 11 | 内心独白占比 | > 10% | medium | polish 中度 + 改动作暗示 |
| 12 | **纯描写段落占比** | > 35% | **high 阻断** | 触发子Agent重写，**禁止自动注入描写** |
| 13 | **核心事件数** | < 1 | **high 阻断** | 触发子Agent重写 |
| 14 | 时间/场景切换 | 0 | medium | polish 中度 |
| 15 | **Cliché 套路短语**（v1.2.3 黑名单 40+ → 80+ 词条：增"战斗套路"+"转折模板"+"情绪标签"三类）| ≥ 3 个不同短语 | **high 阻断** | 触发子Agent重写 |
| 16 | 场景类型占比 | 日常/过渡 > 30% | medium | 调整 rhythm 规划 |

> **编号说明**：v1.2.2 → v1.2.3 编号顺延 2（新增项占 7/8 位），原 7-13 号顺延为 9-15；v1.2.3 → v1.2.4 新增第 9 项（dialog_emotion_commentary），原 9-15 号不变。

### D. 扫描结果处理（v1.2.3 修订）

- **critical 命中**（无 —— 当前规则无 critical 级，保留扩展位）→ 立即暂停批次
- **high 阻断命中**（12/13/15 任一）→ **写 fix-plan.json `type=anti_ai_blocked`**，触发 write 重写流程；父 Agent 不得用"插入 2-4 段描写"方式补字数
- **medium 命中**（1/2/5/7/8/9/10/11/14/16 任一）→ **自动触发 polish 轻量级**（不再仅写 changelog 提醒用户）；连续 2 批同章节同问题升级为 high
- **low 命中**（3/4/6 任一）→ 写 changelog，留待 polish 中度时处理
- **7/8/9 号新检查说明**：micro_arc / dialog_marker / dialog_emotion_commentary 留 medium 不进阻断，先观察一轮后视情况升级（v1.2.3/v1.2.4 灰度策略）

**历史兼容性**：v1.2.1 及之前的"`anti-ai-flagged` 章节 → 记录到 changelog，不阻塞"已废弃。新行为：从 passive 提醒升级为 active 联动。

## 四、冲突检测规则
| 规则ID | 描述 | 严重程度 |
|--------|------|----------|
| `unique_location` | 同一人物不能同时在两个地点| critical |
| `destroyed_item_used` | 已毁道具不能再次使用 | critical |
| `foreshadowing_recycled` | 已回收伏笔不能再次active | high |
| `character_state_regression` | 人物状态不能无原因回退 | high |
| `power_level_consistency` | 战力等级不能无原因跳跟| medium |
| `timeline_order` | 事件时间线必须有库| high |

## 五、伏笔管理
### 伏笔状态流转
`设置(active) →推进(mentioned) →回收(resolved)`，期望回收章节已过时自动提醒

### 伏笔字段

```json
{
  "id": "v1",
  "description": "伏笔描述",
  "status": "active|pending|resolved",
  "first_appeared": 15,
  "last_mentioned": 42,
  "expected_payoff_chapter": 80,
  "importance": "high|medium|low",
  "related_chapters": [15, 28, 42],
  "payoff_chapter": null,
  "payoff_detail": null
}
```

### 管理建议

- **过期提醒**：期望回收章节已过时提醒
- **数量控制**：活跃超过0个时建议回收低优先级
- **新伏笔规则**：近期设置多个新伏笔时规划回收时间
---

# 第十一部分：输出级别与安全约定

## 输出级别规范

| 级别 | 说明 | 适用场景 |
|------|------|----------|
| `quiet` | 只输出进度和关键节点 | **默认**，日常创作|
| `normal` | 输出进度 + 阶段总结 + 问题提醒 | 用户明确要求 |
| `verbose` | 完整输出所有中间报告 | 调试/审查 |

**quiet 模式只输出：** 阶段开始完成通知、进度条、错误和警告。-2 行阶段总结。不输出脚本详细输出、中间报告、技术细节。
## 写作安全与原创性
- 避免直接复刻现实公众人物、真实组织、地名、知名 IP 角色
- 参考作品时只学节奏和类型结构，不抄具体内容
- 涉及敏感内容时优先合规化改写并说明风险

## 标题与文件命名规范

### 禁止叙事性标题

章节标题（显示在正文中的标题）和文件名均不得使用叙事性标题。叙事性标题指描述文本在故事结构中的功能/位置而非具体内容的标题，这类标题不具备信息量且容易造成混乱。

### 禁止列表

以下类型的标题一律禁止作为章节标题或文件名：

| 禁止类型 | 示例 | 判定依据 |
|---------|------|----------|
| 章节位置型 | 第一章、下一章、最后一章 | 仅描述章节在序列中的位置，无内容信息 |
| 卷归属型 | 第一卷、卷末、卷终、本卷完 | 描述卷归属或卷位置，非本章实际事件 |
| 结构功能型 | 终章、尾声、后记、序章、结局 | 描述文本功能而非具体情节 |
| 模糊叙事型 | 开篇、开章、中篇、续章、前篇 | 笼统描述叙事阶段，缺少具体内容 |

### 命名规范

**章节文件名格式**：`三位编号-描述性标题.md`
- 正确：`001-觉醒仙脉.md`、`042-北域截杀.md`
- 错误：`001-第一章.md`、`042-最后一章.md`

**章节标题（文件中显示）**：必须反映该章的核心事件或场景，使用具体名词或动宾短语。
- 正确：第001章 觉醒仙脉 / 第042章 北域截杀
- 错误：第001章 第一章 / 第042章 最后一章

**卷标题**：必须反映本卷的核心冲突或主题，而非卷在全书中的位置。
- 正确：第一卷 仙门初入 / 第二卷 北域风云
- 错误：第一卷 / 最后一卷

### 例外规则

如果叙事性标题在故事中有特殊叙事意义（如小说中的人物写了一篇题为"最后一章"的文章作为剧情伏笔），需在章节任务卡中注明理由并经 review 确认。此类用例必须在 `outlines/chapters.json` 的对应章节任务卡中标记 `narrative_title_exception: true`。

### 校验规则

- 写入章节文件前，父Agent必须校验标题和文件名是否包含禁止的叙事性标题模式
- 发现违规 → 拒绝写入，提示修改为描述性标题
- sumeru-review 审查阶段增加标题合规性检查项
- sumeru-finalize 导出阶段执行最终标题校验
---

# 第十二部分：子Agent精简版规则
> **子Agent专用规则**规`subagent-rules.md`。子Agent只读 context pack + 该文件，不读取本全局规则。
---

# 第十三部分：平台适配规则索引

平台适配规则按阶段拆分，各阶段职责不重叠）
| 阶段 | 负责 Skill | 检查内容| 输出 |
|------|-----------|----------|------|
| **选题阶段** | `sumeru-topic` | 风格-平台兼容性矩阵、章节字数平台匹配 | 警告 + `platform-fit.json` |
| **审查阶段** | `sumeru-review` | 开篇钩子强度、叙事效率（对话/独白/描写占比）、信息密库| 审查报告 + fix-plan |
| **构建阶段** | `sumeru-finalize` | Build 前质量门禁（同review 指标，但不修改章节） | `build-quality-report.md` + 平台适配建议 |

## 核心指标定义

| 指标 | 阈值| 适用范围 |
|------|------|----------|
| 前00字冲突启加| ≥00存| 第章|
| 前00字无设定铺陈 | 0存| 第章|
| 结尾钩子 | 每章必须本| 第-3章强制，其余建议 |
| 对话占比 | ≥5% | 全部章节 |
| 内心独白占比 | ≥0% | 全部章节 |
| 纯描写占比| ≥5% | 全部章节 |
| 核心事件数| ≥为章| 全部章节 |
| 连续低密库| ≥章| 全部章节 |

---

# 第十四部分：质量检查
执行任一 Skill 后检查：

1. 预期输出文件是否生成
2. `.sumeru/` 结构化数据与用户可见输出是否一致
3. 章节文件按三位编号排序，无缺章重章
4. 修改型Skill 是否生成备份和变更记录
5. 写作/重写/润色后是否通过 SUMERU_STATUS 与 continuity cache 校验
6. 章节标题和文件名是否符合命名规范（禁止叙事性标题，参见"标题与文件命名规范"）
7. 发布导出是否剥离 SUMERU_STATUS 注释
8. **正文是否残留元信息标注**（"视角：""伏笔：""下一章""预告""本章完"等）——写作/润色后自检，finalize 导出时剥离

## 跨卷连续性检查

> 定义见 `sumeru-outline/SKILL.md` "大纲自检项·跨卷连续性检查"（#25-#32）。

大纲阶段和审查阶段必须执行跨卷连续性检查。使用以下**跨卷依赖表**格式记录跨卷依赖：

### 跨卷依赖表格式（写入 `outline.md`）

```markdown
## 跨卷依赖表

| 依赖类型 | 内容 | 源卷 | 目标卷 | 依赖说明 |
|----------|------|------|--------|----------|
| 伏笔 | F3 黑衣人身份 | 卷1·005 | 卷3·012 | 卷1埋设，卷3回收 |
| 成长 | 主角练气三层→筑基 | 卷1→卷2 | 卷2尾 | 卷1末尾练气三层→卷2经历3次战斗后突破 |
| 关系 | 主角↔苏瑾 信任→怀疑 | 卷2·008 | 卷3·010 | 卷2结盟 → 卷3因误会生嫌 |
| 设定 | 黑色残片吸收上限 | 卷1·intro | 卷3 | 卷1限定吸收3次 → 卷3突破上限需新设定补充 |
```

### 跨卷检查的执行时机

| 阶段 | 检查范围 | 执行者 |
|------|----------|--------|
| outline 完成 | 跨卷依赖表生成 + 8 项跨卷自检 | sumeru-outline 父Agent |
| review 完成 | 跨卷依赖表中每项的实际执行情况验证 | sumeru-review 子Agent（并行审查时分配） |
| 新卷写作启动前 | 读取跨卷依赖表，确保前卷承诺在本卷可落地 | sumeru-write 父Agent（自举时读取） |

### 跨卷冲突检测规则（新增）

| 规则ID | 描述 | 严重程度 | 检测时机 |
|--------|------|----------|----------|
| `cross_volume_foreshadowing_gap` | 跨卷伏笔两卷间无提及 | high | outline/review |
| `cross_volume_state_jump` | 跨卷人物状态无因跳跃 | critical | review/write |
| `cross_volume_power_leap` | 跨卷战力无因暴涨 | high | review/write |
| `cross_volume_timeline_gap` | 跨卷时间跳跃未交代 | medium | outline/review |
| `cross_volume_setting_conflict` | 本卷新设定与前卷矛盾 | critical | review |
| `cross_volume_emotion_cliff` | 卷间情绪断层（悲→喜无过渡） | low | outline/review |
| `cross_volume_rhythm_cliff` | 卷间节奏断崖（fast→slow无过渡） | low | outline/review |
| `cross_volume_relationship_stall` | 跨卷人物关系无推进 | medium | review |

---

# 第十五部分：分卷隔离与卷切换协议

> **适用条件**：项目 `chapters/` ≥ 150 章，或 `project.json` 中 `volumeCount ≥ 2`。
> 少于 150 章的项目继续使用扁平模式，无需 volumes/ 目录。

## 一、分卷目录结构

当分卷模式激活时，父Agent在自举阶段自动创建以下目录结构：

```text
.sumeru/volumes/
├── vol-001-仙门初入/
│   ├── outline.md              # 本卷剧情框架（由 sumeru-outline 生成）
│   ├── characters/              # 本卷活跃人物（从全局 characters/ 筛选的副本）
│   ├── continuity/
│   │   ├── state-start.json    # 本卷开场全局状态
│   │   ├── state-current.json  # 当前最新状态
│   │   ├── batch-summaries/    # 批次摘要（见第二部分·批次间串行摘要）
│   │   └── checkpoints/        # 卷内阶段性快照
│   ├── status.json             # 本卷章节状态（200 条，非全局 1500 条）
│   └── world-addendum.md       # 本卷新增设定（可选，不覆盖 world.md）
├── vol-002-北域风云/
│   └── ...
└── vol-003-...
```

此外，自举阶段创建跨卷骨架数据：

```text
.sumeru/cross-volume/
├── dependency-table.md         # 跨卷依赖表（同 outline.md 末尾格式）
├── master-timeline.md          # 全局时间线主干（每卷起止时间 + 关键事件）
└── master-characters.md        # 全局人物索引（每卷出场标记）
```

## 二、卷切换协议（Volume Handoff）

### Phase A — 当前卷完结

由 `sumeru-write` 父Agent检测到当前卷最后一批写作完成时自动触发：

1. **最终快照**：将 `state-current.json` 复制为 `state-final.json`，写入 `vol-N/continuity/`
2. **卷级总结**：生成 ≤ 500 字卷级总结，包含：
   - 本卷起止章节号、时间跨度的
   - 本卷核心事件清单（5-8 条）
   - 本卷结束时各主要人物状态
   - 本卷埋设的跨卷伏笔（指向目标卷）
   - 本卷结束时未回收的伏笔列表
3. **更新跨卷骨架**：
   - `cross-volume/master-timeline.md` 追加卷条目
   - `cross-volume/dependency-table.md` 追加本卷新注册的跨卷依赖
   - `cross-volume/master-characters.md` 更新人物状态
4. **存档批次摘要**：`vol-N/continuity/batch-summaries/` → 移入 `vol-N-archived/`（保留只读）
5. **标记卷完成**：`project.json` → `volumes[vol-N].status = "completed"`
6. **回写 changelog**：`.sumeru/changelog.md` 追加卷完结记录

### Phase B — 新卷启动

由 `sumeru-worldbuilder` 编排 `sumeru-outline` 在新卷写作开始前执行：

1. **加载前卷快照**：从 `vol-N/continuity/state-final.json` 读取
2. **生成本卷开场状态**：`state-start.json` — 继承 state-final 中与本卷相关的子集（过滤掉下卷不再活跃的人物/道具）
3. **创建卷目录**：`.sumeru/volumes/vol-M/` 及子目录
4. **生成 outline**：`vol-M/outline.md`（本卷剧情框架，由 sumeru-outline 生成）
5. **筛选活跃人物**：从 `cross-volume/master-characters.md` 筛选本卷出场人物，复制到 `vol-M/characters/`
6. **加载跨卷承诺**：从 `cross-volume/dependency-table.md` 筛选 `目标卷 = vol-M` 的条目，注入 `vol-M/outline.md` 的"本卷必须兑现"清单
7. **初始化状态**：`vol-M/status.json`（空状态，章节状态 = `planned`）
8. **清空批次缓存**：`vol-M/continuity/batch-summaries/` 写入唯一的软重置条目（上一卷最后 1 批摘要 + 卷级总结）
9. **更新 project.json**：`currentVolume = "vol-M"`

### Phase C — 跨卷引用查询

任何技能需要读取跨卷数据时，不扫描全量 continuity，而是：

1. 查询 `.sumeru/cross-volume/dependency-table.md` 看是否有与本卷相关的条目
2. 如果有 → 只读取对应卷的 `state-final.json` 或 `state-start.json`
3. 如果没有 → 不做跨卷读取

此规则适用于所有技能（write/review/polish/finalize）。

## 三、分卷模式的文件操作规则

| 操作 | 非分卷模式 | 分卷模式 |
|------|-----------|---------|
| 写入章节 | `chapters/001.md` | 同左（chapters/ 保持扁平全局编号） |
| 更新章状态 | `.sumeru/status.json` | `.sumeru/volumes/vol-N/status.json` |
| 更新 continuity | `.sumeru/continuity/` | `.sumeru/volumes/vol-N/continuity/` |
| 缓存读写 | `.sumeru/cache/` | `.sumeru/cache/vol-N/` |
| 人物卡写入 | `characters/` | `characters/`（全局统一，vol-N/characters/ 为镜像筛选） |
| context pack | `.sumeru/context-packs/` | `.sumeru/context-packs/`（数据源按作用域规则限定） |
| 跨卷查询 | 不适用 | `.sumeru/cross-volume/dependency-table.md` → 精确加载 |

## 四、分卷模式的激活与降级

### 激活条件
- **自动**：`sumeru-worldbuilder` 自举时发现 `chapters/` ≥ 150 章或 `outline.md` 中分卷数 ≥ 2
- **手动**：用户在任意阶段要求 `启用分卷模式` 或 `/sumeru-migrate 启用分卷`

### 降级条件
- **自动**：全书完稿后（所有章节状态为 `finalized`），可选取消除卷隔离归档到扁平结构
- **手动**：用户要求 `合并卷结构`，由 `sumeru-migrate` 执行逆向合并

### volumeCount 配置
见 `project.json` Schema（第七部分）。`volumeCount` 可选，缺失时按扁平模式运行。
分卷模式激活后 `project.json` 新增字段：
```json
{
  "volumeCount": 5,
  "currentVolume": "vol-003",
  "volumes": {
    "vol-001": { "title": "仙门初入", "chapterRange": [1, 200], "status": "completed" },
    "vol-002": { "title": "北域风云", "chapterRange": [201, 400], "status": "completed" },
    "vol-003": { "title": "秘境探秘", "chapterRange": [401, 600], "status": "active" }
  }
}
```

---


