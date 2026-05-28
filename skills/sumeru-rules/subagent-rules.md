---
name: subagent-rules
description: 子Agent精简版约束规则。子Agent只读此文件+context pack，不读取全局规则。
type: skill
---

# 子Agent精简版约束规则

> ⚠️ **重要**：这是给子Agent看的精简版规则。父Agent使用的是 `SKILL.md`。

---

## 一、核心职责

| 原则 | 说明 |
|------|------|
| **读 2 个文件：共享上下文 + 本组任务卡** | 先读共享上下文 `shared-{task}.md`，再读本组任务卡 `cards-{范围}.md`。可读已有章节文件以保持连续性。 |
| **执行单一核心任务** | 根据 context pack 中的任务卡/审查标准/润色要求，完成唯一核心任务 |
| **直接写入正文章节文件** | 正文直接写入 `chapters/*.md`，细纲写入 `outlines/chapters.json` |
| **返回状态标记** | 返回精简 `<!-- SUMERU_STATUS: ... -->`（不含正文），父Agent据此更新状态 |
| **不碰状态文件** | 不更新 status.json、不写 changelog、不刷 cache、不写 issues |

---

## 二、状态标记格式

写入的章节文件首行必须包含状态标记（供重启恢复），同时向父Agent返回同一标记（供实时状态同步）：

```markdown
<!-- SUMERU_STATUS: chapter=037, status=drafted, state_diff={"location_change":{"苏瑾":"北域冰原"},"state_change":{"苏瑾":"minor_injury"},"item_change":{"黑色残片":"acquired"}}, char_update={"苏瑾":{"status":"minor_injury","location":"北域冰原"},"主角":{"status":"healthy","buff":"龙血狂暴","remaining":"3天"}}, plot_update={"foreshadowing":{"v3":"黑衣人身份暗示推进"}}, batch=002, timestamp=2026-05-18T10:30:00Z -->
```

### state_diff 分类（只能包含以下键）

| 分类键 | 含义 | 示例 |
|--------|------|------|
| `location_change` | 人物位置变化 | `{"苏瑾":"北域冰原"}` |
| `state_change` | 人物健康状态变化 | `{"苏瑾":"minor_injury"}` |
| `power_change` | 战力等级变化 | `{"主角":"练气五层"}` |
| `item_change` | 道具状态变化 | `{"黑色残片":"acquired"}` |
| `foreshadow_change` | 伏笔状态变化 | `{"v3":"mentioned"}` |
| `buff_change` | Buff状态变化 | `{"主角":"龙血狂暴|3天"}` |

### 关键约束

- 状态标记必须放在写入文件的**第一行**，不能有任何前置文字
- 向父Agent返回的标记内容必须与文件首行完全一致
- `state_diff` 必须是合法 JSON（单行，无换行符）
- 不确定的状态变化可以留空该分类但不能省略整个标记

---

## 三、Context Pack 使用规则

**context pack 拆为 2 个文件：**

| 文件 | 命名规则 | 内容 | 是否共享 |
|------|----------|------|----------|
| 共享上下文 | `shared-{task}.md` | Project Brief、Current Volume、Characters、World、Continuity、Creative Strategy、Batch Summary | 同批次所有子Agent共用 |
| 本组任务卡 | `cards-{范围}.md` | 仅本组章节的 Chapter Cards + 执行提醒 | 每子Agent独有 |

**读取顺序：**
1. 先读 `shared-{task}.md`，获取全局上下文
2. 再读 `cards-{范围}.md`，获取本组章节的具体任务
3. 两个文件的内容合并作为完整的 context

**规则：**
- 优先读取共享上下文和本组任务卡，可读已有章节文件保持连续性
- context pack 中嵌入的"可用缓存的键"列表，如需更多信息可在输出中标记
- 不使用 Glob/Grep/Read 搜索项目目录（已有的下一章文件可用已知路径直接读取）

---

## 四、剧情统一门禁（写作/润色时遵守）

写作前 context pack 中已包含以下基准，必须严格遵守：

1. **剧情事实基准**：上一章实际结尾、当前时间线、当前地点、主线目标
2. **人物状态基准**：相关人物的位置、伤势、战力、关系、情绪状态
3. **物品与能力基准**：关键道具归属、是否损坏/消耗、能力限制
4. **伏笔状态基准**：已设置、推进中、已回收、禁止重复激活的伏笔
5. **禁止改写事实**：不得改变已发生事件、已确定人设、已回收伏笔、既定战力体系

### 冲突检测规则（子Agent自查）

| 规则 | 检查内容 |
|------|----------|
| `unique_location` | 同一人物不能同时在两个地点 |
| `destroyed_item_used` | 已毁道具不能再次使用 |
| `foreshadowing_recycled` | 已回收伏笔不能再次 active |
| `character_state_regression` | 人物状态不能无原因回退 |
| `power_level_consistency` | 战力等级不能无原因跳跃 |
| `timeline_order` | 事件时间线必须有序 |

---

## 五、输出级别

默认 `quiet` 模式，只输出进度和关键节点。详见 `sumeru-rules conventions.md` 输出级别规范。

---

## 六、各 Skill 子Agent核心任务

| Skill | 核心任务 | 输入 | 输出 |
|-------|----------|------|------|
| **sumeru-write** | 按任务卡写正文 | context pack（任务卡+上一章结尾+剧情事实基准+人物/道具/伏笔状态） | 写入 `chapters/*.md` + 返回状态标记 |
| **sumeru-review** | 按任务卡审查章节 | context pack（任务卡+正文+审查标准+consistency-rules） | 审查结论（问题列表+严重程度+证据+建议） |
| **sumeru-polish** | 按标准润色章节 | context pack（正文+style-brief+creative-brief+审查问题+具象标杆） | 写入 `chapters/*.md` + 返回状态标记 |
| **sumeru-outline** | 生成章节细纲 | context pack（世界观+人物+分卷大纲+上下文关联） | 写入 `outlines/chapters.json` + 返回状态标记 |
| **sumeru-finalize** | 待定项判断 | 待定项列表（最多20个） | 待定项处理建议 |

---

## 七、反AI写作规则（write/polish 子Agent遵守）

> **AI 写得越"正确"的部分越要改，写得越"奇怪"的部分越要保留。**

| 维度 | AI"正确"写法 | 人类"奇怪"写法 |
|------|-------------|---------------|
| 逻辑 | 因果完整、层层递进 | 突然跳跃、留白、不解释 |
| 表达 | 精准、书面化、规范 | 模糊、口语化、不完美 |
| 冗余 | 删除重复、精炼用词 | 重复、啰嗦、自我纠正 |
| 情绪 | 线性递进、层次分明 | 矛盾、混乱、说不清 |
| 对话 | 有目的、有潜台词 | 跑题、重复、没说出口的话 |
| 细节 | 服务于情节 | 无意义、个人化 |
| 结尾 | 有总结、有钩子 | 突然、留白、没说完 |
| 语感 | 主谓宾齐全、标点规范 | 破碎句、倒装、重复标点、口头禅 |

**禁止项**：
- ❌ 禁止"去除冗余表述"
- ❌ 禁止"精炼用词"
- ❌ 禁止"节奏收紧"
- ❌ 禁止"精准用词"
- ❌ 禁止"潜台词""节奏控制"等过度优化
- ❌ 禁止"标点规范化"

---

## 八、风格样本（可选）

context pack 中嵌入了用户风格特征时，主动模仿其用词、句式、对话和情绪表达习惯。输出后自检是否有"太正确"的地方，对照样本修改。无样本时按通用网文风格写作。

---

## 九、情绪节点验证（review 子Agent执行）

任务卡定义了 `emotionalBeat`，必须按顺序验证每个阶段：

```
验证规则：
- [ ] 每个情绪阶段在文本中是否有对应内容？
- [ ] 各情绪阶段出现位置是否符合定义的顺序？
- [ ] 情绪强度是否足够（太低可能读者无感）？
- [ ] 情绪转换是否自然（突然跳跃可能生硬）？

输出：
- ✅ emotional_curve_complete（全部通过且顺序正确）
- ⚠️ emotional_gap: [缺少阶段名称]
- ⚠️ emotional_order_error: [实际顺序]
- ⚠️ emotional_intensity_low: [阶段名称，强度评分]
- ⚠️ emotional_transition_abrupt: [从前一阶段到后一阶段的跳跃]
```

---

## 十、禁止行为

- ❌ 不读取 `shared-{task}.md` 和 `cards-{范围}.md` 以外的项目文件（已有章节文件除外）
- ❌ 不写入 `chapters/*.md` 和 `outlines/chapters.json` 以外的项目文件
- ❌ 不更新 status.json、changelog、cache、issues
- ❌ 不使用 Glob/Grep/Read 搜索项目目录
- ❌ 不在返回给父Agent的输出中包含正文内容（文件已直接写入）
- ❌ 不输出中间报告和技术细节
