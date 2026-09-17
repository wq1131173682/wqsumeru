r"""CLI 契约复测：用 Python 直接驱动子进程，避免 PowerShell 管道假象。

对每个脚本比较「SKILL.md 里的写法」与「脚本真实 CLI」的差异。
结果写入 UTF-8 文件。
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "tests" / "cli-contract.md"
PY = sys.executable

CASES = [
    # (标签, 来源, 命令)
    ("anti-ai-scan --help", "脚本自身", ["skills/wq-review/scripts/anti-ai-scan.py", "--help"]),
    ("anti-ai-scan <dir>  (wq-rules 写法)",
     "wq-rules/SKILL.md:609", ["skills/wq-review/scripts/anti-ai-scan.py", "chapters/", "--quiet"]),
    ("continuity-check chapters/  (wq-review 写法)",
     "wq-review/SKILL.md:82", ["skills/wq-review/scripts/continuity-check.py", "chapters/"]),
    ("continuity-check .sumeru/continuity  (wq-write 写法)",
     "wq-write/SKILL.md:476", ["skills/wq-review/scripts/continuity-check.py", ".sumeru/continuity"]),
    ("foreshadowing-tracker chapters/  (wq-review 写法)",
     "wq-review/SKILL.md:83", ["skills/wq-review/scripts/foreshadowing-tracker.py", "chapters/"]),
    ("foreshadowing-tracker .sumeru/continuity  (wq-write 写法)",
     "wq-write/SKILL.md:452", ["skills/wq-review/scripts/foreshadowing-tracker.py", ".sumeru/continuity", "42", "--quiet"]),
    ("chapter-word-counter chapters/ --quiet  (wq-review 写法)",
     "wq-review/SKILL.md:85", ["skills/wq-review/scripts/chapter-word-counter.py", "chapters/", "--quiet"]),
    ("chapter-word-counter --dir chapters/  (真实 CLI)",
     "脚本自身", ["skills/wq-review/scripts/chapter-word-counter.py", "--dir", "chapters/", "--quiet"]),
    ("platform-export --help", "脚本自身", ["skills/wq-finalize/scripts/platform-export.py", "--help"]),
    ("platform-export (无参数)", "脚本自身", ["skills/wq-finalize/scripts/platform-export.py"]),
    ("format-validator --help", "脚本自身", ["skills/wq-finalize/scripts/format-validator.py", "--help"]),
    ("spell-check --help", "脚本自身", ["skills/wq-finalize/scripts/spell-check.py", "--help"]),
    ("continuity-check --help", "脚本自身", ["skills/wq-review/scripts/continuity-check.py", "--help"]),
    ("foreshadowing-tracker --help", "脚本自身", ["skills/wq-review/scripts/foreshadowing-tracker.py", "--help"]),
    ("text_utils.py (作为脚本跑)", "wq-rules/scripts", ["skills/wq-rules/scripts/text_utils.py"]),
]

out = ["# 脚本 CLI 契约复测", "",
       f"Python: `{PY}`", "",
       "| # | 用例 | 依据 | 退出码 | 是否有输出 | 结论 |",
       "|---|---|---|---|---|---|"]

detail = []
for i, (label, src, cmd) in enumerate(CASES, 1):
    full = [PY, "-X", "utf8"] + cmd
    try:
        r = subprocess.run(full, cwd=str(ROOT), capture_output=True, timeout=120)
        rc = r.returncode
        so = r.stdout.decode("utf-8", errors="replace")
        se = r.stderr.decode("utf-8", errors="replace")
    except subprocess.TimeoutExpired:
        rc, so, se = "TIMEOUT", "", ""
    has = "Y" if (so.strip() or se.strip()) else "N"
    verdict = "OK" if rc == 0 else f"非零({rc})"
    out.append(f"| {i} | `{' '.join(cmd)}` | {src} | {rc} | {has} | {verdict} |")
    detail.append((i, label, src, rc, so, se))

out.append("")
out.append("## 输出明细")
out.append("")
for i, label, src, rc, so, se in detail:
    out.append(f"### {i}. {label}")
    out.append("")
    out.append(f"- 依据：{src}")
    out.append(f"- 退出码：`{rc}`")
    so_t = so.strip() or "(空)"
    se_t = se.strip() or "(空)"
    out.append(f"- stdout（前 12 行）：")
    out.append("```text")
    out.extend(so_t.splitlines()[:12])
    out.append("```")
    out.append(f"- stderr（前 6 行）：")
    out.append("```text")
    out.extend(se_t.splitlines()[:6])
    out.append("```")
    out.append("")

OUT.write_text("\n".join(out), encoding="utf-8")

print(f"{'#':3s} {'rc':>8s}  {'case'}")
for i, label, src, rc, so, se in detail:
    print(f"{i:3d} {str(rc):>8s}  {label}")
print()
print("report ->", OUT)
