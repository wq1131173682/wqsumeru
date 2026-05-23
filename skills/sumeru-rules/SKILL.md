---
name: sumeru-rules
description: 须弥写作全局约束规则。包含父Agent/子Agent职责划分、状态标记格式、Context Pack格式、独立调用自举、剧情一致性冲突检测、伏笔管理、输出级别等所有Skill共享的全局约束。
type: skill
---

# 须弥写作全局约束规则

所有须弥写作 Skill 必须遵守以下规则。规则按角色拆分：子Agent用精简版 `subagent-rules.md`，父Agent读本文件。

---

## 一、子Agent并行处理规则

| 规则 | 说明 |
|------|------|
| **适用范围** | 章节写作、章节重写、剧情审查、轻量修复、内容润色、完稿校验、平台导出、章节细纲生成 |
| **核心原则** | 写正文必须走子agent，单章续写也必须走子agent，父agent绝不写正文 |
| **并行上限** | 最多 5 个子agent同时运行 |
| **分片约束** | 每个子Agent最多负责 3 个连续章节 |
| **计算公式** | 所需Agent数 = `min(ceil(总章节数 / 3), 5)` |
| **分配策略** | 按章节顺序连续分组（1-3、4-6、7-9...） |
| **上下文约束** | 每个子Agent只接收完成任务所需的精简上下文 |

### 批次间串行摘要

每批子Agent完成后，父Agent生成"实际摘要"（≤300字），作为下一批 context pack 的输入。context pack 中只保留最近 3 批摘要，更早的合并为一行概述。

**摘要格式**（纯事实列表）：
```
## 批次摘要: 第1-6章
- 事件：主角觉醒系统(001)、通过宗门考核(003)、击败外门弟子(005)
- 人物：主角练气三层→五层，苏瑾轻伤恢复，赵无极首次出场
- 道具：黑色残片归主角，回春丹消耗2枚
- 伏笔：v1黑衣人身份(mentioned)，v2残片来历(active)
- 情绪：压抑→突破→暗爽
```

**存储位置**：`.sumeru/continuity/batch-summaries/batch-001.md`、`batch-002.md`...

---

## 二、子Agent职责边界规则

**核心原则：子Agent只做单一核心任务，所有状态维护、文件写入、缓存刷新、汇总合并均由父Agent统一处理。**

### 父Agent职责

| 职责 | 说明 |
|------|------|
| 自举 & 环境准备 | 定位项目、读/生成 project.json、status.json、补齐目录 |
| Context pack 生成 | 集中生成 context pack，控制 1500-3000 中文字，分发给各子Agent |
| Cache 摘要读取 | 集中读取 L1 cache 摘要 |
| 任务卡读取 | 集中读取目标章节任务卡，仅提取本组章节所需字段 |
| 任务分发 | 启动 N 个子Agent，每个传入精简 context pack |
| 结果汇总 | 收集所有子Agent输出，检查完整性、顺序、命名 |
| 文件写入 | 统一写入输出文件，避免并发冲突 |
| 备份 | 修改前将原文件备份到 `.sumeru/write/original/`，每章仅保留最近 1 份 |
| 状态更新 | 统一更新 `.sumeru/status.json`（章节状态、阶段状态） |
| 缓存刷新 | 统一刷新相关 cache 摘要 |
| 日志记录 | 统一追加 `.sumeru/changelog.md`、`.sumeru/decisions.md` |
| Issue/测试汇总 | 合并各子Agent发现的问题，写入 `.sumeru/issues.md` |

### 子Agent职责

| 职责 | 说明 |
|------|------|
| 只读 context pack | 不读取 context pack 外的任何文件 |
| 执行核心任务 | 根据 context pack 完成任务卡/审查/润色要求 |
| 输出纯结果 | 纯文本结果，不含状态更新指令 |
| 不碰状态 | 不更新 status.json、changelog、cache、issues |
| 输出状态标记 | 正文/细纲首行必须包含 `<!-- SUMERU_STATUS: ... -->` |

---

## 三、子Agent输出状态标记

每个子Agent的输出首行固定包含状态标记，父Agent提取并更新状态文件，避免单点故障。

### 格式

```markdown
<!-- SUMERU_STATUS: chapter=037, status=drafted, state_diff={"location_change":{"苏瑾":"北域冰原"},"state_change":{"苏瑾":"minor_injury"},"item_change":{"黑色残片":"acquired"}}, char_update={"苏瑾":{"status":"minor_injury","location":"北域冰原"},"主角":{"status":"healthy","buff":"龙血狂暴","remaining":"3天"}}, plot_update={"foreshadowing":{"v3":"黑衣人身份暗示推进"}}, batch=002, timestamp=2026-05-18T10:30:00Z -->
```

### 字段说明

| 字段 | 含义 | 格式 |
|------|------|------|
| `chapter` | 章节号 | 字符串 |
| `status` | 章节状态 | `drafted` / `polished` / `finalized` |
| `state_diff` | 结构化状态变化 | JSON 对象 |
| `char_update` | 人物当前状态 | JSON 对象 |
| `plot_update` | 伏笔线推进 | JSON 对象 |
| `batch` | 所属批次号 | 字符串 |
| `timestamp` | 生成时间 | ISO 8601 |

### state_diff 分类

```json
{
  "location_change": {"人物名": "新地点"},
  "state_change": {"人物名": "新健康状态"},
  "power_change": {"人物名": "新战力等级"},
  "item_change": {"道具名": "acquired|destroyed|transferred"},
  "foreshadow_change": {"伏笔ID": "mentioned|resolved"},
  "buff_change": {"人物名": "buff描述|expired"}
}
```

各分类键可选，只包含本章有变化的分类。`state_diff` 必须是合法 JSON 单行。

### 关键约束

- 状态标记必须在输出**第一行**
- 标记缺失、JSON 不合法、章节号不匹配时，不得更新状态文件

### 父Agent处理流程

1. 提取每章的 `<!-- SUMERU_STATUS -->` 标记
2. 解析 `state_diff` 更新 `.sumeru/continuity/consistency-rules.json`
3. 解析 `char_update` 更新人物状态
4. 将 `status` 写入 `.sumeru/status.json`
5. 重启后扫描 `chapters/*.md` 标记即可重建状态

---

## 四、子Agent调用协议

父Agent将 context pack 写入 `.sumeru/context-packs/<task>-<range>.md`，通过 Task tool 的 prompt 指示子Agent只读取该文件。子Agent只返回文本结果，不写项目文件。

**沙箱约束：** 子Agent只能读 context pack，不能写项目文件，不能搜索项目目录。

---

## 五、Context Pack 格式

控制在 **1500-3000 中文字**，最多 5000 字。

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

## 本章执行提醒 (≤5条, 可选)
具体可执行的过程提醒，如"主角必须主动选择"、"第15段附近制造反转"。

## Batch Summary (仅非第一批)
前N批实际摘要（≤500字）。

## Output Requirements
文件命名、状态更新需求（由父agent执行）。
```

### 分层摘要缓存

context pack 中嵌入可用缓存的键列表，子Agent可在输出中标记需要补充的缓存：

```
【可用缓存的键】：char:主角, char:反派, plotline:v1, plotline:v2, world:current, prev:actual, arc:001-003
```

### 具象标杆（polish 专属）

polish 子Agent的 context pack 须嵌入已确认的好段落作为风格标杆：

```
【风格标杆】--打斗标杆(第003章)--原文/润色 --对话标杆(第005章)--原文/润色 --情绪标杆(第008章)--原文/润色
```

---

## 六、独立调用自举协议

任何 Skill 单独启动时必须执行：

1. **定位项目**：从当前目录向上查找 `.sumeru/project.json` / `plan.md` / `outline.md` / `chapters/` / `outlines/`
2. **识别版本**：存在 `.sumeru/project.json` 按新协议，否则进入兼容模式
3. **最小初始化**：缺配置时根据已有文件生成最小配置
4. **补齐目录**：按需创建 `.sumeru/cache/` / `context-packs/` / `continuity/` / `issues.md`
5. **兼容输入**：旧版 `.sumeru/outline/chapter-outlines.json` 只读兼容
6. **刷新缓存**：相关 cache 缺失或过期时生成最小摘要
7. **生成 context pack**：缺 context pack 时生成临时 pack
8. **执行并回写**：更新 `.sumeru/status.json`、cache、issue 文件
9. **记录变更**：追加到 `.sumeru/changelog.md` 和 `.sumeru/decisions.md`

### Canonical 路径

| 类型 | 新写入路径 | 旧路径处理 |
|------|------------|------------|
| 项目配置 | `.sumeru/project.json`、`.sumeru/status.json` | 无 |
| 需求/设定/创意 | `plan.md` | `docs/*`、`ideas/*` 只读兼容 |
| 大纲/任务卡 | `outline.md`、`outlines/chapters.json` | `.sumeru/outline/chapter-outlines.json` 只读兼容 |
| 正文 | `chapters/` 或短篇 `story.md` | 无 |
| 问题清单 | `.sumeru/issues.md` | `.sumeru/issues/index.json` 只读兼容 |
| 审查摘要 | `reviews/review-report.md` | 按需生成 |
| 发布产物 | `publish/` | 无 |

### 独立调用原则

- 不要求先运行 worldbuilder
- 能从现有文件推断的信息不重复询问
- 缺信息但不阻塞任务时用合理默认值
- 不因缓存/context pack 缺失而失败

---

## 七、项目配置 Schema

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
  "outputLevel": "quiet",
  "createdAt": "2026-05-16T00:00:00Z",
  "updatedAt": "2026-05-16T00:00:00Z"
}
```

**阶段状态：** `pending` / `in_progress` / `blocked` / `completed` / `skipped`

**章节状态：** `planned` / `drafted` / `reviewed` / `fixed` / `polished` / `finalized` / `exported`

---

## 八、各 Skill 子Agent职责明细

| Skill | 子Agent核心任务 | 子Agent输入 | 子Agent输出 | 父Agent后续处理 |
|-------|----------------|------------|------------|----------------|
| **sumeru-write** | 按任务卡写正文 | context pack（任务卡+上一章结尾+剧情事实基准+人物/道具/伏笔状态） | 纯正文 + 状态标记 | 剧情统一校验→写入 chapters/→备份→更新 status→刷新 continuity cache |
| **sumeru-review** | 按任务卡审查章节 | context pack（任务卡+正文+审查标准+consistency-rules） | 审查结论（问题列表+严重程度+证据+建议） | 合并问题写入 issues.md，按需生成 review report，制定 fix-plan |
| **sumeru-polish** | 按标准润色章节 | context pack（正文+style-brief+creative-brief+审查问题+具象标杆） | 润色后正文 + 状态标记 | 备份后直接写入最终正文，更新 status→polished |
| **sumeru-outline** | 生成章节细纲 | context pack（世界观+人物+分卷大纲+上下文关联） | 章节细纲 JSON/Markdown + 状态标记 | 合并校验→写入 outlines/chapters.json→刷新 cache |
| **sumeru-finalize** | 脚本预处理 + 待定项判断 | 脚本扫描结果（待定项列表，最多20个） | 待定项处理建议 | 汇总建议→最终校验→写入 publish/→build-manifest |

---

## 九、修改边界

- `sumeru-review` 直接修复错别字、轻微逻辑补丁、字数不足，不大量重写
- `sumeru-polish` 优化文笔/节奏/对话/爽点，不改变主线事实和角色关系
- `sumeru-finalize` 专注技术校验和发布格式，不承担剧情重构
- 下游 Skill 不直接调用上游；需返工时输出结构化计划
- 正文修改默认产出最终版，修改前保留最小备份

---

## 十、质量检查

执行任一 Skill 后检查：

1. 预期输出文件是否生成
2. `.sumeru/` 结构化数据与用户可见输出是否一致
3. 章节文件按三位编号排序，无缺章/重章
4. 修改型 Skill 是否生成备份和变更记录
5. 写作/重写/润色后是否通过 SUMERU_STATUS 与 continuity cache 校验
6. 发布导出是否剥离 SUMERU_STATUS 注释

---

## 十一、剧情统一与一致性冲突检测

所有写作/重写/润色必须先校验剧情事实再写入。

### 剧情统一门禁

父Agent写入前检查：

1. **承接检查**：本章必须承接上一章实际结尾
2. **人物检查**：位置、伤势、战力、关系与 consistency-rules.json 一致
3. **道具检查**：归属、消耗、损坏状态一致
4. **时间线检查**：事件顺序不倒置；回忆/梦境/插叙显式标记
5. **伏笔检查**：已回收伏笔不重新 active；新伏笔有 ID/首次章节/预期回收方向
6. **任务卡检查**：不违反 `protectedElements` 和 `acceptanceCriteria`

**处理规则：** critical/high 冲突→暂停写入，写 issue 等待仲裁；medium→允许草稿但标记待修复；low→自动修复或记入 changelog

### 冲突检测规则

| 规则ID | 描述 | 严重程度 |
|--------|------|----------|
| `unique_location` | 同一人物不能同时在两个地点 | critical |
| `destroyed_item_used` | 已毁道具不能再次使用 | critical |
| `foreshadowing_recycled` | 已回收伏笔不能再次 active | high |
| `character_state_regression` | 人物状态不能无原因回退 | high |
| `power_level_consistency` | 战力等级不能无原因跳跃 | medium |
| `timeline_order` | 事件时间线必须有序 | high |

### 检查脚本

```bash
python scripts/continuity-check.py .sumeru/continuity --output continuity-report.json
python scripts/foreshadowing-tracker.py .sumeru/continuity 50 --output foreshadowing-report.json
```

---

## 十二、伏笔管理

### 伏笔状态流转

`设置(active) → 推进(mentioned) → 回收(resolved)`，期望回收章节已过时自动提醒

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
- **数量控制**：活跃超过10个时建议回收低优先级
- **新伏笔规划**：近期设置多个新伏笔时规划回收时间

---

## 十三、输出级别规范

| 级别 | 说明 | 适用场景 |
|------|------|----------|
| `quiet` | 只输出进度和关键节点 | **默认**，日常创作 |
| `normal` | 输出进度 + 阶段总结 + 问题提醒 | 用户明确要求 |
| `verbose` | 完整输出所有中间报告 | 调试/审查 |

**quiet 模式只输出：** 阶段开始/完成通知、进度条、错误和警告、1-2 行阶段总结。不输出脚本详细输出、中间报告、技术细节。

---

## 十四、写作安全与原创性

- 避免直接复刻现实公众人物、真实组织、地名、知名 IP 角色
- 参考作品时只学节奏和类型结构，不抄具体内容
- 涉及敏感内容时优先合规化改写并说明风险
