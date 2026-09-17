r"""wq-* 技能包 · 中文损坏目录器（含修复建议）

背景：本仓库 SKILL.md 存在系统性文本损坏——中文字被替换成近形/近义字，
伴随换行丢失。损坏早于 git 历史（最早提交 406be85 即已存在）。

本工具按「证据强度」分四类输出，便于人工/自动修复：
  A. 结构证据（最强）：行尾 `）` 但语义应为 `：`
  B. 词典证据：已确认的近形/近义替换对
  C. 换行丢失：标题吞并正文、列表项粘连
  D. 语法证据：JSON 代码块语法错误

用法:
  python tests/find-corruptions.py            # 只报告
  python tests/find-corruptions.py --fix      # 应用 A 类修复（仅行尾冒号）
输出: tests/corruption-catalog.md
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
OUT = ROOT / "tests" / "corruption-catalog.md"
APPLY_FIX = "--fix" in sys.argv

# ---------- B 类：已确认的替换对 ----------
# 每项：(损坏形, 建议正确形, 判据说明)
PAIRS = [
    ("平可", "平台", "「平台」被替换，见 wq-rules 推进规则"),
    ("字存", "字数", "「字数」被替换"),
    ("完数", "完整", "「完整」被替换，如『字段完整性检查』"),
    ("弟存", "弟子", "「弟子」被替换"),
    ("章节可", "章节号", "「号」→「可」"),
    ("章节及", "章节号", "「号」→「及」（wq-migrate 字段表）"),
    ("字符为", "字符串", "「串」→「为」（wq-rules 状态标记字段表）"),
    ("分类锁", "分类键", "「键」→「锁」"),
    ("状态文从", "状态文件", "「件」→「从」"),
    ("扫提", "扫描", "「描」→「提」"),
    ("至就", "至少", "「少」→「就」"),
    ("信息密库", "信息密度", "「度」→「库」"),
    ("连续低密库", "连续低密度", "「度」→「库」"),
    ("战力等级不能无原因跳跟", "战力等级不能无原因跳跃", "「跃」→「跟」"),
    ("事件时间线必须有库", "事件时间线必须有序", "「序」→「库」"),
    ("活跃超过0个", "活跃超过 N 个", "数字与限定词丢失"),
    ("位人", "写入", "wq-rules consistency-rules 段落"),
    ("规`", "见 `", "「见」→「规」（第十二部分）"),
    ("冲突启加", "冲突叠加", "wq-rules 核心指标表"),
    # ── 2026-09 补：上一轮漏检的实例（教训：判据收窄会掩盖问题）──
    ("第-6章", "第1-6章", "数字位丢失（批次摘要示例）"),
    ("首次出在", "首次出场", "「场」→「在」"),
    ("消者构", "消耗", "「耗」→「者构」（换行丢失+替换）"),
    ("黑衣人身从", "黑衣人身份", "「份」→「从」"),
    ("伏笔线推过", "伏笔线推进", "「进」→「过」"),
    ("2000 存", "2000 字", "「字」→「存」（context pack 大小）"),
    ("500 存", "500 字", "「字」→「存」（context pack 大小）"),
    ("更新人物状态4.", "更新人物状态\\n4.", "编号粘连（父Agent处理流程）"),
    ("迁移规则**）1.", "迁移规则**：\\n1.", "「：」→「）」+ 换行丢失"),
    ("卷1?03", "卷1·003", "「·」→「?」"),
    ("交求", "交汇", "「汇」→「求」"),
    ("新的一大", "新的一天", "「天」→「大」"),
]

# A 类：行尾 `）` 实为 `：` 的结构判据
# 关键：必须「有 ） 但整行没有 （」才算不平衡。
# 形如 `### 句号分段规则（强制）` 是合法中文标题，不能误判。
RE_TRAILING_COLON = re.compile(r"^.*）\s*$")

findings = []   # (类别, 文件, 行号, 说明, 原文, 建议)


def scan_file(path: Path):
    rel = path.relative_to(ROOT).as_posix()
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")

    # ---- E 类：独立 .json 文件本身不可解析 ----
    if path.suffix == ".json":
        try:
            json.loads(text)
            parse_ok = True
        except json.JSONDecodeError as e:
            parse_ok = False
            src = lines[e.lineno - 1] if e.lineno <= len(lines) else ""
            findings.append(("E·JSON", rel, e.lineno,
                             f"文件无法解析：{e.msg}（列 {e.colno}）",
                             src.strip()[:90],
                             "检查值内是否混入了未转义的 ASCII 引号（原文应为中文引号）"))
        # 仅当解析失败时，才把「值内出现 ASCII 引号」当作损坏证据。
        # 解析成功说明那些引号是合法的 JSON 结构引号（如 spell-dict.json 的多对键值行）。
        if not parse_ok:
            for i, ln in enumerate(lines, start=1):
                m = re.match(r'^(\s*"[^"]+"\s*:\s*)"(.*)"(\s*,?)\s*$', ln)
                if m and '"' in m.group(2):
                    findings.append(("E·JSON", rel, i,
                                     f"值内含 {m.group(2).count(chr(34))} 个未转义 ASCII 引号（原文应为中文引号）",
                                     ln.strip()[:90],
                                     "改为 “ ”"))
        return

    # ---- A 类 ----
    # 结构判据：整行「）」数量 > 「（」数量，且行尾为「）」。
    # 注意：`（有发现时注入，v1.4.8）` 这类括号是平衡的，不能误判——
    # 必须先比较全行的 （ 与 ） 数量。
    for i, ln in enumerate(lines, start=1):
        if not RE_TRAILING_COLON.match(ln):
            continue
        if ln.lstrip().startswith(("```", "|", "-", "*", "1.", "2.", "3.")):
            continue
        if ln.count("）") <= ln.count("（"):
            continue          # 括号平衡 → 合法标题/正文，跳过
        if "http" in ln:
            continue
        suggested = ln[:ln.rstrip().rfind("）")] + "："
        findings.append(("A·结构", rel, i,
                         "「）」不平衡（全行无「（」），应为行尾「：」",
                         ln.strip()[:90], suggested.strip()[:90]))

    # ---- B 类 ----
    for i, ln in enumerate(lines, start=1):
        for bad, good, why in PAIRS:
            if bad in ln:
                findings.append(("B·词典", rel, i, f"{why}",
                                 ln.strip()[:90], ln.replace(bad, good).strip()[:90]))

    # ---- C 类 ----
    in_code = False
    for i, ln in enumerate(lines, start=1):
        if ln.lstrip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        # 标题吞并正文：长标题**且**含列表/加粗标签等"本应换行"的特征。
        # 单纯的长标题（如带版本说明的章节名）是合法的，不能仅凭长度判定。
        if re.match(r"^#{1,6} ", ln) and len(ln.lstrip("#").strip()) > 45:
            body = ln.lstrip("#").strip()
            looks_merged = (
                body.count("- ") >= 2
                or re.search(r"\*\*[^*]+\*\*\s*[）)]", body)
                or re.search(r"[\u4e00-\u9fff]\s*-\s*`", body)
            )
            if looks_merged:
                findings.append(("C·换行", rel, i, "标题行吞并后续内容（换行丢失）",
                                 ln.strip()[:90], "在标题后插入换行"))
        # 表格行里出现 "- " 列表粘连
        if ln.strip().startswith("|") and ln.count("- ") >= 2 and "：" in ln:
            findings.append(("C·换行", rel, i, "表格单元格内列表项粘连（换行丢失）",
                             ln.strip()[:90], "拆分为多行"))

    # ---- D 类 ----
    in_code = False
    buf, start = [], 0
    for i, ln in enumerate(lines, start=1):
        if ln.lstrip().startswith("```"):
            if in_code:
                lang = buf[0].strip() if buf else ""
                body = "\n".join(buf[1:]).strip()
                if lang in ("json", "") and body.startswith(("{", "[")):
                    # 占位符式示例（含 `...` / `[...]`）是文档惯例，非语法错误
                    if "..." in body:
                        pass
                    else:
                        try:
                            json.loads(body)
                        except json.JSONDecodeError as e:
                            src = body.split("\n")
                            ev = src[e.lineno - 1] if e.lineno <= len(src) else ""
                            findings.append(("D·语法", rel, f"{start}-{i}",
                                             f"JSON 非法：{e.msg}（第 {e.lineno} 行）",
                                             ev.strip()[:90], "补全缺失的引号/括号"))
                buf, in_code = [], False
            else:
                in_code, buf, start = True, [ln.lstrip()[3:]], i
            continue
        if in_code:
            buf.append(ln)


for md in sorted(SKILLS.rglob("*.md")):
    scan_file(md)

# JSON 同样受此损坏影响（见 wq-score/config/scoring-criteria.json L206）
for js in sorted(SKILLS.rglob("*.json")):
    scan_file(js)

# ---------- 应用 A 类修复 ----------
applied = 0
if APPLY_FIX:
    by_file = {}
    for cat, rel, ln_no, *_ in findings:
        if cat == "A·结构":
            by_file.setdefault(rel, []).append(ln_no)
    for rel, nos in by_file.items():
        p = ROOT / rel
        lines = p.read_text(encoding="utf-8").split("\n")
        for n in nos:
            old = lines[n - 1]
            if RE_TRAILING_COLON.match(old) and old.count("）") > old.count("（"):
                idx = old.rstrip().rfind("）")
                lines[n - 1] = old[:idx] + "：" + old[idx + 1:]
                applied += 1
        p.write_text("\n".join(lines), encoding="utf-8")

# ---------- 报告 ----------
from collections import Counter
cnt = Counter(f[0] for f in findings)
files = Counter(f[1] for f in findings)

out = ["# wq-* 技能包 · 中文损坏目录", "",
       "> 损坏性质：中文字被替换为近形/近义字（UTF-8 第 3 字节被改写），并伴随换行丢失。",
       "> 已取证：损坏早于 git 历史（最早提交 `406be85` 即存在），非编辑事故。", ""]
out.append(f"总发现：**{len(findings)}** 处")
out.append("")
out.append("| 类别 | 数量 | 证据强度 |")
out.append("|---|---|---|")
strength = {"A·结构": "强（结构可判定）", "B·词典": "强（已人工确认）",
            "C·换行": "中（格式异常）", "D·语法": "强（解析器判定）",
            "E·JSON": "强（解析器判定）"}
for k in ("A·结构", "B·词典", "C·换行", "D·语法", "E·JSON"):
    out.append(f"| {k} | {cnt.get(k, 0)} | {strength[k]} |")
out.append("")
out.append("## 按文件分布")
out.append("")
out.append("| 文件 | 发现数 |")
out.append("|---|---|")
for f, c in files.most_common():
    out.append(f"| `{f}` | {c} |")
out.append("")
out.append("## 明细")
out.append("")
for cat in ("A·结构", "B·词典", "C·换行", "D·语法", "E·JSON"):
    sel = [f for f in findings if f[0] == cat]
    if not sel:
        continue
    out.append(f"### {cat}（{len(sel)} 处）")
    out.append("")
    out.append("| 文件 | 行 | 说明 | 原文 | 建议 |")
    out.append("|---|---|---|---|---|")
    for _, rel, ln_no, why, ev, sug in sel:
        e = ev.replace("|", "\\|")
        s = sug.replace("|", "\\|")
        out.append(f"| `{rel}` | {ln_no} | {why} | `{e}` | `{s}` |")
    out.append("")

OUT.write_text("\n".join(out), encoding="utf-8")

print(f"total = {len(findings)}")
for k in ("A·结构", "B·词典", "C·换行", "D·语法"):
    print(f"  {k:10s} {cnt.get(k,0)}")
print(f"files affected = {len(files)}")
if APPLY_FIX:
    print(f"APPLIED A-class fixes = {applied}")
print(f"report -> {OUT}")
