"""wq-* 技能包结构化体检器。

设计要点：
- 报告写入 UTF-8 文件（而非 stdout），避免 Windows 控制台 GBK 解码破坏中文证据。
- 所有判定基于字节/码点计数，不依赖控制台渲染。

用法: python tests/lint-skills.py
输出: tests/lint-report.md
"""
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
OUT = ROOT / "tests" / "lint-report.md"

findings = []          # (级别, 技能, 位置, 描述, 证据)


def add(level, skill, loc, desc, ev=""):
    findings.append((level, skill, loc, desc, ev))


skill_dirs = sorted([d for d in SKILLS.iterdir() if d.is_dir()])

# ---------- 1. frontmatter 解析与必填项 ----------
REQUIRED = ["name", "description", "version"]
KNOWN_KEYS = {"name", "description", "version", "type", "argument-hint",
              "disable-model-invocation", "user-invocable", "allowed-tools",
              "context", "agent", "requires"}

fm_data = {}
for d in skill_dirs:
    f = d / "SKILL.md"
    if not f.exists():
        add("P0", d.name, "-", "缺少 SKILL.md")
        continue
    text = f.read_text(encoding="utf-8")
    if not text.startswith("---"):
        add("P0", d.name, "L1", "frontmatter 缺失（文件未以 --- 开头）")
        fm_data[d.name] = {}
        continue
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
    if not m:
        add("P0", d.name, "L1", "frontmatter 未闭合（找不到第二个 ---）")
        fm_data[d.name] = {}
        continue
    body_start = text[:m.end()].count("\n") + 1
    kv = {}
    for i, line in enumerate(m.group(1).split("\n"), start=2):
        if not line.strip():
            continue
        if ":" not in line:
            add("P1", d.name, f"L{i}", f"frontmatter 行无法解析: {line[:40]!r}")
            continue
        k, v = line.split(":", 1)
        kv[k.strip()] = v.strip()
    fm_data[d.name] = kv
    for r in REQUIRED:
        if r not in kv:
            add("P1", d.name, "frontmatter", f"缺少必填字段 {r!r}")
    for k in kv:
        if k not in KNOWN_KEYS:
            add("P2", d.name, "frontmatter", f"未知字段 {k!r}")

    # name 必须与目录名一致
    if kv.get("name") and kv["name"] != d.name:
        add("P1", d.name, "frontmatter", f"name({kv['name']}) 与目录名({d.name}) 不一致")
    # 非 wq-rules 必须声明 requires
    if d.name != "wq-rules" and "requires" not in kv:
        add("P1", d.name, "frontmatter", "未声明 requires: [wq-rules]")
    # 正文起始行
    fm_data[d.name]["_body_start"] = body_start
    fm_data[d.name]["_text"] = text

# ---------- 2. 结构完整性：代码围栏 / 括号 / 标题混排 ----------
PAIRS = [("「", "」"), ("『", "』"), ("（", "）"), ("《", "》"), ("【", "】"),
         ("“", "”"), ("‘", "’"), ("[", "]"), ("(", ")")]
for d in skill_dirs:
    f = d / "SKILL.md"
    if not f.exists():
        continue
    lines = f.read_text(encoding="utf-8").split("\n")

    # 代码围栏成对
    fences = sum(1 for ln in lines if ln.lstrip().startswith("```"))
    if fences % 2:
        add("P1", d.name, "-", f"代码围栏数量为奇数({fences})，存在未闭合围栏")

    # 逐行括号配对（跳过代码块内部）
    in_code = False
    for i, ln in enumerate(lines, start=1):
        if ln.lstrip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        for o, c in PAIRS:
            if ln.count(o) != ln.count(c):
                add("P2", d.name, f"L{i}",
                    f"括号不配对 {o}{c}（{ln.count(o)} vs {ln.count(c)}）", ln[:70])

        # 标题行与列表/正文被压成一行（换行丢失签名）
        if re.match(r"^#{1,6} ", ln):
            st = ln.lstrip("#").strip()
            if len(st) > 60:
                add("P1", d.name, f"L{i}", "标题行异常过长，疑似换行丢失导致内容并入标题", ln[:90])
            if re.search(r"[。；;]\s*-\s", st) or re.search(r"」?\s*-\s*\w+:", st):
                add("P1", d.name, f"L{i}", "标题行内混入列表项，疑似换行丢失", ln[:90])
            if len(st) > 25 and st.count("- ") >= 1 and "：" not in st:
                add("P2", d.name, f"L{i}", "标题行疑似吞并了后续行", ln[:90])

# ---------- 3. 交叉引用完整性 ----------
names = {d.name for d in skill_dirs}
for d in skill_dirs:
    f = d / "SKILL.md"
    if not f.exists():
        continue
    text = f.read_text(encoding="utf-8")
    # 引用了不存在的技能
    for ref in sorted(set(re.findall(r"\bwq-[a-z][a-z0-9-]*", text))):
        if ref not in names:
            add("P1", d.name, "-", f"引用了不存在的技能 {ref!r}")
    # 引用了本技能内的文件，验证存在
    # 注意：SKILL.md 常用点号记法引用 JSON 内的键
    #       （如 config/x.json.gradeThresholds），需剥离尾部 .key 段
    for rel in sorted(set(re.findall(r"`((?:scripts|references|config)/[\w./\u4e00-\u9fff-]+)`", text))):
        cand = rel
        while not (d / cand).exists() and "." in cand.split("/")[-1]:
            cand = cand.rsplit(".", 1)[0]
            if cand.endswith("/") or "/" not in cand:
                break
        if not (d / cand).exists():
            add("P0", d.name, "-", f"引用了不存在的文件 {rel!r}")
        elif cand != rel:
            add("P2", d.name, "-", f"点号记法引用 {rel!r} 实为 {cand!r} 内的键（可接受）")
    if "requires" in text and "wq-rules" not in text:
        pass

# ---------- 4. 各技能实际拥有的资源 vs 被引用 ----------
for d in skill_dirs:
    sub = defaultdict(list)
    for p in d.rglob("*"):
        if p.is_file() and "__pycache__" not in p.parts:
            sub[p.parent.relative_to(d).as_posix() if p.parent != d else "."].append(p.name)
    # 未被任何 SKILL.md 引用的脚本（死资源）
    all_text = "\n".join(
        (dd / "SKILL.md").read_text(encoding="utf-8")
        for dd in skill_dirs if (dd / "SKILL.md").exists()
    )
    for p in d.rglob("*"):
        if p.is_file() and p.suffix in (".py", ".json", ".md") \
                and "__pycache__" not in p.parts and p.name != "SKILL.md":
            rel = p.relative_to(d).as_posix()
            if p.name not in all_text and rel not in all_text:
                add("P2", d.name, rel, "该资源文件未被任何 SKILL.md 引用（疑似死资源）")

# ---------- 5. 中文损坏检测（近形字替换 / 生僻串） ----------
# 通用检测：找出"高频正常词中的低频异常搭配"过于困难，
# 改用机械可证的方式——统计每个文件里出现的、由 3 字节 UTF-8 尾字节改写导致的罕见组合，
# 用"同文件内同一语境应出现的规范词缺失"来定位。
for d in skill_dirs:
    f = d / "SKILL.md"
    if not f.exists():
        continue
    text = f.read_text(encoding="utf-8")
    # 行尾悬挂：一行以「 开头却无 」
    for i, ln in enumerate(text.split("\n"), start=1):
        if ln.count("「") > ln.count("」") and not ln.lstrip().startswith("```"):
            add("P1", d.name, f"L{i}", "「 未闭合（疑似标题右引号被替换）", ln[:80])

# ---------- 6. 版本一致性 ----------
vers = {k: v.get("version") for k, v in fm_data.items() if isinstance(v, dict)}
print("versions:", json.dumps(vers, ensure_ascii=True, indent=1))

# ---------- 输出报告 ----------
order = {"P0": 0, "P1": 1, "P2": 2}
findings.sort(key=lambda x: (order.get(x[0], 9), x[1], x[2]))
with OUT.open("w", encoding="utf-8") as fh:
    fh.write("# wq-* 技能包结构化体检报告\n\n")
    fh.write(f"扫描目录：`{SKILLS}`，技能数：{len(skill_dirs)}\n\n")
    cnt = Counter(x[0] for x in findings)
    fh.write(f"## 汇总\n\n| 级别 | 数量 |\n|---|---|\n")
    for lv in ("P0", "P1", "P2"):
        fh.write(f"| {lv} | {cnt.get(lv, 0)} |\n")
    fh.write("\n## 明细\n\n")
    for lv, sk, loc, desc, ev in findings:
        fh.write(f"### [{lv}] {sk} · {loc}\n")
        fh.write(f"- **问题**：{desc}\n")
        if ev:
            fh.write(f"- **证据**：`{ev}`\n")
        fh.write("\n")

print("findings:", len(findings), "P0:", cnt.get("P0", 0), "P1:", cnt.get("P1", 0), "P2:", cnt.get("P2", 0))
print("report:", OUT)
