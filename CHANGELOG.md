# Changelog

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
