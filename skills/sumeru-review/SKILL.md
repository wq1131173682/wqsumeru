---
name: sumeru-review
description: 小说逻辑/剧情审查、项目测试与创意疲劳检测。用户要检查小说bug、时间线矛盾、人物OOC、剧情前后冲突、章节任务卡验收、伏笔是否回收、章节字数是否达标、剧情合理性、逻辑漏洞、套路重复、爽点同质化、角色被剧情推着走或创意不够新时必须使用本技能。
user-invocable: true
---

> ⚠️ **依赖技能**：本 Skill 依赖 `sumeru-rules` 中的全局约束。执行前请确保已加载。

> 📌 **核心功能增强**：本 Skill 包含剧情一致性自动检查脚本（`scripts/continuity-check.py`）和伏笔追踪脚本（`scripts/foreshadowing-tracker.py`）。

> 📌 **输出级别**：默认 `quiet` 模式，只输出问题和进度。详细规范见 `sumeru-rules` "输出级别规范"。

## 网文逻辑审查

### 触发关键词
帮我检查下小说有没有bug、看看时间线有没有矛盾、人物有没有OOC、找剧情前后冲突、梳理伏笔有没有回收、检查小说剧情合理性、看看有没有剧情漏洞、人物行为不符合性格、检查时间线对不对、找小说前后矛盾的地方、帮我梳理所有伏笔、小说剧情bug检查、逻辑漏洞排查、小说剧情审查

### 核心功能
1. **全局审查**：分析整体剧情脉络、时间线、设定一致性、冲突点分布、伏笔回收状态
2. **章节细节审查**：逐章检查字数、时间线、人物OOC、物品状态、场景质量、伏笔设置
3. **统一修复**：轻量问题直接修复，严重问题写入修复计划
4. **创意疲劳检测**：套路重复、情绪重复、创意目标未落地检测

### 独立调用自举
1. 定位项目根目录，读取或生成 `.sumeru/project.json`、`.sumeru/status.json`
2. 根据 `chapters/` 推断可审查章节范围
3. 若缺少 `outlines/chapters.json`，尝试读取 `.sumeru/outline/chapter-outlines.json`
4. 若缺少 `.sumeru/cache/`，生成最小摘要
5. 若缺少当前范围的 context pack，先生成临时 context pack 再审查

### 按模式审查
| 模式 | 输出内容 |
|------|----------|
| `short/light` | 单文件 `review.md`，检查结构、人物动机、反转合理性 |
| `medium/standard` | `reviews/review-report.md`，问题记录到 `.sumeru/issues.md` |
| `long/full` | 完整 `reviews/`、`tests/`、`.sumeru/issues/`，支持轻扫和深度审查 |

### 三阶段审查修复流程

**第一阶段：全局信息审查（父Agent执行）**
- 加载完整大纲和章节细纲，建立全局审查基准
- 分析整体剧情脉络和时间线结构
- 审查全局设定一致性
- 记录全局问题清单到 `.sumeru/review/global-issues.json`

**第二阶段：章节细节审查（子Agent并行）**
- 每个子Agent最多 3 章，使用 `review-<range>.md` context pack
- 子Agent输出审查结论+状态标记
- 父Agent汇总所有子Agent输出

**第三阶段：统一修复**
- 轻量修复 → 直接修改 `chapters/`（自动备份到 `.sumeru/write/original/`）
- 重写修复 → 生成 `fix-plan.json`，由 `sumeru-worldbuilder` 编排或用户手动调用 `sumeru-write` 处理

### fix-plan.json 格式定义

`fix-plan.json` 由 review 阶段生成，供 write 阶段的重写流程读取：

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
      "description": "第12章事件发生在第11章之前",
      "suggestedFix": "调整第12章时间线，确保在第11章之后",
      "autoFixable": true
    }
  ]
}
```

**字段说明：**
- `type`：问题类型（`character_ooc`、`timeline_error`、`plot_hole`、`foreshadow_missing`、`word_count`、`other`）
- `severity`：严重程度（`critical`、`high`、`medium`、`low`）
- `autoFixable`：是否可自动修复（`true` 时 write 子Agent可直接处理，`false` 时需用户确认）

**重写流程：**
1. 用户调用 `/sumeru-write 重写第5章` 或 worldbuilder 自动触发
2. write Skill 读取 `fix-plan.json` 中对应章节的 fix 项
3. 将 fix 项嵌入 context pack 的 `## 重写要求` 章节
4. write 子Agent按 fix 要求重写，输出新正文 + 状态标记
5. 父Agent将 fix 项标记为 `fixed`，更新 status.json

### 检查类型
- **字数检查**：章节字数达标检查，不足自动填充
- **时间线**：时间线/年龄/事件顺序一致性
- **人物OOC**：人物性格/行为OOC检查
- **剧情逻辑**：剧情逻辑/设定一致性
- **伏笔**：伏笔回收检查
- **常识**：常识/因果合理性检查
- **创意疲劳**：套路重复、情绪重复、创意目标未落地
- **情绪节点验证**（新增）：检查 emotionalCurve 中的每个阶段是否在文本中有对应内容

### 情绪节点验证规则

**问题**：任务卡定义了 `emotionalBeat: "压抑 → 困惑 → 恍然 → 暗爽"`，但 AI 可能跳过某个阶段或顺序错乱。

**解决方案**：生成后自动检查每个情绪阶段是否有对应内容，且顺序正确。

**验证规则：**
```markdown
## 情绪节点验证

### 输入
- emotionalBeat: "压抑 → 困惑 → 恍然 → 暗爽"

### 检查（必须按顺序验证）
- [ ] "压抑"阶段：文本前 1/4 是否有体现压抑情绪的内容？
- [ ] "困惑"阶段：文本 1/4-1/2 是否有体现困惑情绪的内容？（必须在压抑之后）
- [ ] "恍然"阶段：文本 1/2-3/4 是否有体现恍然情绪的内容？（必须在困惑之后）
- [ ] "暗爽"阶段：文本后 1/4 是否有体现暗爽情绪的内容？（必须在恍然之后）

### 顺序校验
- 各情绪阶段在文本中的出现位置必须符合 emotionalBeat 定义的顺序
- 允许中间穿插其他情绪，但主情绪顺序不可颠倒
- 如果"暗爽"出现在"压抑"之前 → ⚠️ emotional_order_error

### 输出
- 全部通过且顺序正确 → ✅ emotional_curve_complete
- 缺少某阶段 → ⚠️ emotional_gap: [缺少阶段名称]
- 顺序错乱 → ⚠️ emotional_order_error: [实际顺序]
```

**示例：**
```markdown
# 任务卡定义
"emotionalBeat": "压抑 → 困惑 → 恍然 → 暗爽"

# 实际文本
- 压抑（段落5）：✅ 开篇展示主角废柴处境
- 困惑：❌ 直接跳到恍然，缺少困惑阶段
- 恍然（段落20）：✅ 主角识破残片真实价值
- 暗爽（段落25）：✅ 反派以为自己赢了，实际是主角的陷阱

# 审查结果
⚠️ emotional_gap: 困惑
建议：在"识破残片"前增加主角的困惑阶段（如"这残片...不对劲？"）
```

### 数据持久化
**用户可见输出**：
- `reviews/review-report.md`：用户可读审查报告
- `tests/*.md`：各类测试报告

**中间数据（`.sumeru/`）**：
- `.sumeru/issues/index.json`：问题索引
- `.sumeru/review/global-issues.json`：全局问题清单
- `.sumeru/review/fix-plan.json`：重写修复计划

### 与其他 Skill 配合
- **前置**：`sumeru-write` 生成的 `chapters/` 和 `sumeru-outline` 的大纲数据
- **后续**：输出供 `sumeru-polish`、`sumeru-finalize` 使用

### 全局约束引用
> 完整全局约束见 `sumeru-rules` 技能，核心要点如下：
> - **子Agent规则**：最多5个并行，每个最多3章
> - **职责边界**：子Agent只读 context pack，输出纯结果+状态标记
> - **状态标记**：输出首行必须包含 `<!-- SUMERU_STATUS: chapter=X, status=Y, ... -->`
> - **Context Pack**：控制在1500-3000中文字，包含审查标准、正文、consistency-rules.json
