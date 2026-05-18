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

**第一阶段：全局信息审查（父Agent执行）**
- 加载完整大纲和章节细纲，建立全局审查基准
- 优先加载 `outlines/chapters.json` 章节任务卡、`docs/architecture.md`、`docs/style-guide.md`、`docs/glossary.md`
- 分析整体剧情脉络和时间线结构
- 审查全局设定一致性（世界观、力量体系、规则设定）
- 识别主线支线关联问题和伏笔回收情况
- 检查整体冲突点分布和节奏把控
- 记录**全局问题清单**到 `.sumeru/review/global-issues.json`
- 同步生成或更新 `.sumeru/issues/index.json`

**第二阶段：章节细节审查（子Agent并行）**

**⚠️ 职责边界**
| 任务 | 父Agent（调度器） | 子Agent（执行器） |
|------|------------------|-------------------|
| 生成 context pack | ✅ 集中生成，含审查标准、正文、consistency-rules.json | ❌ |
| 启动子Agent | ✅ 计算所需Agent数，分配章节 | ❌ |
| **章节审查** | ❌ | **✅ 唯一任务** |
| 合并审查结论 | ✅ 汇总所有子Agent输出 | ❌ |
| 写入 issues/ | ✅ 统一写入结构化问题单 | ❌ |
| 生成 tests/ | ✅ 统一生成各类测试报告 | ❌ |
| 生成 fix-plan.json | ✅ 统一制定修复计划 | ❌ |
| 更新 consistency-rules.json | ✅ 根据子Agent输出的状态标记更新 | ❌ |

**调度逻辑**
```mermaid
flowchart LR
    A[批量审查任务] --> B[父Agent: 自举 & 读取章节列表]
    B --> C[父Agent: 读取 consistency-rules.json & 审查标准]
    D[父Agent: 计算Agent数 = min(ceil/总章/3/, 5)]
    C --> D
    D --> E[父Agent: 生成 context pack + 批次摘要]
    E --> F[父Agent: 启动N个并行子agent N≤5]
    F --> G[子Agent: 读取 context pack → 审查章节 → 输出审查结论+状态标记]
    G --> H{所有子Agent完成?}
    H -->|否| F
    H -->|是| I[父Agent: 提取状态标记 & 合并审查结论]
    I --> J[父Agent: 更新 consistency-rules.json]
    J --> K[父Agent: 写入 issues/ & 生成 tests/]
    K --> L[父Agent: 制定 fix-plan.json]
    L --> M{还有剩余章节?}
    M -->|是| D
    M -->|否| N[完成]
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
