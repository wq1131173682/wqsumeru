---
name: wq-score
description: 小说完稿评分系统——五维评分、分级输出、子Agent并行评审
version: 1.0.0
type: skill
argument-hint: "[目标范围(全书/卷N/章节N-M)] [输出模式(score-card/report/data)] [维度筛选(completeness/narrative/creativity/technical/market_fit)]"
disable-model-invocation: false
user-invocable: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, task
context: project
agent: build
requires: [wq-rules]
---

> 依赖 `wq-rules`，默认 `quiet` 模式。
> 评分标准定义见 `config/scoring-criteria.json`。

# WQ 写作评分系统

## 触发场景

| 触发词 | 说明 |
|--------|------|
| "评分"、"打分"、"评估"、"评价"、"测评分" | 用户主动触发评分 |
| "看看写得怎么样"、"质量如何"、"值不值得发" | 质量评估需求 |
| **自动触发**：`finalize → build/release` 管道中，若 `project.json.currentStage` 含 `score` | 管道集成 |
| **worldbuilder 编排**：worldbuilder 在 `polish → finalize` 之间可选择插入 | 编排需求 |

## 五维评分模型

| 维度 | 权重 | 核心考察 |
|------|------|---------|
| **完整性** Completeness | 20% | 结构完整、主线收束、伏笔回收、全章节 |
| **叙事质量** Narrative | 25% | 情节逻辑、人物塑造、节奏、对话、张力 |
| **创意性** Creativity | 20% | 设定原创度、世界观、反转、套路突破 |
| **技术执行力** Technical | 15% | 文笔、语法、一致性、格式、反AI指标 |
| **市场契合度** Market Fit | 20% | 类型遵守、平台适配、留存潜力、商业可行性 |

各维度下分多个评分项（详见 `config/scoring-criteria.json`），每项 1-5 分，带 S/A/B/C/D 五级评语锚。

## 等级体系

| 等级 | 分数 | 含义 | 建议动作 |
|------|------|------|---------|
| **S** | 90-100 | 卓越 | 可直接发布或极小修改 |
| **A** | 80-89 | 优秀 | 中轻度润色后可发布 |
| **B** | 70-79 | 良好 | 需中度修改后方可发布 |
| **C** | 60-69 | 及格 | 需大幅修改或部分重构 |
| **D** | 0-59 | 不及格 | 严重不完整/质量问题 |

## 输出模式

| 模式 | 输出内容 | 适用场景 |
|------|---------|---------|
| `score-card` | 单行摘要：总分+等级+各维度分 | 快速概览、管道集成 |
| `report` | 完整报告：维度分解+每项得分+评语+强弱点分析+改进建议 | 详细评估 |
| `data` | JSON-only `.sumeru/score/latest.json` + `score-snapshot.json` | 下游消费、趋势追踪 |

### score-card 输出格式

```
═══ 须弥评分 ═══
总分: 85/100 → A（优秀）
  完整性 18/20 | 叙事 21/25 | 创意 17/20 | 技术 12/15 | 市场 17/20
─────────────────
🥇 最强: 叙事质量 — 人物塑造扎实，节奏控制精准
📉 最弱: 技术执行力 — 反AI扫描有2项medium警告
💡 建议: 先跑 /wq-polish 修复句式重复问题
```

### report 输出格式

```
═══ 须弥评分报告 ═══
项目: {标题} | 范围: 全书 | 评分日期: {日期}

━━━ 总分: 85/100 → A（优秀）━━━

【完整性】18/20 (90% → S)
  ✅ 结构完整度 5/5 — 三段式结构清晰，起承转合完整
  ✅ 主线收束 4/5 — 主线全收，2条支线略悬空
  ⚠️ 伏笔回收 4/5 — v9/v12两处小伏笔未回收
  ✅ 章节完整 5/5 — 全章节无缺
  ✅ 分卷完整 4/5 — 卷2结尾略仓促

【叙事质量】21/25 (84% → A)
  ✅ 情节逻辑 5/5 — 因果链完整无硬伤
  ✅ 人物塑造 5/5 — 主角弧光完整，配角有辨识度
  ⚠️ 节奏掌控 4/5 — 第30-35章略拖
  ✅ 对话质量 4/5 — 自然，配角差异可更鲜明
  ⚠️ 情绪张力 4/5 — 高潮有感染力但铺垫略长
  ⚠️ 开篇钩子 4/5 — 钩子有力但悬念展开略慢

...

【改进建议】
1. 优先修复：反AI扫描medium警告（句式重复）
2. 中等优先级：回收v9/v12伏笔
3. 锦上添花：第30-35章精简20%字数提速

【平台适配建议】（目标平台：番茄）
  优势：爽点密度高、章节结尾钩子强 → 完读率预计不错
  风险：开篇前500字冲突来得慢一拍 → 可提前到第1段插入冲突
```

## 管道集成

`wq-score` 设计为**可选的管道中间节点**，在 `polish → finalize` 之间插入：

```
→ polish → score(可选) → finalize → build/release
```

### 触发方式

1. **用户手动调用**：`/wq-score 全书 report`
2. **worldbuilder 编排**：worldbuilder 根据用户选择或项目配置自动插入
3. **管道条件触发**：当 `project.json.workflowLevel ≥ long` 时自动建议评分

### 评分结果存储

评分结果写入 `.sumeru/score/` 目录：

| 文件 | 内容 |
|------|------|
| `.sumeru/score/latest.json` | 最新评分完整JSON |
| `.sumeru/score/score-snapshot.json` | 评分快照（供下游消费的最小字段集） |
| `.sumeru/score/history/` | 历史评分归档（每次评分生成一份 `{YYYY-MM-DD}T{HHmmss}.json`） |
| `.sumeru/score/report.md` | 最近一次 report 输出（仅report模式生成） |

### snapshot 格式（供 finalize/其他技能消费）

```json
{
  "scoreId": "score-20260623T133000",
  "scopedAt": "2026-06-23T13:30:00Z",
  "scope": "full",
  "dimensions": {
    "completeness": { "score": 18, "max": 20, "grade": "S" },
    "narrative": { "score": 21, "max": 25, "grade": "A" },
    "creativity": { "score": 17, "max": 20, "grade": "A" },
    "technical": { "score": 12, "max": 15, "grade": "A" },
    "market_fit": { "score": 17, "max": 20, "grade": "A" }
  },
  "total": { "score": 85, "max": 100, "grade": "A" },
  "weakestDimension": "technical",
  "strongestDimension": "narrative",
  "improvementTips": ["建议优先解决反AI句式重复问题"],
  "deficientChapters": [
    {
      "chapter": "015",
      "chapterFile": "chapters/015-拍卖会冲突.md",
      "totalScore": 6.5,
      "grade": "C",
      "threshold": 7.5,
      "deficiencies": [
        { "dimension": "narrative", "item": "pacing", "score": 3, "evidence": "第30-35章略拖" },
        { "dimension": "completeness", "item": "word_count", "current": 1800, "target": 2500 }
      ]
    }
  ]
}
```

> **`deficientChapters` 字段**：低于 `config/scoring-criteria.json.gradeThresholds` 中对应等级阈值的章节清单，供 `wq-revise` 消费做收敛式修稿。每章含 `deficiencies` 明细（维度 + 评分项 + 当前值 + 证据），revise 据此映射 allowedOps。**创意性/市场契合度**类缺陷也写入此字段，由 revise 标 `escalate` 交人工，不自动修。

## 使用示例

```
/wq-score 全书 score-card           # 全书快速评分
/wq-score 全书 report               # 全书详细评分报告
/wq-score 卷1 score-card             # 仅评分第一卷
/wq-score 第1-50章 data             # 评分前50章，仅输出JSON
/wq-score 全书 report creativity    # 仅评分创意维度
/wq-score 全书 report completeness  # 仅评分完整性
```

## 评分协议

### 父Agent职责

| 职责 | 说明 |
|------|------|
| 自举与范围确定 | 读取 `project.json`、`status.json`，确定评分范围（全书/分卷/章节段） |
| 读取评分标准 | 加载 `config/scoring-criteria.json`，确认维度权重和rubric |
| 上下文聚合 | 按范围收集需评估的数据（chapters/、continuity/、characters/、world.md等） |
| 子Agent分发 | 按维度（或按章节分片）分发并行评分任务 |
| 分数计算与汇总 | 收集子Agent结果，按权重公式计算总分，映射等级 |
| 输出渲染 | 按指定输出模式（score-card/report/data）渲染结果 |
| 存储与同步 | 写入 `.sumeru/score/`，更新 `status.json` 中评分记录 |
| 改进建议 | 输出排序后的改进建议（高→低优先级） |
| **低分章节清单** | 按等级阈值筛选低于阈值的章节，写入 `score-snapshot.json.deficientChapters`，每章含维度/评分项/当前值/证据，供 `wq-revise` 消费 |

### subAgent 并行评分规则

**并行策略**：按**维度**分发，5个子Agent各评一个维度，并行运行。

| 子Agent | 输入 | 输出 |
|---------|------|------|
| 完整性评审 | chapters/、outline.md、chapters.json、continuity/foreshadowing | 结构、伏笔、章节完整性评分+评语 |
| 叙事质量评审 | chapters/、characters/、creative-anchors.md | 情节、人物、节奏、对话、张力评分+评语 |
| 创意性评审 | plan.md、outline.md、creative-anchors.md、chapters/ | 原创度、世界观、反转、套路突破评分+评语 |
| 技术执行评审 | chapters/、continuity/consistency-rules.json、review/anti-ai-scan.py输出 | 文笔、语法、一致性、格式、反AI评分+评语 |
| 市场契合评审 | plan.md（targetPlatform）、chapters/ | 类型、平台、留存、商业性评分+评语 |

**子Agent输出格式**（每个子Agent返回JSON）：

```json
{
  "dimensionId": "narrative",
  "items": [
    {
      "itemId": "plot_logic",
      "score": 5,
      "grade": "S",
      "evidence": "因果链完整无硬伤，所有事件均有合理动机",
      "issues": [],
      "suggestions": []
    },
    {
      "itemId": "character_development",
      "score": 4,
      "grade": "A",
      "evidence": "主角塑造扎实，配角有一定辨识度",
      "issues": ["配角苏瑾第30章后弧光不明显"],
      "suggestions": ["建议第30-35章给苏瑾增加一条独立目标线"]
    }
  ],
  "dimensionScore": 21,
  "dimensionMax": 25,
  "dimensionGrade": "A",
  "summary": "叙事质量优秀，人物塑造扎实，但节奏在第30-35章略拖",
  "strengthItems": ["plot_logic"],
  "weaknessItems": ["pacing"]
}
```

**父Agent合并规则**：
1. 按维度收集各子Agent评分
2. 每项得分 = 子Agent报告的score（1-5）
3. 维度分 = sum(各项得分 × 各项权重) × 100 / 5
4. 总分 = sum(各维度分 × 各维度权重)
5. 等级 = 总分 mapping to gradeThresholds
6. 全局强项 = 各子Agent报告的 strengthItems 中得分最高的
7. 全局弱项 = 各子Agent报告的 weaknessItems 中得分最低的
8. 改进建议 = 所有子Agent的 suggestions 按关联维度权重排序
9. **低分章节清单** = 遍历各子Agent返回的 per-chapter 评分（item 级 evidence 含 chapter 字段时），筛选低于 `gradeThresholds` 阈值的章节，聚合为 `deficientChapters`，每章 `deficiencies` 列出失分项（dimension + item + score + current/target + evidence）

**并行上限**：最大5个子Agent同时运行（每维度一个）。

## 输出级别

遵循 `wq-rules` quiet 规范：

```
# quiet:
═══ 须弥评分 ═══
总分: 85/100 → A（优秀）
  完整性 18/20 | 叙事 21/25 | 创意 17/20 | 技术 12/15 | 市场 17/20

# normal:
↑ + 各维度2行摘要 + 最强/最弱维度 + 3条改进建议

# verbose:
↑ + 完整报告逐项输出
```

## 自举协议

独立启动时执行：

1. **定位项目**：从当前目录向上查找 `.sumeru/project.json`
2. **确定范围**：从参数提取目标范围（默认全书）
3. **读取评分标准**：加载 `config/scoring-criteria.json`
4. **收集数据**：按范围收集 chapters/、continuity/、characters/、平面数据
5. **分发评分子Agent**：按维度并行启动5个子Agent
6. **汇总计算**：收集结果 → 权重公式 → 等级映射
7. **输出渲染**：按指定模式输出
8. **存储结果**：写入 `.sumeru/score/`

## 平台适配

评分维度中的"市场契合度"权重可根据 `project.json.targetPlatform` 自动调节（从 `config/scoring-criteria.json.platformStandards` 读取）：

| 目标平台 | 权重调整 | 说明 |
|---------|---------|------|
| 起点 | 叙事+5%（从完整性移入） | 重视长期追读和故事厚度 |
| 番茄 | 市场+5%（从技术移入） | 重视完读率和爽点密度 |
| 晋江 | 创意+5%（从技术移入） | 重视人设和情感张力 |
| 七猫 | 市场+5%（从技术移入） | 重视爽点和留存 |
| 纵横 | 完整+5%（从市场移入） | 重视稳定更新和长篇结构 |

## 与现有技能的集成

| 上游 | 关系 |
|------|------|
| `wq-polish` | score 检测到 weak 维度 → 可触发 polish 定向修复 |
| `wq-finalize` | score 结果可作为 build 前门禁（S/A级允许发布，B级建议先polish，C/D级阻断） |
| `wq-review` | score 复用 review 的 continuity check / foreshadowing tracking 数据 |
| `wq-worldbuilder` | 编排时在 `polish → finalize` 之间可选择插入 score 阶段 |
| `wq-revise`（下游） | score 输出 `deficientChapters` 字段供 revise 做评分驱动·收敛式修稿；**低分回头改的唯一合法入口是 revise，禁止 `score → write` 回环** |

## 版本历史

| 版本 | 变更 |
|------|------|
| 1.0.0 | 初始版本：五维评分模型、子Agent并行、score-card/report/data 三种输出模式 |
