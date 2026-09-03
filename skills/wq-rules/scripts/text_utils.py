#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
共享文本工具模块（skills/wq-rules/scripts/text_utils.py）

目的：消除 wq-review/anti-ai-scan.py 与 wq-finalize 脚本之间的重复实现，
集中维护对话提取、句子切分、段落切分、章节文件扫描等基础函数。

历史背景：P1-1/P1-2 bug（anti-ai-scan 不识别中文双引号 "" 导致对话占比检测全面失效）
就是因为对话提取逻辑散落多处、修改时遗漏同步。把对话引号匹配集中到本模块，
后续任何脚本都从这里取，改一处即全链路生效。

零外部依赖，纯 stdlib。可被任意 skill 的脚本 import：

    import sys
    from pathlib import Path
    _SHARED = Path(__file__).resolve().parent.parent.parent / "wq-rules" / "scripts"
    sys.path.insert(0, str(_SHARED))
    from text_utils import extract_dialogue_chars, split_sentences, iter_chapter_files
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Iterator, List


# ---------------------------------------------------------------------------
# 章节文件扫描
# ---------------------------------------------------------------------------

def iter_chapter_files(chapters_dir, pattern: str = "*.md") -> Iterator[Path]:
    """递归遍历章节目录下的 .md 文件，按文件名排序。

    递归以兼容分卷项目（chapters/vol-001/...）。P2-1 修复前的
    chapter-word-counter.py 只扫顶层目录，分卷项目漏章，本函数统一行为。
    """
    base = Path(chapters_dir)
    if not base.exists():
        return iter(())
    return iter(sorted(base.rglob(pattern)))


def chapter_number_from_name(filename: str) -> int | None:
    """从章节文件名提取章节号。`015-拍卖会冲突.md` -> 15。失败返回 None。"""
    m = re.match(r"^(\d{1,4})[-_]", filename)
    if m:
        return int(m.group(1))
    return None


# ---------------------------------------------------------------------------
# 句子与段落切分
# ---------------------------------------------------------------------------

def split_sentences(text: str) -> List[str]:
    """中文句子切分（中英文标点）。

    按中英文句号、问号、感叹号、省略号切。注意：英文句号会对 Mr./e.g./URL
    产生误切（P1-6 已知，影响低），网文中英文片段较少可接受。
    """
    if not text:
        return []
    text = re.sub(r"\s+", " ", text)
    raw = re.split(r"(?<=[。！？!?\.…])\s*", text)
    return [s.strip() for s in raw if s and s.strip()]


def split_paragraphs(text: str) -> List[str]:
    """按空行切分段落。"""
    if not text:
        return []
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p and p.strip()]
    return paras


# ---------------------------------------------------------------------------
# 对话提取（P1-1/P1-2 关键函数，集中维护）
# ---------------------------------------------------------------------------

# 引号正则集中定义，便于一次性增补新引号类型
_DIALOGUE_PATTERNS = (
    # 英文双引号 "..."
    re.compile(r"\"([^\"\\]*(?:\\.[^\"\\]*)*)\""),
    # 中文双引号 “...”（U+201C .. U+201D）—— 网文最常用，P1-1 修复前漏匹配
    re.compile(r"\u201c([^\u201d]*)\u201d"),
    # 直角引号 「...」
    re.compile(r"「([^」]*)」"),
)


def extract_dialogue_chars(text: str) -> int:
    """对话字数：英文双引号 / 中文双引号 / 直角引号 包裹的字符总数。

    P1-1 修复：原版只匹配英文双引号 + 直角引号，遗漏中文双引号 “”，
    导致几乎所有中文网文章节触发 narrative_low_dialogue 误报。
    """
    if not text:
        return 0
    total = 0
    for pat in _DIALOGUE_PATTERNS:
        for m in pat.finditer(text):
            total += len(m.group(1))
    return total


def extract_dialogue_segments(text: str) -> List[str]:
    """返回所有对话片段文本列表（用于对话后旁白解说检测等）。"""
    if not text:
        return []
    segments: List[str] = []
    for pat in _DIALOGUE_PATTERNS:
        for m in pat.finditer(text):
            segments.append(m.group(1))
    return segments


# ---------------------------------------------------------------------------
# 自检（直接运行时验证关键函数）
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # 冒烟自检：中文双引号必须被识别
    sample = '他说：“你好。”她答「嗯」。He said "hi".'
    d = extract_dialogue_chars(sample)
    assert d > 0, "中文双引号对话未被识别（P1-1 回归）"
    s = split_sentences("第一句。第二句！第三句？")
    assert len(s) == 3, f"句子切分错误: {s}"
    print("text_utils self-check OK; dialogue_chars=", d)
