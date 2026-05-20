---
name: sumeru-outline
description: 小说大纲、世界观、人设设计与创意架构。用户要写小说大纲、设计主角/配角/反派、做世界观设定、搭剧情框架、分卷大纲、章节细纲、人物卡、爽点排布、反套路设计、惊喜反转、情绪曲线或梳理小说剧情时必须使用本技能。
type: skill
---

> ⚠️ **依赖技能**：本 Skill 依赖 `sumeru-rules` 中的全局约束。执行前请确保已加载。

> 📌 **输出级别**：默认 `quiet` 模式，只输出进度。详细规范见 `sumeru-rules` "输出级别规范"。

## 网文大纲设计

### 触发关键词
帮我写个小说大纲、设计主角人设、做世界观设定、搭小说剧情框架、写分卷细纲、给我设计小说人物、做个玄幻世界观、帮我梳理小说剧情、小说人物设定、写小说分章大纲、爽点排布规划、做小说人设卡、构建小说世界、小说大纲生成、写完整章节细纲、生成全本细纲、所有章节细纲

### 核心功能
1. 世界观设定：世界背景、力量体系、社会规则、地理设定
2. 人物设定：主角、配角、反派的人物画像、性格、成长线
3. 剧情框架：主线故事、支线剧情、关键节点、高潮安排
4. 分卷大纲：按卷划分剧情阶段，明确每卷核心冲突与目标
5. 爽点排布：规划关键爽点、转折点、悬念点的位置
6. **强制合规检查**：识别可能的真实人名/地名，避免侵权风险

### 独立调用自举
1. 定位项目根目录，读取或生成 `.sumeru/project.json`、`.sumeru/status.json`
2. 若已有 `plan.md`、`.sumeru/topic/options.json` 或旧版 `docs/requirements.md`，复用既有选题和需求
3. 若缺少 `plan.md`，先生成最小创意策略和创意库存
4. 大纲完成后生成或刷新 `outlines/chapters.json`；长篇项目同步拆分
5. 更新 `.sumeru/status.json`、`.sumeru/cache/` 相关摘要

### 按模式输出
| 模式 | 输出内容 |
|------|----------|
| `short/light` | `outline.md`，包含高概念、人物、三幕结构、核心反转、情绪曲线 |
| `medium/standard` | `plan.md`、`outline.md`、`outlines/chapters.json` |
| `long/full` | `plan.md`、`outline.md`、`outlines/chapters.json`，必要时拆分章节任务卡 |

### 项目化输出要求
- `plan.md`：需求、世界观、人物、风格、创意策略、术语合并维护
- `outline.md`：故事架构、主线、分卷规划、关键高潮、伏笔规划
- `outlines/chapters.json`：章节任务卡主文件（每章必须包含 `purpose`、`events`、`outputs`、`acceptanceCriteria`）

### 创意架构要求
- **高概念锁定**：选择主 pitch，写入 `plan.md`
- **类型混血控制**：说明主类型承诺和嫁接类型的边界
- **反套路策略**：列出本书最容易俗套的 5 个桥段，并给出替代写法
- **卷级惊喜**：每卷至少设计 1-3 个"意外但合理"的反转
- **情绪曲线**：规划每卷主导情绪和相邻章节情绪差异
- **角色主动性压力测试**：主角、反派、重要配角都必须有独立欲望和主动选择

### 合规约束规则
1. **人名约束**：禁止使用真实人名（历史人物、公众人物、知名IP角色名）
2. **地名约束**：禁止使用真实地名（国家名、城市名、山脉名等）
3. **自动检查**：发现疑似真实名称时自动提示并提供3个以上虚构替换方案

### 子Agent并行细纲生成
当章节数大于3章时，支持子Agent并行生成细纲。每个子Agent最多负责3章，按卷分配优先。

### 数据持久化
**用户可见输出**：
- `plan.md`、`outline.md`、`outlines/chapters.json`

**中间数据（`.sumeru/outline/`）**：
- 仅保存必要缓存；旧版 `world.json`、`characters.json`、`plot-outline.json`、`chapter-outlines.json` 只读兼容

### 与其他 Skill 配合
- **前置**：可读取 `sumeru-topic` 的 `options.json`
- **后续**：生成的数据可供 `sumeru-write`、`sumeru-review` 使用

### 全局约束引用
> 完整全局约束见 `sumeru-rules` 技能，核心要点如下：
> - **子Agent规则**：最多5个并行，每个最多3章
> - **职责边界**：子Agent只读 context pack，输出纯结果+状态标记
> - **状态标记**：输出首行必须包含 `<!-- SUMERU_STATUS: chapter=X, status=Y, ... -->`
> - **Context Pack**：控制在1500-3000中文字
