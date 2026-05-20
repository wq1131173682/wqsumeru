# AGENTS.md - 须弥写作 Skill 全局规则

## 项目定位

本仓库提供一组面向网文/小说创作的 AI Skill，覆盖选题、世界观与大纲、章节写作、剧情审查、文笔润色、完稿校验与平台导出。各 Skill 可以独立使用，也可以由 `sumeru-worldbuilder` 串联成完整创作流程。

## Skill 列表

```
skills/
├── sumeru-worldbuilder/  # 全流程编排
├── sumeru-topic/         # 选题策划
├── sumeru-outline/       # 大纲、世界观、人设、章节细纲
├── sumeru-write/         # 章节写作、续写、重写、扩写
├── sumeru-review/        # 剧情逻辑、时间线、OOC、伏笔审查
├── sumeru-polish/        # 文笔、节奏、爽点、对话润色
├── sumeru-finalize/      # 错别字、敏感词、排版、发布格式导出
└── sumeru-rules/         # 全局约束（子Agent规则、输出级别等）
```

每个 Skill 目录必须包含 `SKILL.md`，可按需包含 `scripts/` 和 `references/`。

---

## 一、小说项目目录结构

**核心原则：能合并就合并，能省略就省略，减少文件数量和 Token 消耗。**

### 模式分层

| projectMode | workflowLevel | 适用范围 | 目标 |
|---|---|---|---|
| `short` | `light` | 1-10章，3万字以内 | 快速产出，最少文件 |
| `medium` | `standard` | 10-50章，3万-20万字 | 有结构但不过度工程化 |
| `long` | `full` | 50章以上，20万字以上 | 完整项目化、可断点、可发布 |

自动判断规则：
- `plannedChapters <= 10` 或 `plannedWords <= 30000`：默认 `short/light`
- `plannedChapters <= 50` 或 `plannedWords <= 200000`：默认 `medium/standard`
- `plannedChapters > 50` 或 `plannedWords > 200000`：默认 `long/full`

### short/light 结构（最少文件）

```
short-story/
├── story.md                  # 正文（短篇可直接写在一个文件）
├── outline.md                # 简纲
└── .sumeru/
    ├── project.json
    └── status.json
```

### medium/standard 结构

```
novella-project/
├── story.md                  # 正文
├── outline.md                # 大纲
├── plan.md                   # 合并：需求+设定+创意
├── chapters/                 # 分章正文（超过 10 章时启用）
└── .sumeru/
    ├── project.json
    ├── status.json
    └── cache/
```

### long/full 结构

```
novel-project/
├── plan.md                    # 合并：需求+设定+创意
├── outline.md                 # 故事结构、主线、伏笔、章节规划摘要
├── outlines/                  # chapters.json 章节任务卡
├── chapters/                  # 正文，按 001-标题.md 命名
├── publish/                   # 发布构建产物
└── .sumeru/
    ├── project.json
    ├── status.json
    ├── cache/
    ├── continuity/            # 连贯性状态库
    └── issues.md              # 问题清单（单文件）
```

**精简说明：**
- `docs/` + `ideas/` → 合并为 `plan.md`（减少 6-8 个文件）
- `tests/` + `reviews/` → 只在需要时创建
- `issues/` 目录 → 合并为 `.sumeru/issues.md` 单文件
- `drafts/` → 用户手动管理，系统不创建

---

## 二、上下文预算与缓存策略

### 文件加载层级

**L0 常驻配置层**（每次任务可读取，必须短小）：
```
.sumeru/project.json
.sumeru/status.json
```

**L1 稳定摘要缓存层**（优先读摘要而不是原始大文件）：
```
.sumeru/cache/project-brief.md
.sumeru/cache/plan-brief.md      # 合并：world+characters+style+creative
.sumeru/cache/continuity-brief.md
.sumeru/cache/issue-brief.md
```

**L2 任务上下文包**（每个子Agent只读取自己的 context pack）：
```
.sumeru/context-packs/write-001-003.md
.sumeru/context-packs/review-001-003.md
```

**L3 原始大文件层**（只有摘要不足时才读取）：
```
plan.md
chapters/*.md
```

### 读取预算规则

- 单章/三章写作只读取目标章节任务卡、前 1 章摘要、后 1 章任务卡摘要
- 批量子Agent只读取 `.sumeru/context-packs/<task>-<range>.md`
- 章节正文默认只读目标章节、前 1 章和必要的后续任务卡
- 单段润色只读用户片段、风格要求和必要术语，不生成 context pack
- 完稿校验只在用户明确完稿/导出时触发

---

## 三、输出级别规范

**核心原则：创作过程中用户只需要知道进度，其他技术细节静默处理。**

### 输出级别

| 级别 | 说明 | 适用场景 |
|------|------|----------|
| `quiet` | 只输出进度和关键节点 | **默认**，日常创作 |
| `normal` | 输出进度 + 阶段总结 + 问题提醒 | 用户明确要求 |
| `verbose` | 完整输出所有中间报告 | 调试/审查 |

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

### 输出示例对比

**Verbose（太啰嗦）：**
```
🔍 找到 50 个章节文件，正在统计...
📊 统计结果：总章节数: 50, 总字数: 150,000
⚠️ 发现 3 章过短
✅ 字数统计报告已生成：.sumeru/review/word-count-report.json
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

### 项目配置

在 `.sumeru/project.json` 中设置：

```json
{
  "outputLevel": "quiet"
}
```

### 脚本 Quiet 模式

所有脚本支持 `--quiet` 参数：

```bash
python scripts/continuity-check.py .sumeru/continuity --quiet
```

---

## 四、断点恢复与独立调用自举

用户可能不通过 `sumeru-worldbuilder`，而是直接调用任意 Skill。任何 Skill 单独启动时，都必须执行同一套自举流程。

### 自举流程（9步）

1. **定位项目根目录**：查找 `.sumeru/project.json`、`.sumeru/status.json`、`plan.md`、`chapters/`
2. **识别项目版本**：若有 `.sumeru/project.json` 按新协议执行；否则进入兼容模式
3. **最小初始化**：缺少配置时根据已有文件生成最小配置
4. **补齐目录**：按需创建 `.sumeru/cache/`、`.sumeru/context-packs/`、`.sumeru/continuity/`
5. **迁移兼容输入**：旧版 `.sumeru/outline/chapter-outlines.json` 仍可读取
6. **刷新摘要缓存**：cache 缺失时生成最小摘要
7. **生成 context pack**：缺少时生成临时 context pack
8. **执行任务并回写状态**：更新 `.sumeru/status.json`、相关 cache
9. **记录变更**：追加到 `.sumeru/changelog.md`

### Canonical 路径协议

新写入只使用：`plan.md`、`outline.md`、`outlines/chapters.json`、`chapters/`、`.sumeru/issues.md`、`publish/`。

旧路径 `docs/*`、`ideas/*`、`.sumeru/issues/index.json`、`.sumeru/outline/chapter-outlines.json` 只读兼容，不再作为新写入目标。

### 独立调用原则

- 单独调用 skill 时，不要求用户先运行 worldbuilder
- 能从现有项目文件推断的信息，不重复询问用户
- 不因为缓存缺失而失败；缓存缺失时生成最小缓存
- 兼容旧项目，但新写入内容应遵守新项目结构

---

## 五、项目配置 Schema

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
  "outputLevel": "quiet",
  "createdAt": "2026-05-16T00:00:00Z",
  "updatedAt": "2026-05-16T00:00:00Z"
}
```

`.sumeru/status.json` 记录状态机和章节进度。

```json
{
  "currentStage": "write",
  "stages": {
    "init": "completed",
    "topic": "completed",
    "outline": "completed",
    "write": "in_progress",
    "review": "pending",
    "polish": "pending",
    "finalize": "pending"
  },
  "chapters": {
    "001": "finalized",
    "002": "polished",
    "003": "drafted"
  },
  "lastAction": "generated chapter 003"
}
```

**阶段状态**：`pending`、`in_progress`、`blocked`、`completed`、`skipped`

**章节状态**：`planned`、`drafted`、`reviewed`、`fixed`、`polished`、`finalized`、`exported`

---

## 六、AI 创意引擎

工程化结构用于保证长篇不崩，创意引擎用于保证作品有新鲜感、记忆点和传播性。

### 创意选择评分

- 新鲜度：是否避免同质化套路
- 爽感：是否提供清晰情绪价值
- 合理性：是否符合已建立设定和伏笔
- 可持续性：是否能支撑后续章节
- 传播性：是否有一句话安利点
- 类型契合度：是否仍满足目标平台和目标读者期待

### 高概念 Pitch 格式

```markdown
## Pitch A
- 一句话：一个只能靠失败升级的天才，被迫把所有胜利都伪装成失败。
- 类型混血：高武玄幻 + 反向升级系统 + 校园竞技
- 核心反差：越强越要装弱，越赢越危险
- 爽点来源：读者知道主角在赢，书中角色以为他在输
- 代价/限制：系统只承认公开失败，私下胜利不计入成长
- 传播句：别人都怕输，只有他怕赢得太明显。
```

### 反套路检查

生成选题、大纲、章节前检查：
- 这个桥段是否太常见？
- 读者是否能提前猜到解决方式？
- 有没有比"反派嘲讽→主角打脸"更有记忆点的版本？

---

## 七、章节任务卡

章节不是单纯的文本生成任务，而是一个带输入、输出和验收标准的 feature。

`outlines/chapters.json`（兼容旧路径 `.sumeru/outline/chapter-outlines.json`）中每章应包含：

```json
{
  "chapterNumber": 12,
  "chapterId": "012",
  "title": "拍卖会风波",
  "status": "planned",
  "purpose": "让主角第一次公开展现判断力并获得关键道具",
  "creativeGoal": "制造一次读者预期反转，并留下可传播的名场面",
  "tropeToAvoid": "反派嘲讽后主角直接加价打脸",
  "freshnessHook": "主角故意让反派拍下宝物",
  "emotionalBeat": "压抑 → 困惑 → 恍然 → 暗爽",
  "readerMemoryPoint": "反派以为自己赢了，实际买下的是主角留给他的雷",
  "suggestedWords": "2500-3000",
  "events": ["主角进入拍卖会", "反派抬价羞辱", "主角识破残片真实价值"],
  "outputs": {
    "characterStateChanges": ["沈青鸢开始怀疑主角并非普通人"],
    "itemStateChanges": ["黑色残片归主角所有"],
    "foreshadowingAdded": ["残片来自上古遗迹"]
  },
  "acceptanceCriteria": [
    "本章必须出现一次反派抬价打压",
    "主角不能暴露真正实力",
    "结尾必须留下残片异常的悬念"
  ]
}
```

---

## 八、Issue 与测试体系

剧情审查应像项目测试一样输出结构化结果。

- `.sumeru/issues.md`：所有问题的清单（合并为单文件）
- `tests/continuity-report.md`：时间线、人物状态、物品状态检查
- `tests/chapter-acceptance-report.md`：章节任务卡验收结果

**Issue 状态**：`open`、`fixed`、`wontfix`、`needs-rewrite`、`needs-user-decision`

---

## 九、连贯性规则库

**问题**：review 全局一致性审查太昂贵，需要读全部正文才能发现矛盾。

**解决方案**：建立持续维护的 `consistency-rules.json`，将全局一致性从"事后大海捞针"变成"实时规则检查"。

**文件位置**：`.sumeru/continuity/consistency-rules.json`

**维护时机**：
- write 子Agent每次输出正文时，必须附带 `state_diff`（通过状态标记），父Agent自动更新
- review 子Agent审查时，不需要读全部正文，只需用此文件交叉验证

---

## 十、Build 与 Release

完稿导出视为 build/release 流程。

- build 前必须检查章节状态，默认只导出 `finalized` 的章节
- build 前必须检查是否存在 `TODO`、`FIXME`、未关闭的 `critical`/`major` issue
- build 时必须剥离章节首行的 `SUMERU_STATUS` 注释
- build 输出写入 `publish/`，并生成 `.sumeru/finalize/build-manifest.json`

---

## 十一、子Agent并行处理规则

**⚠️ 核心约束：写正文必须走子agent，单章续写也必须走子agent，父agent绝不写正文。**

| 规则 | 说明 |
|------|------|
| 并行上限 | 最多 5 个子agent同时运行 |
| 分片约束 | 每个子Agent最多负责 3 个连续章节 |
| 计算公式 | 所需Agent数 = `min(ceil(总章节数 / 3), 5)` |
| 分配策略 | 按章节顺序连续分组（1-3、4-6、7-9...） |

### 批次间串行摘要

每批完成后，父Agent生成"实际摘要"（≤300字），作为下一批 context pack 的输入。采用**滚动窗口策略**：context pack 中只保留最近 3 批摘要，更早的合并为一行概述。

```
第 1 批（并行）: 子Agent A 写 1-3章 + 子Agent B 写 4-6章
                  ↓ 父Agent生成"1-6章实际摘要"（≤300字，纯事实列表）
第 2 批（并行）: 子Agent C 写 7-9章 + 子Agent D 写 10-12章
                  （context pack 中包含"第1批概述"）
```

---

## 十二、子Agent职责边界规则

**核心原则：子Agent只做"单一核心任务"，所有状态维护、文件写入、缓存刷新、汇总合并均由父Agent（调度器）统一处理。**

### 父Agent（调度器）职责

- 自举 & 环境准备
- Context pack 生成（1500-3000 中文字）
- Cache 摘要读取
- 任务卡读取
- 任务分发
- 结果汇总
- 文件写入（统一写入，避免并发冲突）
- 备份（修改前备份到 `.sumeru/write/original/`）
- 状态更新
- 缓存刷新
- 日志记录
- Issue/测试汇总

### 子Agent（执行器）职责

- 只读 context pack（不读取任何额外文件）
- 执行核心任务
- 输出纯结果（不包含状态更新指令）
- 不碰状态（不更新 status.json、不写 changelog、不刷 cache）
- **输出状态标记**（首行必须包含 `<!-- SUMERU_STATUS: ... -->`）

### 状态标记格式

```markdown
<!-- SUMERU_STATUS: chapter=037, status=drafted, state_diff={"location_change":{"苏瑾":"北域冰原"},"state_change":{"苏瑾":"minor_injury"},"item_change":{"黑色残片":"acquired"}}, char_update={"苏瑾":{"status":"minor_injury","location":"北域冰原"}}, plot_update={"foreshadowing":{"v3":"黑衣人身份暗示推进"}}, batch=002, timestamp=2026-05-18T10:30:00Z -->
```

**关键约束**：
- 状态标记必须放在输出内容的**第一行**
- `state_diff` 必须是合法 JSON（单行，无换行符），按变化类型分类：`location_change`、`state_change`、`power_change`、`item_change`、`foreshadow_change`、`buff_change`
- 父Agent按分类键直接更新 `.sumeru/continuity/consistency-rules.json` 对应数组

### 各 Skill 子Agent职责明细

| Skill | 子Agent核心任务 | 子Agent输入 | 子Agent输出 |
|-------|----------------|------------|------------|
| **sumeru-write** | 按任务卡写正文 | context pack（含任务卡、前一章结尾） | 纯正文文本 + 状态标记 |
| **sumeru-review** | 按任务卡审查章节 | context pack（含任务卡、正文、consistency-rules.json） | 审查结论 |
| **sumeru-polish** | 按标准润色章节 | context pack（含正文、style-brief、具象标杆） | 润色后正文 + diff |
| **sumeru-outline** | 生成章节细纲 | context pack（含世界观、人物、分卷大纲） | 章节细纲 JSON/Markdown |
| **sumeru-finalize** | 脚本预处理 + 待定项判断 | 脚本扫描结果（待定项列表） | 待定项处理建议 |

---

## 十三、Context Pack 精简规则

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

## Batch Summary (仅非第一批)
前N批实际摘要（≤500字）。
```

### 具象标杆（polish 专属）

polish 子Agent的 context pack 中，必须嵌入**具象标杆段落**：

```
【风格标杆】（摘自已完成章节）：
---打斗场景标杆---
原文：...
润色后：...
---对话场景标杆---
原文：...
润色后：...
---情绪高潮标杆---
原文：...
润色后：...
```

---

## 十四、修改边界

- `sumeru-review` 可以直接修复错别字、轻微逻辑补丁、字数不足补充等轻量问题
- `sumeru-review` 不应直接大面积重写章节；严重问题写入 `fix-plan.json`
- `sumeru-polish` 可以直接修改 `chapters/` 做文笔、节奏、对话、爽点优化，但不得改变主线事实
- `sumeru-finalize` 专注技术性校验和发布格式，不承担剧情重构
- 下游 Skill 不直接调用上游 Skill；需要返工时输出结构化计划

---

## 十五、质量检查

执行任一 Skill 后，应至少检查：

1. 预期输出文件是否生成
2. `.sumeru/` 中的结构化数据是否与用户可见输出一致
3. 章节文件是否按三位编号排序且没有缺章、重章
4. 修改型 Skill 是否已生成备份和变更记录
5. 报告中是否区分已修复问题、待用户确认问题和需要重写的问题

---

## 十六、写作安全与原创性

- 避免直接复刻现实公众人物、真实组织、真实地名、知名 IP 角色
- 用户要求参考某作品时，只学习节奏、类型结构和读者情绪价值
- 涉及敏感、血腥、低俗、未成年人不当内容时，优先进行合规化改写
