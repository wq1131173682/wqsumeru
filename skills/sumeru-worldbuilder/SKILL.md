---
name: sumeru-worldbuilder
description: 网文/小说全流程创作世界构建师和项目管理器
version: 1.2.2
type: skill
argument-hint: '[题材] ["核心创意"] [标题"xxx"] [长篇/中篇/短篇] [风格] [跳过...]'
disable-model-invocation: false
user-invocable: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, task
context: project
agent: build
---

> 依赖 `sumeru-rules`，默认 `quiet` 模式。

## 网文创作世界构建师

### 触发关键词
我想写小说、写一本网文、从零开始创作小说、帮我写本XX类型的小说、我要写本小说、给我整个小说创作流程、自动写小说、小说创作一站式服务、帮我完成一本小说、我只有创意怎么写小说、从零开始写网文、小说全流程创作、初始化小说项目、新建小说项目

> **与 sumeru-write 的区别**：worldbuilder 负责"从零到完稿"的全流程统筹；write 负责具体的写续写/扩写/重写章节。用户说"帮我写小说且未指定具体章节时走 worldbuilder；明确说"写第X章、续写"、扩写这段"时走 write。

### 核心功能
worldbuilder 是网文创作的一站式主控技能，负责统筹协调从创意萌芽到作品完稿的完整创作链路：

0. **项目初始化**：创建标准小说项目目录
1. **选题策划**：调用 `sumeru-topic` 进行市场分析、选题定位、创意引擎、平台定向
2. **大纲设计**：调用 `sumeru-outline` 构建完整世界观、人物设定、分卷大纲与章节任务单
2.5 **风格样本询问（可选）**：大纲完成后，询问用户是否提供写作风格样本（不提供不影响后续）。
2.6 **简介生成**：大纲完成后自动生成 `.sumeru/intro.md`（作品名称、目标读者、类型标签、主角名、简介正文、平台标签映射）
2.7 **创意锚点确认**（新增）：大纲完成后、写作开始前，从大纲中提取核心创意锚点供用户确认
3. **内容创作**：调用 `sumeru-write` 按章节任务卡进行分章节内容撰写
4. **逻辑审查**：调用 `sumeru-review` 对已完成章节进行项目测试式审查
4.5 **修复**：根据审查结果修复问题（轻量 auto-fix 或重写），章节状态更新为 `fixed`
5. **内容润色**：调用 `sumeru-polish` 对已修复章节进行文笔优化
6. **完稿构建**：调用 `sumeru-finalize` 对已润色章节完成技术校验、平台格式 build 和 release

### 项目初始化协议
当用户要求初始化小说项目或当前目录缺失 `.sumeru/project.json` 时：

1. 根据用户指定、计划章节数、计划字数判断 `projectMode` 和 `workflowLevel`
2. **模式与章节数交叉校验**：选择 mode 后执行以下检查

   | 模式 | 推荐章节范围 | 超出时行为 |
   |------|-------------|-----------|
   | `short/light` | 1-10 章 | 超出 → 自动升级为 `medium` 并提示：`ℹ️ 章节数超过 10 章，模式已自动升级为 medium/standard` |
   | `medium/standard` | 10-50 章 | 超出 50 章 → 提示：`⚠️ 章节数超过 50 章，建议升级为 long/full 模式以启用 continuity 追踪。确认继续 medium 或自动升级？`，用户确认后写入 decisions.md |
   | `long/full` | 50 章以上 | 符合 |

   mode 确认后写入 `.sumeru/project.json`，并将验证结果记录到 `.sumeru/decisions.md`

3. **分卷模式判定**：当以下任一条件满足时启用分卷模式 —
   - 计划章节数 ≥ 150
   - 用户明确要求"分卷"或指定卷数

   满足条件时计算 `volumeCount`：按每卷 150-250 章均分计划章节数，记录到 `.sumeru/project.json` 的 `volumeCount` / `currentVolume` / `volumes[vol-N]` 字段。例如 200 章 / 每卷约 150 章 → `volumeCount = 2`：`vol-001`（第 1-150 章）、`vol-002`（第 151-200 章）。结果写入 `.sumeru/decisions.md`。具体规范见 `sumeru-rules/SKILL.md` 第十五部分·分卷隔离与卷切换协议。
4. 写入 `.sumeru/project.json`（含 `projectMode` 和 `workflowLevel`，分卷模式下同时写入 `volumeCount` / `currentVolume` / `volumes`）
5. 生成 `.sumeru/status.json`
6. 按模式创建目录（不一次性创建 full 结构）
7. 生成必要 cache 和 context pack
8. 生成 `.sumeru/backlog.md`、`.sumeru/decisions.md`、`.sumeru/changelog.md`

### 模式初始化
| 模式 | 创建内容 |
|------|----------|
| `short/light` | `README.md`、`story.md`、`outline.md`、`.sumeru/project.json`、`.sumeru/status.json`、`.sumeru/cache/story-brief.md` |
| `medium/standard` | `README.md`、`plan.md`、`outline.md`、`outlines/chapters.json`、`characters/`、`.sumeru/intro.md`、`chapters/`、`publish/`、`.sumeru/cache/`、`.sumeru/issues.md`、`.sumeru/continuity/consistency-rules.json`（空 schema，见 `sumeru-rules/SKILL.md` §consistency-rules.json 格式；medium 模式同样启用 `sumeru-review/scripts/continuity-check.py` / `foreshadowing-tracker.py` 校验） |
| `long/full` | medium 结构 + `world.md`、`.sumeru/context-packs/`、必要时 `reviews/`、`tests/` + `.sumeru/volumes/`（若 `volumeCount >= 2`）+ `.sumeru/cross-volume/` |

### 模式升级协议
- `short -> medium`：补齐 `plan.md`、`outlines/chapters.json`、`chapters/`、标准 cache
- `medium -> long`：补齐 `.sumeru/context-packs/`，`reviews/` 和 `tests/` 按需创建
- 升级后更新 `.sumeru/project.json`，记录到 `.sumeru/decisions.md` 和 `.sumeru/changelog.md`

**自动触发升级的条件**：当项目恢复时，若 `chapters/` 或 `outlines/chapters.json` 中的实际章节数超出当前 mode 推荐范围，worldbuilder 应主动提示升级，并询问用户是否确认。用户拒绝时记录到 `.sumeru/decisions.md`。

### 项目恢复与迁移接续协议

> **目标**：识别三类"恢复"场景——常规恢复、迁移后接续、新项目——避免混淆 anchor/intro 必填项与历史未走迁移协议的项目。
>
> **配套**：`sumeru-migrate` v1.3.0+ 写入 `status.json.migrationHandoff` 字段；本端读取该字段决定续作路径。
> **字段 Schema**：`sumeru-migrate/SKILL.md` §11.5、**状态机语义**：`sumeru-rules` §状态字段语义对照。

#### 触发命令
```
/sumeru-worldbuilder {题材} 恢复上次创作
```

#### 入口检测三态
| 检测结果 | 处理路径 |
|----------|----------|
| `status.json.migrationHandoff` 存在 | **接续模式**：按字段分流入 anchor/intro 确认，详见下表 |
| `migrationHandoff` 不存在但 `.sumeru/migration.json` 存在 | **警告**：旧版迁移未出 handoff。提示先跑 `/sumeru-migrate` 补齐接续协议（子模式选"补齐配置"），再回来续作 |
| 两者都不存在 | **常规恢复模式**：检查 `chapters/` 文件数和模式升级，沿用上述"自动触发升级的条件"逻辑 |

#### 字段处理细则（接续模式）
| handoff 字段 | worldbuilder 行为 |
|--------------|------------------|
| `anchorStatus = pending` | 进入 anchor 确认流程；要求用户逐条标 `confirmed` / `user_modified` / `user_added`；全部确认后写回 `.sumeru/creative-anchors.md` 并把字段升级为 `confirmed` |
| `anchorStatus = confirmed` | 跳过 anchor 阶段，直接进入 write |
| `anchorStatus = skipped` | 写一条 warning 到 `.sumeru/issues.md`（"迁移时跳过 anchor，建议补做"），允许用户继续但不弹窗 |
| `introStatus = pending` | 引导用户校对 `.sumeru/intro.md`（300-500 字，四要素：困境→转折→冲突→悬念），校对完成标 `confirmed` |
| `introStatus = confirmed` | 跳过 intro 阶段 |
| `introStatus = skipped` | 写一条 warning（"迁移时跳过 intro，建议补做"），允许用户继续 |

#### recommendedNext 字段
- 读 `recommendedNext`，若为 `/sumeru-worldbuilder 恢复上次创作`，按上表三态处理
- 若为 `/sumeru-outline 重新生成` 等其他值，原样输出推荐命令给用户，**不替用户做决定**
- 字段缺失时默认 `"/sumeru-worldbuilder 恢复上次创作"`，按 handoff 是否存在继续走三态分支

#### 字段正交性与审计
- `migrationHandoff` 只增不改，**不参与** `currentStage` 流转
- 接续模式完成后，worldbuilder 推进 `currentStage` 到 anchor 完成（若 anchor 新确认）或 write（若 anchor 跳过）
- handoff 字段保留在 `status.json` 作为审计轨迹，**不删除**
- 每次接续动作追加一条到 `.sumeru/changelog.md`（时间戳 + 接续状态 + 实际走的分支）

### 项目状态机
**阶段顺序（扁平模式）**：`[migrate? →] init → topic → outline → intro → anchor → write → review → fix → polish → finalize → build/release`

**阶段顺序（分卷模式，`volumeCount >= 2`）**：`[migrate? →] init → topic → outline → intro → anchor → write → [volume_handoff? → write → ...] → review → fix → polish → finalize → build/release`

> **migrate 前缀**：对于已有旧项目（存在 `chapters/` 但缺少 `.sumeru/` 规范目录的项目），第一阶段应为调用 `sumeru-migrate` 完成旧项目迁移规整，再进入 `init`。新项目直接跳过此步。
>
> **volume_handoff 中间态**：仅当分卷模式下写完当前卷最后一章时插入，详见"分卷模式编排"节。扁平模式永不触发。

**章节状态流转**：`planned -> drafted -> reviewed -> fixed -> polished -> finalized -> exported`

**卷状态流转（分卷模式）**：`planned -> active -> completed -> archived`，存储在 `.sumeru/project.json.volumes[vol-N].status`，详见"分卷模式编排"节。

**推进规则**：
- `topic` 完成：`plan.md` 已写入，至少包含选题方向和核心创意，且包含目标平台信息
- `outline` 完成：`outline.md`、`outlines/chapters.json`、`.sumeru/intro.md` 存在，且章节任务卡通过字段完整性验证（所有章节包含全部必填字段：`purpose`、`events`、`outputs`、`acceptanceCriteria`、`creativeGoal`、`emotionalBeat`、`readerMemoryPoint`、`tropeToAvoid`、`protectedElements`、`rhythm`）
- `anchor` 完成：`.sumeru/creative-anchors.md` 存在，至少 3 个用户确认的锚点
- `write` 完成：目标章节文件存在，章节状态更新为 `drafted`，且没有缺章
- `review` 完成：目标范围已审查，问题写入 `.sumeru/issues.md`；完整报告和 tests 仅在用户要求时生成
- `fix` 完成：轻量问题已修复，重写问题已转为 `needs-rewrite` 或完成重写；反审验证通过后章节状态更新为 `fixed`
- `polish` 完成：章节状态更新为 `polished`；发现逻辑硬伤时自动触发反审
- `finalize` 完成：技术校验通过，章节状态更新为 `finalized`

> 子 Agent 并行规则、分片策略、输出级别见 `sumeru-rules`。

📝 写作中... 第 37/50 章 (74%)

**阶段完成时简洁总结：**
```
✅ 第3 阶段完成：章节撰写
   已生成 50 章，共 125,000 字
   → 进入下一阶段：逻辑审查
```

**有问题时才提醒：**
```
⚠️ 第 25 章字数不足（1200 字，建议 2000+）。
```

**不输出：**
- ✗ 脚本详细输出
- ✗ 中间报告内容
- ✗ 技术细节（Agent 数量、context pack 等）

**用户可指定输出级别：**
```
/sumeru-worldbuilder 玄幻 "废柴逆袭" 输出级别 normal
/sumeru-worldbuilder 玄幻 "废柴逆袭" 输出级别 verbose  # 调试用
```

### 交互式需求引导
当用户提供的信息过于简略时，自动触发交互式提问：

**基础信息确认（必问）**：
1. 题材确认（细分类型）
2. 篇幅预期
3. 核心爽点
4. 受众定位
5. **目标发布平台**（起点/番茄/七猫/晋江/纵横/其他，必填，选题时进行平台定向分析）

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
用户需求→收集需求→[migrate? →] topic[选题策划+平台定向] →outline[大纲设计] →intro[简介生成] →anchor[创意锚点确认] →write →[volume_handoff? 分卷模式触发时插入] →review →[fix] →polish →finalize →build/release
                                      →
                              阶段检查点验证
```

> `[volume_handoff?]` 为分卷模式（`volumeCount >= 2`）的**条件中间节点**：仅当写完当前卷最后一章时插入，执行 Phase A→B→C 卷切换后回到 `write`；扁平模式不出现。详见"分卷模式编排"节与 `sumeru-rules/SKILL.md` 第十五部分·分卷隔离与卷切换协议。

### 使用示例
```
/sumeru-worldbuilder 玄幻 "废柴逆袭+系统流"
/sumeru-worldbuilder 言情 "霸道总裁+契约恋爱" 标题 "总裁的契约新娘"
/sumeru-worldbuilder 玄幻 "废柴逆袭+系统流" 恢复上次创作
/sumeru-worldbuilder 都市 "职场+重生" 跳过选题阶段
/sumeru-worldbuilder 悬疑 "连环杀人心理侧写+反转" 详写风格 暗黑调
```

### 小说简介生成

大纲完成后自动生成。从 `plan.md` 提取作品名称、目标读者、主角名、核心设定，从 `outlines/chapters.json` 提取主线冲突和爽点，撰写 300-500 字简介正文（困境→转折→冲突→悬念），生成平台标签映射，写入 `.sumeru/intro.md`。仅首次生成，后续不覆盖手动修改。

**简介质量**：作品名称简洁、目标读者明确、标签≥8 个且来自平台标签库、正文含四要素、不剧透关键反转、结尾有传播句。

### 创意锚点确认机制

> **目标**：在大纲完成后，从 AI 生成的完整大纲中提炼真正只属于本书的核心创意锚点，让用户确认修改，作为后续所有写作的不可动摇的创意基准。

#### 锚点提取

父 Agent 从 `plan.md` 和 `outline.md` 中提取 5-7 个候选锚点，分为以下类型：

| 锚点类型 | 含义 | 示例 |
|----------|------|------|
| **核心反差** | 主角/世界最独特的矛盾设定 | "最强废柴——战力体系第一却被所有人认为是废物" |
| **情感锚** | 贯穿全书的核心情感驱动 | "为师父复仇——所有选择最终指向这个执念" |
| **设定钩子** | 最独特的设定金手指 | "每次死亡都回到前一天，但记忆保留" |
| **关系张力** | 最重要的人物关系矛盾 | "必须杀了她才能活，但她是唯一理解你的人" |
| **名场面种子** | 全书必须兑现的高概念场景 | "在万人面前展示真实实力，让所有嘲笑者闭嘴" |
| **价值观冲突** | 本书探讨的核心价值冲突 | "力量至上 vs 人性底线" |
| **风格签名** | 本书最独特的叙事风格腔调 | "冷幽默暗黑童话调" |

#### 锚点附加字段

| 字段 | 适用类型 | 必填 | 含义 |
|------|----------|------|------|
| `targetChapter` | 名场面种子 | 否 | 预期兑现章节号；sumeru-write 写前检查：距当前章 ≤ 3 时在 context pack 头部注入"请在本章或近期兑现 XX 锚点"提醒 |
| `protectedTag` | 全部 | 否 | 锚点保护标签，被 sumeru-write 子 Agent 在 `protectedElements` 字段中引用；多个锚点共享同一 tag 表示绑定兑现 |

#### 确认流程

1. 父 Agent 提取候选锚点并输出表格
2. 用户逐条确认（保留/修改/删除/新增）
3. 确认后的锚点列表写入 `.sumeru/creative-anchors.md`
4. 每个锚点标记为 `confirmed` / `user_modified` / `user_added`

#### 后续使用

- **context pack 注入**：写作阶段每个 shared context pack 开头插入锚点速查
- **子 Agent 自检**：每章必须至少体现 1 个锚点（写作自检增加此项）
- **review 验证**：审查阶段检查锚点是否被悄然遗忘，连续 3 章未体现任何锚点 → 标记 `high` 警告
- **修改保护**：锚点被视为 `protectedElements` 的最高优先级，子 Agent 不可违背

### 分卷模式编排

> **目标**：当 `project.json.volumeCount >= 2` 时，worldbuilder 接管卷切换编排，保证每卷独立 continuity/cache、不污染全局、跨卷承诺可追溯。
>
> **完整规范**：见 `sumeru-rules/SKILL.md` 第十五部分·分卷隔离与卷切换协议。本节只描述 worldbuilder 的编排职责与状态机衔接。

#### 1. 分卷模式判定

- 大纲阶段完成后，worldbuilder 读取 `.sumeru/project.json.volumeCount`
- 若 `volumeCount >= 2` → 进入分卷模式（`currentVolume` / `volumes[vol-N].status` 等字段生效）
- 若 `volumeCount` 缺失或 `< 2` → 扁平模式，不触发本节任何流程

#### 2. 跨卷基础数据初始化（首次进入分卷模式时执行一次）

启用分卷模式后，worldbuilder 必须同步初始化 `.sumeru/cross-volume/` 目录：

| 文件 | 来源 | 用途 |
|------|------|------|
| `cross-volume/master-timeline.md` | 从 `outline.md` 主线时间线 + `outlines/chapters.json` 提炼 | 卷级时间线骨架，每卷交接时追加卷条目 |
| `cross-volume/master-characters.md` | 从 `characters/` 全集 + `outline.md` 人物关系表聚合 | 全局人物索引，卷切换时筛选本卷出场人物 |
| `cross-volume/dependency-table.md` | 从 `outline.md` 跨卷依赖表提取 | 登记跨卷伏笔/承诺，标注 `目标卷` 字段供 Phase B 加载 |

初始化记录写入 `.sumeru/decisions.md` 与 `.sumeru/changelog.md`。

#### 3. 卷切换流程（Volume Handoff）

当 `write` 阶段写完当前卷最后一个章节时，worldbuilder 自动进入 `volume_handoff` 状态，按 **Phase A → B → C** 顺序执行：

##### Phase A — 完成当前卷

1. 检查当前卷所有章节状态：若存在非 `drafted`（或更高）章节 → 调用 `sumeru-write` 补写至至少 `drafted`
2. 更新 `.sumeru/project.json`：`volumes[vol-N].status = "completed"`，并记录 `completedAt` 时间戳
3. 在 `.sumeru/cross-volume/master-timeline.md` 追加该卷条目
4. 在 `.sumeru/cross-volume/master-characters.md` 同步本卷人物状态变更
5. 追加 `.sumeru/changelog.md`：卷完成事件

##### Phase B — 准备下一卷（`vol-M`）

1. 创建目录树：
   ```
   .sumeru/volumes/vol-M/
   ├── continuity/
   ├── cache/batch-summaries/
   ├── characters/
   └── outline.md   # 本卷专属 outline 引用
   ```
2. 从 `.sumeru/cross-volume/` 复制状态快照（state-start.json）：当前 continuity 子集、master-characters 子集、master-timeline 到卷切换点
3. 从 `cross-volume/master-characters.md` 筛选 `vol-M` 出场人物，复制到 `vol-M/characters/`
4. 从 `cross-volume/dependency-table.md` 加载所有 `目标卷 = vol-M` 的条目，作为 `vol-M/outline.md` 的"本卷必须兑现"清单
5. 把上卷最后 1 批摘要 + 卷级总结（~500 字）保留为新卷 `batch-summaries` 第一项；更早的摘要归档到 `vol-N-archived/`

##### Phase C — 激活下一卷

1. 更新 `.sumeru/project.json`：
   - `currentVolume = "vol-M"`
   - `volumes[vol-M].status = "active"`，记录 `activatedAt`
2. 刷新 `.sumeru/status.json.currentStage = "write"`
3. 清空旧卷对应的 `.sumeru/context-packs/`，按 `vol-M` 重新生成 volume-scoped context packs（每包仅含 `vol-M/continuity/` + `vol-M/cache/` + `cross-volume/` 中本卷相关条目）
4. 追加 `.sumeru/changelog.md`：卷激活事件
5. 回到 `write` 阶段继续创作 `vol-M` 章节

#### 4. 卷状态管理

`.sumeru/project.json.volumes[vol-N].status` 取值：

```
planned → active → completed → archived
```

| 状态 | 含义 | 允许流转到 |
|------|------|-----------|
| `planned` | 已规划未开始 | `active` |
| `active` | 正在创作 | `completed` |
| `completed` | 全部章节 ≥ `drafted` | `archived` |
| `archived` | 已归档（后续审查/导出只读） | （终态） |

每次状态变更同步写入 `.sumeru/changelog.md`。

#### 5. 归档流程（卷完成 → `archived`）

当所有卷进入 `completed` 且项目准备进入 `finalize` 之前，worldbuilder 可对已完成卷执行归档：
- 把 `vol-N/continuity/`、`vol-N/cache/` 复制到 `vol-N-archived/`（压缩只读）
- `project.json.volumes[vol-N].status = "archived"`
- 保留 `vol-N/characters/` 引用以供 review/finalize 阶段查询
- 追加 `.sumeru/changelog.md`：归档事件

#### 6. 状态机衔接

项目状态机在分卷模式下扩展为：

```
[... → write → volume_handoff → write → review → fix → polish → finalize → build/release]
```

`volume_handoff` 是分卷模式下的**条件中间态**（仅当需要切卷时插入），非分卷模式永不触发。
