# 文档命令实测（自动抽取）

夹具：`tests\_tmp_doccmd`（含 chapters/、outlines/chapters.json、.sumeru/continuity/consistency-rules.json、project.json）

共执行 **16** 条命令，失败 **0** 条。

| 退出码 | 来源 | 命令 |
|---|---|---|
| 1 | `skills/wq-polish/SKILL.md:280` | `D:/openclaw/workspace/wqsumeru/skills/wq-review/scripts/anti-ai-scan.py chapters --chapters 001 --output .sumeru/polish --quiet` |
| 1 | `skills/wq-review/SKILL.md:65` | `D:/openclaw/workspace/wqsumeru/skills/wq-review/scripts/anti-ai-scan.py chapters --chapters 001 --project . --quiet` |
| 0 | `skills/wq-review/SKILL.md:96` | `D:/openclaw/workspace/wqsumeru/skills/wq-review/scripts/continuity-check.py .sumeru/continuity --quiet` |
| 0 | `skills/wq-review/SKILL.md:97` | `D:/openclaw/workspace/wqsumeru/skills/wq-review/scripts/foreshadowing-tracker.py .sumeru/continuity --quiet` |
| 1 | `skills/wq-review/SKILL.md:98` | `D:/openclaw/workspace/wqsumeru/skills/wq-review/scripts/anti-ai-scan.py chapters/ --output .sumeru/review --quiet` |
| 0 | `skills/wq-review/SKILL.md:99` | `D:/openclaw/workspace/wqsumeru/skills/wq-review/scripts/chapter-word-counter.py --dir chapters/ --quiet` |
| 1 | `skills/wq-review/SKILL.md:164` | `D:/openclaw/workspace/wqsumeru/skills/wq-review/scripts/anti-ai-scan.py chapters/` |
| 0 | `skills/wq-review/SKILL.md:417` | `D:/openclaw/workspace/wqsumeru/skills/wq-review/scripts/continuity-check.py .sumeru/continuity` |
| 3 | `skills/wq-review/SKILL.md:420` | `D:/openclaw/workspace/wqsumeru/skills/wq-review/scripts/continuity-check.py .sumeru/volumes/vol-N/continuity` |
| 3 | `skills/wq-review/SKILL.md:422` | `D:/openclaw/workspace/wqsumeru/skills/wq-review/scripts/foreshadowing-tracker.py .sumeru/volumes/vol-N/continuity` |
| 1 | `skills/wq-revise/SKILL.md:206` | `D:/openclaw/workspace/wqsumeru/skills/wq-review/scripts/anti-ai-scan.py chapters --chapters 001 --quiet` |
| 1 | `skills/wq-revise/SKILL.md:214` | `D:/openclaw/workspace/wqsumeru/skills/wq-review/scripts/anti-ai-scan.py chapters --chapters 001 --output .sumeru/revise --quiet` |
| 0 | `skills/wq-revise/SKILL.md:215` | `D:/openclaw/workspace/wqsumeru/skills/wq-review/scripts/continuity-check.py .sumeru/continuity --chapters 001 --quiet` |
| 0 | `skills/wq-write/SKILL.md:452` | `D:/openclaw/workspace/wqsumeru/skills/wq-review/scripts/foreshadowing-tracker.py .sumeru/continuity 1 --quiet` |
| 1 | `skills/wq-write/SKILL.md:471` | `D:/openclaw/workspace/wqsumeru/skills/wq-review/scripts/anti-ai-scan.py chapters --outlines outlines/chapters.json --output .sumeru/review --quiet` |
| 3 | `skills/wq-write/SKILL.md:594` | `D:/openclaw/workspace/wqsumeru/skills/wq-review/scripts/foreshadowing-tracker.py    .sumeru/volumes/vol-N/continuity 1 --quiet` |