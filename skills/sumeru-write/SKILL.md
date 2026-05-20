---
name: sumeru-write
description: 小说章节内容创作与创意落地。用户要写一章小说、续写、扩写、重写、生成某个情节、按细纲写章节、批量生成章节、写开篇/高潮/过渡章，或要求"帮我写小说内容"时必须使用本技能。
type: skill
---

> ⚠️ **依赖技能**：本 Skill 依赖 `sumeru-rules` 中的全局约束。执行前请确保已加载。

## 网文章节撰写

### 触发关键词
帮我写一章小说、续写接下来的内容、生成XX情节、批量写网文章节、扩写/重写这段内容、帮我写个XX情节、续写小说、把这段内容扩写、重写这一章、批量生成小说章节、写个开篇章节、写个高潮情节、小说内容生成、帮我写小说内容、网文章节生成、从细纲生成章节、按细纲写小说、批量生成所有章节、细纲驱动写作

### 核心功能
1. **基于完整细纲生成**：自动读取 `.sumeru/outline/chapter-outlines.json`
2. **智能细纲匹配**：支持按章节号、卷号、或全部章节进行生成
3. 自动适配网文节奏：开头抓眼球、中间有冲突、结尾留悬念
4. 保持人物性格、剧情逻辑的一致性
5. 支持自定义章节长度（默认4000-5000字/章）
6. 支持续写、修改、调整已有章节内容

### 独立调用自举
1. 定位项目根目录，读取或生成 `.sumeru/project.json`、`.sumeru/status.json`
2. 若缺少 `outlines/chapters.json`，尝试读取 `.sumeru/outline/chapter-outlines.json`
3. 若缺少 `.sumeru/cache/`，生成最小摘要
4. 若缺少当前范围的 context pack，先生成临时 context pack 再写作
5. 根据 `chapters/` 已有文件推断续写位置，默认不覆盖已有章节
6. **写正文必须走子agent（即使是单章续写），父agent绝不写正文**

### 按模式写作
| 模式 | 处理方式 |
|------|----------|
| `short/light` | 优先写入或续写 `story.md`，不强制 context pack |
| `medium/standard` | 按 `outlines/chapters.md` 写入 `chapters/`，批量超3章生成临时 context pack |
| `long/full` | 必须使用拆分任务卡、cache 和 context pack，每个子Agent 1-3 章 |

### 输入优先级
1. 用户本次明确要求（章节号、字数、风格、视角、必须出现/禁止出现的情节）
2. `.sumeru/context-packs/write-<range>.md`（批量写作首选）
3. `.sumeru/cache/` 摘要（project-brief、style-brief、creative-brief、continuity-brief）
4. `.sumeru/review/fix-plan.json` 中标记的重写要求
5. `outlines/chapters/<id>.json` 中的目标章节任务卡
6. 已存在的 `chapters/` 内容用于续写和风格衔接

### 章节任务卡执行规则
- 正文必须完成任务卡中的 `purpose`
- 正文必须落实 `creativeGoal`、`freshnessHook`、`emotionalBeat`、`readerMemoryPoint`
- 遇到 `tropeToAvoid` 时必须避开直给套路
- 若存在 `surpriseTwist`，必须提前埋下公平线索
- 正文必须满足全部 `acceptanceCriteria`

### 创意落地检查（生成章节前自检）
1. 本章是否有读者能记住的一幕、一个选择或一句话
2. 本章爽点是否和前 3 章重复
3. 主角是否通过选择推动局势，而不是被剧情推着走
4. 反派或阻力是否足够聪明，是否让胜利付出代价
5. 结尾钩子是否既承接本章输出，又诱导下一章点击

### 细纲驱动批量生成
```
/sumeru-write 全部章节       # 生成所有章节（自动并行）
/sumeru-write 第1-50章       # 生成指定范围
/sumeru-write 第1卷          # 生成特定卷
/sumeru-write 第3章 "概要"   # 单章创作
/sumeru-write 第3章 按细纲生成
```

### 章节文件命名规范
**强制格式：`{三位章节号}-{章节标题}.md`**
- ✅ `003-第一次解析.md`、`001-废物觉醒系统.md`
- ❌ `第3章-第一次解析.md`、`3-第一次解析.md`、`003_第一次解析.md`

### 数据持久化
**用户可见输出**：`chapters/` 下的纯净正文文件

**中间数据（`.sumeru/write/`）**：
- `progress.json`、`chapter-meta.json`、`character-state.json`、`original/`

### 与其他 Skill 配合
- **前置**：`sumeru-outline` 的 `chapter-outlines.json`、`characters.json`、`world.json`
- **后续**：供 `sumeru-review`、`sumeru-polish`、`sumeru-finalize` 使用

### 全局约束引用
> 完整全局约束见 `sumeru-rules` 技能，核心要点如下：
> - **子Agent规则**：写正文必须走子agent，最多5个并行，每个最多3章
> - **职责边界**：子Agent只读 context pack，输出纯结果+状态标记，不碰状态文件
> - **状态标记**：输出首行必须包含 `<!-- SUMERU_STATUS: chapter=X, status=Y, state_diff="...", char_update="...", batch=N, timestamp=... -->`
> - **Context Pack**：控制在1500-3000中文字，包含项目brief、人物摘要、世界观摘要、任务卡、批次摘要
