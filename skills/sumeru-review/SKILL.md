---
name: sumeru-review
description: 小说逻辑/剧情审查、项目测试与创意疲劳检测
version: 1.2.2
type: skill
argument-hint: "[章节范围] [仅检查...]"
disable-model-invocation: false
user-invocable: true
allowed-tools: Read, Glob, Grep, Bash(python scripts/*.py), task
context: project
agent: build
---

> 依赖 `sumeru-rules`，默认`quiet` 模式。附检查脚本：`scripts/continuity-check.py`、`scripts/foreshadowing-tracker.py`。
## 网文逻辑审查

### 触发关键词
帮我检查下小说有没有bug、看看时间线有没有矛盾、人物有没有OOC、找剧情前后冲突、梳理伏笔有没有回收、检查小说剧情合理性、看看有没有剧情漏洞、人物行为不符合性格、检查时间线对不对、找小说前后矛盾的地方、帮我梳理所有伏笔、小说剧情bug检查、逻辑漏洞排查、小说剧情审查、自动修复错别字、情绪节点验证
### 核心功能
1. **全局审查**：分析整体剧情脉络、时间线、设定一致性、冲突点分布、伏笔回收状态
2. **章节细节审查**：逐章检查字数、时间线、人物OOC、物品状态、场景质量、伏笔设置
3. **统一修复**：轻量问题直接修复并输出最终版本，严重问题写入修复计划
4. **创意疲劳检测**：套路重复、情绪重复、创意目标未落地检测
5. **剧情统一验收**：检查章节是否承接上一章实际结尾，是否违反 continuity 中的人物、道具、伏笔、战力和时间线状态
### 独立调用自举
1. 定位项目根目录，读取或生成`.sumeru/project.json`、`.sumeru/status.json`
2. 根据 `chapters/` 推断可审查章节范围；若 `project.json.volumeCount >= 2`，按**分卷模式**定位 continuity 路径（见下方「分卷审查模式」），扫描当前卷的 `.sumeru/volumes/vol-N/continuity/` 而非 `.sumeru/continuity/`
3. 若缺少`outlines/chapters.json`，按旧路径兼容策略处理（见`sumeru-rules/SKILL.md` 第六部分"独立调用自举协议"）
4. 若缺少`.sumeru/cache/`，生成最小摘要
5. 若缺少当前范围的 context pack，先生成临时 context pack 再审查
### 按模式审查
| 模式 | 输出内容 |
|------|----------|
| `short/light` | 单文件`reviews/review-report.md`，检查结构、人物动机、反转合理性|
| `medium/standard` | `reviews/review-report.md`，问题记录到 `.sumeru/issues.md` |
| `long/full` | 目标范围审查；用户要求完整报告时生成 `reviews/` 和`tests/` |

### 四阶段审查修复流程
**第一阶段：目标范围基准审查（父Agent执行）**
- 加载目标章节任务卡、前后必要摘要和 consistency-rules
- 只分析当前范围所需的剧情脉络、时间线和设定一致性
- 用户要求"全书审查/完整报告"时，才加载全局大纲并生成完整报告
**第二阶段：章节细节审查（子Agent并行）**

> **并行规则**详见 `sumeru-rules/SKILL.md` 第二部分"子Agent并行处理规则"）
- 每个子Agent最多3 章，使用 `review-<range>.md` context pack
- 子Agent输出审查结论+状态标记
- 父Agent汇总所有子Agent输出

**第三阶段：统一修复**
- 轻量修复 → 备份后直接修改`chapters/`，产出最终版本
- 重写修复 → 生成 `fix-plan.json`，由 `sumeru-worldbuilder` 编排或用户手动调用`sumeru-write` 处理

**第四阶段：修复验证（反审模式）**
修复完成后（auto-fix 或 rewrite），自动触发轻量反审。
**反审范围**：仅验证 fix-plan.json 中标记的问题是否已解决
- 不重新做全量审查
- 只检查fix 目标章节中已报告问题的修复状态
- 输出 `.sumeru/review/reverify-result.json`

**反审流程**：
1. 读取 fix-plan.json 中的修复记录
2. 对每个已修复章节执行针对性验证（只检查原问题类型）
3. 验证通过 → 章节状态更新为 `fixed`
4. 验证未通过 → 追加到issues.md，标记`reverify_failed`

**反审由父Agent直接执行**，不启动子Agent。
### fix-plan.json 格式定义

`fix-plan.json` 在review 阶段生成，供 write 阶段的重写流程读取：

```json
{
  "generatedAt": "2026-05-18T10:00:00Z",
  "chapters": ["005", "012"],
  "fixes": [
    {
      "chapter": "005",
      "type": "character_ooc",
      "severity": "high",
      "description": "苏瑾性格突变，从冷静变为暴躁",
      "suggestedFix": "保留冷静人设，将暴躁对话改为内心独白",
      "autoFixable": false
    },
    {
      "chapter": "012",
      "type": "timeline_error",
      "severity": "critical",
      "description": "第12章事件发生在第11章之后",
      "suggestedFix": "调整第12章时间线，确保在第11章之后",
      "autoFixable": true
    }
  ]
}
```

**字段说明**
- `type`：问题类型（`character_ooc`、`timeline_error`、`plot_hole`、`foreshadow_missing`、`word_count`、`typo`、`punctuation`、`punctuation_space`、`quote_closure`、`book_title`、`punctuation_format`、`repeated_char`、`format`、`other`）
- `severity`：严重程度（`critical`、`high`、`medium`、`low`）
- `autoFixable`：是否可自动修复（`true` 时write 子Agent可直接处理，`false` 时需用户确认）
---

### 自动修复策略

#### 可自动修复的问题

| 问题类型 | 修复方式 | 示例 |
|----------|----------|------|
| **错别字** | 词典匹配 + 上下文验证 | "在次" 改为"再次"、"在经" 改为"已经" |
| **标点错误** | 规则替换 | 连续逗号"，，"改为"、"、英文标点改为中文标点、省略号格式统一为"……"、破折号格式统一为"——"、引号/书名号/括号闭合检查、标点前后空格清理（详见 `sumeru-rules` 第六点五部分） |
| **重复字** | 去重 | "非常非常" 改为"非常"、"真的真的" 改为"真的" |
| **格式问题** | 统一格式 | 章节标题格式统一为`第X章 标题`、首行缩进统一 |
| **重复段落** | 标记 + 去重 | 连续两段内容高度相似时标记 |
| **空格/换行异常** | 规范化 | 多余空行合并、首尾空格去掉 |
| **句号未分段** | 自动换行 | 检测句号（。）后无换行符的情况，自动在句号后插入换行符 |
| **字数不足** | ⚠️ **不再自动注入描写段**（防止水文）。改用反 AI 扫描+ fix-plan 标记，触发 write 重写 | 调用 `python skills/sumeru-review/scripts/anti-ai-scan.py <chapters_dir>` 报告问题；将 `word_count_short` 写入 `fix-plan.json`，由 write 阶段在当前场景中"自然展开"（让人物多一个反应、多一句停顿、多一段沉默）补足 |

**自动修复流程**：
1. 脚本扫描（错别字词典、10类标点规范检测、重复字检测）
2. 标记可自动修复项（`autoFixable: true`）
3. 父Agent直接应用修复（不经过子Agent）
4. 修复后生成`fix-log.json` 记录修复内容

#### 不可自动修复的问题
| 问题类型 | 原因 | 处理方式 |
|----------|------|----------|
| **人物OOC** | 需要理解人物性格和剧情脉络 | 写入 `fix-plan.json`，需用户确认或重写 |
| **剧情bug** | 需要理解整体剧情逻辑 | 写入 `fix-plan.json`，需用户确认或重写 |
| **战力跳跃** | 需要理解战力体系和战斗描写 | 写入 `fix-plan.json`，需用户确认或重写 |
| **时间线矛盾** | 需要理解时间线和事件顺序 | 写入 `fix-plan.json`，需用户确认或重写 |
| **伏笔未回收** | 需要理解伏笔意图和回收时机 | 写入 `fix-plan.json`，需用户确认或重写 |
| **情绪曲线问题** | 需要理解情绪设计和读者体验 | 写入 `fix-plan.json`，需用户确认或重写 |
| **创意疲劳** | 需要理解创意目标和套路对比 | 写入 `fix-plan.json`，需用户确认或重写 |

#### 自动修复边界

- 自动修复只针对**技术性错误**（错别字、标点、重复字、格式）
- 自动修复**不改变剧情事实、人物性格、设定、伏笔**
- 自动修复后必须生成修复日志，用户可随时查阅撤销
- 涉及剧情/人物/设定的修改必须经过用户确认
---

### 检查类型
- **剧情统一**：上一章结尾承接、人物位置/伤势/战力、道具归属、伏笔状态、时间线顺序
- **字数检查**：章节字数达标检查，不足时按任务卡直接补充
- **时间线**：时间线/年龄/事件顺序一致性
- **人物OOC**：人物性格/行为OOC检查
- **剧情逻辑**：剧情逻辑/设定一致性
- **伏笔**：伏笔回收检查
- **常识**：常识/因果合理性检查
- **创意疲劳**：套路重复、情绪重复、创意目标未落地
- **情绪节点验证**（新增）：检查emotionalCurve 中的每个阶段是否在文本中有对应内容
- **平台适配验证**（新增）：开篇钩子强度、叙事效率、对话叙述比例、章节信息密度，对标七猫/番茄免费阅读平台标准
- **句号分段检查**（强制）：检查正文是否每个句号（。）后都换行分段，对话中的句号同样需要分段

### 反 AI / 反水文扫描（v1.3.3+ 新增，v1.3.4 扩展）

> **关键定位**：本节为反水文的**主防线**。父 Agent 在每批写作/重写/润色后**必须**调用反 AI 扫描脚本，**不能仅依赖人工/规则文字自检**。

#### 扫描脚本

```bash
python skills/sumeru-review/scripts/anti-ai-scan.py <chapters_dir> \
    [--outlines outlines/chapters.json] \
    [--output .sumeru/review] \
    [--quiet] [--strict]
```

输出：
- `.sumeru/review/anti-ai-report.json`：结构化报告
- `.sumeru/review/anti-ai-report.md`：人工可读报告

#### 扫描项（共 17 项 + 9 维反 AI 句式，v1.3.4: 6→8 维，v1.2.4: 8→9 维，黑名单 40+ → 80+）

| 类别 | 检查项 | 阈值 | 严重度 |
|------|--------|------|--------|
| 9 维反 AI | 句式重复 | 连续 ≥ 6 句主谓宾完整 | medium |
| 9 维反 AI | 段内开场重复 | 同一段连续 3 句同主语 | low |
| 9 维反 AI | 连续推进无缓冲 | 连续 ≥ 3 段都在推进剧情 | low |
| 9 维反 AI | 批内开场雷同 | 相邻章首 8 字重复 | medium |
| 9 维反 AI | 批内钩子雷同 | 相邻章末 8 字重复 | medium |
| 9 维反 AI | 字数波动 | 偏离批均值 ±50% | low |
| 9 维反 AI | **段间 micro-arc 模板**（v1.3.4 新增）| 4 段结构指纹（A=推进/B=心理/C=描写/D=对话）出现 ≥ 2 次（章节 ≥ 8 段）| medium |
| 9 维反 AI | **对话标记词集中**（v1.3.4 新增）| 单一标记词占全部 ≥ 80%（总标记 ≥ 5）| medium |
| 9 维反 AI | **对话后旁白解说**（v1.2.4 新增）| 对话引号后 50 字内情绪解说词 ≥ 3 处 | medium |
| 水文硬指标 | 对话占比 | < 5% | medium |
| 水文硬指标 | 内心独白占比 | > 10% | medium |
| 水文硬指标 | 纯描写段落占比 | > 35% | **high（阻断）** |
| 水文硬指标 | 核心事件数 | < 1 | **high（阻断）** |
| 水文硬指标 | 时间/场景切换 | 0 | medium |
| 水文硬指标 | **Cliché 套路短语**（v1.3.4 黑名单扩展：+ 战斗套路 + 转折模板 + 情绪标签）| ≥ 3 个不同短语 | **high（阻断）** |
| 节奏拖沓 | 场景类型占比 | 日常/过渡 > 30% | medium |
| 节奏拖沓 | 字数不足（不再自动修复） | < `chapterWordRange[0]` | medium（写 fix-plan） |
| 节奏拖沓 | 字数过多 | > `chapterWordRange[1]` | low |

#### 阻断规则

以下任一命中触发**重写**而非自动修复（由父 Agent 决定是否中断批次）：
- `narrative_high_description`（high）
- `narrative_low_event_density`（high）
- `water_text_cliche_density`（high）

**v1.3.4 灰度说明**：`anti_ai_micro_arc_repeat` / `anti_ai_dialog_marker_dominant` 暂留 medium 不进阻断，先观察一轮后视情况升级为 high（避免对既有合规文风误伤）。

父 Agent 处理：
1. 将 `blocking=true` 的章节写入 `fix-plan.json`，`type=anti_ai_blocked`
2. 调用 sumeru-write 走重写流程，强制 context pack 中携带反 AI 扫描报告
3. 严禁用"插入 2-4 段感官细节/内心独白/场景描写"方式补字数（v1.3.2 及之前的错误做法，v1.3.3 已删除）
4. v1.3.4 新增：micro_arc 命中时优先用"重排段落顺序"或"调换段间衔接"修复，而非简单插入内容

#### quiet 模式输出约定

- 无问题：`✅ 反 AI 扫描通过 (N 章无问题)`
- 有问题：`⚠️ 反 AI 扫描发现 X 项问题 (critical=… high=… medium=… low=…)` + 报告路径
- 阻断：`🚨 含阻断规则，建议重写`

### 平台适配审查规则

> **定位**：通用质量检查，不区分平台类型。所有小说都需要检查的叙事效率指标，适用于七猫/番茄/起点/晋江等全平台。
> **核心指标阈值定义**见`sumeru-rules/SKILL.md` 第十三部分"平台适配规则索引"。本节仅定义审查阶段的执行流程和输出格式。
#### 开篇钩子强度检查
仅对**第1章**执行。对标免费阅读平台读者留存规律：

| 指标 | 阈值 | 说明 |
|------|------|------|
| **100字冲突启动** | 必须在100字内出现核心冲突/反常事件/悬念 | 超出→警告`hook_delay` |
| **100字无设定铺陈** | 100字禁止出现世界观介绍、人物背景说明、环境长描写 | 出现→警告`hook_expo_dump` |
| **第1章结尾钩子** | 结尾必须有"必须翻页"的悬念/反转/未解问题 | 无→警告 `hook_missing_ch1` |
| **主角第一幕主动性** | 主角在前500字内必须做出主动选择（非被动接受） | 无→警告 `hook_passive_protagonist` |

#### 叙事效率检查
| 指标 | 阈值 | 适用章节 | 说明 |
|------|------|----------|------|
| **对话占比** | >5% | 全部章节 | 对话占总字数比例。对话引号内文本。不足→警告 `narrative_low_dialogue` |
| **内心独白占比** | >10% | 全部章节 | 心理描写/内心活动占总字数比例。超出→警告 `narrative_high_monologue` |
| **纯描写段落占比** | >35% | 全部章节 | 环境描写/外貌描写/动作细节描写。超出→警告 `narrative_high_description` |
| **每章核心事件数** | ≥1 | 全部章节 | 每章至少有一个明确的情节推进事件。不足→警告 `narrative_low_event_density` |
| **相邻章核心事件重复** | 0 | 全部章节 | 连续2章不能做同一件事（如"连续2章都在搭讪"属异常）。出现→警告 `narrative_event_stagnation` |

#### 信息密度检查
| 指标 | 阈值 | 说明 |
|------|------|------|
| **章内时间推进** | ≥1个时间节点变化 | 章内必须有至少一个时间推进（如下午→傍晚、今天→明天）|
| **章内地点变化** | ≥1个场景切换或地点变化 | 章内不能从头到尾待在同一个位置不动 |
| **断章位置（低密度警告）** | 连续3章单事件密度=1 | 连续3章每章只发生一件事→警告`density_low_chain` |

#### 审查输出格式

平台适配问题整合到主审查报告中，使用独立 section。
```markdown
## 平台适配审查

### 开篇钩子
| 章节 | 100字冲突 | 设定铺陈 | 结尾钩子 | 主角主动性 | 状态 |
|------|------------|---------|---------|-----------|------|
| 001 | 前198字工作铺垫 | ⚠️ 展品清单背景 | ⚠️ | ⚠️ | hook_delay |

### 叙事效率
| 章节 | 对话占比 | 内心独白占比 | 描写占比 | 核心事件数 | 问题 |
|------|---------|------------|---------|-----------|------|
| 001 | 8% | 42% | 35% | 1 | narrative_low_dialogue, narrative_high_monologue |
| 002 | 3% | 68% | 22% | 1 | narrative_low_dialogue, narrative_high_monologue |

### 信息密度
| 章节范围 | 时间推进 | 地点变化 | 连续低密度 | 问题 |
|----------|---------|---------|-----------|------|
| 001-007 | ⚠️ | ⚠️ | ⚠️ 7章单事件 | density_low_chain(001-007) |
```

#### 问题严重度分级
平台适配问题按严重度分级处理：
| 级别 | 条件 | 自动修复 | 处理方式 |
|------|------|---------|---------|
| **critical** | 第1章无结尾钩子 OR 连续5章以上低密度 | 不支持 | 写入 fix-plan.json，需重写 |
| **high** | 100字有设定铺陈 OR 对话占比<15% OR 连续3章低密度 | 不支持 | 写入 fix-plan.json，建议重写 |
| **medium** | 内心独白>40% OR 描写>35% OR 连续2章事件重复 | 可自动修复 | 润色阶段降低比例 |
| **low** | 对话占比20-25% OR 章内无地点变化 | 可自动修复 | 润色阶段微调 |

### 题材自适应

根据 `.sumeru/project.json` 的`style` 字段调整审查重点：
| style 关键词 | 审查重点 |
|-------------|---------|
| 包含"爽文""热血""快节奏" | 爽点密度、反派智商、战力体系、节奏压迫感 |
| 其他（含"精品文""细腻""文艺"及未设置） | 情感递进、情绪节拍转换、对话真实度、场景质量 |

字数检查统一读取 `project.json` 中的 `chapterWordRange` 作为目标范围，不依赖模式。
### 情绪节点验证规则（增强版）
**问题**：任务卡定义的`emotionalBeat: "压抑 → 困惑 → 恍然 → 暗爽"`，但 AI 可能跳过某个阶段、顺序错乱、强度不足或转换生硬。
**解决方案**：生成后自动检查每个情绪阶段的**存在性、顺序、强度、转换自然度**。
#### 验证规则

```markdown
## 情绪节点验证（增强版）
### 输入
- emotionalBeat: "压抑 → 困惑 → 恍然 → 暗爽"
- 文本内容：完整章节正文
### 检查项（必须全部验证）

#### 1. 存在性检查
- [ ] "压抑"阶段：文本前 1/4 是否有体现压抑情绪的内容？
- [ ] "困惑"阶段：文本1/4-1/2 是否有体现困惑情绪的内容？（必须在压抑之后）
- [ ] "恍然"阶段：文本1/2-3/4 是否有体现恍然情绪的内容？（必须在困惑之后）
- [ ] "暗爽"阶段：文本后 1/4 是否有体现暗爽情绪的内容？（必须在恍然之后）

#### 2. 顺序校验
- 各情绪阶段在文本中的出现位置必须符合 emotionalBeat 定义的顺序
- 允许中间穿插其他情绪，但主情绪顺序不可颠倒
- 如果"暗爽"出现在"压抑"之前 → ⚠️ emotional_order_error

#### 3. 强度检查（新增）每个情绪阶段需要达到最低强度阈值，否则读者无感：

| 情绪类型 | 强度指标 | 阈值 |
|----------|----------|------|
| 压抑 | 负面词汇密度 + 环境压抑描写 | 2处明显压抑描写 |
| 困惑 | 疑问句/内心疑问/不确定性表达 | 2处明显困惑表达 |
| 恍然 | 顿悟/发现/恍然大悟的描写 | 2处明显恍然时刻 |
| 暗爽 | 胜利/反击/打脸的描写 | 2处明显爽点 |

- 如果某阶段强度不足 → ⚠️ emotional_intensity_low: [阶段名称，强度评分]

#### 4. 转换自然度检查（新增）情绪转换不能过于突兀，需要合理的过渡：
| 检查项 | 说明 |
|--------|------|
| 过渡段落 | 两个情绪阶段之间是否有过渡段落（1-3段）？|
| 触发事件 | 情绪转换是否有明确的触发事件（如某个发现、某个对话）？|
| 心理描写 | 情绪转换是否有内心活动的过渡描写？|

- 如果转换过于突兀 → ⚠️ emotional_transition_abrupt: [从前一阶段到后一阶段的跳跃]

### 输出

| 结果 | 说明 |
|------|------|
| ✅ emotional_curve_complete | 全部通过且顺序正确 |
| ⚠️ emotional_gap: [缺少阶段名称] | 缺少某阶段 |
| ⚠️ emotional_order_error: [实际顺序] | 顺序错乱 |
| ⚠️ emotional_intensity_low: [阶段名称，强度评分] | 强度不足 |
| ⚠️ emotional_transition_abrupt: [从前一阶段到后一阶段] | 转换生硬 |

```

---

## 分卷审查模式

> **适用条件**：项目 `project.json.volumeCount >= 2`（详见 `sumeru-rules/SKILL.md` 第十五部分·分卷隔离与卷切换协议）。未启用分卷模式的项目继续使用扁平 continuity 路径，本节不生效。
> **职责定位**：review 阶段是**跨卷状态连续性的最终把关者**。write 阶段可能漏掉跨卷依赖的兑现、卷边界的状态漂移，本节定义的检查项就是用来发现这些问题的。

### 1. 范围收窄（Volume-scoped Continuity）

分卷模式下，父Agent在自举阶段从 `project.json.currentVolume` 确定当前卷，审查范围按卷收窄：

- **continuity 读取路径**：`.sumeru/continuity/` → `.sumeru/volumes/vol-N/continuity/`（`state-start.json`、`state-current.json`、`consistency-rules.json`）
- **不扫描其他卷的 continuity**（避免误判跨卷人为设置的差异，例如跨卷战力跃升是预期的）
- **批次摘要路径**：`.sumeru/cache/` → `.sumeru/volumes/vol-N/continuity/batch-summaries/`（按卷隔离）
- **章节状态路径**：`.sumeru/status.json` → `.sumeru/volumes/vol-N/status.json`

### 2. 脚本路径（Volume Mode Script Args）

当 volumes 存在时，父Agent调用检查脚本必须**追加 `--continuity-dir` 参数**，指向当前卷的 continuity 目录：

```bash
# 扁平模式（默认）
python skills/sumeru-review/scripts/continuity-check.py <chapters_dir>

# 分卷模式（追加参数）
python skills/sumeru-review/scripts/continuity-check.py <chapters_dir> \
    --continuity-dir .sumeru/volumes/vol-N/continuity

python skills/sumeru-review/scripts/foreshadowing-tracker.py <chapters_dir> \
    --continuity-dir .sumeru/volumes/vol-N/continuity
```

`currentVolume` 由父Agent从 `project.json.currentVolume` 字段读取后透传给脚本，不得让脚本自行推断（避免跨卷误判）。

### 3. 跨卷检查点（Cross-volume Checkpoint）

审查范围除当前卷内容外，还需**校验本卷是否兑现跨卷依赖**：

1. 父Agent读取 `.sumeru/cross-volume/dependency-table.md`
2. 筛选 `目标卷 == currentVolume` 的所有条目
3. 对每个条目，在本卷章节中查找对应兑现动作（伏笔回收、人物登场、设定启用、关系变化等）
4. 输出**「跨卷依赖检查」section**到审查报告中：

```markdown
## 跨卷依赖检查

| 来源卷 | 依赖类型 | 描述 | 目标章节 | 状态 |
|--------|----------|------|----------|------|
| vol-001 | foreshadow | "黑玉断续膏"在第一卷被埋下 | vol-002/ch020 | ✅ 已兑现（vol-002/ch021 使用） |
| vol-001 | character | "燕无归"承诺第二卷归来 | vol-002/ch005 | ⚠️ 延迟（实际登场 vol-002/ch008） |
| vol-002 | setting | "天机阁"组织设定启用 | vol-003/ch010 | ❌ 未启用 |
```

- **未启用/未兑现的依赖**写入 `fix-plan.json`，`type=cross_volume_dependency_missing`，`severity=high`
- **延迟兑现**（晚于目标章节）写入 `issues.md`，标记 `cross_volume_dependency_delayed`

### 4. 卷边界审查（Volume-edge Review）

当审查范围跨越卷边界（即同时包含某卷最后 5 章 + 下一卷前 5 章）时，父Agent必须追加**边界专项检查**：

| 检查项 | 检查内容 | 严重度 |
|--------|----------|--------|
| **状态连续性** | vol-N `state-final.json` 与 vol-M `state-start.json` 是否一致（人物位置/道具归属/战力值/时间线） | critical |
| **人物状态一致性** | 跨边界人物的位置、伤势、关系、情绪是否自然延续，无突兀跳转 | high |
| **伏笔不悬空** | 卷尾埋设的伏笔是否已注册到 `dependency-table.md`，未注册的补注册 | medium |
| **风格/节奏过渡** | 卷首 5 章是否承接卷尾的情绪曲线和叙事节奏，无风格断层 | low |
| **时间线连贯** | 卷尾时间点 → 卷首时间点是否合理（无时间跳跃无交代 / 时间倒流） | critical |

边界审查输出追加到审查报告的「卷边界检查」section，问题严重度按上表处理。

### 5. 全书审查模式（Global Review Mode）

当用户**明确要求**「全书审查 / 完整报告 / 跨卷分析」时，审查范围扩展为全局：

- **额外加载** `.sumeru/cross-volume/` 全部数据（`dependency-table.md`、`master-timeline.md`、`master-characters.md`）
- **扫描所有卷的 continuity**（`vol-001` ~ `vol-N`）做跨卷一致性对比
- **检查项扩展**：
  - 跨卷战力体系一致性（`cross_volume_power_leap`）
  - 跨卷时间线连贯性（`cross_volume_timeline_gap`）
  - 跨卷设定无矛盾（`cross_volume_setting_conflict`）
  - 卷间情绪/节奏过渡自然度（`cross_volume_emotion_cliff` / `cross_volume_rhythm_cliff`）
  - 跨卷人物关系推进（`cross_volume_relationship_stall`）
- **默认审查模式（仅单卷）不触发上述扩展**，仅在用户显式声明「全书审查」时启用

---

### 数据持久化
**用户可见输出**：
- `reviews/review-report.md`：用户可读审查报告
- `tests/*.md`：各类测试报告
**中间数据（`.sumeru/`）**：
- `.sumeru/issues.md`：问题清单
- `.sumeru/review/global-issues.json`：全局问题清单
- `.sumeru/review/fix-plan.json`：重写修复计划
**分卷模式下的路径差异**（`project.json.volumeCount >= 2` 时）：
- continuity 数据源：`.sumeru/volumes/vol-N/continuity/` 而非 `.sumeru/continuity/`
- 章节状态：`.sumeru/volumes/vol-N/status.json` 而非 `.sumeru/status.json`
- 跨卷依赖校验读：`.sumeru/cross-volume/dependency-table.md`
- 卷边界/跨卷问题写入 `fix-plan.json` 时，`type` 前缀加 `cross_volume_`（如 `cross_volume_dependency_missing`、`cross_volume_setting_conflict`）
- 详细规范见 `sumeru-rules/SKILL.md` 第十五部分·分卷隔离与卷切换协议
### 与其他Skill 配合
- **前置**：`sumeru-write` 生成的`chapters/` 和`sumeru-outline` 的大纲数据
- **后续**：输出供 `sumeru-polish`、`sumeru-finalize` 使用


