r"""校验「子Agent产出契约」在全部技能中是否已一致。

判据（按用户 2026 决策：子Agent直接写入文件）：
  1. 不得再出现「不写入任何项目文件」这类一刀切禁令
  2. 不得再出现「只返回文本」「输出纯文本结果」这类与写文件冲突的表述
  3. 声明写文件的技能，必须同时声明路径
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
OUT = ROOT / "tests" / "contract-consistency.md"

BANNED = [
    (r"不写入任何项目文件", "一刀切禁令（与「直接写入」冲突）"),
    (r"输出纯文本结果", "与「必须写入文件」冲突"),
    (r"只返回修改后的文本", "与「写入文件」冲突"),
    (r"不写项目文件", "与「写入文件」冲突"),
]

REQUIRED = [
    (r"写入\s*`?chapters/", "write/revise 应声明 chapters/ 写入路径"),
    (r"\.sumeru/polish/temp/", "polish 应声明 temp 写入路径"),
]

rows = []
for md in sorted(SKILLS.rglob("*.md")):
    rel = md.relative_to(ROOT).as_posix()
    lines = md.read_text(encoding="utf-8").split("\n")
    for i, ln in enumerate(lines, start=1):
        for pat, why in BANNED:
            if re.search(pat, ln):
                rows.append(("BANNED", rel, i, why, ln.strip()[:100]))

print("=" * 78)
print("禁用表述检查（应为 0）")
print("=" * 78)
if rows:
    for kind, rel, i, why, txt in rows:
        print(f"  [{kind}] {rel}:{i}")
        print(f"        {why}")
        print(f"        {txt}")
else:
    print("  ✅ 未发现冲突表述")

print()
print("=" * 78)
print("写入路径声明检查")
print("=" * 78)
for pat, why in REQUIRED:
    hits = []
    for md in sorted(SKILLS.rglob("*.md")):
        t = md.read_text(encoding="utf-8")
        if re.search(pat, t):
            hits.append(md.relative_to(ROOT).as_posix())
    print(f"  {why}")
    print(f"      命中 {len(hits)} 个文件: {hits[:6]}")

print()
print("=" * 78)
print("subagent-rules.md 关键条款")
print("=" * 78)
sar = (SKILLS / "wq-rules/subagent-rules.md").read_text(encoding="utf-8")
checks = [
    ("必须写入文件", "正文/细纲必须写入文件"),
    ("禁止自行推断", "禁止自行推断路径"),
    ("产出契约", "三·五 产出契约章节"),
    ("不含正文", "返回内容不含正文"),
    ("分析类技能不写文件", "分析类技能例外说明"),
]
for key, label in checks:
    print(f"  {'✅' if key in sar else '❌'} {label}")

# 报告
report = ["# 子Agent产出契约一致性校验", "",
          "决策：**子Agent直接写入文件**（用户 2026 确认）。", ""]
report.append("## 禁用表述（应为 0）")
report.append("")
if rows:
    report.append("| 文件 | 行 | 原因 | 原文 |")
    report.append("|---|---|---|---|")
    for kind, rel, i, why, txt in rows:
        report.append(f"| `{rel}` | {i} | {why} | `{txt.replace('|', chr(92)+'|')}` |")
else:
    report.append("未发现冲突表述 ✅")
report.append("")
report.append("## subagent-rules.md 条款自检")
report.append("")
report.append("| 条款 | 存在 |")
report.append("|---|---|")
for key, label in checks:
    report.append(f"| {label} | {'✅' if key in sar else '❌'} |")
OUT.write_text("\n".join(report), encoding="utf-8")
print()
print("report ->", OUT)
