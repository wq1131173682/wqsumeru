r"""精确定位 description 识别失效的双重根因。

根因 1：DESCRIPTION_PARAGRAPH_MIN_LEN = 80，而网文段落普遍 30-60 字 → 直接短路
根因 2：EVENT_VERBS 含极常见单字（看/立/放/起/出/见/到/入），长段落几乎必命中

设计对照实验：把同一段环境描写加长到 >80 字，且刻意回避所有 EVENT_VERBS。
若能识别 → 说明逻辑本身可用，问题在阈值/词表过宽。
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
print("[A] 对照：同题材描写，长度 vs 是否命中 EVENT_VERBS")
print("=" * 74)

cases = []

# 1) 短段落（网文常态 30-60 字），无 EVENT_VERBS
short_clean = ("天空阴沉，云层低垂，远处的山峦在雾气里若隐若现。"
               "林间寂静，只有风声穿过树梢。")
cases.append(("短(无动词字)", short_clean))

# 2) 短段落，含常见动词字
short_dirty = ("天空阴沉，云层低垂，远处的山峦在雾气里若隐若现。"
               "他看了一会儿，转身走了。")
cases.append(("短(含动词字)", short_dirty))

# 3) 长段落（>80 字），刻意回避所有 EVENT_VERBS
long_clean = ("天空阴沉，云层低垂，远处的山峦在雾气里若隐若现。"
              "林间寂静，只有风声穿过树梢，松针上凝着一层薄薄的水汽。"
              "崖壁的缝隙中长满了青苔，颜色深绿，如同一块湿润的绒布。"
              "谷底的溪流缓慢蜿蜒，水面上浮着几片枯叶，随波轻轻打转。")
cases.append(("长(无动词字)", long_clean))

# 4) 长段落，含一个常见动词字
long_dirty = long_clean + "他站在崖边，默默望着这片景色。"
cases.append(("长(含动词字)", long_dirty))

# 5) 长段落，仅含 EVENT_VERBS 中最常见的几个字之一
for ch in ("看", "立", "起", "放", "出", "见", "到", "入"):
    probe = long_clean + f"远处有一{ch}痕迹。"
    r = m.is_description_paragraph(probe)
    hits = [v for v in m.EVENT_VERBS if v in probe]
    print(f"  仅追加一个「{ch}」字 → 判定={r}  命中={hits}")

print()
for label, text in cases:
    r = m.is_description_paragraph(text)
    hits = [v for v in m.EVENT_VERBS if v in text]
    kws = [k for k in m.DESCRIPTION_NARRATIVE_KEYWORDS if k in text]
    print(f"  {label}  长度={len(text)}  判定纯描写={r}")
    print(f"      EVENT_VERBS 命中 = {hits}")
    print(f"      描写关键词命中  = {kws}")

print()
print("=" * 74)
print("[B] EVENT_VERBS 的误伤面：统计它们在常用段落中的必然命中率")
print("=" * 74)
# 用一段最朴素的写景文字做基准
base = ("天空阴沉，云层低垂，远处的山峦在雾气里若隐若现。"
        "林间寂静，只有风声穿过树梢，松针上凝着一层薄薄的水汽。"
        "崖壁的缝隙中长满了青苔，颜色深绿，如同一块湿润的绒布。"
        "谷底的溪流缓慢蜿蜒，水面上浮着几片枯叶，随波轻轻打转。")
print(f"  基准段落（纯写景，无人物动作）长度 = {len(base)}")
hit = [v for v in m.EVENT_VERBS if v in base]
print(f"  未追加任何内容时命中的 EVENT_VERBS = {hit}")

# 单字动词占比
single = [v for v in m.EVENT_VERBS if len(v) == 1]
print(f"  单字动词 {len(single)}/{len(m.EVENT_VERBS)} = {len(single)/len(m.EVENT_VERBS):.0%}")
print(f"  单字动词列表 = {single}")
print()
print("  解析：这些单字（走/跑/入/出/到/回/说/问/见/看/听/望/取/拿/收/放/")
print("        起/立/坐/死/伤/醒/倒…）在中文写景、心理、陈设描写中")
print("        出现概率极高，导致 80 字以上的段落几乎不可能被判定为纯描写。")
