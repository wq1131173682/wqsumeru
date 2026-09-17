r"""校验 skills/ 下所有 JSON 配置文件的合法性，并检查配置与脚本的键是否对得上。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"

print("=" * 74)
print("[1] JSON 配置文件合法性")
print("=" * 74)
ok, bad = [], []
for p in sorted(SKILLS.rglob("*.json")):
    rel = p.relative_to(ROOT).as_posix()
    raw = p.read_bytes()
    bom = raw[:3] == b"\xef\xbb\xbf"
    try:
        data = json.loads(raw.decode("utf-8"))
        kind = type(data).__name__
        n = len(data) if hasattr(data, "__len__") else "-"
        print(f"  OK    {rel:64s} {kind:6s} n={n}  BOM={bom}")
        ok.append((rel, data))
    except Exception as e:  # noqa: BLE001
        print(f"  FAIL  {rel:64s} {type(e).__name__}: {e}")
        bad.append((rel, str(e)))

print()
print(f"合法 {len(ok)} / 非法 {len(bad)}")

print()
print("=" * 74)
print("[2] anti-ai-thresholds.json 的键 vs 脚本读取的键")
print("=" * 74)
thr = next((d for r, d in ok if r.endswith("anti-ai-thresholds.json")), None)
src = (SKILLS / "wq-review/scripts/anti-ai-scan.py").read_text(encoding="utf-8")
if thr is not None:
    print(f"  配置键：{sorted(thr.keys())}")
    import re
    # 脚本里 cfg.get("xxx") / thresholds.get("xxx") 的键名
    used = sorted(set(re.findall(r'(?:cfg|thr|thresholds|T)\.get\(\s*"([a-zA-Z_0-9]+)"', src)))
    print(f"  脚本读取键：{used}")
    missing = [k for k in used if k not in thr]
    unused = [k for k in thr if k not in used]
    print(f"  脚本读了但配置里没有：{missing}")
    print(f"  配置里有但脚本没读：{unused}")

print()
print("=" * 74)
print("[3] cliche-blacklist.json 结构")
print("=" * 74)
cli = next((d for r, d in ok if r.endswith("cliche-blacklist.json")), None)
if cli is not None:
    print(f"  顶层键：{sorted(cli.keys()) if isinstance(cli, dict) else type(cli)}")
    if isinstance(cli, dict):
        for k, v in cli.items():
            if isinstance(v, list):
                print(f"    {k}: list[{len(v)}] 例: {v[:3]}")
            elif isinstance(v, dict):
                print(f"    {k}: dict keys={sorted(v.keys())[:8]}")

print()
print("=" * 74)
print("[4] scoring-criteria.json 权重和")
print("=" * 74)
sc = next((d for r, d in ok if r.endswith("scoring-criteria.json")), None)
if sc is not None and isinstance(sc, dict):
    print(f"  顶层键：{sorted(sc.keys())}")
    for key in ("dimensions", "weights", "gradeThresholds", "platformStandards"):
        if key in sc:
            v = sc[key]
            print(f"  --- {key} ---")
            if isinstance(v, dict):
                print(f"      keys={list(v.keys())[:12]}")
                nums = {k: x for k, x in v.items() if isinstance(x, (int, float))}
                if nums:
                    print(f"      数值和 = {sum(nums.values())}")
            elif isinstance(v, list):
                print(f"      list[{len(v)}]")
