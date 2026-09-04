---
name: wq-finalize
description: 小说完稿校验与导出。用户说小说写完了、要检查错别字/标点/语法、检测敏感词、整理发布版、排版、导出md/txt分章格式、导出整文、修复已有导出时必须使用本技能。
version: 1.2.3
type: skill
user-invocable: true
requires: [wq-rules]
---

> 依赖 `wq-rules`，默认 `quiet` 模式。

## 网文完稿校验

### 触发关键词
小说写完了帮我检查下、导出md格式、导出txt格式、分章导出、导出整文、修复导出、查有没有错别字、检测敏感词、整理成发布版本、帮我导出小说发布格式、检查小说错别字、敏感词检测、小说完稿检查、小说排版整理、小说完稿导出

### 核心功能
1. 错别字、标点符号、语法错误检查
2. 敏感内容、违规内容排查（三级分类）
3. 格式规范统一：章节标题、段落格式、10类标点规范（破折号/省略号/感叹号问号/中英文混排/标点空格/引号闭合/书名号/括号/顿号逗号边界/重复标点，详见 `wq-rules` 第六点五部分）
4. 全文字数统计、完稿报告生成
5. **分章导出**：md/txt 格式，每章独立文件
6. **整文导出**：md/txt 格式，全文合并为一个文件
7. **修复导出**：按当前规则重新导出 publish/
8. 批量替换功能
9. 自动分段功能

### Skill 边界
- 技术性文字校验（错别字/标点/语法）由本 Skill 负责
- `wq-polish` 专注文笔和内容层面优化，两者互补不重叠
- 不改变剧情事实、人物关系、伏笔状态和章节结尾钩子
- 只在完稿、发布前检查或用户明确要求导出时触发；普通写作、审查、润色阶段不提前运行

### 独立调用自举
1. 定位项目根目录，读取或生成 `.sumeru/project.json`、`.sumeru/status.json`
2. 根据 `chapters/` 推断可导出章节
3. 若缺少 tests 或 issue summary，不阻塞技术校验
4. 若缺少当前范围的 context pack，先生成临时 context pack

### 按模式导出
| 模式 | 输出内容 |
|------|----------|
| `short/light` | `publish/full.md` + `publish/full.txt`，基础检查 |
| `medium/standard` | 分章 + 整文（md + txt），生成 `publish/` 和 release 检查报告 |
| `long/full` | 完整 build/release，生成 `publish/md/` + `publish/txt/`、`tests/release-check-report.md`、`build-manifest.json` |

### Build 前检查
- 读取 `.sumeru/status.json`，默认只导出状态为 `finalized` 的章节
- **读取修稿与评分状态（质量门禁）**：读取 `.sumeru/revise/revise-status.json` 与 `.sumeru/score/score-snapshot.json`，把以下章节列入 `build-quality-report.md` 风险项：
  - `revise-status` 中 `best-effort` 章节（撞重试上限的次品）→ 标 `⚠️ build_best_effort`，附 `stopReason`；
  - `revise-status` 中 `escalated` 章节（创意/市场不足需人工）→ 标 `🚫 build_escalated`，**默认阻断发布**，除非用户显式 `允许发布未修章节` 放行；
  - `score-snapshot.deficientChapters` 中仍 `resolved != true` 的项 → 标 `⚠️ build_score_unresolved`。
- 检查 `chapters/` 是否缺章、重章、命名不规范
- 检查正文是否包含 `TODO`、`FIXME`、未替换占位符
- **检查正文是否残留元信息标注**：扫描"视角：""伏笔：""伏笔设置""下一章""下章""预告""本章完""章节小结""剧情推进"等模式，命中则警告并从导出中剥离
- 检查 `.sumeru/issues.md` 是否存在未关闭的 `critical` 或 `major` issue；旧版 `.sumeru/issues/index.json` 只读兼容
- 导出到 `publish/`（包括 `publish/md/`、`publish/txt/`）时必须剥离章节首行的 `SUMERU_STATUS` 注释
- 若存在 `.sumeru/intro.md`，将简介写入各导出版本的开头

#### 平台内容适配检查

> **定位**：Build 前的最终质量门禁。检查结果不阻塞导出（不修改已有章节），但输出适配评分和警告供作者决策。
>
> **与 review 的区分**：`wq-review` 负责审查阶段的平台适配检查（可修改章节）；`wq-finalize` 负责 build 前的最终门禁（仅报告，不修改）。

##### 检查项目

| 检查项 | 阈值 | 严重度 | 说明 |
|--------|------|--------|------|
| 开篇前300字冲突启动 | >100字 | critical | 超限标记 `build_hook_delay` |
| 开篇前300字设定铺陈 | 0字 | high | 存在标记 `build_hook_expo` |
| 第1-3章结尾钩子 | 每章必须有 | critical | 缺失标记 `build_hook_missing` |
| 全局对话占比 | >55% | medium | 每章独立计算，汇总报告 |
| 全局内心独白占比 | >30% | medium | 每章独立计算，汇总报告 |
| 连续低密度警告 | >3章 | medium | 连续3章以上低密度标记 `build_density_low` |
| 章节字数范围 | 依 `project.json` 的 `chapterWordRange` | low | 标注超出范围的章节 |

##### 检查流程

1. 父Agent遍历全部章节，逐章计算叙事效率指标（对话占比/独白占比/描写占比）
2. 每章额外执行钩子强度检查
3. 汇总各章指标，生成 `build-quality-report.md`
4. 问题按严重度分级输出警告，不修改章节内容

##### 输出格式

```markdown
## build-quality-report.md（写入 `.sumeru/finalize/`）

### 综合评分
| 维度 | 评分 | 说明 |
|------|------|------|
| 开篇钩子 | ⚠️ 2/4 | 第1章前198字工作铺垫，未达标 |
| 叙事效率 | ⚠️ 18/30分 | 12章对话占比不足55% |
| 信息密度 | ⚠️ 3章 | 连续7章低密度，每章仅1个核心事件 |

### 平台适配建议
- **七猫/番茄**：不推荐直接投递。开篇钩子不足 + 首章节奏过慢
- **晋江**：可投递，建议优化对话占比后发布
- **起点**：可投递，章节字数偏短但精品文可接受

### 修稿风险项（读取 revise-status + score-snapshot）
| 章节 | 风险 | 来源 | 处理 |
|------|------|------|------|
| 第015章 | ⚠️ build_best_effort | revise-status（max-retries-reached）| 列入风险，允许发布但建议人工复核 |
| 第099章 | 🚫 build_escalated | revise-status（创意性不足，需人工）| **默认阻断**，用户 `允许发布未修章节` 才导出 |
| 第022章 | ⚠️ build_score_unresolved | score-snapshot（deficientChapters 未 resolved）| 列入风险 |
```

> escalated 章节默认阻断发布是质量兜底——创意性/市场契合度不可逐章自动修复，强行发布会把已知低质内容带到平台。用户须显式放行才会导出，并记录到 `.sumeru/decisions.md`。

### 子Agent并行校验机制

#### 架构设计原则

finalize 采用**父Agent脚本预处理 + 子Agent待定项判断**的两阶段架构。

| 阶段 | 执行者 | 任务 | 原因 |
|------|--------|------|------|
| **第一阶段** | 父Agent | 脚本预处理 | 规则明确、可脚本化、无需AI判断 |
| **第二阶段** | 子Agent | 待定项判断 | 需要上下文理解、语义分析 |

#### 为什么父Agent直接执行脚本？

1. **确定性任务**：错别字检查、敏感词初筛、格式规范等任务有明确规则，脚本执行更可靠
2. **性能考虑**：脚本批量处理比子Agent逐条判断更快
3. **一致性保证**：脚本输出稳定，不受AI随机性影响
4. **成本优化**：减少子Agent调用次数，降低token消耗

#### 父Agent直接执行的任务

| 任务 | 脚本 | 说明 |
|------|------|------|
| 错别字检查 | `scripts/spell-check.py` | 词典匹配 + 上下文验证 |
| 敏感词初筛 | `scripts/sensitive-word-filter.py` | 正则匹配 + 三级分类 |
| 格式规范 | `scripts/format-validator.py` | 章节标题、段落格式、10类标点规范检测（破折号/省略号/感叹号问号/中英文混排/标点空格/引号闭合/书名号/括号/顿号逗号边界/重复标点） |
| 格式导出 | `scripts/platform-export.py` | md/txt 分章 + 整文 + 按卷导出（章节文件直接写格式目录，文件名 `第001章-标题.md`）|
| 修复导出 | `scripts/platform-export.py repair` | 清理旧结构（clean/、chapters/ 子目录、纯数字旧命名）后重新导出 md + txt |
| Build前检查 | 内置逻辑 | 缺章检查、TODO检查、issue检查 |

#### 子Agent处理的任务

子Agent只处理脚本标记出的**待定项**（需要上下文判断的敏感词）：

| 任务 | 说明 |
|------|------|
| 敏感词上下文判断 | 判断敏感词在上下文中是否安全 |
| 替换建议 | 如果需要替换，提供合适的替代词 |

**处理流程**：
```
1. 父Agent运行脚本 → 生成待定项列表（最多20个）
2. 父Agent生成 context pack（含待定项前后100字符上下文）
3. 子Agent读取 context pack → 判断每个待定项
4. 子Agent返回处理建议 → 写入 pending-results.json
5. 父Agent根据建议执行最终修改
```

**待定项返回协议：**
```json
{
  "results": [
    {
      "chapter": "005",
      "word": "杀人灭口",
      "position": 1234,
      "verdict": "safe|remove|replace",
      "reason": "此处为角色对话中的威胁用语，非实际暴力描写",
      "replacement": null
    }
  ]
}
```

### 导出格式规则

#### 目录结构（v1.4.3）

完稿导出**只有 `md/` 和 `txt/` 两个文件夹**，章节文件直接写在格式目录下（不再嵌套 `chapters/` 子目录），文件名 `第001章-标题.md`。`clean/` 已废弃——SUMERU_STATUS 注释的剥离并入 md/txt 导出的常规清理流程。

```
非分卷:
publish/
├── md/
│   ├── 第001章-标题.md
│   ├── 第002章-标题.md
│   └── full.md          ← 全书整文
└── txt/
    ├── 第001章-标题.txt
    └── full.txt

分卷:
publish/
├── md/
│   ├── vol-001/                       ← 卷目录（顶层不再平铺分章，避免与卷内重复）
│   │   ├── 第001章-标题.md
│   │   └── full.md                    ← 本卷整文
│   ├── vol-002/
│   │   └── ...
│   └── full.md                        ← 全书整文（所有卷合并）
└── txt/
    ├── vol-001/
    │   └── ...
    └── full.txt
```

#### 分章导出

每章独立文件，直接写在格式目录下（分卷时写在 `vol-NNN/` 内）：

| 格式 | 文件名 | 内容格式 |
|------|--------|----------|
| md | `publish/md/第001章-标题.md` | 第一行 `第X章 标题`，正文紧随其后 |
| txt | `publish/txt/第001章-标题.txt` | 同上，纯文本 |

- 文件名格式：`第{三位章号}章-{标题}.{ext}`，如 `第001章-开端.md`
- 章节号 3 位前导零（001, 002, ...）
- 标题中的非法文件名字符（`<>:"/\|?*` 与控制符）自动替换为 `_`
- 空标题退化为 `第XXX章.md`
- 标题只出现在文件第一行，正文中不重复

#### 整文导出

所有章节合并为一个文件，章节之间空行分隔：

| 格式 | 文件名 |
|------|--------|
| md | `publish/md/full.md`（分卷时全书整文；卷整文在 `vol-NNN/full.md`）|
| txt | `publish/txt/full.txt`（同上）|

#### 按卷导出

当项目包含卷信息时自动启用（需通过 `--project` 指定项目根目录）。卷信息读取优先级：

1. **`outlines/chapters.json`**：每章的 `volume` 或 `vol` 字段
2. **`.sumeru/outlines/chapters.json`**：同上，新路径
3. **`outline.md`**：从 "第X卷" 和章节范围文本中正则提取（兜底）

分卷时：
- 卷目录名固定 `vol-NNN`（3 位前导零，如 `vol-001`）
- 顶层格式目录**只放全书整文**（`full.md`/`full.txt`），分章文件进各 `vol-NNN/` 子目录，避免顶层与卷内重复
- 每卷含本卷分章文件 + 本卷整文 `vol-NNN/full.md`
- 无卷信息的章节归入 `vol-000`（如有）

#### 标题规则

- 章节标题格式：`第X章 标题`（X 为阿拉伯数字）
- 标题统一写在章节内容第一行
- 单章中只有第一行是标题，正文中不重复

#### 修复导出（repair）

`repair` 模式用于把**已有 publish/ 目录**规整成新结构——解决多本小说导出格式不一致的问题：
- 先清理旧结构：删除 `clean/` 目录、删除 `chapters/` 子目录、删除纯数字旧命名文件（`001.md`/`002.txt`）
- 再从 `chapters/` 重新读取，按新规则生成 md + txt（分章 + 整文 + 按卷）
- 覆盖已有 `publish/` 内容

> 旧小说的 publish/ 不一致（有人有 clean/、有人嵌套 chapters/、有人文件名纯数字）跑一次 `/wq-finalize 修复导出` 即可统一成新结构。

### 调用示例

```bash
# 导出 md 格式（分章 + 整文 + 按卷）
/wq-finalize 导出md格式
/wq-finalize 导出md格式 自动分段

# 导出 txt 格式
/wq-finalize 导出txt格式

# 导出全部（md + txt）
/wq-finalize 导出全部

# 修复已有导出（清理旧结构 + 按新规则重新生成 publish/）
/wq-finalize 修复导出

# 批量替换后重新导出
/wq-finalize 替换"张三"为"李玄" 导出全部
```

### 卷信息配置

如需启用按卷导出，在 `outlines/chapters.json` 中为每章添加 `volume` 字段：

```json
{
  "chapters": [
    {
      "num": 1,
      "title": "觉醒",
      "volume": 1,
      "purpose": "...",
      "events": [...]
    },
    {
      "num": 2,
      "title": "试炼",
      "volume": 1,
      ...
    },
    {
      "num": 15,
      "title": "宗门大会",
      "volume": 2,
      ...
    }
  ]
}
```

父Agent在调用导出脚本时，会自动传入 `--project` 参数（指向项目根目录），脚本自动读取卷信息并按卷分组导出。

### 敏感词检测标准

| 级别 | 说明 | 处理方式 |
|------|------|----------|
| 一级 | 违反法律法规、政治敏感、色情淫秽、暴力恐怖等 | 必须修改 |
| 二级 | 血腥暴力、低俗用语、医疗描写、未成年人不当内容等 | 建议修改 |
| 三级 | 网络用语过多、易歧义表述、争议话题等 | 优化建议 |

### 数据持久化
**用户可见输出**：
- `publish/md/第001章-标题.md`：分章 md 导出（直接写格式目录，不再嵌套 chapters/）
- `publish/md/full.md`：全书整文 md 导出
- `publish/md/vol-NNN/`：按卷 md 导出（卷内分章 + 卷整文，如有卷信息）
- `publish/txt/第001章-标题.txt`：分章 txt 导出
- `publish/txt/full.txt`：全书整文 txt 导出
- `publish/txt/vol-NNN/`：按卷 txt 导出（如有卷信息）
- `tests/release-check-report.md`：发布前检查报告

**中间数据（`.sumeru/finalize/`）**：
- `error-report.json`、`stats.json`、`build-manifest.json`

**项目元数据**：
- `.sumeru/intro.md`：小说简介（大纲完成后自动生成）

### 与其他 Skill 配合
- **前置**：读取最终章节内容（`chapters/`）
