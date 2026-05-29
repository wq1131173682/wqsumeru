---
name: sumeru-migrate
description: 旧项目迁移与规整。用户说"规整项目"�?迁移旧项�?�?补齐缺失文件"�?检查项目完整�?�?修复项目结构"时必须使用本技能�?version: 1.2.0
type: skill
user-invocable: true
---

> 依赖 `sumeru-rules`，默�?`quiet` 模式�?
## 旧项目迁移与规整

### 触发关键�?规整项目、迁移旧项目、补齐缺失文件、检查项目完整性、修复项目结构、升级项目格式、旧项目升级、项目检查、查缺补漏、项目规范化

### 核心功能
1. **项目扫描**：全面扫描现有项目结构，识别文件缺失和字段问�?2. **路径迁移**：旧路径自动迁移到新 canonical 路径
3. **配置补齐**：生成缺失的 `.sumeru/project.json`、`status.json` 等配置文�?4. **目录补齐**：创建缺失的目录结构
5. **字段补全**：补齐章节任务卡缺失的必填字�?6. **人物卡生�?*：从大纲中提取人物信息生成人物卡
7. **迁移报告**：生成详细的迁移报告

### 使用方式

```bash
/sumeru-migrate                    # 完整迁移检查与修复
/sumeru-migrate 仅检�?            # 只检查不修复
/sumeru-migrate 仅迁移路�?        # 只迁移旧路径
/sumeru-migrate 补齐配置           # 只补齐配置文�?/sumeru-migrate 补齐人物�?        # 只生成缺失的人物�?```

---

## 一、迁移检查清�?
### 1.1 项目配置检�?
| 检查项 | 修复方式 |
|--------|----------|
| `.sumeru/project.json` 不存�?| 根据已有文件推断配置，生�?project.json |
| `.sumeru/status.json` 不存�?| 扫描 chapters/ �?outlines/ 推断状�?|
| `.sumeru/changelog.md` 不存�?| 创建空文�?|
| `.sumeru/decisions.md` 不存�?| 创建空文�?|
| `.sumeru/backlog.md` 不存�?| 创建空文�?|
| `.sumeru/issues.md` 不存�?| 创建空文�?|

### 1.2 目录结构检�?
| 检查项 | 修复方式 |
|--------|----------|
| `chapters/` 不存�?| 创建空目�?|
| `characters/` 不存�?| 创建空目�?|
| `outlines/` 不存�?| 创建空目�?|
| `publish/` 不存�?| 创建空目�?|
| `.sumeru/cache/` 不存�?| 创建空目�?|
| `.sumeru/context-packs/` 不存�?| 创建空目�?|
| `.sumeru/continuity/` 不存�?| 创建空目�?|

### 1.3 旧路径迁移检�?
| 旧路�?| 新路�?| 迁移方式 |
|--------|--------|----------|
| `.sumeru/outline/chapter-outlines.json` | `outlines/chapters.json` | 读取旧文件，合并到新文件 |
| `.sumeru/issues/index.json` | `.sumeru/issues.md` | 读取�?JSON，转换为 Markdown |
| `docs/requirements.md` | `plan.md` | 读取旧文件，合并�?plan.md |
| `docs/glossary.md` | `plan.md` 术语�?| 合并�?plan.md 术语部分 |
| `docs/style-guide.md` | `.sumeru/cache/style-brief.md` | 转换为缓存格�?|
| `ideas/*` | `plan.md` | 合并创意�?plan.md |

### 1.4 章节任务卡字段检�?
`outlines/chapters.json` 每章必须包含以下 15 个必填字段：

| 字段 | 说明 |
|------|------|
| `chapter` | 章节�?|
| `title` | 章节标题 |
| `purpose` | 本章核心作用 |
| `events` | 核心事件列表（≥3项） |
| `openingHook` | 具体开场方�?|
| `outputs` | 必须产出内容 |
| `acceptanceCriteria` | 验收条件 |
| `creativeGoal` | 创意目标 |
| `freshnessHook` | 新鲜感来�?|
| `emotionalBeat` | 情绪走向 |
| `emotionalBeatTemplate` | 情绪模板ID |
| `readerMemoryPoint` | 读者记忆点 |
| `tropeToAvoid` | 要避开的套�?|
| `protectedElements` | 底线元素 |
| `rhythm` | 节奏（fast/medium/slow�?|

**修复方式**�?- 缺字�?�?�?`.sumeru/outline/chapter-XXX-YYY.md` 回退补充
- 无回退�?�?从大纲和已有章节推断，标记为 `auto-generated`

### 1.5 人物卡检�?
| 检查项 | 修复方式 |
|--------|----------|
| `characters/` 目录为空 | �?`plan.md` �?`outline.md` 提取人物信息生成 |
| 人物卡缺少必要字�?| 补齐：姓名、年龄、身份、核心性格、人物弧�?|
| 人物卡与大纲不一�?| 以大纲为准，更新人物�?|

### 1.6 伏笔管理检�?
| 检查项 | 修复方式 |
|--------|----------|
| `outline.md` 缺少伏笔管理�?| 从已有章节提取伏笔，生成管理�?|
| 伏笔缺少 ID | 自动分配 ID（F1、F2...�?|
| 伏笔缺少预期回收位置 | 根据剧情推断，标记为 `待规划` |

### 1.7 章节状态检�?
| 检查项 | 修复方式 |
|--------|----------|
| 章节文件缺少 SUMERU_STATUS 标记 | 扫描章节内容推断状态，添加标记 |
| status.json 与实际章节不一�?| 以实际章节为准更�?status.json |
| 章节命名不规�?| 提示用户手动重命�?|

---

## 二、迁移流�?
```
用户调用 /sumeru-migrate
    �?    �?┌─────────────────────────────────────�?�?第一阶段：项目扫�?                   �?�?- 扫描目录结构                        �?�?- 识别旧路�?                         �?�?- 检查配置文�?                       �?�?- 检查章节任务卡字段                  �?└─────────────────────────────────────�?    �?    �?┌─────────────────────────────────────�?�?第二阶段：生成迁移计�?               �?�?- 列出需要修复的项目                  �?�?- 按优先级排序                        �?�?- 询问用户确认                        �?└─────────────────────────────────────�?    �?    �?┌─────────────────────────────────────�?�?第三阶段：执行迁�?                   �?�?- 迁移旧路�?                         �?�?- 补齐配置文件                        �?�?- 补齐目录结构                        �?�?- 补齐章节任务卡字�?                 �?�?- 生成人物�?                         �?└─────────────────────────────────────�?    �?    �?┌─────────────────────────────────────�?�?第四阶段：生成报�?                   �?�?- 迁移报告                            �?�?- 更新 status.json                    �?�?- 记录 changelog                      �?└─────────────────────────────────────�?```

---

## 三、project.json 推断规则

�?`.sumeru/project.json` 不存在时，根据已有文件推断：

| 推断来源 | 推断字段 |
|----------|----------|
| `plan.md` 标题 | `title` |
| `plan.md` 类型标签 | `genre` |
| `plan.md` 受众定位 | `audience` |
| `plan.md` 目标平台 | `targetPlatform` |
| `outline.md` 分卷�?| `plannedChapters` |
| `chapters/` 已有文件 | `currentStage` |
| 章节平均字数 | `chapterWordRange` |

**推断不出的字�?*：使用默认值，标记�?`inferred`�?
---

## 四、status.json 推断规则

�?`.sumeru/status.json` 不存在时，根据已有文件推断：

| 推断来源 | 推断逻辑 |
|----------|----------|
| `chapters/` 文件数量 | 已完成章节数 |
| 章节首行 SUMERU_STATUS | 章节状态（drafted/polished/finalized�?|
| `.sumeru/reviews/` 是否存在 | 是否经过审查 |
| `publish/` 是否存在 | 是否已导�?|

---

## 五、旧路径迁移详细规则

### 5.1 chapter-outlines.json �?chapters.json

```javascript
// 迁移逻辑
1. 读取 .sumeru/outline/chapter-outlines.json
2. 解析每个章节的基本信息（chapter, title, purpose, events�?3. 缺少的必填字段标记为 "待补�?
4. 写入 outlines/chapters.json
5. 备份旧文件到 .sumeru/backup/
```

### 5.2 issues/index.json �?issues.md

```markdown
# 迁移逻辑
1. 读取 .sumeru/issues/index.json
2. 按严重程度分�?3. 转换�?Markdown 格式
4. 写入 .sumeru/issues.md
5. 备份旧文件到 .sumeru/backup/
```

### 5.3 docs/ �?plan.md

```markdown
# 迁移逻辑
1. 读取 docs/requirements.md（需求）
2. 读取 docs/glossary.md（术语）
3. 读取 docs/style-guide.md（风格）
4. 合并�?plan.md 对应章节
5. 备份旧文件到 .sumeru/backup/
```

---

## 六、人物卡生成规则

�?`plan.md` �?`outline.md` 提取人物信息�?
### 提取来源
1. `plan.md` 人物设定部分
2. `outline.md` 主要人物列表
3. `outline.md` 人物关系描述
4. 已有章节中的人物描写

### 生成格式

```markdown
# {人物名}

## 基础信息
- **姓名**：{从大纲提取}
- **年龄**：{从大纲提取或推断}
- **身份**：{从大纲提取}
- **外貌特征**：{从章节描写提取，或标�?待补�?}

## 性格画像
- **核心性格**：{从大纲提取}
- **说话风格**：{从章节对话提取，或标�?待补�?}
- **行为习惯**：{从章节描写提取，或标�?待补�?}
- **内在矛盾**：{从大纲推断，或标�?待补�?}

## 人物弧光
- **起点状�?*：{从大纲提取}
- **关键转折**：{从大纲提取}
- **终点状�?*：{从大纲提取}

## 核心驱动�?- **核心欲望**：{从大纲提取}
- **核心恐惧**：{从大纲推断}

## 人物关系
| 对象 | 关系 | 当前状�?|
|------|------|----------|
| {从大纲提取} | {从大纲提取} | {从大纲提取} |

## 战力/能力
- **能力等级**：{从大纲提取或推断}
- **特殊技�?*：{从大纲提取}

## 人物标签
`#{类型}` `#{�?阶段}`
```

---

## 七、迁移报告格�?
```markdown
# 项目迁移报告

## 迁移概要
- **迁移时间**：{timestamp}
- **项目名称**：{title}
- **迁移模式**：{完整迁移/仅检�?仅迁移路径}

## 检查结�?
### 项目配置
| 项目 | 状�?| 说明 |
|------|------|------|
| project.json | �?已存�?/ 🔧 已生�?/ �?生成失败 | {说明} |
| status.json | �?已存�?/ 🔧 已生�?| {说明} |

### 目录结构
| 目录 | 状�?|
|------|------|
| chapters/ | �?已存�?/ 🔧 已创�?|
| characters/ | �?已存�?/ 🔧 已创�?|
| outlines/ | �?已存�?/ 🔧 已创�?|

### 旧路径迁�?| 旧路�?| 新路�?| 状�?|
|--------|--------|------|
| .sumeru/outline/chapter-outlines.json | outlines/chapters.json | �?已迁�?/ ⚠️ 需手动处理 |

### 章节任务�?| 章节 | 缺失字段 | 状�?|
|------|----------|------|
| 001 | �?| �?完整 |
| 002 | openingHook, freshnessHook | 🔧 已补�?/ ⚠️ 待补�?|

### 人物�?| 人物 | 状�?|
|------|------|
| 主角 | �?已生�?|
| 反派 | ⚠️ 待补充详�?|

## 待办事项
- [ ] {需要用户手动处理的事项}

## 下一步建�?- {建议用户执行的操作}
```

---

## 八、数据持久化

**用户可见输出**�?- `migration-report.md`：迁移报�?
**中间数据**�?- `.sumeru/backup/`：旧文件备份
- `.sumeru/migration.json`：迁移记�?
---

## 九、与其他 Skill 配合

- **前置**：无（可直接调用�?- **后续**：迁移完成后可继续使�?`sumeru-worldbuilder` 恢复创作，或使用其他 Skill 继续

---

## 十、独立调用自�?
1. 定位项目根目�?2. 执行项目扫描
3. 生成迁移计划
4. 询问用户确认
5. 执行迁移
6. 生成报告
7. 更新 status.json �?changelog
