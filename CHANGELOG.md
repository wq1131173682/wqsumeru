# Changelog

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
