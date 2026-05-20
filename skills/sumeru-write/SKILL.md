---
name: sumeru-write
description: 小说章节内容创作与创意落地。用户要写一章小说、续写、扩写、重写、生成某个情节、按细纲写章节、批量生成章节、写开篇/高潮/过渡章，或要求"帮我写小说内容"时必须使用本技能。
type: skill
---

> ⚠️ **依赖技能**：本 Skill 依赖 `sumeru-rules` 中的全局约束。执行前请确保已加载。

> 📌 **输出级别**：默认 `quiet` 模式，只输出进度。详细规范见 `sumeru-rules` "输出级别规范"。

> 📌 **模式选择**：默认使用 `medium` 模式。可通过参数指定 `light`/`medium`/`full`。

## 网文章节撰写

### 触发关键词
帮我写一章小说、续写接下来的内容、生成XX情节、批量写网文章节、扩写/重写这段内容、帮我写个XX情节、续写小说、把这段内容扩写、重写这一章、批量生成小说章节、写个开篇章节、写个高潮情节、小说内容生成、帮我写小说内容、网文章节生成、从细纲生成章节、按细纲写小说、批量生成所有章节、细纲驱动写作

### 核心功能
1. **基于完整细纲生成**：自动读取 `outlines/chapters.json`（兼容 `.sumeru/outline/chapter-outlines.json`）
2. **智能细纲匹配**：支持按章节号、卷号、或全部章节进行生成
3. 自动适配网文节奏：开头抓眼球、中间有冲突、结尾留悬念
4. 保持人物性格、剧情逻辑的一致性
5. 支持自定义章节长度（默认4000-5000字/章）
6. 支持续写、修改、调整已有章节内容

### 独立调用自举
1. 定位项目根目录，读取或生成 `.sumeru/project.json`、`.sumeru/status.json`
2. 若缺少 `outlines/chapters.json`，尝试读取 `.sumeru/outline/chapter-outlines.json`（兼容旧路径）
3. 若缺少 `.sumeru/cache/`，生成最小摘要
4. 若缺少当前范围的 context pack，先生成临时 context pack 再写作
5. 根据 `chapters/` 已有文件推断续写位置，默认不覆盖已有章节
6. **写正文必须走子agent（即使是单章续写），父agent绝不写正文**

### 按模式写作

**核心原则：核心层 + 增量层架构，所有模式共享核心规则。**

| 模式 | 核心层 | 增量 | 总消耗 | 适用场景 |
|------|--------|------|--------|----------|
| `light` | ✅ | 无 | ~2000 字 | 过渡章、日常章、高潮章（严格控制） |
| `medium` | ✅ | medium 增量 | ~4000 字 | 人物互动章、情感章（默认） |
| `full` | ✅ | medium + full 增量 | ~8000 字 | 人物塑造章、首次公开场合 |

**模式选择：**
```
/sumeru-write 第3章 "概要" 模式 light
/sumeru-write 第3章 "概要" 模式 medium  # 默认
/sumeru-write 第3章 "概要" 模式 full
```

### 输入优先级
1. 用户本次明确要求（章节号、字数、风格、视角、必须出现/禁止出现的情节）
2. `.sumeru/context-packs/write-<range>.md`（批量写作首选）
3. `.sumeru/cache/` 摘要（project-brief、style-brief、creative-brief、continuity-brief）
4. `.sumeru/review/fix-plan.json` 中标记的重写要求
5. `outlines/chapters.json` 中的目标章节任务卡（兼容旧路径 `.sumeru/outline/chapter-outlines.json`）
6. 已存在的 `chapters/` 内容用于续写和风格衔接

### 章节任务卡执行规则

**核心规则（所有模式共享）：**
- 正文必须完成任务卡中的 `purpose`
- 正文必须落实 `creativeGoal`、`freshnessHook`、`emotionalBeat`、`readerMemoryPoint`
- 遇到 `tropeToAvoid` 时必须避开直给套路
- 若存在 `surpriseTwist`，必须提前埋下公平线索
- 正文必须满足全部 `acceptanceCriteria`

**创意自由度控制：**
```json
{
  "creativeFreedom": "medium",
  "protectedElements": ["主角必须展现判断力", "不能暴露真正实力"],
  "allowedDeviations": ["可以添加人物小习惯", "可以有对话停顿/口误"]
}
```

**优先级规则：**
```
protectedElements（底线） → 不可违背
    ↓
purpose（必须完成） → 可以改变"如何完成"的方式
    ↓
allowedDeviations（鼓励添加） → 不强制，但鼓励
```

**protectedElements 执行保障：**
- 子Agent严格按 protectedElements 写作，不做任何例外申请
- 子Agent输出后，父Agent对比 state_diff 与 protectedElements，检测是否违反
- 发现违反时，父Agent暂停并询问用户确认

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
> - **状态标记**：输出首行必须包含 `<!-- SUMERU_STATUS: chapter=X, status=Y, state_diff={JSON}, char_update={JSON}, batch=N, timestamp=... -->`
> - **Context Pack**：控制在1500-3000中文字，包含项目brief、人物摘要、世界观摘要、任务卡、批次摘要

---

## 核心规则引用

> ⚠️ **核心规则在 `sumeru-write-core` 技能中定义**，所有模式共享。

**核心层包含：**
- 任务卡执行规则
- 创意自由度控制 + 破例通道
- 创意落地五问
- 毛边核心原则
- 毛边场景触发机制
- 自检清单

**加载方式：**
```
父Agent 启动写作时，自动加载：
1. sumeru-write-core（核心层，必选）
2. sumeru-write-medium（medium 增量，默认）
3. sumeru-write-full（full 增量，仅 full 模式）
```

---

## 模式说明

### light 模式
- **内容**：核心层
- **消耗**：~2000 字
- **适用**：过渡章、日常章、高潮章（严格控制）
- **特点**：保证节奏，毛边最少

### medium 模式（默认）
- **内容**：核心层 + medium 增量
- **消耗**：~4000 字
- **适用**：人物互动章、情感章
- **特点**：平衡节奏与深度

### full 模式
- **内容**：核心层 + medium 增量 + full 增量
- **消耗**：~8000 字
- **适用**：人物塑造章、首次公开场合
- **特点**：完整示例参考，毛边最丰富

**核心层更新时，所有模式自动同步。**
