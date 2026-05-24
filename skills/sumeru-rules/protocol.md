---
name: sumeru-rules-protocol
description: Context Pack 格式、自举协议、项目 Schema、Skill 职责明细、修改边界、质量检查
type: skill
---

# 调用协议与配置

> 本文件是 `SKILL.md` 的拆分模块，所有 Skill 共同遵守。

---

## 一、Context Pack 格式

**为减少同批次内容重复，context pack 拆为 2 个文件：**

| 文件 | 命名规则 | 大小 | 是否共享 |
|------|----------|------|----------|
| 共享上下文 | `shared-{task}.md` | ~1500-2000 字 | 同批次所有子Agent共用 |
| 本组任务卡 | `cards-{范围}.md` | ~300-500 字 | 每子Agent独有 |

子Agent先读共享上下文，再读本组任务卡，两者合并作为完整 context。

### 共享上下文格式（`shared-{task}.md`）

```markdown
# Shared Context: write (batch 002)

## Project Brief (1-2行)
题材、平台、字数范围、整体风格。

## Current Volume (1-2行)
本卷目标、当前冲突、卷级反转、阶段情绪。

## Relevant Characters (仅本卷相关)
相关人物的当前状态、目标、关系、语言风格。

## Relevant World & Glossary (仅本卷会用到的)
地点、组织、功法、道具、禁用变体。

## Continuity State
上一章结尾、关键道具状态、未回收伏笔、时间线位置。

## Creative Strategy
创意目标、要避开的套路、情绪节拍变化、读者记忆点。

## Batch Summary (仅非第一批)
前N批实际摘要（≤500字）。

## Output Requirements
文件命名、状态更新需求（由父agent执行）。
```

### 本组任务卡格式（`cards-{范围}.md`）

```markdown
# Task Cards: 004-006

## Chapter Cards
### 第004章「标题」
- purpose: ...
- events: ...
- acceptanceCriteria: ...
- creativeGoal: ...
- emotionalBeat: 压抑→困惑→恍然→暗爽

### 第005章「标题」
...

## 本章执行提醒 (≤5条)
具体可执行的过程提醒，如"主角必须主动选择"、"第15段附近制造反转"。
```

### 具象标杆（polish 专属）

polish 的共享上下文中额外嵌入风格标杆：

```
【风格标杆】--打斗标杆(第003章)--原文/润色 --对话标杆(第005章)--原文/润色 --情绪标杆(第008章)--原文/润色
```

### 节省计算

同批次 5 个子Agent，原方案 vs 新方案：

| 方案 | 每Agent传输量 | 每批总传输量 | 节省 |
|------|--------------|-------------|------|
| 原方案（单文件） | 2400 字 × 1 文件 | 2400 × 5 = 12000 字 | - |
| 新方案（双文件） | 1800 字（共享）+ 400 字（卡片） | 1800 × 1 + 400 × 5 = 3800 字 | **68%** |

### 分层摘要缓存

共享上下文中嵌入可用缓存的键列表，子Agent可在输出中标记需要补充的缓存：

```
【可用缓存的键】：char:主角, char:反派, plotline:v1, plotline:v2, world:current, prev:actual, arc:001-003
```

---

## 二、独立调用自举协议

任何 Skill 单独启动时必须执行：

1. **定位项目**：从当前目录向上查找 `.sumeru/project.json` / `plan.md` / `outline.md` / `chapters/` / `outlines/`
2. **识别版本**：存在 `.sumeru/project.json` 按新协议，否则进入兼容模式
3. **最小初始化**：缺配置时根据已有文件生成最小配置
4. **补齐目录**：按需创建 `.sumeru/cache/` / `context-packs/` / `continuity/` / `issues.md`
5. **兼容输入**：旧版 `.sumeru/outline/chapter-outlines.json` 只读兼容
6. **刷新缓存**：相关 cache 缺失或过期时生成最小摘要
7. **生成 context pack**：缺 context pack 时生成临时 pack
8. **执行并回写**：更新 `.sumeru/status.json`、cache、issue 文件
9. **记录变更**：追加到 `.sumeru/changelog.md` 和 `.sumeru/decisions.md`

### Canonical 路径

| 类型 | 新写入路径 | 旧路径处理 |
|------|------------|------------|
| 项目配置 | `.sumeru/project.json`、`.sumeru/status.json` | 无 |
| 需求/设定/创意 | `plan.md` | `docs/*`、`ideas/*` 只读兼容 |
| 大纲/任务卡 | `outline.md`、`outlines/chapters.json` | `.sumeru/outline/chapter-outlines.json` 只读兼容 |
| 正文 | `chapters/` 或短篇 `story.md` | 无 |
| 人物卡 | `characters/` 目录 | 无 |
| 世界观 | `world.md` | 无 |
| 问题清单 | `.sumeru/issues.md` | `.sumeru/issues/index.json` 只读兼容 |
| 审查摘要 | `reviews/review-report.md` | 按需生成 |
| 发布产物 | `publish/` | 无 |

### 独立调用原则

- 不要求先运行 worldbuilder
- 能从现有文件推断的信息不重复询问
- 缺信息但不阻塞任务时用合理默认值
- 不因缓存/context pack 缺失而失败

---

## 三、项目配置 Schema

```json
{
  "schemaVersion": 1,
  "title": "未命名作品",
  "genre": "玄幻",
  "targetPlatform": "番茄",
  "audience": "男频",
  "plannedWords": 800000,
  "plannedChapters": 300,
  "chapterWordRange": [2000, 3000],
  "style": "快节奏爽文",
  "tone": "热血",
  "currentStage": "outline",
  "outputLevel": "quiet",
  "createdAt": "2026-05-16T00:00:00Z",
  "updatedAt": "2026-05-16T00:00:00Z"
}
```

**阶段状态：** `pending` / `in_progress` / `blocked` / `completed` / `skipped`

**章节状态：** `planned` / `drafted` / `reviewed` / `fixed` / `polished` / `finalized` / `exported`

修复后经反审验证通过进入 `fixed`；润色发现逻辑硬伤时触发反审验证。

---

## 四、各 Skill 子Agent职责明细

| Skill | 子Agent核心任务 | 子Agent输入 | 子Agent输出 | 父Agent后续处理 |
|-------|----------------|------------|------------|----------------|
| **sumeru-topic** | 生成选题方案 | context pack（题材方向+创意引擎） | 选题方案（pitch+类型混血+金手指变体+反套路策略） | 合并写入 `plan.md`、`.sumeru/topic/` |
| **sumeru-outline** | 生成章节细纲 | context pack（世界观+人物+分卷大纲+上下文关联） | 章节细纲 JSON/Markdown + 状态标记 | 合并校验→写入 outlines/chapters.json→刷新 cache |
| **sumeru-write** | 按任务卡写正文 | context pack（任务卡+上一章结尾+剧情事实基准+人物/道具/伏笔状态） | 纯正文 + 状态标记 | 剧情统一校验→写入 chapters/→备份→更新 status→刷新 continuity cache |
| **sumeru-review** | 按任务卡审查章节 | context pack（任务卡+正文+审查标准+consistency-rules） | 审查结论（问题列表+严重程度+证据+建议） | 合并问题写入 issues.md，按需生成 review report，制定 fix-plan |
| **sumeru-polish** | 按标准润色章节 | context pack（正文+style-brief+creative-brief+审查问题+具象标杆） | 润色后正文 + 状态标记 | 备份后直接写入最终正文，更新 status→polished |
| **sumeru-finalize** | 脚本预处理 + 待定项判断 | 脚本扫描结果（待定项列表，最多20个） | 待定项处理建议 | 汇总建议→最终校验→写入 publish/→build-manifest |

---

## 五、修改边界

- `sumeru-review` 直接修复错别字、轻微逻辑补丁、字数不足，不大量重写
- `sumeru-polish` 优化文笔/节奏/对话/爽点，不改变主线事实和角色关系
- `sumeru-finalize` 专注技术校验和发布格式，不承担剧情重构
- 下游 Skill 不直接调用上游；需返工时输出结构化计划
- 正文修改默认产出最终版，修改前保留最小备份

---

## 六、质量检查

执行任一 Skill 后检查：

1. 预期输出文件是否生成
2. `.sumeru/` 结构化数据与用户可见输出是否一致
3. 章节文件按三位编号排序，无缺章/重章
4. 修改型 Skill 是否生成备份和变更记录
5. 写作/重写/润色后是否通过 SUMERU_STATUS 与 continuity cache 校验
6. 发布导出是否剥离 SUMERU_STATUS 注释
