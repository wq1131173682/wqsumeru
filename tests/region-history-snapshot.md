# 行区历史比对：`skills/wq-rules/SKILL.md` L149-L158

锚点：`批次间串行摘要`

| 提交 | 日期 | 主题 | 该区行数 | 数字总数 | 损坏字符数 |
|---|---|---|---|---|---|
| `a5d71c8` | 2026-09-07 | feat: v1.5.0 五大瓶颈优化（Token/耗时减半） | 10 | 31 | 6 |
| `8af6f1d` | 2026-09-07 | feat: v1.4.9 context pack 预算压缩 + | 10 | 31 | 6 |
| `d9cf3d5` | 2026-09-04 | fix(rules): 所有技能显式声明 requires: [ | 10 | 31 | 6 |
| `24c609d` | 2026-09-04 | fix(finalize): 字数门槛降级为警告（v1.4.5） | 10 | 31 | 6 |
| `c69ff7d` | 2026-09-04 | feat: 字数门槛硬化 + 轻量修稿路径 v1.4.4 | 10 | 31 | 6 |
| `27249f7` | 2026-09-03 | feat: 整体优化 v1.4.2 — 修订后回归门/质量闭环/ | 10 | 31 | 6 |
| `17a9c56` | 2026-08-28 | fix(write): 修复子Agent 写入 nul 文件问题 | 10 | 31 | 6 |
| `0dd9024` | 2026-08-26 | fix: 子Agent并行上限5→3，新增禁止嵌套调度规则 | 10 | 31 | 6 |
| `e36ca1e` | 2026-08-13 | fix: 系统性 bug 审查与修复 — 11 项问题修复 | 10 | 31 | 6 |
| `406be85` | 2026-08-06 | feat: rebrand sumeru-* to wq-* s | 10 | 31 | 6 |

## 各版本该区原文

### `406be85` (2026-08-06) — feat: rebrand sumeru-* to wq-* s

```text
L139: ## 批次间串行摘要
L140: 每批子Agent完成后，父Agent生成"实际摘要"（≤300字），作为下一批 context pack 的输入。context pack 中只保留最近3 批摘要，更早的合并为一行概述。
L141: **摘要格式**（纯事实列表）：
L142: ```
L143: ## 批次摘要: 第-6章- 事件：主角觉醒系统001)、通过宗门考核(003)、击败外门弟存005)
L144: - 人物：主角练气三层→五层，苏瑾轻伤恢复，赵无极首次出在- 道具：黑色残片归主角，回春丹消者构- 伏笔：v1黑衣人身从mentioned)，v2残片来历(active)
L145: - 情绪：压抑→突破→暗爆```
L146: 
L147: **存储位置（< 150 章）**：`.sumeru/continuity/batch-summaries/batch-001.md`、`batch-002.md`...
L148: **存储位置（≥ 150 章，分卷模式）**：`.sumeru/volumes/vol-N/continuity/batch-summaries/batch-001.md`...
```

### `e36ca1e` (2026-08-13) — fix: 系统性 bug 审查与修复 — 11 项问题修复

```text
L139: ## 批次间串行摘要
L140: 每批子Agent完成后，父Agent生成"实际摘要"（≤300字），作为下一批 context pack 的输入。context pack 中只保留最近3 批摘要，更早的合并为一行概述。
L141: **摘要格式**（纯事实列表）：
L142: ```
L143: ## 批次摘要: 第-6章- 事件：主角觉醒系统001)、通过宗门考核(003)、击败外门弟存005)
L144: - 人物：主角练气三层→五层，苏瑾轻伤恢复，赵无极首次出在- 道具：黑色残片归主角，回春丹消者构- 伏笔：v1黑衣人身从mentioned)，v2残片来历(active)
L145: - 情绪：压抑→突破→暗爆```
L146: 
L147: **存储位置（< 150 章）**：`.sumeru/continuity/batch-summaries/batch-001.md`、`batch-002.md`...
L148: **存储位置（≥ 150 章，分卷模式）**：`.sumeru/volumes/vol-N/continuity/batch-summaries/batch-001.md`...
```

### `0dd9024` (2026-08-26) — fix: 子Agent并行上限5→3，新增禁止嵌套调度规则

```text
L140: ## 批次间串行摘要
L141: 每批子Agent完成后，父Agent生成"实际摘要"（≤300字），作为下一批 context pack 的输入。context pack 中只保留最近3 批摘要，更早的合并为一行概述。
L142: **摘要格式**（纯事实列表）：
L143: ```
L144: ## 批次摘要: 第-6章- 事件：主角觉醒系统001)、通过宗门考核(003)、击败外门弟存005)
L145: - 人物：主角练气三层→五层，苏瑾轻伤恢复，赵无极首次出在- 道具：黑色残片归主角，回春丹消者构- 伏笔：v1黑衣人身从mentioned)，v2残片来历(active)
L146: - 情绪：压抑→突破→暗爆```
L147: 
L148: **存储位置（< 150 章）**：`.sumeru/continuity/batch-summaries/batch-001.md`、`batch-002.md`...
L149: **存储位置（≥ 150 章，分卷模式）**：`.sumeru/volumes/vol-N/continuity/batch-summaries/batch-001.md`...
```

### `17a9c56` (2026-08-28) — fix(write): 修复子Agent 写入 nul 文件问题

```text
L140: ## 批次间串行摘要
L141: 每批子Agent完成后，父Agent生成"实际摘要"（≤300字），作为下一批 context pack 的输入。context pack 中只保留最近3 批摘要，更早的合并为一行概述。
L142: **摘要格式**（纯事实列表）：
L143: ```
L144: ## 批次摘要: 第-6章- 事件：主角觉醒系统001)、通过宗门考核(003)、击败外门弟存005)
L145: - 人物：主角练气三层→五层，苏瑾轻伤恢复，赵无极首次出在- 道具：黑色残片归主角，回春丹消者构- 伏笔：v1黑衣人身从mentioned)，v2残片来历(active)
L146: - 情绪：压抑→突破→暗爆```
L147: 
L148: **存储位置（< 150 章）**：`.sumeru/continuity/batch-summaries/batch-001.md`、`batch-002.md`...
L149: **存储位置（≥ 150 章，分卷模式）**：`.sumeru/volumes/vol-N/continuity/batch-summaries/batch-001.md`...
```

### `27249f7` (2026-09-03) — feat: 整体优化 v1.4.2 — 修订后回归门/质量闭环/

```text
L147: ## 批次间串行摘要
L148: 每批子Agent完成后，父Agent生成"实际摘要"（≤300字），作为下一批 context pack 的输入。context pack 中只保留最近3 批摘要，更早的合并为一行概述。
L149: **摘要格式**（纯事实列表）：
L150: ```
L151: ## 批次摘要: 第-6章- 事件：主角觉醒系统001)、通过宗门考核(003)、击败外门弟存005)
L152: - 人物：主角练气三层→五层，苏瑾轻伤恢复，赵无极首次出在- 道具：黑色残片归主角，回春丹消者构- 伏笔：v1黑衣人身从mentioned)，v2残片来历(active)
L153: - 情绪：压抑→突破→暗爆```
L154: 
L155: **存储位置（< 150 章）**：`.sumeru/continuity/batch-summaries/batch-001.md`、`batch-002.md`...
L156: **存储位置（≥ 150 章，分卷模式）**：`.sumeru/volumes/vol-N/continuity/batch-summaries/batch-001.md`...
```

### `c69ff7d` (2026-09-04) — feat: 字数门槛硬化 + 轻量修稿路径 v1.4.4

```text
L147: ## 批次间串行摘要
L148: 每批子Agent完成后，父Agent生成"实际摘要"（≤300字），作为下一批 context pack 的输入。context pack 中只保留最近3 批摘要，更早的合并为一行概述。
L149: **摘要格式**（纯事实列表）：
L150: ```
L151: ## 批次摘要: 第-6章- 事件：主角觉醒系统001)、通过宗门考核(003)、击败外门弟存005)
L152: - 人物：主角练气三层→五层，苏瑾轻伤恢复，赵无极首次出在- 道具：黑色残片归主角，回春丹消者构- 伏笔：v1黑衣人身从mentioned)，v2残片来历(active)
L153: - 情绪：压抑→突破→暗爆```
L154: 
L155: **存储位置（< 150 章）**：`.sumeru/continuity/batch-summaries/batch-001.md`、`batch-002.md`...
L156: **存储位置（≥ 150 章，分卷模式）**：`.sumeru/volumes/vol-N/continuity/batch-summaries/batch-001.md`...
```

### `24c609d` (2026-09-04) — fix(finalize): 字数门槛降级为警告（v1.4.5）

```text
L147: ## 批次间串行摘要
L148: 每批子Agent完成后，父Agent生成"实际摘要"（≤300字），作为下一批 context pack 的输入。context pack 中只保留最近3 批摘要，更早的合并为一行概述。
L149: **摘要格式**（纯事实列表）：
L150: ```
L151: ## 批次摘要: 第-6章- 事件：主角觉醒系统001)、通过宗门考核(003)、击败外门弟存005)
L152: - 人物：主角练气三层→五层，苏瑾轻伤恢复，赵无极首次出在- 道具：黑色残片归主角，回春丹消者构- 伏笔：v1黑衣人身从mentioned)，v2残片来历(active)
L153: - 情绪：压抑→突破→暗爆```
L154: 
L155: **存储位置（< 150 章）**：`.sumeru/continuity/batch-summaries/batch-001.md`、`batch-002.md`...
L156: **存储位置（≥ 150 章，分卷模式）**：`.sumeru/volumes/vol-N/continuity/batch-summaries/batch-001.md`...
```

### `d9cf3d5` (2026-09-04) — fix(rules): 所有技能显式声明 requires: [

```text
L147: ## 批次间串行摘要
L148: 每批子Agent完成后，父Agent生成"实际摘要"（≤300字），作为下一批 context pack 的输入。context pack 中只保留最近3 批摘要，更早的合并为一行概述。
L149: **摘要格式**（纯事实列表）：
L150: ```
L151: ## 批次摘要: 第-6章- 事件：主角觉醒系统001)、通过宗门考核(003)、击败外门弟存005)
L152: - 人物：主角练气三层→五层，苏瑾轻伤恢复，赵无极首次出在- 道具：黑色残片归主角，回春丹消者构- 伏笔：v1黑衣人身从mentioned)，v2残片来历(active)
L153: - 情绪：压抑→突破→暗爆```
L154: 
L155: **存储位置（< 150 章）**：`.sumeru/continuity/batch-summaries/batch-001.md`、`batch-002.md`...
L156: **存储位置（≥ 150 章，分卷模式）**：`.sumeru/volumes/vol-N/continuity/batch-summaries/batch-001.md`...
```

### `8af6f1d` (2026-09-07) — feat: v1.4.9 context pack 预算压缩 +

```text
L147: ## 批次间串行摘要
L148: 每批子Agent完成后，父Agent生成"实际摘要"（≤300字），作为下一批 context pack 的输入。context pack 中只保留最近3 批摘要，更早的合并为一行概述。
L149: **摘要格式**（纯事实列表）：
L150: ```
L151: ## 批次摘要: 第-6章- 事件：主角觉醒系统001)、通过宗门考核(003)、击败外门弟存005)
L152: - 人物：主角练气三层→五层，苏瑾轻伤恢复，赵无极首次出在- 道具：黑色残片归主角，回春丹消者构- 伏笔：v1黑衣人身从mentioned)，v2残片来历(active)
L153: - 情绪：压抑→突破→暗爆```
L154: 
L155: **存储位置（< 150 章）**：`.sumeru/continuity/batch-summaries/batch-001.md`、`batch-002.md`...
L156: **存储位置（≥ 150 章，分卷模式）**：`.sumeru/volumes/vol-N/continuity/batch-summaries/batch-001.md`...
```

### `a5d71c8` (2026-09-07) — feat: v1.5.0 五大瓶颈优化（Token/耗时减半）

```text
L147: ## 批次间串行摘要
L148: 每批子Agent完成后，父Agent生成"实际摘要"（≤300字），作为下一批 context pack 的输入。context pack 中只保留最近3 批摘要，更早的合并为一行概述。
L149: **摘要格式**（纯事实列表）：
L150: ```
L151: ## 批次摘要: 第-6章- 事件：主角觉醒系统001)、通过宗门考核(003)、击败外门弟存005)
L152: - 人物：主角练气三层→五层，苏瑾轻伤恢复，赵无极首次出在- 道具：黑色残片归主角，回春丹消者构- 伏笔：v1黑衣人身从mentioned)，v2残片来历(active)
L153: - 情绪：压抑→突破→暗爆```
L154: 
L155: **存储位置（< 150 章）**：`.sumeru/continuity/batch-summaries/batch-001.md`、`batch-002.md`...
L156: **存储位置（≥ 150 章，分卷模式）**：`.sumeru/volumes/vol-N/continuity/batch-summaries/batch-001.md`...
```
