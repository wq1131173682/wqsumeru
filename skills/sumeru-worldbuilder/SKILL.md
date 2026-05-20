---
name: sumeru-worldbuilder
description: 网文/小说全流程创作世界构建师和项目管理器。用户想从零写小说、初始化小说项目、把创意发展成完整作品、自动完成选题/大纲/章节/审查/润色/导出，或说"我想写小说""帮我写本XX类型小说""给我整个小说创作流程"时必须使用本技能。
type: skill
---

## 网文创作世界构建师

### 触发关键词
我想写小说、写一本网文、从零开始创作小说、帮我写本XX类型的小说、我要写本小说、给我整个小说创作流程、自动写小说、小说创作一站式服务、帮我完成一本小说、我只有创意怎么写小说、从零开始写网文、小说全流程创作

### 核心功能
worldbuilder 是网文创作的一站式主控技能，负责统筹协调从创意萌芽到作品完稿的完整创作链路：

0. **项目初始化**：创建标准小说项目目录，生成 `README.md`、`NOVEL.md`、`docs/`、`outlines/`、`ideas/`、`.sumeru/project.json`、`.sumeru/status.json`
1. **选题策划**：调用 `sumeru-topic` 进行市场分析、选题定位
2. **大纲设计**：调用 `sumeru-outline` 构建完整世界观、人物设定、分卷大纲与章节任务卡
3. **内容创作**：调用 `sumeru-write` 按章节任务卡进行分章节内容撰写
4. **逻辑审查**：调用 `sumeru-review` 对已完成章节进行项目测试式审查
5. **内容润色**：调用 `sumeru-polish` 对已审查章节进行文笔优化
6. **完稿构建**：调用 `sumeru-finalize` 对已润色章节完成技术校验、平台格式 build 和 release

### 项目初始化协议
当用户要求"初始化小说项目"或当前目录缺少 `.sumeru/project.json` 时，先执行初始化：

1. 根据用户指定、计划章节数、计划字数判断 `projectMode` 和 `workflowLevel`。
2. 写入 `.sumeru/project.json`，包含 `projectMode`、`workflowLevel`、题材、平台、篇幅等。
3. 生成 `.sumeru/status.json`，初始化阶段状态和章节状态。
4. 按模式创建目录，不一刀切创建 full 结构。
5. 生成必要 cache；只有 medium/long 或批量任务需要时才生成 context pack。
6. 生成 `.sumeru/backlog.md`、`.sumeru/decisions.md`、`.sumeru/changelog.md`。

#### 模式初始化
| 模式 | 创建内容 |
|------|----------|
| `short/light` | `README.md`、`story.md`、`outline.md`、`.sumeru/project.json`、`.sumeru/status.json`、`.sumeru/cache/story-brief.md` |
| `medium/standard` | `README.md`、`NOVEL.md`、`docs/requirements.md`、`docs/outline.md`、`docs/characters.md`、`docs/style-guide.md`、`docs/creative-strategy.md`、`outlines/chapters.md`、`chapters/`、`publish/`、`.sumeru/cache/`、`.sumeru/issues.md` |
| `long/full` | 完整工程化结构（见 AGENTS.md "long/full 结构"） |

### 模式升级协议
- `short -> medium`：补齐 `docs/`、`outlines/`、`chapters/`、标准 cache，把 `story.md` 拆为章节。
- `medium -> long`：补齐 `ideas/`、`tests/`、`.sumeru/issues/`、`.sumeru/context-packs/`、`.sumeru/continuity/`，拆分章节任务卡。
- 升级后更新 `.sumeru/project.json` 的 `projectMode`、`workflowLevel`，记录到 `.sumeru/decisions.md` 和 `.sumeru/changelog.md`。

### 项目状态机
worldbuilder 是唯一负责推进全局阶段状态的 skill。

**阶段顺序**：`init -> topic -> outline -> write -> review -> fix -> polish -> finalize -> build/release`

**章节状态顺序**：`planned -> drafted -> reviewed -> fixed -> polished -> finalized -> exported`

**推进规则**：
- `outline` 完成：`docs/architecture.md`、`docs/plot.md`、`outlines/chapters.json` 存在，且章节任务卡包含 `acceptanceCriteria`。
- `write` 完成：目标章节文件存在，章节状态更新为 `drafted`，且没有缺章。
- `review` 完成：`tests/continuity-report.md`、`tests/chapter-acceptance-report.md`、`.sumeru/issues/index.json` 生成。
- `fix` 完成：轻量问题已修复，重写问题已转为 `needs-rewrite` 或完成重写。
- `polish` 完成：章节状态更新为 `polished`。
- `finalize` 完成：技术校验通过，章节状态更新为 `finalized`。
- `build/release` 完成：`publish/` 生成目标平台产物，`.sumeru/finalize/build-manifest.json` 生成。

### 低 Token 调度规则
调用任何批量子技能前，必须先准备最小上下文：
1. 刷新 `.sumeru/cache/*.md` 中与本阶段相关的摘要。
2. 根据章节范围生成 `.sumeru/context-packs/<stage>-<range>.md`。
3. 子Agent prompt 中明确"只读取 context pack"。
4. 汇总阶段检查缺章、状态、issue、测试结果和缓存是否需要刷新。

### 分片策略
- **outline 章节任务卡生成**：每个子Agent最多 3 章
- **write 创作**：每个子Agent 1-3 章，必须使用 `write-<range>.md` context pack
- **review 深度审查**：每个子Agent最多 3 章，必须使用 `review-<range>.md` context pack
- **review 全本轻扫**：可按 10-20 章分片，只生成候选问题
- **polish 润色**：每个子Agent 1-3 章，必须使用 `polish-<range>.md` context pack
- **finalize 技术校验/导出**：脚本预处理 + 子Agent只处理待定项（最多20个/批）
- **fix/rewrite**：按问题严重度单独分片，重写型任务每个子Agent最多 1-2 章

### 交互式需求引导
当用户提供的信息过于简略时，自动触发交互式提问：

**基础信息确认（必问）**：
1. 题材确认（细分类型）
2. 篇幅预期
3. 核心爽点
4. 受众定位

**核心设定引导（可选）**：
5. 主角设定偏好
6. 反派设定偏好
7. 世界观偏好
8. 参考作品

**风格偏好设置（可选）**：
9. 写作风格
10. 发布平台
11. 禁忌内容

### Skill 协调流程
```
用户需求
    ↓
[收集创作需求 → 保存到 docs/requirements.md 与 .sumeru/project.json]
    ↓
[sumeru-topic] 选题策划 → 输出: 选题策划报告.md, .sumeru/topic/options.json
    ↓
[sumeru-outline] 大纲设计 → 输出: docs/*.md, outlines/chapters.json
    ↓
[阶段检查点 1] 确认章节细纲已生成
    ↓
[sumeru-write] 章节撰写 → 输出: chapters/*.md
    ↓
[阶段检查点 2] 验证所有章节已完成
    ↓
[sumeru-review] 逻辑审查 → 输出: reviews/*.md, tests/*.md, .sumeru/issues/
    ↓
{fix-plan.json 有重写项?}
    →|是| [调用sumeru-write重写指定章节]
    →|否| 继续
    ↓
[sumeru-polish] 内容润色 → 输出: chapters/*.md（润色后）
    ↓
[sumeru-finalize] 完稿校验 → 输出: publish/*, tests/release-check-report.md
```

### 参数说明
- **作品类型**（必填）：玄幻、都市、仙侠、科幻、言情、悬疑、历史、游戏、竞技等
- **核心创意关键词**（必填）：支持多个关键词用"+"连接

**可选信息**：
- 作品标题、预期篇幅、写作风格、整体调性、输出目录、中断恢复、跳过阶段

### 使用示例
```
# 基础用法
/sumeru-worldbuilder 玄幻 "废柴逆袭+系统流"

# 指定标题
/sumeru-worldbuilder 言情 "霸道总裁+契约恋爱" 标题"总裁的契约新娘"

# 中断恢复
/sumeru-worldbuilder 玄幻 "废柴逆袭+系统流" 恢复上次创作

# 跳过阶段
/sumeru-worldbuilder 都市 "职场+重生" 跳过选题阶段

# 多风格组合
/sumeru-worldbuilder 悬疑 "连环杀人+心理侧写+反转" 详写风格 暗黑调性
```

### 全局约束引用
- 子Agent并行处理规则：见 AGENTS.md "子Agent并行处理规则"
- 职责边界：见 AGENTS.md "子Agent职责边界规则"
- 状态标记格式：见 AGENTS.md "子Agent输出状态标记"
- Context Pack 格式：见 AGENTS.md "Context Pack 格式"
- 项目配置 Schema：见 AGENTS.md "项目配置 Schema"
- 数据持久化规范：见 AGENTS.md "全局存储结构"
- 批次间串行摘要：见 AGENTS.md "批次间串行摘要"
