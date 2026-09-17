# 合并行（换行丢失）检测报告

候选 9 处。**仅供人工确认，未自动修改。**

| 类型 | 数量 |
|---|---|
| P4_标签粘连 | 8 |
| P3_编号粘连 | 1 |

## 明细

| 类型 | 文件 | 行 | 内容 |
|---|---|---|---|
| P3_编号粘连 | `skills/wq-outline/SKILL.md` | 21 | `3. **人物设定**：主角、配角、反派的人物画像、性格、成长线，同步写入`characters/` 人物卡4. **剧情框架**：主线故事、支线剧情、关键节点、高潮安排5. **分卷大纲**：按卷划分剧情阶段，明确每卷核心冲突与目标6. ` |
| P4_标签粘连 | `skills/wq-outline/SKILL.md` | 21 | `3. **人物设定**：主角、配角、反派的人物画像、性格、成长线，同步写入`characters/` 人物卡4. **剧情框架**：主线故事、支线剧情、关键节点、高潮安排5. **分卷大纲**：按卷划分剧情阶段，明确每卷核心冲突与目标6. ` |
| P4_标签粘连 | `skills/wq-outline/SKILL.md` | 320 | `**跨卷检查补充工具**：大纲阶段完成后，建议在 `outline.md` 末尾追加一张**跨卷依赖表**：` |
| P4_标签粘连 | `skills/wq-revise/SKILL.md` | 204 | `4. **轻量评分（v1.5.0 优化）**：不再调用 wq-score（避免重复读全章 × 5 维度）。改用**双指标判定**：` |
| P4_标签粘连 | `skills/wq-worldbuilder/SKILL.md` | 85 | `> **字段 Schema**：`wq-migrate/SKILL.md` §11.5、**状态机语义**：`wq-rules` §状态字段语义对照。` |
| P4_标签粘连 | `skills/wq-write/SKILL.md` | 452 | `1. **伏笔活跃度预检**：调用 `python skills/wq-review/scripts/foreshadowing-tracker.py .sumeru/continuity <current_chapter> --quiet` |
| P4_标签粘连 | `skills/wq-write/SKILL.md` | 469 | `2. **剧情统一校验**：解析 SUMERU_STATUS，与 consistency-rules.json 对比。**分卷模式**：从 `.sumeru/volumes/vol-N/continuity/consistency-rule` |
| P4_标签粘连 | `skills/wq-write/SKILL.md` | 470 | `3. **foreshadowing 增量更新**：遍历 `plot_update.foreshadowing`，对每个提及的伏笔 ID 同步写入 `consistency-rules.json.foreshadowing.<id>.las` |
| P4_标签粘连 | `skills/wq-write/SKILL.md` | 476 | `5. **（可选）连续性冲突检查**：若 `consistency-rules.json` 已有累积状态，调用 `python skills/wq-review/scripts/continuity-check.py .sumeru/con` |