---
name: sumeru-review
description: 小说逻辑/剧情审查、项目测试与创意疲劳检测。用户要检查小说bug、时间线矛盾、人物OOC、剧情前后冲突、章节任务卡验收、伏笔是否回收、章节字数是否达标、剧情合理性、逻辑漏洞、套路重复、爽点同质化、角色被剧情推着走或创意不够新时必须使用本技能。它优先读取 .sumeru/context-packs/review-*.md、.sumeru/cache/*.md、目标章节正文和相关任务卡，必要时才读取 outlines/docs/ideas 原始文件，输出 reviews/、tests/ 和 .sumeru/issues/；轻量问题可自动备份后直接修复 chapters/，严重问题写入 fix-plan.json 供重写。批量深度审查时每个子Agent最多负责3章，全本轻扫可按10-20章摘要分片。
user-invocable: true
---

## 网文逻辑审查

### 触发关键词
帮我检查下小说有没有bug、看看时间线有没有矛盾、人物有没有OOC、找剧情前后冲突、梳理伏笔有没有回收、检查小说剧情合理性、看看有没有剧情漏洞、人物行为不符合性格、检查时间线对不对、找小说前后矛盾的地方、帮我梳理所有伏笔、小说剧情bug检查、逻辑漏洞排查、小说剧情审查

### 核心功能

### 独立调用自举
如果用户直接调用 `sumeru-review`，不要假设 worldbuilder 已运行。先执行 AGENTS.md 的“断点恢复与独立调用自举”：
- 定位项目根目录，读取或生成 `.sumeru/project.json`、`.sumeru/status.json`。
- 根据 `chapters/` 推断可审查章节范围；用户未指定范围时默认审查已存在章节。
- 若缺少 `outlines/chapters.json`，尝试读取 `.sumeru/outline/chapter-outlines.json`；仍缺失时只做正文逻辑审查，并把缺失任务卡写入 issue 或 backlog。
- 若缺少 `.sumeru/cache/`，生成最小 `continuity-brief.md`、`issue-brief.md`、`latest-test-summary.md`。
- 若缺少当前范围的 `review-<range>.md` context pack，先生成临时 context pack 再审查。
- 审查完成后更新 `.sumeru/issues/index.json`、`tests/*.md`、`.sumeru/status.json`、`.sumeru/cache/latest-test-summary.md`。

### 按模式审查
- `short/light`：输出单文件 `review.md`，检查结构、人物动机、反转合理性、错别字和结尾余味；不强制生成 `tests/` 和 `.sumeru/issues/`。
- `medium/standard`：输出 `reviews/review-report.md` 或 `tests/review-report.md`，问题记录到 `.sumeru/issues.md`。
- `long/full`：输出完整 `reviews/`、`tests/`、`.sumeru/issues/`，支持轻扫和深度审查两层流程。

### 低 Token 审查规则
- 全本审查先读取 `.sumeru/cache/latest-test-summary.md`、`issue-brief.md`、`continuity-brief.md` 和章节索引，先做轻扫，不直接读取所有正文。
- `short/light` 直接审查 `story.md` 或少量章节，不使用复杂 issue/test 结构。
- `medium/standard` 优先读取 `issues.md` 和合并审查报告，不拆 issue 文件。
- 深度审查使用 `.sumeru/context-packs/review-<range>.md`，每个子Agent最多 3 章。
- 全本轻扫可按 10-20 章分片，只生成候选问题和高风险章节，不直接修改正文。
- 只有定位到具体问题时，才读取相关章节正文、相关 issue 文件、相关任务卡。
- 生成 tests 后同步更新 `.sumeru/cache/latest-test-summary.md` 和 `.sumeru/cache/issue-brief.md`。

#### 三阶段审查修复流程设计

为确保审查全面性和修复质量，本 skill 采用三阶段审查修复流程：

**第一阶段：全局信息审查**
- 加载完整大纲和章节细纲，建立全局审查基准
- 优先加载 `outlines/chapters.json` 章节任务卡、`docs/architecture.md`、`docs/style-guide.md`、`docs/glossary.md`
- 分析整体剧情脉络和时间线结构
- 审查全局设定一致性（世界观、力量体系、规则设定）
- 识别主线支线关联问题和伏笔回收情况
- 检查整体冲突点分布和节奏把控
- 记录**全局问题清单**到 `.sumeru/review/global-issues.json`
- 同步生成或更新 `.sumeru/issues/index.json`

**第二阶段：章节细节审查（Agent Team 并行）**
- 使用多 Agent 并行处理，每个 Agent 负责一定数量的章节
- **⚠️ 遵循全局约束：每个子Agent最多负责3个章节**（详见 AGENTS.md "子Agent并行处理规则"）
- 所需Agent数 = ceil(总章节数 / 3)，分配策略为按章节顺序连续分配
- 为每章生成核心剧情概要（去掉细节，仅保留关键事件）
- 对每章进行详细审查：
  - 章节任务卡 `acceptanceCriteria` 验收
  - 创意目标 `creativeGoal` 是否落地
  - 情绪节拍 `emotionalBeat` 是否和前后章重复
  - 读者记忆点 `readerMemoryPoint` 是否足够清晰
  - `tropeToAvoid` 是否被避开
  - 字数统计与填充需求识别
  - 时间线与事件时序验证
  - 人物行为与性格一致性（OOC检测）
  - 物品状态与信息边界检查
  - 场景描写与对话质量评估
  - 伏笔设置与回收状态
- 生成**章节概要**到 `.sumeru/review/summaries/` 目录
- 记录**章节问题清单**到 `.sumeru/review/chapter-issues/` 目录
- 生成测试报告到 `tests/chapter-acceptance-report.md`、`tests/continuity-report.md`、`tests/foreshadowing-report.md`、`tests/word-count-report.md`
- 生成创意质量报告到 `tests/creativity-report.md`
- 支持断点续传，已审查章节可跳过

**第三阶段：统一修复执行**
- 合并全局问题和章节问题，按严重程度排序（致命 > 严重 > 中等 > 轻微）
- 制定并执行**修复计划**，分为两种修复类型：
   - **轻量修复**（review 直接执行）：错别字、标点、少量段落调整、局部语句优化、字数不足补充等不改变主线事实的修改，**直接修改 `chapters/` 文件**（修改前自动备份到 `.sumeru/write/original/`）
  - **重写修复**（标记待处理）：剧情逻辑严重矛盾、大面积OOC、设定崩坏等需要重写的章节，记录到修复计划
- 执行轻量修复策略：
   - **全局问题处理**：整理整体时间线、统一术语和设定表述；涉及主线结构变化时只写入修复计划，不直接重构全书
   - **章节问题修复**：逐章修复字数、局部逻辑、轻微OOC、轻微剧情矛盾等轻量级问题
  - **联动修复**：处理跨章节的关联问题（如伏笔回收、人物成长）
- 生成**修复报告**到 `.sumeru/review/fix-report.json`
- 生成**修复计划** `fix-plan.json`，标记需要重写的章节及具体修复建议
- 修复后重新审查，验证所有轻量修复问题已彻底解决

#### 三阶段功能分配

**第一阶段：全局审查功能**
1. **整体剧情脉络分析**：审查主线、支线、伏笔的整体分布
2. **全局时间线校验**：梳理完整时间线，识别大跨度时序问题
3. **设定一致性检查**：验证世界观、力量体系、规则设定的统一性
4. **冲突点分布评估**：评估冲突强度、分布密度、节奏把控
5. **伏笔回收状态检查**：识别所有未回收的伏笔和回收方向

**第二阶段：章节细节审查功能**
6. **字数检查与填充**：确保每章字数达标，字数不足自动填充
7. **章节时间线与事件时序**：检查每章内部的时间逻辑和事件顺序
8. **OOC检测与人物一致性**：检查人物行为、性格、对话的一致性
9. **物品状态与信息边界**：追踪物品状态变化和人物信息边界
10. **场景描写与对话质量**：评估场景细节和对话的自然度
11. **章节伏笔设置**：记录每章的伏笔设置和预期回收位置
- **⚠️ 遵循全局约束：每个子Agent最多负责3个章节的审查**（详见 AGENTS.md）

**第三阶段：统一修复功能**
12. **问题统一修复**：合并所有问题，按严重程度排序，制定修复计划
13. **轻量修复执行**：错别字、标点、局部段落调整、语句优化、字数填充等直接修改 `chapters/` 文件
14. **重写修复标记**：对需要重写的章节生成 `fix-plan.json`，记录具体问题与修复建议
15. **全局问题处理**：整理整体剧情、时间线、设定等大尺度问题；大改动写入修复计划
16. **章节问题修复**：逐章修复字数、逻辑、人物、场景等轻量级细节问题
17. **联动修复**：处理跨章节关联问题，确保修复后的整体一致性
18. **修复验证**：修复后重新审查，确保所有轻量修复问题已彻底解决
- **⚠️ 轻量修复阶段遵循全局约束：每个Agent最多负责3个章节**（详见 AGENTS.md）

#### 修复机制说明
- **轻量级修复**：直接修改 `chapters/` 中不改变主线事实的段落或句子，修改前自动备份原始文件到 `.sumeru/write/original/`
- **重写修复**：对于严重有问题的章节，记录到 `fix-plan.json`，建议使用 `sumeru-write` 重新生成
- **自动备份**：修改 `chapters/` 文件前，自动将原始版本备份到 `.sumeru/write/original/`，确保可回滚
- **修复记录**：所有修复操作都记录在 `issues-fixed.json` 中，包含修复前后对比

### 输出内容
**第一阶段：全局审查输出**
- **全局剧情脉络分析报告**：主线、支线、伏笔的整体分布图
- **完整故事时间线图谱**：按时间轴整理的关键事件序列
- **设定一致性检查报告**：世界观、力量体系、规则设定的统一性分析
- **冲突点分布评估**：冲突强度、分布密度、节奏把控评估
- **全局伏笔回收状态表**：所有未回收伏笔清单与回收方向建议

**第二阶段：章节细节审查输出**
- **章节概要目录**：每章核心剧情概要（`.sumeru/review/summaries/`）
- **字数检查报告**：每章字数统计、不达标的章节列表、填充改进记录
- **章节时间线与事件时序报告**：每章内部时间逻辑检查结果
- **OOC检测报告**：人物行为异常点、性格偏离分析
- **物品状态追踪表**：重要物品的获得、使用、丢失状态变化
- **章节伏笔设置记录表**：每章伏笔设置与预期回收位置
- **剧情连贯性评分**：多维度综合评分（时间线、逻辑性、人物一致性等）

**第三阶段：统一修复输出**
- **问题修复报告**：所有问题的修复情况记录、修复前后对比
- **全局问题修复记录**：整体剧情、时间线、设定的调整记录
- **章节问题修复记录**：逐章修复的详细记录
- **联动修复说明**：跨章节关联问题的处理方案
- **修复验证报告**：修复后重新审查的验证结果
- **优化建议**：剧情调整方案、伏笔回收建议、冲突优化建议

### 项目测试输出
- `reviews/剧情审查报告.md`：用户可读总报告。
- `tests/continuity-report.md`：时间线、人物状态、物品状态、地点、信息边界检查。
- `tests/chapter-acceptance-report.md`：逐章验收 `acceptanceCriteria`，标记 pass/fail/evidence。
- `tests/foreshadowing-report.md`：伏笔新增、推进、回收、遗留状态。
- `tests/creativity-report.md`：套路重复、爽点同质化、情绪疲劳、创意目标落地、读者记忆点检查。
- `tests/word-count-report.md`：章节字数统计和过短/过长章节。
- `.sumeru/issues/index.json`：结构化 issue 索引。
- `.sumeru/issues/ISSUE-0001-*.md`：单个问题说明，包含证据、影响、建议修复、状态。

Issue 严重度使用：`critical`、`major`、`minor`、`suggestion`。Issue 状态使用：`open`、`fixed`、`wontfix`、`needs-rewrite`、`needs-user-decision`。

### 创意审查标准
- **套路重复**：连续章节是否反复使用同一解决方式，如“嘲讽→打脸”“遇敌→爆种”。
- **爽点同质化**：爽点是否只有战力碾压，缺少智斗、反差、身份、情感、探索等变化。
- **情绪疲劳**：连续 3 章以上是否情绪曲线相同。
- **反转公平性**：惊喜反转是否有前文线索，是否“意外但合理”。
- **角色主动性**：主角、反派、配角是否有独立欲望和主动选择。
- **记忆点强度**：本章是否有可被读者复述的画面、台词或局势。
- **类型承诺**：创意是否仍服务目标读者，不为反套路而反套路。

### 数据持久化
**用户可见输出（当前工作目录）**：
- `reviews/剧情审查报告.md`：完整审查结果报告，包含所有问题、严重程度、修复建议（直接可读）
- `字数检查与填充报告.md`：字数统计、填充改进记录
- `全局审查报告.md`：第一阶段的全局分析结果
- `章节细节审查报告.md`：第二阶段的章节分析结果
- `统一修复报告.md`：第三阶段的修复记录

**中间数据（仅系统内部使用，存于`.sumeru/review/`目录）**：
**第一阶段：全局审查数据**
- `global-issues.json`：全局问题清单，包含时间线、设定、伏笔等问题
- `timeline.json`：完整时间线图谱，按时间轴排列的关键事件序列
- `plot-map.json`：剧情脉络图，显示主线、支线、冲突点分布
- `foreshadowing-tracking.json`：伏笔追踪表，包含所有伏笔的位置、内容、回收状态
- `coherence-score.json`：剧情连贯性评分明细

**第二阶段：章节细节审查数据**
- `summaries/`：章节概要目录
  - `001.json`、`002.json`... 每章的核心剧情概要（章节号三位数零填充）
  - `summary-progress.json`：概要生成进度记录
- `chapter-issues/`：章节问题清单
  - `001.json`、`002.json`... 每章的详细问题记录（章节号三位数零填充）
- `word-count.json`：字数统计数据，每章字数、目标字数、填充情况

**第三阶段：统一修复数据**
- `issues.json`：合并后的完整问题清单，按严重程度、类型分类
- `fix-report.json`：问题修复报告，包含修复前后对比
- `fix-plan.json`：重写修复计划，标记需要重写的章节及具体修复建议
- `issues-fixed.json`：已修复问题记录
- `global-fix.log`：全局问题修复日志
- `chapter-fix.log`：章节问题修复日志

#### 与其他 Skill 配合
- **前置 Skill**：读取 `sumeru-outline` 的大纲数据和 `sumeru-write` 的章节数据
   - 使用 `docs/` 的世界观、人设、大纲、风格规范作为基准
   - **使用 `outlines/chapters.json` 作为章节任务卡和验收标准**
   - 兼容读取 `.sumeru/outline/chapter-outlines.json` 作为预期剧情参考
   - 使用 `chapters/` 目录下的章节内容进行审查
   - 将实际章节内容与细纲进行对比，识别剧情偏离

- **修复计划输出**：修复完成后生成 `fix-plan.json`，其中标记了需要重写的章节及具体修复建议
   - worldbuilder 在编排流程时读取此文件，决定是否需要调用 `sumeru-write` 进行重写
   - 独立使用时，用户可查看 `fix-plan.json` 后手动调用 `sumeru-write` 重写指定章节

- **后续 Skill**：
   - **sumeru-write**：读取 `fix-plan.json`，执行重写修复（由 worldbuilder 编排或用户手动调用）
   - **sumeru-polish**：接收修复后的章节内容，进行文笔润色
   - **sumeru-finalize**：接收修复后的章节内容，进行完稿校验和多平台导出

#### 三阶段数据流向
```
sumeru-write 章节
    ↓
第一阶段：全局审查（global-issues.json）
    ↓
第二阶段：章节细节审查（chapter-issues/ + summaries/）
    ↓
合并问题清单（issues.json）
    ↓
第三阶段：统一修复
    ├─ 轻量修复 → 直接修改 chapters/（自动备份到 .sumeru/write/original/）
    └─ 重写修复 → 生成 fix-plan.json
    ↓
供 polish 和 finalize 使用
```

#### 数据复用
- 返工修改时直接读取问题清单定位需要调整的章节
- 支持增量审查，新增章节时基于已有审查结果只检测新增内容
- 修复完成后可再次调用自动验证问题是否解决
- 字数填充记录可用于后续章节的字数参考
