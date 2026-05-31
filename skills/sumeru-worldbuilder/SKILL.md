---
name: sumeru-worldbuilder
description: 网文/小说全流程创作世界构建师和项目管理器。用户想从零写小说、初始化小说项目、把创意发展成完整作品、自动完成选题/大纲/章节/审查/润色/导出，或说"我想写小说""帮我写本XX类型小说""给我整个小说创作流程"时必须使用本技能。version: 1.2.0
type: skill
user-invocable: true
---

> 依赖 `sumeru-rules`，默�?`quiet` 模式�?

## 网文创作世界构建�?

### 触发关键�?
我想写小说、写一本网文、从零开始创作小说、帮我写本XX类型的小说、我要写本小说、给我整个小说创作流程、自动写小说、小说创作一站式服务、帮我完成一本小说、我只有创意怎么写小说、从零开始写网文、小说全流程创作、初始化小说项目、新建小说项�?

> **�?sumeru-write 的区�?*：worldbuilder 负责"从零到完�?的全流程统筹；write 负责具体�?�?续写/扩写/重写章节"。用户说"帮我写小�?且未指定具体章节时走 worldbuilder；明确说"写第X�?�?续写"�?扩写这段"时走 write�?

### 核心功能
worldbuilder 是网文创作的一站式主控技能，负责统筹协调从创意萌芽到作品完稿的完整创作链路：

0. **项目初始�?*：创建标准小说项目目�?
1. **选题策划**：调�?`sumeru-topic` 进行市场分析、选题定位、创意引擎、平台定�?
2. **大纲设计**：调�?`sumeru-outline` 构建完整世界观、人物设定、分卷大纲与章节任务�?
2.5 **风格样本询问（可选）**：大纲完成后，询问用户是否提供写作风格样本（不提供不影响后续�?
2.6 **简介生�?*：大纲完成后自动生成 `.sumeru/intro.md`（作品名称、目标读者、类型标签、主角名、简介正文、平台标签映射）
2.7 **创意锚点确认**（新增）：大纲完成后、写作开始前，从大纲中提取核心创意锚点供用户确认
3. **内容创作**：调�?`sumeru-write` 按章节任务卡进行分章节内容撰�?
4. **逻辑审查**：调�?`sumeru-review` 对已完成章节进行项目测试式审�?
4.5 **修复**：根据审查结果修复问题（轻量 auto-fix 或重写），章节状态更新为 `fixed`
5. **内容润色**：调�?`sumeru-polish` 对已修复章节进行文笔优化
6. **完稿构建**：调�?`sumeru-finalize` 对已润色章节完成技术校验、平台格�?build �?release

### 项目初始化协�?
当用户要�?初始化小说项�?或当前目录缺�?`.sumeru/project.json` 时：

1. 根据用户指定、计划章节数、计划字数判�?`projectMode` �?`workflowLevel`
2. **模式与章节数交叉校验**：选择 mode 后执行以下检�?

   | 模式 | 推荐章节范围 | 超出时行�?|
   |------|-------------|-----------|
   | `short/light` | 1-10 �?| 超出 �?自动升级�?`medium` 并提示：`ℹ️ 章节数超�?0章，模式已自动升级为 medium/standard` |
   | `medium/standard` | 10-50 �?| 超出 50 �?�?提示：`⚠️ 章节数超�?0章，建议升级�?long/full 模式以启�?continuity 追踪。确认继�?medium 或自动升级？`，用户确认后写入 decisions.md |
   | `long/full` | 50 章以�?| 符合 |

   mode 确认后写�?`.sumeru/project.json`，并将验证结果记录到 `.sumeru/decisions.md`

3. 写入 `.sumeru/project.json`（含 `projectMode` �?`workflowLevel`�?
4. 生成 `.sumeru/status.json`
5. 按模式创建目录（不一刀切创�?full 结构�?
6. 生成必要 cache �?context pack
7. 生成 `.sumeru/backlog.md`、`.sumeru/decisions.md`、`.sumeru/changelog.md`

### 模式初始�?
| 模式 | 创建内容 |
|------|----------|
| `short/light` | `README.md`、`story.md`、`outline.md`、`.sumeru/project.json`、`.sumeru/status.json`、`.sumeru/cache/story-brief.md` |
| `medium/standard` | `README.md`、`plan.md`、`outline.md`、`outlines/chapters.json`、`characters/`、`.sumeru/intro.md`、`chapters/`、`publish/`、`.sumeru/cache/`、`.sumeru/issues.md` |
| `long/full` | medium 结构 + `world.md`、`.sumeru/context-packs/`、`.sumeru/continuity/`、必要时 `reviews/`、`tests/` |

### 模式升级协议
- `short -> medium`：补�?`plan.md`、`outlines/chapters.json`、`chapters/`、标�?cache
- `medium -> long`：补�?`.sumeru/context-packs/`、`.sumeru/continuity/`，`reviews/` �?`tests/` 按需创建
- 升级后更�?`.sumeru/project.json`，记录到 `.sumeru/decisions.md` �?`.sumeru/changelog.md`

**自动触发升级的条�?*：当项目恢复时，�?`chapters/` �?`outlines/chapters.json` 中的实际章节数超出当�?mode 推荐范围，worldbuilder 应主动提示升级，并询问用户是否确认。用户拒绝时记录�?`.sumeru/decisions.md`�?

### 项目状态机
**阶段顺序**：`init -> topic -> outline -> intro -> anchor -> write -> review -> fix -> polish -> finalize -> build/release`

**章节状态顺�?*：`planned -> drafted -> reviewed -> fixed -> polished -> finalized -> exported`

**推进规则**�?
- `topic` 完成：`plan.md` 已写入，至少包含选题方向和核心创意，且包含目标平台信�?
- `outline` 完成：`outline.md`、`outlines/chapters.json`、`.sumeru/intro.md` 存在，且章节任务卡通过字段完整性验证（所有章节包含全部必填字段：`purpose`、`events`、`outputs`、`acceptanceCriteria`、`creativeGoal`、`emotionalBeat`、`readerMemoryPoint`、`tropeToAvoid`、`protectedElements`、`rhythm`�?
- `anchor` 完成：`.sumeru/creative-anchors.md` 存在，至�?3 个用户确认的锚点
- `write` 完成：目标章节文件存在，章节状态更新为 `drafted`，且没有缺章
- `review` 完成：目标范围已审查，问题写�?`.sumeru/issues.md`；完整报告和 tests 仅在用户要求时生�?
- `fix` 完成：轻量问题已修复，重写问题已转为 `needs-rewrite` 或完成重写；反审验证通过后章节状态更新为 `fixed`
- `polish` 完成：章节状态更新为 `polished`；发现逻辑硬伤时自动触发反�?
- `finalize` 完成：技术校验通过，章节状态更新为 `finalized`

> 子Agent并行规则、分片策略、输出级别见 `sumeru-rules`�?

📝 写作�?.. �?37/50 �?(74%)

**阶段完成时简洁总结�?*
```
�?�?3 阶段完成：章节撰�?
   已生�?50 章，�?125,000 �?
   �?进入下一阶段：逻辑审查
```

**有问题时才提醒：**
```
⚠️ �?25 章字数不足（1200 字，建议 2000+�?
```

**不输出：**
- �?脚本详细输出
- �?中间报告内容
- �?技术细节（Agent 数量、context pack 等）

**用户可指定输出级别：**
```
/sumeru-worldbuilder 玄幻 "废柴逆袭" 输出级别 normal
/sumeru-worldbuilder 玄幻 "废柴逆袭" 输出级别 verbose  # 调试�?
```

### 交互式需求引�?
当用户提供的信息过于简略时，自动触发交互式提问�?

**基础信息确认（必问）**�?
1. 题材确认（细分类型）
2. 篇幅预期
3. 核心爽点
4. 受众定位
5. **目标发布平台**（起�?番茄/七猫/晋江/纵横/其他，必填，选题时进行平台定向分析）

**核心设定引导（可选）**�?
5. 主角设定偏好
6. 反派设定偏好
7. 世界观偏�?
8. 参考作�?

**风格偏好设置（可选）**�?
9. 写作风格
10. 发布平台
11. 禁忌内容

### Skill 协调流程
```
用户需�?�?收集需�?�?topic[选题策划+平台定向] �?outline[大纲设计] �?intro[简介生成] �?anchor[创意锚点确认] �?write �?review �?[fix] �?polish �?finalize �?build/release
                                     �?
                             阶段检查点验证
```

### 使用示例
```
/sumeru-worldbuilder 玄幻 "废柴逆袭+系统�?
/sumeru-worldbuilder 言�?"霸道总裁+契约恋爱" 标题"总裁的契约新�?
/sumeru-worldbuilder 玄幻 "废柴逆袭+系统�? 恢复上次创作
/sumeru-worldbuilder 都市 "职场+重生" 跳过选题阶段
/sumeru-worldbuilder 悬疑 "连环杀�?心理侧写+反转" 详写风格 暗黑调�?
```

### 小说简介生�?

大纲完成后自动生成。从 `plan.md` 提取作品名称、目标读者、主角名、核心设定，�?`outlines/chapters.json` 提取主线冲突和爽点，撰写 300-500 字简介正文（困境→转折→冲突→悬念），生成平台标签映射，写入 `.sumeru/intro.md`。仅首次生成，后续不覆盖手动修改�?

**简介质量：** 作品名称简洁、目标读者明确、标签≥8个且来自平台标签库、正文含四要素、不剧透关键反转、结尾有传播句�?

### 创意锚点确认机制

> **目标**：在大纲完成后，从AI生成的完整大纲中提炼�?只属于本�?的核心创意锚点，让用户确�?修改，作为后续所有写作的不可动摇的创意基准�?

#### 锚点提取

父Agent�?`plan.md` �?`outline.md` 中提�?5-7 个候选锚点，分为以下类型�?

| 锚点类型 | 含义 | 示例 |
|----------|------|------|
| **核心反差** | 主角/世界最独特的矛盾设�?| "最强废�?——战力体系第一却被所有人认为是废�?|
| **情感�?* | 贯穿全书的核心情感驱�?| "为师父复�?——所有选择最终指向这个执�?|
| **设定钩子** | 最独特的设�?金手�?| "每次死亡都回�?天前，但记忆保留" |
| **关系张力** | 最重要的人物关系矛�?| "必须杀了她才能活，但她是唯一理解你的�? |
| **名场面种�?* | 全书必须兑现的高概念场景 | "在万人面前展示真实实力，让所有嘲笑者闭�? |
| **价值观冲突** | 本书探讨的核心价值冲�?| "力量至上 vs 人性底�? |
| **风格签名** | 本书最独特的叙事风�?腔调 | "冷幽�?暗黑童话�? |

#### 确认流程

1. 父Agent提取候选锚点并输出表格
2. 用户逐条确认（保�?修改/删除/新增�?
3. 确认后的锚点列表写入 `.sumeru/creative-anchors.md`
4. 每个锚点标记�?`confirmed` / `user_modified` / `user_added`

#### 后续使用

- **context pack 注入**：写作阶段每�?shared context pack 开头插入锚点速查
- **子Agent自检**：每章必须至少体�?1 个锚点（写作自检增加此项�?
- **review 验证**：审查阶段检查锚点是否被稀�?遗忘，连�?3 章未体现任何锚点 �?标记 `high` 警告
- **修改保护**：锚点被视为 `protectedElements` 的最高优先级，子Agent不可违背
