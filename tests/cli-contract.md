# 脚本 CLI 契约复测

Python: `C:\Program Files\Python312\python.exe`

| # | 用例 | 依据 | 退出码 | 是否有输出 | 结论 |
|---|---|---|---|---|---|
| 1 | `skills/wq-review/scripts/anti-ai-scan.py --help` | 脚本自身 | 0 | Y | OK |
| 2 | `skills/wq-review/scripts/anti-ai-scan.py chapters/ --quiet` | wq-rules/SKILL.md:609 | 2 | Y | 非零(2) |
| 3 | `skills/wq-review/scripts/continuity-check.py chapters/` | wq-review/SKILL.md:82 | 0 | Y | OK |
| 4 | `skills/wq-review/scripts/continuity-check.py .sumeru/continuity` | wq-write/SKILL.md:476 | 0 | Y | OK |
| 5 | `skills/wq-review/scripts/foreshadowing-tracker.py chapters/` | wq-review/SKILL.md:83 | 0 | Y | OK |
| 6 | `skills/wq-review/scripts/foreshadowing-tracker.py .sumeru/continuity 42 --quiet` | wq-write/SKILL.md:452 | 0 | N | OK |
| 7 | `skills/wq-review/scripts/chapter-word-counter.py chapters/ --quiet` | wq-review/SKILL.md:85 | 2 | Y | 非零(2) |
| 8 | `skills/wq-review/scripts/chapter-word-counter.py --dir chapters/ --quiet` | 脚本自身 | 1 | Y | 非零(1) |
| 9 | `skills/wq-finalize/scripts/platform-export.py --help` | 脚本自身 | 1 | Y | 非零(1) |
| 10 | `skills/wq-finalize/scripts/platform-export.py` | 脚本自身 | 1 | Y | 非零(1) |
| 11 | `skills/wq-finalize/scripts/format-validator.py --help` | 脚本自身 | 0 | Y | OK |
| 12 | `skills/wq-finalize/scripts/spell-check.py --help` | 脚本自身 | 0 | Y | OK |
| 13 | `skills/wq-review/scripts/continuity-check.py --help` | 脚本自身 | 0 | Y | OK |
| 14 | `skills/wq-review/scripts/foreshadowing-tracker.py --help` | 脚本自身 | 0 | Y | OK |
| 15 | `skills/wq-rules/scripts/text_utils.py` | wq-rules/scripts | 0 | Y | OK |

## 输出明细

### 1. anti-ai-scan --help

- 依据：脚本自身
- 退出码：`0`
- stdout（前 12 行）：
```text
usage: anti-ai-scan.py [-h] [--outlines OUTLINES] [--output OUTPUT] [--quiet]
                       [--strict] [--filter FILTER] [--project PROJECT]
                       [--no-cache]
                       chapters_dir

wq-review 反 AI / 反水文扫描

positional arguments:
  chapters_dir         章节目录，例如 .sumeru/chapters/

options:
  -h, --help           show this help message and exit
```
- stderr（前 6 行）：
```text
(空)
```

### 2. anti-ai-scan <dir>  (wq-rules 写法)

- 依据：wq-rules/SKILL.md:609
- 退出码：`2`
- stdout（前 12 行）：
```text
(空)
```
- stderr（前 6 行）：
```text
❌ 目录不存在: chapters
```

### 3. continuity-check chapters/  (wq-review 写法)

- 依据：wq-review/SKILL.md:82
- 退出码：`0`
- stdout（前 12 行）：
```text
正在检查剧情一致性: chapters/

============================================================
剧情一致性检查结果
============================================================
错误: 目录不存在: chapters/
```
- stderr（前 6 行）：
```text
(空)
```

### 4. continuity-check .sumeru/continuity  (wq-write 写法)

- 依据：wq-write/SKILL.md:476
- 退出码：`0`
- stdout（前 12 行）：
```text
正在检查剧情一致性: .sumeru/continuity

============================================================
剧情一致性检查结果
============================================================
错误: 目录不存在: .sumeru/continuity
```
- stderr（前 6 行）：
```text
(空)
```

### 5. foreshadowing-tracker chapters/  (wq-review 写法)

- 依据：wq-review/SKILL.md:83
- 退出码：`0`
- stdout（前 12 行）：
```text
正在追踪伏笔状态: chapters/ (当前章节: 0)

============================================================
伏笔追踪报告
============================================================
错误: 目录不存在: chapters/
```
- stderr（前 6 行）：
```text
(空)
```

### 6. foreshadowing-tracker .sumeru/continuity  (wq-write 写法)

- 依据：wq-write/SKILL.md:452
- 退出码：`0`
- stdout（前 12 行）：
```text
(空)
```
- stderr（前 6 行）：
```text
(空)
```

### 7. chapter-word-counter chapters/ --quiet  (wq-review 写法)

- 依据：wq-review/SKILL.md:85
- 退出码：`2`
- stdout（前 12 行）：
```text
(空)
```
- stderr（前 6 行）：
```text
usage: chapter-word-counter.py [-h] [--dir DIR] [--pattern PATTERN]
                               [--min MIN] [--max MAX] [--warn-min WARN_MIN]
                               [--warn-max WARN_MAX] [--output OUTPUT]
                               [--quiet]
chapter-word-counter.py: error: unrecognized arguments: chapters/
```

### 8. chapter-word-counter --dir chapters/  (真实 CLI)

- 依据：脚本自身
- 退出码：`1`
- stdout（前 12 行）：
```text
❌ 执行出错: 章节目录不存在: chapters/
```
- stderr（前 6 行）：
```text
(空)
```

### 9. platform-export --help

- 依据：脚本自身
- 退出码：`1`
- stdout（前 12 行）：
```text
用法: python platform-export.py <章节目录> <格式|repair> [--output <输出目录>] [--project <项目根目录>] [--quiet]

格式: md, txt（clean 已废弃）
  md:     Markdown 格式导出（publish/md/）
  txt:    纯文本格式导出（publish/txt/）
  repair: 按新规则重新导出 md + txt（先清理旧结构 clean/、chapters/ 子目录、纯数字旧命名）

目录结构:
  非分卷: publish/md/第001章-标题.md + full.md  （txt 同理）
  分卷:   publish/md/vol-001/第001章-标题.md + vol-001/full.md + full.md（全书）

示例:
```
- stderr（前 6 行）：
```text
(空)
```

### 10. platform-export (无参数)

- 依据：脚本自身
- 退出码：`1`
- stdout（前 12 行）：
```text
用法: python platform-export.py <章节目录> <格式|repair> [--output <输出目录>] [--project <项目根目录>] [--quiet]

格式: md, txt（clean 已废弃）
  md:     Markdown 格式导出（publish/md/）
  txt:    纯文本格式导出（publish/txt/）
  repair: 按新规则重新导出 md + txt（先清理旧结构 clean/、chapters/ 子目录、纯数字旧命名）

目录结构:
  非分卷: publish/md/第001章-标题.md + full.md  （txt 同理）
  分卷:   publish/md/vol-001/第001章-标题.md + vol-001/full.md + full.md（全书）

示例:
```
- stderr（前 6 行）：
```text
(空)
```

### 11. format-validator --help

- 依据：脚本自身
- 退出码：`0`
- stdout（前 12 行）：
```text
正在扫描章节目录: --help

============================================================
格式检查结果
============================================================
扫描章节数: 0
发现格式问题总数: 0
```
- stderr（前 6 行）：
```text
(空)
```

### 12. spell-check --help

- 依据：脚本自身
- 退出码：`0`
- stdout（前 12 行）：
```text
正在扫描章节目录: --help

============================================================
错别字检查结果
============================================================
扫描章节数: 0
发现错误总数: 0
```
- stderr（前 6 行）：
```text
(空)
```

### 13. continuity-check --help

- 依据：脚本自身
- 退出码：`0`
- stdout（前 12 行）：
```text
正在检查剧情一致性: --help

============================================================
剧情一致性检查结果
============================================================
错误: 目录不存在: --help
```
- stderr（前 6 行）：
```text
(空)
```

### 14. foreshadowing-tracker --help

- 依据：脚本自身
- 退出码：`0`
- stdout（前 12 行）：
```text
正在追踪伏笔状态: --help (当前章节: 0)

============================================================
伏笔追踪报告
============================================================
错误: 目录不存在: --help
```
- stderr（前 6 行）：
```text
(空)
```

### 15. text_utils.py (作为脚本跑)

- 依据：wq-rules/scripts
- 退出码：`0`
- stdout（前 12 行）：
```text
text_utils self-check OK; dialogue_chars= 6
```
- stderr（前 6 行）：
```text
(空)
```
