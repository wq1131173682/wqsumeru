---
name: sumeru-rules
description: 须弥写作全局约束规则。包含父Agent/子Agent职责划分、状态标记格式、Context Pack格式、独立调用自举、剧情一致性冲突检测、伏笔管理、输出级别等所有Skill共享的全局约束。规则拆分为 global-rules.md（父Agent）+ subagent-rules.md（子Agent精简版）。
type: skill
---

# 须弥写作全局约束规则

> ⚠️ **重要**：所有须弥写作 Skill 都必须遵守以下全局约束。单独调用任意 Skill 时，请确保已加载本规则。

> 📌 **规则拆分**：本文件为总索引。详细规则已拆分为：
> - **`global-rules.md`** — 父Agent（调度器）完整规则，包含子Agent管理、状态维护、文件写入、剧情统一校验等
> - **`subagent-rules.md`** — 子Agent精简版规则，只包含子Agent需要的核心约束

---

## 一、子Agent并行处理规则

所有涉及章节级批量操作的 Skill 必须遵守：

| 规则 | 说明 |
|------|------|
| **适用范围** | 章节写作、章节重写、剧情审查、轻量修复、内容润色、完稿校验、平台导出、章节细纲生成 |
| **核心原则** | 写正文必须走子agent，单章续写也必须走子agent，父agent绝不写正文 |
| **并行上限** | 最多 5 个子agent同时运行 |
| **分片约束** | 每个子Agent最多负责 3 个连续章节 |
| **计算公式** | 所需Agent数 = `min(ceil(总章节数 / 3), 5)` |
| **分配策略** | 按章节顺序连续分组（1-3、4-6、7-9...） |
| **上下文约束** | 每个子Agent只接收完成任务所需的精简上下文，避免把全书正文塞入单个上下文 |

### 批次间串行摘要（长篇连贯性保障）

每批子Agent完成后，父Agent生成"实际摘要"（≤300字），作为下一批 context pack 的输入。

**滚动窗口策略**：context pack 中只保留**最近 3 批**摘要，更早的摘要合并为一行概述。

```
第 1 批（并行）: 子Agent A 写 1-3章 + 子Agent B 写 4-6章
                  ↓ 父Agent生成"1-6章实际摘要"（≤300字）
第 2 批（并行）: 子Agent C 写 7-9章 + 子Agent D 写 10-12章
                  ↓ 父Agent生成"7-12章实际摘要"（≤300字）
第 3 批（并行）: 子Agent E 写 13-15章 + 子Agent F 写 16-18章
                  （context pack 中包含：第1批概述 + 第2批摘要 + 第3批无）
```

**摘要格式**（纯事实列表，不含描写，严控字数）：
```
## 批次摘要: 第1-6章
- 事件：主角觉醒系统(001)、通过宗门考核(003)、击败外门弟子(005)
- 人物：主角练气三层→五层，苏瑾轻伤恢复，赵无极首次出场
- 道具：黑色残片归主角，回春丹消耗2枚
- 伏笔：v1黑衣人身份(mentioned)，v2残片来历(active)
- 情绪：压抑→突破→暗爽
```

**存储位置**：`.sumeru/continuity/batch-summaries/batch-001.md`、`batch-002.md`...
**Context Pack 中只嵌入最近 3 批**，更早的合并为 `## 历史概述（第1-N章）: <一句话概括>`

---

## 二、子Agent职责边界规则

**核心原则：子Agent只做"单一核心任务"，所有状态维护、文件写入、缓存刷新、汇总合并均由父Agent（调度器）统一处理。**

### 父Agent（调度器）职责

| 职责 | 说明 |
|------|------|
| 自举 & 环境准备 | 定位项目、读/生成 project.json、status.json、补齐目录 |
| Context pack 生成 | 集中生成 context pack，控制 1500-3000 中文字，分发给各子Agent |
| Cache 摘要读取 | 集中读取 L1 cache 摘要（project-brief、style-brief、creative-brief、continuity-brief 等） |
| 任务卡读取 | 集中读取目标章节任务卡（outlines/chapters/*.json），仅提取本组章节所需字段 |
| 任务分发 | 启动 N 个子Agent，每个传入精简 context pack |
| 结果汇总 | 收集所有子Agent输出，检查完整性、顺序、命名 |
| 文件写入 | 统一写入输出文件（chapters/、outlines/、reviews/ 等），避免并发冲突 |
| 备份 | 修改前将原文件备份到 `.sumeru/write/original/`，默认每章仅保留最近 1 份 |
| 状态更新 | 统一更新 `.sumeru/status.json`（章节状态、阶段状态） |
| 缓存刷新 | 统一刷新相关 cache 摘要 |
| 日志记录 | 统一追加 `.sumeru/changelog.md`、`.sumeru/decisions.md` |
| Issue/测试汇总 | 合并各子Agent发现的问题，写入 `.sumeru/issues.md`；`tests/` 按需生成 |

### 子Agent（执行器）职责

| 职责 | 说明 |
|------|------|
| 只读 context pack | 不读取任何额外文件，context pack 外的一切文件访问均视为违规 |
| 执行核心任务 | 根据 context pack 中的任务卡/审查标准/润色要求，完成单一核心任务 |
| 输出纯结果 | 输出纯文本结果（正文、审查结论、润色后文本、细纲），不包含状态更新指令 |
| 不碰状态 | 不更新 status.json、不写 changelog、不刷 cache、不写 issues |
| **输出状态标记** | **正文/细纲首行必须包含 `<!-- SUMERU_STATUS: ... -->` 注释** |

---

## 三、子Agent输出状态标记

**问题**：父Agent集中维护状态存在单点故障风险，父Agent崩溃时状态文件可能损坏。

**解决方案**：每个子Agent的输出首行固定包含状态标记注释，父Agent只需提取标记并追加写入。

### 格式规范

```markdown
<!-- SUMERU_STATUS: chapter=037, status=drafted, state_diff={"location_change":{"苏瑾":"北域冰原"},"state_change":{"苏瑾":"minor_injury"},"item_change":{"黑色残片":"acquired"}}, char_update={"苏瑾":{"status":"minor_injury","location":"北域冰原"},"主角":{"status":"healthy","buff":"龙血狂暴","remaining":"3天"}}, plot_update={"foreshadowing":{"v3":"黑衣人身份暗示推进"}}, batch=002, timestamp=2026-05-18T10:30:00Z -->
```

### 字段说明

| 字段 | 含义 | 格式 | 示例 |
|------|------|------|------|
| `chapter` | 章节号 | 字符串 | `037` |
| `status` | 章节状态 | 枚举值 | `drafted` / `polished` / `finalized` |
| `state_diff` | 结构化状态变化（JSON 片段） | JSON 对象 | 见下方分类说明 |
| `char_update` | 人物当前状态（JSON 对象） | JSON 对象 | `{"苏瑾":{"status":"minor_injury"}}` |
| `plot_update` | 伏笔线推进（JSON 对象） | JSON 对象 | `{"foreshadowing":{"v1":"resolved"}}` |
| `batch` | 所属批次号 | 字符串 | `002` |
| `timestamp` | 生成时间 | ISO 8601 | `2026-05-18T10:30:00Z` |

### state_diff 分类说明

`state_diff` 使用 JSON 对象，按变化类型分类，父Agent可直接解析并更新 `consistency-rules.json` 对应字段：

```json
{
  "location_change": {"人物名": "新地点"},           // → 更新 character_locations
  "state_change": {"人物名": "新健康状态"},            // → 更新 character_state.status
  "power_change": {"人物名": "新战力等级"},            // → 更新 character_state.power_level
  "item_change": {"道具名": "acquired|destroyed|transferred"},  // → 更新 weapons/key_items
  "foreshadow_change": {"伏笔ID": "mentioned|resolved"},        // → 更新 foreshadowing
  "buff_change": {"人物名": "buff描述|expired"}       // → 更新 active_buffs
}
```

- 各分类键可选，只包含本章有变化的分类
- 值为 `{"实体名": "变化描述"}` 的简单映射
- 父Agent按分类键直接写入 `consistency-rules.json` 对应数组，无需自然语言理解

### 关键约束

- 状态标记必须放在输出内容的**第一行**，不能有任何前置文字
- `state_diff` 必须是合法 JSON（单行，无换行符）
- 如果子Agent不确定某个状态变化，可以留空该分类但不能省略整个标记

### 父Agent处理流程

1. 汇总子Agent输出时，提取每章的 `<!-- SUMERU_STATUS -->` 标记
2. 解析 `state_diff` JSON，按分类键更新 `.sumeru/continuity/consistency-rules.json` 对应数组
3. 解析 `char_update` JSON，更新 `.sumeru/continuity/consistency-rules.json` 的 `character_state`
4. 将标记中的 `status` 写入 `.sumeru/status.json` 对应章节
5. 即使父Agent中断，重启后扫描 `chapters/*.md` 的标记即可重建所有状态文件

---

## 四、子Agent调用协议

### 输入传递

父Agent将 context pack 写入临时文件 `.sumeru/context-packs/<task>-<range>.md`，通过 Task tool 的 prompt 参数指示子Agent只读取该文件。

```
父Agent:
  1. 生成 context pack → 写入 .sumeru/context-packs/write-001-003.md
  2. 启动 Task tool，prompt 中包含：
     "请读取 .sumeru/context-packs/write-001-003.md，按其中的任务卡完成第1-3章写作。"
  3. 子Agent读取该文件并执行任务
```

### 输出返回

子Agent只通过任务返回文本结果，不写项目文件。父Agent收到结果后再统一写入正式文件，必要时可由父Agent保存临时 result。

```
子Agent:
  1. 读取 context pack
  2. 执行核心任务
  3. 返回正文/审查结论/润色结果
父Agent:
  4. 提取 SUMERU_STATUS 标记
  5. 校验剧情统一
  6. 将最终结果写入 chapters/ 或报告文件
```

### 沙箱约束

- 子Agent只能读取 context pack 文件（通过 prompt 明确约束："只读取指定的 context pack 文件"）
- 子Agent不写入任何项目文件
- 父Agent负责将结果合并到正式文件（chapters/、outlines/、reviews/ 等）
- 子Agent不应使用 Glob/Grep/Read 工具搜索项目目录

---

## 五、Context Pack 格式

context pack 必须控制在 **1500-3000 中文字**，复杂任务最多不超过 5000 中文字。

### 最小消耗策略

默认只读取完成当前任务所需的最小上下文：

- 单章写作/续写：项目 brief、目标任务卡、上一章实际结尾、相关人物/道具/伏笔状态。
- 1-3 章批量写作：目标任务卡、最近 3 批摘要、必要 continuity，不读全书正文。
- 单段润色：只读用户片段、风格要求、必要术语；不生成 context pack。
- 小范围审查：只读目标章节、前后各 1 章摘要、consistency-rules。
- 完稿导出：只在用户明确完稿/导出时运行，不在普通写作和润色阶段提前触发。

除非用户要求 `verbose` 或“完整报告”，默认不输出中间报告，不展开脚本细节。

### 标准结构

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

## 本章执行提醒（新增）
- 必须在第15段附近制造情绪反转（keyMoment）
- 主角必须主动选择，不能被推着走
- 本章爽点类型：信息差碾压（前3章为：武力碾压、智力碾压、财富碾压 → 检查是否重复）
- 毛边机会点：对手倒下的瞬间，主角的反应可以反常

## Batch Summary (仅非第一批)
前N批实际摘要（≤500字），来自 .sumeru/continuity/batch-summaries/。

## Output Requirements (仅本组章节)
文件命名、状态更新需求（由父agent执行，子agent无需关心）。
```

**本章执行提醒说明：**
- 这不是规则，是"创作过程中的耳语"
- 事后检查治标，过程提醒治本
- 提醒内容要具体、可执行、不超过 5 条

### 分层摘要缓存 + 按需检索

context pack 中嵌入**可用缓存的键列表**，而非全量数据：

```
【可用缓存的键】（子Agent可在输出中标记需要以下缓存内容，父Agent下一轮补充）：
- char:主角        （人物当前状态摘要，约200字）
- char:反派        （人物当前状态摘要，约200字）
- plotline:v1      （伏笔线1摘要，约150字）
- plotline:v2      （伏笔线2摘要，约150字）
- world:current    （当前世界观状态，约100字）
- prev:actual      （上一章实际结尾，约200字）
- arc:001-003      （第1-3章实际摘要，约300字）
```

### 具象标杆（polish 专属）

polish 子Agent的 context pack 中，除了 abstract 的 style-brief，还必须嵌入**具象标杆段落**：

```
【风格标杆】（以下是本项目已写过的"好段落"示例，请以此为标准润色）：
---打斗场景标杆（摘自第003章）---
原文：...
润色后：...
---对话场景标杆（摘自第005章）---
原文：...
润色后：...
---情绪高潮标杆（摘自第008章）---
原文：...
润色后：...
```

---

## 六、独立调用自举协议

用户可能不通过 `sumeru-worldbuilder`，而是直接调用任意 Skill。任何 Skill 单独启动时，都必须执行同一套自举流程。

### 自举流程（9步）

1. **定位项目根目录**：从当前目录向上查找 `.sumeru/project.json`、`.sumeru/status.json`、`plan.md`、`outline.md`、`chapters/`、`outlines/`。找到任一组合即可视为候选项目根。
2. **识别项目版本**：若存在 `.sumeru/project.json`，按新协议执行；若只存在旧版 `.sumeru/outline/chapter-outlines.json` 或 `chapters/`，进入兼容模式。
3. **最小初始化**：缺少 `.sumeru/project.json` 时，根据已有文件生成最小配置；缺少 `.sumeru/status.json` 时，根据 `chapters/`、`outlines/`、`publish/` 推断阶段和章节状态。
4. **补齐目录/文件**：按需创建 `.sumeru/cache/`、`.sumeru/context-packs/`、`.sumeru/continuity/`、`.sumeru/issues.md`。`reviews/`、`tests/` 仅在用户要求报告或完稿检查时创建。不要覆盖用户已有内容。
5. **迁移兼容输入**：若只有 `.sumeru/outline/chapter-outlines.json`，可以继续读取；新写入统一生成 `outlines/chapters.json`。
6. **刷新摘要缓存**：如果相关 cache 缺失或明显过期，先生成最小摘要。
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

### 独立调用原则

- 单独调用 skill 时，不要求用户先运行 worldbuilder
- 能从现有项目文件推断的信息，不重复询问用户
- 缺少关键信息但不阻塞任务时，使用合理默认值
- 缺少关键信息且会影响输出正确性时，只问最少问题
- 不因为缓存缺失而失败；缓存缺失时生成最小缓存
- 不因为 context pack 缺失而全量读取项目；先生成当前任务的 context pack
- 兼容旧项目，但新写入内容应遵守新项目结构

### Canonical 路径协议

新写入只使用以下路径；旧路径只读兼容，不再主动生成：

| 类型 | 新写入路径 | 旧路径处理 |
|------|------------|------------|
| 项目配置 | `.sumeru/project.json`、`.sumeru/status.json` | 无 |
| 需求/设定/创意 | `plan.md` | `docs/*`、`ideas/*` 只读兼容 |
| 大纲/任务卡 | `outline.md`、`outlines/chapters.json` | `.sumeru/outline/chapter-outlines.json` 只读兼容 |
| 正文 | `chapters/` 或短篇 `story.md` | 无 |
| 问题清单 | `.sumeru/issues.md` | `.sumeru/issues/index.json` 只读兼容 |
| 审查摘要 | `reviews/review-report.md` | 按需生成，不做默认全量报告 |
| 发布产物 | `publish/` | 无 |

---

## 七、项目配置 Schema

`.sumeru/project.json` 是全项目唯一配置源。

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

### 阶段状态（只能使用以下值）

`pending`、`in_progress`、`blocked`、`completed`、`skipped`

### 章节状态（只能使用以下值）

`planned`、`drafted`、`reviewed`、`fixed`、`polished`、`finalized`、`exported`

---

## 八、各 Skill 子Agent职责明细

| Skill | 子Agent核心任务 | 子Agent输入 | 子Agent输出 | 父Agent后续处理 |
|-------|----------------|------------|------------|----------------|
| **sumeru-write** | 按任务卡写正文（单章续写也走子agent） | context pack（含任务卡、上一章实际结尾、剧情事实基准、人物/道具/伏笔状态） | 纯正文文本 + 状态标记 | 先做剧情统一校验，通过后写入 chapters/、备份、更新 status、刷新 continuity cache |
| **sumeru-review** | 按任务卡审查章节 | context pack（含任务卡、正文、审查标准、consistency-rules.json） | 审查结论（问题列表、严重程度、证据、建议） | 合并问题写入 `.sumeru/issues.md`，按需生成 review report，制定 fix-plan |
| **sumeru-polish** | 按标准润色章节 | context pack（含正文、style-brief、creative-brief、审查问题、具象标杆） | 润色后正文 + 状态标记 | 备份后直接写入最终正文，更新 status→polished、刷新 continuity cache |
| **sumeru-outline** | 生成章节细纲 | context pack（含世界观、人物、分卷大纲、上下文关联） | 章节细纲 JSON/Markdown + 状态标记 | 合并所有子Agent细纲、校验一致性、写入 outlines/chapters.json、刷新 cache |
| **sumeru-finalize** | 脚本预处理 + 待定项判断 | 脚本扫描结果（待定项列表，最多20个） | 待定项处理建议 | 汇总建议、执行最终校验、写入 publish/、生成 build-manifest |

---

## 九、修改边界

- `sumeru-review` 默认直接修复错别字、轻微逻辑补丁、字数不足补充、局部段落顺序等轻量问题，输出最终可读版本
- `sumeru-review` 不应直接大面积重写章节；严重问题写入 `fix-plan.json`
- `sumeru-polish` 默认直接修改 `chapters/` 做文笔、节奏、对话、爽点优化，但不得改变主线事实、关键设定和角色关系
- `sumeru-finalize` 专注技术性校验和发布格式，不承担剧情重构和文风再创作
- 下游 Skill 不直接调用上游 Skill；需要返工时输出结构化计划

正文修改默认产出最后版本。修改前只保留最小备份和状态记录，不要求用户阅读原文、diff 或中间建议。

### 最小备份策略

- 默认每章覆盖前只保留最近 1 份备份。
- 批量任务保留最近 1 次批次快照。
- 用户明确要求保留历史版本时，才增加长期备份。

---

## 十、质量检查

执行任一 Skill 后，应至少检查：

1. 预期输出文件是否生成
2. `.sumeru/` 中的结构化数据是否与用户可见输出一致
3. 章节文件是否按三位编号排序且没有缺章、重章
4. 修改型 Skill 是否已生成备份和变更记录
5. 报告中是否区分已修复问题、待用户确认问题和需要重写的问题
6. 写作、重写、润色后是否通过剧情统一校验，且 `SUMERU_STATUS` 与 continuity cache 一致
7. 发布导出是否剥离 `SUMERU_STATUS` 注释

---

## 十一、剧情统一与一致性冲突检测

**问题**：多个子Agent并行写作时，可能报告矛盾的 `state_diff`（如一个说"主角在北域"，另一个说"主角在南海"）。

**解决方案**：建立剧情统一门禁和冲突检测规则库。所有写作、重写、润色都必须先校验剧情事实，再写入正式章节。

### 剧情统一门禁

父Agent在写入 `chapters/` 前必须完成以下检查：

1. **承接检查**：本章开头和事件推进必须承接上一章实际结尾，不得跳过关键状态变化。
2. **人物检查**：人物位置、伤势、战力、关系、情绪状态必须与 `.sumeru/continuity/consistency-rules.json` 一致。
3. **道具检查**：关键道具归属、消耗、损坏、转移状态必须一致。
4. **时间线检查**：章节事件顺序不得倒置；回忆、梦境、插叙必须显式标记。
5. **伏笔检查**：已回收伏笔不得重新 active；新伏笔必须有 ID、首次出现章节和预期回收方向。
6. **任务卡检查**：正文不得违反 `protectedElements` 和 `acceptanceCriteria`。

处理规则：
- `critical` 或 `high` 冲突：暂停写入正式章节，写入 issue 或 fix-plan，等待用户确认或重写。
- `medium` 冲突：允许写入草稿，但必须在 review 报告中标记并进入待修复列表。
- `low` 冲突：可自动修复或记录到 changelog。

### 冲突检测规则

| 规则ID | 描述 | 严重程度 | 处理方式 |
|--------|------|----------|----------|
| `unique_location` | 同一人物不能同时在两个地点 | critical | 暂停写入，等待仲裁 |
| `destroyed_item_used` | 已毁道具不能再次使用 | critical | 暂停写入，等待仲裁 |
| `foreshadowing_recycled` | 已回收伏笔不能再次active | high | 标记为issue |
| `character_state_regression` | 人物状态不能无原因回退 | high | 检查治疗情节 |
| `power_level_consistency` | 战力等级不能无原因跳跃 | medium | 提醒检查 |
| `timeline_order` | 事件时间线必须有序 | high | 检查时间线 |

### 状态标记校验

父Agent解析 `SUMERU_STATUS` 时必须执行 schema 校验：

- `chapter` 必须属于当前任务范围。
- `status` 只能使用章节状态枚举。
- `state_diff` 只能包含 `location_change`、`state_change`、`power_change`、`item_change`、`foreshadow_change`、`buff_change`。
- `char_update` 和 `plot_update` 必须是合法 JSON 对象。
- 标记缺失、JSON 不合法、章节号不匹配时，不得更新 `.sumeru/status.json` 和 continuity cache。

### 状态回退检测规则

人物状态回退需有合理情节支撑：

```
healthy → minor_injury → injured → seriously_injured → critical → deceased
   ↑          ↑            ↑              ↑              ↑
   └──────────┴────────────┴──────────────┴──────────────┘
              只能单向恶化，回退需治疗情节
```

### 检查脚本

```bash
# 剧情一致性检查
python scripts/continuity-check.py .sumeru/continuity --output continuity-report.json

# 伏笔追踪
python scripts/foreshadowing-tracker.py .sumeru/continuity 50 --output foreshadowing-report.json
```

## 十二、伏笔管理

**问题**：长篇创作容易忘记回收伏笔，导致剧情漏洞。

**解决方案**：系统化伏笔追踪，自动提醒回收。

### 伏笔状态流转

```
设置(active) → 推进(mentioned) → 回收(resolved)
      ↑                              ↓
      └────────── 过期提醒 ──────────┘
```

### 伏笔字段规范

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

### 伏笔管理建议生成

- **过期提醒**：期望回收章节已过，自动提醒
- **数量控制**：活跃伏笔超过10个时，建议回收低优先级
- **新伏笔规划**：近期设置多个新伏笔时，规划回收时间

## 十三、输出级别规范

**问题**：创作过程中输出过多技术细节，用户只需要知道进度和结果。

**解决方案**：定义三级输出级别，默认使用静默模式。

### 输出级别

| 级别 | 说明 | 适用场景 |
|------|------|----------|
| `quiet` | 只输出进度和关键节点，静默处理中间过程 | **默认**，日常创作 |
| `normal` | 输出进度 + 阶段总结 + 问题提醒 | 用户明确要求 |
| `verbose` | 完整输出所有中间报告和脚本结果 | 调试/审查 |

### Quiet 模式输出规范

**只输出：**
- ✅ 阶段开始/完成通知
- ✅ 进度条（章节号/总数）
- ✅ 错误和警告（只有关键问题）
- ✅ 阶段完成总结（1-2 行）

**不输出：**
- ❌ 脚本详细输出（字数统计、敏感词列表等）
- ❌ 中间报告内容
- ❌ 技术细节（Agent 数量、context pack 内容等）
- ❌ 重复的状态更新

### 输出示例对比

**Verbose（当前）：**
```
🔍 找到 50 个章节文件，正在统计...
📊 统计结果：总章节数: 50, 总字数: 150,000
⚠️ 发现 3 章过短
✅ 字数统计报告已生成：.sumeru/review/word-count-report.json
...
```

**Quiet（推荐）：**
```
📝 写作中... 第 37/50 章 (74%)
```

**有问题时：**
```
⚠️ 第 25 章字数不足（1200 字，建议 2000+）
```

### 阶段完成总结格式

```
✅ 第 N 阶段完成：[阶段名]
   [关键结果，1-2 行]
   → 进入下一阶段：[下一阶段名]
```

示例：
```
✅ 第 3 阶段完成：章节撰写
   已生成 50 章，共 125,000 字
   → 进入下一阶段：逻辑审查
```

### 项目配置

在 `.sumeru/project.json` 中设置：

```json
{
  "outputLevel": "quiet",
  "quiet": {
    "show_progress": true,
    "show_stage_change": true,
    "show_errors_only": true,
    "hide_script_output": true,
    "hide_intermediate_reports": true
  }
}
```

### 脚本 Quiet 模式

所有脚本支持 `--quiet` 参数：

```bash
# Quiet 模式：只输出 JSON，不打印中间信息
python scripts/continuity-check.py .sumeru/continuity --quiet

# Normal 模式：输出进度和摘要
python scripts/continuity-check.py .sumeru/continuity

# Verbose 模式：完整输出
python scripts/continuity-check.py .sumeru/continuity --verbose
```

---

## 十四、写作安全与原创性

- 避免直接复刻现实公众人物、真实组织、真实地名、知名 IP 角色和受版权保护的具体设定
- 用户要求参考某作品时，只学习节奏、类型结构和读者情绪价值，不复用具体人物、世界观、桥段或专有名词
- 涉及敏感、血腥、低俗、未成年人不当内容时，优先进行合规化改写并在报告中说明风险
