r"""全仓库扫描「编号项粘连」与「加粗标记未闭合」。"""
import io
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
FENCE = "```"

num_merge = []   # 编号粘连：正文后直接跟 "N. **"
bold_unclosed = []  # 加粗未闭合：**xx* 或 *xx**

RE_NUM = re.compile(r"[\u4e00-\u9fff`\)）]\s*(\d+)\.\s+\*\*")
# 加粗标签里只有一个星号收尾，如 **世界观设定*
# 注意：必须排除「**加粗** 后面还有反引号/星号」的合法情形，
# 例如 `- **不移动** \`chapters/*.md\`` 里 `** ` 与 `*` 并非未闭合标签。
RE_BOLD_BAD = re.compile(r"\*\*[^*\n`]{2,24}\*(?!\*)")

for md in sorted(SKILLS.rglob("*.md")):
    rel = md.relative_to(ROOT).as_posix()
    in_code = False
    for i, ln in enumerate(md.read_text(encoding="utf-8").split("\n"), start=1):
        if ln.lstrip().startswith(FENCE):
            in_code = not in_code
            continue
        if in_code:
            continue
        for m in RE_NUM.finditer(ln):
            num_merge.append((rel, i, m.group(1), ln.strip()[:110]))
        for m in RE_BOLD_BAD.finditer(ln):
            bold_unclosed.append((rel, i, m.group(0), ln.strip()[:110]))

print(f"编号粘连 = {len(num_merge)}")
for rel, i, num, t in num_merge:
    print(f"  {rel}:{i}  (后接 {num}.)")
    print(f"      {t}")

print()
print(f"加粗未闭合 = {len(bold_unclosed)}")
seen = set()
for rel, i, frag, t in bold_unclosed:
    key = (rel, i)
    if key in seen:
        continue
    seen.add(key)
    print(f"  {rel}:{i}  片段={frag!r}")
    print(f"      {t}")
