---
name: sumeru-migrate
description: 旧项目迁移与规整、整顿后可继续按新技能创作
version: 1.3.0
type: skill
argument-hint: "[仅检查/仅迁移路径/补齐配置/补齐人物卡]"
disable-model-invocation: false
user-invocable: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, task
model: sonnet
context: project
agent: build
---

> 依赖 `sumeru-rules`，默认`quiet` 模式。
## 旧项目迁移与规整

### 触发关键词规整项目、迁移旧项目、补齐缺失文件、检查项目完整性、修复项目结构、升级项目格式、旧项目升级、项目检查、查缺补漏、项目规范化

### 核心功能
1. **项目扫描**：全面扫描现有项目结构，识别文件缺失和字段问题2. **路径迁移**：旧路径自动迁移到新 canonical 路径
3. **配置补齐**：生成缺失的 `.sumeru/project.json`、`status.json` 等配置文件4. **目录补齐**：创建缺失的目录结构
5. **字段补全**：补齐章节任务卡缺失的必填字段6. **人物卡生成*：从大纲中提取人物信息生成人物卡
7. **迁移报告**：生成详细的迁移报告

### 使用方式

```bash
/sumeru-migrate                    # 完整迁移检查与修复
/sumeru-migrate 仅检查            # 只检查不修复
/sumeru-migrate 仅迁移路径        # 只迁移旧路径
/sumeru-migrate 补齐配置           # 只补齐配置文件/sumeru-migrate 补齐人物卡        # 只生成缺失的人物卡```

---

## 一、迁移检查清单
### 1.1 项目配置检查
| 检查项 | 修复方式 |
|--------|----------|
| `.sumeru/project.json` 不存在| 根据已有文件推断配置，生成project.json |
| `.sumeru/status.json` 不存在| 扫描 chapters/ 和outlines/ 推断状态|
| `.sumeru/changelog.md` 不存在| 创建空文件|
| `.sumeru/decisions.md` 不存在| 创建空文件|
| `.sumeru/backlog.md` 不存在| 创建空文件|
| `.sumeru/issues.md` 不存在| 创建空文件|

### 1.2 目录结构检查
| 检查项 | 修复方式 |
|--------|----------|
| `chapters/` 不存在| 创建空目录|
| `characters/` 不存在| 创建空目录|
| `outlines/` 不存在| 创建空目录|
| `publish/` 不存在| 创建空目录|
| `.sumeru/cache/` 不存在| 创建空目录|
| `.sumeru/context-packs/` 不存在| 创建空目录|
| `.sumeru/continuity/` 不存在| 创建空目录|

### 1.3 旧路径迁移检查
| 旧路径| 新路径| 迁移方式 |
|--------|--------|----------|
| `.sumeru/outline/chapter-outlines.json` | `outlines/chapters.json` | 读取旧文件，合并到新文件 |
| `.sumeru/issues/index.json` | `.sumeru/issues.md` | 读取旧JSON，转换为 Markdown |
| `docs/requirements.md` | `plan.md` | 读取旧文件，合并到plan.md |
| `docs/glossary.md` | `plan.md` 术语补| 合并到plan.md 术语部分 |
| `docs/style-guide.md` | `.sumeru/cache/style-brief.md` | 转换为缓存格式|
| `ideas/*` | `plan.md` | 合并创意到plan.md |

### 1.4 章节任务卡字段检查
`outlines/chapters.json` 每章必须包含以下 15 个必填字段：

| 字段 | 说明 |
|------|------|
| `chapter` | 章节及|
| `title` | 章节标题 |
| `purpose` | 本章核心作用 |
| `events` | 核心事件列表（≥3项） |
| `openingHook` | 具体开场方式|
| `outputs` | 必须产出内容 |
| `acceptanceCriteria` | 验收条件 |
| `creativeGoal` | 创意目标 |
| `freshnessHook` | 新鲜感来源|
| `emotionalBeat` | 情绪走向 |
| `emotionalBeatTemplate` | 情绪模板ID |
| `readerMemoryPoint` | 读者记忆点 |
| `tropeToAvoid` | 要避开的套路|
| `protectedElements` | 底线元素 |
| `rhythm` | 节奏（fast/medium/slow：|

**修复方式**：- 缺字段→件`.sumeru/outline/chapter-XXX-YYY.md` 回退补充
- 无回退源→从大纲和已有章节推断，标记为 `auto-generated`

### 1.5 人物卡检查
| 检查项 | 修复方式 |
|--------|----------|
| `characters/` 目录为空 | 件`plan.md` 和`outline.md` 提取人物信息生成 |
| 人物卡缺少必要字段| 补齐：姓名、年龄、身份、核心性格、人物弧关|
| 人物卡与大纲不一致 | 以大纲为准，更新人物卡 |

### 1.6 伏笔管理检查
| 检查项 | 修复方式 |
|--------|----------|
| `outline.md` 缺少伏笔管理补| 从已有章节提取伏笔，生成管理补|
| 伏笔缺少 ID | 自动分配 ID（F1、F2...：|
| 伏笔缺少预期回收位置 | 根据剧情推断，标记为 `待规划` |

### 1.7 章节状态检查
| 检查项 | 修复方式 |
|--------|----------|
| 章节文件缺少 SUMERU_STATUS 标记 | 扫描章节内容推断状态，添加标记 |
| status.json 与实际章节不一致 | 以实际章节为准，更新 status.json |
| 章节命名不规范| 提示用户手动重命启|

### 1.8 接续文件检查（v1.3.0 新增）
> **目的**：检查 `sumeru-worldbuilder` 恢复所需的前置文件是否齐全。
> **范围**：仅完整迁移模式执行；`仅检查` 模式也执行此段以输出诊断报告。
> **详细处理规则**：见「第十一、接续协议」。

| 检查项 | 模式 | 缺失时 |
|--------|------|--------|
| `.sumeru/creative-anchors.md` | 全部 | 进入 H1：从 plan.md + outline.md 推断 5-7 个锚点，标记 `pending` |
| `.sumeru/intro.md` | 全部 | 进入 H2：推断生成 300-500 字简介，标记 `pending` |
| `.sumeru/status.json.migrationHandoff` | 全部 | 进入 H3：写入 handoff 字段 |
| `.sumeru/context-packs/` | long/full | 进入 H4：初始化空目录 |
| `.sumeru/continuity/consistency-rules.json` | long/full | 进入 H5：从章节 `SUMERU_STATUS.state_diff` 合并重建 |
| `chapters/*.md` 中 `SUMERU_STATUS` 标记 | 全部 | 进入 H6：按内容/mtime 推断状态后补写 |
| `outlines/chapters.json` 字段完整性 | 全部 | 已在 1.4 处理；接续阶段不再重复 |
| `characters/*.md` 字段完整性 | 全部 | 已在 1.5 处理；接续阶段不再重复 |

**与 1.1-1.7 的区别**：
- 1.1-1.7 解决"文件是否齐全 / 字段是否完整"——属于**文件层**整顿
- 1.8 解决"恢复所需文件是否就绪"——属于**流程层**接续
- 1.8 的处理全部进入第五阶段「接续准备」执行，不阻塞第三阶段「执行迁移」

---

## 二、迁移流程
```
用户调用 /sumeru-migrate
    │
    ├─[第一阶段：项目扫描]
    │   ├─ 扫描目录结构
    │   ├─ 识别旧路径
    │   ├─ 检查配置文件
    │   └─ 检查章节任务卡字段
    │
    ├─[第二阶段：生成迁移计划]
    │   ├─ 列出需要修复的项目
    │   ├─ 按优先级排序
    │   └─ 询问用户确认
    │
    ├─[第三阶段：执行迁移]
    │   ├─ 迁移旧路径
    │   ├─ 补齐配置文件
    │   ├─ 补齐目录结构
    │   ├─ 补齐章节任务卡字段
    │   └─ 生成人物卡
    │
    ├─[第四阶段：生成报告]
    │   ├─ 迁移报告
    │   ├─ 更新 status.json
    │   └─ 记录 changelog
    │
    └─[第五阶段：接续准备] ⭐ v1.3.0 新增
        ├─ 补做 creative-anchors.md（H1）
        ├─ 补做 intro.md（H2）
        ├─ 写入 migrationHandoff 字段（H3）
        ├─ 初始化 context-packs/（H4，仅 long/full）
        ├─ 重建 consistency-rules.json（H5，仅 long/full）
        └─ 补全章节 SUMERU_STATUS 标记（H6）
        → 详见「第十一、接续协议」
```

**模式区别：**
- **仅检查 / 仅迁移路径 / 补齐配置 / 补齐人物卡**：执行到第三阶段相应子任务即结束，**不进入第五阶段**
- **完整迁移**（无子参数）：必须执行全五阶段；第五阶段任意子步骤失败时，整体标记为 `partial`，详见 11.7

---

## 三、project.json 推断规则

当`.sumeru/project.json` 不存在时，根据已有文件推断：

| 推断来源 | 推断字段 |
|----------|----------|
| `plan.md` 标题 | `title` |
| `plan.md` 类型标签 | `genre` |
| `plan.md` 受众定位 | `audience` |
| `plan.md` 目标平台 | `targetPlatform` |
| `outline.md` 分卷数| `plannedChapters` |
| `chapters/` 已有文件 | `currentStage` |
| 章节平均字数 | `chapterWordRange` |

**推断不出的字段*：使用默认值，标记不`pending`。
---

## 四、status.json 推断规则

当`.sumeru/status.json` 不存在时，根据已有文件推断：

| 推断来源 | 推断逻辑 |
|----------|----------|
| `chapters/` 文件数量 | 已完成章节数 |
| 章节首行 SUMERU_STATUS | 章节状态（drafted/polished/finalized：|
| `.sumeru/reviews/` 是否存在 | 是否经过审查 |
| `publish/` 是否存在 | 是否已导准|

---

## 五、旧路径迁移详细规则

### 5.1 chapter-outlines.json →chapters.json

```javascript
// 迁移逻辑
1. 读取 .sumeru/outline/chapter-outlines.json
2. 解析每个章节的基本信息（chapter, title, purpose, events：3. 缺少的必填字段标记为 "待补关
4. 写入 outlines/chapters.json
5. 备份旧文件到 .sumeru/backup/
```

### 5.2 issues/index.json →issues.md

```markdown
# 迁移逻辑
1. 读取 .sumeru/issues/index.json
2. 按严重程度分类3. 转换不Markdown 格式
4. 写入 .sumeru/issues.md
5. 备份旧文件到 .sumeru/backup/
```

### 5.3 docs/ →plan.md

```markdown
# 迁移逻辑
1. 读取 docs/requirements.md（需求）
2. 读取 docs/glossary.md（术语）
3. 读取 docs/style-guide.md（风格）
4. 合并到plan.md 对应章节
5. 备份旧文件到 .sumeru/backup/
```

---

## 六、人物卡生成规则

件`plan.md` 和`outline.md` 提取人物信息：
### 提取来源
1. `plan.md` 人物设定部分
2. `outline.md` 主要人物列表
3. `outline.md` 人物关系描述
4. 已有章节中的人物描写

### 生成格式

```markdown
# {人物名}

## 基础信息
- **姓名**：{从大纲提取}
- **年龄**：{从大纲提取或推断}
- **身份**：{从大纲提取}
- **外貌特征**：{从章节描写提取，或标认待补关}

## 性格画像
- **核心性格**：{从大纲提取}
- **说话风格**：{从章节对话提取，或标认待补关}
- **行为习惯**：{从章节描写提取，或标认待补关}
- **内在矛盾**：{从大纲推断，或标认待补关}

## 人物弧光
- **起点状态*：{从大纲提取}
- **关键转折**：{从大纲提取}
- **终点状态*：{从大纲提取}

## 核心驱动功- **核心欲望**：{从大纲提取}
- **核心恐惧**：{从大纲推断}

## 人物关系
| 对象 | 关系 | 当前状态|
|------|------|----------|
| {从大纲提取} | {从大纲提取} | {从大纲提取} |

## 战力/能力
- **能力等级**：{从大纲提取或推断}
- **特殊技能*：{从大纲提取}

## 人物标签
`#{类型}` `#{单阶段}`
```

---

## 七、迁移报告格式
```markdown
# 项目迁移报告

## 迁移概要
- **迁移时间**：{timestamp}
- **项目名称**：{title}
- **迁移模式**：{完整迁移/仅检查仅迁移路径}

## 检查结果
### 项目配置
| 项目 | 状态| 说明 |
|------|------|------|
| project.json | ✅已存在/ 🔧 已生成/ ✗生成失败 | {说明} |
| status.json | ✅已存在/ 🔧 已生成| {说明} |

### 目录结构
| 目录 | 状态|
|------|------|
| chapters/ | ✅已存在/ 🔧 已创建|
| characters/ | ✅已存在/ 🔧 已创建|
| outlines/ | ✅已存在/ 🔧 已创建|

### 旧路径迁移| 旧路径| 新路径| 状态|
|--------|--------|------|
| .sumeru/outline/chapter-outlines.json | outlines/chapters.json | ✅已迁移/ ⚠️ 需手动处理 |

### 章节任务单| 章节 | 缺失字段 | 状态|
|------|----------|------|
| 001 | 旧| ✅完整 |
| 002 | openingHook, freshnessHook | 🔧 已补关/ ⚠️ 待补关|

### 人物卡| 人物 | 状态|
|------|------|
| 主角 | ✅已生成|
| 反派 | ⚠️ 待补充详情|

### 接续准备（v1.3.0 新增）
| 步骤 | 文件 | 状态 | 备注 |
|------|------|------|------|
| H1 anchor | `.sumeru/creative-anchors.md` | ✅已推断 / ⏭️skipped / ❌失败 | {n} 个锚点,全部 `pending` |
| H2 intro | `.sumeru/intro.md` | ✅已推断 / ⏭️skipped / ❌失败 | 字数 {n} |
| H3 handoff | `status.json.migrationHandoff` | ✅已写入 / ❌失败 | 写入 `recommendedNext` |
| H4 context-packs | `.sumeru/context-packs/` | ✅已初始化 / ⏭️非 long/full / ❌失败 | — |
| H5 continuity | `.sumeru/continuity/consistency-rules.json` | ✅已重建 / ⏭️非 long/full / ❌失败 | 合并 {n} 章 state_diff |
| H6 chapter status | `chapters/*.md` 标记补全 | ✅全部已补 / ⚠️部分已补 / ❌失败 | 补 {a} / 共 {b} |

**整体接续状态**：`ready`（可恢复） / `partial`（部分完成，需用户介入） / `failed`（未完成接续）

## 待办事项
- [ ] {需要用户手动处理的事项}

## 续作建议（v1.3.0 新增）⭐

> **完整迁移模式必出本段**；`仅检查` / `仅迁移路径` / `补齐配置` / `补齐人物卡` 模式可省略。

### ✅ 项目已就绪（ready 状态时）

你的项目已完成迁移，可使用新技能继续创作。

**第一步（推荐）**：校对推断的简介
```bash
cat .sumeru/intro.md      # 校对
# 不满意直接编辑，下次 finalize 会使用新版本
```

**第二步（推荐）**：确认创意锚点
```bash
/sumeru-worldbuilder 恢复上次创作
# 系统会按 migrationHandoff 字段：
#   - 跳过 topic / outline 阶段
#   - 进入"锚点确认"流程（pending 锚点逐条确认）
#   - 确认后自动进入 write 续作
```

**第三步**：续作
- 续写："续写第N章"
- 重写："重写第N章"
- 全审："审查全部"
- 润色："润色第X-Y章"

### ⚠️ 项目部分就绪（partial 状态时）

迁移过程中部分接续步骤失败，需用户介入：

| 失败步骤 | 影响 | 用户处理 |
|----------|------|----------|
| {H1-H6 中失败的项} | {对应影响描述} | {具体操作} |

**最小恢复命令**：
```bash
/sumeru-worldbuilder 恢复上次创作
# 恢复时会检测到 partial 状态，逐项提示用户补做
```

### ❌ 项目未就绪（failed 状态时）

接续协议关键步骤失败，项目不可直接恢复。建议：
1. 检查 `.sumeru/migration.json` 中 `errors` 字段
2. 手动补做失败步骤
3. 重新运行 `/sumeru-migrate` 单独补做

### 当前项目快照
| 维度 | 值 |
|------|-----|
| 已完成章节 | {n} / {plannedChapters} |
| 字段补齐 | {a} / {b} 章 |
| 锚点状态 | {pending / confirmed / skipped} |
| 简介状态 | {pending / confirmed / skipped} |
| 下一可写章节 | {next_chapter} |
| 接续状态 | {ready / partial / failed} |
```

---

## 八、数据持久化

**用户可见输出**：- `migration-report.md`：迁移报命
**中间数据**：- `.sumeru/backup/`：旧文件备份
- `.sumeru/migration.json`：迁移记当
---

## 九、与其他 Skill 配合

- **前置**：无（可直接调用：- **后续**：迁移完成后可继续使生`sumeru-worldbuilder` 恢复创作，或使用其他 Skill 继续

---

## 十、独立调用说明
1. 定位项目根目录2. 执行项目扫描
3. 生成迁移计划
4. 询问用户确认
5. 执行迁移
6. 生成报告
7. 更新 status.json 和changelog

---

## 十一、接续协议（Handoff Protocol）

> **目标**：确保 `sumeru-migrate` 完成后，项目处于"可被 `sumeru-worldbuilder` 恢复"的就绪状态。
> **适用版本**：v1.3.0 起。
>
> **与 v1.2 的区别**：v1.2 仅完成"文件规整"即结束；v1.3 必须额外完成"接续准备"（补做 anchor / intro / handoff 标记）才算完成迁移。

### 11.1 为什么需要接续协议

老/不完整项目迁移后存在三个隐藏缺口，必须在迁移阶段补齐，否则 `worldbuilder 恢复上次创作` 会失准：

1. **缺失 `creative-anchors.md`**（1.2.0 新增阶段）：写作子 Agent 拿不到锚点，章节一致性退化。
2. **缺失 `intro.md`**（1.2.0 升级为必填）：finalize / publish 阶段可能跳过简介注入。
3. **缺失 `migrationHandoff` 标记**：`worldbuilder` 无法判断"项目是否经过 migrate"，会按全新项目初始化导致覆盖风险。

### 11.2 接续检查清单（强制执行）

完整迁移（`/sumeru-migrate` 不带子参数）必须在「生成报告」之后依次执行以下步骤，缺一不可：

| 步骤 | 检查项 | 缺失时的处理 |
|------|--------|--------------|
| **H1** | `.sumeru/creative-anchors.md` 是否存在 | 从 `plan.md` + `outline.md` 推断 5-7 个候选锚点，写入文件，全部标记 `pending`（待用户确认） |
| **H2** | `.sumeru/intro.md` 是否存在 | 从 `plan.md` 提取标题/受众/主角名，从 `outline.md` 提取主线冲突，生成 300-500 字简介，标记 `pending` |
| **H3** | `.sumeru/status.json` 是否含 `migrationHandoff` 字段 | 写入 `{version, migratedAt, fromVersion, recommendedNext}` |
| **H4** | `.sumeru/context-packs/` 是否存在（仅 long/full 模式） | 按 `sumeru-rules` 第七部分 Schema 初始化空目录 |
| **H5** | `.sumeru/continuity/consistency-rules.json` 是否存在（仅 long/full 模式） | 扫描所有章节 `SUMERU_STATUS` 的 `state_diff` 合并生成 |
| **H6** | `chapters/` 现有文件是否含 `SUMERU_STATUS` 标记 | 旧章节无标记 → 推断状态（按内容关键词 / 文件 mtime / 章节号）后补写 |

### 11.3 anchor 补做规则（H1 详细）

`creative-anchors.md` 是 1.2.0 新增的不可违背创意基准。老项目没有这个文件时，**不能跳过、不能直接进入 write**，必须按以下规则推断：

**推断来源**：
- `plan.md` 的"核心设定"、"金手指"、"核心冲突"段
- `outline.md` 的"分卷大纲"、"主线"、"人物设定"段
- 已有章节（`chapters/*.md`）的标题、首段、对话片段

**锚点类型**（与世界 builder 第 158-188 行锚点定义保持一致）：

| 锚点类型 | 推断策略 |
|----------|----------|
| 核心反差 | 从 plan.md "金手指" / "主角设定" 提取 |
| 情感锚 | 从 plan.md "核心冲突" / outline.md "主线" 提取 |
| 设定钩子 | 从 plan.md "世界观" 段提取最独特设定 |
| 关系张力 | 从 plan.md / outline.md 人物关系表提取 |
| 价值观冲突 | 从 plan.md "主题" 段提取 |

**输出格式**（与 `sumeru-worldbuilder` 一致）：

```markdown
# 创意锚点（Creative Anchors）

> 状态：⚠️ **pending**（迁移推断，待用户确认）
> 生成时间：{timestamp}
> 推断来源：plan.md, outline.md, chapters/*.md

| # | 类型 | 锚点 | 来源 | 状态 |
|---|------|------|------|------|
| 1 | 核心反差 | {推断的锚点} | plan.md §核心设定 | pending |
| 2 | 情感锚 | {推断的锚点} | outline.md §主线 | pending |
| 3 | 设定钩子 | {推断的锚点} | plan.md §世界观 | pending |
| ... | | | | |

## 确认提示
请用 `/sumeru-worldbuilder {原题材} 锚点确认` 逐条确认、修改或新增，确认后状态从 `pending` 改为 `confirmed` / `user_modified` / `user_added`。
```

### 11.4 intro.md 补做规则（H2 详细）

**生成模板**：

```markdown
# {作品名}

> 状态：⚠️ pending（迁移推断，待用户校对）
> 字数：{实际字数}（建议 300-500 字）

## 基本信息
- **类型**：{从 plan.md genre 字段}
- **受众**：{从 plan.md audience 字段}
- **目标平台**：{从 plan.md targetPlatform 字段}

## 简介正文
{从 outline.md 主线冲突 + plan.md 困境/转折/冲突/悬念 四要素生成，300-500 字}

## 平台标签
{按 plan.md 关键词映射到 4+ 平台标签}
```

**质量门禁**：
- 字数 300-500（短篇可放宽至 200-300）
- 必含四要素：困境 → 转折 → 冲突 → 悬念
- 至少 4 个平台标签

### 11.5 migrationHandoff 字段格式（H3 详细）

`.sumeru/status.json` 顶层追加：

```json
{
  "migrationHandoff": {
    "version": "1.3.0",
    "migratedAt": "2026-06-05T12:00:00Z",
    "fromVersion": "1.0.0",
    "migratedBy": "sumeru-migrate",
    "anchorStatus": "pending",
    "introStatus": "pending",
    "continuityRebuilt": true,
    "recommendedNext": "/sumeru-worldbuilder 恢复上次创作"
  }
}
```

`worldbuilder 恢复` 检测到 `migrationHandoff` 字段时：
- 跳过 topic / outline 阶段（已完成）
- 跳到 intro 校对（如果 anchorStatus / introStatus 为 pending）
- 然后到 anchor 确认（`pending` 锚点逐条确认）
- 最后到当前实际章节续作

### 11.6 续作建议输出格式

迁移报告末尾追加"续作建议"段（**完整迁移必出，仅检查/仅迁移路径模式可省**）：

```markdown
## 续作建议（Next Steps）

### ✅ 项目已就绪

你的项目已完成迁移，可使用新技能继续创作。

### 第一步：校对简介（可选）
```bash
# 校对推断生成的简介
cat .sumeru/intro.md
# 满意 → 无需操作
# 需修改 → 直接编辑文件，下次 finalize 会使用新版本
```

### 第二步：确认创意锚点（推荐）
```bash
/sumeru-worldbuilder 恢复上次创作
# → 系统会自动进入"锚点确认"流程
# → 逐条确认 pending 锚点
# → 确认后进入续作阶段
```

### 第三步：继续创作
锚点确认后系统自动进入 write 阶段。续作规则：
- 续写：直接说"续写第N章"
- 重写某章："重写第N章"
- 全书审查："审查全部"
- 润色："润色第X-Y章"

### 当前项目快照
| 维度 | 值 |
|------|-----|
| 已完成章节 | {n} / {plannedChapters} |
| 章节状态 | {按状态分布} |
| 字段补齐 | {补齐章节数} / {总章节数} |
| 锚点状态 | pending（待确认） |
| 简介状态 | pending（待校对） |
| 下一可写章节 | {下一个 planned 章节号} |
```

### 11.7 失败处理

接续协议任意一步失败的处理：

| 失败步骤 | 处理 |
|----------|------|
| H1 anchor 推断失败（无 plan.md / outline.md） | 跳过 anchor 写入，但 `anchorStatus` 标记为 `skipped`；worldbuilder 恢复时提示用户"需手动建立锚点" |
| H2 intro 推断失败 | 跳过 intro 写入，标记 `skipped`；finalize 阶段检测到无 intro 时给出警告 |
| H3 handoff 字段写入失败 | 整个迁移标记 `partial`；worldbuilder 不会自动接管，需用户手动确认状态 |
| H5 continuity 重建失败（如章节无 SUMERU_STATUS） | 跳过，标记 `skipped`；review 阶段重建 |
| H6 旧章节无状态标记 | 按 H6 规则推断；推断失败 → 标记 `unknown`，worldbuilder 恢复时暂停询问用户 |

### 11.8 与 worldbuilder 的接力协议

`/sumeru-worldbuilder 恢复上次创作` 检测迁移 handoff 的逻辑：

```
1. 读取 .sumeru/status.json
2. 检查 migrationHandoff 字段
3. 如果存在：
   a. if anchorStatus == "pending" → 跳到 anchor 确认
   b. elif introStatus == "pending" → 跳到 intro 校对
   c. else → 跳到当前 actualStage
4. 如果不存在：
   a. 检查 .sumeru/migration.json（migrate 旧版产物）
   b. 如果存在 → 提示用户"建议先运行 /sumeru-migrate 完成接续协议"
   c. 如果不存在 → 按全新项目处理（topic → outline → ...）
```

### 11.9 状态字段语义对照

为避免 `migrationHandoff` 与 `status.json` 现有字段冲突，新增字段**只增不改**：

| 字段 | 归属 | 语义 |
|------|------|------|
| `currentStage` | 现有 | 项目主流程阶段（init/topic/outline/...） |
| `chapterStatus.<n>` | 现有 | 单章状态（drafted/polished/finalized） |
| `migrationHandoff` | **新增** | 迁移交接信息（不影响 currentStage 流转） |

worldbuilder 读 `currentStage` 决定主流程，读 `migrationHandoff.anchorStatus` 决定是否在 anchor 阶段暂停等待确认。两者正交。
