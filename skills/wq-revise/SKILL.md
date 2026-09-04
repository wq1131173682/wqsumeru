---
name: wq-revise
description: 评分驱动·收敛式修稿——定向扩写/压缩/局部重写，硬重试上限+定向重评，杜绝无限循环
version: 1.0.0
type: skill
argument-hint: '[范围(全书/卷N/章节N-M)] [仅诊断] [上限N轮] [每章N次]'
disable-model-invocation: false
user-invocable: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, task
context: project
agent: build
---

> 依赖 `wq-rules`，默认 `quiet` 模式。
> 消费 `wq-score` 输出的 `.sumeru/score/score-snapshot.json` 中 `deficientChapters` 字段。

## 评分驱动·收敛式修稿

### 设计动机

`wq-score` 评出低分章节后，若直接调 `wq-write` 重写会产生**无限循环**：没有"已处理"记忆、没有每章重试上限、全书重评引发级联、没有收敛判定、子Agent自决范围、没有全局硬停。任意一条都足以把流程卡死。

`wq-revise` 是整套技能里**唯一带收敛约束**的修改技能。它把"评分不足回头改"从无约束的自由创作，变成带任务卡、已处理锁、定向重评、单调改进、硬重试上限、父Agent独占调度的收敛流程。**流程必然终止。**

### 触发场景

| 触发词 | 说明 |
|--------|------|
| "评分不足的章节修一下"、"按评分修稿"、"收敛式修稿"、"定向扩写不足章节" | 用户主动触发 |
| **worldbuilder 编排**：`score → finalize` 之间，若 snapshot 含低于阈值的章节 | 自动分支 |
| **手动定向**：`/wq-revise 第5章` | 只修指定章节 |

> **与 wq-write 重写的区别**：write 重写是自由创作契约，无收敛约束，子Agent可改全章；revise 是评分驱动 + 硬收敛 + scope 锁定，子Agent只能动任务卡 `scope` 内的段落。低分回头改的唯一合法入口是 revise，**禁止 `score → write` 回环**。

### 与现有技能边界

| 技能 | 契约性质 | 改动层 | 是否评分驱动 |
|------|---------|--------|-------------|
| `wq-write` 重写 | 自由创作，无收敛 | 任意 | 否 |
| `wq-review` fix | 检测驱动 | 剧情/逻辑/一致性 | 否（review 报告驱动） |
| `wq-polish` | 文笔风格优化 | 句式/用词/节奏感 | 否（风格驱动） |
| **`wq-revise`** | **评分驱动 + 硬收敛 + 硬停止** | **篇幅/局部叙事/伏笔回收** | **是（score snapshot）** |

边界规则：
- 句式/标点/反AI 句式重复 → 交回 `wq-polish`，revise 不接手（避免与 polish 职责重叠）
- 剧情 logic bug / 一致性冲突 → 交回 `wq-review` fix
- 创意性 / 市场契合度 不足 → revise **不自动修**，标 `escalate` 写入 plan 供人工决策（这两维不可逐章自动修复，强行修会引发新一轮循环）
- revise 只自动修：**字数不足（扩写）、节奏（压缩/重排）、局部叙事单薄（replace-segment）、伏笔回收（per-chapter patch）**

## 六大核心机制

### ① 诊断驱动，不靠"重写整章"

父Agent读 `.sumeru/score/score-snapshot.json` 的 `deficientChapters`，结合 `outlines/chapters.json` 与章节正文，把每章不足拆成结构化**修稿任务卡**。不是"重写第5章"，而是"第5章中段叙事单薄，3-8段扩写至目标字数"。

任务卡锁定：可改段落范围（`scope`）、允许操作（`allowedOps`）、禁止操作（`forbiddenOps`）、成功标准（`successCriterion`）、重试上限（`maxRetries`）。子Agent只能在此契约内动手。

### ② 已处理集合锁定（防重复）

`.sumeru/revise/revise-status.json` 记每章状态：`pending → in-progress → converged | best-effort | escalated | skipped`。一旦标记 `converged`/`best-effort`/`escalated`，**本轮修稿不再重挑**。新修稿轮次只挑仍低于阈值的章节。

### ③ 定向重评，不全书重评（防级联）

子Agent交稿后，父Agent只对**这一章**跑定向打分（调用 `wq-score` 的单章 data 模式，或内联轻量评分），不重评全书。改第5章不会触发第4章。级联被切断。

### ④ 单调改进 + 最佳快照（防震荡）

每章保留 `best-snapshots/{chapter}.md` 快照。每次重评：
- 比上次好 → 覆盖 best，`retryCount` 不增；
- 没变好 → `retryCount++`，**恢复 best 版本**再试下一轮；
- 震荡两次（一上一下）→ 立即冻结在 best，停手，标 `best-effort`。

直接杀死"反复扩写某几个章节"。

### ⑤ 每章硬重试上限 + 全局硬停

默认每章 `maxRetries = 2`，全书最多 `3` 轮修稿。撞到上限无论分数如何都进 finalize，写明 `best-effort` 原因。**流程必然终止。**

### ⑥ 父Agent独占调度权

子Agent绝不自决下一步。父Agent持有有序队列，派发 → 回收 → 定向验证 → 更新状态 → 派下一张卡。子Agent只返回修改后的文本 + 改动说明 + SUMERU_STATUS，**没有"我觉得还要改"的发言权**，**禁止再调度子Agent**（沿用 `subagent-rules.md` 第十部分）。

## 修稿任务卡 Schema

`.sumeru/revise/revise-plan.json`：

```json
{
  "planId": "revise-20260823T100000",
  "createdAt": "2026-08-23T10:00:00Z",
  "sourceScoreId": "score-20260823T090000",
  "globalMaxRounds": 3,
  "defaultMaxRetriesPerChapter": 2,
  "tasks": [
    {
      "taskId": "rev-015",
      "chapter": "015",
      "chapterFile": "chapters/015-拍卖会冲突.md",
      "deficiencies": ["字数不足", "叙事质量低"],
      "currentMetrics": { "wordCount": 1800, "narrative": 6.5 },
      "targetMetrics":  { "wordCount": 2500, "narrative": 7.5 },
      "allowedOps":    ["expand", "replace-segment"],
      "forbiddenOps":  ["rewrite-full", "change-plot", "change-ending-hook"],
      "scope": { "paragraphs": "3-8", "reason": "中段叙事单薄，冲突展开不足" },
      "maxRetries": 2,
      "successCriterion": "narrative>=7.5 AND wordCount>=2500",
      "protectedElements": ["主角必须展现判断力", "不能暴露真正实力"]
    },
    {
      "taskId": "rev-030",
      "chapter": "030",
      "chapterFile": "chapters/030-苏瑾的抉择.md",
      "deficiencies": ["伏笔回收"],
      "currentMetrics": { "foreshadowRecycled": false },
      "targetMetrics":  { "foreshadowRecycled": true },
      "allowedOps":   ["patch-foreshadow"],
      "forbiddenOps": ["change-plot", "rewrite-full"],
      "scope": { "anchor": "段落后插入1段回收v9伏笔", "paragraphs": "末段前" },
      "maxRetries": 2,
      "successCriterion": "foreshadow v9 recycled"
    },
    {
      "taskId": "rev-099",
      "chapter": "099",
      "deficiencies": ["创意性不足"],
      "action": "escalate",
      "reason": "创意维度不可逐章自动修复，需人工决策"
    }
  ]
}
```

### allowedOps 取值

| 操作 | 含义 | 适用缺陷 |
|------|------|---------|
| `expand` | 在 scope 段落内扩写，补足字数/叙事厚度 | 字数不足、叙事单薄 |
| `compress` | 压缩 scope 段落，提速 | 节奏过慢 |
| `restructure` | 重排 scope 段落顺序 | 节奏/张力问题 |
| `replace-segment` | 替换 scope 段落（保留情节骨架） | 局部叙事质量低 |
| `patch-foreshadow` | 在指定位置插入伏笔回收段 | 伏笔未回收 |
| `escalate` | 不自动修，写入 plan 供人工 | 创意性、市场契合度 |

### forbiddenOps 默认集

- `rewrite-full`：禁止整章重写（整章重写是 wq-write 的职责）
- `change-plot`：禁止改变已发生情节走向
- `change-ending-hook`：禁止改结尾钩子（除非钩子本身是被评缺陷）
- `change-character-arc`：禁止改既定人物弧光

## 修稿状态 Schema

`.sumeru/revise/revise-status.json`：

```json
{
  "planId": "revise-20260823T100000",
  "globalRound": 1,
  "globalMaxRounds": 3,
  "chapters": {
    "015": {
      "status": "converged",
      "retryCount": 1,
      "bestSnapshot": "best-snapshots/015.md",
      "bestMetrics": { "wordCount": 2520, "narrative": 7.6 },
      "history": [
        { "round": 1, "retry": 0, "metrics": {"wordCount":1800,"narrative":6.5}, "verdict": "improved-keep" }
      ]
    },
    "030": {
      "status": "best-effort",
      "retryCount": 2,
      "bestSnapshot": "best-snapshots/030.md",
      "bestMetrics": { "foreshadowRecycled": true },
      "stopReason": "max-retries-reached"
    },
    "099": {
      "status": "escalated",
      "reason": "创意性不可自动修"
    }
  }
}
```

### 章节状态流转

```
pending → in-progress → converged      （达 successCriterion）
                     → best-effort     （撞 maxRetries，冻结 best）
                     → escalated       （不可自动修，交人工）
                     → skipped         （用户/诊断跳过）
```

`converged` / `best-effort` / `escalated` / `skipped` 均为**终态**，本轮不再重挑。

## 收敛门（Convergence Gate）

子Agent交稿后，父Agent按序执行：

1. **文件路径校验**：文件名符合 `{三位章节号}-{标题}.md`（沿用 wq-write 规则），异常文件名删除并报错终止。
2. **scope 校验**：比对改动是否越出 `scope.paragraphs`。越界改动 → 回退到 best，`retryCount++`，记录 issue。
3. **protectedElements 校验**：比对 SUMERU_STATUS 与 protectedElements，违反 → 回退 best，`retryCount++`。
4. **定向重评**：只对本章跑评分（`wq-score 第N章 data` 或内联轻量评分），不重评全书。
5. **判定**：
   - 达 `successCriterion` 且优于 best → 覆盖 best，标 `converged`；
   - 优于 best 但未达 criterion → 覆盖 best，`retryCount` 不增，若 `retryCount < maxRetries` 续派下一轮（带 refined 诊断），否则标 `best-effort`；
   - 不优于 best → 恢复 best，`retryCount++`，震荡计数 +1；震荡计数 ≥ 2 → 立即冻结 best，标 `best-effort`；
   - `retryCount >= maxRetries` → 标 `best-effort`，记 `stopReason`。
6. **回归扫描（修订后强制）**：对改过的章节跑轻量回归，防止 polish/revise 改稿重新引入 AI 句式/标点/一致性问题：
   - `python skills/wq-review/scripts/anti-ai-scan.py chapters --chapters <本章> --output .sumeru/revise --quiet`；退出码 2（阻断）→ 回退 best，`retryCount++`，记 issue；退出码 1（warning）→ 写入 `.sumeru/issues.md`，不阻断；
   - `python skills/wq-review/scripts/continuity-check.py .sumeru/continuity --chapters <本章> --quiet`（分卷模式先 `export SUMERU_CURRENT_VOLUME=vol-N`，输入 `.sumeru/volumes/vol-N/continuity`）；critical 冲突 → 回退 best，`retryCount++`；
   - 回归扫描与定向重评（第 4 步）可合并为一次子Agent回收后的双校验：先回归扫描通过，再跑定向重评。
7. **写回**：converged/best-effort 才把 best 版本写回 `chapters/`；写前备份原稿到 `.sumeru/revise/original/`。

## 全局硬停

- `globalRound` 每完成一轮（所有 pending 任务各跑一次）+1；
- `globalRound >= globalMaxRounds` → 无论是否全 converged，强制收尾，剩余 pending 标 `best-effort`，进 finalize；
- 用户可用 `上限N轮` 覆盖 `globalMaxRounds`。

## 轻量字数路径（v1.4.4 新增）

**适用场景**：任务 deficiencies **只有** `["字数不足"]`（无叙事/节奏/伏笔等其他缺陷）。

**为什么需要**：纯字数不足是量变不是质变，跑完整收敛门（定向重评 + anti-ai 回归 + continuity 检查 + best-snapshot）是过度工程，每章平均多花 2-3 轮。轻量路径一次性搞定，节省 60%+ 修稿时间。

**流程**：
1. 诊断阶段自动识别：`deficiencies == ["字数不足"]` → 标 `mode=lightweight`
2. 派发子 Agent：context pack 注入 `mode=lightweight`，指示"按缺口比例扩写 scope 段落"
3. 回收后**跳过收敛门**（不跑定向重评、不回写 best-snapshot、不跑 anti-ai 回归）
4. 只做单一验证：父Agent读 `chapters/{chapter}.md`，用 `len(re.findall(r"[\u4e00-\u9fa5]", body))` 计数汉字数，≥ target 即标 `converged`，否则标 `best-effort`
5. 直接写回 chapters/，回写 revise-status.json

**效果对比**：
| 路径 | 单章往返 | 检查项 | 适用场景 |
|------|---------|--------|---------|
| 轻量路径 | 1 轮 | 字数验证 | 纯字数不足 |
| 收敛门 | 1-2 轮 | 定向重评 + anti-ai + continuity | 叙事/节奏/伏笔等质量缺陷 |

> 如果任务同时含 `字数不足` 和其他缺陷（如 `["字数不足", "叙事质量低"]`），走**收敛门**，不走轻量路径——因为质量缺陷需要多轮迭代才能收敛。

## 收尾：快照回写

所有任务达终态后，父Agent**回写全局 `score-snapshot.json`**，避免下游 finalize/worldbuilder 看到修稿前的失真快照：

1. 遍历 `revise-status.json.chapters`，对每个 `converged`/`best-effort` 章节：
   - 在 `score-snapshot.json.deficientChapters` 中找到对应 `chapter` 项；
   - 用 `bestMetrics` 更新该项的 `currentMetrics` / 评分 / `totalScore`，并把 `deficiencies` 中已解决项标记 `resolved: true`；
   - `best-effort` 章节额外写 `stopReason`（`max-retries-reached` / `oscillation-frozen`）。
2. 重算 snapshot 的 `total` / `weakestDimension` / `strongestDimension`（按更新后的章节分重新聚合）。
3. `escalated` 章节**不更新**指标（未改），但在该项追加 `escalated: true` + `reason`，供 finalize 门禁识别。
4. 回写后追加 `.sumeru/changelog.md`：`ℹ️ revise: 回写 {n} 章 best 指标到 score-snapshot，{m} 章 escalated 待人工`。

> 若 revise 未运行（无 deficientChapters）或用户手动跳过，snapshot 保持 score 原样，不回写。

## 子Agent调度协议

### 父Agent职责

| 职责 | 说明 |
|------|------|
| 诊断 | 读 score snapshot + chapters + outlines，生成 revise-plan.json；按 deficiencies 分类任务：纯 `字数不足` → `mode=lightweight`，其他 → `mode=convergence` |
| 队列管理 | 按 taskId 顺序派发，维护已处理锁，绝不重挑终态章节；lightweight 任务优先排（一次过，不占收敛门轮次） |
| context pack 生成 | 每任务生成 `shared-revise.md` + `cards-rev-{chapter}.md`，注入任务卡 + scope 段落原文 + protectedElements；lightweight 任务额外注入 `mode=lightweight` 和缺口比例 |
| 派发 | 最多 3 个子Agent并行（沿用 wq-rules 上限），每子Agent只负责 1 个章节的 1 张任务卡；lightweight 任务可提高到 5 并发（无质量风险） |
| 轻量路径回收 | 字数验证 ≥ target → 直接标 `converged`，写回；< target → 标 `best-effort`，不重试 |
| 收敛门 | 回收后执行上文六步校验与判定（仅 mode=convergence 任务） |
| 写回与备份 | 仅 best/converged 写回 chapters/，写前备份到 `.sumeru/revise/original/` |
| 状态同步 | 更新 revise-status.json、status.json、changelog、issues（escalated 项） |
| 全局硬停判定 | 每轮末检查 globalRound，撞顶强制收尾 |

### 子Agent契约

子Agent读取 `shared-revise.md` + `cards-rev-{chapter}.md`，**只读这两个文件 + 不许 Glob/Grep/Read 搜索项目目录**（沿用 `subagent-rules.md`）。输出：

- 修改后的**完整章节正文**（首行含 `<!-- SUMERU_STATUS: ... -->`，state_diff 只含本次 scope 内变更）；
- 末尾附 `## REVISE_NOTE`：用 2-4 行说明改了哪几段、用了什么 op、为什么这样改。

子Agent**禁止**：
- 改 `scope` 外段落；
- 改 `forbiddenOps` 列出的内容；
- 再调度子Agent；
- 输出"建议再改"之类发言（收敛判定归父Agent）。

### context pack 注入格式

`shared-revise.md` 头部：
```markdown
## 修稿任务（评分驱动·收敛式）
- 源评分: {scoreId}
- 本章当前: 字数 {w} / 叙事 {n}
- 目标: 字数 {tw} / 叙事 {tn}
- 允许操作: {allowedOps}
- 禁止操作: {forbiddenOps}
- scope: 第 {paragraphs} 段（{reason}）
- protectedElements: {列表}
- 重试上限: {maxRetries}（父Agent判定收敛，你只管这一轮）
- 模式: {mode}  ← lightweight(只扩字数) / convergence(全量修复)
```

`cards-rev-{chapter}.md`：scope 段落原文 + 上下各 1 段衔接 + 评分失分证据摘录（来自 score report 的 issues/suggestions）。

## 自举协议

独立启动时：

1. **定位项目**：向上查找 `.sumeru/project.json`。
2. **加载评分来源**：读 `.sumeru/score/score-snapshot.json`；不存在 → 报错终止并提示先跑 `/wq-score`。
3. **筛选任务**：从 `deficientChapters` 取低于阈值的章节；用户指定范围则取交集；`仅诊断` 模式只生成 plan 不执行。
4. **诊断分类**：按缺陷映射 allowedOps，创意/市场类标 `escalate`。
5. **生成 revise-plan.json**：含 tasks、maxRetries（默认 2）、globalMaxRounds（默认 3）。
6. **初始化 revise-status.json**：所有任务标 `pending`，`globalRound=0`。
7. **派发执行**：按队列派子Agent，回收跑收敛门，更新状态。
8. **全局硬停**：每轮末检查，撞顶收尾。
9. **收尾**：所有终态后回写 chapters/（已逐章写过）、status.json（`currentStage` 推进，章节状态保持 `polished`，revise 不改章节状态机值，仅在 revise-status 标记）、changelog、issues（escalated 项）。

> revise 不把章节状态从 `polished` 推到别的值；它是 `polished → finalize` 之间的**质量修补层**，章节状态机的正式推进仍由 finalize 接管。

## 触发与参数

```bash
/wq-revise                    # 读最新 score snapshot，修所有低分章节
/wq-revise 第5章              # 只修指定章节（须在 deficientChapters 内）
/wq-revise 第5-8章            # 范围修
/wq-revise 卷2                # 分卷模式：修卷2低分章节
/wq-revise 仅诊断             # 只生成 revise-plan.json 不执行
/wq-revise 上限4轮            # 覆盖 globalMaxRounds=4
/wq-revise 每章3次            # 覆盖 maxRetries=3
```

## 输出级别

遵循 `wq-rules` quiet 规范：

```
# quiet:
═══ 修稿 ═══
计划: 5 章需修（扩写3 / 压缩1 / 伏笔1）｜全局上限 3 轮｜每章上限 2 次
[轮1] 第5章 converged (叙事 6.5→7.6)  第12章 best-effort (字数仍不足)
✅ 收敛: 4/5｜best-effort: 1｜escalate: 0

# normal:
↑ + 每章 retryCount + best 指标 + 未达 criterion 的差距

# verbose:
↑ + 每轮每章判定明细 + 子Agent REVISE_NOTE
```

## 数据持久化

**中间数据** `.sumeru/revise/`：
- `revise-plan.json`：修稿任务卡队列
- `revise-status.json`：每章状态 + retryCount + best 指标 + history
- `best-snapshots/{chapter}.md`：每章最佳版本快照
- `original/`：写回前的原稿备份（按章节）
- `revise-report.md`：收尾报告（按需，verbose 模式生成）

**用户可见输出**：`chapters/` 下被修章节的最终正文（best 版本）。

## 分卷模式支持

- 诊断阶段读 `.sumeru/score/score-snapshot.json`（全局），不受卷作用域影响；
- context pack 数据源沿用 `wq-write` 分卷规则：`project.json.volumeCount >= 2` 时从 `.sumeru/volumes/vol-N/` 取 continuity/characters/cache；
- 跨卷伏笔回收任务（`patch-foreshadow` 涉及他卷伏笔）→ 额外查 `.sumeru/cross-volume/dependency-table.md`，不预加载全量；
- 调用 continuity 脚本前 `export SUMERU_CURRENT_VOLUME=vol-N`（沿用 wq-write 约定）。

## 与现有技能的集成

| 上下游 | 关系 |
|--------|------|
| `wq-score`（上游） | 消费其 `score-snapshot.json.deficientChapters` 字段 |
| `wq-write` | revise 用 `expand`/`replace-segment` 时复用 write 子Agent 调用模板，但加 scope 锁 + forbiddenOps |
| `wq-review` | revise 的 `patch-foreshadow` 回收后调 `foreshadowing-tracker.py` 验证回收状态 |
| `wq-polish` | 句式/反AI 类缺陷不接手，回交 polish |
| `wq-worldbuilder`（下游） | 编排链 `polish → score → [revise?] → finalize`，revise 完成后进 finalize |
| `wq-finalize` | revise 收尾（converged/best-effort）后才允许进 finalize；escalated 项写入 issues 供 finalize 报告 |

## 版本历史

| 版本 | 变更 |
|------|------|
| 1.0.0 | 初始版本：六机制（诊断驱动 / 已处理锁 / 定向重评 / 单调改进+best快照 / 硬重试上限+全局硬停 / 父Agent独占调度）；revise-plan 与 revise-status schema；收敛门六步校验；默认每章 2 次 / 全局 3 轮 |
