# 须弥写作 (Sumeru Writing) - 二次开发版

> **当前版本**: v1.3.4 · **更新日期**: 2026-06-05 · **完整变更**: [CHANGELOG.md](./CHANGELOG.md)

基于 [xindoo/sumeru](https://github.com/xindoo/sumeru) 二次开发的网文创作AI Agent技能集合，适配Claude Code、OpenCode等AI编程工具，通过Vibe Coding的方式一站式完成从创意到完稿的全流程小说写作。

> 🎯 **定位**: 网文作者的AI创作副驾驶，覆盖**迁移 → 选题 → 大纲 → 写作 → 审稿 → 润色 → 导出**全流程，让创作更高效。

> 📌 **说明**: 本项目基于开源项目 [sumeru](https://github.com/xindoo/sumeru) 进行二次开发，保留了原有核心功能，可根据个人需求进行定制和扩展。

## 🆕 最新更新

- **v1.3.4** (2026-06-05) — 反 AI 扫描闭环套用模板：新增 2 项检查（`micro_arc_template_repeat` 段间结构指纹 + `dialog_marker_dominant` 对话标记集中度）+ Cliché 黑名单 40+ → 80+（战斗套路 + 转折模板 + 情绪标签）+ 6 维 → 8 维反 AI 句式
- **v1.3.3** (2026-06-05) — 反水文扫描脚本（`anti-ai-scan.py`，560 行，15 项检查 + 6 维反 AI 句式 + 40+ Cliché 黑名单）+ 修复 `sumeru-review` L116 内部矛盾
- **v1.3.2** (2026-06-05) — 清理 `scripts-lib` 死代码 + 9 个 SKILL.md 全面 OCR 错字校对
- **v1.3.1** (2026-06-05) — 剧情一致性 + 文笔丰富优化包：medium 模式启用 continuity、anchor 加 `targetChapter`、user-style 自动分析
- **v1.3.0** (2026-06-05) — sumeru-migrate 接续协议：迁移后自动补 anchor/intro/状态标记，worldbuilder 一键续作

## ✨ 核心特性

- **全流程覆盖**: 从迁移旧项目到多平台导出，覆盖网文创作所有核心环节
- **模块化架构**: 9个独立Skill模块（迁移/选题/大纲/写作/审稿/润色/完稿 + 2 个支撑模块），可单独调用也可全流程自动编排
- **项目接续**: sumeru-migrate v1.3.0+ 支持 H1-H6 接续协议，旧版本项目迁移后无缝续作
- **Vibe Coding**: 自然语言指令驱动，无需学习复杂操作
- **市场导向**: 基于主流平台榜单数据分析，提供选题可行性评估
- **逻辑自洽**: 自动校验时间线、剧情一致性、人物OOC等问题
- **风格适配**: 支持小白爽文、精品文、古风、都市等多种写作风格
- **通用格式导出**: 分章 + 整文 md/txt 格式导出，兼容任何平台发布需求
- **断点续传**: 所有创作数据自动持久化，支持中断后恢复进度

## 🏗️ 系统架构

须弥写作采用模块化Skill架构，各模块独立工作又可协同编排：

```
skills/
├── sumeru-worldbuilder/  # 全流程编排器
├── sumeru-topic/         # 选题策划，市场分析→创意引擎→高概念Pitch→金手指设计
├── sumeru-outline/       # 大纲设计，世界观→人设→剧情框架→伏笔管理表→章节细纲
├── sumeru-write/         # 章节撰写，单章/批量创作+续写+重写
├── sumeru-review/        # 逻辑审查，时间线+剧情+人物一致性校验
├── sumeru-polish/        # 内容润色，文笔优化+节奏调整+风格统一
├── sumeru-finalize/      # 完稿校验，合规检查+md/txt格式导出
├── sumeru-migrate/       # 旧项目迁移，路径迁移+配置补齐+字段补全
└── sumeru-rules/         # 全局约束（唯一来源）
```

## 📁 小说项目工程化结构

须弥写作推荐把一本小说当作一个长期开发项目维护。根目录只有一个 `NOVEL.md` 文件（给作者看的），其他所有文件都放在 `.sumeru/` 目录下（给AI看的）。

### 篇幅模式

| 模式 | 复杂度 | 适用范围 | 特点 |
|---|---|---|---|
| `short/light` | 轻量 | 1-10章，3万字以内 | 快速完成，少文件，不强制 context pack/tests/issues |
| `medium/standard` | 标准 | 10-50章，3万-20万字 | 使用 plan/outline/chapters/cache，问题合并为单文件 |
| `long/full` | 完整 | 50章以上，20万字以上 | 启用 context-packs、continuity，报告和 tests 按需生成 |

短篇优先灵感和完成度，中篇优先结构，长篇优先工程化稳定。

```text
novel-project/
├── NOVEL.md                   # 小说说明（给作者看）：名字、简介、类型、状态、进度
└── .sumeru/                   # 内部数据（给AI看）
    ├── project.json           # 项目配置
    ├── status.json            # 阶段与章节状态
    ├── plan.md                # 需求、设定、人物、风格、创意策略、术语
    ├── outline.md             # 故事架构、主线、伏笔管理表、章节规划
    ├── chapters/              # 正文，按 001-标题.md 命名
    ├── characters/            # 人物卡（每人一文件）
    ├── world.md               # 世界观手册（long/full 模式）
    ├── outlines/              # 章节任务卡
    │   └── chapters.json
    ├── cache/                 # 摘要缓存
    ├── context-packs/         # 子Agent上下文包
    ├── continuity/            # 剧情一致性数据
    ├── topic/                 # 选题阶段数据
    ├── write/                 # 写作阶段数据
    ├── review/                # 审查阶段数据
    ├── polish/                # 润色阶段数据
    ├── finalize/              # 完稿阶段数据
    ├── publish/               # 发布产物
    ├── reviews/               # 审查报告
    ├── tests/                 # 检查报告
    ├── issues.md              # 问题清单
    ├── intro.md               # 小说简介
    ├── creative-anchors.md    # 创意锚点
    ├── backlog.md             # 待办事项
    ├── decisions.md           # 决策记录
    └── changelog.md           # 变更日志
```

### NOVEL.md 格式

```markdown
# 小说名称

## 基本信息
- **类型**：玄幻
- **平台**：起点
- **受众**：男频
- **篇幅**：长篇（100章，30万字）

## 简介
（300-500字简介）

## 状态
- **当前阶段**：写作中
- **已完成**：50/100 章
- **已写字数**：150,000 字
- **最后更新**：2026-06-05

## 进度
| 阶段 | 状态 |
|------|------|
| 选题 | ✅ 完成 |
| 大纲 | ✅ 完成 |
| 写作 | 🔧 进行中 (50/100) |
| 审查 | ⏳ 待开始 |
| 润色 | ⏳ 待开始 |
| 导出 | ⏳ 待开始 |
```

### 短篇项目结构

```text
short-story/
├── NOVEL.md
└── .sumeru/
    ├── project.json
    ├── status.json
    ├── story.md
    ├── outline.md
    └── cache/
```

### 关键机制
- `NOVEL.md`：小说说明，给作者看的唯一文件
- `.sumeru/project.json`：项目配置，所有 Skill 优先读取
- `.sumeru/status.json`：阶段状态和章节状态，支持断点恢复
- `.sumeru/plan.md`：需求、设定、人物、风格、创意策略和术语的合并文件
- `.sumeru/outline.md`：故事结构、主线、伏笔管理表、分卷与章节规划摘要
- `.sumeru/chapters/`：正文目录，按 001-标题.md 命名
- `.sumeru/characters/`：人物卡目录，每人一文件
- `.sumeru/world.md`：世界观手册（long/full 模式）
- `.sumeru/outlines/chapters.json`：章节任务卡
- `.sumeru/cache/`：稳定摘要缓存
- `.sumeru/context-packs/`：子Agent任务上下文包
- `.sumeru/continuity/`：剧情一致性数据
- `.sumeru/issues.md`：问题清单
- `.sumeru/publish/`：发布产物（full.md、full.txt、chapters/ 分章）

### 断点恢复与单独调用

所有 Skill 都支持单独调用，不要求必须先运行 `sumeru-worldbuilder`。当你直接调用 `/sumeru-write`、`/sumeru-review`、`/sumeru-polish` 或 `/sumeru-finalize` 时，Skill 会先执行自举流程：

- 自动定位项目根目录。
- 读取或生成 `.sumeru/project.json` 和 `.sumeru/status.json`。
- 从已有 `chapters/`、`publish/`、`.sumeru/outlines/` 推断当前阶段和章节状态。
- 缺少 `.sumeru/cache/` 或 `.sumeru/context-packs/` 时按当前任务生成最小版本，不全量读取项目。
- 兼容旧版 `.sumeru/outline/chapter-outlines.json`。
- 完成后回写状态、缓存、changelog 和必要的 issue/test/build 文件。

因此中断后可以直接说“继续写第23章”“审查已有章节”“润色第10-12章”“导出番茄格式”，不需要从全流程重新开始。

## 🚀 安装方式

在Claude Code / OpenCode项目中执行：
```bash
npx skills add wq1131173682/wqsumeru
```

> 也可参考原版 [xindoo/sumeru](https://github.com/xindoo/sumeru) 的安装和使用文档。

## 📖 快速开始

### 全流程创作（推荐）
直接启动完整创作流程，系统会自动引导你完成所有环节，自动协调选题→大纲→写作→审查→润色→导出全流程：
```bash
/sumeru-worldbuilder <题材类型> "<核心创意关键词>"
```

**可选参数说明：**
| 参数 | 说明 | 示例 |
|------|------|------|
| 标题 | 自定义小说名称 | 标题"重生之互联网大亨" |
| 篇幅 | 预期篇幅 | 长篇/中篇/短篇 |
| 风格 | 写作风格 | 小白爽文/精品文/古风 |
| 调性 | 整体调性 | 轻松/严肃/搞笑 |
| 恢复 | 中断后恢复创作 | 恢复上次创作 |
| 跳过 | 跳过指定环节 | 跳过审查、润色 |

**示例：**
```bash
# 基础用法
/sumeru-worldbuilder 玄幻 "废柴逆袭+系统流+穿越"
/sumeru-worldbuilder 都市 "重生+投资+创业"
/sumeru-worldbuilder 言情 "霸道总裁+契约恋爱" 标题"总裁的契约新娘"

# 带参数的完整用法
/sumeru-worldbuilder 都市 "重生2000年+互联网创业+商战" 标题"重生之网络帝国" 长篇 精品文
/sumeru-worldbuilder 科幻 "星际冒险+机甲+无限流" 长篇 快节奏

# 多风格组合
/sumeru-worldbuilder 都市 "修仙+打工+搞笑" 均衡风格 幽默调性     # 幽默风都市修仙
/sumeru-worldbuilder 悬疑 "连环杀人+心理侧写+反转" 详写风格 暗黑调性  # 暗黑系悬疑推理
/sumeru-worldbuilder 竞技 "篮球+天赋+逆袭" 快节奏 励志调性        # 热血励志竞技

# 中断恢复与阶段跳过
/sumeru-worldbuilder 科幻 "星际冒险+机甲+无限流" 恢复上次创作 跳过选题  # 恢复之前的科幻题材创作，跳过选题环节
/sumeru-worldbuilder 都市 "职场+重生" 跳过选题阶段                    # 跳过选题，直接从已有大纲继续

# 团队协作场景
/sumeru-worldbuilder 玄幻 "废柴逆袭+系统流" 跳过写作、审查、润色、完稿阶段  # 策划完成选题和大纲后交由写手
/sumeru-worldbuilder 玄幻 "废柴逆袭+系统流" 跳过选题、大纲阶段 恢复上次创作  # 写手接手，从创作阶段继续
```

### 独立功能调用
你也可以单独调用任意环节的Skill，灵活组合使用：

---

#### 1. 选题策划（outline 的子阶段）
**适用场景**：不知道写什么、想找热门题材、需要市场可行性分析
**功能**：基于类型经验和模型知识生成3套差异化选题方案，包含金手指设计、核心卖点、爽点模式和风险提示。市场判断为非实时推断，需结合平台最新榜单验证。

```bash
/sumeru-outline 选题 "<题材类型> <核心关键词>"
```

**可选参数说明：**
| 参数 | 说明 | 示例 |
|------|------|------|
| 平台 | 目标发布平台 | 起点/番茄/晋江/纵横 |
| 受众 | 目标受众 | 男频/女频/中性 |
| 篇幅 | 预期篇幅 | 长篇/中篇/短篇 |

**示例：**
```bash
# 基础用法
/sumeru-outline 选题 "玄幻 系统+签到+无敌" 起点平台
/sumeru-outline 选题 "言情 穿越+宫斗+甜宠" 女频 中篇

# 指定平台和受众
/sumeru-outline 选题 "都市 异能+鉴宝+赘婿" 番茄平台 男频
/sumeru-outline 选题 "悬疑 无限流+密室逃脱+灵异" 中性向 中篇

# 直接进入大纲（不执行选题）
/sumeru-outline "重生2000年靠互联网创业"
```

---

#### 2. 大纲设计 Skill（含选题策划）
**适用场景**：写小说大纲、设计人设、做世界观设定、生成章节细纲，向前覆盖选题策划
**功能**：首阶段执行选题策划（市场分析+创意引擎），第二阶段生成 `plan.md`、`outline.md` 和 `outlines/chapters.json`，覆盖世界观、人物、剧情框架、伏笔管理表、爽点排布和章节任务卡。大批量细纲生成时使用子Agent并行处理。

```bash
/sumeru-outline "<核心创意描述>"
```

**可选参数说明：**
| 参数 | 说明 | 示例 |
|------|------|------|
| 复用数据 | 复用已有选题数据 | 复用已有选题数据 |
| 允许映射 | 允许映射真实地名/事件（需自行合规审核） | 允许映射真实地名 |
| 大纲风格 | 大纲风格 | 详细/精简/分卷 |

**示例：**
```bash
# 基础用法
/sumeru-outline "重生2000年靠互联网创业"
/sumeru-outline 复用已有选题数据  # 复用选题阶段生成的创意

# 指定大纲风格
/sumeru-outline "高武世界+校花+系统+高考逆袭" 分卷式大纲   # 生成分卷式大纲
/sumeru-outline "古代权谋+皇子夺嫡+穿越" 允许映射真实地名  # 允许映射真实历史背景

# 复用已有数据继续完善
/sumeru-outline "星际文明+机甲战斗+虫族入侵" 复用已有大纲草稿  # 复用之前的大纲草稿继续完善
```

> 💡 **细纲驱动**：大纲设计完成后自动生成 `outlines/chapters.json`，供 `sumeru-write` 进行细纲驱动的并行批量创作。

---

#### 3. 章节撰写 Skill
**适用场景**：生成章节内容、续写、重写、批量创作
**功能**：**细纲驱动生成**，自动读取 `outlines/chapters.json`，支持单章或批量并行生成章节。使用单一通用写作模式，保持人物性格与剧情一致性，批量生成时每个子Agent最多负责3章。

```bash
/sumeru-write <章节号> "<章节概要>"
```

**可选参数说明：**
| 参数 | 说明 | 示例 |
|------|------|------|
| 风格 | 写作风格 | 仙侠/都市/古风 |
| 字数 | 目标字数 | 2000/3000字 |
| 节奏 | 节奏控制 | 快/中/慢 |
| 视角 | 视角 | 主角/配角/上帝视角 |
| 续写 | 续写已有内容 | 续写 |
| 按细纲生成 | 基于已有细纲生成 | 按细纲生成 |
| 强化爽点 | 强化爽点/打脸情节 | 强化爽点 |

**示例：**
```bash
# 细纲驱动批量生成（推荐）
/sumeru-write 全部章节                           # 从细纲生成所有章节（自动并行）
/sumeru-write 第1-50章                            # 生成指定范围章节
/sumeru-write 第1卷                               # 生成特定卷的所有章节
/sumeru-write 第3章,第5章,第10章                   # 生成特定章节

# 单章创作
/sumeru-write 第3章 "主角首次使用金手指震惊众人" 仙侠风格 强化爽点 2500字
/sumeru-write 第3章 按细纲生成                     # 基于已有细纲生成

# 续写与重写
/sumeru-write 第5章 续写                           # 续写第4章之后的内容

# 批量并行创作
/sumeru-write 第1-100章 批量并行                   # 并行批量生成100章内容

# 更多实用场景
/sumeru-write 第1章 "主角重生回到高考前一天" 都市风格 快节奏 2000字  # 快节奏开篇
/sumeru-write 第20-30章 女配视角 古风             # 从女配视角写10章内容
/sumeru-write 第15章 "拍卖会冲突" 强化爽点 3000字   # 强化打脸爽点的章节
```

> 💡 **并行约束**：批量生成时每个子Agent最多负责3个章节，所需Agent数 = ceil(总章节数 / 3)，自动分配。

---

#### 4. 逻辑审查 Skill
**适用场景**：检查剧情bug、时间线错误、人物OOC、逻辑漏洞、字数不足
**功能**：默认做目标范围最小审查，检查剧情统一、时间线、人物OOC、伏笔、字数和常识问题。轻量问题直接修复为最终版本；需要重写的章节生成修复计划。用户要求全书审查时才生成完整报告。

```bash
/sumeru-review <章节范围>
```

**三阶段审查流程：**
1. **范围审查**：只读取目标章节、前后必要摘要和 continuity 状态
2. **章节细节审查**：检查字数、时间线、人物OOC、物品状态、伏笔设置（必要时子Agent并行）
3. **统一修复**：轻量修复直接修改 chapters/ → 需重写章节生成 fix-plan.json

**支持检查的问题类型：**
- 字数检查：章节字数达标检查，不足自动填充
- 时间线：时间线/年龄/事件顺序一致性
- 人物OOC：人物性格/行为OOC检查
- 剧情逻辑：剧情逻辑/设定一致性
- 伏笔：伏笔回收检查
- 常识：常识/因果合理性检查

**示例：**
```bash
# 基础用法
/sumeru-review 第1-50章
/sumeru-review 审查全部内容
/sumeru-review 第1-20章 仅检查时间线和人物OOC

# 指定检查类型
/sumeru-review 第30-80章 仅检查剧情和伏笔  # 检查剧情矛盾和伏笔回收情况
/sumeru-review 第10-15章 仅检查常识         # 检查这几章的常识/逻辑合理性
/sumeru-review 第1-30章 仅检查字数           # 检查章节字数是否达标
```

> 💡 **自动修复**：审查后自动修复所有轻量级问题（文字修正、段落调整、字数填充等），结果直接修改 `chapters/` 目录，修改前自动备份到 `.sumeru/write/original/`。需要重写的章节记录到 `fix-plan.json`，由 worldbuilder 编排或用户手动调用 `sumeru-write` 处理。

---

#### 5. 内容润色 Skill
**适用场景**：优化文笔、调整节奏、强化爽点、统一风格
**功能**：专注文笔与内容层面优化，支持多风格转换，针对性优化节奏、爽点、对话、悬念等。润色结果直接修改 chapters/ 目录为最终版本，修改前自动备份；用户提供片段时不生成 context pack。

```bash
/sumeru-polish <章节范围>
```

**润色级别说明：**
- 轻度：句式微调，保留原文冗余与口语化特征（保留80%以上原文）
- 中度：重构段落节奏，增强画面感与情绪张力（保留60%原文核心表达）
- 深度：逐句打磨，强化个人化表达与阅读沉浸感（保留核心情节脉络）

**可选参数说明：**
| 参数 | 说明 | 示例 |
|------|------|------|
| 润色级别 | 润色级别 | 轻度/中度/深度 |
| 目标风格 | 目标风格 | 小白爽文/精品文/古风/都市现实/悬疑/科幻 |
| 优化重点 | 优化重点 | 爽点强化、对话优化、文笔提升、悬念增强 |

**示例：**
```bash
# 基础用法
/sumeru-polish 第10章 中度润色 小白爽文风格 强化爽点
/sumeru-polish 第1-3章 轻度润色  # 轻度润色，优化表达流畅度
/sumeru-polish 第5章 深度润色 对话优化+文笔提升

# 更多实用场景
/sumeru-polish 第1-20章 古风风格 文笔提升       # 将前20章转为古风风格，提升文笔
/sumeru-polish 第35章 深度润色 悬念增强+爽点强化  # 深度优化章节悬念和爽点
/sumeru-polish 第1-100章 轻度润色               # 全本轻度润色，优化文字流畅度
```

---

#### 6. 完稿校验 Skill
**适用场景**：完稿检查、敏感词检测、md/txt 导出
**功能**：错别字/标点/语法错误修正，三级敏感内容检测与修正建议，格式标准化，md/txt 分章+整文导出，批量替换与自动分段，**批量处理时使用子Agent并行校验，每个Agent最多负责3个章节**。

> 💡 **Skill 边界**：技术性文字校验（错别字/标点/语法）由本Skill负责，`sumeru-polish` 专注文笔和内容层面优化，两者互补不重叠。

```bash
/sumeru-finalize
```

**可选参数说明：**
| 参数 | 说明 | 示例 |
|------|------|------|
| 导出格式 | 导出格式 | md/txt/全部 |
| 修复导出 | 按当前规则重新导出 | 修复导出 |
| 批量替换 | 启用全局替换功能 | 替换"旧词"为"新词" |
| 自动分段 | 自动分段优化（适配手机阅读） | 自动分段 |

**导出格式说明：**
| 格式 | 分章 | 整文 |
|------|------|------|
| **md** | `publish/chapters/001.md`（每章第一行 `第X章 标题`） | `publish/full.md`（全文合并，空行分隔） |
| **txt** | `publish/chapters/001.txt`（同上，纯文本） | `publish/full.txt`（同上，纯文本） |

**示例：**
```bash
# 基础用法
/sumeru-finalize 导出md格式
/sumeru-finalize 导出txt格式
/sumeru-finalize 导出全部

# 修复已有导出
/sumeru-finalize 修复导出

# 批量替换+自动分段
/sumeru-finalize 替换"张三"为"李玄" 导出全部 自动分段
```

---

#### 7. 项目迁移 Skill
**适用场景**：旧版本项目升级、项目结构不完整、查缺补漏、路径迁移、迁移后接续创作
**功能**：扫描现有项目结构，识别文件缺失和字段问题，自动迁移旧路径、补齐配置文件、生成人物卡、补全章节任务卡字段。**v1.3.0+ 支持接续协议（H1-H6）**：迁移后自动推断补做 `creative-anchors.md` / `intro.md` / 状态标记，写入 `status.json.migrationHandoff` 字段，worldbuilder 后续按字段状态决定跳过/进入确认流程，实现迁移→续作闭环。

```bash
/sumeru-migrate                    # 完整迁移检查与修复（含接续协议）
/sumeru-migrate 仅检查             # 只检查不修复
/sumeru-migrate 仅迁移路径         # 只迁移旧路径
/sumeru-migrate 补齐配置           # 只补齐配置文件
/sumeru-migrate 补齐人物卡         # 只生成缺失的人物卡
```

**可选参数说明：**
| 参数 | 说明 | 示例 |
|------|------|------|
| 仅检查 | 只扫描不修复 | `/sumeru-migrate 仅检查` |
| 仅迁移路径 | 只迁移旧路径到新路径 | `/sumeru-migrate 仅迁移路径` |
| 补齐配置 | 只补齐缺失的配置文件 | `/sumeru-migrate 补齐配置` |
| 补齐人物卡 | 只生成缺失的人物卡 | `/sumeru-migrate 补齐人物卡` |

**示例：**
```bash
# 基础用法
/sumeru-migrate                          # 完整迁移检查与修复

# 仅检查
/sumeru-migrate 仅检查                   # 只检查项目完整性，不修复

# 仅迁移路径
/sumeru-migrate 仅迁移路径               # 只迁移旧路径到新 canonical 路径

# 补齐特定内容
/sumeru-migrate 补齐配置                 # 只补齐缺失的配置文件
/sumeru-migrate 补齐人物卡               # 只生成缺失的人物卡
```

**支持的迁移项：**
- 旧路径迁移：`.sumeru/outline/chapter-outlines.json` → `outlines/chapters.json`
- 旧路径迁移：`.sumeru/issues/index.json` → `.sumeru/issues.md`
- 旧路径迁移：`docs/*` → `plan.md`
- 配置补齐：`project.json`、`status.json` 等
- 目录补齐：`chapters/`、`characters/`、`outlines/` 等
- 字段补全：章节任务卡必填字段
- 人物卡生成：从大纲提取人物信息

## 💾 数据持久化

### 数据存储规范
- **中间数据**：仅系统内部使用的临时数据、元数据、进度信息等，统一存储在 `.sumeru/` 目录下，支持断点恢复与数据复用，用户无需关心
- **用户可见输出**：所有最终成果直接保存在当前工作目录下，用户可直接查看和使用

#### 中间数据目录（.sumeru/）
```
.sumeru/
├── project.json      # 项目配置
├── status.json       # 阶段与章节状态
├── backlog.md        # 待办、待补设定、剧情坑
├── decisions.md      # 重要创作决策
├── changelog.md      # 改动记录
├── continuity/       # 时间线、人物、物品、伏笔、世界状态
├── issues.md         # 合并问题清单
├── cache/            # 项目/世界观/人物/风格/创意/连续性/issue摘要缓存
├── context-packs/    # write/review/polish/finalize 子Agent上下文包
├── topic/            # 选题阶段中间数据
├── outline/          # 旧版大纲兼容数据（只读优先）
├── outlines/         # chapters.json 章节任务卡
├── reviews/           # 按需生成的逻辑审查报告
├── tests/             # 按需生成的连贯性/章节验收/伏笔/字数/release 检查
├── write/            # 创作阶段中间数据
│   └── original/     # 原始章节备份（review/polish修改前自动备份）
├── review/           # 审查阶段中间数据
│   └── fix-plan.json # 重写修复计划（标记需要重写的章节）
├── polish/           # 润色阶段中间数据
└── finalize/         # 完稿阶段中间数据
```

#### 用户可见输出（当前工作目录）
```
./
├── README.md          # 小说首页：书名、简介、标签、平台映射
├── plan.md            # 需求、设定、人物、风格、创意策略、术语
├── outline.md         # 故事架构、主线、伏笔管理表、分卷与章节规划摘要
├── chapters/          # 章节正文（按 001-标题.md 命名）
└── publish/           # 完稿导出（full.md、full.txt、chapters/ 分章）
```

所有创作过程支持断点恢复，中断后无需重头开始。

### 风格样本（可选）

用户可提供个人写作风格样本，让AI模仿其用词、句式、对话和情绪表达习惯。

**使用方式**：
1. 大纲完成后，系统会询问是否提供风格样本（不提供不影响后续）
2. 复制 `style-samples/sample-template.md` 模板
3. 填写你的写作片段（对话、情绪描写、叙事、比喻各300-500字）
4. 保存为 `style-samples/user-sample-<时间戳>.md`
5. 告诉AI文件路径，或直接在对话中粘贴

**目录结构**：
```
style-samples/
├── sample-template.md   # 提交模板
└── user-style.md        # 系统自动生成的风格特征分析
```

**效果**：AI会在后续写作中主动模仿样本中的用词习惯、句式特点、对话风格和情绪表达方式。

## 🎨 核心优势

### 合规安全
- 自动生成虚构的人名、地名、势力名，避免侵权风险
- 三级敏感词检测与修正建议，降低发布风险
- 符合各大平台内容规范要求

### 效率提升
- 多Agent并行创作，效率提升5倍以上
- 智能爽点排布，遵循网文创作黄金节奏公式
- 伏笔管理表自动追踪，提醒回收时机

### 质量保障
- 人物性格与剧情逻辑一致性校验
- 时间线与世界设定合理性检查
- 多轮润色优化，兼顾文笔与节奏

## 🤝 参与贡献

本项目基于 [xindoo/sumeru](https://github.com/xindoo/sumeru) 二次开发，欢迎提交Issue和PR来完善！
- 新增Skill需遵循现有架构规范
- 所有新增功能需包含对应的测试用例
- 提交前请确保通过所有现有测试
- 如有问题可参考原版项目或在此提交Issue

## 📄 许可证

MIT License

---

**让AI成为你的创作伙伴，释放想象力，专注故事本身 ✍️**
