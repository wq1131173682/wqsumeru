---
name: sumeru-rules
description: 须弥写作全局约束规则（唯一来源）。子Agent并行规则 + 职责划分 + 状态标�?+ Context Pack 格式 + 剧情统一门禁 + 输出规范 + 子Agent精简规则�?version: 1.2.0
type: skill
user-invocable: false
---

# 须弥写作全局约束规则

所有须弥写�?Skill 必须遵守以下规则。本文档是唯一全局约束源�?
---

# 第一部分：系统架�?
## 技能清�?
| 技�?| 职责 | 触发场景 | user-invocable |
|------|------|----------|----------------|
| `sumeru-worldbuilder` | 全流程统筹主�?| "从零写小�?�?帮我写本XX类型小说"�?初始化项�? | �?|
| `sumeru-topic` | 选题策划与创意架�?| "不知道写什�?�?找热门题�?�?做选题分析" | �?|
| `sumeru-outline` | 大纲设计（世界观/人物/分卷/章节细纲�?| "写大�?�?设计人物"�?世界观设�? | �?|
| `sumeru-write` | 章节内容创作 | "写第X�?�?续写"�?扩写"�?重写"�?批量生成" | �?|
| `sumeru-review` | 逻辑审查与创意疲劳检�?| "检查bug"�?时间线矛�?�?人物OOC" | �?|
| `sumeru-polish` | 文笔润色与创意强�?| "润色"�?改文�?�?优化节奏"�?强化爽点" | �?|
| `sumeru-finalize` | 完稿校验与发布导�?| "检查错别字"�?检测敏感词"�?导出平台格式" | �?|
| `sumeru-migrate` | 旧项目迁移与规整 | "规整项目"�?迁移旧项�?�?补齐缺失文件"�?查缺补漏" | �?|
| `sumeru-rules` | 全局约束规则（不直接调用�?| �?| �?|

## 调用链路

```
用户需�?    �?    �?┌─────────────────────────────────────────────────────────────�?�? sumeru-worldbuilder（全流程统筹�?                           �?�? 负责：项目初始化、阶段推进、状态管理、结果汇�?                   �?└─────────────────────────────────────────────────────────────�?    �?    ├─�?sumeru-topic        选题策划 �?plan.md
    �?    ├─�?sumeru-outline      大纲设计 �?outline.md, chapters.json, characters/
    �?    ├─�?.sumeru/intro.md    简介生成（worldbuilder 内置�?    �?    ├─�?.sumeru/creative-anchors.md  创意锚点确认（worldbuilder 内置�?    �?    ├─�?sumeru-write        章节写作 �?chapters/*.md
    �?      �?    �?      └─ 子Agent并行（最�?个，每个�?章）
    �?    ├─�?sumeru-review       逻辑审查 �?issues.md, fix-plan.json
    �?      �?    �?      └─ 子Agent并行审查 + 反审验证
    �?    ├─�?sumeru-write        修复重写（读�?fix-plan.json�?    �?    ├─�?sumeru-polish       文笔润色 �?chapters/*.md（替换原文）
    �?      �?    �?      └─ 子Agent并行润色
    �?    └─�?sumeru-finalize     完稿校验 + 发布导出 �?publish/
```

**独立调用**：每�?skill 都可以脱�?worldbuilder 单独启动，执行自举协议�?
## 状态机

### 项目状态流�?
```
init �?topic �?outline �?intro �?anchor �?write �?review �?fix �?polish �?finalize �?build/release
```

### 章节状态流�?
```
planned �?drafted �?reviewed �?fixed �?polished �?finalized �?exported
                              �?                              �?(反审未通过时回退)
                              └──────────────────
```

### 推进规则

| 阶段完成条件 | 说明 |
|-------------|------|
| `topic` �?`outline` | `plan.md` 已写入，含选题方向和目标平�?|
| `outline` �?`anchor` | `outline.md`、`chapters.json`、`.sumeru/intro.md` 存在 |
| `anchor` �?`write` | `.sumeru/creative-anchors.md` 存在，≥3 个锚点确�?|
| `write` �?`review` | 目标章节文件存在，状�?`drafted`，无缺章 |
| `review` �?`fix` | 问题写入 `issues.md`，重写项写入 `fix-plan.json` |
| `fix` �?`polish` | 反审验证通过，章节状�?`fixed` |
| `polish` �?`finalize` | 章节状�?`polished` |
| `finalize` �?`build` | 技术校验通过，章节状�?`finalized` |

## 文件索引

### 用户可见文件

| 文件 | 内容 | 生成阶段 |
|------|------|----------|
| `plan.md` | 需求、设定、人物、风格、创意策略、术�?| topic |
| `outline.md` | 故事结构、主线、伏笔、分卷与章节规划 | outline |
| `outlines/chapters.json` | 章节任务�?| outline |
| `characters/*.md` | 人物�?| outline |
| `world.md` | 世界观手�?| outline (long/full) |
| `chapters/*.md` | 正文 | write / polish |
| `reviews/review-report.md` | 审查报告 | review |
| `publish/` | 发布产物 | finalize |

### 中间数据（`.sumeru/`�?
| 文件/目录 | 内容 |
|-----------|------|
| `.sumeru/project.json` | 项目配置 |
| `.sumeru/status.json` | 阶段和章节状�?|
| `.sumeru/intro.md` | 小说简�?|
| `.sumeru/creative-anchors.md` | 创意锚点 |
| `.sumeru/issues.md` | 问题清单 |
| `.sumeru/changelog.md` | 变更日志 |
| `.sumeru/decisions.md` | 决策记录 |
| `.sumeru/backlog.md` | 待办事项 |
| `.sumeru/cache/` | 各类摘要缓存 |
| `.sumeru/context-packs/` | 子Agent上下文包 |
| `.sumeru/continuity/` | 剧情一致性数�?|
| `.sumeru/topic/` | 选题阶段数据 |
| `.sumeru/write/` | 写作阶段数据 |
| `.sumeru/polish/` | 润色阶段数据 |
| `.sumeru/finalize/` | 完稿阶段数据 |

### 旧路径兼容（只读�?
| 旧路�?| 新路�?| 说明 |
|--------|--------|------|
| `.sumeru/outline/chapter-outlines.json` | `outlines/chapters.json` | 章节任务�?|
| `.sumeru/issues/index.json` | `.sumeru/issues.md` | 问题清单 |
| `docs/*`、`ideas/*` | `plan.md` | 需�?设定 |

---

# 第二部分：子Agent并行处理规则

| 规则 | 说明 |
|------|------|
| **适用范围** | 章节写作、章节重写、剧情审查、轻量修复、内容润色、完稿校验、平台导出、章节细纲生�?|
| **核心原则** | 写正文必须走子agent，单章续写也必须走子agent，父agent绝不写正�?|
| **并行上限** | 最�?5 个子agent同时运行 |
| **分片约束** | 每个子Agent最多负�?3 个连续章�?|
| **计算公式** | 所需Agent�?= `min(ceil(总章节数 / 3), 5)` |
| **分配策略** | 按章节顺序连续分组（1-3�?-6�?-9...�?|
| **上下文约�?* | 每个子Agent只接收完成任务所需的精简上下�?|

## 批次间串行摘�?
每批子Agent完成后，父Agent生成"实际摘要"（≤300字），作为下一�?context pack 的输入。context pack 中只保留最�?3 批摘要，更早的合并为一行概述�?
**摘要格式**（纯事实列表）：
```
## 批次摘要: �?-6�?- 事件：主角觉醒系�?001)、通过宗门考核(003)、击败外门弟�?005)
- 人物：主角练气三层→五层，苏瑾轻伤恢复，赵无极首次出�?- 道具：黑色残片归主角，回春丹消�?�?- 伏笔：v1黑衣人身�?mentioned)，v2残片来历(active)
- 情绪：压抑→突破→暗�?```

**存储位置**：`.sumeru/continuity/batch-summaries/batch-001.md`、`batch-002.md`...

---

# 第三部分：子Agent职责边界

**核心原则：子Agent直接写入本组正文章节文件，返回精简状态标记；父Agent负责备份、状态同步、缓存刷新和汇总�?*

## 父Agent职责

| 职责 | 说明 |
|------|------|
| 自举 & 环境准备 | 定位项目、读/生成 project.json、status.json、补齐目�?|
| Context pack 生成 | 集中生成 context pack，控�?1500-3000 中文字，分发给各子Agent |
| Cache 摘要读取 | 集中读取 L1 cache 摘要 |
| 任务卡读�?| 集中读取目标章节任务卡，仅提取本组章节所需字段 |
| 任务分发 | 启动 N 个子Agent，每个传入精简 context pack |
| 结果汇�?| 收集所有子Agent输出，检查完整性、顺序、命�?|
| 文件写入 & 备份 | 子Agent写入后，父Agent校验文件存在性、SUMERU_STATUS标记完整性；将原文件备份�?`.sumeru/write/original/`，每章仅保留最�?1 �?|
| 状态更�?| 统一更新 `.sumeru/status.json`（章节状态、阶段状态） |
| 缓存刷新 | 统一刷新相关 cache 摘要 |
| 日志记录 | 统一追加 `.sumeru/changelog.md`、`.sumeru/decisions.md` |
| Issue/测试汇�?| 合并各子Agent发现的问题，写入 `.sumeru/issues.md` |

## 子Agent职责

| 职责 | 说明 |
|------|------|
| 只读 context pack | 不读�?context pack 外的任何文件（已有章节文件除外） |
| 执行核心任务 | 根据 context pack 完成任务�?审查/润色要求 |
| 直接写入正文章节文件 | 正文写入 `chapters/*.md`，细纲写�?`outlines/chapters.json`，无需经父Agent透传 |
| 返回状态标�?| 只返�?`<!-- SUMERU_STATUS: ... -->`（不含正文），父Agent据此更新状�?|
| 不碰状态文�?| 不更�?status.json、changelog、cache、issues |

---

# 第四部分：Context Pack 格式与生成规�?
**为减少同批次内容重复，context pack 拆为 2 个文件：**

| 文件 | 命名规则 | 大小 | 是否共享 |
|------|----------|------|----------|
| 共享上下�?| `shared-{task}.md` | ~1500-2000 �?| 同批次所有子Agent共用 |
| 本组任务�?| `cards-{范围}.md` | ~300-500 �?| 每子Agent独有 |

子Agent先读共享上下文，再读本组任务卡，两者合并作为完�?context�?
## 一、通用共享上下文格�?
```markdown
# Shared Context: {task} (batch {N})

## Project Brief (1-2�?
题材、平台、字数范围、整体风格�?
## Current Volume (1-2�?
本卷目标、当前冲突、卷级反转、阶段情绪�?
## Relevant Characters (仅本卷相�?
相关人物的当前状态、目标、关系、语言风格�?
## Relevant World & Glossary (仅本卷会用到�?
地点、组织、功法、道具、禁用变体�?
## Continuity State
上一章结尾、关键道具状态、未回收伏笔、时间线位置�?
## Creative Strategy
创意目标、要避开的套路、情绪节拍变化、读者记忆点�?
## Batch Summary (仅非第一�?
前N批实际摘要（�?00字）�?
## Output Requirements
文件命名、状态更新需求（由父agent执行）�?
## Opening & Style Diversity
- 同一批次各章开场方式必须不�?- 同一批次各章结尾钩子句式必须不同
- 同一章内连续超过 5 句完整主谓宾结构 �?必须插入破碎�?口语短句
```

## 二、通用任务卡格�?
```markdown
# Task Cards: {范围}

## Chapter Cards
### 第{N}章「标题�?- purpose: ...
- events: ...（≥3个具体事件）
- openingHook: 本章开场方式（可执行的场景描述�?- acceptanceCriteria: ...
- creativeGoal: ...
- emotionalBeat: ...

## 本章执行提醒 (�?�?
具体可执行的过程提醒�?```

## 三、各技能专用部�?
### write 专用

**共享上下文增�?*�?- Output Requirements 中明确：每章首行 SUMERU_STATUS，多章间 --- 分隔

**任务卡增�?*�?- 完整的章节任务卡字段（purpose、events、openingHook、outputs、acceptanceCriteria、creativeGoal、freshnessHook、emotionalBeat、readerMemoryPoint、tropeToAvoid、protectedElements、rhythm�?
### review 专用

**共享上下文增�?*�?- 审查标准（检查类型、严重程度定义）
- consistency-rules.json 摘要

**任务卡格�?*�?```markdown
# Review Cards: {范围}

## Chapter Review Cards
### 第{N}章「标题�?- 检查类型：剧情统一/字数/时间�?人物OOC/伏笔/常识
- 重点检查：{根据章节特点指定}
- 已知问题：{如有}

## 审查执行提醒
- 轻量问题直接修复
- 严重问题写入 fix-plan.json
```

### polish 专用

**共享上下文增�?*�?- 风格标杆（具象标杆，300字以内）
- 润色等级（轻�?中度/深度�?- 场景类型分布提示

**任务卡格�?*�?```markdown
# Polish Cards: {范围}

## Chapter Polish Cards
### 第{N}章「标题�?- 润色等级：{轻度|中度|深度}
- 场景类型：{打斗/对话/心理/日常/高潮}
- 重点优化：{�?强化爽点"�?优化对话"}

## 润色执行提醒
- 场景类型规则 > 禁止项规�?- 副词处理：个人化保留，AI式隔一清一
```

**具象标杆格式**�?```
【风格标杆�?--场景标杆(�?03�?--
[原文段落�?00字以内]

--对话标杆(�?05�?--
[原文段落�?00字以内]

--情绪标杆(�?08�?--
[原文段落�?00字以内]
```

### finalize 专用

**共享上下文增�?*�?- 待定项列表（最�?0个）
- 待定项上下文（前�?00字符�?
**任务卡格�?*�?```markdown
# Finalize Cards: {范围}

## Pending Items
### 待定�?1
- 章节：{N}
- 词语：{敏感词}
- 位置：{position}
- 上下文：{前后100字符}
- 初步判断：{safe|remove|replace}

## 处理建议
- 根据上下文判断是否需要修�?- 返回 verdict + reason + replacement
```

## 四、文件位�?
所�?context pack 写入 `.sumeru/context-packs/`�?- `shared-{task}.md`：共享上下文
- `cards-{范围}.md`：本组任务卡

---

# 第五部分：子Agent输出状态标�?
每个子Agent写入的章节文件首行必须包含状态标记（供重启恢复），同时向父Agent返回同一标记（供实时状态同步）�?
## 格式

```markdown
<!-- SUMERU_STATUS: chapter=037, status=drafted, state_diff={"location_change":{"苏瑾":"北域冰原"},"state_change":{"苏瑾":"minor_injury"},"item_change":{"黑色残片":"acquired"}}, char_update={"苏瑾":{"status":"minor_injury","location":"北域冰原"},"主角":{"status":"healthy","buff":"龙血狂暴","remaining":"3�?}}, plot_update={"foreshadowing":{"v3":"黑衣人身份暗示推�?}}, batch=002, timestamp=2026-05-18T10:30:00Z -->
```

## 字段说明

| 字段 | 含义 | 格式 |
|------|------|------|
| `chapter` | 章节�?| 字符�?|
| `status` | 章节状�?| `drafted` / `polished` / `finalized` |
| `state_diff` | 结构化状态变�?| JSON 对象 |
| `char_update` | 人物当前状�?| JSON 对象 |
| `plot_update` | 伏笔线推�?| JSON 对象 |
| `batch` | 所属批次号 | 字符�?|
| `timestamp` | 生成时间 | ISO 8601 |

## state_diff 分类

| 分类�?| 含义 | 示例 |
|--------|------|------|
| `location_change` | 人物位置变化 | `{"苏瑾":"北域冰原"}` |
| `state_change` | 人物健康状态变�?| `{"苏瑾":"minor_injury"}` |
| `power_change` | 战力等级变化 | `{"主角":"练气五层"}` |
| `item_change` | 道具状态变�?| `{"黑色残片":"acquired"}` |
| `foreshadow_change` | 伏笔状态变�?| `{"v3":"mentioned"}` |
| `buff_change` | Buff状态变�?| `{"主角":"龙血狂暴|3�?}` |

各分类键可选，只包含本章有变化的分类。`state_diff` 必须是合�?JSON 单行�?
## 关键约束

- 状态标记必须在输出**第一�?*
- 标记缺失、JSON 不合法、章节号不匹配时，不得更新状态文�?
## 父Agent处理流程

1. 提取每章�?`<!-- SUMERU_STATUS -->` 标记
2. 解析 `state_diff` 更新 `.sumeru/continuity/consistency-rules.json`
3. 解析 `char_update` 更新人物状�?4. �?`status` 写入 `.sumeru/status.json`
5. 重启后扫�?`chapters/*.md` 标记即可重建状�?
---

# 第六部分：独立调用自举协�?
任何 Skill 单独启动时必须执行：

1. **定位项目**：从当前目录向上查找 `.sumeru/project.json` / `plan.md` / `outline.md` / `chapters/` / `outlines/`
2. **识别版本**：存�?`.sumeru/project.json` 按新协议，否则进入兼容模�?3. **最小初始化**：缺配置时根据已有文件生成最小配�?4. **补齐目录**：按需创建 `.sumeru/cache/` / `context-packs/` / `continuity/` / `issues.md`
5. **兼容输入**：旧�?`.sumeru/outline/chapter-outlines.json` 只读兼容
6. **刷新缓存**：相�?cache 缺失或过期时生成最小摘�?7. **生成 context pack**：缺 context pack 时生成临�?pack
8. **执行并回�?*：更�?`.sumeru/status.json`、cache、issue 文件
9. **记录变更**：追加到 `.sumeru/changelog.md` �?`.sumeru/decisions.md`

## Canonical 路径

| 类型 | 新写入路�?| 旧路径处�?|
|------|------------|------------|
| 项目配置 | `.sumeru/project.json`、`.sumeru/status.json` | �?|
| 需�?设定/创意 | `plan.md` | `docs/*`、`ideas/*` 只读兼容 |
| 大纲/任务�?| `outline.md`、`outlines/chapters.json` | `.sumeru/outline/chapter-outlines.json` 只读兼容 |
| 简�?| `.sumeru/intro.md` | �?|
| 正文 | `chapters/` 或短�?`story.md` | �?|
| 人物�?| `characters/` 目录 | �?|
| 世界�?| `world.md` | �?|
| 问题清单 | `.sumeru/issues.md` | `.sumeru/issues/index.json` 只读兼容 |
| 审查摘要 | `reviews/review-report.md` | 按需生成 |
| 测试报告 | `tests/` | 按需生成 |
| 发布产物 | `publish/` | �?|

## 旧路径兼容策�?
**原则**：旧路径只读兼容，新写入一律使�?canonical 路径�?
| 旧路�?| 兼容方式 | 迁移时机 |
|--------|----------|----------|
| `.sumeru/outline/chapter-outlines.json` | 读取时自动映射到 `outlines/chapters.json` | 下次写入时迁�?|
| `.sumeru/issues/index.json` | 读取时自动映射到 `.sumeru/issues.md` | 下次写入时迁�?|
| `docs/*`、`ideas/*` | 只读引用，不自动迁移 | 用户手动整理 |
| `docs/glossary.md` | 只读引用，映射到 `plan.md` 术语�?| 用户手动整理 |
| `docs/style-guide.md` | 只读引用，映射到 `.sumeru/cache/style-brief.md` | 用户手动整理 |

**迁移规则**�?1. 读取旧路径时，先检�?canonical 路径是否存在
2. canonical 路径存在 �?直接使用 canonical 路径
3. canonical 路径不存�?+ 旧路径存�?�?读取旧路径，写入时使�?canonical 路径
4. 两者都不存�?�?按新协议创建

## 独立调用原则

- 不要求先运行 worldbuilder
- 能从现有文件推断的信息不重复询问
- 缺信息但不阻塞任务时用合理默认�?- 不因缓存/context pack 缺失而失�?
---

# 第七部分：项目配�?Schema

```json
{
  "schemaVersion": 1,
  "title": "未命名作�?,
  "genre": "玄幻",
  "targetPlatform": "番茄",
  "audience": "男频",
  "plannedWords": 800000,
  "plannedChapters": 300,
  "chapterWordRange": [2000, 3000],
  "style": "快节奏爽�?,
  "tone": "热血",
  "currentStage": "outline",
  "outputLevel": "quiet",
  "createdAt": "2026-05-16T00:00:00Z",
  "updatedAt": "2026-05-16T00:00:00Z"
}
```

**阶段状态：** `pending` / `in_progress` / `blocked` / `completed` / `skipped`

**章节状态：** `planned` / `drafted` / `reviewed` / `fixed` / `polished` / `finalized` / `exported`

修复后经反审验证通过进入 `fixed`；润色发现逻辑硬伤时触发反审验证�?
## consistency-rules.json 格式

由父Agent从每章的 SUMERU_STATUS 解析合并生成，位�?`.sumeru/continuity/consistency-rules.json`�?
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

**更新规则�?* 每批次完成后，父Agent汇总本批所有子Agent�?state_diff/char_update/plot_update，合并写入该文件。持续累积，不重置�?
---

# 第八部分：各 Skill 子Agent职责明细

| Skill | 子Agent核心任务 | 子Agent输入 | 子Agent输出 | 父Agent后续处理 |
|-------|----------------|------------|------------|----------------|
| **sumeru-topic** | 生成选题方案 | context pack（题材方�?创意引擎�?| 选题方案（pitch+类型混血+金手指变�?反套路策略） | 合并写入 `plan.md`、`.sumeru/topic/` |
| **sumeru-outline** | 生成章节细纲 | context pack（世界观+人物+分卷大纲+上下文关联） | 章节细纲 JSON/Markdown + 状态标�?| 合并校验→写�?outlines/chapters.json→刷�?cache |
| **sumeru-write** | 按任务卡写正�?| context pack（任务卡+上一章结�?剧情事实基准+人物/道具/伏笔状态） | 纯正�?+ 状态标�?| 剧情统一校验→写�?chapters/→备份→更新 status→刷�?continuity cache |
| **sumeru-review** | 按任务卡审查章节 | context pack（任务卡+正文+审查标准+consistency-rules�?| 审查结论（问题列�?严重程度+证据+建议�?| 合并问题写入 issues.md，按需生成 review report，制�?fix-plan |
| **sumeru-polish** | 按标准润色章�?| context pack（正�?style-brief+creative-brief+审查问题+具象标杆�?| 润色后正�?+ 状态标�?| 备份后直接写入最终正文，更新 status→polished |
| **sumeru-finalize** | 脚本预处�?+ 待定项判�?| 脚本扫描结果（待定项列表，最�?0个） | 待定项处理建�?| 汇总建议→最终校验→写入 publish/→build-manifest |

---

# 第九部分：修改边�?
- `sumeru-review` 直接修复错别字、轻微逻辑补丁、字数不足，不大量重�?- `sumeru-polish` 优化文笔/节奏/对话/爽点，不改变主线事实和角色关�?- `sumeru-finalize` 专注技术校验和发布格式，不承担剧情重构
- 下游 Skill 不直接调用上游；需返工时输出结构化计划
- 正文修改默认产出最终版，修改前保留最小备�?
---

# 第十部分：剧情统一门禁与反AI扫描

所有写�?重写/润色必须先校验剧情事实再写入，写入后执行反AI扫描�?
## 一、剧情统一检查项

父Agent写入前检查：

1. **承接检�?*：本章必须承接上一章实际结�?2. **人物检�?*：位置、伤势、战力、关系与 consistency-rules.json 一�?3. **道具检�?*：归属、消耗、损坏状态一�?4. **时间线检�?*：事件顺序不倒置；回�?梦境/插叙显式标记
5. **伏笔检�?*：已回收伏笔不重�?active；新伏笔�?ID/首次章节/预期回收方向
6. **任务卡检�?*：不违反 `protectedElements` �?`acceptanceCriteria`

**处理规则�?* critical/high 冲突→暂停写入，�?issue 等待仲裁；medium→允许草稿但标记待修复；low→自动修复或记入 changelog

## 二、父Agent校验流程

写作/润色完成后，父Agent必须执行以下校验�?
```
1. 提取 SUMERU_STATUS 中的 state_diff、char_update、plot_update
2. �?consistency-rules.json、最�?3 批摘要、上一章实际结尾对�?3. 检查：
   - 人物位置冲突（unique_location�?   - 道具状态冲突（destroyed_item_used�?   - 时间线倒置（timeline_order�?   - 战力无因跳跃（power_level_consistency�?   - 伤势无因恢复（character_state_regression�?   - 已回收伏笔重复激活（foreshadowing_recycled�?4. 发现 critical/high 冲突 �?暂停写入，生�?issue
5. 校验通过 �?更新 chapters/、status.json、continuity cache
```

## 三、反AI句式扫描

剧情校验通过后，父Agent对每批子Agent输出执行以下扫描�?
| # | 扫描�?| 阈�?| 处理方式 |
|---|--------|------|----------|
| 1 | **句式重复**：同一章内连续超过 5 句全部是完整主谓宾结�?| 6+ �?| 标记 `anti-ai-flagged`，提示用�?|
| 2 | **开场重�?*：本批相邻两章以相同/相似模式开�?| �? �?| 提示并触发子Agent重写开�?|
| 3 | **结构重复**：连�?3 段都在推进剧情（无缓冲段�?| 3 �?| 提示插入缓冲段落 |
| 4 | **句子开头重�?*：同一段内连续 3 句以同一主语开�?| 3 �?| 提示调整句子开�?|
| 5 | **章间钩子雷同**：本批相邻章节结尾钩子使用了相同句式 | �? �?| 提示并触发子Agent重写结尾 |
| 6 | **字数波动**：本批各章字数偏差超�?±50% | 超出 | 提示补充 |

**扫描结果处理**�?- `anti-ai-flagged` 章节 �?记录�?changelog，不阻塞，提�?polish 修复
- 开�?结构/钩子重复 �?如果子Agent未释放，触发重写
- 字数波动 �?如果低于下限且子Agent未释放，触发补充

## 四、冲突检测规�?
| 规则ID | 描述 | 严重程度 |
|--------|------|----------|
| `unique_location` | 同一人物不能同时在两个地�?| critical |
| `destroyed_item_used` | 已毁道具不能再次使用 | critical |
| `foreshadowing_recycled` | 已回收伏笔不能再�?active | high |
| `character_state_regression` | 人物状态不能无原因回退 | high |
| `power_level_consistency` | 战力等级不能无原因跳�?| medium |
| `timeline_order` | 事件时间线必须有�?| high |

## 五、伏笔管�?
### 伏笔状态流�?
`设置(active) �?推进(mentioned) �?回收(resolved)`，期望回收章节已过时自动提醒

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
- **数量控制**：活跃超�?0个时建议回收低优先级
- **新伏笔规�?*：近期设置多个新伏笔时规划回收时�?
---

# 第十一部分：输出级别与安全约定

## 输出级别规范

| 级别 | 说明 | 适用场景 |
|------|------|----------|
| `quiet` | 只输出进度和关键节点 | **默认**，日常创�?|
| `normal` | 输出进度 + 阶段总结 + 问题提醒 | 用户明确要求 |
| `verbose` | 完整输出所有中间报�?| 调试/审查 |

**quiet 模式只输出：** 阶段开�?完成通知、进度条、错误和警告�?-2 行阶段总结。不输出脚本详细输出、中间报告、技术细节�?
## 写作安全与原创�?
- 避免直接复刻现实公众人物、真实组织、地名、知�?IP 角色
- 参考作品时只学节奏和类型结构，不抄具体内容
- 涉及敏感内容时优先合规化改写并说明风�?
---

# 第十二部分：子Agent精简版规�?
> **子Agent专用规则**�?`subagent-rules.md`。子Agent只读 context pack + 该文件，不读取本全局规则�?
---

# 第十三部分：平台适配规则索引

平台适配规则按阶段拆分，各阶段职责不重叠�?
| 阶段 | 负责 Skill | 检查内�?| 输出 |
|------|-----------|----------|------|
| **选题阶段** | `sumeru-topic` | 风格-平台兼容性矩阵、章节字�?平台匹配 | 警告 + `platform-fit.json` |
| **审查阶段** | `sumeru-review` | 开篇钩子强度、叙事效率（对话/独白/描写占比）、信息密�?| 审查报告 + fix-plan |
| **构建阶段** | `sumeru-finalize` | Build 前质量门禁（�?review 指标，但不修改章节） | `build-quality-report.md` + 平台适配建议 |

## 核心指标定义

| 指标 | 阈�?| 适用范围 |
|------|------|----------|
| �?00字冲突启�?| �?00�?| �?�?|
| �?00字无设定铺陈 | 0�?| �?�?|
| 结尾钩子 | 每章必须�?| �?-3章强制，其余建议 |
| 对话占比 | �?5% | 全部章节 |
| 内心独白占比 | �?0% | 全部章节 |
| 纯描写占�?| �?5% | 全部章节 |
| 核心事件�?| �?�?�?| 全部章节 |
| 连续低密�?| �?�?| 全部章节 |

---

# 第十四部分：质量检�?
执行任一 Skill 后检查：

1. 预期输出文件是否生成
2. `.sumeru/` 结构化数据与用户可见输出是否一�?3. 章节文件按三位编号排序，无缺�?重章
4. 修改�?Skill 是否生成备份和变更记�?5. 写作/重写/润色后是否通过 SUMERU_STATUS �?continuity cache 校验
6. 发布导出是否剥离 SUMERU_STATUS 注释

---

# 第十五部分：脚本索引

| 脚本 | 所�?Skill | 功能 |
|------|-----------|------|
| `sumeru-review/scripts/continuity-check.py` | review | 剧情一致性检�?|
| `sumeru-review/scripts/foreshadowing-tracker.py` | review | 伏笔生命周期追踪 |
| `sumeru-review/scripts/chapter-word-counter.py` | review | 章节字数统计 |
| `sumeru-finalize/scripts/spell-check.py` | finalize | 错别字检�?|
| `sumeru-finalize/scripts/sensitive-word-filter.py` | finalize | 敏感词检�?|
| `sumeru-finalize/scripts/format-validator.py` | finalize | 格式校验 |
| `sumeru-finalize/scripts/platform-export.py` | finalize | 平台格式导出 |
