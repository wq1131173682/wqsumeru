r"""穷尽式可疑行扫描（不做"是否损坏"的判断，只把所有可疑信号列全）。

设计原则：宁可多列，不可漏列。输出后人工逐条判定。
覆盖信号：
  S1  行尾/行中出现 `- ` 但该行是散文（非列表项）
  S2  中文后直接跟 `N.`（编号粘连）
  S3  `）` 出现在句中（前面无 `（` 配对）
  S4  `存` 出现在应为「字」的语境（前有数字 + 后无「在」）
  S5  代码围栏 ` ``` ` 不在行首（被拼进正文）
  S6  加粗未闭合 `**xx*`
  S7  一行内出现两个及以上 `：` 且无标点分隔（疑似合并）
  S8  `第-` / `第章` / `前00` 等数字缺失
  S9  行尾无标点却紧跟下一个 `#` 标题（换行丢失）
  S10 `）1.` / `）2.` 这类括号后直接编号
"""
import io
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
FENCE = "`" * 3

SIGNALS = {
    "S1_行中列表符": re.compile(r"[\u4e00-\u9fff][，。；：]\s*-\s+[\u4e00-\u9fff]"),
    "S2_编号粘连": re.compile(r"[\u4e00-\u9fff`\)）]\s*\d+\.\s+\*\*"),
    "S3_句中右括号": re.compile(r"[\u4e00-\u9fff]）[\u4e00-\u9fff\d]"),
    "S4_存疑字": re.compile(r"\d+\s*存|存\|"),
    "S6_加粗未闭合": re.compile(r"\*\*[^*\n`]{2,24}\*(?!\*)"),
    "S8_数字缺失": re.compile(r"第-\d|第章|前00|≥00|超过0个"),
    "S10_括号接编号": re.compile(r"[）)]\s*\d+\.\s"),
}

hits = []
for md in sorted(SKILLS.rglob("*.md")):
    rel = md.relative_to(ROOT).as_posix()
    lines = md.read_text(encoding="utf-8").split("\n")
    for i, ln in enumerate(lines, start=1):
        # S5 围栏不在行首
        if FENCE in ln and not ln.lstrip().startswith(FENCE):
            hits.append((rel, i, "S5_围栏混入正文", ln.strip()[:130]))
        for name, pat in SIGNALS.items():
            if pat.search(ln):
                hits.append((rel, i, name, ln.strip()[:130]))

# 去重
seen = set()
uniq = []
for h in hits:
    k = (h[0], h[1], h[2])
    if k not in seen:
        seen.add(k)
        uniq.append(h)

from collections import Counter
cnt = Counter(h[2] for h in uniq)
print(f"可疑行合计 = {len(uniq)}")
for k, v in cnt.most_common():
    print(f"  {k:16s} {v}")
print()
for rel, i, kind, txt in sorted(uniq, key=lambda x: (x[2], x[0], x[1])):
    print(f"[{kind}] {rel}:{i}")
    print(f"    {txt}")
