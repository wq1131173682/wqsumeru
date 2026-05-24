---
name: sumeru-rules
description: 须弥写作全局约束规则（入口）。子Agent规则 + 职责划分 + 状态标记格式。详细展开见同一目录下的 continuity.md / protocol.md / conventions.md。
type: skill
---

# 须弥写作全局约束规则

所有须弥写作 Skill 必须遵守以下规则。规则按角色拆分：子Agent用精简版 `subagent-rules.md`，父Agent读本文件。

## 文件索引

| 文件 | 内容 |
|------|------|
| `SKILL.md` （本文件） | 子Agent并行处理、职责边界、状态标记、调用协议 |
| `continuity.md` | 剧情统一门禁、冲突检测规则、伏笔生命周期管理 |
| `protocol.md` | Context Pack 格式、自举协议、项目 Schema、Skill 职责明细、修改边界、质量检查 |
| `conventions.md` | 输出级别规范、写作安全与原创性 |

---

## 一、子Agent并行处理规则

| 规则 | 说明 |
|------|------|
| **适用范围** | 章节写作、章节重写、剧情审查、轻量修复、内容润色、完稿校验、平台导出、章节细纲生成 |
| **核心原则** | 写正文必须走子agent，单章续写也必须走子agent，父agent绝不写正文 |
| **并行上限** | 最多 5 个子agent同时运行 |
| **分片约束** | 每个子Agent最多负责 3 个连续章节 |
| **计算公式** | 所需Agent数 = `min(ceil(总章节数 / 3), 5)` |
| **分配策略** | 按章节顺序连续分组（1-3、4-6、7-9...） |
| **上下文约束** | 每个子Agent只接收完成任务所需的精简上下文 |

### 批次间串行摘要

每批子Agent完成后，父Agent生成"实际摘要"（≤300字），作为下一批 context pack 的输入。context pack 中只保留最近 3 批摘要，更早的合并为一行概述。

**摘要格式**（纯事实列表）：
```
## 批次摘要: 第1-6章
- 事件：主角觉醒系统(001)、通过宗门考核(003)、击败外门弟子(005)
- 人物：主角练气三层→五层，苏瑾轻伤恢复，赵无极首次出场
- 道具：黑色残片归主角，回春丹消耗2枚
- 伏笔：v1黑衣人身份(mentioned)，v2残片来历(active)
- 情绪：压抑→突破→暗爽
```

**存储位置**：`.sumeru/continuity/batch-summaries/batch-001.md`、`batch-002.md`...

---

## 二、子Agent职责边界规则

**核心原则：子Agent只做单一核心任务，所有状态维护、文件写入、缓存刷新、汇总合并均由父Agent统一处理。**

### 父Agent职责

| 职责 | 说明 |
|------|------|
| 自举 & 环境准备 | 定位项目、读/生成 project.json、status.json、补齐目录 |
| Context pack 生成 | 集中生成 context pack，控制 1500-3000 中文字，分发给各子Agent |
| Cache 摘要读取 | 集中读取 L1 cache 摘要 |
| 任务卡读取 | 集中读取目标章节任务卡，仅提取本组章节所需字段 |
| 任务分发 | 启动 N 个子Agent，每个传入精简 context pack |
| 结果汇总 | 收集所有子Agent输出，检查完整性、顺序、命名 |
| 文件写入 | 统一写入输出文件，避免并发冲突 |
| 备份 | 修改前将原文件备份到 `.sumeru/write/original/`，每章仅保留最近 1 份 |
| 状态更新 | 统一更新 `.sumeru/status.json`（章节状态、阶段状态） |
| 缓存刷新 | 统一刷新相关 cache 摘要 |
| 日志记录 | 统一追加 `.sumeru/changelog.md`、`.sumeru/decisions.md` |
| Issue/测试汇总 | 合并各子Agent发现的问题，写入 `.sumeru/issues.md` |

### 子Agent职责

| 职责 | 说明 |
|------|------|
| 只读 context pack | 不读取 context pack 外的任何文件 |
| 执行核心任务 | 根据 context pack 完成任务卡/审查/润色要求 |
| 输出纯结果 | 纯文本结果，不含状态更新指令 |
| 不碰状态 | 不更新 status.json、changelog、cache、issues |
| 输出状态标记 | 正文/细纲首行必须包含 `<!-- SUMERU_STATUS: ... -->` |

---

## 三、子Agent输出状态标记

每个子Agent的输出首行固定包含状态标记，父Agent提取并更新状态文件，避免单点故障。

### 格式

```markdown
<!-- SUMERU_STATUS: chapter=037, status=drafted, state_diff={"location_change":{"苏瑾":"北域冰原"},"state_change":{"苏瑾":"minor_injury"},"item_change":{"黑色残片":"acquired"}}, char_update={"苏瑾":{"status":"minor_injury","location":"北域冰原"},"主角":{"status":"healthy","buff":"龙血狂暴","remaining":"3天"}}, plot_update={"foreshadowing":{"v3":"黑衣人身份暗示推进"}}, batch=002, timestamp=2026-05-18T10:30:00Z -->
```

### 字段说明

| 字段 | 含义 | 格式 |
|------|------|------|
| `chapter` | 章节号 | 字符串 |
| `status` | 章节状态 | `drafted` / `polished` / `finalized` |
| `state_diff` | 结构化状态变化 | JSON 对象 |
| `char_update` | 人物当前状态 | JSON 对象 |
| `plot_update` | 伏笔线推进 | JSON 对象 |
| `batch` | 所属批次号 | 字符串 |
| `timestamp` | 生成时间 | ISO 8601 |

### state_diff 分类

```json
{
  "location_change": {"人物名": "新地点"},
  "state_change": {"人物名": "新健康状态"},
  "power_change": {"人物名": "新战力等级"},
  "item_change": {"道具名": "acquired|destroyed|transferred"},
  "foreshadow_change": {"伏笔ID": "mentioned|resolved"},
  "buff_change": {"人物名": "buff描述|expired"}
}
```

各分类键可选，只包含本章有变化的分类。`state_diff` 必须是合法 JSON 单行。

### 关键约束

- 状态标记必须在输出**第一行**
- 标记缺失、JSON 不合法、章节号不匹配时，不得更新状态文件

### 父Agent处理流程

1. 提取每章的 `<!-- SUMERU_STATUS -->` 标记
2. 解析 `state_diff` 更新 `.sumeru/continuity/consistency-rules.json`
3. 解析 `char_update` 更新人物状态
4. 将 `status` 写入 `.sumeru/status.json`
5. 重启后扫描 `chapters/*.md` 标记即可重建状态

---

## 四、子Agent调用协议

父Agent生成 2 个文件写入 `.sumeru/context-packs/`：

1. **共享上下文** `shared-{task}.md`：同批次所有子Agent共用，含 Project Brief、Continuity、Creative Strategy 等
2. **本组任务卡** `cards-{范围}.md`：每子Agent独有，仅含本组章节的任务卡 + 执行提醒

通过 Task tool 的 prompt 指示子Agent先读共享上下文，再读本组任务卡。子Agent只返回文本结果，不写项目文件。

**沙箱约束：** 子Agent只能读这 2 个文件，不能写项目文件，不能搜索项目目录。
