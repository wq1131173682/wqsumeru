r"""取证 scoring-criteria.json 的 JSON 损坏：定位所有未转义 ASCII 引号。"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
p = ROOT / "skills/wq-score/config/scoring-criteria.json"
raw = p.read_bytes()
text = raw.decode("utf-8")

print(f"file bytes={len(raw)}  BOM={raw[:3] == b'\xef\xbb\xbf'}")
try:
    json.loads(text)
    print("JSON OK")
except json.JSONDecodeError as e:
    print(f"JSON FAIL: {e.msg} @ line {e.lineno} col {e.colno}")
    lines = text.split("\n")
    for n in range(max(1, e.lineno - 2), min(len(lines), e.lineno + 2) + 1):
        mark = " <<<" if n == e.lineno else ""
        print(f"  L{n}: {lines[n-1]}{mark}")

print()
print("=== 逐行统计：值内出现的 ASCII 双引号（应为中文引号）===")
lines = text.split("\n")
bad = []
for i, ln in enumerate(lines, start=1):
    # 形如  "key": "....."xxx"....."   值内多出的引号
    m = re.match(r'^(\s*"[^"]+"\s*:\s*")(.*)("[,]?)$', ln)
    if not m:
        continue
    inner = m.group(2)
    if '"' in inner:
        cnt = inner.count('"')
        bad.append((i, cnt, ln.strip()[:120]))
        print(f"  L{i}: 值内 {cnt} 个未转义引号")
        print(f"       {ln.strip()[:120]}")

print()
print(f"受影响行数 = {len(bad)}")

print()
print("=== 中文引号 vs ASCII 引号 统计 ===")
print(f"  中文左引号 “ = {text.count(chr(0x201C))}")
print(f"  中文右引号 ” = {text.count(chr(0x201D))}")
print(f"  ASCII 双引号 \" = {text.count(chr(0x22))}（其中大部分是 JSON 结构引号）")

# 其他 JSON 是否也有同类问题
print()
print("=== 全仓库 JSON：中文引号使用情况（对照）===")
for q in sorted((ROOT / "skills").rglob("*.json")):
    t = q.read_bytes().decode("utf-8", errors="replace")
    lq, rq = t.count(chr(0x201C)), t.count(chr(0x201D))
    try:
        json.loads(t)
        st = "OK"
    except json.JSONDecodeError as e:
        st = f"FAIL L{e.lineno}"
    rel = q.relative_to(ROOT).as_posix()
    flag = "  <== 含中文引号" if lq or rq else ""
    print(f"  {st:12s} “={lq:3d} ”={rq:3d}  {rel}{flag}")
