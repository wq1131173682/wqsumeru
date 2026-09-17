r"""损坏签名检测器（第二版）：机械化可证的证据。

检测项：
  1. 代码块中的 JSON 语法错误（损坏导致引号/括号缺失）
  2. 不合理的数字（前导零、位数缺失），如 "前00字"、"≥00存"、"0-150章"
  3. 空表格单元格（内容丢失）：`| |` 或 `||`
  4. 全角括号不平衡 / 「」未闭合（重复第一版但统一在此）
  5. 行内混排：标题吞并正文

输出写 UTF-8 文件。
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "tests" / "corruption-signatures.md"

findings = []

for md in sorted((ROOT / "skills").rglob("*.md")):
    rel = md.relative_to(ROOT).as_posix()
    text = md.read_text(encoding="utf-8")
    lines = text.split("\n")

    # ---- 1. 代码块 JSON 校验 ----
    in_block = False
    buf = []
    start = 0
    for i, ln in enumerate(lines, start=1):
        if ln.lstrip().startswith("```"):
            if in_block:
                lang = buf[0].strip() if buf else ""
                body = "\n".join(buf[1:])
                if lang in ("json", ""):
                    stripped = body.strip()
                    # 占位符式示例（[...] / ... 表示"此处省略"）不是损坏，跳过。
                    # 它们是文档惯例，而非语法错误。
                    if "..." in stripped:
                        pass
                    elif stripped.startswith("{") or stripped.startswith("["):
                        try:
                            json.loads(stripped)
                        except json.JSONDecodeError as e:
                            findings.append(
                                (rel, f"L{start}-L{i}", "JSON_INVALID",
                                 f"{e.msg} @ line {e.lineno} col {e.colno}",
                                 stripped.split("\n")[max(0, e.lineno - 1)][:100] if e.lineno <= len(stripped.split(chr(10))) else "")
                            )
                buf = []
                in_block = False
            else:
                in_block = True
                buf = [ln.lstrip()[3:]]
                start = i
            continue
        if in_block:
            buf.append(ln)

    # ---- 2. 数字位丢失（损坏特有位型）----
    # 合法写法（第001章 / vol-001 / 时间戳 / 区间）全部排除；
    # 只保留「CJK + 00 + CJK」这种正常中文里不会出现的位型
    # （如「前00字」原文应为「前300字」、「≥00存」原文应为「≥100字」）。
    for i, ln in enumerate(lines, start=1):
        if ln.lstrip().startswith("```"):
            continue
        for m in re.finditer(r"[\u4e00-\u9fff](0{2,})[\u4e00-\u9fff]", ln):
            ctx = ln[max(0, m.start() - 14):m.end() + 14]
            findings.append((rel, f"L{i}", "DIGIT_LOST",
                             f"数字位缺失，疑似原文为多位数字（现为 {m.group(1)!r}）", ctx))

    # ---- 3. 空表格单元格 ----
    for i, ln in enumerate(lines, start=1):
        if not ln.strip().startswith("|"):
            continue
        if re.search(r"\|\s*\|\s*\|", ln) or re.search(r"^\|\s*\|\s*$", ln):
            findings.append((rel, f"L{i}", "EMPTY_TABLE_CELL", "表格单元格内容丢失", ln[:90]))

    # ---- 4. 全角括号不平衡（跳过代码块）----
    in_code = False
    for i, ln in enumerate(lines, start=1):
        if ln.lstrip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        o, c = ln.count("（"), ln.count("）")
        if o != c:
            findings.append((rel, f"L{i}", "PAREN_UNBALANCED",
                             f"（{o} vs ）{c}", ln[:90]))
        if ln.count("「") > ln.count("」"):
            findings.append((rel, f"L{i}", "QUOTE_UNCLOSED", "「 未闭合", ln[:90]))

    # ---- 5. 标题吞并正文 ----
    in_code = False
    for i, ln in enumerate(lines, start=1):
        if ln.lstrip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if re.match(r"^#{1,6} ", ln):
            st = ln.lstrip("#").strip()
            if len(st) > 45:
                findings.append((rel, f"L{i}", "HEADING_MERGED",
                                 f"标题行过长({len(st)} 字)，疑似吞并后续行", ln[:100]))

out = ["# 损坏签名检测（机械化可证证据）", "",
       f"扫描：`{ROOT / 'skills'}` 下全部 .md", "",
       "| # | 文件 | 位置 | 类型 | 说明 | 原文证据 |",
       "|---|---|---|---|---|---|"]
from collections import Counter
cnt = Counter(f[2] for f in findings)
out.append(f"## 汇总\n")
out.append("| 类型 | 数量 |")
out.append("|---|---|")
for k, v in cnt.most_common():
    out.append(f"| {k} | {v} |")
out.append("")
out.append("## 明细\n")
for i, (rel, loc, kind, desc, ev) in enumerate(
        sorted(findings, key=lambda x: (x[2], x[0], x[1])), 1):
    ev_clean = ev.replace("|", "\\|")
    out.append(f"### {i}. [{kind}] `{rel}` · {loc}")
    out.append(f"- **说明**：{desc}")
    if ev:
        out.append(f"- **原文**：`{ev_clean}`")
    out.append("")

OUT.write_text("\n".join(out), encoding="utf-8")

print(f"total findings = {len(findings)}")
for k, v in cnt.most_common():
    print(f"  {k:20s} {v}")
print()
print("=== JSON_INVALID 明细 ===")
for rel, loc, kind, desc, ev in findings:
    if kind == "JSON_INVALID":
        print(f"  {rel} {loc}: {desc}")
        print(f"      {ev[:100]}")
print()
print("=== DIGIT_LOST 明细 ===")
for rel, loc, kind, desc, ev in findings:
    if kind == "DIGIT_LOST":
        print(f"  {rel} {loc}: {desc}  | {ev[:80]}")
print()
print("report ->", OUT)
