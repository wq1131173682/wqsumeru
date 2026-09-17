# canonical 路径一致性检查

来源：`wq-rules/SKILL.md` §Canonical 路径（L387-402）

## 各路径形态出现情况

| 概念 | 路径形态 | 次数 | 文件数 |
|---|---|---|---|
| 审查报告 | `.sumeru/review/` | 8 | 2 |
| 审查报告 | `reviews/review-report.md` | 4 | 2 |
| 章节任务卡 | `.sumeru/outlines/chapters.json` | 1 | 1 |
| 章节任务卡 | `outlines/chapters.json` | 57 | 11 |
| 章节细纲目录 | `.sumeru/outline/` | 9 | 3 |
| 章节细纲目录 | `outlines/` | 68 | 11 |
| 简介 | `.sumeru/intro.md` | 16 | 5 |
| 简介 | `intro.md` | 4 | 2 |
| 问题清单 | `.sumeru/issues.md` | 21 | 8 |
| 问题清单 | `.sumeru/issues/index.json` | 6 | 3 |

## 明细

### [审查报告] `.sumeru/review/`（8 处）

| 文件 | 行 | 原文 |
|---|---|---|
| `skills/wq-review/SKILL.md` | 60 | `- 输出 `.sumeru/review/reverify-result.json`` |
| `skills/wq-review/SKILL.md` | 206 | `- `.sumeru/review/anti-ai-report.json`：结构化报告` |
| `skills/wq-review/SKILL.md` | 207 | `- `.sumeru/review/anti-ai-report.md`：人工可读报告` |
| `skills/wq-review/SKILL.md` | 471 | `- `.sumeru/review/global-issues.json`：全局问题清单` |
| `skills/wq-review/SKILL.md` | 472 | `- `.sumeru/review/fix-plan.json`：重写修复计划` |
| `skills/wq-write/SKILL.md` | 426 | `4. `.sumeru/review/fix-plan.json` 中的重写要求` |
| `skills/wq-write/SKILL.md` | 481 | `**扫描报告写入** `.sumeru/review/anti-ai-report.json` 与 `.sumeru/review/anti-ai-report.md`（路径以脚本实际输出为准，旧版 `.sumeru/w` |
| `skills/wq-write/SKILL.md` | 481 | `**扫描报告写入** `.sumeru/review/anti-ai-report.json` 与 `.sumeru/review/anti-ai-report.md`（路径以脚本实际输出为准，旧版 `.sumeru/w` |

### [审查报告] `reviews/review-report.md`（4 处）

| 文件 | 行 | 原文 |
|---|---|---|
| `skills/wq-review/SKILL.md` | 35 | `\| `short/light` \| 单文件`reviews/review-report.md`，检查结构、人物动机、反转合理性\|` |
| `skills/wq-review/SKILL.md` | 36 | `\| `medium/standard` \| `reviews/review-report.md`，问题记录到 `.sumeru/issues.md` \|` |
| `skills/wq-review/SKILL.md` | 467 | `- `reviews/review-report.md`：用户可读审查报告` |
| `skills/wq-rules/SKILL.md` | 399 | `\| 审查摘要 \| `reviews/review-report.md` \| 按需生成 \|` |

### [章节任务卡] `.sumeru/outlines/chapters.json`（1 处）

| 文件 | 行 | 原文 |
|---|---|---|
| `skills/wq-finalize/SKILL.md` | 236 | `2. **`.sumeru/outlines/chapters.json`**：同上，新路径` |

### [章节任务卡] `outlines/chapters.json`（57 处）

| 文件 | 行 | 原文 |
|---|---|---|
| `skills/wq-finalize/SKILL.md` | 235 | `1. **`outlines/chapters.json`**：每章的 `volume` 或 `vol` 字段` |
| `skills/wq-finalize/SKILL.md` | 282 | `如需启用按卷导出，在 `outlines/chapters.json` 中为每章添加 `volume` 字段：` |
| `skills/wq-migrate/SKILL.md` | 67 | `\| `.sumeru/outline/chapter-outlines.json` \| `outlines/chapters.json` \| 读取旧文件，合并到新文件 \|` |
| `skills/wq-migrate/SKILL.md` | 75 | ``outlines/chapters.json` 每章必须包含以下 15 个必填字段：` |
| `skills/wq-migrate/SKILL.md` | 132 | `\| `outlines/chapters.json` 字段完整性 \| 全部 \| 已在 1.4 处理；接续阶段不再重复 \|` |
| `skills/wq-migrate/SKILL.md` | 150 | `\| 扁平 `outlines/chapters.json` 含 150+ 章 \| 提供可选子模式：将全局 chapters.json 按卷拆分到 `vol-N/outlines/chapters.json`（per-vo` |
| `skills/wq-migrate/SKILL.md` | 150 | `\| 扁平 `outlines/chapters.json` 含 150+ 章 \| 提供可选子模式：将全局 chapters.json 按卷拆分到 `vol-N/outlines/chapters.json`（per-vo` |
| `skills/wq-migrate/SKILL.md` | 200 | `├─ 可选：拆分 outlines/chapters.json 到 per-volume` |
| `skills/wq-migrate/SKILL.md` | 250 | `4. 写入 outlines/chapters.json` |
| `skills/wq-migrate/SKILL.md` | 351 | `\| .sumeru/outline/chapter-outlines.json \| outlines/chapters.json \| ✅已迁移/ ⚠️ 需手动处理 \|` |
| `skills/wq-migrate/SKILL.md` | 451 | `- `.sumeru/volumes/vol-N/outlines/chapters.json`：每卷章节任务卡（可选拆分，按用户确认）` |
| `skills/wq-migrate/SKILL.md` | 522 | `│   ├─ 询问用户：是否将 outlines/chapters.json 按卷拆分到 per-volume 副本？` |
| `skills/wq-migrate/SKILL.md` | 525 | `│   │     ├─ 写入 vol-N/outlines/chapters.json` |
| `skills/wq-migrate/SKILL.md` | 526 | `│   │     └─ 保留根级 outlines/chapters.json 作为单一来源（per-volume 是缓存镜像）` |
| `skills/wq-migrate/SKILL.md` | 621 | `**核心原则**：`outlines/chapters.json`（全局）始终是**单一真相源（single source of truth）**；`vol-N/outlines/chapters.json` 是**按卷` |
| `skills/wq-migrate/SKILL.md` | 621 | `**核心原则**：`outlines/chapters.json`（全局）始终是**单一真相源（single source of truth）**；`vol-N/outlines/chapters.json` 是**按卷` |
| `skills/wq-migrate/SKILL.md` | 624 | `1. 如 `vol-N/outlines/chapters.json` 存在 → 优先使用（per-volume）` |
| `skills/wq-migrate/SKILL.md` | 625 | `2. 否则回退到全局 `outlines/chapters.json` 并按 `chapter` 字段过滤` |
| `skills/wq-migrate/SKILL.md` | 630 | `const globalChapters = readJSON('outlines/chapters.json');` |
| `skills/wq-migrate/SKILL.md` | 634 | `writeJSON(`vol-N/outlines/chapters.json`, slice);` |
| `skills/wq-migrate/SKILL.md` | 637 | `**不拆分场景**：用户拒绝、章节数 < 200、或 `outlines/chapters.json` 字段不完整（先执行 1.4 字段补全）。` |
| `skills/wq-outline/references/volume-chapter-split.md` | 277 | `然后依据此规划表生成 `outlines/chapters.json` 的每章任务卡。` |
| `skills/wq-outline/SKILL.md` | 24 | `5. 大纲完成后生成或刷新 `outlines/chapters.json`；长篇项目同步拆分6. 同步生成 `characters/` 人物卡7. 若 `project.json.volumeCount ≥ 2`，执行` |
| `skills/wq-outline/SKILL.md` | 29 | `\| `medium/standard` \| `plan.md`、`outline.md`、`outlines/chapters.json`、`characters/` \|` |
| `skills/wq-outline/SKILL.md` | 30 | `\| `long/full` \| `plan.md`、`outline.md`、`outlines/chapters.json`、`characters/`、`world.md`，必要时拆分章节任务卡\|` |
| `skills/wq-outline/SKILL.md` | 45 | `- 主 `outlines/chapters.json` 仍保留所有章节的完整任务卡（全局统一索引）` |
| `skills/wq-outline/SKILL.md` | 49 | `### 项目化输出要求- `plan.md`：需求、世界观、人物、风格、创意策略、术语合并维护- `outline.md`：故事架构、主线、支线、分卷规划、关键高潮、伏笔管理表、节奏规划- `outlines/chapt` |
| `skills/wq-outline/SKILL.md` | 52 | `> ⚠️ 生成 `outlines/chapters.json` 后必须执行章节任务卡输出验证质量门禁，缺字段不标记完成。` |
| `skills/wq-outline/SKILL.md` | 53 | `### 章节任务卡格式（`outlines/chapters.json`）` |
| `skills/wq-outline/SKILL.md` | 101 | ``outlines/chapters.json` 生成后，父Agent必须执行以下验证，全部通过才允许标记 `outline` 阶段完成）` |
| `skills/wq-outline/SKILL.md` | 192 | `- 模板ID写入 `outlines/chapters.json` 每章任务卡的 `emotionalBeatTemplate` 字段` |
| `skills/wq-outline/SKILL.md` | 368 | `### 数据持久化**用户可见输出**）- `plan.md`、`outline.md`、`outlines/chapters.json`、`characters/`、`world.md`` |
| `skills/wq-polish/SKILL.md` | 144 | `- `outlines/chapters.json` 的`acceptanceCriteria` 已满足的内容` |
| `skills/wq-review/SKILL.md` | 29 | `3. 若缺少`outlines/chapters.json`，按旧路径兼容策略处理（见`wq-rules/SKILL.md` 第六部分"独立调用自举协议"）` |
| `skills/wq-review/SKILL.md` | 200 | `[--outlines outlines/chapters.json] \` |
| `skills/wq-revise/SKILL.md` | 55 | `父Agent读 `.sumeru/score/score-snapshot.json` 的 `deficientChapters`，结合 `outlines/chapters.json` 与章节正文，把每章不足拆成结构化` |
| `skills/wq-rules/SKILL.md` | 128 | `\| `.sumeru/outline/chapter-outlines.json` \| `outlines/chapters.json` \| 章节任务单\|` |
| `skills/wq-rules/SKILL.md` | 189 | `\| 直接写入正文章节文件 \| 正文写入 `chapters/*.md`，细纲写入 `outlines/chapters.json`，无需经父Agent透传 \|` |
| `skills/wq-rules/SKILL.md` | 326 | `**跨卷引用**：仅当 `outlines/chapters.json` 目标章节的 `protectedElements` 或伏笔涉及跨卷依赖表中注册的项时，才从 `cross-volume/dependency-ta` |
| `skills/wq-rules/SKILL.md` | 393 | `\| 大纲/任务单\| `outline.md`、`outlines/chapters.json` \| `.sumeru/outline/chapter-outlines.json` 只读兼容 \|` |

### [章节细纲目录] `.sumeru/outline/`（9 处）

| 文件 | 行 | 原文 |
|---|---|---|
| `skills/wq-migrate/SKILL.md` | 67 | `\| `.sumeru/outline/chapter-outlines.json` \| `outlines/chapters.json` \| 读取旧文件，合并到新文件 \|` |
| `skills/wq-migrate/SKILL.md` | 95 | `**修复方式**：- 缺字段→件`.sumeru/outline/chapter-XXX-YYY.md` 回退补充` |
| `skills/wq-migrate/SKILL.md` | 248 | `1. 读取 .sumeru/outline/chapter-outlines.json` |
| `skills/wq-migrate/SKILL.md` | 351 | `\| .sumeru/outline/chapter-outlines.json \| outlines/chapters.json \| ✅已迁移/ ⚠️ 需手动处理 \|` |
| `skills/wq-outline/SKILL.md` | 370 | `**中间数据（`.sumeru/outline/`）*）- 仅保存必要缓存；旧版 `world.json`、`characters.json`、`plot-outline.json`、`chapter-outlines.` |
| `skills/wq-rules/SKILL.md` | 128 | `\| `.sumeru/outline/chapter-outlines.json` \| `outlines/chapters.json` \| 章节任务单\|` |
| `skills/wq-rules/SKILL.md` | 381 | `5. **兼容输入**：旧版`.sumeru/outline/chapter-outlines.json` 只读兼容` |
| `skills/wq-rules/SKILL.md` | 393 | `\| 大纲/任务单\| `outline.md`、`outlines/chapters.json` \| `.sumeru/outline/chapter-outlines.json` 只读兼容 \|` |
| `skills/wq-rules/SKILL.md` | 408 | `\| `.sumeru/outline/chapter-outlines.json` \| 读取时自动映射到 `outlines/chapters.json` \| 下次写入时迁移\|` |

### [章节细纲目录] `outlines/`（68 处）

| 文件 | 行 | 原文 |
|---|---|---|
| `skills/wq-finalize/SKILL.md` | 235 | `1. **`outlines/chapters.json`**：每章的 `volume` 或 `vol` 字段` |
| `skills/wq-finalize/SKILL.md` | 282 | `如需启用按卷导出，在 `outlines/chapters.json` 中为每章添加 `volume` 字段：` |
| `skills/wq-migrate/SKILL.md` | 41 | `\| `.sumeru/status.json` 不存在\| 扫描 chapters/ 和outlines/ 推断状态\|` |
| `skills/wq-migrate/SKILL.md` | 52 | `\| `outlines/` 不存在\| 创建空目录\|` |
| `skills/wq-migrate/SKILL.md` | 67 | `\| `.sumeru/outline/chapter-outlines.json` \| `outlines/chapters.json` \| 读取旧文件，合并到新文件 \|` |
| `skills/wq-migrate/SKILL.md` | 75 | ``outlines/chapters.json` 每章必须包含以下 15 个必填字段：` |
| `skills/wq-migrate/SKILL.md` | 132 | `\| `outlines/chapters.json` 字段完整性 \| 全部 \| 已在 1.4 处理；接续阶段不再重复 \|` |
| `skills/wq-migrate/SKILL.md` | 150 | `\| 扁平 `outlines/chapters.json` 含 150+ 章 \| 提供可选子模式：将全局 chapters.json 按卷拆分到 `vol-N/outlines/chapters.json`（per-vo` |
| `skills/wq-migrate/SKILL.md` | 150 | `\| 扁平 `outlines/chapters.json` 含 150+ 章 \| 提供可选子模式：将全局 chapters.json 按卷拆分到 `vol-N/outlines/chapters.json`（per-vo` |
| `skills/wq-migrate/SKILL.md` | 200 | `├─ 可选：拆分 outlines/chapters.json 到 per-volume` |
| `skills/wq-migrate/SKILL.md` | 250 | `4. 写入 outlines/chapters.json` |
| `skills/wq-migrate/SKILL.md` | 347 | `\| outlines/ \| ✅已存在/ 🔧 已创建\|` |
| `skills/wq-migrate/SKILL.md` | 351 | `\| .sumeru/outline/chapter-outlines.json \| outlines/chapters.json \| ✅已迁移/ ⚠️ 需手动处理 \|` |
| `skills/wq-migrate/SKILL.md` | 451 | `- `.sumeru/volumes/vol-N/outlines/chapters.json`：每卷章节任务卡（可选拆分，按用户确认）` |
| `skills/wq-migrate/SKILL.md` | 509 | `│   │     .sumeru/volumes/vol-N/outlines/    （可选，按 D 执行）` |
| `skills/wq-migrate/SKILL.md` | 522 | `│   ├─ 询问用户：是否将 outlines/chapters.json 按卷拆分到 per-volume 副本？` |
| `skills/wq-migrate/SKILL.md` | 525 | `│   │     ├─ 写入 vol-N/outlines/chapters.json` |
| `skills/wq-migrate/SKILL.md` | 526 | `│   │     └─ 保留根级 outlines/chapters.json 作为单一来源（per-volume 是缓存镜像）` |
| `skills/wq-migrate/SKILL.md` | 621 | `**核心原则**：`outlines/chapters.json`（全局）始终是**单一真相源（single source of truth）**；`vol-N/outlines/chapters.json` 是**按卷` |
| `skills/wq-migrate/SKILL.md` | 621 | `**核心原则**：`outlines/chapters.json`（全局）始终是**单一真相源（single source of truth）**；`vol-N/outlines/chapters.json` 是**按卷` |
| `skills/wq-migrate/SKILL.md` | 624 | `1. 如 `vol-N/outlines/chapters.json` 存在 → 优先使用（per-volume）` |
| `skills/wq-migrate/SKILL.md` | 625 | `2. 否则回退到全局 `outlines/chapters.json` 并按 `chapter` 字段过滤` |
| `skills/wq-migrate/SKILL.md` | 630 | `const globalChapters = readJSON('outlines/chapters.json');` |
| `skills/wq-migrate/SKILL.md` | 634 | `writeJSON(`vol-N/outlines/chapters.json`, slice);` |
| `skills/wq-migrate/SKILL.md` | 637 | `**不拆分场景**：用户拒绝、章节数 < 200、或 `outlines/chapters.json` 字段不完整（先执行 1.4 字段补全）。` |
| `skills/wq-outline/references/volume-chapter-split.md` | 277 | `然后依据此规划表生成 `outlines/chapters.json` 的每章任务卡。` |
| `skills/wq-outline/SKILL.md` | 24 | `5. 大纲完成后生成或刷新 `outlines/chapters.json`；长篇项目同步拆分6. 同步生成 `characters/` 人物卡7. 若 `project.json.volumeCount ≥ 2`，执行` |
| `skills/wq-outline/SKILL.md` | 29 | `\| `medium/standard` \| `plan.md`、`outline.md`、`outlines/chapters.json`、`characters/` \|` |
| `skills/wq-outline/SKILL.md` | 30 | `\| `long/full` \| `plan.md`、`outline.md`、`outlines/chapters.json`、`characters/`、`world.md`，必要时拆分章节任务卡\|` |
| `skills/wq-outline/SKILL.md` | 45 | `- 主 `outlines/chapters.json` 仍保留所有章节的完整任务卡（全局统一索引）` |
| `skills/wq-outline/SKILL.md` | 49 | `### 项目化输出要求- `plan.md`：需求、世界观、人物、风格、创意策略、术语合并维护- `outline.md`：故事架构、主线、支线、分卷规划、关键高潮、伏笔管理表、节奏规划- `outlines/chapt` |
| `skills/wq-outline/SKILL.md` | 52 | `> ⚠️ 生成 `outlines/chapters.json` 后必须执行章节任务卡输出验证质量门禁，缺字段不标记完成。` |
| `skills/wq-outline/SKILL.md` | 53 | `### 章节任务卡格式（`outlines/chapters.json`）` |
| `skills/wq-outline/SKILL.md` | 101 | ``outlines/chapters.json` 生成后，父Agent必须执行以下验证，全部通过才允许标记 `outline` 阶段完成）` |
| `skills/wq-outline/SKILL.md` | 192 | `- 模板ID写入 `outlines/chapters.json` 每章任务卡的 `emotionalBeatTemplate` 字段` |
| `skills/wq-outline/SKILL.md` | 347 | `**细纲输出格式（写入`outlines/chapter-XXX-YYY.md`）*）` |
| `skills/wq-outline/SKILL.md` | 368 | `### 数据持久化**用户可见输出**）- `plan.md`、`outline.md`、`outlines/chapters.json`、`characters/`、`world.md`` |
| `skills/wq-polish/SKILL.md` | 144 | `- `outlines/chapters.json` 的`acceptanceCriteria` 已满足的内容` |
| `skills/wq-review/SKILL.md` | 29 | `3. 若缺少`outlines/chapters.json`，按旧路径兼容策略处理（见`wq-rules/SKILL.md` 第六部分"独立调用自举协议"）` |
| `skills/wq-review/SKILL.md` | 200 | `[--outlines outlines/chapters.json] \` |

### [简介] `.sumeru/intro.md`（16 处）

| 文件 | 行 | 原文 |
|---|---|---|
| `skills/wq-finalize/SKILL.md` | 58 | `- 若存在 `.sumeru/intro.md`，将简介写入各导出版本的开头` |
| `skills/wq-finalize/SKILL.md` | 334 | `- `.sumeru/intro.md`：小说简介（大纲完成后自动生成）` |
| `skills/wq-migrate/SKILL.md` | 127 | `\| `.sumeru/intro.md` \| 全部 \| 进入 H2：推断生成 300-500 字简介，标记 `pending` \|` |
| `skills/wq-migrate/SKILL.md` | 367 | `\| H2 intro \| `.sumeru/intro.md` \| ✅已推断 / ⏭️skipped / ❌失败 \| 字数 {n} \|` |
| `skills/wq-migrate/SKILL.md` | 388 | `cat .sumeru/intro.md      # 校对` |
| `skills/wq-migrate/SKILL.md` | 721 | `\| **H2** \| `.sumeru/intro.md` 是否存在 \| 从 `plan.md` 提取标题/受众/主角名，从 `outline.md` 提取主线冲突，生成 300-500 字简介，标记 `pending`` |
| `skills/wq-migrate/SKILL.md` | 832 | `cat .sumeru/intro.md` |
| `skills/wq-outline/SKILL.md` | 402 | `- **后续**：`.sumeru/intro.md` 可供 `wq-finalize` 在发布导出时复用简介；`wq-write` 可参考其中的传播句作为章节结尾钩子；`characters/` 和`world.md`` |
| `skills/wq-rules/SKILL.md` | 79 | `\| `outline` →`anchor` \| `outline.md`、`chapters.json`、`.sumeru/intro.md` 存在 \|` |
| `skills/wq-rules/SKILL.md` | 106 | `\| `.sumeru/intro.md` \| 小说简介 \|` |
| `skills/wq-rules/SKILL.md` | 394 | `\| 简介 \| `.sumeru/intro.md` \| 无\|` |
| `skills/wq-worldbuilder/SKILL.md` | 31 | `2.6 **简介生成**：大纲完成后自动生成 `.sumeru/intro.md`（作品名称、目标读者、类型标签、主角名、简介正文、平台标签映射）` |
| `skills/wq-worldbuilder/SKILL.md` | 70 | `\| `medium/standard` \| `README.md`、`plan.md`、`outline.md`、`outlines/chapters.json`、`characters/`、`.sumeru/intro` |
| `skills/wq-worldbuilder/SKILL.md` | 105 | `\| `introStatus = pending` \| 引导用户校对 `.sumeru/intro.md`（300-500 字，四要素：困境→转折→冲突→悬念），校对完成标 `confirmed` \|` |
| `skills/wq-worldbuilder/SKILL.md` | 139 | `- `outline` 完成：`outline.md`、`outlines/chapters.json`、`.sumeru/intro.md` 存在，且章节任务卡通过字段完整性验证（所有章节包含全部必填字段：`purpo` |
| `skills/wq-worldbuilder/SKILL.md` | 221 | `大纲完成后自动生成。从 `plan.md` 提取作品名称、目标读者、主角名、核心设定，从 `outlines/chapters.json` 提取主线冲突和爽点，撰写 300-500 字简介正文（困境→转折→冲突→悬念），` |

### [简介] `intro.md`（4 处）

| 文件 | 行 | 原文 |
|---|---|---|
| `skills/wq-migrate/SKILL.md` | 188 | `├─ 补做 intro.md（H2）` |
| `skills/wq-migrate/SKILL.md` | 711 | `2. **缺失 `intro.md`**（1.2.0 升级为必填）：finalize / publish 阶段可能跳过简介注入。` |
| `skills/wq-migrate/SKILL.md` | 766 | `### 12.4 intro.md 补做规则（H2 详细）` |
| `skills/wq-rules/SKILL.md` | 41 | `→ intro.md + creative-anchors.md (worldbuilder 内置)` |

### [问题清单] `.sumeru/issues.md`（21 处）

| 文件 | 行 | 原文 |
|---|---|---|
| `skills/wq-finalize/SKILL.md` | 56 | `- 检查 `.sumeru/issues.md` 是否存在未关闭的 `critical` 或 `major` issue；旧版 `.sumeru/issues/index.json` 只读兼容` |
| `skills/wq-migrate/SKILL.md` | 45 | `\| `.sumeru/issues.md` 不存在\| 创建空文件\|` |
| `skills/wq-migrate/SKILL.md` | 68 | `\| `.sumeru/issues/index.json` \| `.sumeru/issues.md` \| 读取旧JSON，转换为 Markdown \|` |
| `skills/wq-migrate/SKILL.md` | 260 | `4. 写入 .sumeru/issues.md` |
| `skills/wq-polish/SKILL.md` | 281 | `- `1` = warning，写入 `.sumeru/issues.md`，可写回但标记 `anti_ai_warning`；` |
| `skills/wq-polish/SKILL.md` | 334 | `- 仍失败则标记 `polish_failed` 到 `.sumeru/issues.md`，记录到 `summary.json`` |
| `skills/wq-review/SKILL.md` | 36 | `\| `medium/standard` \| `reviews/review-report.md`，问题记录到 `.sumeru/issues.md` \|` |
| `skills/wq-review/SKILL.md` | 470 | `- `.sumeru/issues.md`：问题清单` |
| `skills/wq-revise/SKILL.md` | 214 | `- `python skills/wq-review/scripts/anti-ai-scan.py chapters --chapters <本章> --output .sumeru/revise --quiet`；退` |
| `skills/wq-rules/SKILL.md` | 108 | `\| `.sumeru/issues.md` \| 问题清单 \|` |
| `skills/wq-rules/SKILL.md` | 129 | `\| `.sumeru/issues/index.json` \| `.sumeru/issues.md` \| 问题清单 \|` |
| `skills/wq-rules/SKILL.md` | 181 | `\| Issue/测试汇总 \| 合并各子Agent发现的问题，写入 `.sumeru/issues.md` \|` |
| `skills/wq-rules/SKILL.md` | 398 | `\| 问题清单 \| `.sumeru/issues.md` \| `.sumeru/issues/index.json` 只读兼容 \|` |
| `skills/wq-rules/SKILL.md` | 409 | `\| `.sumeru/issues/index.json` \| 读取时自动映射到 `.sumeru/issues.md` \| 下次写入时迁移\|` |
| `skills/wq-worldbuilder/SKILL.md` | 70 | `\| `medium/standard` \| `README.md`、`plan.md`、`outline.md`、`outlines/chapters.json`、`characters/`、`.sumeru/intro` |
| `skills/wq-worldbuilder/SKILL.md` | 104 | `\| `anchorStatus = skipped` \| 写一条 warning 到 `.sumeru/issues.md`（"迁移时跳过 anchor，建议补做"），允许用户继续但不弹窗 \|` |
| `skills/wq-worldbuilder/SKILL.md` | 142 | `- `review` 完成：目标范围已审查，问题写入 `.sumeru/issues.md`；完整报告和 tests 仅在用户要求时生成` |
| `skills/wq-write/SKILL.md` | 475 | `- `3` = **字数未达标**（章节汉字数 < chapterWordRange[0] × 80%）→ **仅警告，不阻断**；写入 issues.md 标记为 soft-warning，父 Agent 记录到 `.` |
| `skills/wq-write/SKILL.md` | 476 | `5. **（可选）连续性冲突检查**：若 `consistency-rules.json` 已有累积状态，调用 `python skills/wq-review/scripts/continuity-check.py .` |
| `skills/wq-write/SKILL.md` | 588 | `\| issues.md 写入 \| `.sumeru/issues.md` \| `.sumeru/issues.md`（全局；卷号前缀标注） \|` |
| `skills/wq-write/SKILL.md` | 588 | `\| issues.md 写入 \| `.sumeru/issues.md` \| `.sumeru/issues.md`（全局；卷号前缀标注） \|` |

### [问题清单] `.sumeru/issues/index.json`（6 处）

| 文件 | 行 | 原文 |
|---|---|---|
| `skills/wq-finalize/SKILL.md` | 56 | `- 检查 `.sumeru/issues.md` 是否存在未关闭的 `critical` 或 `major` issue；旧版 `.sumeru/issues/index.json` 只读兼容` |
| `skills/wq-migrate/SKILL.md` | 68 | `\| `.sumeru/issues/index.json` \| `.sumeru/issues.md` \| 读取旧JSON，转换为 Markdown \|` |
| `skills/wq-migrate/SKILL.md` | 258 | `1. 读取 .sumeru/issues/index.json` |
| `skills/wq-rules/SKILL.md` | 129 | `\| `.sumeru/issues/index.json` \| `.sumeru/issues.md` \| 问题清单 \|` |
| `skills/wq-rules/SKILL.md` | 398 | `\| 问题清单 \| `.sumeru/issues.md` \| `.sumeru/issues/index.json` 只读兼容 \|` |
| `skills/wq-rules/SKILL.md` | 409 | `\| `.sumeru/issues/index.json` \| 读取时自动映射到 `.sumeru/issues.md` \| 下次写入时迁移\|` |

## 磁盘实际结构

### `.sumeru`

```text
```

## CLAUDE.md 的路径声明

```text
# CLAUDE.md - WQ 写作项目上下文

本仓库以 `skills/wq-rules/SKILL.md` 为唯一全局约束源。

## 当前 Skill

```
skills/
├── wq-worldbuilder/
├── wq-topic/          # 选题策划（拆自 outline）
├── wq-outline/        # 大纲设计（拆自 outline）
├── wq-write/
├── wq-scan/           # 扫榜分析与竞品拆解
├── wq-review/
├── wq-polish/
├── wq-score/          # 完稿评分（五维）
├── wq-revise/         # 评分驱动·收敛式修稿（硬收敛，杜绝低分回头改死循环）
├── wq-finalize/
├── wq-migrate/        # 旧项目迁移与规整
└── wq-rules/          # 全局约束（唯一来源）
```

## Canonical 路径

以 `skills/wq-rules/SKILL.md` 第三部分·Canonical 路径为准。概要如下：

### 用户可见文件（项目根目录）
- `NOVEL.md`：小说说明（名字、简介、类型、状态、进度）
- `plan.md`：需求、设定、人物、风格、创意策略、术语
- `outline.md`：故事结构、主线、伏笔、分卷与章节规划摘要
- `chapters/`：正文，按 001-标题.md 命名（短篇可用 `story.md`）
- `characters/`：人物卡（每人一文件）
- `world.md`：世界观手册（long/full 模式）
- `reviews/`：审查报告
- `tests/`：检查报告
- `publish/`：发布产物

### AI 内部数据（.sumeru/ 目录）
- `.sumeru/project.json`：项目配置
- `.sumeru/status.json`：阶段和章节状态
```