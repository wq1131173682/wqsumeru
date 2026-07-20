# Changelog

## 1.3.7 (2026-07-20)

### 标点符号规范体系：10类检测规则 + 全链路集成

> **背景**：AI 生成小说正文存在系统性标点问题——破折号滥用做简单承接、省略号格式混乱、感叹号堆叠制造虚假戏剧感、中英文标点混排。原有脚本仅检测重复标点和英文标点占比，覆盖面严重不足。本次新增 10 类标点检测规则，从检测脚本到 SKILL.md 规则文件全链路集成。

**改动**（9 个文件，+720 −26 行）：

- **A. `anti-ai-scan.py` 新增 3 维标点检测**（+164 行）
  - `detect_em_dash_abuse()`：破折号密度检测（≥5/千字触发 medium）+ 简单承接型误用检测（`——是/有/在/这/那` 等模式，≥3 处触发 medium）
  - `detect_ellipsis_format()`：英文 `...` → `……`、单 `…` → `……`、`……。` 去多余句号
  - `detect_exclamation_abuse()`：`！！！`→`！`、`？？？`→`？`、`！？`/`？！` 混合叠用 + 感叹号密度（≥3/千字触发 medium）
  - `anti-ai-thresholds.json` 新增 5 项阈值（版本升至 v1.3.0）

- **B. `format-validator.py` 新增 4 个验证函数**（+255 行）
  - `validate_punctuation_space()`：标点前后多余空格检测
  - `validate_quote_closure()`：中文双引号 `""` 和直角引号 `「」` 未闭合检测
  - `validate_book_title_marks()`：书名号 `《》` 闭合 + 英文 `<>` 误用检测
  - `validate_punctuation_format()`：省略号/破折号/括号格式标准化 + 闭合检测
  - `validate_punctuation()` 改进：从"占比 >1%"粗略检测改为"中文标点前后有中文字符"精确检测

- **C. `spell-check.py` 严重度统一**
  - 标点重复检测严重度从 `low` → `medium`，与 `format-validator.py` 保持一致

- **D. `sumeru-rules/SKILL.md` 新增第六点五部分：标点符号规范**（+77 行）
  - 10 个子章节：破折号、省略号、感叹号问号、中英文混排、标点空格、引号闭合、书名号、括号、顿号逗号边界、脚本检测阈值
  - 作为全局标点规范的唯一权威来源

- **E. 标点规范向下游 Skill 传播**
  - `sumeru-write/SKILL.md`：反AI自检清单新增标点检查项
  - `sumeru-polish/SKILL.md`：新增标点符号润色规范（不受"禁止标点规范化"约束）
  - `subagent-rules.md`：新增标点符号规范（强制），子Agent写作/润色时必须执行

- **F. 文档同步**
  - `README.md`：版本升至 v1.3.7，新增更新条目，finalize 功能描述补充 10 类标点检测
  - `QWEN.md`：format-validator.py 描述更新，anti-ai-scan.py 描述补充 3 维标点检测
  - `sumeru-finalize/SKILL.md`：版本升至 v1.2.2，标点规范引用更新
  - `sumeru-review/SKILL.md`：type 枚举扩展、自动修复表扩充、脚本扫描描述更新

**未破坏项**：
- 原有标点重复检测和英文标点检测逻辑保留，新增检测为增量
- JSON 配置无配置文件时使用内置默认值，向后兼容
- `spell-check.py` 严重度调整不影响已有调用方逻辑

---

## 1.3.6 (2026-06-08)

### 反 AI 扫描第 9 维：对话后旁白解说检测

> **背景**：对话已表达情绪后，叙述用散文"翻译"同一情绪（如"你给我滚！"他愤怒地说），是 AI 最典型的行为模式之一。

**改动**：
- `anti-ai-scan.py` 新增 `detect_post_dialog_emotion_commentary()` 检测函数
- 阈值 ≥ 3 处触发 medium 级 polish
- 8 维 → 9 维反 AI 句式扫描
- 水文硬指标编号顺延 9-15 → 10-16

---

## 1.3.5 (2026-06-08)

### 技能生态优化：Token 精简 + OCR 错字根除 + JSON 配置外置

> **背景**：v1.3.4 修复了模板化套用问题，但技能体系仍有冗余章节、残余 OCR 错字和硬编码配置。本次集中清理存量技术债，将可配置参数外置为零外部依赖的 JSON 文件，降低维护成本。

**改动**（17 个文件，+397 −382 行）：

- **A. `sumeru-rules/SKILL.md` 精简冗余章节**（−120 行）
  - 删除 §四·三「Context Pack 通用模板」（各技能格式已在对应 SKILL.md 中定义）
  - 删除 §八「各 Skill 子Agent职责明细」（与 §一·技能清单重复，子Agent I/O 见各 SKILL.md）
  - 删除 §十五「脚本索引」（脚本注册信息已在各 SKILL.md 中内联）
  - 同步修复 OCR 残存错字 15+ 处：`相全→相关`、`目当→目录`、`人物单→人物卡`、`内定→内容`、`简从→简介`、`世界规→世界观`、`机时→无`、`汇态→汇总`、`生或→生成`、`边略→边界`、`备从→备份`、`课自→一致`、`结就→结局`、`确设→确认`
  - 调用链路图从 ASCII 方块简化为纯文本箭头链
  - 删除「用户可见文件」表（信息冗余）
  - `migrationHandoff` 取值注释同步：`inferred`→`pending`、`failed`→`skipped`

- **B. 反 AI 检测配置外置 JSON**（2 个新文件）
  - 新增 `skills/sumeru-review/config/anti-ai-thresholds.json`：20 项阈值集中定义，`anti-ai-scan.py` 启动时自动加载，无此文件时使用代码内置默认值
  - 新增 `skills/sumeru-review/config/cliche-blacklist.json`：8 分类 80+ 词条，`anti-ai-scan.py` 启动时自动加载，无此文件时使用内置黑名单
  - `anti-ai-scan.py`（−163/+163 行）：移除硬编码的全局阈值和 CLICHE_BLACKLIST 列表，改为 `_load_thresholds()` / `_load_cliches()` 动态加载
  - 参数示例：章节目录参数从 `./chapters/` 更新为 `.sumeru/chapters/`（与规范路径对齐）
  - `chapter-word-counter.py`：`--dir` 默认值同步为 `.sumeru/chapters/`

- **C. 拼写词典外置 JSON**（2 个新文件）
  - 新增 `skills/sumeru-finalize/config/spell-dict.json`：拼写检查词典（~30 条目），`spell-check.py` 启动时加载
  - 新增 `skills/sumeru-finalize/config/sensitive-words.json`：敏感词库（~7 条目），`sensitive-word-filter.py` 启动时加载
  - `spell-check.py`（−169/+169 行）：重写加载逻辑，从硬编码内置词典改为 JSON 配置 + 内置后备
  - `sensitive-word-filter.py`：敏感词加载逻辑同步外置
  - `format-validator.py`：修复硬编码单引号语法错误

- **D. `sumeru-migrate/SKILL.md` 接续协议状态简化**（−70/+70 行）
  - `inferred` → `pending`：更清晰表达"待处理"语义
  - `failed` → `skipped`：消除"错误"歧义，反映用户主动跳过的本质
  - `校对完成` → `confirmed`：与 anchorStatus 统一命名
  - 同步更新 worldbuilder 中的字段处理细则（`failed` 状态处理行移除）
  - 同步更新 sumeru-rules 中的字段状态表

- **E. `sumeru-worldbuilder/SKILL.md` 流程增强**
  - 阶段顺序增加 `migrate?` 前缀标记：`[migrate? →] init → topic → outline → intro → anchor → write → review → fix → polish → finalize → build/release`
  - Skill 协调流程同步增加 `[migrate? →]` 前缀
  - 删除 `failed` 状态处理行（接续状态已简化为三态：pending/confirmed/skipped）

- **F. 技能版本统一**（新增 + 关联同步）
  - `sumeru-topic`：1.2.0 → **1.2.1**（触发：部分 rules 引用路径修正）
  - `sumeru-polish`：1.2.0 → **1.2.1**（触发：反 AI 引用路径修正 + context pack 引用同步）
  - `sumeru-finalize`：1.2.0 → **1.2.1**（触发：spell-check.py / sensitive-word-filter.py 重构）
  - 其他已为 v1.2.1+ 的 skill 未动

**未破坏项**：
- 9 个 skill 的协议层（接续协议、targetChapter、protectedTag、风格样本自动分析）均保留
- 所有 Python 脚本编译通过（6 个脚本全部验证）
- 内置默认值与旧硬编码阈值一致，无 JSON 配置时行为不变
- 无外部依赖引入（配置加载使用 `json.loads()` 标准库）

**遗留**（建议后续清理）：
- `format-validator.py` `--chapter-dir` 默认值仍指向 `./chapters/`（需与 other 脚本对齐）
- `anti-ai-scan.py` `cliche_hit_threshold` 在阈值 JSON 中配置但未被 Python 脚本实际使用（stub 预留）
- `platform-export.py` 仍有零散调试注释待清理
- long/full 模式的 context-packs 和 continuity 自动补齐仍有未覆盖场景（见 migrate §未覆盖场景）

### 元数据同步：README.md 同步到 v1.3.5

**改动**：
- 顶部版本状态行：`v1.3.4` → `v1.3.5`，日期 `2026-06-05` → `2026-06-08`
- 🆕 最新更新 段补 v1.3.5 条目

---

## 1.3.4 (2026-06-05)

### 质量优化：反 AI 扫描闭环套用模板问题

> **背景**：v1.3.3 修复了"水文"问题（套用低质量填充），但仍有 7 类"套用模板"维度未覆盖：段间 micro-arc 模板、中观结构指纹、对话标记词重复、情绪标签定语、战斗模板、转折模板、推进行为序列。本版本终结模板化套用。

**改动**：

- **A. 扩展 `skills/sumeru-review/scripts/anti-ai-scan.py`（570 → 660 行）**
  - **新增检查 7：段间 micro-arc 模板**
    - 段落四象限分类：A=推进 / B=心理 / C=描写 / D=对话
    - 滑动窗口 4 段生成结构指纹（如 "ABCD"）
    - 同一指纹在 8+ 段章节中出现 ≥ 2 次即命中（medium）
    - 典型命中："动作-心理-环境-对话"机械循环、对话段连用（DDDD）
  - **新增检查 8：对话标记词集中度**
    - 统计 30+ 对话标记动词（说/道/问/答/喝道/笑道/叹道/低声道/沉声道…）
    - 最高频标记词占比 > 80% 且总标记 ≥ 5 即命中（medium）
    - 典型命中：全章"XX说："机械重复（"说" 100% 集中度）
  - **Cliché 黑名单扩展（40+ → 80+ 词条）**
    - 战斗套路：数百回合 / 数十回合 / 你来我往 / 不分胜负 / 势均力敌 / 棋逢对手…
    - 转折模板：然而就在这时 / 说时迟那时快 / 话音未落 / 不料 / 岂料 / 刹那间…
    - 情绪标签：愤怒的他 / 温柔的眼眸 / 紧握的拳头 / 心中充满了 / 不禁感到…
  - markdown 报告表头加 `micro-arc` + `dialog_marker` 两列
  - 阻断规则**不变**（micro_arc / dialog_marker 留 medium 灰度观察一轮）

- **B. `sumeru-rules/SKILL.md` 第十部分·三 同步**（v1.2.2 → v1.2.3）
  - 6 维反 AI → 8 维反 AI（B 表加 7/8 两行）
  - 9 项水文硬指标 → 11 项（编号顺延 2，加 micro_arc + dialog_marker）
  - 处理策略 D 节加 v1.2.3 灰度说明：新检查留 medium 不进阻断
  - cliché 黑名单行加 "v1.2.3 增战斗套路 + 转折模板 + 情绪标签" 注释

- **C. `sumeru-review/SKILL.md` 反 AI 扫描节同步**（v1.2.1 → v1.2.2）
  - 扫描项表 15 → 17 项（加 micro_arc / dialog_marker）
  - 维度声明「6 维」→「8 维」
  - 阻断规则下加 v1.3.4 灰度说明 + 第 4 条父 Agent 处理（micro_arc 修复方式：重排段落顺序或调换段间衔接，非插入内容）

**验证**（4 章测试样例 + v1.3.3 旧样例 5 章）：

| 测试章节 | 命中项 |
|----------|--------|
| ch020 (micro_arc test) | `anti_ai_micro_arc_repeat` × 3（DDDD 指纹）+ cliché × 9 |
| ch021 (dialog_marker test) | `anti_ai_dialog_marker_dominant`（"说" 100% 集中度 20/20）|
| ch022 (cliche 扩展 test) | `water_text_cliche_density` × 18（新增：你来我往/不分胜负/数百回合/数十回合/愤怒的他/然而就在这时…）|
| ch023 (干净) | 仅 2 LOW + 1 MEDIUM 短章主谓宾阈值误判（v1.3.4.1 候选）|

总计 9 章 / 31 项问题 / 4 high 阻断 / 退出码 2。

**未破坏项**：
- 9 个 skill 的协议层（接续协议、targetChapter、protectedTag、风格样本自动分析）未动
- Python 脚本（`continuity-check.py` / `foreshadowing-tracker.py` / `chapter-word-counter.py`）未动
- sumeru-topic / sumeru-worldbuilder / sumeru-outline / sumeru-migrate / sumeru-polish / sumeru-finalize 未动
- v1.3.3 引入的 anti-ai-scan.py 主框架 + 阻断规则（11/12/14 旧编号 → 现 12/14/17）未动

**遗留**（建议后续清理）：
- 项目级 `cliche-blacklist.json` 扩展机制（v1.3.5 候选）
- 内心独白识别为粗略正则，复杂句式可能误判
- 短章（< 800 字）主谓宾阈值 6 略严，建议加字数门控（v1.3.4.1 候选）
- micro_arc / dialog_marker 灰度观察一轮后决定是否升级为 high 阻断

### 元数据同步：README.md 同步到 v1.3.4

**改动**：
- 顶部加版本状态行：`v1.3.4 · 2026-06-05 · 完整变更: CHANGELOG.md`
- 🆕 最新更新 段补 v1.3.4 条目

---

## 1.3.3 (2026-06-05)

### 质量优化：反水文扫描脚本 + 内部矛盾修复

> **背景**：审计发现仓库中"反 AI 句式扫描"在 `sumeru-rules/SKILL.md` 第十部分有完整规范但**无任何脚本实现**；`sumeru-review/SKILL.md` L116 字数自动修复逻辑直接"插入 2-4 段感官细节/内心独白/场景描写"，与 `sumeru-write/SKILL.md` L154「自然展开」原则直接矛盾，是**唯一主动生产水文的 skill 条款**。本版本终结"文档规范 vs. 实际行为"两层皮。

**改动**：

- **A. 新增 `skills/sumeru-review/scripts/anti-ai-scan.py`（560 行）**
  - 实现 sumeru-rules/SKILL.md 第十部分·三 的 6 维反 AI 句式扫描
    - 句式重复（连续 6+ 句主谓宾完整）
    - 段内开场重复（连续 3 句同主语）
    - 连续推进无缓冲（连续 3 段无描写/无动作）
    - 批内开场雷同（相邻章首 8 字重复）
    - 批内钩子雷同（相邻章末 8 字重复）
    - 字数波动（批均值 ±50%）
  - 扩展 sumeru-write/SKILL.md §叙事效率通用自检 的 5 项硬指标
    - 对话占比 < 5%（medium）
    - 内心独白占比 > 10%（medium）
    - **纯描写段落占比 > 35%（high 阻断）**
    - **核心事件数 < 1（high 阻断）**
    - 时间/场景切换 = 0（medium）
  - 新增 Cliché 黑名单 40+ 短语（景色/表情/外貌/动作/句式 5 大类）
  - 新增场景类型占比检查（日常/过渡 > 30% flag）
  - 输出 `.sumeru/review/anti-ai-report.json` + `.md`
  - 退出码：`0`=无问题 / `1`=warning / `2`=critical 或含阻断
  - 支持 `--quiet` / `--strict` / `--outlines` / `--filter`
  - 纯标准库，零外部依赖

- **B. 修复 `sumeru-review/SKILL.md` L116 内部矛盾**（v1.2.0 → v1.2.1）
  - 删除「字数不足 → 插入 2-4 段感官细节/内心独白/场景描写」自动修复逻辑
  - 改为：调用 `anti-ai-scan.py` 量化报告 + 将 `word_count_short` 写入 `fix-plan.json`，由 write 阶段在当前场景中"自然展开"补足
  - 新增「反 AI / 反水文扫描」整节：扫描入口、扫描项表、阻断规则、quiet 模式输出约定

- **C. `sumeru-rules/SKILL.md` 第十部分·三 处理策略升级**（v1.2.1 → v1.2.2）
  - 旧策略："`anti-ai-flagged` 章节 → 记录到 changelog，不阻塞"
  - 新策略：**分层处理**
    - high 阻断（9/10/12 任一）→ 写 fix-plan `type=anti_ai_blocked`，触发 write 重写
    - medium（1/2/5/7/8/11/13 任一）→ **自动触发 polish 轻量级**（不再仅 changelog）
    - low（3/4/6 任一）→ 写 changelog，留待 polish 中度
  - 新增「水文硬指标」表（7 项），与脚本阈值完全对齐
  - 旧路径 `.sumeru/write/anti-ai-report.json` 已废弃，新路径 `.sumeru/review/anti-ai-report.json`

- **D. `sumeru-write/SKILL.md` 写后自检强化**（v1.2.1 → v1.2.2）
  - 「叙事效率通用自检」加 v1.2.2 强约束声明：5 项检查**必须**通过 `anti-ai-scan.py` 量化执行，子 Agent 不可仅凭经验主观判断
  - 「父Agent在子Agent写入**后**必须执行」第 3 步：明确调用命令、退出码语义、阻断时父 Agent 行为契约
  - 明确禁止父 Agent 用"插入 2-4 段描写"方式补字数或绕过阻断

**未破坏项**：
- 9 个 skill 的协议层（接续协议、targetChapter、protectedTag、风格样本自动分析）已就位，未动
- Python 脚本（`continuity-check.py` / `foreshadowing-tracker.py` / `chapter-word-counter.py`）未动
- sumeru-topic / sumeru-worldbuilder / sumeru-outline / sumeru-migrate / sumeru-polish / sumeru-finalize 未动

**遗留**（建议后续清理）：
- Cliché 黑名单为静态内置，v1.3.4 计划支持项目级 `cliche-blacklist.json` 扩展
- 内心独白识别为粗略正则，复杂句式可能误判（影响极小，不阻塞）
- 场景类型识别依赖 `outlines/chapters.json` 的 `sceneType`/`rhythm` 字段；缺失时跳过该检查

### 元数据同步：README.md 同步到 v1.3.3

**改动**：
- 顶部加版本状态行：`v1.3.3 · 2026-06-05 · 完整变更: CHANGELOG.md`
- 🆕 最新更新 段补 v1.3.3 条目

## 1.3.2 (2026-06-05)

### 质量优化：OCR 错别字全面校对 + scripts-lib 死代码清理

**改动**：

- **A. OCR 错别字全面校对**（30+ 处）
  - `sumeru-topic/SKILL.md`：**整文件重写**（94 行）。修复 20+ 处 OCR 错字与缺失换行，包括：`调生→调用`、`提参→提取`、`废查/废片→废柴`、`执必→执念`、`设实→设定`、`驱功→驱动`、`情感键→情感锚`、`金手持→金手指`、`矛目→矛盾`、`名场面种字→名场面种子`、`价值冲窗→价值冲突`、`启生→启用`、`闭嘉→闭嘴`、`底约→底线`、`稀里遗忘→悄然遗忘`、`调试生→调试用`、`为师父复件→为师父复仇`、`本之的→本作品的`、`父Agent件→父 Agent 从`、`更文→更新`、`项目初始化协认→项目初始化协议`、`缺小→缺失`、`判文→判断`、`写出→写入`等
  - `sumeru-worldbuilder/SKILL.md`：**整文件重写**（236 行）。修复 ~30 处 OCR 错字与缺失换行，包括：`调生→调用`（6+ 处）、`提参→提取`、`废查/废片→废柴`、`执必→执念`、`设实→设定`、`驱功→驱动`、`情感键→情感锚`、`金手持→金手指`、`矛目→矛盾`、`名场面种字→名场面种子`、`价值冲窗→价值冲突`、`启生→启用`、`闭嘉→闭嘴`、`回到天前→回到前一天`、`底约→底线`、`稀里遗忘→悄然遗忘`、`调试生→调试用`、`为师父复件→为师父复仇`、`冷幽默暗黑童话意→冷幽默暗黑童话调`、`本之的→本作品的`、`反实→反审`、`写关→写入`、`判文→判断`、`缺小→缺失`、`更文→更新`、`章以不→章以上`、`总结：*→总结：**`、`写作不..→写作中...`、`交互式需求引对→交互式需求引导`、`节好爽文→快节奏爽文`、`❤→✗` 等
  - `sumeru-migrate/SKILL.md`：修复 2 处（`不一自→不一致`、`更文→更新`，共 §97 §110）
  - `sumeru-outline/SKILL.md`：修复 8 处（`差异化锚点*→：`、`起点状态*→：`、`终点状态*→：`、`核心驱动力- →核心驱动力 + 换行`、`本么→本书`、`述年→近年`、`黑衣人）→黑衣人？`、`锚点检查*→：`、`金手指是否有代价/限制（不能无敌））→金手指是否有代价/限制（不能无敌）`）
  - `sumeru-rules/SKILL.md`：修复 5 处（`金手指变作→金手指变式`、`状态更文→状态更新`、`不碰状态文从→不碰状态文件`、`执行并回写*→执行并回写：`、`待定项判文→待定项判断`、`待定项处理建设→待定项处理建议`）
  - 全部 skill frontmatter 未动
  - 保留所有 v1.3.0 / v1.3.1 已加入的协议（H1-H6、targetChapter、protectedTag、风格样本自动分析等）

- **B. scripts-lib 死代码清理**
  - 验证：grep 全 9 个 skill，确认 `scripts-lib/sumeru_utils.py` 0 引用、`scripts-lib/resume_check.py` 0 引用
  - 操作：删除 `skills/scripts-lib/` 整个目录（2 个 Python 文件）
  - 不影响 CLAUDE.md（CLAUDE.md 引用为概念性提及，无具体路径）

- 不破坏项：
  - 9 个 skill 的协议层（接续协议、targetChapter、continuity）已就位
  - Python 脚本（`continuity-check.py` / `foreshadowing-tracker.py` / 4 个 finalize 脚本）均未动
  - sumeru-worldbuilder 的「接续协议」节、sumeru-topic 的「与 worldbuilder 关系」节（m0118）均保留
  - medium/standard 模式补创 continuity 的协议（m0088）保留

**遗留**（建议后续清理）：
- sumeru-rules 内部仍有 ~5 处 typo（行 165/178 等"备份则→备份至"、"返因→返回"、"汇态→汇总"等），因属长期 canonical 文件，未在本轮彻底处理
- sumeru-outline 头部 113-130 行（人物卡模板）仍有几处 OCR 拼接错（如 "）- **年龄**）"），影响小

### 元数据同步：README.md 同步到 v1.3.2

**改动**：
- 顶部加版本状态行：`v1.3.2 · 2026-06-05 · 完整变更: CHANGELOG.md`
- 加 `🆕 最新更新` 段（v1.3.0 / v1.3.1 / v1.3.2 三条）
- "8 个独立 Skill 模块" → **9 个**（含 sumeru-migrate）
- 核心特性补"项目接续"条（H1-H6 接续协议）
- 定位描述补"迁移"到流程：迁移 → 选题 → 大纲 → 写作 → 审稿 → 润色 → 导出
- 最后更新日期 2026-05-29 → 2026-06-05
- sumeru-migrate §7 描述补 v1.3.0 接续协议说明
- 子模式注释补"含接续协议"提示

## 1.3.1 (2026-06-05)

### 新增：剧情一致性 + 文笔丰富优化包（用户硬约束）

> **背景**：用户提出"在保证剧情一致性和文笔丰富的基础上,有没有什么优化方案"。经审计发现,代码库中 80% 优化目标（`continuity-check.py` / `foreshadowing-tracker.py` / `consistency-rules.json` / `style-samples/` 模板）已存在,主要问题是**接缝未连**。
>
> 本次为接缝优化,非新建。**无新增 Python 脚本**,复用 `sumeru-review/scripts/continuity-check.py`（450 行）与 `foreshadowing-tracker.py`（211 行）。

**改动**：

- `sumeru-worldbuilder` (v1.2.1 → v1.2.2)
  - **模式初始化表**：medium/standard 模式补创 `.sumeru/continuity/consistency-rules.json`（空 schema）；long/full 行移除 `continuity/`
  - **模式升级协议**：medium → long 升级清单移除 `continuity/`（已在 medium 阶段创建）
  - **创意锚点 附加字段**：新增 `targetChapter`（名场面种子,可选）/ `protectedTag`（全部,可选）字段定义

- `sumeru-write` (v1.2.0 → v1.2.1)
  - **剧情统一门禁 写前步骤**：新增 2 条
    - 伏笔活跃度预检：调用 `foreshadowing-tracker.py --quiet` 把逾期伏笔注入 `shared-write.md`
    - 锚点临近检查：找出 `targetChapter` 距当前章 ≤ 3 的名场面种子,提示"请在本章或近期兑现 XX"
  - **剧情统一门禁 写后步骤**：增量更新逻辑
    - 解析 `SUMERU_STATUS.plot_update.foreshadowing`,同步写 `consistency-rules.json` 的 `last_mentioned` + `mentionCount`
    - 可选调用 `continuity-check.py --quiet`,critical 冲突立即报出

- `sumeru-outline` (v1.2.0 → v1.2.1)
  - **风格样本自动分析**：检测到 `style-samples/user-sample-*.md` 时,父 Agent 按 6 维度分析并填充 `user-style.md` 的"待分析"占位；后续作为 context pack 固定组成部分

**不破坏项**：
- `user-style.md` 首次生成后保留手动修改,后续不覆盖
- 现有 `continuity-check.py` / `foreshadowing-tracker.py` 无需修改
- 现有 `consistency-rules.json` schema 不变（仅使用 `last_mentioned` 字段,该字段已在 `sumeru-rules/SKILL.md` §consistency-rules.json 格式 定义）
- 用户未提供样本时,user-style.md 保持"待分析"状态,以 `plan.md.creativeStrategy` 兜底

### 同步：SKILL.md frontmatter 版本号（2026-06-05）

本次同步将以下 skill 的 frontmatter `version` 字段与 CHANGELOG 对齐：

- `sumeru-worldbuilder`：1.2.0 → **1.2.2**（handoff v1.2.1 + continuity v1.2.2）
- `sumeru-rules`：1.2.0 → **1.2.1**（handoff 字段索引）
- `sumeru-write`：1.2.0 → **1.2.1**（continuity 增量 + 写前预检）
- `sumeru-outline`：1.2.0 → **1.2.1**（风格样本自动分析）
- `sumeru-migrate`：1.2.0 → **1.3.0**（已在 v1.3.0 release 同步过）
- 其余 4 个 skill（topic / review / polish / finalize）保持 1.2.0，本次未做改动

注：本仓库采用"每 skill 独立版本号" + "CHANGELOG 顶层 release 标签"双重版本管理。各 skill `version` 反映该 skill 自身的演进，CHANGELOG 顶层 vX.Y.Z 反映一次发布的整体编号。

## 1.3.0 (2026-06-05)

### 新增：sumeru-migrate 接续协议（Handoff Protocol）

**问题**：v1.2.0 起 `sumeru-worldbuilder` 增加了 `anchor` 阶段（创意锚点）和强化了 `intro.md` 必填项，但 `sumeru-migrate` 仅完成"文件规整"就结束，迁移后的项目进入 `worldbuilder 恢复` 时会因缺失 `creative-anchors.md` / `intro.md` / `migrationHandoff` 标记而失准。

**改动**：

- `sumeru-migrate` (v1.2.0 → v1.3.0)
  - 新增「第十一、接续协议」章节：
    - H1: 推断补做 `.sumeru/creative-anchors.md`（从 plan.md + outline.md 推断 5-7 个锚点，全部标记 `inferred`）
    - H2: 推断补做 `.sumeru/intro.md`（从 plan.md 提取四要素，生成 300-500 字简介）
    - H3: 写入 `.sumeru/status.json.migrationHandoff` 字段（version / migratedAt / fromVersion / anchorStatus / introStatus / recommendedNext）
    - H4: 初始化 `.sumeru/context-packs/`（仅 long/full）
    - H5: 重建 `.sumeru/continuity/consistency-rules.json`（仅 long/full）
    - H6: 补全 `chapters/*.md` 缺失的 `SUMERU_STATUS` 标记
  - 迁移流程增加「第五阶段：接续准备」
  - 检查清单增加 1.8「接续文件检查」
  - 迁移报告增加「续作建议」段，输出明确的 `/sumeru-worldbuilder 恢复上次创作` 命令
  - 完整迁移模式必出接续协议；`仅检查` / `仅迁移路径` / `补齐配置` / `补齐人物卡` 模式可省略
  - 接续状态分级：`ready` / `partial` / `failed`，对应不同的恢复提示

- 关联：sumeru-worldbuilder 后续应增加 `migrationHandoff` 字段检测逻辑
  - 跳过 topic / outline 阶段（已完成）
  - 按 anchorStatus / introStatus 决定是否进入确认流程
  - 详见 migrate/SKILL.md §11.8「与 worldbuilder 的接力协议」

### 新增：sumeru-worldbuilder 迁移接续对端实现

**改动**：

- `sumeru-worldbuilder` (v1.2.0 → v1.2.1)
  - 新增「项目恢复与迁移接续协议」章节：
    - 入口检测三态：`migrationHandoff` 存在 / 仅 `migration.json` 存在 / 都没有
    - 接续模式字段处理细则：`anchorStatus` / `introStatus` 各 4 个取值对应的 worldbuilder 行为
    - `recommendedNext` 字段：默认 `/sumeru-worldbuilder 恢复上次创作`，其他值原样输出不替用户决定
    - 字段正交性：`migrationHandoff` 只增不改，不参与 `currentStage` 流转
    - 审计：每次接续动作追加一条到 `.sumeru/changelog.md`
  - 与 `sumeru-migrate` v1.3.0 形成闭环

- `sumeru-rules` (v1.2.0 → v1.2.1)
  - 状态机章节追加「状态字段语义对照」表：
    - `currentStage` / `chapterStatus.<n>` / `migrationHandoff` 三字段
    - 标注 `migrationHandoff` 为「只增不改」字段，指向 migrate §11.5 和 worldbuilder §项目恢复与迁移接续协议

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
