r"""验证 normalize_rules 是否让对象式（wq-rules 权威文档）schema 也能被正确检查。

关键：对象式 schema 下植入一个真实冲突，必须被检出。
  - unique_location：character_locations 需要同一人物两地点。
    对象式 schema 里 characters 是 {name: {location}}，一个 name 只能有一个 location，
    所以"同一人物两地"在对象式下无法直接表达 —— 但人物状态回退（character_state_regression）
    与伏笔重复激活（foreshadowing_recycled）在对象式下是可以表达的，用它们验证。
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIX = ROOT / "tests" / "_tmp_norm"
SCRIPT = ROOT / "skills/wq-review/scripts/continuity-check.py"
PY = sys.executable

CASES = {
    "对象式：伏笔已回收却仍 active（应检出 foreshadowing_recycled）": {
        "characters": {"苏瑾": {"status": "minor_injury", "location": "北域冰原"}},
        "items": {"黑色残片": "acquired"},
        "foreshadowing": {
            "v3": {"status": "active", "payoff_status": "resolved",
                   "last_mentioned": 42, "payoff_chapter": 40},
        },
        "timeline": {"current_location": "北域冰原", "current_chapter": 42},
    },
    "对象式：已毁道具仍在使用（应检出 destroyed_item_used）": {
        "characters": {"苏瑾": {"status": "healthy", "location": "北城"}},
        "items": {"青锋剑": "destroyed"},
        "foreshadowing": {},
        "timeline": {"current_location": "北城", "current_chapter": 10},
    },
    "数组式：同一人物两地点（对照，应检出 unique_location）": {
        "weapons": [], "active_buffs": [], "key_items": [], "character_state": [],
        "character_locations": [
            {"name": "苏瑾", "current_location": "北域冰原", "since_chapter": 35,
             "previous_locations": []},
            {"name": "苏瑾", "current_location": "南疆火域", "since_chapter": 36,
             "previous_locations": []},
        ],
        "foreshadowing": [],
        "timeline": [{"chapter": 1, "event": "抵达", "date": "初",
                      "location": "北域冰原", "characters": ["苏瑾"]}],
    },
}

print(f"{'用例':52s} {'rc':>4s} {'冲突':>5s}  说明")
print("-" * 92)
ok = 0
for label, data in CASES.items():
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
    crashed = "执行失败" in so
    note = "规则崩溃" if crashed else ("检出" if total not in ("0", "?") else "未检出")
    if not crashed and total not in ("0", "?"):
        ok += 1
    print(f"{label:52s} {r.returncode:>4d} {total:>5s}  {note}")

shutil.rmtree(FIX)
print()
print(f"通过 {ok}/{len(CASES)}（要求：无崩溃且检出冲突）")
