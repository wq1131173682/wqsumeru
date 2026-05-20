---
name: sumeru-review
description: 小说逻辑/剧情审查、项目测试与创意疲劳检测。用户要检查小说bug、时间线矛盾、人物OOC、剧情前后冲突、章节任务卡验收、伏笔是否回收、章节字数是否达标、剧情合理性、逻辑漏洞、套路重复、爽点同质化、角色被剧情推着走或创意不够新时必须使用本技能。
user-invocable: true
---

## 网文逻辑审查

### 触发关键词
帮我检查下小说有没有bug、看看时间线有没有矛盾、人物有没有OOC、找剧情前后冲突、梳理伏笔有没有回收、检查小说剧情合理性、看看有没有剧情漏洞、人物行为不符合性格、检查时间线对不对、找小说前后矛盾的地方、帮我梳理所有伏笔、小说剧情bug检查、逻辑漏洞排查、小说剧情审查

### 核心功能
1. **全局审查**：分析整体剧情脉络、时间线、设定一致性、冲突点分布、伏笔回收状态
2. **章节细节审查**：逐章检查字数、时间线、人物OOC、物品状态、场景质量、伏笔设置
3. **统一修复**：轻量问题直接修复，严重问题写入修复计划
4. **创意疲劳检测**：套路重复、情绪重复、创意目标未落地检测

### 独立调用自举
如果用户直接调用 `sumeru-review`，先执行 AGENTS.md 的"断点恢复与独立调用自举"：
- 定位项目根目录，读取或生成 `.sumeru/project.json`、`.sumeru/status.json`。
- 根据 `chapters/` 推断可审查章节范围；用户未指定范围时默认审查已存在章节。
- 若缺少 `outlines/chapters.json`，尝试读取 `.sumeru/outline/chapter-outlines.json`；仍缺失时只做正文逻辑审查。
- 若缺少 `.sumeru/cache/`，生成最小 `continuity-brief.md`、`issue-brief.md`、`latest-test-summary.md`。
- 若缺少当前范围的 `review-<range>.md` context pack，先生成临时 context pack 再审查。

### 按模式审查
- `short/light`：输出单文件 `review.md`，检查结构、人物动机、反转合理性、错别字和结尾余味。
- `medium/standard`：输出 `reviews/review-report.md` 或 `tests/review-report.md`，问题记录到 `.sumeru/issues.md`。
- `long/full`：输出完整 `reviews/`、`tests/`、`.sumeru/issues/`，支持轻扫和深度审查两层流程。

### 低 Token 审查规则
- 全本审查先读取 `.sumeru/cache/latest-test-summary.md`、`issue-brief.md`、`continuity-brief.md` 和章节索引，先做轻扫。
- `short/light` 直接审查 `story.md` 或少量章节。
- `medium/standard` 优先读取 `issues.md` 和合并审查报告。
- 深度审查使用 `.sumeru/context-packs/review-<range>.md`，每个子Agent最多 3 章。
- 全本轻扫可按 10-20 章分片，只生成候选问题和高风险章节。

### 三阶段审查修复流程

**第一阶段：全局信息审查（父Agent执行）**
- 加载完整大纲和章节细纲，建立全局审查基准
- 优先加载 `outlines/chapters.json`、`docs/architecture.md`、`docs/style-guide.md`、`docs/glossary.md`
- 分析整体剧情脉络和时间线结构
- 审查全局设定一致性（世界观、力量体系、规则设定）
- 识别主线支线关联问题和伏笔回收情况
- 记录全局问题清单到 `.sumeru/review/global-issues.json`

**第二阶段：章节细节审查（子Agent并行）**
- 每个子Agent最多 3 章，使用 `review-<range>.md` context pack
- 子Agent输出审查结论+状态标记
- 父Agent汇总所有子Agent输出，更新 `consistency-rules.json`

**第三阶段：统一修复**
- 轻量修复 → 直接修改 `chapters/`（自动备份到 `.sumeru/write/original/`）
- 重写修复 → 生成 `fix-plan.json`，由 `sumeru-worldbuilder` 编排或用户手动调用 `sumeru-write` 处理

### 检查类型
- **字数检查**：章节字数达标检查，不足自动填充
- **时间线**：时间线/年龄/事件顺序一致性
- **人物OOC**：人物性格/行为OOC检查
- **剧情逻辑**：剧情逻辑/设定一致性
- **伏笔**：伏笔回收检查
- **常识**：常识/因果合理性检查
- **创意疲劳**：套路重复、情绪重复、创意目标未落地

### 数据持久化
**用户可见输出**：
- `reviews/review-report.md`：用户可读审查报告
- `tests/*.md`：各类测试报告（continuity、chapter-acceptance、foreshadowing、word-count）

**中间数据（`.sumeru/`）**：
- `.sumeru/issues/index.json`：问题索引
- `.sumeru/issues/ISSUE-*.md`：单个问题详细说明
- `.sumeru/review/global-issues.json`：全局问题清单
- `.sumeru/review/fix-plan.json`：重写修复计划

### 与其他 Skill 配合
- **前置**：读取 `sumeru-write` 生成的 `chapters/` 和 `sumeru-outline` 的大纲数据
- **后续**：输出供 `sumeru-polish`、`sumeru-finalize` 使用

### 全局约束引用
- 子Agent并行处理规则：见 AGENTS.md "子Agent并行处理规则"
- 职责边界：见 AGENTS.md "子Agent职责边界规则"
- 状态标记格式：见 AGENTS.md "子Agent输出状态标记"
- Context Pack 格式：见 AGENTS.md "Context Pack 格式"
- 独立调用自举：见 AGENTS.md "断点恢复与独立调用自举"
- 项目配置 Schema：见 AGENTS.md "项目配置 Schema"
- consistency-rules.json 维护：见 AGENTS.md "连贯性规则库"
