r"""实测 anti-ai-scan 的纯描写段落识别是否失效。

假设（需验证）：EVENT_VERBS 含有大量极常见汉字（山/水/风/云/见/看/听/走/到/入/出/起/立/坐），
任何 80 字以上的中文环境描写都会命中其一，导致 is_description_paragraph 永远返回 False，
从而 description_ratio 恒为 0，high 级阻断规则（>35% 纯描写）永不触发。
"""
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "skills/wq-review/scripts/anti-ai-scan.py"

spec = importlib.util.spec_from_file_location("aas", SCRIPT)
m = importlib.util.module_from_spec(spec)
sys.modules["aas"] = m
spec.loader.exec_module(m)

print("=" * 74)
print("[1] 常量")
print("=" * 74)
print(f"  DESCRIPTION_PARAGRAPH_MIN_LEN = {m.DESCRIPTION_PARAGRAPH_MIN_LEN}")
print(f"  DESCRIPTION_RATIO_MAX         = {m.DESCRIPTION_RATIO_MAX}")
print(f"  EVENT_VERBS 数量              = {len(m.EVENT_VERBS)}")
print(f"  DESCRIPTION_NARRATIVE_KEYWORDS 数量 = {len(m.DESCRIPTION_NARRATIVE_KEYWORDS)}")
print(f"  EVENT_VERBS = {m.EVENT_VERBS}")

# 纯描写段落样本：刻意写成教科书式的环境描写，不含任何"角色动作"
SAMPLES = [
    ("标准环境描写（自然景物）",
     "天色渐暗，远处的群山被暮色笼罩，山谷间弥漫着淡淡的雾气。"
     "林间的树叶在晚风中轻轻摇曳，偶尔有几片飘落，落在寂静的小径上。"),
    ("城池外貌描写",
     "青石砌成的城墙巍峨耸立，斑驳的苔痕爬满了砖缝。"
     "城楼上的旗帜在风中猎猎作响，城门两侧的石狮已经磨损得看不清面目。"),
    ("室内陈设描写",
     "屋内陈设简单，一张木桌靠着斑驳的墙壁，桌上放着一盏油灯。"
     "窗棂上糊着泛黄的纸，光线透进来，在空气中浮起细细的尘埃。"),
    ("氛围描写",
     "空气凝重得像要滴出水来，殿内的寂静压得人喘不过气。"
     "香炉里的烟缓缓升起，在昏暗的光线中盘旋，最终消散在梁柱之间。"),
]

print()
print("=" * 74)
print("[2] is_description_paragraph 逐样本判定")
print("=" * 74)
ok = 0
for label, text in SAMPLES:
    n = len(text)
    r = m.is_description_paragraph(text)
    hits = [v for v in m.EVENT_VERBS if v in text]
    kws = [k for k in m.DESCRIPTION_NARRATIVE_KEYWORDS if k in text]
    if r:
        ok += 1
    print(f"  {label}  (长度 {n})")
    print(f"      判定为纯描写 = {r}   {'✅' if r else '❌ 未被识别'}")
    print(f"      命中的 EVENT_VERBS = {hits}")
    print(f"      命中的描写关键词   = {kws}")

print()
print(f"识别成功 {ok}/{len(SAMPLES)}")

print()
print("=" * 74)
print("[3] 阻断链路验证：构造满篇纯描写章节，看是否触发 high 阻断")
print("=" * 74)
import shutil
import subprocess

FIX = ROOT / "tests" / "_tmp_desc"
if FIX.exists():
    shutil.rmtree(FIX)
(FIX / "chapters").mkdir(parents=True)

# 10 段纯描写（全部 ≥80 字），模拟"纯描写占比 100%"的极端章节
paras = [t for _, t in SAMPLES] * 3
body = "\n\n".join(paras)
(FIX / "chapters" / "001-描写测试.md").write_text(
    "<!-- SUMERU_STATUS: chapter=001, status=drafted -->\n\n" + body + "\n",
    encoding="utf-8")

hanzi = sum(1 for c in body if "\u4e00" <= c <= "\u9fff")
print(f"  样本章节：{len(paras)} 段，汉字 {hanzi} 字")
print(f"  期望：纯描写占比接近 100% > 35% → 应触发 high 阻断 (narrative_high_description)")

r = subprocess.run([sys.executable, "-X", "utf8", str(SCRIPT),
                    "chapters/", "--output", ".sumeru/review", "--quiet"],
                   cwd=str(FIX), capture_output=True, timeout=180)
so = (r.stdout + r.stderr).decode("utf-8", errors="replace")
print(f"  退出码 = {r.returncode}")
print("  输出：")
for ln in so.strip().splitlines()[:12]:
    print(f"    {ln}")

rep = FIX / ".sumeru" / "review" / "anti-ai-report.json"
if rep.exists():
    import json
    data = json.loads(rep.read_text(encoding="utf-8"))
    ch = data.get("chapters", [{}])[0]
    met = ch.get("metrics", {})
    print()
    print(f"  description_paragraph_count = {met.get('description_paragraph_count')}")
    print(f"  description_ratio           = {met.get('description_ratio')}")
    codes = [i.get("code") for i in ch.get("issues", [])]
    print(f"  命中检查项 = {codes}")
    print(f"  是否含 narrative_high_description = {'narrative_high_description' in codes}")
    print(f"  blocking = {data.get('blocking')}")

shutil.rmtree(FIX)
print()
print("fixture cleaned:", not FIX.exists())
