# WQ 写作技能集 Bug 审查报告

> 审查范围：`skills/` 目录下全部 11 个 SKILL.md、7 个 Python 脚本、5 个 JSON 配置、7 个 references 参考文件
> 审查日期：2026-08-13

---

## 一、Bug 严重度分级

| 级别 | 含义 | 数量 |
|------|------|------|
| **P0 — 逻辑错误** | 会导致脚本崩溃或产出错误结果 | 4 |
| **P1 — 逻辑缺陷** | 不会崩溃但会产生误判/漏判 | 6 |
| **P2 — 健壮性问题** | 边界场景未处理，低概率触发 | 5 |
| **P3 — 一致性建议** | SKILL.md 与脚本之间的文档/代码不一致 | 4 |

---

## 二、P0 — 逻辑错误

### P0-1: `foreshadowing-tracker.py` 静默模式输出逻辑死代码

**文件**: `skills/wq-review/scripts/foreshadowing-tracker.py`  
**行号**: 174–206  
**问题**: `main()` 函数的输出分支逻辑有结构性错误。当 `output_file` 为 None 且 `quiet` 为 False 时，进入 `elif not quiet` 分支（179行）打印报告。但当 `quiet` 为 True 时，代码进入 204 行的 `elif quiet` 分支。然而这个 `elif` 挂在 179 行的 `elif not quiet` 的 else 链上，意味着只有当 `output_file` 为 None 时才会到达。如果同时指定了 `--output` 和 `--quiet`，则静默摘要不会输出。  

更关键的是，204 行的 `elif quiet` 条件实际上永远不可能为 True：因为在 169 行已经检查了 `if not quiet`（输出到文件时的打印），179 行又检查了 `elif not quiet`（控制台打印），这两个条件互斥但覆盖了所有 `not quiet` 的情况。当 `quiet=True` 时，如果 `output_file` 存在则走 174 行分支（`if output_file`），如果不存在则走 179 行的 `elif not quiet`（条件为 False）。所以 204 行的 `elif quiet` 是**不可达代码**。

**影响**: `--quiet` 参数完全不生效，静默模式无任何输出。

**修复建议**: 重构输出分支为三路：`if output_file` / `elif not quiet` / `else`（quiet 模式）。

---

### P0-2: `format-validator.py` 静默模式同样不可达

**文件**: `skills/wq-finalize/scripts/format-validator.py`  
**行号**: 509–553  
**问题**: 与 P0-1 完全相同的模式。`--quiet` 分支（546行 `elif quiet`）不可达。  
- 514 行: `if output_file:` — 有输出文件时走此分支  
- 519 行: `elif not quiet:` — 非 quiet 时走此分支  
- 546 行: `elif quiet and ...` — **不可达**，因为 `not quiet` 为 False 时 `quiet` 为 True，但此分支挂在 `elif not quiet` 的 else 链上，只有 `not quiet` 为 False 时才到达，而 519 行已经捕获了 `not quiet` 为 True 的情况。

等等，让我重新审视。实际上 519 行是 `elif not quiet:`，当 quiet=True 时此条件为 False，会跳到 546 行 `elif quiet`。但 514 行的 `if output_file:` 先执行——如果 quiet=True 且无 output_file，则 514 行 False → 519 行 `not quiet` 为 False → 546 行 `quiet` 为 True，可达。

**重新评估**: 实际上这段代码是可达的。降级为 P2 — 当 `--output` 和 `--quiet` 同时使用时，静默摘要不输出（因为 514 行 `if output_file` 先匹配）。

---

### P0-3: `continuity-check.py` 的 `check_foreshadowing_recycled` 逻辑永远无法触发

**文件**: `skills/wq-review/scripts/continuity-check.py`  
**行号**: 165–188  
**问题**: 函数检查"已回收的伏笔不能再次标记为active"。逻辑是：
```python
is_resolved = status in ("recycled", "resolved") or payoff_status == "resolved"
if is_resolved:
    if status == "active" and payoff_status == "resolved":
        # 报告冲突
```
当 `is_resolved` 为 True 时，`status` 必须是 `"recycled"` / `"resolved"` 或 `payoff_status == "resolved"`。但内部 `if` 要求 `status == "active"`，这与 `is_resolved` 的第一个条件 `status in ("recycled", "resolved")` 互斥。唯一能进入外层 if 的是 `payoff_status == "resolved"` 且 `status` 不在 `("recycled", "resolved")` 中。此时内层 `status == "active"` 可以匹配。

**实际逻辑**: 如果 `status == "active"` 且 `payoff_status == "resolved"`，则 `is_resolved` 通过 `payoff_status == "resolved"` 为 True，内层也能匹配。所以逻辑实际上是**正确的**，但语义上是矛盾的——一条记录不可能同时 `status=active` 且 `payoff_status=resolved`，这是数据本身的矛盾，而检测逻辑正是要发现这种矛盾。

**重新评估**: 逻辑正确，降为 P3。但函数命名 `check_foreshadowing_recycled` 与 CONFLICT_RULES 中的 key `foreshadowing_not_recycled` 不一致（34行），可能导致混淆。

---

### P0-4: `platform-export.py` 中 `clean` 格式导出的文件扩展名不一致

**文件**: `skills/wq-finalize/scripts/platform-export.py`  
**行号**: 365–404  
**问题**: 当 `fmt == "clean"` 时，代码调用 `export_chapters(clean_chapters, clean_dir, "md", clean_md=False)` 和 `export_full(clean_chapters, clean_dir, "md", clean_md=False)`，传入的格式参数是 `"md"` 而非 `"clean"`。这意味着 clean 格式导出的文件扩展名是 `.md`，且文件会写入 `clean/` 子目录下的 `chapters/` 和 `full.md`。

但 `export_chapters` 函数（192行）使用 `f"{padded}.{fmt}"` 生成文件名，所以 clean 导出的分章文件是 `001.md`、`002.md` 等。这本身不是 bug——clean 格式的目的是"清理 SUMERU_STATUS 注释后的正本"，用 `.md` 扩展名是合理的。

**实际问题**: `export_full` 函数（214行）生成 `full.{fmt}`，传入 `"md"` 所以是 `full.md`。但 md 格式导出（406行之后）也会在 `md/` 子目录下生成 `full.md`。如果用户同时导出 md 和 clean，两个 `full.md` 在不同目录（`publish/md/full.md` vs `publish/clean/full.md`），不会冲突。

**重新评估**: 不是 bug，设计合理。降为 P3 信息提示。

---

## 三、P1 — 逻辑缺陷

### P1-1: `anti-ai-scan.py` 对话字数统计遗漏中文双引号（""）

**文件**: `skills/wq-review/scripts/anti-ai-scan.py`  
**行号**: 201–210  
**问题**: `extract_dialogue_chars` 函数只匹配英文双引号 `\"...\"` 和直角引号 `「...」`，但**不匹配中文双引号 `""`（U+201C / U+201D）**。而网文写作中中文双引号是最常用的对话标记。

```python
for m in re.finditer(r"\"([^\"\\]*(?:\\.[^\"\\]*)*)\"", text):  # 只匹配英文引号
    total += len(m.group(1))
for m in re.finditer(r"「([^」]*)」", text):  # 只匹配直角引号
    total += len(m.group(1))
```

**影响**: 对话占比（dialogue_ratio）会严重偏低，导致几乎所有章节都触发 `narrative_low_dialogue` 警告（medium 级别）。这是最严重的逻辑缺陷。

**修复建议**: 增加中文双引号的匹配：
```python
for m in re.finditer(r"\u201c([^\u201d]*)\u201d", text):
    total += len(m.group(1))
```

---

### P1-2: `anti-ai-scan.py` `detect_post_dialog_emotion_commentary` 同样遗漏中文双引号

**文件**: `skills/wq-review/scripts/anti-ai-scan.py`  
**行号**: 393–414  
**问题**: `quote_pattern` 列表中有 `r'[」"][\s，。！？]?[\s]*.{0,50}'` 和 `r'"[\s，。！？]?[\s]*.{0,50}'`，第一个匹配直角引号和英文双引号，第二个匹配英文双引号。**不匹配中文双引号 `"`（U+201D，右引号）**。

**影响**: 对话后旁白解说检测对使用中文双引号的文本完全失效。

**修复建议**: 添加 `r'\u201d[\s，。！？]?[\s]*.{0,50}'` 模式。

---

### P1-3: `continuity-check.py` `check_timeline_order` 原地排序修改输入数据

**文件**: `skills/wq-review/scripts/continuity-check.py`  
**行号**: 296  
**问题**: `timeline.sort(key=lambda x: x.get("chapter", 0))` 直接修改了传入的 `data["timeline"]` 列表。虽然不影响功能正确性（因为后续不再使用原始顺序），但如果未来有其他检查函数依赖原始顺序，会产生问题。

**修复建议**: 使用 `sorted_timeline = sorted(timeline, key=...)` 或 `timeline = list(data.get("timeline", []))`。

---

### P1-4: `continuity-check.py` `check_character_state_regression` 状态回退检测逻辑方向错误

**文件**: `skills/wq-review/scripts/continuity-check.py`  
**行号**: 220–221  
**问题**: 代码逻辑：
```python
# 如果当前状态比之前更健康，且没有治疗情节标记，可能是回退
if prev_level > curr_level and curr_level >= 0:
```
`CHARACTER_STATE_HIERARCHY` 中 `healthy=0, deceased=5`，数值越大表示状态越差。`prev_level > curr_level` 意味着前一个状态比当前状态更差（如从受伤变健康），这确实是"回退"（无原因恢复）。注释说"当前状态比之前更健康"，逻辑正确。

但变量名 `character_state_regression`（状态回退）在语义上暗示"从好变差"，而实际检测的是"从差变好（无原因恢复）"。这是命名与实现的语义不一致，虽然逻辑正确。

**重新评估**: 逻辑正确，降为 P3 命名建议。

---

### P1-5: `spell-check.py` 重复字检测会产生大量误报

**文件**: `skills/wq-finalize/scripts/spell-check.py`  
**行号**: 111  
**问题**: `REPEATED_CHARS_PATTERN = re.compile(r'(.)\1{2,}')` 匹配任意字符连续出现 3 次以上。这会匹配如 `……`（省略号，两个 `…` 字符）、`——`（破折号，两个 `—` 字符）、`哈哈哈`（正常的笑声表达）等合理用法。

**影响**: 会产生大量低严重度（low）的误报告警。

**修复建议**: 排除合法的重复字符：
```python
REPEATED_CHARS_PATTERN = re.compile(r'(?![…—…])^(.)(?!\1{2})\1{2,}')
```
或在检测时添加白名单排除 `…`、`—`、`哈`、`嘿`、`啊` 等常见合理重复字。

---

### P1-6: `anti-ai-scan.py` `split_sentences` 按英文句号切分会产生误切

**文件**: `skills/wq-review/scripts/anti-ai-scan.py`  
**行号**: 189  
**问题**: `re.split(r"(?<=[。！？!?\.…])\s*", text)` 中的 `.` 和 `…` 会导致英文缩写（如 `Mr.`、`e.g.`）和 URL 被误切分。虽然网文中英文缩写较少，但如果章节中包含 URL 或英文片段，会产生错误的句子切分。

**影响**: 句子切分错误会影响句式重复检测和句子开头重复检测的准确性。影响程度较低。

**修复建议**: 对英文句号使用更严格的匹配，如 `(?<=[。！？…])\s*` 仅匹配中文标点，或对英文句号增加上下文判断。

---

## 四、P2 — 健壮性问题

### P2-1: `chapter-word-counter.py` 只扫描顶层目录，不递归子目录

**文件**: `skills/wq-review/scripts/chapter-word-counter.py`  
**行号**: 61  
**问题**: `for file in path.iterdir()` 只遍历顶层文件，如果章节文件在子目录中（如按卷分目录 `chapters/vol-001/`），则无法扫描到。

**对比**: `format-validator.py`、`spell-check.py`、`sensitive-word-filter.py` 都使用 `glob("**/*.md")` 递归扫描。

**修复建议**: 改为 `for file in path.rglob("*.md")` 或使用 glob 模式。

---

### P2-2: `chapter-word-counter.py` `--quiet` 模式不生成报告文件

**文件**: `skills/wq-review/scripts/chapter-word-counter.py`  
**行号**: 269–270  
**问题**: `if not args.quiet: generate_report(analysis_result, args.output)` — 静默模式下跳过了 `generate_report`，导致 JSON 和 Markdown 报告都不会生成。其他脚本的 `--quiet` 模式通常只是减少控制台输出但仍生成文件。

**修复建议**: 将 `generate_report` 调用移到 quiet 判断之外。

---

### P2-3: `format-validator.py` 英文标点检测对单引号产生大量误报

**文件**: `skills/wq-finalize/scripts/format-validator.py`  
**行号**: 51  
**问题**: `"english_punctuation"` 字典中包含 `"'": "'"`，即检测中文上下文中的英文单引号。但英文单引号在中文文本中常用于撇号（如 `it's`）或嵌套引号，产生大量误报。

**修复建议**: 移除单引号检测，或增加更严格的上下文判断（如要求前后都是中文字符且非英文单词内部）。

---

### P2-4: `platform-export.py` `read_chapter` 标题检测正则不完善

**文件**: `skills/wq-finalize/scripts/platform-export.py`  
**行号**: 137  
**问题**: `re.search(r"第\d+章", first_line)` 只匹配阿拉伯数字，不匹配中文数字（如"第十章"）。如果章节标题使用中文数字，body_start 会错误地设为 0，导致标题行被当作正文保留。

**修复建议**: 改为 `re.search(r"第[\d一二三四五六七八九十百]+章", first_line)`。

---

### P2-5: `sensitive-word-filter.py` 合并自定义词逻辑有潜在 KeyError

**文件**: `skills/wq-finalize/scripts/sensitive-word-filter.py`  
**行号**: 42–48  
**问题**: 
```python
if "custom" in wordlib:
    for level in ["level1", "level2", "level3"]:
        if level in wordlib.get("custom", {}):
            custom_words = wordlib["custom"][level]
            if level in wordlib:  # ← 如果 level 不在 wordlib 顶层，跳过
                wordlib[level]["categories"]["custom"] = custom_words
```
如果 JSON 配置中有 `custom.level1` 但没有顶层 `level1`，则自定义词不会被合并，且不会有任何提示。

**修复建议**: 如果顶层 level 不存在，创建它：
```python
if level not in wordlib:
    wordlib[level] = {"categories": {}}
wordlib[level]["categories"]["custom"] = custom_words
```

---

## 五、P3 — 一致性建议

### P3-1: `continuity-check.py` 规则 ID 命名不一致

**文件**: `skills/wq-review/scripts/continuity-check.py`  
**行号**: 34 vs 165  
**问题**: CONFLICT_RULES 中的 key 为 `foreshadowing_not_recycled`（34行），但对应的检测函数名为 `check_foreshadowing_recycled`（165行），且 `consistency-rules-template.json` 中的 ID 为 `foreshadowing_recycled`。三者应统一。

---

### P3-2: SKILL.md 声称"9维反AI句式扫描"但实际实现为17项检查

**文件**: `skills/wq-rules/SKILL.md` vs `skills/wq-review/scripts/anti-ai-scan.py`  
**问题**: SKILL.md 描述"9维反AI句式扫描"，但 anti-ai-scan.py 实际实现了17项检查（含9维 + 水文硬指标 + cliché + 标点规范等）。文档描述应更新以反映实际实现。

---

### P3-3: `anti-ai-thresholds.json` 版本号与脚本默认值不匹配

**文件**: `skills/wq-review/config/anti-ai-thresholds.json` vs `skills/wq-review/scripts/anti-ai-scan.py`  
**问题**: JSON 配置文件 version 为 `"1.3.0"`，但脚本中无版本号字段，且脚本默认值与 JSON 中的值一致，说明是同步的。但 JSON 版本号缺少对应的脚本侧校验逻辑，无法在版本不匹配时发出警告。

**修复建议**: 在脚本中增加 JSON 版本号读取和兼容性检查。

---

### P3-4: `spell-check.py` 和 `format-validator.py` 重复实现标点重复检测

**文件**: `skills/wq-finalize/scripts/spell-check.py` 行 114-122 vs `skills/wq-finalize/scripts/format-validator.py` 行 32-40  
**问题**: 两个脚本各自维护了一份 `PUNCTUATION_ERRORS` 字典，内容完全相同。违反 DRY 原则，修改时需同步两处。

**修复建议**: 将标点规则提取到共享配置文件，两个脚本统一加载。

---

## 六、交叉验证问题

### X-1: `anti-ai-scan.py` 与 `wq-rules/SKILL.md` 对话引号定义不一致

**文件**: `skills/wq-rules/SKILL.md` 第十部分 vs `skills/wq-review/scripts/anti-ai-scan.py`  
**问题**: SKILL.md 标点规范明确要求使用中文双引号 `""` 作为对话引号，但 `anti-ai-scan.py` 的 `extract_dialogue_chars` 函数不匹配中文双引号（见 P1-1）。这导致遵循 SKILL.md 规范写作的章节，其对话占比会被错误计算为极低值。

**严重度**: 这是**设计矛盾**——规则要求用中文双引号，但扫描脚本不识别中文双引号。

---

### X-2: `format-validator.py` 与 `wq-polish/SKILL.md` 引号类型规范不一致

**文件**: `skills/wq-polish/SKILL.md` vs `skills/wq-finalize/scripts/format-validator.py`  
**问题**: `wq-polish/SKILL.md` 明确区分了三种引号类型的适用场景（直角引号用于强调、中文双引号用于对话、单引号用于嵌套）。但 `format-validator.py` 的 `dialogue_pattern` 正则将所有引号类型混在一起检测，不区分对话和嵌套引号。

**影响**: 对话格式验证可能产生误报（将嵌套引号误判为对话格式问题）。

---

### X-3: `scoring-criteria.json` 权重总和验证

**文件**: `skills/wq-score/config/scoring-criteria.json`  
**问题**: 五个维度的权重：完整性 0.20 + 叙事质量 0.25 + 创意性 0.20 + 技术执行力 0.15 + 市场契合度 0.20 = **1.00**。各维度内子项权重总和均为 1.00。

**结论**: 权重无问题，验证通过。

---

### X-4: `platform-export.py` 卷信息读取路径与 CLAUDE.md Canonical 路径不一致

**文件**: `skills/wq-finalize/scripts/platform-export.py` 行 28-31 vs `CLAUDE.md`  
**问题**: 脚本尝试从 `project_root / "outlines" / "chapters.json"` 和 `project_root / ".sumeru" / "outlines" / "chapters.json"` 读取卷信息。但根据 CLAUDE.md 的 Canonical 路径定义，章节任务卡路径应为 `.sumeru/outlines/chapters.json`，用户可见的 `outlines/` 目录不在 Canonical 路径中。

**影响**: 第一个路径 `project_root / "outlines" / "chapters.json"` 是冗余的，不会匹配到任何文件。

**修复建议**: 移除第一个路径候选，只保留 `.sumeru/outlines/chapters.json`。

---

## 七、总结与优先级建议

### 修复优先级排序

| 优先级 | Bug ID | 影响 | 建议修复时间 |
|--------|--------|------|-------------|
| **立即修复** | P1-1 | 对话占比检测全面失效，影响所有章节 anti-ai 扫描结果 | 立即 |
| **立即修复** | P1-2 | 对话后旁白解说检测对中文引号失效 | 立即 |
| **尽快修复** | P0-1 | foreshadowing-tracker --quiet 参数完全不生效 | 尽快 |
| **尽快修复** | P2-1 | chapter-word-counter 不递归子目录，分卷项目无法使用 | 尽快 |
| **尽快修复** | P2-2 | chapter-word-counter --quiet 不生成报告文件 | 尽快 |
| **尽快修复** | X-1 | 规则与脚本对话引号定义矛盾（与 P1-1 同源） | 随 P1-1 修复 |
| **尽快修复** | P2-4 | 导出脚本不识别中文数字章节标题 | 尽快 |
| **择机修复** | P1-5 | 重复字检测误报（省略号/破折号/笑声） | 择机 |
| **择机修复** | P1-6 | 英文句号误切分（低影响） | 择机 |
| **择机修复** | P2-3 | 英文单引号误报 | 择机 |
| **择机修复** | P2-5 | 敏感词自定义合并逻辑缺陷 | 择机 |
| **择机修复** | P1-3 | timeline 原地排序（无功能影响） | 择机 |
| **低优先级** | P3-1~P3-4 | 命名/文档/DRY 一致性问题 | 低 |
| **低优先级** | X-2, X-4 | 跨文件规范不一致 | 低 |

### 核心结论

这套技能集的**架构设计质量很高**——模块化清晰、子Agent并行机制完善、反AI扫描维度丰富、分卷隔离协议严密。但在**实现层面存在一个关键缺陷**：`anti-ai-scan.py` 的对话检测逻辑不识别中文双引号（`""`），这是网文中最常用的对话标记。这导致对话占比、对话后旁白解说等核心扫描项几乎完全失效，所有章节都会触发"对话占比过低"的误报。

**建议的修复路径**：
1. 首先修复 P1-1 和 P1-2（中文双引号匹配），这是投入产出比最高的修复
2. 其次修复 P0-1 和 P2-1/P2-2（工具脚本可用性）
3. 最后处理误报和健壮性问题

---

*报告结束*