---
name: sumeru-finalize
description: 小说完稿校验与导出，也负责小说项目 build/release。用户说小说写完了、要检查错别字/标点/语法、检测敏感词、整理发布版、排版、构建发布包、导出起点/番茄/晋江/纵横等平台格式、多平台导出、自动拆章、标题优化、简介适配时必须使用本技能。
type: skill
---

> 依赖 `sumeru-rules`，默认 `quiet` 模式。

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
- 只在完稿、发布前检查或用户明确要求导出时触发；普通写作、审查、润色阶段不提前运行

### 独立调用自举
1. 定位项目根目录，读取或生成 `.sumeru/project.json`、`.sumeru/status.json`
2. 根据 `chapters/` 推断可导出章节
3. 若缺少 tests 或 issue summary，不阻塞技术校验
4. 若缺少当前范围的 context pack，先生成临时 context pack

### 按模式导出
| 模式 | 输出内容 |
|------|----------|
| `short/light` | `publish/release.md` 或单篇发布稿，基础检查 |
| `medium/standard` | 导出全文和分章版本，生成 `publish/` 和 release 检查报告 |
| `long/full` | 完整 build/release，生成 `publish/`、`tests/release-check-report.md`、`build-manifest.json` |

### Build 前检查
- 读取 `.sumeru/status.json`，默认只导出状态为 `finalized` 的章节
- 检查 `chapters/` 是否缺章、重章、命名不规范
- 检查正文是否包含 `TODO`、`FIXME`、未替换占位符
- 检查 `.sumeru/issues.md` 是否存在未关闭的 `critical` 或 `major` issue；旧版 `.sumeru/issues/index.json` 只读兼容
- 导出到 `publish/` 时必须剥离章节首行的 `SUMERU_STATUS` 注释
- 若存在 `.sumeru/intro.md`，将简介写入各平台导出版本的开头（起点/番茄/纵横等）

### 子Agent并行校验机制

**核心设计原则：finalize 的核心任务大部分可以用规则+词典覆盖，不需要子Agent创作**

**父Agent直接调用脚本做**（不经过子Agent）：
- 错别字词典扫描
- 正则敏感词初筛（一级/二级/三级分类）
- 格式规范统一
- 多平台格式转换
- Build前检查清单

**子Agent只处理脚本标记出的"待定项"**：
- 敏感词上下文判断
- 每次最多传 20 个待定项给子Agent
- 待定项 context 字段扩展为前后 100 字符（原 30 字符不足）
- 子Agent输出待定项的处理建议，写入 `.sumeru/finalize/pending-results.json`

**待定项返回协议：**
```json
// .sumeru/finalize/pending-results.json
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

### 各平台导出格式规则

#### 导出类型

| 导出类型 | 格式规则 |
|----------|----------|
| **分章导出** | 每章独立文件，标题格式统一为 `第X章 标题xxxx`，章节号用阿拉伯数字不加前导零 |
| **总导出** | 去掉章节标题，采用书名作为总标题，章节内容连续排版，仅用空行分隔各章 |

> 各平台格式规则和智能导出由脚本处理，详见 `scripts/platform-export.py`。

### 敏感词检测标准

| 级别 | 说明 | 处理方式 |
|------|------|----------|
| 一级 | 违反法律法规、政治敏感、色情淫秽、暴力恐怖等 | 必须修改 |
| 二级 | 血腥暴力、低俗用语、医疗描写、未成年人不当内容等 | 建议修改 |
| 三级 | 网络用语过多、易歧义表述、争议话题等 | 优化建议 |

### 数据持久化
**用户可见输出**：
- `publish/`：各平台导出版本（含简介）
- `tests/release-check-report.md`：发布前检查报告

**中间数据（`.sumeru/finalize/`）**：
- `clean/full-text.md`、`clean/chapters/`、`error-report.json`、`stats.json`、`build-manifest.json`

**项目元数据**：
- `.sumeru/intro.md`：小说简介（大纲完成后自动生成）

### 与其他 Skill 配合
- **前置**：读取最终章节内容（`chapters/`）


