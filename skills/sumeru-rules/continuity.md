---
name: sumeru-rules-continuity
description: 剧情统一门禁、一致性冲突检测规则、伏笔生命周期管理
type: skill
---

# 剧情一致性与伏笔管理

> 本文件是 `SKILL.md` 的拆分模块，所有 Skill 共同遵守。

---

## 一、剧情统一门禁

所有写作/重写/润色必须先校验剧情事实再写入。

### 剧情统一检查项

父Agent写入前检查：

1. **承接检查**：本章必须承接上一章实际结尾
2. **人物检查**：位置、伤势、战力、关系与 consistency-rules.json 一致
3. **道具检查**：归属、消耗、损坏状态一致
4. **时间线检查**：事件顺序不倒置；回忆/梦境/插叙显式标记
5. **伏笔检查**：已回收伏笔不重新 active；新伏笔有 ID/首次章节/预期回收方向
6. **任务卡检查**：不违反 `protectedElements` 和 `acceptanceCriteria`

**处理规则：** critical/high 冲突→暂停写入，写 issue 等待仲裁；medium→允许草稿但标记待修复；low→自动修复或记入 changelog

---

## 二、冲突检测规则

| 规则ID | 描述 | 严重程度 |
|--------|------|----------|
| `unique_location` | 同一人物不能同时在两个地点 | critical |
| `destroyed_item_used` | 已毁道具不能再次使用 | critical |
| `foreshadowing_recycled` | 已回收伏笔不能再次 active | high |
| `character_state_regression` | 人物状态不能无原因回退 | high |
| `power_level_consistency` | 战力等级不能无原因跳跃 | medium |
| `timeline_order` | 事件时间线必须有序 | high |

### 检查脚本

```bash
python scripts/continuity-check.py .sumeru/continuity --output continuity-report.json
python scripts/foreshadowing-tracker.py .sumeru/continuity 50 --output foreshadowing-report.json
```

---

## 三、伏笔管理

### 伏笔状态流转

`设置(active) → 推进(mentioned) → 回收(resolved)`，期望回收章节已过时自动提醒

### 伏笔字段

```json
{
  "id": "v1",
  "description": "伏笔描述",
  "status": "active|pending|resolved",
  "first_appeared": 15,
  "last_mentioned": 42,
  "expected_payoff_chapter": 80,
  "importance": "high|medium|low",
  "related_chapters": [15, 28, 42],
  "payoff_chapter": null,
  "payoff_detail": null
}
```

### 管理建议

- **过期提醒**：期望回收章节已过时提醒
- **数量控制**：活跃超过10个时建议回收低优先级
- **新伏笔规划**：近期设置多个新伏笔时规划回收时间
