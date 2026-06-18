---
name: sumeru-write
description: 小说章节内容创作与创意落地
version: 1.2.2
type: skill
argument-hint: '[章节号] ["章节概要"] [风格] [字数] [节奏] [视角] [续写/按细纲生成]'
disable-model-invocation: false
user-invocable: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, task
context: project
agent: build
---

> 依赖 `sumeru-rules`，默认`quiet` 模式。

## 网文章节撰写

### 触发关键词
写第X章、续写、续写接下来的内容、扩写这段、重写这一章、批量写网文章节、批量生成小说章节、写个开篇章节、写个高潮情节、从细纲生成章节、按细纲写小说、批量生成所有章节、细纲驱动写作、生成XX情节、帮我写个XX情节

> **与 sumeru-worldbuilder 的区别**：write 负责具体的章节写作操作（写一章、续写、扩写、重写、批量生成）。用户说"帮我写小说"且未指定具体章节时走 worldbuilder 统筹；明确说"写第X章"、"续写"、"扩写这段"时走 write。

### 核心功能
1. **基于完整细纲生成**：自动读取`outlines/chapters.json`（旧路径兼容见`sumeru-rules/SKILL.md` 第六部分"独立调用自举协议"）
2. **智能细纲匹配**：支持按章节号、卷号、或全部章节进行生成
3. 自动适配网文节奏：开头抓眼球、中间有冲突、结尾留悬念
4. 保持人物性格、剧情逻辑的一致性
5. **章节长度自适应**：优先读取`.sumeru/project.json` 中的 `chapterWordRange`（如 `[1400, 1800]`），无配置时默认 4000-5000 字。
6. 支持续写、修改、调整已有章节内容

### 独立调用自举
1. 定位项目根目录，读取或生成`.sumeru/project.json`、`.sumeru/status.json`
2. 若缺少`outlines/chapters.json`，按旧路径兼容策略处理（见`sumeru-rules/SKILL.md` 第六部分"独立调用自举协议"）
3. 若缺少`.sumeru/cache/`，生成最小摘要
4. 若缺少当前范围的 context pack，先生成临时 context pack 再写。
5. 根据 `chapters/` 已有文件推断续写位置，默认不覆盖已有章节
6. **写正文必须走子agent（即使是单章续写），父agent绝不写正文**

### 反AI写作规则

> **详见 `subagent-rules.md` 第四部分** 核心原则：AI 写得"正确"的部分越要改，写得越"奇怪"的部分越要保留。

**写入后自检：**
- 是否有一段超过5 句全部是主谓宾完整的句子？→ 插入破碎句或口语短句
- 是否有连续3 段都在推进剧情？→ 加入一段环境/动作/无关对话缓冲
- 人物的情绪是否直接说出来？→ 改为用动作细节暗示
- 对话是否太"工整"？→ 加入打断、跑题、停顿、重复
- 对话已表达情绪后，叙述是否在"翻译"同一情绪？→ 删除旁白解说，保留对话本身；若情绪暗示不足则改为动作细节
- **正文是否残留元信息标注？** 检查"视角：""伏笔：""下一章""下章""预告""本章完"等模式→ 删除，正文只保留故事内容

### 句号分段规则（强制）

> **核心要求**：每个句号（。）后面必须换行分段，形成独立段落。

**执行规则：**
1. **句号后强制换行**：正文中的每个句号（。）后面必须紧跟换行符，下一句从新行开始
2. **对话中的句号**：对话引号内的句号同样需要分段
3. **省略号/感叹号例外**：省略号（……）和感叹号（！）后可以不分段，保持原文节奏
4. **段落内标点**：逗号（，）、顿号（、）、分号（；）等不影响分段，保持在同段落内

**示例：**
```
原文（错误）：
他走进房间，看到桌上放着一封信。信封上没有署名，只画着一朵黑色的花。他拿起信封，手指微微颤抖。

修改后（正确）：
他走进房间，看到桌上放着一封信。
信封上没有署名，只画着一朵黑色的花。
他拿起信封，手指微微颤抖。
```

**自检清单：**
- [ ] 检查正文是否每个句号后都换行
- [ ] 检查对话中的句号是否也分段
- [ ] 确认省略号和感叹号保持原样

### 人物真实感与毛边规则

**核心：让人物像真人一样"不完美地活着"。**

| 规则 | 说明 |
|------|------|
| **言行不一** | 人物说的和想的不一定一样|
| **非理性选择** | 人物可以做明知不对的决定 |
| **个人习惯** | 每个人都有小动作、口头禅 |
| **受过去影响** | 过往经历影响当下的反应|
| **对不同人的差别** | 跟不同的人说话方式不同|
| **可以犯错** | 主角不是全知全能的|
| **内心矛盾** | 同时存在两种冲突的情绪|

**强度控制**：紧急战斗场景减少毛边，日常/过渡场景加大毛边，重要人物比龙套有更多毛边。

---

### 叙事效率通用自检

> **通用规则**：所有章节写作时强制执行，不区分平台。对标免费阅读平台读者留存规律，同时适用于付费阅读平台的基本叙事效率要求。

**检查项（写入后自检）：**
- 本章对话占比是否>5%？不足→在已有场景中增加对话轮次，而不是另加与场景无关的描写句
- 本章内心独白占比是否>10%？超出→将部分内心活动转换为动作暗示或对话潜台词
- 本章纯描写段落（环境/外貌/背景说明）占比是否≤35%？超出→删除冗余描写，用动作推动替代静态描写
- 本章是否有≥1个核心事件推进了剧情？不足→在现有场景中加入一个具体的情节转折
- 本章是否有≥1个时间节点变化或场景切换？不足→在章内插入一个时间跳跃或地点转移

**v1.2.2 强约束**：以上 5 项检查**必须**通过 `anti-ai-scan.py` 脚本量化执行（见后文「父Agent在子Agent写入**后**必须执行」第 3 步），子 Agent 不可仅凭经验主观判断。脚本阈值与本节阈值完全对齐。

### 开篇章节叙事规则

> **适用章节**：第1-3章。对标全平台读者留存规律，第一章是决定读者是否继续阅读的关键。

#### 第1章强制规则

| 规则 | 阈值 | 说明 |
|------|------|------|
| **100字禁止设定铺垫** | 0-100字世界观/人物背景/环境长描写 | 100字只能出现：冲突事件、对话、动作、反常现象 |
| **300字必须有冲突** | 300字内启动核心冲突/反常事件/悬念 | 超限→章节不通过，必须重写 |
| **主角第一幕必须主动选择** | 500字内主角做出带风险的选择 | 被动接受/被命运推动→章节不通过 |
| **结尾必须留钩子** | 章末必须有未解悬念/意外发现/预示冲突 | 软收尾/总结式→章节不通过 |
| **禁止大段闪回** | 1000字内禁止100字的回忆/闪回 | 打断当下节奏，推迟冲突感。 |

#### 第2-3章强制规则

| 规则 | 阈值 | 说明 |
|------|------|------|
| **结尾钩子** | 每章结尾必须有悬念或翻转 | 软收尾→警告 |
| **100字回顾** | 禁止用≥100字复述前文 | 直接推进新事件 |
| **核心事件差异** | 连续章节核心事件不得同质（如连续章都是"搭讪" | 同质→警告 |

#### 父Agent写入 context pack 时的开篇提醒

写作第1-3章时，父Agent必须在`shared-write.md` 中注入开篇规则提醒：

```markdown
## 开篇写作强制规则
1. 本章前100字：禁止世界背景/人物介绍/设定说明/环境长描写。只写冲突、对话、动作。
2. 主角必须在前500字内做一个有风险的选择——不是"被选中"，而是"主动选"
3. 章末必须留钩子：一个未解的悬念、一个刚揭露的线索、一个即将发生的冲突。
4. 禁止在1000字内插入100字的回忆闪回——打断当下节奏。
```

#### 父Agent写入 context pack 时的开场多样性提醒（所有章节）

父Agent必须在`cards-{范围}.md` 末尾注入开场多样性提醒：

```markdown
## 本章开场方式
- 第X章开场：{从`outlines/chapters.json` 的openingHook 字段摘取}
- 第Y章开场：{同上}
- 第Z章开场：{同上}

⚠️ 禁止"被X叫醒""从床上醒来""新的一天开始了""推门进来"等模板开场。
⚠️ 同批次各章之间开场方式必须不同，不可出现连续两章以相同模式起始。
```

### 创意落地自检

子Agent写入章节前逐条检查。根据`.sumeru/project.json` 的`style` 字段自动选择自检项：

| style 关键词 | 自检模式 |
|-------------|---------|
| 包含"爽文""热血""快节奏" | 爽文模式 |
| 其他（含"精品文""细腻""文艺"及未设置） | 精品文模式 |

##### 通用自检项（所有模式强制执行）

| # | 检查项 | 不通过处理 |
|---|--------|-----------|
| 0 | **对话占比>5%**（对话引号内文本） | 在当前场景插入对话轮次 |
| 0 | **内心独白>10%**（心理描写占总字数） | 将部分内心活动转为动作暗示 |
| 0 | **纯描写≤35%**（环境/外貌/背景说明） | 删除冗余描写，动作化 |
| 0 | **核心事件≥1**（明确推动剧情的事件） | 补充一个情节转折 |

#### 爽文模式
1. **名场面**：本章是否有读者能记住的一幕、一个选择或一句话？
2. **主角主动性**：主角是否通过选择推动局势，而不是被剧情推着走？
3. **结尾钩子**：结尾是否既承接本章输出，又诱导下一章点击？
4. **爽点排重**：本章爽点是否和前3章重复？（同类型爽点隔3章再出现）
5. **反派智商**：反派或阻力是否足够聪明，是否让胜利付出代价？

#### 精品文模式（默认）
1. **名场面**：本章是否有读者能记住的一幕、一个选择或一句话？
2. **主角主动性**：主角是否通过选择推动局势，而不是被剧情推着走？
3. **字数达标**：是否达到`project.json` 的`chapterWordRange` 的下限？不够时在当前场景中自然展开——让人物多一个反应、多一句停顿、多一段沉默，而不是另加与场景无关的描写句。
4. **情绪节拍**：本章是否有明确的情绪变化？（至少两个不同情绪状态）
5. **结尾处理**：结尾是否既承接本章输出，又为下一章留空间？（不强行要求"钩子"）

所选模式的 5 条全部通过才允许输出。任意一条不满足则重写调整后再提交。

### 子Agent调用模板

> **通用模板**（见`subagent-rules.md` 第二部分）。以下为 write 专用参数。

父Agent启动 write 子Agent时，在通用模板基础上补充：

```
角色：资深网文作者，主攻{题材}题材

写作风格：
- 句子有松有紧，不每句都主谓宾齐全，偶尔破碎句、口语化
- 人物像真人一样有毛边：会紧张、会嘴硬、会做不理性的选择
- 对话自然随意，可以跑题、重复、说一半的话
- 情绪不直白交代，用动作和环境暗示
- 结尾不留总结，留悬念钩子

输出前自检：
1. 本章有没有读者能记住的一幕？
2. 主角是主动选择还是被剧情推着走？
3. {自检项-根据style动态替换}
4. {自检项}
5. {自检项}

跨章多样性检查（你有3章，输出前对照）：
1. 每章的开场方式是否各不相同？
2. 每章的段落结构是否有明显重复？
3. 每章的结尾钩子句式是否雷同？
4. 同一句式是否连续超过5句？
5. 每章中两个相邻章节是否用了相同的情节触发器？

发现重复则在输出前主动调整。
```

**自检项3-5根据style动态替换**：
- 包含"爽文""热血""快节奏" → 爽文模式（结尾钩子/爽点排重/反派智商）
- 其他 → 精品文模式（字数达标/情绪节拍/结尾处理）

### 章节任务卡字段完整性检测与回退机制

父Agent在读取`outlines/chapters.json` 后、生成context pack 前，必须先执行字段完整性检测：

**1. 检测目标章节的必填字段**

目标章节范围（如第1-3章）的每章任务卡必须包含：`purpose`、`events`、`outputs`、`acceptanceCriteria`、`creativeGoal`、`emotionalBeat`、`readerMemoryPoint`、`tropeToAvoid`、`protectedElements`、`rhythm`

**2. 缺失处理策略**

| 情况 | 行为 |
|------|------|
| 全部字段齐全 | 直接生成 context pack |
| 缺字段，但存在`outlines/chapter-XXX-YYY.md` | 从batch outline 文件中提取详情补入卡片，并记录：`ℹ️ 第X章字段从 chapter-XXX-YYY.md 回退补充` |
| 缺字段，且无对应 batch outline 文件 | 警告用户：`⚠️ chapters.json 第X章缺字段且无 batch outline 回退，正文质量可能受影响`，使用当前可用数据继续 |
| 目标章节在`chapters.json` 中完全不存在 | 报错终止：`在chapters.json 中找不到第X章任务卡` |

**3. batch outline 回退映射规则**

当`outlines/chapter-XXX-YYY.md` 存在时，按以下映射将内容填充到cards：

```
batch outline 字段 → task card 字段
─────────────────────────────────
章节目的 / chapter purpose  → purpose
剧情推进 / events            → events（列表化）
开场方式 / openingHook      → openingHook
情绪模板 / emotionalBeat     → emotionalBeat
acceptanceCriteria 无直接对应 → 从events + purpose 自动推导
（其他字段无法映射的不填充）
```

**4. 回退警告写入**

回退行为必须记录到`.sumeru/changelog.md`：
```
ℹ️ write: 第1-3章chapters.json 缺字段，从outlines/chapter-001-015.md 回退补充
```

### 父Agent context pack 生成规则

> **详见 `sumeru-rules/SKILL.md` 第四部分"Context Pack 格式"与第五部分"分卷数据源作用域规则"。** 完整目录结构与卷切换协议见 `sumeru-rules/SKILL.md` **第十五部分·分卷隔离与卷切换协议**。

每批子Agent启动前，父Agent生成 2 个文件：
1. **共享上下文`shared-write.md`**：同批次所有子Agent共用
2. **本组任务卡`cards-{范围}.md`**：每子Agent独有

**文件位置：** `.sumeru/context-packs/`

**分卷模式**：当 `project.json.volumeCount >= 2` 时，shared context pack 的数据源**必须按卷作用域**限定（详见下文「分卷模式支持」第一节），从 `.sumeru/volumes/vol-N/` 读取对应数据，而非全局 `characters/` / `.sumeru/continuity/` / `.sumeru/cache/`。

### 扫榜写作指南注入

当 `.sumeru/research/writing-guide.md` 存在时（由 `sumeru-scan` 生成），父Agent在生成 context pack 时必须：

1. **读取写作指南**：从 `.sumeru/research/writing-guide.md` 读取「七、注入Context Pack指令」section
2. **注入共享上下文**：将写作指南的关键内容写入 `shared-write.md` 的「写作指南」section
3. **子Agent参考执行**：子Agent写作时参考写作指南的开篇、爽点、人设、节奏、避坑等要求

**注入格式示例**：
```markdown
## 写作指南（基于{平台}{题材}扫榜数据）

### 开篇要求
- {从writing-guide.md提取}

### 爽点要求
- {从writing-guide.md提取}

### 人设要求
- {从writing-guide.md提取}

### 节奏要求
- {从writing-guide.md提取}

### 避坑要求
- {从writing-guide.md提取}
```

### 仿写模式

当用户指定仿写目标时（如 `/sumeru-write 第1章 --imitate 《书名》`），父Agent执行以下流程：

#### 触发条件
- 用户明确指定 `--imitate` 或 `--imitation-guide` 参数
- 或在 context pack 中注入了仿写指令

#### 仿写注入流程
1. **读取仿写指南**：从 `.sumeru/research/imitation-guide-{书名}.md` 读取
2. **提取仿写指令**：提取「四、仿写执行指令」section（结构指令、风格指令、套路指令）
3. **注入共享上下文**：将仿写指令写入 `shared-write.md` 的「仿写指令」section
4. **标注原创要求**：在 context pack 开头强调原创保障声明

#### 仿写 context pack 注入格式
```markdown
## ⚠️ 仿写模式（基于《{书名}》）

**核心原则**：学骨架不学血肉，学模式不学内容。

**原创保障**：
- 人物名称、外貌、背景**完全原创**
- 地名、组织名、功法名**完全原创**
- 具体情节、对话、场景**完全原创**
- 核心设定有差异化（不能照搬金手指）

---

## 仿写结构指令

### 开篇要求
- 第1章：{模仿的开篇模式}
- 第2章：{模仿的推进模式}
- 第3章：{模仿的第一个爽点}

### 节奏要求
- 小爽点间隔：{N}章
- 大爽点间隔：{N}章
- 章节字数：{N}-{M}字

### 钩子要求
- 每章结尾：{模仿的钩子类型}
- 大钩子频率：{每N章}

---

## 仿写风格指令

### 句式要求
- 句子长度：{模仿的特征}
- 破碎句：{模仿的频率}
- 口语化：{模仿的程度}

### 对话要求
- 对话占比：{N}%
- 标记词：{模仿的偏好}
- 打断/停顿：{模仿的频率}

### 情绪要求
- 表达方式：{直白/暗示/平衡}
- 内心独白：{模仿的占比}
- 环境烘托：{模仿的频率}

---

## 仿写套路指令

### 金手指（用原创设定，模仿模式）
- 类型：{模仿的类型}
- 展示节奏：{模仿的节奏}
- 升级曲线：{模仿的曲线}

### 人设（用原创人物，模仿模板）
- 主角类型：{模仿的类型}
- 核心性格：{模仿的特征}
- 成长弧线：{模仿的弧线}

### 冲突（用原创情节，模仿模式）
- 冲突来源：{模仿的来源}
- 铺垫方式：{模仿的方式}
- 爆发节奏：{模仿的节奏}

### 打脸（用原创场景，模仿模式）
- 铺垫结构：{模仿的结构}
- 铺垫长度：{N}章
- 打脸方式：{模仿的方式}
```

#### 仿写自检清单
子Agent写入后，父Agent必须检查：
- [ ] 人物名称是否与原作重复？→ 必须完全原创
- [ ] 地名/组织名是否与原作重复？→ 必须完全原创
- [ ] 具体情节是否与原作雷同？→ 必须完全原创
- [ ] 金手指是否照搬原作？→ 必须有差异化
- [ ] 结构/节奏/套路模式是否正确模仿？→ 应与仿写指令一致

#### 仿写调用示例
```bash
# 指定仿写目标
/sumeru-write 第1章 --imitate 《书名》

# 指定仿写指南文件
/sumeru-write 第1章 --imitation-guide imitation-guide-XX.md

# 批量仿写
/sumeru-write 第1-10章 --imitate 《书名》
```

### 输入优先级
1. 用户本次明确要求
2. context pack（批量写作首选）
3. `.sumeru/cache/` 摘要
4. `.sumeru/review/fix-plan.json` 中的重写要求
5. `outlines/chapters.json` 中的任务卡
6. `outlines/chapter-XXX-YYY.md`（回退源）
7. 已存在的 `chapters/` 内容

### 剧情统一门禁与反AI扫描

> **详见 `sumeru-rules/SKILL.md` 第十部分"剧情统一门禁与反AI扫描"**

父Agent在子Agent写入**前**必须执行：

1. **伏笔活跃度预检**：调用 `python skills/sumeru-review/scripts/foreshadowing-tracker.py .sumeru/continuity <current_chapter> --quiet`，把输出的逾期伏笔与近期伏笔建议注入 `shared-write.md` 头部（父 Agent 决定是否提示用户）。**分卷模式**：脚本输入路径替换为 `.sumeru/volumes/vol-N/continuity/`，父 Agent 在调用前先 `export SUMERU_CURRENT_VOLUME=vol-N` 让脚本读取卷内 `consistency-rules.json` 与本卷伏笔表。
2. **锚点临近检查**：读取 `.sumeru/creative-anchors.md`，找出 `targetChapter` 字段距当前章 ≤ 3 的「名场面种子」，在 `shared-write.md` 头部追加"⚠️ 锚点临近：本章或近 3 章需兑现 XX 锚点"

父Agent在子Agent写入**后**必须执行：

1. **剧情统一校验**：解析 SUMERU_STATUS，与 consistency-rules.json 对比。**分卷模式**：从 `.sumeru/volumes/vol-N/continuity/consistency-rules.json` 读取，父 Agent 调用前先 `export SUMERU_CURRENT_VOLUME=vol-N`。
2. **foreshadowing 增量更新**：遍历 `plot_update.foreshadowing`，对每个提及的伏笔 ID 同步写入 `consistency-rules.json.foreshadowing.<id>.last_mentioned = current_chapter` 且 `mentionCount += 1`（新伏笔初始化 `{status: "active", last_mentioned: current_chapter, mentionCount: 1, first_appeared: current_chapter}`）。**分卷模式**：写入 `.sumeru/volumes/vol-N/continuity/consistency-rules.json`。
3. **反AI / 反水文扫描（v1.2.2 强约束）**：**必须**调用 `python skills/sumeru-review/scripts/anti-ai-scan.py chapters --outlines outlines/chapters.json --output .sumeru/review --quiet`。脚本退出码：
   - `0` = 通过，继续下一步
   - `1` = warning，写入 fix-plan.json `type=anti_ai_warning`；可选触发 polish 轻量级
   - `2` = 含阻断（`narrative_high_description` / `narrative_low_event_density` / `water_text_cliche_density` 命中）→ **禁止更新状态文件**，必须将当前章节打回子 Agent 重写。父 Agent **不得**用"插入 2-4 段描写"方式补字数或绕过阻断。
4. **（可选）连续性冲突检查**：若 `consistency-rules.json` 已有累积状态，调用 `python skills/sumeru-review/scripts/continuity-check.py .sumeru/continuity --quiet`，把 critical 冲突立即报出；high/medium 写入 `.sumeru/issues.md`。**分卷模式**：脚本输入路径替换为 `.sumeru/volumes/vol-N/continuity/`，父 Agent 调用前先 `export SUMERU_CURRENT_VOLUME=vol-N`；跨卷冲突写入 `.sumeru/cross-volume/dependency-table.md` 的「已发现冲突」section。

校验通过后才允许更新 `chapters/` 和状态文件。

**扫描报告写入** `.sumeru/review/anti-ai-report.json` 与 `.sumeru/review/anti-ai-report.md`（路径以脚本实际输出为准，旧版 `.sumeru/write/anti-ai-report.json` 已废弃）。

### 章节任务卡执行规则

**核心规则：**
- 正文必须完成任务卡中的`purpose`
- 正文必须落实 `creativeGoal`、`freshnessHook`、`emotionalBeat`、`readerMemoryPoint`
- 遇到 `tropeToAvoid` 时必须避开直给套路
- 若存在`surpriseTwist`，必须提前埋下公平线索。
- 正文必须满足全部 `acceptanceCriteria`

**创意自由度控制：**
```json
{
  "creativeFreedom": "medium",
  "protectedElements": ["主角必须展现判断力", "不能暴露真正实力"],
  "allowedDeviations": ["可以添加人物小习惯", "可以有对话停顿/口误"]
}
```

**优先级规则：**
```
protectedElements（底线） → 不可违背
    ↓
purpose（必须完成） → 可以改变"如何完成"的方式
    ↓
allowedDeviations（鼓励添加） → 不强制，但鼓励
```

**protectedElements 执行保障：**
- 子Agent严格按照protectedElements 写作，不做任何例外申请
- 子Agent输出后，父Agent对比 state_diff 与protectedElements，检测是否违反
- 发现违反时，父Agent暂停并询问用户确认

### 细纲驱动批量生成
```
/sumeru-write 全部章节       # 生成所有章节（自动并行）
/sumeru-write 第1-50章      # 生成指定范围
/sumeru-write 第3章         # 生成特定章
/sumeru-write 第3章 "概要"   # 单章创作
/sumeru-write 第3章 按细纲生成
/sumeru-write 第1卷         # 分卷模式：生成第1卷所有章节（详见「分卷模式支持·四」）
/sumeru-write vol-003       # 用 vol-ID 形式指定卷
```

### 章节文件命名规范
**强制格式：`{三位章节号}-{章节标题}.md`**
- ✅ `003-第一次接触.md`、`001-废物觉醒系统.md`
- ❌ `第3章-第一次接触.md`、`3-第一次接触.md`、`003_第一次接触.md`

### 正文标题格式规范
**强制格式：正文第一行必须为 `第X章 标题xxxx`**
- ✅ `第1章 离婚协议落在雨里`
- ✅ `第3章 雨夜告别`
- ❌ `第一章 离婚协议落在雨里`（不能用中文数字）
- ❌ `1. 离婚协议落在雨里`（不能用阿拉伯数字加点）
- ❌ `001-离婚协议落在雨里`（不能用短横线）

**格式规则：**
- 章节号：阿拉伯数字，不加前导零（`第1章` 不是 `第01章`）
- 标题：与文件名中的章节标题一致
- 第一行：必须是标题行，后面跟空行，然后是正文

## 分卷模式支持

> **适用条件**：项目 `chapters/` ≥ 150 章，或 `project.json` 中 `volumeCount >= 2`。
> 完整目录结构与卷切换协议见 `sumeru-rules/SKILL.md` **第十五部分·分卷隔离与卷切换协议**。
> 少于 150 章的项目继续使用扁平模式，所有卷作用域规则**降级为**全局规则，不创建 `volumes/` 目录。

分卷模式下，父 Agent 在自举阶段需读取 `project.json.volumeCount` 与 `currentVolume` 字段，并按本节规则限定所有数据源路径。

### 一、Context Pack 卷作用域

当 `project.json.volumeCount >= 2` 时，shared context pack 的数据源**必须**按卷作用域限定，禁止从全局 `characters/` / `.sumeru/continuity/` / `.sumeru/cache/` 读取本卷数据：

| Context Pack 字段 | 分卷模式数据源 |
|---|---|
| **Relevant Characters** | `.sumeru/volumes/vol-N/characters/`（本卷活跃人物镜像） **并集** `.sumeru/cross-volume/master-characters.md`（全局人物索引）。**不读**全局 `characters/` 整目录 |
| **Continuity State** | `.sumeru/volumes/vol-N/continuity/state-current.json`（本卷当前状态）。**不读** `.sumeru/continuity/` |
| **Batch Summary** | `.sumeru/volumes/vol-N/cache/batch-summaries/`（本卷批次摘要）。**不读** `.sumeru/cache/batch-summaries/` |
| **Current Volume outline** | `.sumeru/volumes/vol-N/outline.md`（本卷剧情框架）。**不读** 全局 `outline.md` 分卷章节 |
| **World Addendum** | `world.md` 全书规则 **并集** `.sumeru/volumes/vol-N/world-addendum.md`（如有） |

**跨卷引用（按需查询，不预加载）**：
仅当目标章节的 `protectedElements` 或伏笔涉及跨卷依赖表中注册的项时，**额外**查询一次 `.sumeru/cross-volume/dependency-table.md`，从 `dependency-table.md` 锁定目标卷，再按需读取 `state-final.json` / `state-start.json`。**禁止**扫描全量 continuity 或预加载全部跨卷数据。

父 Agent 在生成 `shared-write.md` 头部必须显式标注：
```markdown
## 当前卷
- Volume: vol-N（{卷名}）
- 数据源作用域：`.sumeru/volumes/vol-N/` + `.sumeru/cross-volume/`
- 跨卷引用：见 `dependency-table.md`（仅按需）
```

### 二、Continuity 写入作用域

在「剧情统一门禁与反AI扫描」节的 pre-check / post-check 流程中，**分卷模式下**：

| 操作 | 非分卷模式 | 分卷模式 |
|------|-----------|---------|
| 读取 `consistency-rules.json` | `.sumeru/continuity/` | `.sumeru/volumes/vol-N/continuity/consistency-rules.json` |
| 读取 `state-current.json` | `.sumeru/continuity/` | `.sumeru/volumes/vol-N/continuity/state-current.json` |
| 写入伏笔增量 | `.sumeru/continuity/consistency-rules.json` | `.sumeru/volumes/vol-N/continuity/consistency-rules.json` |
| `foreshadowing-tracker.py` 输入目录 | `.sumeru/continuity` | `.sumeru/volumes/vol-N/continuity` |
| `continuity-check.py` 输入目录 | `.sumeru/continuity` | `.sumeru/volumes/vol-N/continuity` |
| 跨卷冲突登记 | 不适用 | `.sumeru/cross-volume/dependency-table.md`「已发现冲突」section |
| 章状态更新 | `.sumeru/status.json` | `.sumeru/volumes/vol-N/status.json` |
| issues.md 写入 | `.sumeru/issues.md` | `.sumeru/issues.md`（全局；卷号前缀标注） |

**父 Agent 调用脚本前置条件**：
```bash
# 分卷模式下，父 Agent 在调用 continuity 脚本前必须设置：
export SUMERU_CURRENT_VOLUME=vol-N
python skills/sumeru-review/scripts/foreshadowing-tracker.py \
  .sumeru/volumes/vol-N/continuity <current_chapter> --quiet
# 同理 continuity-check.py
```

`SUMERU_CURRENT_VOLUME` 必须与 `project.json.currentVolume` 一致；若两者不一致，父 Agent 应中止并提示用户：
```
⚠️ SUMERU_CURRENT_VOLUME={env} 与 project.json.currentVolume={json} 不一致
```

### 三、批次摘要软重置（卷切换边界）

当父 Agent 检测到当前批次的章节范围**跨过卷边界**（即 `chapters.json` 中下一章 `volume` 字段发生变化），执行软重置协议：

1. **保留前卷最后 1 批摘要 + 卷级总结**（≤ 500 字），整体作为**新卷** `.sumeru/volumes/vol-M/continuity/batch-summaries/batch-000-handoff.md` 第一条记录写入。
2. **归档更早批次**：`vol-N/continuity/batch-summaries/batch-002.md` 之前的所有摘要，整体移入 `vol-N/continuity/batch-summaries-archived/`（保留只读，可用于回溯但不再被 context pack 加载）。
3. **新卷初始化**：若 `vol-M/continuity/batch-summaries/` 仍为空（无 handoff 条目），按本节第一步补写。
4. **回写 changelog**：`.sumeru/changelog.md` 追加 `ℹ️ write: vol-N → vol-M 软重置，{N} 条旧摘要归档，1 条 handoff 写入`。
5. **回写 project.json**：`currentVolume = "vol-M"`，`volumes[vol-M].status` 从 `planned` 切到 `active`。

软重置**不删除**任何历史摘要，只移动位置并标记只读。子 Agent 看到的 batch-summaries 数量在卷切换后立刻从「前卷累计 N 条」变为「新卷 1 条 handoff + 后续累积」，避免 context pack 因摘要膨胀超限。

### 四、批量卷写（`/sumeru-write 第N卷`）

新增 `/sumeru-write 第N卷` 调用形式，父 Agent 自动按卷范围批量生成该卷所有章节：

**触发命令示例**：
```bash
/sumeru-write 第1卷               # 写第1卷所有章节
/sumeru-write 第2卷 仙侠风格       # 第2卷 + 风格覆盖
/sumeru-write vol-003              # 用 vol-ID 形式
/sumeru-write 第1卷 --from-batch 5 # 从第5批开始（卷内偏移）
```

**卷边界自动检测**（按优先级）：
1. **`chapters.json.volume` 字段**：若 `chapters.json` 章节任务卡包含 `volume` 字段（值为 `"vol-001"` 等），按该字段过滤属于 `vol-N` 的所有章节号
2. **`project.json.volumes[vol-N].chapterRange`**：回退到 `chapterRange: [start, end]`，取 `[start, end]` 闭区间
3. **`outline.md` 分卷章节标记**：从 `outline.md` 解析 `## 第N卷` 标题下的章节列表

**执行流程**：
1. 解析出目标卷的章节号集合 `chapterList = [ch1, ch2, ...]`
2. 按 3 章/子 Agent 的约束自动分批（与扁平模式相同）
3. 卷首（第一批次）触发 context pack 软重置（见第三节）
4. 卷内批次正常串行（与扁平模式相同）
5. 卷尾（最后一批次）若为该卷最后章节，**仅在用户明确要求**时触发 `sumeru-write` 父 Agent 的 `Phase A` 卷完结流程（最终快照 + 卷级总结 + 跨卷骨架更新）；**默认不自动**触发 Phase A，留给 `sumeru-worldbuilder` 编排

**章节范围约定**：`/sumeru-write 第1卷` 与 `/sumeru-write 第1-30章`（章节号范围）可以混用；优先按 `volume` 字段匹配，未匹配时回退到范围语法。


### 数据持久化
**用户可见输出**：`chapters/` 下的纯净正文文件

**中间数据**：

**扁平模式（`project.json.volumeCount < 2`）：**
- `.sumeru/write/`：`progress.json`、`chapter-meta.json`、`character-state.json`、`original/`
- `.sumeru/continuity/`：`consistency-rules.json`、`state-current.json`、`batch-summaries/`
- `.sumeru/cache/`：项目/世界观/人物/风格/创意/连续性/issue 摘要

**分卷模式（`project.json.volumeCount >= 2`，详见「分卷模式支持」与 `sumeru-rules/SKILL.md` 第十五部分）：**
- `.sumeru/write/`：仅放全局写阶段元数据
- `.sumeru/volumes/vol-N/continuity/`：本卷 `consistency-rules.json`、`state-current.json`、`state-start.json`、`state-final.json`
- `.sumeru/volumes/vol-N/continuity/batch-summaries/`：本卷批次摘要
- `.sumeru/volumes/vol-N/continuity/batch-summaries-archived/`：本卷已归档批次（只读）
- `.sumeru/volumes/vol-N/cache/`：本卷缓存
- `.sumeru/volumes/vol-N/status.json`：本卷章节状态
- `.sumeru/cross-volume/`：`master-characters.md`、`master-timeline.md`、`dependency-table.md`

### 与其他Skill 配合
- **前置**：`sumeru-topic` 选题 + `sumeru-outline` 大纲（`plan.md`、`outline.md`、`outlines/chapters.json`）
- **前置（可选）**：`sumeru-scan` 扫榜分析（`writing-guide.md` 注入context pack）
- **前置（可选）**：`sumeru-scan` 仿写指南（`imitation-guide-{书名}.md` 注入context pack）
- **后续**：供 `sumeru-review`、`sumeru-polish`、`sumeru-finalize` 使用

> 风格样本机制详见 `sumeru-rules/SKILL.md` 第十二部分子Agent精简版规则中的风格样本说明。用户提供样本后父Agent注入 context pack。
> 反AI写作规则详见本文`反AI写作规则` 节和 `人物真实感与毛边规则` 节。
> 分卷模式完整规范（目录结构、卷切换协议、Phase A/B/C、激活与降级）见 `sumeru-rules/SKILL.md` **第十五部分·分卷隔离与卷切换协议**；本文「分卷模式支持」节是 write 侧的操作约束。
