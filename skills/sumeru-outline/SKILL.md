---
name: sumeru-outline
description: 小说大纲设计：世界观构建、人物设定、剧情框架、分卷大纲、章节细纲。写小说大纲、设计人物、做世界观设定、搭剧情框架、分卷大纲、章节细纲、人物卡、爽点排布、伏笔管理时必须使用本技能。选题策划请调用 sumeru-topic。
version: 1.0.0
type: skill
user-invocable: true
---

> 依赖 `sumeru-rules`，默认 `quiet` 模式。

## 网文大纲设计

### 核心功能
1. **选题复用**：自动读取 `plan.md`、`.sumeru/topic/options.json` 中的选题成果（旧路径兼容见 `sumeru-rules protocol.md`）
2. **世界观设定**：世界背景、力量体系、社会规则、地理设定
3. **人物设定**：主角、配角、反派的人物画像、性格、成长线，同步写入 `characters/` 人物卡
4. **剧情框架**：主线故事、支线剧情、关键节点、高潮安排
5. **分卷大纲**：按卷划分剧情阶段，明确每卷核心冲突与目标
6. **爽点排布**：规划关键爽点、转折点、悬念点的位置
7. **伏笔管理表**：设计伏笔埋设、推进与回收计划
8. **强制合规检查**：识别可能的真实人名/地名，避免侵权风险

### 独立调用自举
1. 定位项目根目录，读取或生成 `.sumeru/project.json`、`.sumeru/status.json`
2. 若已有 `plan.md`、`.sumeru/topic/summary.json`，复用既有选题和需求（旧路径兼容见 `sumeru-rules protocol.md`）
3. 若缺少 `plan.md`，提示先执行 `sumeru-topic` 选题策划，或生成最小创意库存
4. 大纲完成后生成或刷新 `outlines/chapters.json`；长篇项目同步拆分
5. 同步生成 `characters/` 人物卡
6. 更新 `.sumeru/status.json`、`.sumeru/cache/` 相关摘要

### 按模式输出
| 模式 | 大纲输出 |
|------|----------|
| `short/light` | `outline.md`，包含高概念、人物、三幕结构、核心反转、情绪曲线 |
| `medium/standard` | `plan.md`、`outline.md`、`outlines/chapters.json`、`characters/` |
| `long/full` | `plan.md`、`outline.md`、`outlines/chapters.json`、`characters/`、`world.md`，必要时拆分章节任务卡 |

### 项目化输出要求
- `plan.md`：需求、世界观、人物、风格、创意策略、术语合并维护
- `outline.md`：故事架构、主线、分卷规划、关键高潮、伏笔管理表
- `outlines/chapters.json`：章节任务卡主文件（旧路径 `.sumeru/outline/chapter-outlines.json` 只读兼容，见 `sumeru-rules protocol.md`）。每章必须包含 `purpose`、`events`、`outputs`、`acceptanceCriteria`
- `characters/`：人物卡目录，每人物独立文件
- `world.md`：世界观手册（long/full 模式）

### 创意架构要求
- **高概念锁定**：选择主 pitch，写入 `plan.md`
- **类型混血控制**：说明主类型承诺和嫁接类型的边界
- **反套路策略**：列出本书最容易俗套的 5 个桥段，并给出替代写法
- **卷级惊喜**：每卷至少设计 1-3 个"意外但合理"的反转
- **情绪曲线**：规划每卷主导情绪和相邻章节情绪差异
- **角色主动性压力测试**：主角、反派、重要配角都必须有独立欲望和主动选择
- **伏笔管理表**：大纲阶段必须输出伏笔清单，写入 `outline.md`。每项伏笔包含：
  - `id` — 唯一编号（`F1`、`F2` ...）
  - `内容` — 伏笔的具体描述
  - `类型` — 设定伏笔 / 人物伏笔 / 道具伏笔 / 事件伏笔
  - `埋设位置` — 第几卷·第几章·场景
  - `预期回收位置` — 第几卷·第几章
  - `状态` — 已埋 / 待收 / 已收
  - `备注` — 可选，说明回收条件或替代方案
- **情绪节拍模板池与轮换**（新增）：每章 `emotionalBeat` 必须从模板池中按轮换规则选取，避免连续多章使用同一情绪走向

### 情绪节拍模板池

> **规则**：连续 3 章不得使用同一模板。卷首章优先用 B（递进型）或 D（双线型），卷尾章优先用 A（反转型）或 C（抑扬型）。

| 模板ID | 名称 | 情绪走向 | 适用场景 |
|--------|------|----------|----------|
| A | 反转型 | 期待 → 落空 → 意外 → 爽 | 反转章节、打脸、揭秘 |
| B | 递进型 | 平静 → 波动 → 升级 → 爆发 | 战斗、冲突升级、成长突破 |
| C | 抑扬型 | 低谷 → 挣扎 → 转机 → 希望 | 战败后重整、低谷反弹、日常后的危机 |
| D | 双线型 | A线紧张 + B线松弛 → 交汇 → 引爆 | 多线叙事、伏笔推进、平行场景 |
| E | 悬念型 | 异常 → 试探 → 揭示 → 新的未知 | 悬疑推进、世界观揭示、阴谋铺展 |
| F | 情绪型 | 抵触 → 触动 → 接纳 → 升温 | 人物关系变化、情感线推进 |
| G | 低谷型 | 压制 → 崩溃边缘 → 觉醒 → 反击 | 大挫折、绝境重生、战力觉醒 |

**分配策略**：
- 写作前由父Agent扫描前3章已用模板，排除重复选项
- 从剩余模板中按"场景最适合优先"原则选择，不强制随机
- 模板ID写入 `outlines/chapters.json` 每章任务卡的 `emotionalBeatTemplate` 字段
- `emotionalBeat` 的具体情绪词根据模板框架和本章情节细化

### 合规约束规则
1. **人名约束**：禁止使用真实人名（历史人物、公众人物、知名IP角色名）
2. **地名约束**：禁止使用真实地名（国家名、城市名、山脉名等）
3. **自动检查**：发现疑似真实名称时自动提示并提供3个以上虚构替换方案

### 子Agent并行细纲生成

> **并行规则**详见 `sumeru-rules SKILL.md` 第一节"子Agent并行处理规则"。

当章节数大于3章时，支持子Agent并行生成细纲。每个子Agent最多负责3章，按卷分配优先。

### 数据持久化
**用户可见输出**：
- `plan.md`、`outline.md`、`outlines/chapters.json`、`characters/`、`world.md`

**中间数据（`.sumeru/outline/`）**：
- 仅保存必要缓存；旧版 `world.json`、`characters.json`、`plot-outline.json`、`chapter-outlines.json` 只读兼容（旧路径兼容策略见 `sumeru-rules protocol.md`）

> 风格样本机制详见 `sumeru-rules subagent-rules.md`。大纲完成后父 Agent 可询问用户是否提供样本，不提供不影响后续。

_（小说简介生成已移至 `sumeru-worldbuilder`）_

### 与其他 Skill 配合
- **前置**：`sumeru-topic`（选题策划），可复用已有 `plan.md`
- **后续**：`.sumeru/intro.md` 可供 `sumeru-finalize` 在发布导出时复用简介；`sumeru-write` 可参考其中的传播句作为章节结尾钩子；`characters/` 和 `world.md` 供全部下游技能使用
