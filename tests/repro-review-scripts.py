r"""真实场景复现：项目里 chapters/ 存在，但按 SKILL.md 的写法调用审查脚本。

关心的不是"目录不存在"的报错，而是：
  - 脚本是否静默通过（退出码 0）
  - 是否漏检（本该检查 consistency-rules.json 却检查了 chapters/）
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIX = ROOT / "tests" / "_tmp_project"
OUT = ROOT / "tests" / "repro-review-scripts.md"
PY = sys.executable

if FIX.exists():
    shutil.rmtree(FIX)
(FIX / "chapters").mkdir(parents=True)
(FIX / ".sumeru" / "continuity").mkdir(parents=True)

# 一个最小章节
(FIX / "chapters" / "001-觉醒.md").write_text(
    "<!-- SUMERU_STATUS: chapter=001, status=drafted -->\n\n"
    "他走进房间。\n桌上放着一封信。\n他拿起信封，手指微微颤抖。\n",
    encoding="utf-8",
)

# 关键的 continuity 数据 —— 放在正确位置，且故意制造一个 critical 冲突
# 同一人物同时在两个地点（unique_location）
rules = {
    "characters": {
        "苏瑾": {"status": "healthy", "location": "北域冰原"},
        "苏瑾_分身": {"status": "healthy", "location": "南疆火域"},
    },
    "items": {},
    "foreshadowing": {},
    "timeline": {"current_location": "北域冰原", "current_chapter": 1},
}
(FIX / ".sumeru" / "continuity" / "consistency-rules.json").write_text(
    json.dumps(rules, ensure_ascii=False, indent=2), encoding="utf-8")

CASES = [
    ("按 wq-review/SKILL.md:82 写法（错误）",
     ["skills/wq-review/scripts/continuity-check.py", "chapters/"],
     FIX),
    ("按 wq-write/SKILL.md:476 写法（正确）",
     ["skills/wq-review/scripts/continuity-check.py", ".sumeru/continuity"],
     FIX),
    ("按 wq-review/SKILL.md:83 写法（错误）",
     ["skills/wq-review/scripts/foreshadowing-tracker.py", "chapters/", "--quiet"],
     FIX),
    ("按 wq-review/SKILL.md:85 写法（错误）",
     ["skills/wq-review/scripts/chapter-word-counter.py", "chapters/", "--quiet"],
     FIX),
    ("anti-ai-scan 按 SKILL.md:84 写法",
     ["skills/wq-review/scripts/anti-ai-scan.py", "chapters/", "--output", ".sumeru/review", "--quiet"],
     FIX),
]

report = ["# 真实场景复现：审查脚本按 SKILL.md 调用", "",
          f"夹具目录：`{FIX.relative_to(ROOT)}`",
          "- `chapters/001-觉醒.md`（已存在）",
          "- `.sumeru/continuity/consistency-rules.json`（含 1 个 critical 冲突：苏瑾 / 苏瑾_分身 分处两地）",
          ""]

print(f"{'case':44s} {'rc':>4s}  verdict")
print("-" * 90)
for label, cmd, cwd in CASES:
    full = [PY, "-X", "utf8"] + [str(ROOT / c) if c.startswith("skills") else c for c in cmd]
    r = subprocess.run(full, cwd=str(cwd), capture_output=True, timeout=120)
    so = r.stdout.decode("utf-8", errors="replace")
    se = r.stderr.decode("utf-8", errors="replace")
    combined = so + se
    silent = "目录不存在" in combined or "未找到" in combined
    verdict = []
    if r.returncode == 0 and silent:
        verdict.append("!! 退出码0 但实际没检查到目录")
    if r.returncode == 0 and "冲突" in combined and "0" in combined:
        verdict.append("可能漏检")
    if r.returncode != 0:
        verdict.append(f"失败")
    if not verdict:
        verdict.append("正常")
    print(f"{label:44s} {r.returncode:>4d}  {' / '.join(verdict)}")

    report.append(f"## {label}")
    report.append("")
    report.append(f"命令：`python {' '.join(cmd)}`（cwd = 项目根）")
    report.append(f"退出码：`{r.returncode}`")
    report.append("")
    report.append("stdout：")
    report.append("```text")
    report.extend((so.strip() or "(空)").splitlines()[:14])
    report.append("```")
    if se.strip():
        report.append("stderr：")
        report.append("```text")
        report.extend(se.strip().splitlines()[:8])
        report.append("```")
    report.append("")

# 反证：正确的调用确实能发现 critical 冲突吗？
report.append("## 反证：continuity-check 用正确目录时能否发现冲突")
report.append("")
r = subprocess.run([PY, "-X", "utf8", str(ROOT / "skills/wq-review/scripts/continuity-check.py"),
                    ".sumeru/continuity"],
                   cwd=str(FIX), capture_output=True, timeout=120)
so = r.stdout.decode("utf-8", errors="replace")
report.append(f"退出码：`{r.returncode}`")
report.append("")
report.append("```text")
report.extend(so.strip().splitlines()[:30])
report.append("```")

OUT.write_text("\n".join(report), encoding="utf-8")

shutil.rmtree(FIX)
print()
print("fixture cleaned:", not FIX.exists())
print("report ->", OUT)
