# QWEN.md — WQ 写作 (WQ Writing) 项目上下文

> **版本**: v1.4.0 · **基础**: [xindoo/sumeru](https://github.com/xindoo/sumeru) 二次开发
> **全局约束唯一来源**: `skills/wq-rules/SKILL.md`

## 项目概述

WQ 写作是一个网文（网络小说）创作 AI Agent 技能集合，适配 Claude Code、OpenCode、Qwen Code 等 AI 编程工具。通过 Vibe Coding（自然语言指令驱动）方式，一站式完成从创意到完稿的全流程小说写作。

核心定位：网文作者的 AI 创作副驾驶，覆盖 **迁移 → 选题 → 大纲 → 写作 → 审稿 → 润色 → 评分 → 导出** 全流程。

## 技术架构

### Skill 模块化架构

10 个独立 Skill 模块，可单独调用也可全流程自动编排：

| Skill | 职责 | 触发关键词 |
|-------|------|-----------|
| `wq-worldbuilder` | 全流程统筹主管 | "从零写小说"、初始化项目 |
| `wq-scan` | 扫榜分析与竞品拆解 | "扫榜"、分析热榜" |
| `wq-topic` | 选题策划与创意架构 | "不知道写什么、找热门题材" |
| `wq-outline` | 大纲设计（世界观/人物/分卷/章节细纲） | "写大纲、设计人物" |
| `wq-write` | 章节内容创作 | "写第X章、续写、扩写" |
| `wq-review` | 逻辑审查与创意疲劳检测 | "检查bug、时间线矛盾、人物OOC" |
| `wq-polish` | 文笔润色与创意强化 | "润色、改文笔、强化爽点" |
| `wq-score` | 完稿评分系统（五维评分） | "评分、打分、评估作品质量" |
| `wq-finalize` | 完稿校验与发布导出 | "检查错别字、检测敏感词、导出" |
| `wq-migrate` | 旧项目迁移与规整 | "规整项目、迁移旧项目、查缺补漏" |
| `wq-rules` | 全局约束规则（不直接调用） | — |

### 调用链路

```
用户需求 → worldbuilder → scan(可选) → topic → outline → intro → anchor → write → review → fix → polish → [score?] → finalize → build/release
```

每个 Skill 都可脱离 worldbuilder 单独启动，执行自举协议（自动定位项目、读/生成配置、补齐目录）。

### 子Agent 并行处理

- 写正文、审查、润色等核心任务走子Agent
- 最多 3 个子Agent 同时运行，每个最多负责 3 个连续章节；子Agent 禁止再调度子Agent
- 子Agent 只读 context pack + 本组任务卡，直接写入章节文件，返回 `<!-- SUMERU_STATUS: ... -->` 状态标记
- 父Agent 负责备份、状态同步、缓存刷新、汇总

### 状态机

- **项目阶段**: `init → scan(可选) → topic → outline → intro → anchor → write → review → fix → polish → [score?] → finalize → build/release`
- **章节状态**: `planned → drafted → reviewed → fixed → polished → finalized → exported`
- 断点恢复：所有创作数据持久化到 `.sumeru/`，中断后可直接续作

## 目录结构

### 本仓库（技能开发目录）

```
wqsumeru/
├── skills/                    # 10个 Skill 模块
│   ├── wq-rules/          # 全局约束（唯一来源）
│   │   ├── SKILL.md           # 主约束文件
│   │   └── subagent-rules.md  # 子Agent精简版规则
│   ├── wq-worldbuilder/   # 全流程编排器
│   ├── wq-topic/          # 选题策划
│   ├── wq-outline/        # 大纲设计
│   ├── wq-write/          # 章节撰写
│   ├── wq-scan/           # 扫榜分析
│   ├── wq-review/         # 逻辑审查
│   │   ├── SKILL.md
│   │   ├── config/            # 反AI检测配置（JSON外置）
│   │   │   ├── anti-ai-thresholds.json
│   │   │   └── cliche-blacklist.json
│   │   └── scripts/            # Python扫描脚本
│   │       ├── anti-ai-scan.py
│   │       ├── chapter-word-counter.py
│   │       ├── continuity-check.py
│   │       └── foreshadowing-tracker.py
│   ├── wq-polish/         # 内容润色
│   ├── wq-score/          # 完稿评分
│   ├── wq-finalize/       # 完稿校验与导出
│   │   ├── SKILL.md
│   │   ├── config/            # 拼写/敏感词配置（JSON外置）
│   │   │   ├── spell-dict.json
│   │   │   └── sensitive-words.json
│   │   └── scripts/           # Python校验脚本
│   │       ├── format-validator.py
│   │       ├── platform-export.py
│   │       ├── sensitive-word-filter.py
│   │       └── spell-check.py
│   └── wq-migrate/        # 旧项目迁移
├── style-samples/             # 风格样本模板
│   ├── sample-template.md     # 提交模板
│   └── user-style.md          # 系统自动生成的风格分析
├── CLAUDE.md                  # Claude Code 协议文件
├── CHANGELOG.md               # 变更日志
├── README.md                  # 项目说明
└── QWEN.md                    # 本文件
```

### 小说项目工程化结构（生成产物）

技能运行时在用户工作目录生成的小说项目结构：

```
novel-project/
├── NOVEL.md                   # 小说说明（给作者看）
├── plan.md                    # 需求、设定、人物、风格、创意策略、术语
├── outline.md                 # 故事架构、主线、伏笔管理表、章节规划
├── chapters/                  # 正文，按 001-标题.md 命名
├── characters/                # 人物卡（每人一文件）
├── world.md                   # 世界观手册（long/full 模式）
├── outlines/                  # 章节任务卡（chapters.json）
├── reviews/                   # 审查报告
├── tests/                     # 检查报告
├── publish/                   # 发布产物（full.md、full.txt、chapters/）
└── .sumeru/                   # AI 内部数据
    ├── project.json           # 项目配置
    ├── status.json            # 阶段与章节状态
    ├── intro.md               # 小说简介
    ├── creative-anchors.md    # 创意锚点
    ├── issues.md              # 问题清单
    ├── changelog.md           # 变更日志
    ├── decisions.md           # 决策记录
    ├── backlog.md             # 待办事项
    ├── outlines/              # 章节任务卡
    ├── cache/                 # 摘要缓存
    ├── context-packs/         # 子Agent上下文包
    ├── continuity/            # 剧情一致性数据
    ├── volumes/               # 分卷隔离数据（150+章时启用）
    ├── cross-volume/          # 跨卷依赖表
    └── ...
```

## 篇幅模式

| 模式 | 适用范围 | 特点 |
|------|---------|------|
| `short/light` | 1-10章，3万字以内 | 快速完成，少文件 |
| `medium/standard` | 10-50章，3万-20万字 | 使用 plan/outline/chapters/cache |
| `long/full` | 50章以上，20万字以上 | 启用 context-packs、continuity、分卷 |

## 关键技术组件

### Python 脚本（`skills/*/scripts/`）

- **反AI扫描** (`anti-ai-scan.py`): 9维反AI句式 + 15项水文硬指标 + 80+ Cliché黑名单 + 3维标点检测（破折号滥用/省略号格式/感叹号叠用），阈值和黑名单从 JSON 配置加载
- **字数统计** (`chapter-word-counter.py`): 章节字数达标检查
- **连续性检查** (`continuity-check.py`): 时间线、人物位置、道具状态一致性
- **伏笔追踪** (`foreshadowing-tracker.py`): 伏笔设置与回收追踪
- **拼写检查** (`spell-check.py`): 错别字检测，词典从 JSON 加载
- **敏感词过滤** (`sensitive-word-filter.py`): 三级敏感词检测，词库从 JSON 加载
- **格式校验** (`format-validator.py`): 10类标点规范检测（破折号/省略号/感叹号问号/中英文混排/标点空格/引号闭合/书名号/括号/顿号逗号边界/重复标点）+ 章节标题/段落/对话格式校验
- **平台导出** (`platform-export.py`): md/txt 分章+整文导出

### JSON 外置配置

- `wq-review/config/anti-ai-thresholds.json`: 25项反AI检测阈值（含5项标点检测阈值）
- `wq-review/config/cliche-blacklist.json`: 8分类80+条Cliché黑名单
- `wq-finalize/config/spell-dict.json`: 拼写检查词典
- `wq-finalize/config/sensitive-words.json`: 敏感词库

所有脚本启动时动态加载 JSON 配置，无配置文件时使用代码内置默认值，零外部依赖。

## 开发与使用

### 安装

```bash
npx skills add wq1131173682/wqsumeru
```

### 典型工作流

```bash
# 全流程创作
/wq-worldbuilder 玄幻 "废柴逆袭+系统流+穿越"

# 独立调用各环节
/wq-outline 选题 "玄幻 系统+签到+无敌" 起点平台
/wq-write 全部章节          # 细纲驱动批量生成
/wq-review 第1-50章
/wq-polish 第10章 中度润色 小白爽文风格 强化爽点
/wq-finalize 导出全部
/wq-migrate                 # 旧项目迁移
```

### 技能文件格式

每个 Skill 的 `SKILL.md` 包含 YAML frontmatter：
```yaml
---
name: sumeru-xxx
description: 技能描述
version: x.x.x
type: skill
argument-hint: '[参数提示]'
disable-model-invocation: false  # 是否禁止模型自动调用
user-invocable: true              # 是否可由用户直接调用
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, task
context: project
agent: build
---
```

## 开发约定

- **全局约束唯一来源**: `skills/wq-rules/SKILL.md`，所有 Skill 必须遵守
- **子Agent规则**: `skills/wq-rules/subagent-rules.md`（精简版，子Agent只读此文件 + context pack）
- **Canonical 路径**: 用户可见文件在项目根目录，AI内部数据在 `.sumeru/` 目录
- **旧路径兼容**: 支持旧版路径只读优先（如 `.sumeru/outline/chapter-outlines.json` → `outlines/chapters.json`）
- **正文必须走子Agent**: 父Agent绝不直接写正文
- **配置外置**: 可配置参数使用 JSON 文件外置，零外部依赖，无配置时使用内置默认值
- **状态标记**: 子Agent输出首行必须包含 `<!-- SUMERU_STATUS: ... -->` 注释
- **发布导出**: 必须剥离 `SUMERU_STATUS` 注释
- **默认 quiet 模式**: 只输出进度、关键结果和必要警告
- **Git 排除**: `.sumeru/`、`.omo/`、`.qwen/`、`.opencode/` 等目录不提交 git

## 版本

当前 v1.4.0，完整变更见 [CHANGELOG.md](./CHANGELOG.md)。
