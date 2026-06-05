# Changelog

## 1.3.2 (2026-06-05)

### 质量优化：OCR 错别字全面校对 + scripts-lib 死代码清理

**改动**：

- **A. OCR 错别字全面校对**（30+ 处）
  - `sumeru-topic/SKILL.md`：**整文件重写**（94 行）。修复 20+ 处 OCR 错字与缺失换行，包括：`调生→调用`、`提参→提取`、`废查/废片→废柴`、`执必→执念`、`设实→设定`、`驱功→驱动`、`情感键→情感锚`、`金手持→金手指`、`矛目→矛盾`、`名场面种字→名场面种子`、`价值冲窗→价值冲突`、`启生→启用`、`闭嘉→闭嘴`、`底约→底线`、`稀里遗忘→悄然遗忘`、`调试生→调试用`、`为师父复件→为师父复仇`、`本之的→本作品的`、`父Agent件→父 Agent 从`、`更文→更新`、`项目初始化协认→项目初始化协议`、`缺小→缺失`、`判文→判断`、`写出→写入`等
  - `sumeru-worldbuilder/SKILL.md`：**整文件重写**（236 行）。修复 ~30 处 OCR 错字与缺失换行，包括：`调生→调用`（6+ 处）、`提参→提取`、`废查/废片→废柴`、`执必→执念`、`设实→设定`、`驱功→驱动`、`情感键→情感锚`、`金手持→金手指`、`矛目→矛盾`、`名场面种字→名场面种子`、`价值冲窗→价值冲突`、`启生→启用`、`闭嘉→闭嘴`、`回到天前→回到前一天`、`底约→底线`、`稀里遗忘→悄然遗忘`、`调试生→调试用`、`为师父复件→为师父复仇`、`冷幽默暗黑童话意→冷幽默暗黑童话调`、`本之的→本作品的`、`反实→反审`、`写关→写入`、`判文→判断`、`缺小→缺失`、`更文→更新`、`章以不→章以上`、`总结：*→总结：**`、`写作不..→写作中...`、`交互式需求引对→交互式需求引导`、`节好爽文→快节奏爽文`、`❤→✗` 等
  - `sumeru-migrate/SKILL.md`：修复 2 处（`不一自→不一致`、`更文→更新`，共 §97 §110）
  - `sumeru-outline/SKILL.md`：修复 8 处（`差异化锚点*→：`、`起点状态*→：`、`终点状态*→：`、`核心驱动力- →核心驱动力 + 换行`、`本么→本书`、`述年→近年`、`黑衣人）→黑衣人？`、`锚点检查*→：`、`金手指是否有代价/限制（不能无敌））→金手指是否有代价/限制（不能无敌）`）
  - `sumeru-rules/SKILL.md`：修复 5 处（`金手指变作→金手指变式`、`状态更文→状态更新`、`不碰状态文从→不碰状态文件`、`执行并回写*→执行并回写：`、`待定项判文→待定项判断`、`待定项处理建设→待定项处理建议`）
  - 全部 skill frontmatter 未动
  - 保留所有 v1.3.0 / v1.3.1 已加入的协议（H1-H6、targetChapter、protectedTag、风格样本自动分析等）

- **B. scripts-lib 死代码清理**
  - 验证：grep 全 9 个 skill，确认 `scripts-lib/sumeru_utils.py` 0 引用、`scripts-lib/resume_check.py` 0 引用
  - 操作：删除 `skills/scripts-lib/` 整个目录（2 个 Python 文件）
  - 不影响 CLAUDE.md（CLAUDE.md 引用为概念性提及，无具体路径）

- 不破坏项：
  - 9 个 skill 的协议层（接续协议、targetChapter、continuity）已就位
  - Python 脚本（`continuity-check.py` / `foreshadowing-tracker.py` / 4 个 finalize 脚本）均未动
  - sumeru-worldbuilder 的「接续协议」节、sumeru-topic 的「与 worldbuilder 关系」节（m0118）均保留
  - medium/standard 模式补创 continuity 的协议（m0088）保留

**遗留**（建议后续清理）：
- sumeru-rules 内部仍有 ~5 处 typo（行 165/178 等"备份则→备份至"、"返因→返回"、"汇态→汇总"等），因属长期 canonical 文件，未在本轮彻底处理
- sumeru-outline 头部 113-130 行（人物卡模板）仍有几处 OCR 拼接错（如 "）- **年龄**）"），影响小

### 元数据同步：README.md 同步到 v1.3.2

**改动**：
- 顶部加版本状态行：`v1.3.2 · 2026-06-05 · 完整变更: CHANGELOG.md`
- 加 `🆕 最新更新` 段（v1.3.0 / v1.3.1 / v1.3.2 三条）
- "8 个独立 Skill 模块" → **9 个**（含 sumeru-migrate）
- 核心特性补"项目接续"条（H1-H6 接续协议）
- 定位描述补"迁移"到流程：迁移 → 选题 → 大纲 → 写作 → 审稿 → 润色 → 导出
- 最后更新日期 2026-05-29 → 2026-06-05
- sumeru-migrate §7 描述补 v1.3.0 接续协议说明
- 子模式注释补"含接续协议"提示

## 1.3.1 (2026-06-05)

### 新增：剧情一致性 + 文笔丰富优化包（用户硬约束）

> **背景**：用户提出"在保证剧情一致性和文笔丰富的基础上,有没有什么优化方案"。经审计发现,代码库中 80% 优化目标（`continuity-check.py` / `foreshadowing-tracker.py` / `consistency-rules.json` / `style-samples/` 模板）已存在,主要问题是**接缝未连**。
>
> 本次为接缝优化,非新建。**无新增 Python 脚本**,复用 `sumeru-review/scripts/continuity-check.py`（450 行）与 `foreshadowing-tracker.py`（211 行）。

**改动**：

- `sumeru-worldbuilder` (v1.2.1 → v1.2.2)
  - **模式初始化表**：medium/standard 模式补创 `.sumeru/continuity/consistency-rules.json`（空 schema）；long/full 行移除 `continuity/`
  - **模式升级协议**：medium → long 升级清单移除 `continuity/`（已在 medium 阶段创建）
  - **创意锚点 附加字段**：新增 `targetChapter`（名场面种子,可选）/ `protectedTag`（全部,可选）字段定义

- `sumeru-write` (v1.2.0 → v1.2.1)
  - **剧情统一门禁 写前步骤**：新增 2 条
    - 伏笔活跃度预检：调用 `foreshadowing-tracker.py --quiet` 把逾期伏笔注入 `shared-write.md`
    - 锚点临近检查：找出 `targetChapter` 距当前章 ≤ 3 的名场面种子,提示"请在本章或近期兑现 XX"
  - **剧情统一门禁 写后步骤**：增量更新逻辑
    - 解析 `SUMERU_STATUS.plot_update.foreshadowing`,同步写 `consistency-rules.json` 的 `last_mentioned` + `mentionCount`
    - 可选调用 `continuity-check.py --quiet`,critical 冲突立即报出

- `sumeru-outline` (v1.2.0 → v1.2.1)
  - **风格样本自动分析**：检测到 `style-samples/user-sample-*.md` 时,父 Agent 按 6 维度分析并填充 `user-style.md` 的"待分析"占位；后续作为 context pack 固定组成部分

**不破坏项**：
- `user-style.md` 首次生成后保留手动修改,后续不覆盖
- 现有 `continuity-check.py` / `foreshadowing-tracker.py` 无需修改
- 现有 `consistency-rules.json` schema 不变（仅使用 `last_mentioned` 字段,该字段已在 `sumeru-rules/SKILL.md` §consistency-rules.json 格式 定义）
- 用户未提供样本时,user-style.md 保持"待分析"状态,以 `plan.md.creativeStrategy` 兜底

### 同步：SKILL.md frontmatter 版本号（2026-06-05）

本次同步将以下 skill 的 frontmatter `version` 字段与 CHANGELOG 对齐：

- `sumeru-worldbuilder`：1.2.0 → **1.2.2**（handoff v1.2.1 + continuity v1.2.2）
- `sumeru-rules`：1.2.0 → **1.2.1**（handoff 字段索引）
- `sumeru-write`：1.2.0 → **1.2.1**（continuity 增量 + 写前预检）
- `sumeru-outline`：1.2.0 → **1.2.1**（风格样本自动分析）
- `sumeru-migrate`：1.2.0 → **1.3.0**（已在 v1.3.0 release 同步过）
- 其余 4 个 skill（topic / review / polish / finalize）保持 1.2.0，本次未做改动

注：本仓库采用"每 skill 独立版本号" + "CHANGELOG 顶层 release 标签"双重版本管理。各 skill `version` 反映该 skill 自身的演进，CHANGELOG 顶层 vX.Y.Z 反映一次发布的整体编号。

## 1.3.0 (2026-06-05)

### 新增：sumeru-migrate 接续协议（Handoff Protocol）

**问题**：v1.2.0 起 `sumeru-worldbuilder` 增加了 `anchor` 阶段（创意锚点）和强化了 `intro.md` 必填项，但 `sumeru-migrate` 仅完成"文件规整"就结束，迁移后的项目进入 `worldbuilder 恢复` 时会因缺失 `creative-anchors.md` / `intro.md` / `migrationHandoff` 标记而失准。

**改动**：

- `sumeru-migrate` (v1.2.0 → v1.3.0)
  - 新增「第十一、接续协议」章节：
    - H1: 推断补做 `.sumeru/creative-anchors.md`（从 plan.md + outline.md 推断 5-7 个锚点，全部标记 `inferred`）
    - H2: 推断补做 `.sumeru/intro.md`（从 plan.md 提取四要素，生成 300-500 字简介）
    - H3: 写入 `.sumeru/status.json.migrationHandoff` 字段（version / migratedAt / fromVersion / anchorStatus / introStatus / recommendedNext）
    - H4: 初始化 `.sumeru/context-packs/`（仅 long/full）
    - H5: 重建 `.sumeru/continuity/consistency-rules.json`（仅 long/full）
    - H6: 补全 `chapters/*.md` 缺失的 `SUMERU_STATUS` 标记
  - 迁移流程增加「第五阶段：接续准备」
  - 检查清单增加 1.8「接续文件检查」
  - 迁移报告增加「续作建议」段，输出明确的 `/sumeru-worldbuilder 恢复上次创作` 命令
  - 完整迁移模式必出接续协议；`仅检查` / `仅迁移路径` / `补齐配置` / `补齐人物卡` 模式可省略
  - 接续状态分级：`ready` / `partial` / `failed`，对应不同的恢复提示

- 关联：sumeru-worldbuilder 后续应增加 `migrationHandoff` 字段检测逻辑
  - 跳过 topic / outline 阶段（已完成）
  - 按 anchorStatus / introStatus 决定是否进入确认流程
  - 详见 migrate/SKILL.md §11.8「与 worldbuilder 的接力协议」

### 新增：sumeru-worldbuilder 迁移接续对端实现

**改动**：

- `sumeru-worldbuilder` (v1.2.0 → v1.2.1)
  - 新增「项目恢复与迁移接续协议」章节：
    - 入口检测三态：`migrationHandoff` 存在 / 仅 `migration.json` 存在 / 都没有
    - 接续模式字段处理细则：`anchorStatus` / `introStatus` 各 4 个取值对应的 worldbuilder 行为
    - `recommendedNext` 字段：默认 `/sumeru-worldbuilder 恢复上次创作`，其他值原样输出不替用户决定
    - 字段正交性：`migrationHandoff` 只增不改，不参与 `currentStage` 流转
    - 审计：每次接续动作追加一条到 `.sumeru/changelog.md`
  - 与 `sumeru-migrate` v1.3.0 形成闭环

- `sumeru-rules` (v1.2.0 → v1.2.1)
  - 状态机章节追加「状态字段语义对照」表：
    - `currentStage` / `chapterStatus.<n>` / `migrationHandoff` 三字段
    - 标注 `migrationHandoff` 为「只增不改」字段，指向 migrate §11.5 和 worldbuilder §项目恢复与迁移接续协议

## 1.2.0 (2026-05-29)

### 优化：架构精简与功能增强

**消耗优化**：

- `sumeru-rules` 辅助文件合并
  - 将 6 个文件（SKILL.md, ARCHITECTURE.md, protocol.md, continuity.md, conventions.md, subagent-rules.md）合并为单个 SKILL.md + subagent-rules.md
  - 子Agent只需读取 subagent-rules.md (139行)，而非父Agent的完整规则

- 各技能 SKILL.md 精简
  - 移除重复的反AI写作规则（指向 subagent-rules.md）
  - 精简子Agent调用模板（提取通用部分）
  - 精简 Context Pack 生成规则（统一模板）

**功能增强**：

- 新增 `sumeru-migrate` 技能
  - 旧项目迁移与规整
  - 路径迁移、配置补齐、字段补全、人物卡生成
  - 支持"仅检查"、"仅迁移路径"、"补齐配置"、"补齐人物卡"等模式

- 反AI扫描统一
  - 将反AI句式扫描从 write 扩展到 polish 流程
  - 统一定义在 sumeru-rules 第十部分

- Context Pack 统一模板
  - 在 sumeru-rules 中定义通用模板
  - 各技能定义专用部分（write/review/polish/finalize）

- finalize 架构说明
  - 明确父Agent直接执行脚本的原因（确定性任务、性能、一致性、成本）
  - 清晰划分父Agent脚本预处理和子Agent待定项判断的职责

**版本更新**：
- 所有技能版本统一更新为 v1.2.0

## 1.0.0 (2026-05-16)

### 初始发布

基于 [xindoo/sumeru](https://github.com/xindoo/sumeru) 二次开发，适配 Claude Code、OpenCode 等 AI 编程工具。

**核心模块**：
- `sumeru-worldbuilder`：全流程编排器，统筹选题→大纲→写作→审查→润色→导出
- `sumeru-topic`：选题策划，市场分析+创意引擎+平台定向
- `sumeru-outline`：大纲设计，世界观+人设+剧情框架+章节任务卡
- `sumeru-write`：章节撰写，细纲驱动+反AI写作规则+人物真实感
- `sumeru-review`：逻辑审查，时间线+剧情+人物OOC+创意疲劳检测
- `sumeru-polish`：内容润色，文笔优化+副词清理+场景差异化
- `sumeru-finalize`：完稿校验，错别字+敏感词+多平台导出
- `sumeru-rules`：全局约束，子Agent并行规则+状态标记+Context Pack格式

**关键特性**：
- 三种篇幅模式：short/light (1-10章), medium/standard (10-50章), long/full (50章+)
- 子Agent并行创作，每个最多负责3章
- SUMERU_STATUS 状态标记，支持断点恢复
- 多平台导出：起点、番茄、晋江、纵横、17k

## 1.1.0 (2026-05-28)

### 修复：章节任务卡字段完整性断层

**问题**：outline 产出的 `chapters.json` 缺少 `purpose`、`events`、`acceptanceCriteria` 等必填字段，导致 write 子Agent收到空任务卡，正文质量依赖模型自由发挥。

**改动**：

- `sumeru-outline` (v1.0.0 → v1.1.0)
  - 新增"章节任务卡输出验证"质量门禁：生成后逐章检查 13 个必填字段，缺字段不标记 outline 完成
  - 项目化输出要求增加字段完整性说明

- `sumeru-write` (v1.0.0 → v1.1.0)
  - 新增"章节任务卡字段完整性检测与回退机制"：读取 `chapters.json` 后检查目标章节字段，缺字段时自动从 `outlines/chapter-XXX-YYY.md` 回退补充，仍缺失时警告用户
  - 输入优先级增加 batch outline 回退路径

- `sumeru-worldbuilder` (v1.0.0 → v1.1.0)
  - 项目初始化协议增加"模式与章节数交叉校验"：short(1-10章)、medium(10-50章)、long(50章+)，超出自动提示升级
  - outline 完成条件升级为要求字段完整性验证通过
  - 模式升级协议增加自动触发升级条件

### 更新方法

重新安装技能即可获取最新版本：

```bash
npx skills add wq1131173682/wqsumeru
# 或更新已安装技能
npx skills update wq1131173682/wqsumeru
```
