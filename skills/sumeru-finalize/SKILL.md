---
name: sumeru-finalize
description: 小说完稿校验与导出。用户说小说写完了、要检查错别字/标点/语法、检测敏感词、整理发布版、排版、导出md/txt分章格式、导出整文、修复已有导出时必须使用本技能。
version: 1.2.1
type: skill
user-invocable: true
---

> 依赖 `sumeru-rules`，默认 `quiet` 模式。

## 网文完稿校验

### 触发关键词
小说写完了帮我检查下、导出md格式、导出txt格式、分章导出、导出整文、修复导出、查有没有错别字、检测敏感词、整理成发布版本、帮我导出小说发布格式、检查小说错别字、敏感词检测、小说完稿检查、小说排版整理、小说完稿导出

### 核心功能
1. 错别字、标点符号、语法错误检查
2. 敏感内容、违规内容排查（三级分类）
3. 格式规范统一：章节标题、段落格式、标点规范
4. 全文字数统计、完稿报告生成
5. **分章导出**：md/txt 格式，每章独立文件
6. **整文导出**：md/txt 格式，全文合并为一个文件
7. **修复导出**：按当前规则重新导出 publish/
8. 批量替换功能
9. 自动分段功能

### Skill 边界
- 技术性文字校验（错别字/标点/语法）由本 Skill 负责
- `sumeru-polish` 专注文笔和内容层面优化，两者互补不重叠
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
| `long/full` | 完整 build/release，生成 `publish/md/` + `publish/txt/` + `publish/clean/`、`tests/release-check-report.md`、`build-manifest.json` |

### Build 前检查
- 读取 `.sumeru/status.json`，默认只导出状态为 `finalized` 的章节
- 检查 `chapters/` 是否缺章、重章、命名不规范
- 检查正文是否包含 `TODO`、`FIXME`、未替换占位符
- 检查 `.sumeru/issues.md` 是否存在未关闭的 `critical` 或 `major` issue；旧版 `.sumeru/issues/index.json` 只读兼容
- 导出到 `publish/`（包括 `publish/md/`、`publish/txt/`、`publish/clean/`）时必须剥离章节首行的 `SUMERU_STATUS` 注释
- 若存在 `.sumeru/intro.md`，将简介写入各导出版本的开头

#### 平台内容适配检查

> **定位**：Build 前的最终质量门禁。检查结果不阻塞导出（不修改已有章节），但输出适配评分和警告供作者决策。
>
> **与 review 的区分**：`sumeru-review` 负责审查阶段的平台适配检查（可修改章节）；`sumeru-finalize` 负责 build 前的最终门禁（仅报告，不修改）。

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
```

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
| 格式规范 | `scripts/format-validator.py` | 章节标题、段落格式、标点规范 |
| 格式导出 | `scripts/platform-export.py` | md/txt/clean 分章 + 整文 + 按卷导出 |
| 修复导出 | `scripts/platform-export.py repair` | 按当前规则重新导出 md + txt + clean |
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

#### 目录结构

导出文件按格式分目录存放：

```
publish/
├── md/             ← Markdown 格式
│   ├── chapters/   ← 分章导出（每个章节独立文件）
│   ├── full.md     ← 整文导出（所有章节合并）
│   ├── vol-001/    ← 按卷导出（如有卷信息）
│   │   ├── chapters/
│   │   ├── full.md
│   │   └── ...
│   └── vol-002/
│       └── ...
├── txt/            ← 纯文本格式（结构同 md/）
│   └── ...
└── clean/          ← 正本（清理 SUMERU_STATUS 的原始版本）
    ├── chapters/
    ├── full.md
    ├── vol-001/
    └── ...
```

#### 分章导出

每章独立文件，输出到对应格式的 `chapters/` 目录：

| 格式 | 文件名 | 内容格式 |
|------|--------|----------|
| md | `publish/md/chapters/001.md` | 第一行 `第X章 标题`，正文紧随其后 |
| txt | `publish/txt/chapters/001.txt` | 同上，纯文本 |
| clean | `publish/clean/chapters/001.md` | 同上，已清理 SUMERU_STATUS 注释 |

- 章节号固定 3 位前导零（001, 002, ...）
- 文件名不含标题文字，避免特殊字符问题
- 标题只出现在文件第一行，正文中不重复

#### 整文导出

所有章节合并为一个文件，章节之间空行分隔：

| 格式 | 文件名 | 内容格式 |
|------|--------|----------|
| md | `publish/md/full.md` | 每章以 `第X章 标题` 开头，然后正文，空行分隔 |
| txt | `publish/txt/full.txt` | 同上，纯文本 |
| clean | `publish/clean/full.md` | 同上，已清理 SUMERU_STATUS 注释 |

#### 按卷导出

当项目包含卷信息时自动启用（需通过 `--project` 指定项目根目录）。卷信息从以下位置读取（优先级从高到低）：

1. **`outlines/chapters.json`**：每章的 `volume` 或 `vol` 字段定义了所属卷号
2. **`.sumeru/outlines/chapters.json`**：同上，新路径
3. **`outline.md`**：从 "第X卷" 和章节范围文本中正则提取（兜底方案）

按卷导出时，每卷独立目录：

| 格式 | 目录 |
|------|------|
| md | `publish/md/vol-001/chapters/`, `publish/md/vol-001/full.md` |
| txt | `publish/txt/vol-001/chapters/`, `publish/txt/vol-001/full.txt` |
| clean | `publish/clean/vol-001/chapters/`, `publish/clean/vol-001/full.md` |

- 卷目录名固定 `vol-NNN` 格式（3 位前导零，如 `vol-001`）
- 无卷信息的章节归入 `vol-000`（如有）
- 按卷导出不影响分章和整文导出，是额外生成的

#### 正本导出（clean）

正本（clean 模式）是经过清理的原始版本，与 md/txt 导出的区别：

| 对比项 | md/txt 导出 | clean 正本导出 |
|--------|-------------|----------------|
| 用途 | 发布/分享用 | 存档/备份/版本对照 |
| SUMERU_STATUS | 已剥离 | 已剥离 |
| 格式 | md 或 txt | 仅 md |
| 输出位置 | `publish/md/` 或 `publish/txt/` | `publish/clean/` |
| 内容 | 成品格式 | 原文保留，最小改动 |
| 按卷导出 | 支持 | 支持 |

#### 标题规则

- 章节标题格式：`第X章 标题`（X为阿拉伯数字）
- 标题统一写在章节内容第一行
- 单章中只有第一行是标题，正文中不重复

#### 修复导出

`repair` 模式用于按当前技能规则重新生成已有 publish/ 目录：
- 从 `chapters/` 重新读取
- 生成全新的 md + txt + clean 分章、整文和按卷导出
- 覆盖已有 `publish/` 内容

### 调用示例

```bash
# 导出 md 格式（分章 + 整文 + 按卷）
/sumeru-finalize 导出md格式
/sumeru-finalize 导出md格式 自动分段

# 导出 txt 格式（分章 + 整文 + 按卷）
/sumeru-finalize 导出txt格式

# 导出全部（md + txt + 正本）
/sumeru-finalize 导出全部

# 仅导出正本（clean，清理 SUMERU_STATUS 的原始版本）
/sumeru-finalize 导出正本
/sumeru-finalize 导出clean

# 修复已有导出（按新规则重新生成 publish/）
/sumeru-finalize 修复导出

# 批量替换后重新导出
/sumeru-finalize 替换"张三"为"李玄" 导出全部
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
- `publish/md/full.md`：整文 md 导出
- `publish/md/chapters/`：分章 md 导出（001.md, 002.md, ...）
- `publish/md/vol-NNN/`：按卷 md 导出（如有卷信息）
- `publish/txt/full.txt`：整文 txt 导出
- `publish/txt/chapters/`：分章 txt 导出
- `publish/txt/vol-NNN/`：按卷 txt 导出（如有卷信息）
- `publish/clean/full.md`：整文正本
- `publish/clean/chapters/`：分章正本
- `publish/clean/vol-NNN/`：按卷正本（如有卷信息）
- `tests/release-check-report.md`：发布前检查报告

**中间数据（`.sumeru/finalize/`）**：
- `error-report.json`、`stats.json`、`build-manifest.json`

**项目元数据**：
- `.sumeru/intro.md`：小说简介（大纲完成后自动生成）

### 与其他 Skill 配合
- **前置**：读取最终章节内容（`chapters/`）
