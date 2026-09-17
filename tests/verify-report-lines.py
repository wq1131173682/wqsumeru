r"""校验审计报告中引用的行号是否准确。

报告是交付物，其中的 文件:行号 必须可核对。
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "tests" / "AUDIT-REPORT.md"
text = REPORT.read_text(encoding="utf-8")

# 抓取形如 `wq-rules/SKILL.md` L140 或 `skills/...:476` 的引用
refs = set()
for m in re.finditer(r"`([\w\-./]+\.(?:md|py|json))`[^\n]{0,24}?L(\d+)", text):
    refs.add((m.group(1), int(m.group(2))))
for m in re.finditer(r"`([\w\-./]+\.(?:md|py|json)):(\d+)`", text):
    refs.add((m.group(1), int(m.group(2))))

print(f"报告中可解析的 文件:行号 引用 = {len(refs)}")
print()
ok = bad = missing = 0
for rel, line in sorted(refs):
    # 解析路径
    cands = [ROOT / rel, ROOT / "skills" / rel,
             ROOT / rel.replace("skills/", "", 1) if rel.startswith("skills/") else None]
    p = next((c for c in cands if c and c.exists()), None)
    if p is None:
        print(f"  MISSING_FILE  {rel}:{line}")
        missing += 1
        continue
    lines = p.read_text(encoding="utf-8").split("\n")
    if line > len(lines):
        print(f"  OUT_OF_RANGE  {rel}:{line} (文件仅 {len(lines)} 行)")
        bad += 1
        continue
    ok += 1

print()
print(f"行号有效 {ok} / 越界 {bad} / 文件缺失 {missing}")

print()
print("=== 报告中引用的每个行号及其内容（抽样核对）===")
for rel, line in sorted(refs)[:30]:
    cands = [ROOT / rel, ROOT / "skills" / rel]
    p = next((c for c in cands if c.exists()), None)
    if p is None:
        continue
    lines = p.read_text(encoding="utf-8").split("\n")
    if line <= len(lines):
        content = lines[line - 1].strip()[:88]
        print(f"  {rel}:{line}")
        print(f"      {content}")
