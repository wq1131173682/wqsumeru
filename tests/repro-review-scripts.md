# 真实场景复现：审查脚本按 SKILL.md 调用

夹具目录：`tests\_tmp_project`
- `chapters/001-觉醒.md`（已存在）
- `.sumeru/continuity/consistency-rules.json`（含 1 个 critical 冲突：苏瑾 / 苏瑾_分身 分处两地）

## 按 wq-review/SKILL.md:82 写法（错误）

命令：`python skills/wq-review/scripts/continuity-check.py chapters/`（cwd = 项目根）
退出码：`0`

stdout：
```text
正在检查剧情一致性: chapters/

============================================================
剧情一致性检查结果
============================================================
错误: 文件不存在: chapters\consistency-rules.json
```

## 按 wq-write/SKILL.md:476 写法（正确）

命令：`python skills/wq-review/scripts/continuity-check.py .sumeru/continuity`（cwd = 项目根）
退出码：`0`

stdout：
```text
正在检查剧情一致性: .sumeru/continuity

============================================================
剧情一致性检查结果
============================================================
检查规则数: 6
发现冲突总数: 1

冲突严重程度统计:

冲突详情:

  [1] [ERROR] timeline_order
      检查规则'timeline_order'执行失败: 'str' object has no attribute 'get'
```

## 按 wq-review/SKILL.md:83 写法（错误）

命令：`python skills/wq-review/scripts/foreshadowing-tracker.py chapters/ --quiet`（cwd = 项目根）
退出码：`0`

stdout：
```text
(空)
```

## 按 wq-review/SKILL.md:85 写法（错误）

命令：`python skills/wq-review/scripts/chapter-word-counter.py chapters/ --quiet`（cwd = 项目根）
退出码：`2`

stdout：
```text
(空)
```
stderr：
```text
usage: chapter-word-counter.py [-h] [--dir DIR] [--pattern PATTERN]
                               [--min MIN] [--max MAX] [--warn-min WARN_MIN]
                               [--warn-max WARN_MAX] [--output OUTPUT]
                               [--quiet]
chapter-word-counter.py: error: unrecognized arguments: chapters/
```

## anti-ai-scan 按 SKILL.md:84 写法

命令：`python skills/wq-review/scripts/anti-ai-scan.py chapters/ --output .sumeru/review --quiet`（cwd = 项目根）
退出码：`0`

stdout：
```text
⚠️ 反 AI 扫描发现 2 项问题 (critical=0 high=0 medium=2 low=0)
   详见: .sumeru\review\anti-ai-report.md
```
stderr：
```text
💾 缓存已更新: 0 命中, 1 次重新扫描 → cache\anti-ai-scan-cache.json
```

## 反证：continuity-check 用正确目录时能否发现冲突

退出码：`0`

```text
正在检查剧情一致性: .sumeru/continuity

============================================================
剧情一致性检查结果
============================================================
检查规则数: 6
发现冲突总数: 1

冲突严重程度统计:

冲突详情:

  [1] [ERROR] timeline_order
      检查规则'timeline_order'执行失败: 'str' object has no attribute 'get'
```