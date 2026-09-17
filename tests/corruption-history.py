r"""git 历史取证：定位各 SKILL.md 的中文损坏是在哪个提交引入的。

方法：对每个提交版本，统计“规范词”与“损坏形”的出现次数。
规范词/损坏形全部以 \uXXXX 转义书写，保证脚本自身 ASCII 安全（注意本 docstring 必须是 raw）。
输出写入 UTF-8 文件。
"""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "tests" / "corruption-history.md"

# (标签, 规范形, 损坏形)
PAIRS = [
    ("平台", "\u5e73\u53f0", "\u5e73\u53ef"),
    ("章节号", "\u7ae0\u8282\u53f7", "\u7ae0\u8282\u53ef"),
    ("字符串", "\u5b57\u7b26\u4e32", "\u5b57\u7b26\u4e3a"),
    ("分类键", "\u5206\u7c7b\u952e", "\u5206\u7c7b\u9501"),
    ("状态文件", "\u72b6\u6001\u6587\u4ef6", "\u72b6\u6001\u6587\u4ece"),
    ("扫描", "\u626b\u63cf", "\u626b\u63d0"),
    ("字数", "\u5b57\u6570", "\u5b57\u5b58"),
    ("完整", "\u5b8c\u6574", "\u5b8c\u6570"),
    ("弟子", "\u5f1f\u5b50", "\u5f1f\u5b58"),
    ("介绍", "\u4ecb\u7ecd", "\u4ecb\u7ecd"),
]

def run(args):
    r = subprocess.run(args, cwd=str(ROOT), capture_output=True)
    return r.stdout.decode("utf-8", errors="replace"), r.returncode

lines_out = ["# SKILL.md 中文损坏 · git 历史取证", ""]
lines_out.append(f"仓库：`{ROOT}`")
lines_out.append("")
lines_out.append("统计方式：在指定提交的文本版本中，统计『规范词』与『损坏形』出现次数。")
lines_out.append("若某提交中损坏形 > 0 且规范形 = 0，说明该提交已带入损坏。")
lines_out.append("")

files = sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / "skills").rglob("SKILL.md"))

summary = []
for rel in files:
    log, rc = run(["git", "log", "--format=%h|%ad|%s", "--date=short", "--", rel])
    if rc != 0 or not log.strip():
        continue
    commits = [l for l in log.strip().split("\n") if "|" in l]
    lines_out.append(f"## `{rel}`")
    lines_out.append("")
    lines_out.append("| 提交 | 日期 | 主题 | " + " | ".join(f"{p[0]}好/坏" for p in PAIRS[:8]) + " |")
    lines_out.append("|---|---|---|" + "---|" * 8)
    first_bad = None
    # git log 为「新→旧」；反转为「旧→新」，找最早出现损坏的提交
    for c in reversed(commits[:24]):
        h, d, s = c.split("|", 2)
        txt, rc2 = run(["git", "show", f"{h}:{rel}"])
        if rc2 != 0:
            continue
        cells = []
        bad_total = 0
        for _, good, bad in PAIRS[:8]:
            g, b = txt.count(good), txt.count(bad)
            cells.append(f"{g}/{b}")
            bad_total += b
        s_clean = s.replace("|", "/")[:34]
        lines_out.append(f"| `{h}` | {d} | {s_clean} | " + " | ".join(cells) + f" | Σ坏={bad_total} |")
        if bad_total > 0 and first_bad is None:
            first_bad = (h, d, s_clean, bad_total)
    lines_out.append("")
    if first_bad:
        lines_out.append(f"**首次出现损坏的提交**：`{first_bad[0]}` ({first_bad[1]}) — {first_bad[2]} — 命中 {first_bad[3]} 个损坏探针")
        summary.append((rel, first_bad[0], first_bad[1], first_bad[3]))
    else:
        lines_out.append("**未检出损坏探针**")
        summary.append((rel, "-", "-", 0))
    lines_out.append("")

lines_out.append("## 汇总")
lines_out.append("")
lines_out.append("| 文件 | 首次损坏提交 | 日期 | 命中探针数 |")
lines_out.append("|---|---|---|---|")
for rel, h, d, n in summary:
    lines_out.append(f"| `{rel}` | `{h}` | {d} | {n} |")

OUT.write_text("\n".join(lines_out), encoding="utf-8")

# 同时输出 ASCII 摘要到 stdout
print("FILE_HAS_CORRUPTION:")
for rel, h, d, n in summary:
    print(f"  probes={n:2d} first_bad={h:8s} {d:10s} {rel}")
print()
print("report ->", OUT)
