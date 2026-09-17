r"""自查：'未被引用的资源' 这一论断是否严谨。

之前只搜索了 SKILL.md，未搜索脚本代码。
本脚本在 skills/ 下全部 .md 与 .py 中搜索资源文件名，
以确认它们是否真的无人引用。
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"

TARGETS = [
    "consistency-rules-template.json",
    "punctuation-rules.json",
    "sensitive-words.json",
    "spell-dict.json",
    "cliche-blacklist.json",
    "anti-ai-thresholds.json",
    "scoring-criteria.json",
    "common-naming-library.md",
    "romance-style-reference.md",
    "sci-fi-style-reference.md",
    "urban-style-reference.md",
    "xianhuan-style-reference.md",
    "xianxia-style-reference.md",
    "volume-chapter-split.md",
    "text_utils.py",
    "subagent-rules.md",
]

# 语料 = 全部 .md + .py（排除被搜索文件自身）
corpus = []
for p in sorted(SKILLS.rglob("*")):
    if p.is_file() and p.suffix in (".md", ".py"):
        corpus.append((p, p.read_text(encoding="utf-8", errors="replace")))

print(f"语料文件数 = {len(corpus)}（.md + .py）")
print()
print(f"{'资源':40s} {'引用它的文件'}")
print("-" * 84)
unref = []
for t in TARGETS:
    hits = []
    for p, txt in corpus:
        if p.name == t:
            continue
        if t in txt or t.replace(".json", "").replace(".md", "") in txt and t in txt:
            hits.append(p.relative_to(ROOT).as_posix())
        elif t in txt:
            hits.append(p.relative_to(ROOT).as_posix())
    # 更宽松：也搜不带扩展名的基名
    if not hits:
        base = t.rsplit(".", 1)[0]
        for p, txt in corpus:
            if p.name == t or p.stem == base and p.name == t:
                continue
            if base in txt and p.name != t:
                hits.append(p.relative_to(ROOT).as_posix() + " (基名)")
    if hits:
        print(f"{t:40s} {hits[:4]}")
    else:
        print(f"{t:40s} —— 无引用 ——")
        unref.append(t)

print()
print(f"确认为无引用 = {len(unref)}")
for u in unref:
    print(f"   {u}")
