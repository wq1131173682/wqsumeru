r"""定量统计 scoring-criteria.json 中被替换为 ASCII 引号的损坏点。

判据：一行形如 `"key": "值",`，把最外层 JSON 引号剥掉后，
值内若仍出现 `"`，即为未转义引号（原文应为中文引号 “”）。
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
p = ROOT / "skills/wq-score/config/scoring-criteria.json"
lines = p.read_text(encoding="utf-8").split("\n")

# 匹配:  缩进 "键": "……"  [,]
PAT = re.compile(r'^(\s*"[^"]+"\s*:\s*)"(.*)"(\s*,?)\s*$')

bad = []
for i, ln in enumerate(lines, start=1):
    m = PAT.match(ln)
    if not m:
        continue
    inner = m.group(2)
    if '"' in inner:
        bad.append((i, inner, ln))

print(f"受影响行数 = {len(bad)}")
print()
for i, inner, ln in bad:
    n = inner.count('"')
    print(f"L{i}  未转义引号 {n} 个")
    print(f"    原文: {ln.strip()[:130]}")
    # 生成建议：把值内的 ASCII 引号按出现顺序替换为 “ ”
    parts = inner.split('"')
    rebuilt = ""
    for k, seg in enumerate(parts):
        rebuilt += seg
        if k < len(parts) - 1:
            rebuilt += "\u201C" if k % 2 == 0 else "\u201D"
    print(f"    建议: {rebuilt[:130]}")
    print()

print("=" * 74)
print("若修复这些引号，文件能否解析？")
print("=" * 74)
text = "\n".join(lines)
import json
for i, inner, ln in bad:
    parts = inner.split('"')
    rebuilt = ""
    for k, seg in enumerate(parts):
        rebuilt += seg
        if k < len(parts) - 1:
            rebuilt += "\u201C" if k % 2 == 0 else "\u201D"
    text = text.replace(f'"{inner}"', f'"{rebuilt}"', 1)

try:
    data = json.loads(text)
    print("  ✅ 修复后 JSON 合法")
    print(f"  顶层键：{sorted(data.keys())}")
    for k, v in data.items():
        if isinstance(v, dict):
            print(f"    {k}: dict({len(v)}) keys={list(v.keys())[:8]}")
        elif isinstance(v, list):
            print(f"    {k}: list[{len(v)}]")
except json.JSONDecodeError as e:
    print(f"  ❌ 仍有错误：{e.msg} @ L{e.lineno}")
