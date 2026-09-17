r"""核实内部矛盾：并行上限、版本号、扫描项计数、pycache。"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"

print("=" * 72)
print("[1] 并行上限矛盾：wq-rules 声明「硬性上限 3，不可突破」")
rules = (SKILLS / "wq-rules/SKILL.md").read_text(encoding="utf-8")
lines = rules.split("\n")
for i, ln in enumerate(lines, 1):
    if "并行上限" in ln or "硬性上限" in ln:
        print(f"  L{i}: {ln.strip()[:110]}")
print("  --- 同一文件后文推荐值 ---")
for i, ln in enumerate(lines, 1):
    if "推荐并行度" in ln or re.search(r"\*\*5\*\*", ln) or "并发" in ln and "→" in ln:
        print(f"  L{i}: {ln.strip()[:110]}")

print()
print("=" * 72)
print("[2] 反AI 扫描项计数：正文称「共 19 项」")
b = re.search(r"### B\. 9 维反 AI 句式扫描.*?\n(.*?)\n### C\.", rules, re.S)
c = re.search(r"### C\. 水文硬指标.*?\n(.*?)\n### D\.", rules, re.S)
b_rows = len(re.findall(r"^\|\s*\d+\s*\|", b.group(1), re.M)) if b else -1
c_rows = len(re.findall(r"^\|\s*\d+\s*\|", c.group(1), re.M)) if c else -1
print(f"  B 表数据行 = {b_rows}")
print(f"  C 表数据行 = {c_rows}")
print(f"  B + C = {b_rows + c_rows}")
claim = re.search(r"共\s*(\d+)\s*项", rules)
print(f"  正文声明 = {claim.group(1) if claim else '?'}")
# 编号重复
b_nums = re.findall(r"^\|\s*(\d+)\s*\|", b.group(1), re.M) if b else []
c_nums = re.findall(r"^\|\s*(\d+)\s*\|", c.group(1), re.M) if c else []
dup = set(b_nums) & set(c_nums)
print(f"  B 编号 = {b_nums}")
print(f"  C 编号 = {c_nums}")
print(f"  重复编号 = {sorted(dup, key=int)}")

print()
print("=" * 72)
print("[3] frontmatter version vs CHANGELOG")
cl = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
for md in sorted(SKILLS.rglob("SKILL.md")):
    t = md.read_text(encoding="utf-8")
    m = re.search(r"^version:\s*(\S+)", t, re.M)
    name = md.parent.name
    v = m.group(1) if m else "?"
    # CHANGELOG 里该技能最后一次提到的版本
    hits = re.findall(rf"`{name}`[^\n]*?(v?\d+\.\d+\.\d+)", cl)
    print(f"  {name:18s} frontmatter={v:8s} changelog_last={hits[-1] if hits else '-'}")

print()
print("=" * 72)
print("[4] __pycache__ 污染")
pyc = sorted(SKILLS.rglob("*.pyc"))
print(f"  .pyc 文件数 = {len(pyc)}")
dirs = sorted({p.parent for p in pyc})
for d in dirs:
    print(f"    {d.relative_to(ROOT)}")

print()
print("=" * 72)
print("[5] 脚本 vs 文档：anti-ai-scan 实际检查码")
scan = (SKILLS / "wq-review/scripts/anti-ai-scan.py").read_text(encoding="utf-8")
codes = sorted(set(re.findall(r'"code":\s*"([a-z_0-9]+)"', scan)))
print(f"  脚本内 code 数 = {len(codes)}")
for c_ in codes:
    print(f"    {c_}")
