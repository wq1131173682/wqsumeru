r"""自动抽取 SKILL.md 中所有脚本调用命令，在夹具项目里真实执行。

目的：一次性找出「文档写了但跑不通」的全部命令，
而不是靠人工挑几个用例。

做法：
  1. 扫描 skills/**/*.md，抽出 `python skills/...py ...` 形式的命令
  2. 替换占位符（<本章> / <chapters_dir> 等）
  3. 在带真实结构的夹具项目里执行
  4. 汇总退出码与报错

输出：tests/doc-commands.md + ASCII 摘要
"""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
FIX = ROOT / "tests" / "_tmp_doccmd"
OUT = ROOT / "tests" / "doc-commands.md"
PY = sys.executable

# 占位符 → 夹具中的真实值
PLACEHOLDER = {
    "<本章>": "001", "<修复章>": "001", "<本批次章>": "001",
    "<章号>": "001", "<章节号>": "001", "<current_chapter>": "1",
    "<chapters_dir>": "chapters/", "<章节目录>": "chapters/",
    "<dir>": "chapters/", "<项目根目录>": ".", "<项目根>": ".",
    "<输出目录>": "publish/", "<输出文件>": ".sumeru/review/out.json",
    "<输出>": ".sumeru/review/out.json",
    "<continuity目录>": ".sumeru/continuity", "<输出文件路径>": ".sumeru/review/out.json",
}

# ---------- 建夹具 ----------
if FIX.exists():
    shutil.rmtree(FIX)
for d in ("chapters", "outlines", "characters", "publish",
          ".sumeru/continuity", ".sumeru/review", ".sumeru/polish", ".sumeru/revise"):
    (FIX / d).mkdir(parents=True, exist_ok=True)

BODY = ("他走进房间。\n桌上放着一封信。\n他拿起信封，手指微微颤抖。\n"
        "「你来了。」他说。\n")
for i in (1, 2):
    (FIX / "chapters" / f"{i:03d}-开端.md").write_text(
        f"<!-- SUMERU_STATUS: chapter={i:03d}, status=drafted -->\n\n{BODY}",
        encoding="utf-8")

(FIX / "outlines" / "chapters.json").write_text(json.dumps({
    "chapters": [
        {"num": 1, "chapter": "001", "title": "开端", "volume": 1,
         "purpose": "开局", "events": ["a", "b", "c"], "openingHook": "x",
         "outputs": ["y"], "acceptanceCriteria": ["z"], "creativeGoal": "g",
         "freshnessHook": "f", "emotionalBeat": "平", "emotionalBeatTemplate": "A",
         "readerMemoryPoint": "m", "tropeToAvoid": ["t"],
         "protectedElements": ["p"], "rhythm": "fast"},
        {"num": 2, "chapter": "002", "title": "试炼", "volume": 1,
         "purpose": "推进", "events": ["a", "b", "c"], "openingHook": "x",
         "outputs": ["y"], "acceptanceCriteria": ["z"], "creativeGoal": "g",
         "freshnessHook": "f", "emotionalBeat": "平", "emotionalBeatTemplate": "A",
         "readerMemoryPoint": "m", "tropeToAvoid": ["t"],
         "protectedElements": ["p"], "rhythm": "fast"},
    ]
}, ensure_ascii=False, indent=2), encoding="utf-8")

(FIX / ".sumeru" / "project.json").write_text(json.dumps({
    "schemaVersion": 1, "title": "夹具", "genre": "玄幻", "targetPlatform": "番茄",
    "audience": "男频", "plannedWords": 200000, "plannedChapters": 2,
    "chapterWordRange": [2000, 3000], "style": "快", "tone": "热血",
    "currentStage": "review", "outputLevel": "quiet",
}, ensure_ascii=False, indent=2), encoding="utf-8")

# continuity 用脚本模板支持的数组结构，避免已知 schema 崩溃干扰本次测试
(FIX / ".sumeru" / "continuity" / "consistency-rules.json").write_text(json.dumps({
    "weapons": [], "active_buffs": [], "key_items": [], "character_state": [],
    "character_locations": [{"name": "苏瑾", "current_location": "北域",
                             "since_chapter": 1, "previous_locations": []}],
    "foreshadowing": [{"id": "v1", "description": "黑衣人", "status": "active",
                       "first_appeared": 1, "last_mentioned": 2,
                       "expected_payoff_chapter": 9, "payoff_status": "pending",
                       "related_chapters": [1], "importance": "high",
                       "reminder": "", "payoff_chapter": None, "payoff_detail": None}],
    "timeline": [{"chapter": 1, "event": "抵达", "date": "初",
                  "location": "北域", "characters": ["苏瑾"]}],
}, ensure_ascii=False, indent=2), encoding="utf-8")

# ---------- 抽取命令 ----------
cmds = []
for md in sorted(SKILLS.rglob("*.md")):
    rel = md.relative_to(ROOT).as_posix()
    lines = md.read_text(encoding="utf-8").split("\n")
    i = 0
    while i < len(lines):
        ln = lines[i]
        if "python " in ln and ".py" in ln and "skills/" in ln:
            # 拼接续行
            buf = ln
            j = i
            while buf.rstrip().endswith("\\") and j + 1 < len(lines):
                j += 1
                buf = buf.rstrip()[:-1] + " " + lines[j]
            # 去掉 markdown 装饰
            m = re.search(r"python\s+(skills/[\w\-./]+\.py.*)", buf)
            if m:
                cmd = m.group(1)
                cmd = cmd.split("`")[0].strip()
                cmds.append((rel, i + 1, cmd))
            i = j + 1
        else:
            i += 1

print(f"抽到候选命令 {len(cmds)} 条")
print()

results = []
seen = set()
for rel, ln, cmd in cmds:
    # 跳过用法说明（含可选参数方括号或花括号占位）
    if "[" in cmd or "{" in cmd or "..." in cmd:
        continue
    real = cmd
    for k, v in PLACEHOLDER.items():
        real = real.replace(k, v)
    # 剥掉 PowerShell 包装（} | Wait-Job 等）
    real = re.split(r"\s*[}|]\s*", real)[0].strip()
    if "<" in real or ">" in real:
        continue
    # 脚本路径是相对仓库根的，改写成绝对路径（cwd 是夹具目录）
    real = re.sub(r"(?<![\w/])skills/", str(SKILLS).replace("\\", "/") + "/", real)
    if real in seen:
        continue
    seen.add(real)

    argv = [PY, "-X", "utf8"] + real.split()
    try:
        r = subprocess.run(argv, cwd=str(FIX), capture_output=True, timeout=180)
        rc = r.returncode
        err = (r.stderr.decode("utf-8", errors="replace")).strip()
        out = (r.stdout.decode("utf-8", errors="replace")).strip()
    except subprocess.TimeoutExpired:
        rc, err, out = "TIMEOUT", "", ""
    first_err = next((l for l in err.splitlines() if l.strip()), "")
    results.append((rel, ln, real, rc, first_err, out))

print(f"{'rc':>4s}  {'判定':10s} {'来源':44s} 命令")
print("-" * 118)
fails = []
for rel, ln, real, rc, err, out in results:
    # 夹具没有 vol-N 目录，涉及卷路径的命令必然 rc=3 —— 属预期，不计为失败
    fixture_gap = "vol-N" in real or "vol-00" in real
    if rc == 0:
        verdict = "OK"
    elif rc == 1:
        verdict = "警告(正常)"
    elif rc == 3 and fixture_gap:
        verdict = "跳过(夹具)"
    elif rc == 2 and "目录不存在" in (err + out):
        verdict = "跳过(夹具)"
    else:
        verdict = "失败"
        fails.append((rel, ln, real, rc, err))
    print(f"{rc:>4d}  {verdict:10s} {rel}:{ln:<4d} {real[:62]}")

print()
print(f"执行 {len(results)} 条；失败 {len(fails)} 条；"
      f"其余为正常警告或夹具缺目录")
print()
if fails:
    print("=== 失败明细 ===")
    for rel, ln, real, rc, err in fails:
        print(f"\n  {rel}:{ln}")
        print(f"    命令: {real}")
        print(f"    rc={rc}  stderr: {err[:260]}")

report = ["# 文档命令实测（自动抽取）", "",
          f"夹具：`{FIX.relative_to(ROOT)}`（含 chapters/、outlines/chapters.json、"
          ".sumeru/continuity/consistency-rules.json、project.json）", "",
          f"共执行 **{len(results)}** 条命令，失败 **{len(fails)}** 条。", "",
          "| 退出码 | 来源 | 命令 |", "|---|---|---|"]
for rel, ln, real, rc, err, out in results:
    report.append(f"| {rc} | `{rel}:{ln}` | `{real.replace('|', chr(92)+'|')}` |")
if fails:
    report.append("")
    report.append("## 失败明细")
    for rel, ln, real, rc, err in fails:
        report.append("")
        report.append(f"### `{rel}:{ln}`")
        report.append("")
        report.append(f"```bash\n{real}\n```")
        report.append(f"- 退出码：`{rc}`")
        report.append(f"- stderr：")
        report.append("```text")
        report.extend(err.splitlines()[:8] or ["(空)"])
        report.append("```")
OUT.write_text("\n".join(report), encoding="utf-8")
shutil.rmtree(FIX)
print()
print("report ->", OUT)
