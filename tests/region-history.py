r"""逐提交比对某个文件的指定行区，找出最后一个"完好版本"与损坏引入提交。

用法: python tests/region-history.py <相对路径> <起始行> <结束行> [锚点文本]
锚点文本用于在版本间定位同一逻辑位置（因为行号会漂移）。
输出 UTF-8 报告 + ASCII 摘要。
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
rel = sys.argv[1]
lo = int(sys.argv[2])
hi = int(sys.argv[3])
anchor = sys.argv[4] if len(sys.argv) > 4 else None

OUT = ROOT / "tests" / "region-history.md"


def git(args):
    r = subprocess.run(args, cwd=str(ROOT), capture_output=True)
    return r.stdout.decode("utf-8", errors="replace"), r.returncode


log, _ = git(["git", "log", "--format=%h|%ad|%s", "--date=short", "--", rel])
commits = [l for l in log.strip().split("\n") if "|" in l]

out = [f"# 行区历史比对：`{rel}` L{lo}-L{hi}", ""]
if anchor:
    out.append(f"锚点：`{anchor}`")
out.append("")
out.append("| 提交 | 日期 | 主题 | 该区行数 | 数字总数 | 损坏字符数 |")
out.append("|---|---|---|---|---|---|")

# 用「数字总数」和「待查损坏字符」做量化指纹
SUSPECT_CHARS = ["\u53ef", "\u5b58", "\u4e3a", "\u9501", "\u4ece", "\u63d0",
                 "\u5c31", "\u5e93"]  # 可 存 为 锁 从 提 就 库

rows = []
for c in commits:
    h, d, s = c.split("|", 2)
    txt, rc = git(["git", "show", f"{h}:{rel}"])
    if rc != 0:
        continue
    lines = txt.split("\n")
    # 定位：优先锚点，其次行号
    start = None
    if anchor:
        for i, ln in enumerate(lines):
            if anchor in ln:
                start = i
                break
    if start is None:
        start = max(0, lo - 1)
    seg = lines[start:start + (hi - lo + 1)]
    digits = sum(ch.isdigit() for ln in seg for ch in ln)
    susp = sum(ln.count(x) for ln in seg for x in SUSPECT_CHARS)
    rows.append((h, d, s.replace("|", "/")[:32], len(seg), digits, susp))
    out.append(f"| `{h}` | {d} | {s.replace('|','/')[:32]} | {len(seg)} | {digits} | {susp} |")

out.append("")
out.append("## 各版本该区原文")
out.append("")
# 从旧到新打印
for h, d, s, n, dg, sp in reversed(rows):
    txt, rc = git(["git", "show", f"{h}:{rel}"])
    lines = txt.split("\n")
    start = None
    if anchor:
        for i, ln in enumerate(lines):
            if anchor in ln:
                start = i
                break
    if start is None:
        start = max(0, lo - 1)
    seg = lines[start:start + (hi - lo + 1)]
    out.append(f"### `{h}` ({d}) — {s}")
    out.append("")
    out.append("```text")
    for i, ln in enumerate(seg, start=start + 1):
        out.append(f"L{i}: {ln}")
    out.append("```")
    out.append("")

OUT.write_text("\n".join(out), encoding="utf-8")

print(f"REGION {rel} L{lo}-{hi} anchor={anchor!r}")
print(f"{'commit':9s} {'date':11s} lines digits suspect  subject")
for h, d, s, n, dg, sp in rows:
    print(f"{h:9s} {d:11s} {n:5d} {dg:6d} {sp:7d}  {s}")
print(f"\nreport -> {OUT}")
