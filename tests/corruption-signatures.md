# 损坏签名检测（机械化可证证据）

扫描：`D:\openclaw\workspace\wqsumeru\skills` 下全部 .md

| # | 文件 | 位置 | 类型 | 说明 | 原文证据 |
|---|---|---|---|---|---|
## 汇总

| 类型 | 数量 |
|---|---|
| PAREN_UNBALANCED | 36 |
| HEADING_MERGED | 5 |
| JSON_INVALID | 2 |
| DIGIT_LOST | 2 |
| EMPTY_TABLE_CELL | 1 |
| QUOTE_UNCLOSED | 1 |

## 明细

### 1. [DIGIT_LOST] `skills/wq-rules/SKILL.md` · L771
- **说明**：数字位缺失，疑似原文为多位数字（现为 '00'）
- **原文**：`\| 前00字冲突启加\| ≥00存\| 第章`

### 2. [DIGIT_LOST] `skills/wq-rules/SKILL.md` · L772
- **说明**：数字位缺失，疑似原文为多位数字（现为 '00'）
- **原文**：`\| 前00字无设定铺陈 \| 0存\| 第章`

### 3. [EMPTY_TABLE_CELL] `skills/wq-migrate/SKILL.md` · L760
- **说明**：表格单元格内容丢失
- **原文**：`\| ... \| \| \| \| \|`

### 4. [HEADING_MERGED] `skills/wq-migrate/SKILL.md` · L18
- **说明**：标题行过长(66 字)，疑似吞并后续行
- **原文**：`### 触发关键词规整项目、迁移旧项目、补齐缺失文件、检查项目完整性、修复项目结构、升级项目格式、旧项目升级、项目检查、查缺补漏、项目规范化`

### 5. [HEADING_MERGED] `skills/wq-outline/SKILL.md` · L368
- **说明**：标题行过长(90 字)，疑似吞并后续行
- **原文**：`### 数据持久化**用户可见输出**）- `plan.md`、`outline.md`、`outlines/chapters.json`、`characters/`、`world.md``

### 6. [HEADING_MERGED] `skills/wq-outline/SKILL.md` · L49
- **说明**：标题行过长(192 字)，疑似吞并后续行
- **原文**：`### 项目化输出要求- `plan.md`：需求、世界观、人物、风格、创意策略、术语合并维护- `outline.md`：故事架构、主线、支线、分卷规划、关键高潮、伏笔管理表、节奏规划- `outl`

### 7. [HEADING_MERGED] `skills/wq-review/SKILL.md` · L221
- **说明**：标题行过长(56 字)，疑似吞并后续行
- **原文**：`#### 扫描项（共 19 项，v1.4.4 增字数检测，v1.4.5 字数降级为警告，v1.4.8 增全书跨章模板检测）`

### 8. [HEADING_MERGED] `skills/wq-rules/SKILL.md` · L633
- **说明**：标题行过长(50 字)，疑似吞并后续行
- **原文**：`### C. 水文硬指标（v1.2.2 新增，v1.2.3 扩展黑名单，v1.2.4 编号顺延；与脚本同步）`

### 9. [JSON_INVALID] `skills/wq-finalize/SKILL.md` · L284-L308
- **说明**：Expecting value @ line 8 col 18
- **原文**：`      "events": [...]`

### 10. [JSON_INVALID] `skills/wq-worldbuilder/SKILL.md` · L354-L356
- **说明**：Expecting value @ line 1 col 2
- **原文**：`[... → write → volume_handoff → write → review → fix → polish → finalize → build/release]`

### 11. [PAREN_UNBALANCED] `skills/wq-migrate/SKILL.md` · L249
- **说明**：（1 vs ）0
- **原文**：`2. 解析每个章节的基本信息（chapter, title, purpose, events：3. 缺少的必填字段标记为 "待补关`

### 12. [PAREN_UNBALANCED] `skills/wq-outline/SKILL.md` · L101
- **说明**：（0 vs ）1
- **原文**：``outlines/chapters.json` 生成后，父Agent必须执行以下验证，全部通过才允许标记 `outline` 阶段完成）`

### 13. [PAREN_UNBALANCED] `skills/wq-outline/SKILL.md` · L110
- **说明**：（0 vs ）1
- **原文**：`**验证规则**）- 每章必须包含全部 **15 个必填字段*：`chapter`、`title`、`purpose`、`events`、`openingHook`、`output`

### 14. [PAREN_UNBALANCED] `skills/wq-outline/SKILL.md` · L115
- **说明**：（1 vs ）2
- **原文**：`**字段质量规则（额外检查，不阻塞但标记警告）*）`

### 15. [PAREN_UNBALANCED] `skills/wq-outline/SKILL.md` · L125
- **说明**：（0 vs ）1
- **原文**：`每人物独立文件，格式如下）`

### 16. [PAREN_UNBALANCED] `skills/wq-outline/SKILL.md` · L162
- **说明**：（1 vs ）2
- **原文**：`**人物卡质量要求*）- 核心性格必须有内在矛盾"（单一性格=纸片人）`

### 17. [PAREN_UNBALANCED] `skills/wq-outline/SKILL.md` · L190
- **说明**：（0 vs ）1
- **原文**：`**分配策略**）- 写作前由父Agent扫描前章已用模板，排除重复选项`

### 18. [PAREN_UNBALANCED] `skills/wq-outline/SKILL.md` · L196
- **说明**：（0 vs ）1
- **原文**：`大纲必须为每章规划叙事节奏，写入任务卡的 `rhythm` 字段）`

### 19. [PAREN_UNBALANCED] `skills/wq-outline/SKILL.md` · L203
- **说明**：（1 vs ）2
- **原文**：`**节奏规则**）- 连续 2 章`fast` 后必须插入`medium` 或`slow`（读者需要喘息）`

### 20. [PAREN_UNBALANCED] `skills/wq-outline/SKILL.md` · L222
- **说明**：（0 vs ）1
- **原文**：`大纲必须明确规划支线剧情，写入`outline.md`）`

### 21. [PAREN_UNBALANCED] `skills/wq-outline/SKILL.md` · L223
- **说明**：（0 vs ）1
- **原文**：`**支线定义**）- 支线必须有独立的"启动 →发展 →收束"结构`

### 22. [PAREN_UNBALANCED] `skills/wq-outline/SKILL.md` · L241
- **说明**：（2 vs ）8
- **原文**：`**支线数量建议**）- 短篇（≤50章））-2 条支线- 中篇）0-150章））-4 条支线- 长篇（≥150章））-6 条支线`

### 23. [PAREN_UNBALANCED] `skills/wq-outline/SKILL.md` · L242
- **说明**：（2 vs ）3
- **原文**：`**支线禁忌**）- ❌支线启动后无收束（烂尾线）- ❌支线与主线完全无关（注水线）`

### 24. [PAREN_UNBALANCED] `skills/wq-outline/SKILL.md` · L250
- **说明**：（0 vs ）1
- **原文**：`\| 1 \| 主线是否有明确的"起点 →冲突 →高潮 →结局"）\| 补充缺失环节 \|`

### 25. [PAREN_UNBALANCED] `skills/wq-outline/SKILL.md` · L251
- **说明**：（0 vs ）1
- **原文**：`\| 2 \| 主角是否有清晰的成长弧光）\| 设计 2-3 个转折点 \|`

### 26. [PAREN_UNBALANCED] `skills/wq-outline/SKILL.md` · L253
- **说明**：（0 vs ）1
- **原文**：`\| 4 \| 结局是否回应了开篇的核心问题）\| 确保闭合 \|`

### 27. [PAREN_UNBALANCED] `skills/wq-outline/SKILL.md` · L258
- **说明**：（0 vs ）1
- **原文**：`\| 5 \| 每个伏笔是否都有预期回收位置）\| 补充回收计划 \|`

### 28. [PAREN_UNBALANCED] `skills/wq-outline/SKILL.md` · L261
- **说明**：（1 vs ）2
- **原文**：`\| 8 \| 高频伏笔（≥3次提及）是否有升线变体）\| 避免重复提及无进展\|`

### 29. [PAREN_UNBALANCED] `skills/wq-outline/SKILL.md` · L266
- **说明**：（1 vs ）2
- **原文**：`\| 9 \| 主角是否有独立欲望（不是被推着走））\| 设计主动选择节点 \|`

### 30. [PAREN_UNBALANCED] `skills/wq-outline/SKILL.md` · L269
- **说明**：（1 vs ）2
- **原文**：`\| 12 \| 人物关系是否有变化（不是静态））\| 设计关系转折点\|`

### 31. [PAREN_UNBALANCED] `skills/wq-outline/SKILL.md` · L274
- **说明**：（0 vs ）1
- **原文**：`\| 13 \| 每卷是否有至就1 为读者能记住的名场面"）\| 设计名场面种存\|`

### 32. [PAREN_UNBALANCED] `skills/wq-outline/SKILL.md` · L275
- **说明**：（1 vs ）2
- **原文**：`\| 14 \| 爽点分布是否均匀（不能集中在某一卷））\| 重新排布 \|`

### 33. [PAREN_UNBALANCED] `skills/wq-outline/SKILL.md` · L318
- **说明**：（0 vs ）1
- **原文**：`**自检输出格式**）`

### 34. [PAREN_UNBALANCED] `skills/wq-outline/SKILL.md` · L347
- **说明**：（1 vs ）2
- **原文**：`**细纲输出格式（写入`outlines/chapter-XXX-YYY.md`）*）`

### 35. [PAREN_UNBALANCED] `skills/wq-outline/SKILL.md` · L348
- **说明**：（0 vs ）1
- **原文**：`每章必须包含以下信息，后续供 `wq-write` 子Agent的context pack 使用）`

### 36. [PAREN_UNBALANCED] `skills/wq-outline/SKILL.md` · L366
- **说明**：（2 vs ）3
- **原文**：`**细纲质量规则**）- `events`（剧情推进）必须 ≥3 项，且每项是"主语+动词+对象"的具体可执行事件，不是场景建立""情感过渡"等泛化描述- `开场方式` 必须指定一`

### 37. [PAREN_UNBALANCED] `skills/wq-outline/SKILL.md` · L368
- **说明**：（0 vs ）1
- **原文**：`### 数据持久化**用户可见输出**）- `plan.md`、`outline.md`、`outlines/chapters.json`、`characters/`、`world`

### 38. [PAREN_UNBALANCED] `skills/wq-outline/SKILL.md` · L370
- **说明**：（2 vs ）3
- **原文**：`**中间数据（`.sumeru/outline/`）*）- 仅保存必要缓存；旧版 `world.json`、`characters.json`、`plot-outline.json`

### 39. [PAREN_UNBALANCED] `skills/wq-outline/SKILL.md` · L54
- **说明**：（0 vs ）1
- **原文**：`每章任务卡必须包含以下全部字段，供`wq-write` 子Agent直接使用）`

### 40. [PAREN_UNBALANCED] `skills/wq-outline/SKILL.md` · L78
- **说明**：（0 vs ）1
- **原文**：`**字段说明**）`

### 41. [PAREN_UNBALANCED] `skills/wq-review/SKILL.md` · L46
- **说明**：（0 vs ）1
- **原文**：`> **并行规则**详见 `wq-rules/SKILL.md` 第二部分"子Agent并行处理规则"）`

### 42. [PAREN_UNBALANCED] `skills/wq-rules/SKILL.md` · L414
- **说明**：（0 vs ）1
- **原文**：`**迁移规则**）1. 读取旧路径时，先检查canonical 路径是否存在`

### 43. [PAREN_UNBALANCED] `skills/wq-rules/SKILL.md` · L538
- **说明**：（0 vs ）1
- **原文**：`由父Agent从每章的 SUMERU_STATUS 解析合并生成，位人`.sumeru/continuity/consistency-rules.json`）`

### 44. [PAREN_UNBALANCED] `skills/wq-rules/SKILL.md` · L593
- **说明**：（0 vs ）1
- **原文**：`写作/润色完成后，父Agent必须执行以下校验）`

### 45. [PAREN_UNBALANCED] `skills/wq-rules/SKILL.md` · L760
- **说明**：（0 vs ）1
- **原文**：`平台适配规则按阶段拆分，各阶段职责不重叠）`

### 46. [PAREN_UNBALANCED] `skills/wq-write/SKILL.md` · L130
- **说明**：（1 vs ）0
- **原文**：`\| **核心事件差异** \| 连续章节核心事件不得同质（如连续章都是"搭讪" \| 同质→警告 \|`

### 47. [QUOTE_UNCLOSED] `skills/wq-rules/SKILL.md` · L244
- **说明**：「 未闭合
- **原文**：`### 第{N}章「标题。- purpose: ...`
