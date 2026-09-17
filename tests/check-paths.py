r"""canonical 路径一致性检查。

wq-rules/SKILL.md 自称 Canonical 路径的唯一来源。
核对各技能引用的路径是否与该来源一致，以及是否真实存在于磁盘。
"""
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
OUT = ROOT / "tests" / "path-consistency.md"

# 关注这些易混淆的路径对
PAIRS = [
    ("章节任务卡", [r"\.sumeru/outlines/chapters\.json", r"(?<!\.sumeru/)outlines/chapters\.json"]),
    ("章节细纲目录", [r"\.sumeru/outline/", r"(?<!\.sumeru/)outlines/"]),
    ("简介", [r"\.sumeru/intro\.md", r"(?<!\.sumeru/)intro\.md"]),
    ("问题清单", [r"\.sumeru/issues\.md", r"\.sumeru/issues/index\.json"]),
    ("审查报告", [r"reviews/review-report\.md", r"\.sumeru/review/"]),
]

rows = defaultdict(list)   # label -> [(file, lineno, text)]
for md in sorted(SKILLS.rglob("*.md")):
    rel = md.relative_to(ROOT).as_posix()
    for i, ln in enumerate(md.read_text(encoding="utf-8").split("\n"), start=1):
        for label, pats in PAIRS:
            for p in pats:
                for m in re.finditer(p, ln):
                    rows[(label, m.group(0))].append((rel, i, ln.strip()[:110]))

report = ["# canonical 路径一致性检查", "",
          "来源：`wq-rules/SKILL.md` §Canonical 路径（L387-402）", ""]

print(f"{'路径形态':46s} {'出现次数':>8s}  涉及文件数")
print("-" * 82)
for (label, pat), hits in sorted(rows.items(), key=lambda x: (x[0][0], x[0][1])):
    files = {h[0] for h in hits}
    print(f"[{label}] {pat:38s} {len(hits):>8d}  {len(files):>3d}")

report.append("## 各路径形态出现情况")
report.append("")
report.append("| 概念 | 路径形态 | 次数 | 文件数 |")
report.append("|---|---|---|---|")
for (label, pat), hits in sorted(rows.items(), key=lambda x: (x[0][0], x[0][1])):
    report.append(f"| {label} | `{pat}` | {len(hits)} | {len({h[0] for h in hits})} |")

report.append("")
report.append("## 明细")
report.append("")
for (label, pat), hits in sorted(rows.items(), key=lambda x: (x[0][0], x[0][1])):
    report.append(f"### [{label}] `{pat}`（{len(hits)} 处）")
    report.append("")
    report.append("| 文件 | 行 | 原文 |")
    report.append("|---|---|---|")
    for rel, i, txt in hits[:40]:
        report.append(f"| `{rel}` | {i} | `{txt.replace('|', chr(92) + '|')}` |")
    report.append("")

# 磁盘实际结构
report.append("## 磁盘实际结构")
report.append("")
for d in (ROOT / ".sumeru",):
    report.append(f"### `{d.relative_to(ROOT)}`")
    report.append("")
    if not d.exists():
        report.append("（不存在）")
    else:
        report.append("```text")
        for p in sorted(d.rglob("*")):
            report.append(str(p.relative_to(ROOT)).replace("\\", "/"))
        report.append("```")
report.append("")

# CLAUDE.md 的说法
claude = ROOT / "CLAUDE.md"
if claude.exists():
    report.append("## CLAUDE.md 的路径声明")
    report.append("")
    report.append("```text")
    report.extend(claude.read_text(encoding="utf-8").splitlines()[:40])
    report.append("```")

OUT.write_text("\n".join(report), encoding="utf-8")
print()
print("report ->", OUT)
