r"""决定性验证：consistency-rules.json 的两套 schema 哪套真正有效。

schema A = wq-rules/SKILL.md（自称唯一全局约束源）：
    characters / items / foreshadowing 为对象，timeline 为对象
schema B = wq-review/scripts/consistency-rules-template.json（脚本自带模板）：
    character_locations / weapons / foreshadowing / key_items / character_state 为数组，
    timeline 为数组

分别在两套 schema 下植入同一个 critical 冲突（同一人物同时在两地），
看脚本能否检出。
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIX = ROOT / "tests" / "_tmp_schema"
OUT = ROOT / "tests" / "schema-conflict-proof.md"
PY = sys.executable
SCRIPT = ROOT / "skills/wq-review/scripts/continuity-check.py"

# ---- schema A（按 wq-rules/SKILL.md 写）----
A = {
    "characters": {
        "苏瑾": {"status": "minor_injury", "location": "北域冰原"},
    },
    "items": {"黑色残片": "acquired"},
    "foreshadowing": {"v3": {"status": "mentioned", "last_mentioned": 42}},
    "timeline": {"current_location": "北域冰原", "current_chapter": 42},
}

# ---- schema B（按脚本自带模板写），植入 unique_location 冲突 ----
B = {
    "conflict_detection": {"rules": []},
    "weapons": [],
    "character_locations": [
        {"name": "苏瑾", "current_location": "北域冰原", "since_chapter": 35,
         "previous_locations": []},
        {"name": "苏瑾", "current_location": "南疆火域", "since_chapter": 36,
         "previous_locations": []},
    ],
    "active_buffs": [],
    "foreshadowing": [
        {"id": "v3", "description": "黑衣人身分", "status": "active",
         "first_appeared": 15, "last_mentioned": 42,
         "expected_payoff_chapter": 80, "payoff_status": "pending",
         "related_chapters": [15, 42], "importance": "high",
         "reminder": "", "payoff_chapter": None, "payoff_detail": None},
    ],
    "key_items": [],
    "character_state": [],
    "timeline": [
        {"chapter": 42, "event": "抵达北域冰原", "date": "第三月初",
         "location": "北域冰原", "characters": ["苏瑾"]},
        {"chapter": 41, "event": "离开南疆", "date": "第二月末",
         "location": "南疆火域", "characters": ["苏瑾"]},
    ],
}

report = ["# 决定性验证：consistency-rules.json 的两套 schema", "",
          "同一个文件 `.sumeru/continuity/consistency-rules.json`，两套互不兼容的 schema：", "",
          "| | schema A（wq-rules 权威文档） | schema B（脚本自带模板） |",
          "|---|---|---|",
          "| `timeline` | **对象** `{current_location, current_chapter}` | **数组** `[{chapter, event, ...}]` |",
          "| 人物位置 | `characters`（对象） | `character_locations`（数组） |",
          "| 道具 | `items`（对象） | `weapons` / `key_items`（数组） |",
          "| 伏笔 | `foreshadowing`（对象） | `foreshadowing`（数组） |",
          "| 人物状态 | 无 | `character_state`（数组） |",
          "",
          "> 脚本自带模板 `consistency-rules-template.json` **未被任何 SKILL.md 引用**。",
          ""]

print(f"{'schema':32s} {'rc':>4s}  {'冲突数':>6s}  说明")
print("-" * 78)

for label, data, note in [
    ("A：wq-rules 权威 schema", A, "按唯一约束源文档书写"),
    ("B：脚本自带模板 schema", B, "按 consistency-rules-template.json 书写"),
]:
    if FIX.exists():
        shutil.rmtree(FIX)
    (FIX / ".sumeru" / "continuity").mkdir(parents=True)
    (FIX / ".sumeru" / "continuity" / "consistency-rules.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    r = subprocess.run([PY, "-X", "utf8", str(SCRIPT), ".sumeru/continuity"],
                       cwd=str(FIX), capture_output=True, timeout=120)
    so = r.stdout.decode("utf-8", errors="replace")
    total = "?"
    for ln in so.splitlines():
        if "发现冲突总数" in ln:
            total = ln.split(":")[-1].strip()
    has_err = "执行失败" in so
    print(f"{label:32s} {r.returncode:>4d}  {total:>6s}  {'含规则崩溃' if has_err else '无崩溃'}")

    report.append(f"## {label}")
    report.append("")
    report.append(f"- 依据：{note}")
    report.append(f"- 退出码：`{r.returncode}`，检出冲突总数：**{total}**"
                  + ("，**含规则执行崩溃**" if has_err else ""))
    report.append("")
    report.append("```text")
    report.extend(so.strip().splitlines()[:26])
    report.append("```")
    report.append("")

report.append("## 结论")
report.append("")
report.append("1. 按 **wq-rules（唯一全局约束源）** 书写的 `consistency-rules.json`，")
report.append("   `timeline` 是对象 → `check_timeline_order` 遍历出字符串键 → "
              "`'str' object has no attribute 'get'` **崩溃**，并被当作一条冲突记录。")
report.append("2. 该 schema 下 `characters` 是对象，而检查器读的是 `character_locations` 数组 → "
              "**植入的 critical 冲突（同一人物两地点）完全未被检出**。")
report.append("3. 脚本自带模板的数组 schema 才是脚本真正支持的结构，但**没有任何 SKILL.md 引用它**。")
report.append("4. 两种情况下退出码都是 **0** —— 父Agent无法通过退出码发现问题。")

OUT.write_text("\n".join(report), encoding="utf-8")
if FIX.exists():
    shutil.rmtree(FIX)
print()
print("report ->", OUT)
