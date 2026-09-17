r"""验证修复建议：按修正后的命令调用，4 个审查脚本是否都能正常工作。

这确保报告里给出的修复方案是经过实测的，而非推测。
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIX = ROOT / "tests" / "_tmp_fixverify"
OUT = ROOT / "tests" / "fix-verification.md"
PY = sys.executable

if FIX.exists():
    shutil.rmtree(FIX)
(FIX / "chapters").mkdir(parents=True)
(FIX / ".sumeru" / "continuity").mkdir(parents=True)
(FIX / ".sumeru" / "review").mkdir(parents=True)

(FIX / "chapters" / "001-觉醒.md").write_text(
    "<!-- SUMERU_STATUS: chapter=001, status=drafted -->\n\n"
    "「你来了。」他说。\n他走进房间。\n桌上放着一封信。\n他拿起信封，手指微微颤抖。\n",
    encoding="utf-8")
(FIX / "chapters" / "002-试炼.md").write_text(
    "<!-- SUMERU_STATUS: chapter=002, status=drafted -->\n\n"
    "「你来了。」他说。\n他走进房间。\n桌上放着一封信。\n他拿起信封，手指微微颤抖。\n",
    encoding="utf-8")

# 用脚本自带模板的 schema（数组结构），确保检查器不崩溃
(FIX / ".sumeru" / "continuity" / "consistency-rules.json").write_text(
    json.dumps({
        "weapons": [], "active_buffs": [], "key_items": [], "character_state": [],
        "character_locations": [
            {"name": "苏瑾", "current_location": "北域冰原", "since_chapter": 35,
             "previous_locations": []},
            {"name": "苏瑾", "current_location": "南疆火域", "since_chapter": 36,
             "previous_locations": []},
        ],
        "foreshadowing": [
            {"id": "v1", "description": "黑衣人身份", "status": "active",
             "first_appeared": 15, "last_mentioned": 42, "expected_payoff_chapter": 45,
             "payoff_status": "pending", "related_chapters": [15, 42],
             "importance": "high", "reminder": "", "payoff_chapter": None,
             "payoff_detail": None},
        ],
        "timeline": [
            {"chapter": 1, "event": "抵达", "date": "初", "location": "北域冰原",
             "characters": ["苏瑾"]},
            {"chapter": 2, "event": "试炼", "date": "次", "location": "北域冰原",
             "characters": ["苏瑾"]},
        ],
    }, ensure_ascii=False, indent=2), encoding="utf-8")

# 修正后的命令（报告建议）
FIXED = [
    ("continuity-check（修正：continuity 目录）",
     ["skills/wq-review/scripts/continuity-check.py", ".sumeru/continuity", "--quiet"]),
    ("foreshadowing-tracker（修正：continuity 目录 + 当前章号）",
     ["skills/wq-review/scripts/foreshadowing-tracker.py", ".sumeru/continuity", "2", "--quiet"]),
    ("anti-ai-scan（原本就正确）",
     ["skills/wq-review/scripts/anti-ai-scan.py", "chapters/", "--output", ".sumeru/review", "--quiet"]),
    ("chapter-word-counter（修正：--dir）",
     ["skills/wq-review/scripts/chapter-word-counter.py", "--dir", "chapters/", "--quiet"]),
]

report = ["# 修复建议验证", "",
          "按报告建议修正后的命令，在带真实 `chapters/` 与 `consistency-rules.json` 的项目上实测。",
          ""]
print(f"{'case':52s} {'rc':>4s}  结果")
print("-" * 86)
ok = 0
for label, cmd in FIXED:
    full = [PY, "-X", "utf8"] + [str(ROOT / c) if c.startswith("skills") else c for c in cmd]
    r = subprocess.run(full, cwd=str(FIX), capture_output=True, timeout=180)
    so = (r.stdout + r.stderr).decode("utf-8", errors="replace")
    failed = "不存在" in so or "执行失败" in so or "unrecognized" in so
    status = "FAIL" if failed else "OK"
    if not failed:
        ok += 1
    print(f"{label:52s} {r.returncode:>4d}  {status}")

    report.append(f"## {label}")
    report.append("")
    report.append(f"命令：`python {' '.join(cmd)}`")
    report.append(f"退出码：`{r.returncode}`　判定：**{status}**")
    report.append("")
    report.append("```text")
    report.extend(so.strip().splitlines()[:16])
    report.append("```")
    report.append("")

print()
print(f"通过 {ok}/{len(FIXED)}")
report.append("## 总结")
report.append("")
report.append(f"修正后的命令 **{ok}/{len(FIXED)}** 正常执行（无「目录不存在」「规则执行失败」「unrecognized」）。")

OUT.write_text("\n".join(report), encoding="utf-8")
shutil.rmtree(FIX)
print("report ->", OUT)
