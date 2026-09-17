r"""合并行（换行丢失）检测器。

损坏特征：原本应换行的内容被拼到同一行。高置信模式：
  P1  标题行后直接跟正文：`### 标题内容...`（标题内出现列表/句号且无空格分隔）
  P2  加粗标签 + 括号 + 连字符：`**标签**）- 内容`
  P3  编号项粘连：`1. ...2. ...` 或 `5. ...6. ...`
  P4  加粗标签粘连：`**甲**：xxx**乙**：yyy`
  P5  项目符号粘连：`- xxx- yyy`（需两项都较长，降低误报）

输出报告，不自动修改（避免误伤）。
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
OUT = ROOT / "tests" / "merged-lines.md"

findings = []

for md in sorted(SKILLS.rglob("*.md")):
    rel = md.relative_to(ROOT).as_posix()
    lines = md.read_text(encoding="utf-8").split("\n")
    in_code = False
    for i, ln in enumerate(lines, start=1):
        if ln.lstrip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        s = ln.strip()

        # P1 标题吞并正文：标题行里出现 "）- " / "：- " / 多个 "- " 列表项
        if re.match(r"^#{1,6} ", s):
            body = s.lstrip("#").strip()
            if re.search(r"\*\*[^*]+\*\*[）)]", body) or body.count("- ") >= 2 \
               or re.search(r"[\u4e00-\u9fff]-\s*`", body):
                findings.append((rel, i, "P1_标题吞并", s[:120]))

        # P2 加粗标签 + 括号 + 连字符
        if re.search(r"\*\*[^*\n]{2,20}\*\*\s*[）)]\s*-\s", s):
            findings.append((rel, i, "P2_标签括号粘连", s[:120]))

        # P3 编号项粘连
        if re.search(r"\d+\.\s+\*\*[^*]+\*\*[：:][^\n]*?\d+\.\s+\*\*", s):
            findings.append((rel, i, "P3_编号粘连", s[:120]))

        # P4 加粗标签粘连（同一行出现两个 **xx**：）
        if len(re.findall(r"\*\*[^*\n]{2,20}\*\*\s*[：:]", s)) >= 2:
            findings.append((rel, i, "P4_标签粘连", s[:120]))

        # P5 项目符号粘连（两项均 ≥8 字，排除表格）
        if s.startswith("- ") and not s.startswith("- |"):
            m = re.search(r"[\u4e00-\u9fff][-–]\s+[\u4e00-\u9fff]", s)
            if m and len(s) > 40:
                findings.append((rel, i, "P5_项目符号粘连", s[:120]))

from collections import Counter
cnt = Counter(f[2] for f in findings)

print(f"合并行候选 = {len(findings)}")
for k, v in cnt.most_common():
    print(f"  {k:18s} {v}")

print()
print("=== 明细 ===")
for rel, i, kind, txt in sorted(findings, key=lambda x: (x[2], x[0], x[1])):
    print(f"  [{kind}] {rel}:{i}")
    print(f"      {txt}")

report = ["# 合并行（换行丢失）检测报告", "",
          f"候选 {len(findings)} 处。**仅供人工确认，未自动修改。**", "",
          "| 类型 | 数量 |", "|---|---|"]
for k, v in cnt.most_common():
    report.append(f"| {k} | {v} |")
report.append("")
report.append("## 明细")
report.append("")
report.append("| 类型 | 文件 | 行 | 内容 |")
report.append("|---|---|---|---|")
for rel, i, kind, txt in sorted(findings, key=lambda x: (x[2], x[0], x[1])):
    report.append(f"| {kind} | `{rel}` | {i} | `{txt.replace('|', chr(92)+'|')}` |")
OUT.write_text("\n".join(report), encoding="utf-8")
print()
print("report ->", OUT)
