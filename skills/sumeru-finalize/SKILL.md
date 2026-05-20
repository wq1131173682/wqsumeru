---
name: sumeru-finalize
description: 小说完稿校验与导出，也负责小说项目 build/release。用户说小说写完了、要检查错别字/标点/语法、检测敏感词、整理发布版、排版、构建发布包、导出起点/番茄/晋江/纵横等平台格式、多平台导出时必须使用本技能。
type: skill
---

## 网文完稿校验

### 触发关键词
小说写完了帮我检查下、导出适合起点/番茄的格式、查有没有错别字、检测敏感词、整理成发布版本、帮我导出小说发布格式、检查小说错别字、敏感词检测、小说完稿检查、适配起点格式导出、番茄小说格式导出、小说排版整理、多平台格式导出、小说完稿导出

### 核心功能
1. 错别字、标点符号、语法错误检查
2. 敏感内容、违规内容排查（三级分类）
3. 格式规范统一：章节标题、段落格式、标点规范
4. 全文字数统计、完稿报告生成
5. 适配不同平台发布格式导出
6. 批量替换功能
7. 自动分段功能

### Skill 边界
- 技术性文字校验（错别字/标点/语法）由本 Skill 负责
- `sumeru-polish` 专注文笔和内容层面优化，两者互补不重叠
- 不改变剧情事实、人物关系、伏笔状态和章节结尾钩子
- 发现剧情硬伤时记录到 `.sumeru/finalize/logic-notes.json`，建议回到 `sumeru-review` 或 `sumeru-write` 处理

### 独立调用自举
如果用户直接调用 `sumeru-finalize`，先执行 AGENTS.md 的"断点恢复与独立调用自举"：
- 定位项目根目录，读取或生成 `.sumeru/project.json`、`.sumeru/status.json`。
- 根据 `chapters/` 推断可导出章节；若状态缺失，将已有章节标记为至少 `drafted`。
- 若缺少 tests 或 issue summary，不阻塞技术校验；生成 `tests/release-check-report.md` 并标注"缺少审查测试历史"。
- 若缺少当前范围的 `finalize-<range>.md` context pack，先生成临时 context pack 再校验/导出。

### 按模式导出
- `short/light`：默认导出 `publish.md` 或单篇发布稿，做错别字、标点、敏感词和基础排版检查。
- `medium/standard`：导出全文和分章版本，生成 `publish/` 和一份 release 检查报告。
- `long/full`：执行完整 build/release，生成 `publish/`、`tests/release-check-report.md`、`.sumeru/finalize/build-manifest.json`。

### Build 前检查
- 读取 `.sumeru/status.json`，默认只导出状态为 `finalized` 的章节
- 检查 `chapters/` 是否缺章、重章、命名不规范
- 检查正文是否包含 `TODO`、`FIXME`、未替换占位符或明显元数据残留
- 检查 `.sumeru/issues/index.json` 是否存在未关闭的 `critical` 或 `major` issue
- 检查 `tests/foreshadowing-report.md` 是否存在关键伏笔未回收
- 检查 `docs/glossary.md` 中的术语是否出现禁止变体

### 子Agent并行校验机制

**核心设计原则：finalize 的核心任务大部分可以用规则+词典覆盖，不需要子Agent创作**

**父Agent直接调用脚本做**（不经过子Agent）：
- 错别字词典扫描
- 正则敏感词初筛（一级/二级/三级分类）
- 格式规范统一（章节标题、段落格式、标点）
- 多平台格式转换（起点/番茄/晋江/纵横/17K）
- Build前检查清单（缺章/重章/命名/TODO/FIXME/占位符）

**子Agent只处理脚本标记出的"待定项"**：
- 敏感词上下文判断（如特定表述在特定语境中是否需要替换）
- 每次最多传 20 个待定项给子Agent
- 子Agent输出待定项的处理建议

### 各平台导出格式规则

#### 起点中文网（qidian）
- 章节标题格式：`第X章 标题内容`，居中对齐
- 段落首行缩进2字符，每段空一行
- 标点符号使用中文全角，章节字数建议3000-5000字
- 对话单独成段

#### 番茄小说（fanqie）
- 章节标题格式：`第X章 标题内容`
- 段落首行不缩进，段落间空一行
- 每句尽量简短，适合移动端阅读
- 章节字数建议2000-3000字，对话使用引号包裹

#### 晋江文学城（jjwxc）
- 章节标题格式：`第X章 标题内容`
- 支持HTML格式标签，段落首行缩进2字符
- 作者有话要说区域单独设置

#### 纵横中文网（zongheng）
- 章节标题格式：`第X章 标题内容`
- 段落首行缩进2字符，章节字数建议3000-6000字
- 支持分卷设置

#### 17K小说网（17k）
- 章节标题格式：`第X章 标题内容`
- 段落首行缩进2字符，章节字数建议2000-4000字
- 每章结束可设置下章预告

### 敏感词检测标准

| 级别 | 说明 | 处理方式 |
|------|------|----------|
| 一级 | 违反法律法规、政治敏感、色情淫秽、暴力恐怖等 | 必须修改 |
| 二级 | 过于血腥暴力、低俗用语、医疗描写、未成年人不当内容等 | 建议修改 |
| 三级 | 网络用语过多、易歧义表述、争议话题、过度网络热梗等 | 优化建议 |

### 批量替换功能
- 支持全局批量替换指定词汇
- 支持正则表达式替换
- 支持替换前预览确认
- 支持多组替换规则同时执行

### 自动分段功能
- 智能识别对话与叙述内容
- 根据句子长度自动分段（默认100-300字/段）
- 对话自动单独成段
- 场景切换时自动分段

### 数据持久化
**用户可见输出**：
- `publish/`：各平台导出版本，按平台名分类存放
- `tests/release-check-report.md`：发布前检查报告

**中间数据（`.sumeru/finalize/`）**：
- `clean/full-text.md`：校验后的纯净版全文
- `clean/chapters/`：按章节拆分的纯净版文件
- `error-report.json`：错误列表
- `stats.json`：完稿统计报告
- `export-config.json`：各平台导出配置参数
- `build-manifest.json`：构建清单

### 与其他 Skill 配合
- **前置**：读取最终章节内容（`chapters/`）
- **后续**：无

### 全局约束引用
- 子Agent并行处理规则：见 AGENTS.md "子Agent并行处理规则"
- 职责边界：见 AGENTS.md "子Agent职责边界规则"
- 状态标记格式：见 AGENTS.md "子Agent输出状态标记"
- Context Pack 格式：见 AGENTS.md "Context Pack 格式"
- 独立调用自举：见 AGENTS.md "断点恢复与独立调用自举"
- 项目配置 Schema：见 AGENTS.md "项目配置 Schema"
- finalize 脚本化预处理：见 AGENTS.md "finalize 脚本化预处理"
