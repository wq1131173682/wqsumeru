#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
wq-review 反 AI / 反水文扫描脚本

实现 wq-rules/SKILL.md 第十部分·三 的 6 维反 AI 句式扫描，
并扩展 wq-write/SKILL.md §叙事效率通用自检 中的水文硬指标与 cliché 黑名单。

使用方法：
    python anti-ai-scan.py <chapters_dir> [--outlines <outlines/chapters.json>]
                              [--output <输出目录>] [--quiet] [--strict]

输出：
    <output_dir>/anti-ai-report.json   结构化报告（程序消费）
    <output_dir>/anti-ai-report.md     Markdown 报告（人工阅读）

退出码：
    0 = 无问题
    1 = 出现 warning
    2 = 出现 critical（含阻断）
"""
from __future__ import annotations

import sys
import io

# 修复 Windows GBK 控制台无法输出 emoji
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        # 旧 Python 回退：重写 stdout 缓冲
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"

def _load_thresholds() -> dict:
    defaults = {
        "SENTENCE_PATTERN_REPEAT": 6, "SENTENCE_OPENING_REPEAT": 3,
        "OPENING_SIMILAR_WINDOW": 2, "HOOK_SIMILAR_WINDOW": 2,
        "PARAGRAPH_BUFFER_MIN": 1, "PARAGRAPH_BUFFER_MAX": 3,
        "WORD_COUNT_DEVIATION": 0.5,
        "DIALOGUE_RATIO_MIN": 0.05, "MONOLOGUE_RATIO_MAX": 0.10,
        "DESCRIPTION_RATIO_MAX": 0.35, "CORE_EVENTS_MIN": 1,
        "TIME_SCENE_SWITCH_MIN": 1, "TRANSITION_SCENE_MAX_RATIO": 0.30,
        "MICRO_ARC_WINDOW": 4, "MICRO_ARC_MIN_REPEAT": 2,
        "MICRO_ARC_MIN_PARAGRAPHS": 8,
        "DIALOG_MARKER_DOMINANCE": 0.80, "DIALOG_MARKER_MIN_TOTAL": 5,
        "DIALOG_EMOTION_COMMENTARY_MIN_HITS": 3,
        "CLICHE_HIT_THRESHOLD": 3, "DESCRIPTION_PARAGRAPH_MIN_LEN": 80,
        "EM_DASH_DENSITY_PER_1K": 5, "EM_DASH_SIMPLE_CONTINUATION_MIN": 3,
        "ELLIPSIS_FORMAT_MISMATCH_MIN": 2,
        "EXCLAMATION_STACK_MIN": 2, "EXCLAMATION_DENSITY_PER_1K": 3,
    }
    try:
        cfg_file = _CONFIG_DIR / "anti-ai-thresholds.json"
        if cfg_file.exists():
            data = json.loads(cfg_file.read_text("utf-8"))
            key_map = {"sentence_pattern_repeat": "SENTENCE_PATTERN_REPEAT", "sentence_opening_repeat": "SENTENCE_OPENING_REPEAT", "opening_similar_window": "OPENING_SIMILAR_WINDOW", "hook_similar_window": "HOOK_SIMILAR_WINDOW", "paragraph_buffer_min": "PARAGRAPH_BUFFER_MIN", "paragraph_buffer_max": "PARAGRAPH_BUFFER_MAX", "word_count_deviation": "WORD_COUNT_DEVIATION", "dialogue_ratio_min": "DIALOGUE_RATIO_MIN", "monologue_ratio_max": "MONOLOGUE_RATIO_MAX", "description_ratio_max": "DESCRIPTION_RATIO_MAX", "core_events_min": "CORE_EVENTS_MIN", "time_scene_switch_min": "TIME_SCENE_SWITCH_MIN", "transition_scene_max_ratio": "TRANSITION_SCENE_MAX_RATIO", "micro_arc_window": "MICRO_ARC_WINDOW", "micro_arc_min_repeat": "MICRO_ARC_MIN_REPEAT", "micro_arc_min_paragraphs": "MICRO_ARC_MIN_PARAGRAPHS", "dialog_marker_dominance": "DIALOG_MARKER_DOMINANCE", "dialog_marker_min_total": "DIALOG_MARKER_MIN_TOTAL", "dialog_emotion_commentary_min_hits": "DIALOG_EMOTION_COMMENTARY_MIN_HITS", "cliche_hit_threshold": "CLICHE_HIT_THRESHOLD", "description_paragraph_min_len": "DESCRIPTION_PARAGRAPH_MIN_LEN", "em_dash_density_per_1k": "EM_DASH_DENSITY_PER_1K", "em_dash_simple_continuation_min": "EM_DASH_SIMPLE_CONTINUATION_MIN", "ellipsis_format_mismatch_min": "ELLIPSIS_FORMAT_MISMATCH_MIN", "exclamation_stack_min": "EXCLAMATION_STACK_MIN", "exclamation_density_per_1k": "EXCLAMATION_DENSITY_PER_1K"}
            for jk, ck in key_map.items():
                if jk in data:
                    defaults[ck] = data[jk]
    except Exception:
        pass
    return defaults

_th = _load_thresholds()
SENTENCE_PATTERN_REPEAT = _th["SENTENCE_PATTERN_REPEAT"]
SENTENCE_OPENING_REPEAT = _th["SENTENCE_OPENING_REPEAT"]
OPENING_SIMILAR_WINDOW = _th["OPENING_SIMILAR_WINDOW"]
HOOK_SIMILAR_WINDOW = _th["HOOK_SIMILAR_WINDOW"]
PARAGRAPH_BUFFER_MIN = _th["PARAGRAPH_BUFFER_MIN"]
PARAGRAPH_BUFFER_MAX = _th["PARAGRAPH_BUFFER_MAX"]
WORD_COUNT_DEVIATION = _th["WORD_COUNT_DEVIATION"]
DIALOGUE_RATIO_MIN = _th["DIALOGUE_RATIO_MIN"]
MONOLOGUE_RATIO_MAX = _th["MONOLOGUE_RATIO_MAX"]
DESCRIPTION_RATIO_MAX = _th["DESCRIPTION_RATIO_MAX"]
CORE_EVENTS_MIN = _th["CORE_EVENTS_MIN"]
TIME_SCENE_SWITCH_MIN = _th["TIME_SCENE_SWITCH_MIN"]
TRANSITION_SCENE_MAX_RATIO = _th["TRANSITION_SCENE_MAX_RATIO"]
MICRO_ARC_WINDOW = _th["MICRO_ARC_WINDOW"]
MICRO_ARC_MIN_REPEAT = _th["MICRO_ARC_MIN_REPEAT"]
MICRO_ARC_MIN_PARAGRAPHS = _th["MICRO_ARC_MIN_PARAGRAPHS"]
DIALOG_MARKER_DOMINANCE = _th["DIALOG_MARKER_DOMINANCE"]
DIALOG_MARKER_MIN_TOTAL = _th["DIALOG_MARKER_MIN_TOTAL"]
DIALOG_EMOTION_COMMENTARY_MIN_HITS = _th["DIALOG_EMOTION_COMMENTARY_MIN_HITS"]
CLICHE_HIT_THRESHOLD = _th["CLICHE_HIT_THRESHOLD"]
DESCRIPTION_PARAGRAPH_MIN_LEN = _th["DESCRIPTION_PARAGRAPH_MIN_LEN"]
EM_DASH_DENSITY_PER_1K = _th["EM_DASH_DENSITY_PER_1K"]
EM_DASH_SIMPLE_CONTINUATION_MIN = _th["EM_DASH_SIMPLE_CONTINUATION_MIN"]
ELLIPSIS_FORMAT_MISMATCH_MIN = _th["ELLIPSIS_FORMAT_MISMATCH_MIN"]
EXCLAMATION_STACK_MIN = _th["EXCLAMATION_STACK_MIN"]
EXCLAMATION_DENSITY_PER_1K = _th["EXCLAMATION_DENSITY_PER_1K"]

def _load_cliches() -> list:
    defaults = [
        "夕阳西下", "夜色渐浓", "夜幕降临", "晨曦初露", "月光如水",
        "微风拂面", "微风徐来", "清风徐来", "寒风凛冽", "阳光明媚",
        "星光点点", "繁星满天", "雪花飘飘", "细雨绵绵",
        "眼中闪过一抹", "眼底闪过", "眸中闪过",
        "心头一震", "心中一凛", "心中暗道", "不禁感叹",
        "让人不禁", "不由得心中", "让人忍不住",
        "剑眉星目", "身材高挑", "亭亭玉立", "风华绝代",
        "国色天香", "倾国倾城", "貌美如花",
        "他沉默了片刻", "她沉默了片刻", "沉默片刻后",
        "他深吸一口气", "她深吸一口气", "深深地吸了一口气",
        "缓缓开口", "缓缓说道", "缓缓地开口",
        "新的一天开始了", "又是一天", "不知不觉间",
        "你来我往", "不分胜负", "不相上下", "棋逢对手", "难分难解",
        "数百回合", "数十回合", "数招之后", "数合之后",
        "势均力敌", "旗鼓相当", "不相伯仲",
        "身形一闪", "身形一晃", "身形暴退", "身形一滞",
        "然而就在这时", "就在这时", "就在此时", "就在此刻",
        "不料", "岂料", "哪知", "哪想到", "却不想",
        "忽然之间", "猛然间", "刹那间", "电光火石间",
        "说时迟那时快", "话音未落", "话音刚落",
        "愤怒的他", "愤怒的她", "激动的他", "激动的她",
        "温柔的眼眸", "冰冷的眼神", "深邃的眼眸", "锐利的目光",
        "紧握的拳头", "颤抖的双手", "冰冷的双手",
        "心中充满了", "心里充满了", "内心充满了",
        "不由得感到", "不禁感到", "让人感到",
    ]
    try:
        cfg_file = _CONFIG_DIR / "cliche-blacklist.json"
        if cfg_file.exists():
            data = json.loads(cfg_file.read_text("utf-8"))
            if isinstance(data, dict) and "cliches" in data:
                items = [v for cat in data["cliches"].values() for v in cat]
                if items:
                    return items
    except Exception:
        pass
    return defaults

CLICHE_BLACKLIST: List[str] = _load_cliches()

# 内心独白识别模式（粗略启发式，准确性可接受）
MONOLOGUE_PATTERNS: List[str] = [
    r"他心里想[道着]?", r"她心里想[道着]?",
    r"他心想[道着]?", r"她心想[道着]?",
    r"他暗想[道着]?", r"她暗想[道着]?",
    r"他在心里[，,。]+", r"她在心里[，,。]+",
    r"他心中[，,。]+", r"她心中[，,。]+",
    r"(不知|不觉|不由得|忍不住)想[道着]?",
    r"心中暗暗?[思忖揣度盘算想]+",
]

# 纯描写段落识别（无对话/无动作/无角色提及 + 长度≥80 字 + 句末无引号）
DESCRIPTION_NARRATIVE_KEYWORDS = [
    "天空", "云", "风", "阳光", "月光", "夜色", "星辰",
    "山", "水", "河", "湖", "海", "林", "树", "草",
    "城", "镇", "街道", "屋", "殿", "塔", "门", "墙",
    "气氛", "空气中", "弥漫", "笼罩", "寂静", "安静",
]

# 核心事件识别：含以下动词且非对话/非心理
EVENT_VERBS = [
    "打", "击", "斩", "砍", "杀", "破", "退", "挡", "接", "夺",
    "走", "跑", "逃", "追", "冲", "入", "出", "到", "离", "回",
    "说", "喊", "叫", "喝", "令", "命", "答", "问",
    "见", "看", "听", "望", "望见", "发现", "察觉", "意识到",
    "取", "拿", "交", "递", "收", "藏", "放", "丢", "丢下",
    "死", "伤", "昏", "醒", "倒", "起", "立", "跪", "坐",
]


# ---------------------------------------------------------------------------
# 文本基础工具
# ---------------------------------------------------------------------------

def split_sentences(text: str) -> List[str]:
    """中文句子切分（中英文标点）。"""
    if not text:
        return []
    # 合并多空白
    text = re.sub(r"\s+", " ", text)
    # 按中英文句号、问号、感叹号、省略号切
    raw = re.split(r"(?<=[。！？!?\.…])\s*", text)
    return [s.strip() for s in raw if s and s.strip()]


def split_paragraphs(text: str) -> List[str]:
    """按空行切分段落。"""
    if not text:
        return []
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p and p.strip()]
    return paras


def extract_dialogue_chars(text: str) -> int:
    """对话字数：双引号 / 直角引号 包裹的字符总数。"""
    total = 0
    # 双引号对话
    for m in re.finditer(r"\"([^\"\\]*(?:\\.[^\"\\]*)*)\"", text):
        total += len(m.group(1))
    # 直角引号媒介内容
    for m in re.finditer(r"「([^」]*)」", text):
        total += len(m.group(1))
    return total


def is_sv_complete(sentence: str) -> bool:
    """粗略判断一个中文句子是否主谓宾完整。

    启发式：长度 ≥ 12 字，且包含至少 1 个动词特征（动/了/着/过/是/有）。
    该启发式对网络小说足够稳健，不必上 NLP 模型。
    """
    s = sentence.strip()
    if len(s) < 12:
        return False
    verb_markers = ["了", "着", "过", "是", "有", "会", "能", "把", "被", "给", "向", "从", "到"]
    return any(m in s for m in verb_markers)


def is_transition_paragraph(paragraph: str) -> bool:
    """判断段落是否在推进剧情（含核心事件动词或对话）。"""
    if not paragraph:
        return False
    if extract_dialogue_chars(paragraph) > 0:
        return True
    if re.search(r"[「\"].*?[」\"]", paragraph):
        return True
    for verb in EVENT_VERBS:
        if verb in paragraph:
            return True
    return False


def is_description_paragraph(paragraph: str) -> bool:
    """判断段落是否纯描写（无对话/无角色动作）。"""
    if len(paragraph) < DESCRIPTION_PARAGRAPH_MIN_LEN:
        return False
    if extract_dialogue_chars(paragraph) > 0:
        return False
    # 含人物行为动词 → 非纯描写
    for verb in EVENT_VERBS:
        if verb in paragraph:
            return False
    # 至少出现一个描写关键词
    return any(kw in paragraph for kw in DESCRIPTION_NARRATIVE_KEYWORDS)


def detect_monologue_ratio(text: str) -> float:
    """粗略估算内心独白占比。"""
    if not text:
        return 0.0
    hit_chars = 0
    for pattern in MONOLOGUE_PATTERNS:
        for m in re.finditer(pattern, text):
            # 取匹配所在句的近似长度（向后 60 字截断）
            start = m.start()
            end = min(len(text), start + 60)
            chunk = text[start:end]
            hit_chars += len(chunk)
    return min(1.0, hit_chars / max(1, len(text)))


def count_cliche_hits(text: str) -> Tuple[int, List[str]]:
    """返回命中总数与命中的不同短语列表。"""
    hits: List[str] = []
    for phrase in CLICHE_BLACKLIST:
        n = text.count(phrase)
        if n > 0:
            hits.append(f"{phrase}×{n}")
    return len(hits), hits


def extract_opening_line(text: str) -> str:
    """取首段第一句作为开场。"""
    paras = split_paragraphs(text)
    if not paras:
        return ""
    sents = split_sentences(paras[0])
    return sents[0] if sents else paras[0][:60]


def extract_closing_line(text: str) -> str:
    """取末段最后一句作为结尾钩子。"""
    paras = split_paragraphs(text)
    if not paras:
        return ""
    sents = split_sentences(paras[-1])
    return sents[-1] if sents else paras[-1][-60:]


def extract_chapter_no(file_path: Path) -> str:
    """从文件名提取章节号。"""
    m = re.search(r"(\d{3})", file_path.stem)
    return m.group(1) if m else file_path.stem


# v1.3.4 对话标记动词（与 DIALOG_MARKER_DOMINANCE 配合使用）
DIALOG_MARKER_VERBS: List[str] = [
    "说", "道", "问", "答", "答曰",
    "喊", "叫", "喝道", "笑道", "叹道", "冷笑道",
    "低声道", "沉声道", "冷声道", "怒道", "问道", "答道",
    "续道", "又道", "补充道", "忙道", "急道", "忙说道",
    "沉声说", "冷冷说", "轻轻说", "缓缓说",
    "开口", "开口道", "接着说", "紧接着说",
]


def classify_paragraph_type(paragraph: str) -> str:
    """v1.3.4 段落四象限分类。
    A = 推进（含核心事件动词）
    B = 心理（含内心独白模式）
    C = 描写（纯描写/环境/外貌）
    D = 对话（含引号对话）
    优先级：D > B > A > C
    """
    if not paragraph:
        return "C"
    if re.search(r"[「\"].*?[」\"]", paragraph) or extract_dialogue_chars(paragraph) > 0:
        return "D"
    for pattern in MONOLOGUE_PATTERNS:
        if re.search(pattern, paragraph):
            return "B"
    for verb in EVENT_VERBS:
        if verb in paragraph:
            return "A"
    return "C"


def detect_micro_arc_repeat(paragraphs: List[str]) -> Tuple[int, Optional[str]]:
    """v1.3.4 段间 micro-arc 结构指纹重复检测。
    滑动窗口取 MICRO_ARC_WINDOW 段的四象限类型序列，
    若任一指纹出现 ≥ MICRO_ARC_MIN_REPEAT 次 → 命中。
    返回 (重复次数, 示例指纹) 或 (0, None)。
    """
    if len(paragraphs) < MICRO_ARC_MIN_PARAGRAPHS:
        return 0, None
    types = [classify_paragraph_type(p) for p in paragraphs]
    fingerprints = [
        "".join(types[i : i + MICRO_ARC_WINDOW])
        for i in range(len(types) - MICRO_ARC_WINDOW + 1)
    ]
    counter = Counter(fingerprints)
    repeats = [(fp, n) for fp, n in counter.items() if n >= MICRO_ARC_MIN_REPEAT]
    if not repeats:
        return 0, None
    repeats.sort(key=lambda x: -x[1])
    return repeats[0][1], repeats[0][0]


def detect_dialog_marker_dominance(text: str) -> Tuple[Optional[str], int, int, float]:
    """v1.3.4 对话标记词集中度检测。
    返回 (最显著动词, 该动词计数, 全部标记总数, 占比)。
    """
    counts: Counter = Counter()
    for verb in DIALOG_MARKER_VERBS:
        # 模式：<1-4 个中文字符><动词>[：：]  → 如 "李逍遥说：" / "他沉声道："
        pattern = r"[\u4e00-\u9fa5]{1,4}" + re.escape(verb) + r"[：:]"
        counts[verb] = len(re.findall(pattern, text))
    total = sum(counts.values())
    if total < DIALOG_MARKER_MIN_TOTAL or not counts:
        return None, 0, 0, 0.0
    top_verb, top_n = counts.most_common(1)[0]
    return top_verb, top_n, total, top_n / total


# v1.2.4 对话后旁白解说情绪词（与 DIALOG_EMOTION_COMMENTARY_MIN_HITS 配合使用）
# 对话已表达情绪后，叙述用散文"翻译"同一情绪 → AI 最典型行为模式之一
EMOTION_COMMENTARY_KEYWORDS: List[str] = [
    # "语气中/里 + 带着/透着/满是/尽是" 模式（几乎总是冗余）
    "语气中带着", "语气里带着", "语气中透着", "语气里透着",
    "语气中满是", "语气里满是", "语气中尽是", "语气里尽是",
    # "话语中/里 + 带着/透着/满是/尽是" 模式（几乎总是冗余）
    "话语中带着", "话语里带着", "话语中透着", "话语里透着",
    "话语中满是", "话语里满是", "话语中尽是", "话语里尽是",
    # "眼中/底/里 + 闪过一丝" 模式（对话后紧跟时冗余）
    "眼中闪过一丝", "眼底闪过一丝", "眸中闪过一丝",
    "眼中闪过", "眼底闪过", "眸中闪过",
    # "心中/里 + 充满了" 模式（对话后紧跟时冗余）
    "心中充满了", "心里充满了", "内心充满了",
    "心中满是", "心里满是", "内心满是",
    # "语气 + 情绪形容词" 模式（对话后紧跟时冗余）
    "语气冰冷", "语气冷淡", "语气严厉", "语气柔和",
    "语气温柔", "语气激动", "语气愤怒", "语气悲伤",
]


def detect_post_dialog_emotion_commentary(text: str) -> Tuple[int, List[str]]:
    """v1.2.4 对话后旁白解说检测。

    模式：对话引号结束后，紧跟的叙述中包含情绪解说词。
    典型形式：
    - "对话内容。"他/她的语气中带着几分不悦。
    - "对话内容。"他/她愤怒地说。
    - "对话内容。"他/她的话语里满是无奈。

    返回 (命中数, 命中详情列表)。
    """
    hits: List[str] = []
    # 匹配对话后的叙述（引号后50字内）
    # 支持中文引号「」和英文引号""
    for quote_pattern in [r'[」"][\s，。！？]?[\s]*.{0,50}', r'"[\s，。！？]?[\s]*.{0,50}']:
        for match in re.finditer(quote_pattern, text):
            narration = match.group()
            for keyword in EMOTION_COMMENTARY_KEYWORDS:
                if keyword in narration:
                    hits.append(f"对话后旁白解说: '{keyword}' in '{narration[:40]}'")
                    break
    return len(hits), hits


def detect_em_dash_abuse(text: str) -> Tuple[float, int, List[str]]:
    """检测破折号（——）滥用。

    返回 (密度per_1k_chars, 简单承接型误用数, 详情列表)。
    """
    if not text:
        return 0.0, 0, []
    hanzi = len(re.findall(r"[\u4e00-\u9fa5]", text))
    if hanzi == 0:
        return 0.0, 0, []

    all_dashes = re.findall(r"—{2,}", text)
    total_count = sum(len(d) // 2 for d in all_dashes)
    density = total_count / (hanzi / 1000) if hanzi > 0 else 0.0

    simple_hits: List[str] = []
    simple_patterns = [
        r"—{2}(?=是)",
        r"—{2}(?=有)",
        r"—{2}(?=在)",
        r"—{2}(?=这)",
        r"—{2}(?=那)",
        r"—{2}(?=上面)",
        r"—{2}(?=里面)",
        r"—{2}(?=[一-龥]{1,3}[是有着在了])",
    ]
    for pattern in simple_patterns:
        for m in re.finditer(pattern, text):
            ctx_start = max(0, m.start() - 10)
            ctx_end = min(len(text), m.end() + 20)
            ctx = text[ctx_start:ctx_end]
            simple_hits.append(f"破折号简单承接: '{ctx}'")

    return density, len(simple_hits), simple_hits


def detect_ellipsis_format(text: str) -> Tuple[int, List[str]]:
    """检测省略号格式问题。

    返回 (问题数, 详情列表)。
    """
    if not text:
        return 0, []
    issues: List[str] = []

    for m in re.finditer(r'\.{3,}', text):
        ctx_start = max(0, m.start() - 10)
        ctx_end = min(len(text), m.end() + 10)
        issues.append(f"英文省略号 '...' → 应为 '……' in '{text[ctx_start:ctx_end]}'")

    for m in re.finditer(r'(?<!…)…(?!…)', text):
        ctx_start = max(0, m.start() - 10)
        ctx_end = min(len(text), m.end() + 10)
        issues.append(f"单省略号 '…' → 应为 '……' in '{text[ctx_start:ctx_end]}'")

    for m in re.finditer(r'……。', text):
        ctx_start = max(0, m.start() - 10)
        ctx_end = min(len(text), m.end() + 10)
        issues.append(f"省略号后多余句号 '……。' → 应为 '……' in '{text[ctx_start:ctx_end]}'")

    return len(issues), issues


def detect_exclamation_abuse(text: str) -> Tuple[int, float, List[str]]:
    """检测感叹号/问号叠用和密度。

    返回 (叠用次数, 密度per_1k_chars, 详情列表)。
    """
    if not text:
        return 0, 0.0, []
    hanzi = len(re.findall(r"[\u4e00-\u9fa5]", text))
    if hanzi == 0:
        return 0, 0.0, []

    issues: List[str] = []
    stack_count = 0

    for m in re.finditer(r'！{3,}', text):
        ctx_start = max(0, m.start() - 10)
        ctx_end = min(len(text), m.end() + 10)
        issues.append(f"感叹号叠用 '{m.group()}' → 应精简为 '！' in '{text[ctx_start:ctx_end]}'")
        stack_count += 1

    for m in re.finditer(r'？{3,}', text):
        ctx_start = max(0, m.start() - 10)
        ctx_end = min(len(text), m.end() + 10)
        issues.append(f"问号叠用 '{m.group()}' → 应精简为 '？' in '{text[ctx_start:ctx_end]}'")
        stack_count += 1

    for m in re.finditer(r'[！？]{2,}', text):
        if '！' in m.group() and '？' in m.group():
            ctx_start = max(0, m.start() - 10)
            ctx_end = min(len(text), m.end() + 10)
            issues.append(f"感叹问号混合叠用 '{m.group()}' → 应保留一种 in '{text[ctx_start:ctx_end]}'")
            stack_count += 1

    exclamation_count = len(re.findall(r'[！!]', text))
    density = exclamation_count / (hanzi / 1000) if hanzi > 0 else 0.0

    return stack_count, density, issues


def load_outline_meta(outlines_path: Optional[Path]) -> Dict[str, Dict[str, Any]]:
    """读取 outlines/chapters.json，返回 {chapter_no: card}。"""
    meta: Dict[str, Dict[str, Any]] = {}
    if not outlines_path or not outlines_path.exists():
        return meta
    try:
        with open(outlines_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # 兼容多种结构：dict of cards / list of cards / {chapters: [...]}
        cards: List[Dict[str, Any]] = []
        if isinstance(data, list):
            cards = data
        elif isinstance(data, dict):
            for key in ("chapters", "items", "data"):
                if key in data and isinstance(data[key], list):
                    cards = data[key]
                    break
            if not cards:
                # 直接是 {chapter_no: card}
                cards = [{"chapter": k, **v} for k, v in data.items() if isinstance(v, dict)]
        for c in cards:
            chap = str(c.get("chapter") or c.get("id") or c.get("num") or "").zfill(3)
            if chap:
                meta[chap] = c
    except Exception:
        return meta
    return meta


# ---------------------------------------------------------------------------
# 单章扫描
# ---------------------------------------------------------------------------

def scan_chapter(
    file_path: Path,
    outline_card: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """对单个章节文件做完整反 AI / 反水文扫描。"""
    text = file_path.read_text(encoding="utf-8") if file_path.exists() else ""
    # 去除 SUMERU_STATUS 注释行
    text = re.sub(r"<!--\s*SUMERU_STATUS:.*?-->\s*\n?", "", text, flags=re.DOTALL)
    # 去除标题行
    text = re.sub(r"^第\d+章[^\n]*\n", "", text)

    chapter_no = extract_chapter_no(file_path)
    issues: List[Dict[str, Any]] = []
    metrics: Dict[str, Any] = {}

    # 1) 字数
    hanzi = len(re.findall(r"[\u4e00-\u9fa5]", text))
    metrics["hanzi_count"] = hanzi

    # 2) 对话占比
    dialogue_chars = extract_dialogue_chars(text)
    metrics["dialogue_chars"] = dialogue_chars
    metrics["dialogue_ratio"] = dialogue_chars / max(1, hanzi)
    if metrics["dialogue_ratio"] < DIALOGUE_RATIO_MIN:
        issues.append({
            "code": "narrative_low_dialogue",
            "severity": "medium",
            "scope": f"chapter {chapter_no}",
            "detail": f"对话占比 {metrics['dialogue_ratio']:.1%} < 5%（{dialogue_chars}/{hanzi} 字）"
        })

    # 3) 内心独白占比
    monologue_ratio = detect_monologue_ratio(text)
    metrics["monologue_ratio"] = monologue_ratio
    if monologue_ratio > MONOLOGUE_RATIO_MAX:
        issues.append({
            "code": "narrative_high_monologue",
            "severity": "medium",
            "scope": f"chapter {chapter_no}",
            "detail": f"内心独白占比 ≈ {monologue_ratio:.1%} > 10%"
        })

    # 4) 纯描写占比
    paras = split_paragraphs(text)
    desc_paras = [p for p in paras if is_description_paragraph(p)]
    desc_chars = sum(len(p) for p in desc_paras)
    desc_ratio = desc_chars / max(1, hanzi)
    metrics["description_paragraph_count"] = len(desc_paras)
    metrics["description_ratio"] = desc_ratio
    if desc_ratio > DESCRIPTION_RATIO_MAX:
        issues.append({
            "code": "narrative_high_description",
            "severity": "high",
            "scope": f"chapter {chapter_no}",
            "detail": f"纯描写段落占比 {desc_ratio:.1%} > 35%（{len(desc_paras)} 段 / {len(paras)} 段）"
        })

    # 5) 核心事件数（粗略启发式：含事件动词的不同段落数）
    event_paras = [p for p in paras if is_transition_paragraph(p) and not is_description_paragraph(p)]
    metrics["core_events_estimate"] = len(event_paras)
    if len(event_paras) < CORE_EVENTS_MIN:
        issues.append({
            "code": "narrative_low_event_density",
            "severity": "high",
            "scope": f"chapter {chapter_no}",
            "detail": f"核心事件段落仅 {len(event_paras)} 个，未达到 ≥1 的下限"
        })

    # 6) 时间/场景切换：检测显式时间词 + 地点词
    time_signals = len(re.findall(r"(清晨|上午|中午|下午|傍晚|夜晚|凌晨|次日|翌日|第二天|三天后|数日后|次日清晨)", text))
    location_signals = len(re.findall(r"(离开|走出|进入|来到|抵达|返回|赶到|回到|进入.+?(殿|门|城|镇|山|林|谷))", text))
    metrics["time_signals"] = time_signals
    metrics["location_signals"] = location_signals
    if time_signals + location_signals < TIME_SCENE_SWITCH_MIN:
        issues.append({
            "code": "narrative_no_time_or_scene_switch",
            "severity": "medium",
            "scope": f"chapter {chapter_no}",
            "detail": "章内无明显时间推进或场景切换"
        })

    # 7) 句式重复：连续 6 句主谓宾完整
    sents = split_sentences(text)
    max_consecutive_sv = 0
    cur = 0
    for s in sents:
        if is_sv_complete(s):
            cur += 1
            max_consecutive_sv = max(max_consecutive_sv, cur)
        else:
            cur = 0
    metrics["max_consecutive_sv_sentences"] = max_consecutive_sv
    if max_consecutive_sv >= SENTENCE_PATTERN_REPEAT:
        issues.append({
            "code": "anti_ai_sentence_pattern_repeat",
            "severity": "medium",
            "scope": f"chapter {chapter_no}",
            "detail": f"连续 {max_consecutive_sv} 句主谓宾完整（阈值 {SENTENCE_PATTERN_REPEAT}）"
        })

    # 8) 句子开头重复：同一段内连续 3 句以同一主语开头
    repeated_openings = 0
    for p in paras:
        psents = split_sentences(p)
        if len(psents) < SENTENCE_OPENING_REPEAT:
            continue
        for i in range(len(psents) - SENTENCE_OPENING_REPEAT + 1):
            heads = [re.sub(r"[\s，。、；：]", "", psents[i + j])[:2] for j in range(SENTENCE_OPENING_REPEAT)]
            if len(set(heads)) == 1:
                repeated_openings += 1
                break
    metrics["paragraphs_with_repeated_opening"] = repeated_openings
    if repeated_openings > 0:
        issues.append({
            "code": "anti_ai_opening_repeat_in_paragraph",
            "severity": "low",
            "scope": f"chapter {chapter_no}",
            "detail": f"段内连续 3 句以同一主语开头 ×{repeated_openings} 段"
        })

    # 9) 结构重复：连续 3 段都在推进剧情（无缓冲）
    structure_repeat_hits = 0
    consec = 0
    for p in paras:
        if is_transition_paragraph(p) and not is_description_paragraph(p):
            consec += 1
            if consec >= PARAGRAPH_BUFFER_MAX:
                structure_repeat_hits += 1
        else:
            consec = 0
    metrics["structure_buffer_gaps"] = structure_repeat_hits
    if structure_repeat_hits > 0:
        issues.append({
            "code": "anti_ai_structure_no_buffer",
            "severity": "low",
            "scope": f"chapter {chapter_no}",
            "detail": f"连续 3+ 段推进剧情无缓冲 ×{structure_repeat_hits}"
        })

    # 10) Cliché 黑名单命中
    hit_count, hit_details = count_cliche_hits(text)
    metrics["cliche_hits"] = hit_count
    metrics["cliche_details"] = hit_details
    if hit_count >= CLICHE_HIT_THRESHOLD:
        issues.append({
            "code": "water_text_cliche_density",
            "severity": "high",
            "scope": f"chapter {chapter_no}",
            "detail": f"命中 {hit_count} 个套路短语 ≥ {CLICHE_HIT_THRESHOLD}：{', '.join(hit_details[:5])}"
        })

    # 10.5) v1.3.4 段间 micro-arc 结构指纹重复（防套用"动作-心理-环境-对话"等固定循环）
    arc_repeat, arc_fingerprint = detect_micro_arc_repeat(paras)
    metrics["micro_arc_repeat"] = arc_repeat
    metrics["micro_arc_fingerprint"] = arc_fingerprint
    if arc_repeat >= MICRO_ARC_MIN_REPEAT and arc_fingerprint:
        # 找出该指纹的首次出现段落索引用于定位
        types = [classify_paragraph_type(p) for p in paras]
        first_idx = next(
            (i for i in range(len(types) - MICRO_ARC_WINDOW + 1)
             if "".join(types[i : i + MICRO_ARC_WINDOW]) == arc_fingerprint),
            -1,
        )
        issues.append({
            "code": "anti_ai_micro_arc_repeat",
            "severity": "medium",
            "scope": f"chapter {chapter_no}",
            "detail": (
                f"段间 micro-arc 指纹 '{arc_fingerprint}' "
                f"（A=推进/B=心理/C=描写/D=对话）"
                f"重复 {arc_repeat} 次，疑似结构模板套用"
                + (f"（首次出现于第 {first_idx + 1}-{first_idx + MICRO_ARC_WINDOW} 段）" if first_idx >= 0 else "")
            ),
        })

    # 10.6) v1.3.4 对话标记词集中度（防整章机械使用同一标记）
    top_verb, top_n, total, ratio = detect_dialog_marker_dominance(text)
    metrics["dialog_marker_top"] = top_verb
    metrics["dialog_marker_top_n"] = top_n
    metrics["dialog_marker_total"] = total
    metrics["dialog_marker_ratio"] = ratio
    if top_verb and ratio > DIALOG_MARKER_DOMINANCE:
        issues.append({
            "code": "anti_ai_dialog_marker_dominant",
            "severity": "medium",
            "scope": f"chapter {chapter_no}",
            "detail": (
                f"对话标记词 '{top_verb}' 占 {ratio:.1%}（{top_n}/{total}），"
                f"超过 {DIALOG_MARKER_DOMINANCE:.0%} 集中度阈值，疑似对话格式化"
            ),
        })

    # 10.7) v1.2.4 对话后旁白解说（防对话已表达情绪后叙述"翻译"同一情绪）
    emotion_hits, emotion_details = detect_post_dialog_emotion_commentary(text)
    metrics["dialog_emotion_commentary_hits"] = emotion_hits
    metrics["dialog_emotion_commentary_details"] = emotion_details
    if emotion_hits >= DIALOG_EMOTION_COMMENTARY_MIN_HITS:
        issues.append({
            "code": "anti_ai_dialog_emotion_commentary",
            "severity": "medium",
            "scope": f"chapter {chapter_no}",
            "detail": (
                f"对话后旁白解说命中 {emotion_hits} 处 ≥ {DIALOG_EMOTION_COMMENTARY_MIN_HITS}："
                f"{'; '.join(emotion_details[:3])}"
            ),
        })

    # 10.8) 破折号（——）滥用
    em_dash_density, em_dash_simple_hits, em_dash_details = detect_em_dash_abuse(text)
    metrics["em_dash_density"] = em_dash_density
    metrics["em_dash_simple_continuation"] = em_dash_simple_hits
    if em_dash_density >= EM_DASH_DENSITY_PER_1K or em_dash_simple_hits >= EM_DASH_SIMPLE_CONTINUATION_MIN:
        issues.append({
            "code": "punctuation_em_dash_abuse",
            "severity": "medium",
            "scope": f"chapter {chapter_no}",
            "detail": (
                f"破折号密度 {em_dash_density:.1f}/千字"
                f"（阈值 {EM_DASH_DENSITY_PER_1K}），"
                f"简单承接型误用 {em_dash_simple_hits} 处"
                f"（阈值 {EM_DASH_SIMPLE_CONTINUATION_MIN}）"
            ),
        })

    # 10.9) 省略号格式
    ellipsis_count, ellipsis_details = detect_ellipsis_format(text)
    metrics["ellipsis_format_issues"] = ellipsis_count
    if ellipsis_count >= ELLIPSIS_FORMAT_MISMATCH_MIN:
        issues.append({
            "code": "punctuation_ellipsis_format",
            "severity": "medium",
            "scope": f"chapter {chapter_no}",
            "detail": f"省略号格式问题 {ellipsis_count} 处 ≥ {ELLIPSIS_FORMAT_MISMATCH_MIN}：{'; '.join(ellipsis_details[:3])}",
        })

    # 10.10) 感叹号/问号叠用
    exclamation_stack, exclamation_density, exclamation_details = detect_exclamation_abuse(text)
    metrics["exclamation_stack"] = exclamation_stack
    metrics["exclamation_density"] = exclamation_density
    if exclamation_stack >= EXCLAMATION_STACK_MIN or exclamation_density >= EXCLAMATION_DENSITY_PER_1K:
        issues.append({
            "code": "punctuation_exclamation_abuse",
            "severity": "medium",
            "scope": f"chapter {chapter_no}",
            "detail": (
                f"感叹号/问号叠用 {exclamation_stack} 处"
                f"（阈值 {EXCLAMATION_STACK_MIN}），"
                f"感叹号密度 {exclamation_density:.1f}/千字"
                f"（阈值 {EXCLAMATION_DENSITY_PER_1K}）"
            ),
        })

    # 11) 场景类型
    scene_type = (outline_card or {}).get("sceneType") or (outline_card or {}).get("rhythm") or "unknown"
    metrics["scene_type"] = scene_type

    return {
        "chapter": chapter_no,
        "file": str(file_path),
        "metrics": metrics,
        "issues": issues,
        "opening": extract_opening_line(text),
        "closing": extract_closing_line(text),
    }


# ---------------------------------------------------------------------------
# 批次级扫描（章间关系）
# ---------------------------------------------------------------------------

def scan_batch_relations(chapter_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """跨章关系扫描：开场雷同、钩子雷同、字数波动。"""
    batch_issues: List[Dict[str, Any]] = []
    if not chapter_results:
        return batch_issues

    # 12) 开场雷同
    for i in range(len(chapter_results) - 1):
        for j in range(i + 1, min(i + 1 + OPENING_SIMILAR_WINDOW, len(chapter_results))):
            a = chapter_results[i]["opening"]
            b = chapter_results[j]["opening"]
            if not a or not b:
                continue
            # 共享 8 字子串视为雷同
            if a[:8] and a[:8] in b:
                batch_issues.append({
                    "code": "anti_ai_opening_similar",
                    "severity": "medium",
                    "scope": f"chapter {chapter_results[i]['chapter']} ↔ {chapter_results[j]['chapter']}",
                    "detail": f"开场前 8 字重复：'{a[:8]}'"
                })

    # 13) 钩子雷同
    for i in range(len(chapter_results) - 1):
        for j in range(i + 1, min(i + 1 + HOOK_SIMILAR_WINDOW, len(chapter_results))):
            a = chapter_results[i]["closing"]
            b = chapter_results[j]["closing"]
            if not a or not b:
                continue
            if a[:8] and a[:8] in b:
                batch_issues.append({
                    "code": "anti_ai_hook_similar",
                    "severity": "medium",
                    "scope": f"chapter {chapter_results[i]['chapter']} ↔ {chapter_results[j]['chapter']}",
                    "detail": f"结尾钩子前 8 字重复：'{a[:8]}'"
                })

    # 14) 字数波动
    counts = [c["metrics"]["hanzi_count"] for c in chapter_results if c["metrics"]["hanzi_count"] > 0]
    if len(counts) >= 2:
        avg = sum(counts) / len(counts)
        if avg > 0:
            for c in chapter_results:
                n = c["metrics"]["hanzi_count"]
                if n <= 0:
                    continue
                dev = (n - avg) / avg
                if abs(dev) > WORD_COUNT_DEVIATION:
                    batch_issues.append({
                        "code": "anti_ai_word_count_deviation",
                        "severity": "low",
                        "scope": f"chapter {c['chapter']}",
                        "detail": f"字数 {n} 相对批均值 {avg:.0f} 偏差 {dev:+.1%}（阈值 ±{WORD_COUNT_DEVIATION:.0%}）"
                    })

    # 15) 场景类型占比
    scene_counts: Counter = Counter()
    total = 0
    for c in chapter_results:
        st = c["metrics"].get("scene_type", "unknown")
        if st and st != "unknown":
            scene_counts[st] += 1
            total += 1
    if total > 0:
        for st, n in scene_counts.items():
            ratio = n / total
            if ratio > TRANSITION_SCENE_MAX_RATIO and st in ("slow", "transition", "日常", "过渡"):
                batch_issues.append({
                    "code": "anti_ai_scene_type_dominant",
                    "severity": "medium",
                    "scope": f"batch",
                    "detail": f"场景类型 '{st}' 占比 {ratio:.1%} > {TRANSITION_SCENE_MAX_RATIO:.0%}，疑似节奏拖沓"
                })

    return batch_issues


# ---------------------------------------------------------------------------
# 报告生成
# ---------------------------------------------------------------------------

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def build_report(
    chapter_results: List[Dict[str, Any]],
    batch_issues: List[Dict[str, Any]],
) -> Dict[str, Any]:
    all_issues: List[Dict[str, Any]] = []
    for c in chapter_results:
        all_issues.extend(c["issues"])
    all_issues.extend(batch_issues)

    severity_counts: Counter = Counter(i["severity"] for i in all_issues)
    code_counts: Counter = Counter(i["code"] for i in all_issues)

    # 阻断规则：以下任一出现即 critical，触发重写（write 阶段）
    blocking_codes = {
        "narrative_high_description",
        "narrative_low_event_density",
        "water_text_cliche_density",
    }
    # v1.3.4: micro_arc / dialog_marker 留 medium，不进阻断（先观察一轮）
    has_blocking = any(i["code"] in blocking_codes and i["severity"] in ("high", "critical") for i in all_issues)

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "total_chapters": len(chapter_results),
        "total_issues": len(all_issues),
        "severity_counts": dict(severity_counts),
        "code_counts": dict(code_counts),
        "blocking": has_blocking,
        "batch_issues": batch_issues,
        "chapters": chapter_results,
        "all_issues_sorted": sorted(
            all_issues, key=lambda x: (SEVERITY_ORDER.get(x["severity"], 9), x["scope"])
        ),
    }


def write_markdown_report(report: Dict[str, Any], md_path: Path) -> None:
    lines: List[str] = []
    lines.append("# 反 AI / 反水文扫描报告\n")
    lines.append(f"- 生成时间: {report['generated_at']}")
    lines.append(f"- 扫描章节数: {report['total_chapters']}")
    lines.append(f"- 问题总数: {report['total_issues']}")
    lines.append(f"- 是否阻断: **{'是' if report['blocking'] else '否'}**\n")
    lines.append("## 严重程度统计")
    for sev in ("critical", "high", "medium", "low"):
        n = report["severity_counts"].get(sev, 0)
        if n:
            lines.append(f"- {sev}: {n}")
    lines.append("")
    lines.append("## 问题码统计")
    for code, n in sorted(report["code_counts"].items(), key=lambda x: -x[1]):
        lines.append(f"- `{code}`: {n}")
    lines.append("")

    if report["all_issues_sorted"]:
        lines.append("## 问题清单")
        for issue in report["all_issues_sorted"]:
            lines.append(f"- [{issue['severity'].upper()}] `{issue['code']}` @ {issue['scope']} — {issue['detail']}")
        lines.append("")

    lines.append("## 各章指标")
    lines.append("| 章节 | 字数 | 对话% | 独白% | 描写% | 核心事件 | 主谓宾连击 | 开场重复段 | 套路命中 | micro-arc | 对话标记 | 旁白解说 | 破折号 | 省略号 | 感叹号 |")
    lines.append("|------|------|-------|-------|-------|----------|------------|------------|----------|-----------|----------|----------|--------|--------|--------|")
    for c in report["chapters"]:
        m = c["metrics"]
        lines.append(
            f"| {c['chapter']} | {m['hanzi_count']} | "
            f"{m['dialogue_ratio']:.1%} | {m['monologue_ratio']:.1%} | "
            f"{m['description_ratio']:.1%} | {m['core_events_estimate']} | "
            f"{m['max_consecutive_sv_sentences']} | "
            f"{m['paragraphs_with_repeated_opening']} | {m['cliche_hits']} |"
            f" {m.get('micro_arc_repeat', 0)}×{m.get('micro_arc_fingerprint') or '-'} |"
            f" {m.get('dialog_marker_top', '-')}({m.get('dialog_marker_top_n', 0)}/{m.get('dialog_marker_total', 0)}) |"
            f" {m.get('dialog_emotion_commentary_hits', 0)} |"
            f" {m.get('em_dash_density', 0):.1f}/{m.get('em_dash_simple_continuation', 0)} |"
            f" {m.get('ellipsis_format_issues', 0)} |"
            f" {m.get('exclamation_stack', 0)}/{m.get('exclamation_density', 0):.1f} |"
        )
    lines.append("")

    md_path.write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="wq-review 反 AI / 反水文扫描")
    parser.add_argument("chapters_dir", help="章节目录，例如 .sumeru/chapters/")
    parser.add_argument("--outlines", default=None, help="outlines/chapters.json 路径（可选，用于补充场景类型）")
    parser.add_argument("--output", default=".sumeru/review", help="报告输出目录")
    parser.add_argument("--quiet", action="store_true", help="静默模式：只在有问题时输出摘要")
    parser.add_argument("--strict", action="store_true", help="严格模式：medium 视作 high")
    parser.add_argument("--filter", default=None, help="只输出指定 chapter 范围，逗号分隔，如 001,002,005")
    args = parser.parse_args()

    chapters_dir = Path(args.chapters_dir)
    if not chapters_dir.exists():
        print(f"❌ 目录不存在: {chapters_dir}", file=sys.stderr)
        return 2

    outlines_path = Path(args.outlines) if args.outlines else None
    outline_meta = load_outline_meta(outlines_path)

    # 扫描所有章节
    chapter_files = sorted(
        [p for p in chapters_dir.iterdir() if p.is_file() and p.suffix == ".md"],
        key=lambda p: extract_chapter_no(p),
    )
    if not chapter_files:
        print(f"❌ 在 {chapters_dir} 中未找到 .md 章节文件", file=sys.stderr)
        return 2

    # 过滤章节
    if args.filter:
        wanted = {x.strip() for x in args.filter.split(",") if x.strip()}
        chapter_files = [p for p in chapter_files if extract_chapter_no(p) in wanted]

    # 单章扫描
    chapter_results: List[Dict[str, Any]] = []
    for fp in chapter_files:
        chap_no = extract_chapter_no(fp)
        card = outline_meta.get(chap_no)
        chapter_results.append(scan_chapter(fp, card))

    # 批次扫描
    batch_issues = scan_batch_relations(chapter_results)

    # 报告
    report = build_report(chapter_results, batch_issues)

    # 严格模式
    if args.strict:
        for issue in report["all_issues_sorted"]:
            if issue["severity"] == "medium":
                issue["severity"] = "high"
        report["blocking"] = any(
            i["code"] in {"narrative_high_description", "narrative_low_event_density", "water_text_cliche_density"}
            and i["severity"] in ("high", "critical")
            for i in report["all_issues_sorted"]
        )

    # 写报告
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "anti-ai-report.json"
    md_path = out_dir / "anti-ai-report.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown_report(report, md_path)

    # 控制台输出
    total = report["total_issues"]
    blocking = report["blocking"]
    crit = report["severity_counts"].get("critical", 0)
    high = report["severity_counts"].get("high", 0)
    med = report["severity_counts"].get("medium", 0)
    low = report["severity_counts"].get("low", 0)

    if args.quiet:
        if total == 0:
            print(f"✅ 反 AI 扫描通过 ({report['total_chapters']} 章无问题)")
        else:
            print(f"⚠️ 反 AI 扫描发现 {total} 项问题 (critical={crit} high={high} medium={med} low={low})")
            if blocking:
                print(f"🚨 含阻断规则，建议重写")
            print(f"   详见: {md_path}")
    else:
        print(f"🔍 反 AI 扫描完成: {report['total_chapters']} 章 / {total} 项问题")
        print(f"   严重程度: critical={crit} high={high} medium={med} low={low}")
        print(f"   阻断: {'是' if blocking else '否'}")
        print(f"   报告: {md_path}")
        print(f"   JSON: {json_path}")
        if report["all_issues_sorted"]:
            print("\nTop 问题（按严重度排序）:")
            for issue in report["all_issues_sorted"][:10]:
                print(f"  [{issue['severity'].upper()}] {issue['code']} @ {issue['scope']}")
                print(f"      {issue['detail']}")

    if blocking:
        return 2
    if high or crit:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
