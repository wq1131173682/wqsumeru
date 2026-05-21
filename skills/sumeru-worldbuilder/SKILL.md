---
name: sumeru-worldbuilder
description: 网文/小说全流程创作世界构建师和项目管理器。用户想从零写小说、初始化小说项目、把创意发展成完整作品、自动完成选题/大纲/章节/审查/润色/导出、风格样本采集时必须使用本技能。
type: skill
---

> ⚠️ **依赖技能**：本 Skill 依赖 `sumeru-rules` 中的全局约束。执行前请确保已加载。

> 📌 **输出级别**：默认 `quiet` 模式，只输出进度。详细规范见 `sumeru-rules` "输出级别规范"。

## 网文创作世界构建师

### 触发关键词
我想写小说、写一本网文、从零开始创作小说、帮我写本XX类型的小说、我要写本小说、给我整个小说创作流程、自动写小说、小说创作一站式服务、帮我完成一本小说、我只有创意怎么写小说、从零开始写网文、小说全流程创作

### 核心功能
worldbuilder 是网文创作的一站式主控技能，负责统筹协调从创意萌芽到作品完稿的完整创作链路：

0. **项目初始化**：创建标准小说项目目录
1. **选题策划**：调用 `sumeru-outline`（选题阶段）进行市场分析、选题定位
2. **大纲设计**：调用 `sumeru-outline` 构建完整世界观、人物设定、分卷大纲与章节任务卡
2.5 **简介生成**：大纲完成后自动生成 `.sumeru/intro.md`（作品名称、目标读者、类型标签、主角名、简介正文、平台标签映射）
3. **内容创作**：调用 `sumeru-write` 按章节任务卡进行分章节内容撰写
4. **逻辑审查**：调用 `sumeru-review` 对已完成章节进行项目测试式审查
5. **内容润色**：调用 `sumeru-polish` 对已审查章节进行文笔优化
6. **完稿构建**：调用 `sumeru-finalize` 对已润色章节完成技术校验、平台格式 build 和 release

### 项目初始化协议
当用户要求"初始化小说项目"或当前目录缺少 `.sumeru/project.json` 时：

1. 根据用户指定、计划章节数、计划字数判断 `projectMode` 和 `workflowLevel`
2. 写入 `.sumeru/project.json`
3. 生成 `.sumeru/status.json`
4. 按模式创建目录（不一刀切创建 full 结构）
5. 生成必要 cache 和 context pack
6. 生成 `.sumeru/backlog.md`、`.sumeru/decisions.md`、`.sumeru/changelog.md`

### 模式初始化
| 模式 | 创建内容 |
|------|----------|
| `short/light` | `README.md`、`story.md`、`outline.md`、`.sumeru/project.json`、`.sumeru/status.json`、`.sumeru/cache/story-brief.md` |
| `medium/standard` | `README.md`、`plan.md`、`outline.md`、`outlines/chapters.json`、`.sumeru/intro.md`、`chapters/`、`publish/`、`.sumeru/cache/`、`.sumeru/issues.md` |
| `long/full` | medium 结构 + `.sumeru/context-packs/`、`.sumeru/continuity/`、必要时 `reviews/`、`tests/` |

### 模式升级协议
- `short -> medium`：补齐 `plan.md`、`outlines/chapters.json`、`chapters/`、标准 cache
- `medium -> long`：补齐 `.sumeru/context-packs/`、`.sumeru/continuity/`，`reviews/` 和 `tests/` 按需创建
- 升级后更新 `.sumeru/project.json`，记录到 `.sumeru/decisions.md` 和 `.sumeru/changelog.md`

### 项目状态机
**阶段顺序**：`init -> topic -> outline -> write -> review -> fix -> polish -> finalize -> build/release`

**章节状态顺序**：`planned -> drafted -> reviewed -> fixed -> polished -> finalized -> exported`

**推进规则**：
- `outline` 完成：`outline.md`、`outlines/chapters.json`、`.sumeru/intro.md` 存在，且章节任务卡包含 `acceptanceCriteria`
- `write` 完成：目标章节文件存在，章节状态更新为 `drafted`，且没有缺章
- `review` 完成：目标范围已审查，问题写入 `.sumeru/issues.md`；完整报告和 tests 仅在用户要求时生成
- `fix` 完成：轻量问题已修复，重写问题已转为 `needs-rewrite` 或完成重写
- `polish` 完成：章节状态更新为 `polished`
- `finalize` 完成：技术校验通过，章节状态更新为 `finalized`

### 低 Token 调度规则
调用任何批量子技能前，必须先准备最小上下文：
1. 刷新 `.sumeru/cache/*.md` 中与本阶段相关的摘要
2. 根据章节范围生成 `.sumeru/context-packs/<stage>-<range>.md`
3. 写作/重写/润色 context pack 必须包含剧情事实基准、上一章实际结尾、人物/道具/伏笔状态
4. 子Agent prompt 中明确"只读取 context pack"
5. 汇总阶段先做剧情统一校验，再检查缺章、状态、issue、测试结果和缓存

### 分片策略
| 阶段 | 分片规则 |
|------|----------|
| outline 章节任务卡 | 每个子Agent最多 3 章 |
| write 创作 | 每个子Agent 1-3 章 |
| review 深度审查 | 每个子Agent最多 3 章 |
| review 全本轻扫 | 可按 10-20 章分片 |
| polish 润色 | 每个子Agent 1-3 章 |
| finalize 技术校验 | 脚本预处理 + 子Agent只处理待定项（最多20个/批） |

### 输出级别控制（默认静默模式）

**默认使用 `quiet` 模式**，只输出关键信息：

```
📝 写作中... 第 37/50 章 (74%)
```

**阶段完成时简洁总结：**
```
✅ 第 3 阶段完成：章节撰写
   已生成 50 章，共 125,000 字
   → 进入下一阶段：逻辑审查
```

**有问题时才提醒：**
```
⚠️ 第 25 章字数不足（1200 字，建议 2000+）
```

**不输出：**
- ❌ 脚本详细输出
- ❌ 中间报告内容
- ❌ 技术细节（Agent 数量、context pack 等）

**用户可指定输出级别：**
```
/sumeru-worldbuilder 玄幻 "废柴逆袭" 输出级别 normal
/sumeru-worldbuilder 玄幻 "废柴逆袭" 输出级别 verbose  # 调试用
```

### 交互式需求引导
当用户提供的信息过于简略时，自动触发交互式提问：

**基础信息确认（必问）**：
1. 题材确认（细分类型）
2. 篇幅预期
3. 核心爽点
4. 受众定位

**核心设定引导（可选）**：
5. 主角设定偏好
6. 反派设定偏好
7. 世界观偏好
8. 参考作品

**风格偏好设置（可选）**：
9. 写作风格
10. 发布平台
11. 禁忌内容

### Skill 协调流程
```
用户需求 → 收集需求 → outline[选题+大纲] → intro[简介生成] → write → review → [fix] → polish → finalize → build/release
                                    ↓
                            阶段检查点验证
```

### 使用示例
```
/sumeru-worldbuilder 玄幻 "废柴逆袭+系统流"
/sumeru-worldbuilder 言情 "霸道总裁+契约恋爱" 标题"总裁的契约新娘"
/sumeru-worldbuilder 玄幻 "废柴逆袭+系统流" 恢复上次创作
/sumeru-worldbuilder 都市 "职场+重生" 跳过选题阶段
/sumeru-worldbuilder 悬疑 "连环杀人+心理侧写+反转" 详写风格 暗黑调性
```

### 全局约束引用
> 完整全局约束见 `sumeru-rules` 技能，核心要点如下：
> - **子Agent规则**：最多5个并行，每个最多3章
> - **职责边界**：父Agent负责调度、状态维护、文件写入；子Agent只做单一核心任务
> - **状态标记**：子Agent输出首行必须包含 `<!-- SUMERU_STATUS: ... -->`
> - **Context Pack**：控制在1500-3000中文字，包含项目brief、人物摘要、世界观摘要、任务卡、批次摘要
> - **批次间串行摘要**：每批完成后生成≤500字摘要，作为下一批 context pack 的输入
> - **剧情统一门禁**：所有写作、重写、润色结果必须先通过 continuity 校验，再写入正式章节
