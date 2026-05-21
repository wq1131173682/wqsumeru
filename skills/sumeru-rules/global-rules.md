---
name: global-rules
description: 父Agent全局约束规则。包含子Agent管理、状态维护、文件写入、剧情统一校验等父Agent专属职责。
type: skill
---

# 父Agent全局约束规则

> ⚠️ **重要**：这是给父Agent（调度器）看的完整规则。子Agent使用的是精简版 `subagent-rules.md`。

---

## 一、父Agent职责总览

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
| 剧情统一校验 | 写入正式章节前执行剧情统一门禁检查 |

---

## 二、子Agent并行处理规则

所有涉及章节级批量操作的 Skill 必须遵守：

| 规则 | 说明 |
|------|------|
| **适用范围** | 章节写作、章节重写、剧情审查、轻量修复、内容润色、完稿校验、平台导出、章节细纲生成 |
| **核心原则** | 写正文必须走子agent，单章续写也必须走子agent，父agent绝不写正文 |
| **并行上限** | 最多 5 个子agent同时运行 |
| **分片约束** | 每个子Agent最多负责 3 个连续章节 |
| **计算公式** | 所需Agent数 = `min(ceil(总章节数 / 3), 5)` |
| **分配策略** | 按章节顺序连续分组（1-3、4-6、7-9...） |

### 批次间串行摘要（长篇连贯性保障）

每批子Agent完成后，父Agent生成"实际摘要"（≤300字），作为下一批 context pack 的输入。

**滚动窗口策略**：context pack 中只保留**最近 3 批**摘要，更早的摘要合并为一行概述。

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

---

## 三、子Agent调用协议

### 输入传递

1. 父Agent将 context pack 写入临时文件 `.sumeru/context-packs/<task>-<range>.md`
2. 通过 Task tool 的 prompt 参数指示子Agent只读取该文件
3. prompt 中明确约束："只读取指定的 context pack 文件"

### 输出返回

1. 子Agent只通过任务返回文本结果，不写项目文件
2. 父Agent收到结果后统一写入正式文件
3. 必要时可由父Agent保存临时 result

### 沙箱约束

- 子Agent只能读取 context pack 文件
- 子Agent不写入任何项目文件
- 父Agent负责将结果合并到正式文件
- 子Agent不应使用 Glob/Grep/Read 工具搜索项目目录

---

## 四、Context Pack 格式

context pack 必须控制在 **1500-3000 中文字**，复杂任务最多不超过 5000 中文字。

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

## 风格样本（可选，仅当用户提供时）
（从 `.sumeru/style-samples/user-style.md` 读取，如果存在）
- 用词习惯：口语化程度、口头禅、书面/口语比例
- 句式特点：平均句长、断裂句频率、主谓残缺频率
- 对话风格：完整性、潜台词、口头禅、自我纠正
- 情绪表达：直接说情绪 vs 动作承载、情绪矛盾
- 比喻风格：个人化程度、精准度、类型偏好

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

## 五、独立调用自举协议

用户可能不通过 `sumeru-worldbuilder`，而是直接调用任意 Skill。任何 Skill 单独启动时，都必须执行同一套自举流程。

### 自举流程（9步）

1. **定位项目根目录**：从当前目录向上查找 `.sumeru/project.json`、`.sumeru/status.json`、`plan.md`、`outline.md`、`chapters/`、`outlines/`
2. **识别项目版本**：若存在 `.sumeru/project.json` 按新协议执行；否则进入兼容模式
3. **最小初始化**：缺少配置时根据已有文件生成最小配置
4. **补齐目录/文件**：按需创建 `.sumeru/cache/`、`.sumeru/context-packs/`、`.sumeru/continuity/`、`.sumeru/issues.md`
5. **迁移兼容输入**：旧版 `.sumeru/outline/chapter-outlines.json` 只读兼容，新写入统一生成 `outlines/chapters.json`
6. **刷新摘要缓存**：如果相关 cache 缺失或明显过期，先生成最小摘要
7. **生成本次 context pack**：如果直接执行章节级任务且缺少对应 context pack，先生成临时 context pack
8. **执行任务并回写状态**：任务完成后更新 `.sumeru/status.json`、相关 cache、issue/test/manifest 文件
9. **记录变更**：把关键动作追加到 `.sumeru/changelog.md`；涉及创作决策时追加到 `.sumeru/decisions.md`

### Canonical 路径协议

| 类型 | 新写入路径 | 旧路径处理 |
|------|------------|------------|
| 项目配置 | `.sumeru/project.json`、`.sumeru/status.json` | 无 |
| 需求/设定/创意 | `plan.md` | `docs/*`、`ideas/*` 只读兼容 |
| 大纲/任务卡 | `outline.md`、`outlines/chapters.json` | `.sumeru/outline/chapter-outlines.json` 只读兼容 |
| 正文 | `chapters/` 或短篇 `story.md` | 无 |
| 问题清单 | `.sumeru/issues.md` | `.sumeru/issues/index.json` 只读兼容 |
| 审查摘要 | `reviews/review-report.md` | 按需生成 |
| 发布产物 | `publish/` | 无 |

---

## 六、项目配置 Schema

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

## 七、修改边界

- `sumeru-review` 默认直接修复错别字、轻微逻辑补丁、字数不足补充、局部段落顺序等轻量问题
- `sumeru-review` 不应直接大面积重写章节；严重问题写入 `fix-plan.json`
- `sumeru-polish` 默认直接修改 `chapters/` 做文笔、节奏、对话、爽点优化，但不得改变主线事实、关键设定和角色关系
- `sumeru-finalize` 专注技术性校验和发布格式，不承担剧情重构和文风再创作
- 下游 Skill 不直接调用上游 Skill；需要返工时输出结构化计划

### 最小备份策略

- 默认每章覆盖前只保留最近 1 份备份
- 批量任务保留最近 1 次批次快照
- 用户明确要求保留历史版本时，才增加长期备份

---

## 八、质量检查

执行任一 Skill 后，应至少检查：

1. 预期输出文件是否生成
2. `.sumeru/` 中的结构化数据是否与用户可见输出一致
3. 章节文件是否按三位编号排序且没有缺章、重章
4. 修改型 Skill 是否已生成备份和变更记录
5. 报告中是否区分已修复问题、待用户确认问题和需要重写的问题
6. 写作、重写、润色后是否通过剧情统一校验，且 `SUMERU_STATUS` 与 continuity cache 一致
7. 发布导出是否剥离 `SUMERU_STATUS` 注释

---

## 九、剧情统一与一致性冲突检测

### 剧情统一门禁

父Agent在写入 `chapters/` 前必须完成以下检查：

1. **承接检查**：本章开头和事件推进必须承接上一章实际结尾
2. **人物检查**：人物位置、伤势、战力、关系、情绪状态必须与 consistency-rules.json 一致
3. **道具检查**：关键道具归属、消耗、损坏、转移状态必须一致
4. **时间线检查**：章节事件顺序不得倒置；回忆、梦境、插叙必须显式标记
5. **伏笔检查**：已回收伏笔不得重新 active；新伏笔必须有 ID、首次出现章节和预期回收方向
6. **任务卡检查**：正文不得违反 `protectedElements` 和 `acceptanceCriteria`

### 冲突检测规则

| 规则ID | 描述 | 严重程度 | 处理方式 |
|--------|------|----------|----------|
| `unique_location` | 同一人物不能同时在两个地点 | critical | 暂停写入，等待仲裁 |
| `destroyed_item_used` | 已毁道具不能再次使用 | critical | 暂停写入，等待仲裁 |
| `foreshadowing_recycled` | 已回收伏笔不能再次active | high | 标记为issue |
| `character_state_regression` | 人物状态不能无原因回退 | high | 检查治疗情节 |
| `power_level_consistency` | 战力等级不能无原因跳跃 | medium | 提醒检查 |
| `timeline_order` | 事件时间线必须有序 | high | 检查时间线 |

### 状态回退检测规则

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

---

## 十、伏笔管理

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

### 伏笔管理建议

- **过期提醒**：期望回收章节已过，自动提醒
- **数量控制**：活跃伏笔超过10个时，建议回收低优先级
- **新伏笔规划**：近期设置多个新伏笔时，规划回收时间

---

## 十一、输出级别规范

### 输出级别

| 级别 | 说明 | 适用场景 |
|------|------|----------|
| `quiet` | 只输出进度和关键节点 | **默认**，日常创作 |
| `normal` | 输出进度 + 阶段总结 + 问题提醒 | 用户明确要求 |
| `verbose` | 完整输出所有中间报告和脚本结果 | 调试/审查 |

### Quiet 模式输出规范

**只输出：**
- ✅ 阶段开始/完成通知
- ✅ 进度条（章节号/总数）
- ✅ 错误和警告（只有关键问题）
- ✅ 阶段完成总结（1-2 行）

**不输出：**
- ❌ 脚本详细输出
- ❌ 中间报告内容
- ❌ 技术细节（Agent 数量、context pack 内容等）
- ❌ 重复的状态更新

### 脚本 Quiet 模式

所有脚本支持 `--quiet` 参数：

```bash
python scripts/continuity-check.py .sumeru/continuity --quiet
```

---

## 十二、写作安全与原创性

- 避免直接复刻现实公众人物、真实组织、真实地名、知名 IP 角色和受版权保护的具体设定
- 用户要求参考某作品时，只学习节奏、类型结构和读者情绪价值，不复用具体人物、世界观、桥段或专有名词
- 涉及敏感、血腥、低俗、未成年人不当内容时，优先进行合规化改写并在报告中说明风险

---

## 十三、与子Agent规则的关系

| 维度 | global-rules.md（父Agent） | subagent-rules.md（子Agent） |
|------|--------------------------|---------------------------|
| 子Agent并行规则 | ✅ 完整定义 | ✅ 精简引用 |
| 父Agent职责 | ✅ 完整定义 | ❌ 不出现 |
| Context pack 生成 | ✅ 完整定义 | ✅ 使用规则 |
| 状态标记格式 | ✅ 完整定义 | ✅ 精简引用 |
| 剧情统一门禁 | ✅ 完整定义 | ✅ 自查规则 |
| 反AI写作规则 | ✅ 引用 | ✅ 精简版 |
| 风格样本注入 | ✅ 注入流程 | ✅ 模仿要求 |
| 情绪节点验证 | ✅ 完整定义 | ✅ 验证规则 |
| 自动修复策略 | ✅ 完整定义 | ❌ 不出现 |
| 敏感词检测 | ✅ 完整定义 | ❌ 不出现 |
| 平台导出规范 | ✅ 完整定义 | ❌ 不出现 |
