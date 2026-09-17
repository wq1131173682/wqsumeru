r"""P0-8 修复验证：描写识别是否真的生效，且不误伤正常叙事。

双向验证：
  A. 纯描写段落 → 必须被识别（修复前恒为 False）
  B. 含人物施动的叙事段落 → 必须不被识别为纯描写（防止矫枉过正）
  C. 端到端：100% 纯描写章节必须触发 high 阻断
  D. 端到端：正常叙事章节不得误触发 high 阻断
"""
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "skills/wq-review/scripts/anti-ai-scan.py"
PY = sys.executable

spec = importlib.util.spec_from_file_location("aas", SCRIPT)
m = importlib.util.module_from_spec(spec)
sys.modules["aas"] = m
spec.loader.exec_module(m)

print("=" * 76)
print(f"[0] 阈值 DESCRIPTION_PARAGRAPH_MIN_LEN = {m.DESCRIPTION_PARAGRAPH_MIN_LEN}")
print("=" * 76)

# A. 纯描写（无人称代词、无动作短语）
PURE_DESC = [
    ("自然景物", "天色渐暗，远处的群山被暮色笼罩，山谷间弥漫着淡淡的雾气。"
                 "林间的树叶在晚风中轻轻摇曳，偶尔有几片飘落，落在寂静的小径上。"),
    ("城池外貌", "青石砌成的城墙巍峨耸立，斑驳的苔痕爬满了砖缝。"
                 "城楼上的旗帜在风中猎猎作响，城门两侧的石狮已经磨损得看不清面目。"),
    ("室内陈设", "屋内陈设简单，一张木桌靠着斑驳的墙壁，桌上放着一盏油灯。"
                 "窗棂上糊着泛黄的纸，光线透进来，在空气中浮起细细的尘埃。"),
    ("氛围", "空气凝重得像要滴出水来，殿内的寂静压得人喘不过气。"
             "香炉里的烟缓缓升起，在昏暗的光线中盘旋，最终消散在梁柱之间。"),
    ("写景含打转", "湖面平静，水波不兴，几片枯叶在水面上随波轻轻打转。"
                   "远处的山影倒映在水中，随着涟漪一圈圈散开，又慢慢聚拢。"),
]

# B. 叙事（有人物施动）——不得被判为纯描写
NARRATIVE = [
    ("转身", "他转过身，看着窗外的雨。屋内的灯光把他的影子拉得很长，"
             "墙上的钟摆来回晃动，空气里浮着淡淡的尘埃。"),
    ("抬手", "她抬手拂去额前的碎发，走进房间。桌上的油灯已经快燃尽了，"
             "窗外的风声穿过门缝，屋子里的光线愈发昏暗。"),
    ("开口", "苏瑾开口打破了沉默。院子里的风穿过树梢，带起一片沙沙声，"
             "远处城墙上的旗帜也在风中翻卷。"),
]

print("[A] 纯描写段落（应全部 True）")
okA = 0
for label, text in PURE_DESC:
    r = m.is_description_paragraph(text)
    okA += r
    print(f"    {'✅' if r else '❌'} {label:12s} len={len(text):4d} -> {r}")
print(f"    A 通过 {okA}/{len(PURE_DESC)}")

print()
print("[B] 叙事段落（应全部 False，防矫枉过正）")
okB = 0
for label, text in NARRATIVE:
    r = m.is_description_paragraph(text)
    okB += (not r)
    print(f"    {'✅' if not r else '❌'} {label:12s} len={len(text):4d} -> {r}")
print(f"    B 通过 {okB}/{len(NARRATIVE)}")

# C/D 端到端
def run_case(name, paras, expect_block):
    fix = ROOT / "tests" / "_tmp_desc2"
    if fix.exists():
        shutil.rmtree(fix)
    (fix / "chapters").mkdir(parents=True)
    body = "\n\n".join(paras)
    (fix / "chapters" / "001-测试.md").write_text(
        "<!-- SUMERU_STATUS: chapter=001, status=drafted -->\n\n" + body + "\n",
        encoding="utf-8")
    r = subprocess.run([PY, "-X", "utf8", str(SCRIPT), "chapters/",
                        "--output", ".sumeru/review", "--quiet"],
                       cwd=str(fix), capture_output=True, timeout=180)
    rep = fix / ".sumeru" / "review" / "anti-ai-report.json"
    ratio = count = None
    codes = []
    if rep.exists():
        d = json.loads(rep.read_text(encoding="utf-8"))
        ch = d.get("chapters", [{}])[0]
        ratio = ch.get("metrics", {}).get("description_ratio")
        count = ch.get("metrics", {}).get("description_paragraph_count")
        codes = [i.get("code") for i in ch.get("issues", [])]
    shutil.rmtree(fix)
    hit = "narrative_high_description" in codes
    verdict = "✅" if hit == expect_block else "❌"
    print(f"    {verdict} {name}")
    print(f"        description_ratio={ratio}  段数={count}  阻断命中={hit}（期望 {expect_block}）")
    return hit == expect_block

print()
print("[C] 端到端：12 段 100% 纯描写 → 应触发 high 阻断")
okC = run_case("满篇纯描写章节", [t for _, t in PURE_DESC] * 3, True)

print()
print("[D] 端到端：正常叙事章节 → 不应误触发")
okD = run_case("正常叙事章节", [t for _, t in NARRATIVE] * 4, False)

print()
print("=" * 76)
total = okA + okB + int(okC) + int(okD)
print(f"总计：A={okA}/{len(PURE_DESC)}  B={okB}/{len(NARRATIVE)}  C={okC}  D={okD}")
print("全部通过" if (okA == len(PURE_DESC) and okB == len(NARRATIVE) and okC and okD)
      else "存在未通过项")
