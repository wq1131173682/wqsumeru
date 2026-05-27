---
name: sumeru-architecture
description: 须弥写作技能系统架构总览。技能调用链路、数据流向、文件索引、状态机。
type: reference
---

# 须弥写作技能系统架构

> 本文档是整个技能系统的导航地图。各 skill 的详细规则见各自 `SKILL.md`。

---

## 一、技能清单

| 技能 | 职责 | 触发场景 | user-invocable |
|------|------|----------|----------------|
| `sumeru-worldbuilder` | 全流程统筹主控 | "从零写小说"、"帮我写本XX类型小说"、"初始化项目" | ✅ |
| `sumeru-topic` | 选题策划与创意架构 | "不知道写什么"、"找热门题材"、"做选题分析" | ✅ |
| `sumeru-outline` | 大纲设计（世界观/人物/分卷/章节细纲） | "写大纲"、"设计人物"、"世界观设定" | ✅ |
| `sumeru-write` | 章节内容创作 | "写第X章"、"续写"、"扩写"、"重写"、"批量生成" | ✅ |
| `sumeru-review` | 逻辑审查与创意疲劳检测 | "检查bug"、"时间线矛盾"、"人物OOC" | ✅ |
| `sumeru-polish` | 文笔润色与创意强化 | "润色"、"改文笔"、"优化节奏"、"强化爽点" | ✅ |
| `sumeru-finalize` | 完稿校验与发布导出 | "检查错别字"、"检测敏感词"、"导出平台格式" | ✅ |
| `sumeru-rules` | 全局约束规则（不直接调用） | — | ❌ |

---

## 二、调用链路

```
用户需求
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  sumeru-worldbuilder（全流程统筹）                            │
│  负责：项目初始化、阶段推进、状态管理、结果汇总                    │
└─────────────────────────────────────────────────────────────┘
    │
    ├─→ sumeru-topic        选题策划 → plan.md
    │
    ├─→ sumeru-outline      大纲设计 → outline.md, chapters.json, characters/
    │
    ├─→ .sumeru/intro.md    简介生成（worldbuilder 内置）
    │
    ├─→ .sumeru/creative-anchors.md  创意锚点确认（worldbuilder 内置）
    │
    ├─→ sumeru-write        章节写作 → chapters/*.md
    │       │
    │       └─ 子Agent并行（最多5个，每个≤3章）
    │
    ├─→ sumeru-review       逻辑审查 → issues.md, fix-plan.json
    │       │
    │       └─ 子Agent并行审查 + 反审验证
    │
    ├─→ sumeru-write        修复重写（读取 fix-plan.json）
    │
    ├─→ sumeru-polish       文笔润色 → chapters/*.md（替换原文）
    │       │
    │       └─ 子Agent并行润色
    │
    └─→ sumeru-finalize     完稿校验 + 发布导出 → publish/
```

**独立调用**：每个 skill 都可以脱离 worldbuilder 单独启动，执行自举协议（见 `protocol.md` 第二节）。

---

## 三、数据流向

```
选题阶段                    大纲阶段                    写作阶段
─────────                  ─────────                  ─────────
用户输入                   plan.md                    chapters.json
    │                         │                           │
    ▼                         ▼                           ▼
 plan.md                  outline.md               context pack 生成
 .sumeru/topic/           chapters.json                  │
    │                     characters/                     ▼
    │                     world.md                   子Agent并行写作
    │                         │                           │
    └─────────────────────────┘                           ▼
                              │                     chapters/*.md
                              │                     SUMERU_STATUS
                              │                           │
                              ▼                           ▼
审查阶段 ←────────────────────────────────────── continuity cache
─────────
issues.md
fix-plan.json
    │
    ▼
修复阶段 → 重写章节 → 反审验证
    │
    ▼
润色阶段 → chapters/*.md（polished）
    │
    ▼
完稿阶段 → publish/（各平台格式）
```

---

## 四、状态机

### 项目状态流转

```
init → topic → outline → intro → anchor → write → review → fix → polish → finalize → build/release
```

### 章节状态流转

```
planned → drafted → reviewed → fixed → polished → finalized → exported
                              ↑
                              │ (反审未通过时回退)
                              └──────────────────
```

### 推进规则（详见 `sumeru-worldbuilder` 状态机）

| 阶段完成条件 | 说明 |
|-------------|------|
| `topic` → `outline` | `plan.md` 已写入，含选题方向和目标平台 |
| `outline` → `anchor` | `outline.md`、`chapters.json`、`.sumeru/intro.md` 存在 |
| `anchor` → `write` | `.sumeru/creative-anchors.md` 存在，≥3 个锚点确认 |
| `write` → `review` | 目标章节文件存在，状态 `drafted`，无缺章 |
| `review` → `fix` | 问题写入 `issues.md`，重写项写入 `fix-plan.json` |
| `fix` → `polish` | 反审验证通过，章节状态 `fixed` |
| `polish` → `finalize` | 章节状态 `polished` |
| `finalize` → `build` | 技术校验通过，章节状态 `finalized` |

---

## 五、文件索引

### 用户可见文件

| 文件 | 内容 | 生成阶段 |
|------|------|----------|
| `plan.md` | 需求、设定、人物、风格、创意策略、术语 | topic |
| `outline.md` | 故事结构、主线、伏笔、分卷与章节规划 | outline |
| `outlines/chapters.json` | 章节任务卡 | outline |
| `characters/*.md` | 人物卡 | outline |
| `world.md` | 世界观手册 | outline (long/full) |
| `chapters/*.md` | 正文 | write / polish |
| `reviews/review-report.md` | 审查报告 | review |
| `publish/` | 发布产物 | finalize |

### 中间数据（`.sumeru/`）

| 文件/目录 | 内容 |
|-----------|------|
| `.sumeru/project.json` | 项目配置 |
| `.sumeru/status.json` | 阶段和章节状态 |
| `.sumeru/intro.md` | 小说简介 |
| `.sumeru/creative-anchors.md` | 创意锚点 |
| `.sumeru/issues.md` | 问题清单 |
| `.sumeru/changelog.md` | 变更日志 |
| `.sumeru/decisions.md` | 决策记录 |
| `.sumeru/backlog.md` | 待办事项 |
| `.sumeru/cache/` | 各类摘要缓存 |
| `.sumeru/context-packs/` | 子Agent上下文包 |
| `.sumeru/continuity/` | 剧情一致性数据 |
| `.sumeru/topic/` | 选题阶段数据 |
| `.sumeru/write/` | 写作阶段数据 |
| `.sumeru/polish/` | 润色阶段数据 |
| `.sumeru/finalize/` | 完稿阶段数据 |

### 旧路径兼容（只读）

| 旧路径 | 新路径 | 说明 |
|--------|--------|------|
| `.sumeru/outline/chapter-outlines.json` | `outlines/chapters.json` | 章节任务卡 |
| `.sumeru/issues/index.json` | `.sumeru/issues.md` | 问题清单 |
| `docs/*`、`ideas/*` | `plan.md` | 需求/设定 |

---

## 六、子Agent架构

### 父Agent职责

- 自举 & 环境准备
- Context pack 生成（`shared-{task}.md` + `cards-{范围}.md`）
- 任务分发（最多 5 个子Agent并行）
- 结果汇总 & 文件写入
- 状态更新 & 缓存刷新
- 备份 & 日志记录

### 子Agent职责

- 只读 context pack（2 个文件）
- 执行单一核心任务
- 输出纯文本结果 + `SUMERU_STATUS` 标记
- 不碰状态文件、不写项目文件

### 并行规则

| 规则 | 值 |
|------|-----|
| 并行上限 | 5 |
| 分片约束 | 每子Agent ≤ 3 章 |
| 分配策略 | 连续分组（1-3、4-6...） |
| 计算公式 | `min(ceil(总章节数 / 3), 5)` |

---

## 七、脚本索引

| 脚本 | 所属 Skill | 功能 |
|------|-----------|------|
| `sumeru-review/scripts/continuity-check.py` | review | 剧情一致性检查 |
| `sumeru-review/scripts/foreshadowing-tracker.py` | review | 伏笔生命周期追踪 |
| `sumeru-review/scripts/chapter-word-counter.py` | review | 章节字数统计 |
| `sumeru-finalize/scripts/spell-check.py` | finalize | 错别字检查 |
| `sumeru-finalize/scripts/sensitive-word-filter.py` | finalize | 敏感词检测 |
| `sumeru-finalize/scripts/format-validator.py` | finalize | 格式校验 |
| `sumeru-finalize/scripts/platform-export.py` | finalize | 平台格式导出 |

---

## 八、规则文件索引

| 文件 | 内容 |
|------|------|
| `sumeru-rules/SKILL.md` | 子Agent并行处理、职责边界、状态标记、调用协议 |
| `sumeru-rules/continuity.md` | 剧情统一门禁、冲突检测规则、伏笔生命周期 |
| `sumeru-rules/protocol.md` | Context Pack 格式、自举协议、项目 Schema、平台规则索引、修改边界、质量检查 |
| `sumeru-rules/conventions.md` | 输出级别规范、写作安全与原创性 |
| `sumeru-rules/subagent-rules.md` | 子Agent精简版约束规则（子Agent读此文件） |
| `sumeru-rules/ARCHITECTURE.md` | 本文件（系统架构总览） |
