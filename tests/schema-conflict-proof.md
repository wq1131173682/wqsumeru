# 决定性验证：consistency-rules.json 的两套 schema

同一个文件 `.sumeru/continuity/consistency-rules.json`，两套互不兼容的 schema：

| | schema A（wq-rules 权威文档） | schema B（脚本自带模板） |
|---|---|---|
| `timeline` | **对象** `{current_location, current_chapter}` | **数组** `[{chapter, event, ...}]` |
| 人物位置 | `characters`（对象） | `character_locations`（数组） |
| 道具 | `items`（对象） | `weapons` / `key_items`（数组） |
| 伏笔 | `foreshadowing`（对象） | `foreshadowing`（数组） |
| 人物状态 | 无 | `character_state`（数组） |

> 脚本自带模板 `consistency-rules-template.json` **未被任何 SKILL.md 引用**。

## A：wq-rules 权威 schema

- 依据：按唯一约束源文档书写
- 退出码：`0`，检出冲突总数：**0**

```text
正在检查剧情一致性: .sumeru/continuity

============================================================
剧情一致性检查结果
============================================================
检查规则数: 6
发现冲突总数: 0
```

## B：脚本自带模板 schema

- 依据：按 consistency-rules-template.json 书写
- 退出码：`2`，检出冲突总数：**1**

```text
正在检查剧情一致性: .sumeru/continuity

============================================================
剧情一致性检查结果
============================================================
检查规则数: 6
发现冲突总数: 1

冲突严重程度统计:
  critical: 1

冲突详情:

  [1] [CRITICAL] unique_location
      人物'苏瑾'同时出现在多个地点: 南疆火域, 北域冰原
```

## 结论

1. 按 **wq-rules（唯一全局约束源）** 书写的 `consistency-rules.json`，
   `timeline` 是对象 → `check_timeline_order` 遍历出字符串键 → `'str' object has no attribute 'get'` **崩溃**，并被当作一条冲突记录。
2. 该 schema 下 `characters` 是对象，而检查器读的是 `character_locations` 数组 → **植入的 critical 冲突（同一人物两地点）完全未被检出**。
3. 脚本自带模板的数组 schema 才是脚本真正支持的结构，但**没有任何 SKILL.md 引用它**。
4. 两种情况下退出码都是 **0** —— 父Agent无法通过退出码发现问题。