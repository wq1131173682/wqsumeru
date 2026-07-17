#!/usr/bin/env python3
"""
sumeru-finalize 格式校验脚本
检查章节格式规范：章节标题、段落格式、标点符号等

使用方法：
    python format-validator.py <章节目录> [--output <输出文件>]

输出：
    生成 format-report.json 包含所有格式问题
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# 格式规则
FORMAT_RULES = {
    # 章节标题格式
    "chapter_title_pattern": re.compile(r'^(第[一二三四五六七八九十\d]+章|CHAPTER\s+\d+)[\s：:]\s*.+'),
    
    # 段落首行缩进检测（两个全角空格或两个半角空格）
    "indent_pattern": re.compile(r'^( {2}|　{1})[\u4e00-\u9fff]'),
    
    # 对话格式
    "dialogue_pattern": re.compile(r'[""''"][^""''"]+[""''"]'),
    
    # 标点符号规范
    "punctuation_errors": {
        '，，': '，',
        '。。': '。',
        '！！': '！',
        '？？': '？',
        '""': '"',
        '：：': '：',
        '；；': '；',
    },
    
    # 英文标点误用
    "english_punctuation": {
        ',': '，',
        '.': '。',
        '!': '！',
        '?': '？',
        ':': '：',
        ';': '；',
        '"': '"',
        "'": "'",
    },
}


def validate_chapter_title(text: str, chapter_id: str) -> List[Dict]:
    """验证章节标题格式"""
    issues = []
    
    # 检查第一行是否为章节标题
    first_line = text.split('\n')[0].strip()
    
    # 检查是否符合章节标题格式
    if not FORMAT_RULES['chapter_title_pattern'].match(first_line):
        # 尝试其他常见格式
        alt_patterns = [
            re.compile(r'^#+\s*第[一二三四五六七八九十\d]+章'),  # Markdown标题
            re.compile(r'^第[一二三四五六七八九十\d]+章'),  # 无冒号
            re.compile(r'^CHAPTER\s+\d+', re.IGNORECASE),  # 英文
        ]
        
        matched = any(p.match(first_line) for p in alt_patterns)
        if not matched and first_line:
            issues.append({
                "chapter": chapter_id,
                "type": "chapter_title",
                "severity": "medium",
                "position": 0,
                "issue": "章节标题格式不规范",
                "current": first_line,
                "suggestion": "建议使用'第X章 标题'格式",
                "example": "第1章 废柴觉醒"
            })
    
    return issues


def validate_paragraph_format(text: str, chapter_id: str, style: str = "standard") -> List[Dict]:
    """验证段落格式"""
    issues = []
    lines = text.split('\n')
    
    # 检查连续空行
    empty_count = 0
    for i, line in enumerate(lines):
        if not line.strip():
            empty_count += 1
            if empty_count > 2:
                issues.append({
                    "chapter": chapter_id,
                    "type": "paragraph",
                    "severity": "low",
                    "position": i,
                    "issue": "连续空行过多",
                    "suggestion": "删除多余空行，保持段落间一个空行即可"
                })
                empty_count = 0
        else:
            empty_count = 0
    
    # 检查段落首行缩进（根据平台风格）
    prev_blank = True
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            prev_blank = True
            continue
        if prev_blank and stripped:
            # 段落首行应有缩进（两个半角空格或一个全角空格）
            if not line.startswith('  ') and not line.startswith('　'):
                # 排除章节标题、Markdown 标记、空行等非段落内容
                if not stripped.startswith('#') and not stripped.startswith('>') and not stripped.startswith('-') and not stripped.startswith('*'):
                    issues.append({
                        "chapter": chapter_id,
                        "type": "paragraph",
                        "severity": "low",
                        "position": i + 1,
                        "issue": "段落首行缺少缩进",
                        "context": stripped[:50],
                        "suggestion": "段落首行建议缩进两个空格"
                    })
            prev_blank = False
    
    # 检查段落长度（过长的段落建议分段）
    paragraphs = text.split('\n\n')
    for i, para in enumerate(paragraphs):
        if len(para) > 500:  # 超过500字的段落
            issues.append({
                "chapter": chapter_id,
                "type": "paragraph",
                "severity": "low",
                "position": i,
                "issue": f"段落过长({len(para)}字)",
                "suggestion": "建议将长段落拆分为2-3个短段落，提升阅读体验"
            })
    
    return issues


def validate_punctuation(text: str, chapter_id: str) -> List[Dict]:
    """验证标点符号"""
    issues = []

    # 检查重复标点
    for wrong, correct in FORMAT_RULES['punctuation_errors'].items():
        if wrong in text:
            count = text.count(wrong)
            issues.append({
                "chapter": chapter_id,
                "type": "punctuation",
                "severity": "medium",
                "position": 0,
                "issue": f"重复标点'{wrong}'",
                "current": wrong,
                "correct": correct,
                "count": count,
                "suggestion": f"将'{wrong}'改为'{correct}'"
            })

    # 检查英文标点误用（中文标点前后有中文字符时才算误用）
    cn_char = r'[\u4e00-\u9fa5]'
    for wrong, correct in FORMAT_RULES['english_punctuation'].items():
        # 精确检测：中文标点前后有中文字符
        pattern = re.compile(
            cn_char + re.escape(wrong) + r'|'
            + re.escape(wrong) + cn_char
        )
        matches = list(pattern.finditer(text))
        if matches:
            issues.append({
                "chapter": chapter_id,
                "type": "punctuation",
                "severity": "medium",
                "position": matches[0].start(),
                "issue": f"中英文标点混排'{wrong}'",
                "current": wrong,
                "correct": correct,
                "count": len(matches),
                "suggestion": f"建议将英文标点'{wrong}'改为中文标点'{correct}'"
            })

    return issues


def validate_punctuation_space(text: str, chapter_id: str) -> List[Dict]:
    """检测中文标点前后的多余空格"""
    issues = []
    # 中文标点前不得有空格
    space_before = re.finditer(r' +([，。！？：；、）」》])', text)
    for m in space_before:
        ctx_start = max(0, m.start() - 10)
        ctx_end = min(len(text), m.end() + 10)
        issues.append({
            "chapter": chapter_id,
            "type": "punctuation_space",
            "severity": "low",
            "position": m.start(),
            "issue": "标点前多余空格",
            "context": text[ctx_start:ctx_end],
            "suggestion": "删除标点前的空格"
        })
    # 中文标点后不得有连续2个以上空格（排除段首缩进）
    space_after = re.finditer(r'([，。！？：；、（「《]) {2,}', text)
    for m in space_after:
        ctx_start = max(0, m.start() - 10)
        ctx_end = min(len(text), m.end() + 10)
        issues.append({
            "chapter": chapter_id,
            "type": "punctuation_space",
            "severity": "low",
            "position": m.start(),
            "issue": "标点后多余空格",
            "context": text[ctx_start:ctx_end],
            "suggestion": "标点后最多保留一个空格"
        })
    return issues


def validate_quote_closure(text: str, chapter_id: str) -> List[Dict]:
    """检测引号是否成对闭合"""
    issues = []
    # 中文双引号
    left_dq = text.count('\u201c')  # "
    right_dq = text.count('\u201d')  # "
    if left_dq != right_dq:
        issues.append({
            "chapter": chapter_id,
            "type": "quote_closure",
            "severity": "high",
            "issue": f"中文双引号未闭合（左{left_dq}个 vs 右{right_dq}个）",
            "suggestion": "检查引号是否成对使用"
        })
    # 直角引号
    left_ra = text.count('「')
    right_ra = text.count('」')
    if left_ra != right_ra:
        issues.append({
            "chapter": chapter_id,
            "type": "quote_closure",
            "severity": "high",
            "issue": f"直角引号未闭合（左{left_ra}个 vs 右{right_ra}个）",
            "suggestion": "检查引号是否成对使用"
        })
    return issues


def validate_book_title_marks(text: str, chapter_id: str) -> List[Dict]:
    """检测书名号《》规范"""
    issues = []
    left_bt = text.count('《')
    right_bt = text.count('》')
    if left_bt != right_bt:
        issues.append({
            "chapter": chapter_id,
            "type": "book_title",
            "severity": "medium",
            "issue": f"书名号未闭合（左{left_bt}个 vs 右{right_bt}个）",
            "suggestion": "检查书名号是否成对使用"
        })
    # 英文尖括号误用（中文上下文中）
    cn_char = r'[\u4e00-\u9fa5]'
    angle_matches = re.findall(
        cn_char + r'<[^>]+>|<[^>]+>' + cn_char,
        text
    )
    if angle_matches:
        issues.append({
            "chapter": chapter_id,
            "type": "book_title",
            "severity": "low",
            "issue": f"可能误用英文尖括号<>'{angle_matches[0][:20]}'",
            "count": len(angle_matches),
            "suggestion": "建议将英文'<'>'改为中文书名号'《'》'"
        })
    return issues


def validate_punctuation_format(text: str, chapter_id: str) -> List[Dict]:
    """检测省略号、破折号、括号格式规范"""
    issues = []

    # 省略号格式：... → ……，单 … → ……
    for m in re.finditer(r'\.{3,}', text):
        ctx_start = max(0, m.start() - 10)
        ctx_end = min(len(text), m.end() + 10)
        issues.append({
            "chapter": chapter_id,
            "type": "punctuation_format",
            "severity": "medium",
            "position": m.start(),
            "issue": "英文省略号'...'",
            "correct": "……",
            "context": text[ctx_start:ctx_end],
            "suggestion": "将'...'改为中文省略号'……'"
        })
    for m in re.finditer(r'(?<!…)…(?!…)', text):
        ctx_start = max(0, m.start() - 10)
        ctx_end = min(len(text), m.end() + 10)
        issues.append({
            "chapter": chapter_id,
            "type": "punctuation_format",
            "severity": "medium",
            "position": m.start(),
            "issue": "单省略号'…'",
            "correct": "……",
            "context": text[ctx_start:ctx_end],
            "suggestion": "将单'…'改为双'……'"
        })
    # 省略号后多余句号
    for m in re.finditer(r'……。', text):
        issues.append({
            "chapter": chapter_id,
            "type": "punctuation_format",
            "severity": "low",
            "position": m.start(),
            "issue": "省略号后多余句号'……。'",
            "correct": "……",
            "suggestion": "省略号已含句末功能，删除句号"
        })

    # 破折号格式：-- → ——，单个 — → ——
    for m in re.finditer(r'(?<!—)--(?!—)', text):
        ctx_start = max(0, m.start() - 10)
        ctx_end = min(len(text), m.end() + 10)
        issues.append({
            "chapter": chapter_id,
            "type": "punctuation_format",
            "severity": "medium",
            "position": m.start(),
            "issue": "英文破折号'--'",
            "correct": "——",
            "context": text[ctx_start:ctx_end],
            "suggestion": "将'--'改为中文破折号'——'"
        })
    for m in re.finditer(r'(?<!—)—(?!—)', text):
        ctx_start = max(0, m.start() - 10)
        ctx_end = min(len(text), m.end() + 10)
        issues.append({
            "chapter": chapter_id,
            "type": "punctuation_format",
            "severity": "medium",
            "position": m.start(),
            "issue": "单个破折号'—'",
            "correct": "——",
            "context": text[ctx_start:ctx_end],
            "suggestion": "将单个'—'改为双'——'"
        })

    # 括号格式：英文 () → 中文 （）
    cn_char = r'[\u4e00-\u9fa5]'
    paren_matches = re.findall(
        cn_char + r'\([^)]+\)|\([^)]+\)' + cn_char,
        text
    )
    if paren_matches:
        issues.append({
            "chapter": chapter_id,
            "type": "punctuation_format",
            "severity": "low",
            "issue": f"可能误用英文括号'()'",
            "count": len(paren_matches),
            "suggestion": "建议将英文'(')'改为中文'（'）'"
        })
    # 括号闭合
    if text.count('(') != text.count(')'):
        issues.append({
            "chapter": chapter_id,
            "type": "punctuation_format",
            "severity": "medium",
            "issue": "英文括号未闭合",
            "suggestion": "检查括号是否成对使用"
        })
    if text.count('（') != text.count('）'):
        issues.append({
            "chapter": chapter_id,
            "type": "punctuation_format",
            "severity": "medium",
            "issue": "中文括号未闭合",
            "suggestion": "检查括号是否成对使用"
        })

    return issues


def validate_dialogue_format(text: str, chapter_id: str) -> List[Dict]:
    """验证对话格式"""
    issues = []
    
    # 检查对话是否单独成段
    dialogue_pattern = re.compile(r'[""''"][^""''"]+[""''"]')
    matches = list(dialogue_pattern.finditer(text))
    
    for match in matches:
        # 检查对话前后是否有换行
        start = match.start()
        end = match.end()
        
        # 获取对话前后的上下文
        context_start = max(0, start - 5)
        context_end = min(len(text), end + 5)
        context = text[context_start:context_end]
        
        # 如果对话紧跟在其他文字后面，可能格式有问题
        if start > 0 and text[start-1] not in '\n\r':
            if text[start-1] not in '，。！？；：':
                issues.append({
                    "chapter": chapter_id,
                    "type": "dialogue",
                    "severity": "low",
                    "position": start,
                    "issue": "对话可能未单独成段",
                    "context": context,
                    "suggestion": "建议将对话单独成段，提升可读性"
                })
    
    return issues


def scan_chapters(chapters_dir: str) -> Dict:
    """扫描章节目录中的所有文件"""
    all_issues = []
    chapters_scanned = 0
    
    chapters_path = Path(chapters_dir)
    if not chapters_path.exists():
        return {"error": f"目录不存在: {chapters_dir}", "chapters_scanned": 0}
    
    for file_path in chapters_path.glob("**/*.md"):
        chapters_scanned += 1
        chapter_id = file_path.stem
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # 执行各项检查
            issues = []
            issues.extend(validate_chapter_title(text, chapter_id))
            issues.extend(validate_paragraph_format(text, chapter_id))
            issues.extend(validate_punctuation(text, chapter_id))
            issues.extend(validate_punctuation_space(text, chapter_id))
            issues.extend(validate_quote_closure(text, chapter_id))
            issues.extend(validate_book_title_marks(text, chapter_id))
            issues.extend(validate_punctuation_format(text, chapter_id))
            issues.extend(validate_dialogue_format(text, chapter_id))
            
            all_issues.extend(issues)
            
        except Exception as e:
            all_issues.append({
                "chapter": chapter_id,
                "type": "read_error",
                "severity": "high",
                "error": str(e),
                "suggestion": "检查文件编码或权限"
            })
    
    # 统计
    stats = {
        "chapter_title": len([i for i in all_issues if i.get("type") == "chapter_title"]),
        "paragraph": len([i for i in all_issues if i.get("type") == "paragraph"]),
        "punctuation": len([i for i in all_issues if i.get("type") == "punctuation"]),
        "punctuation_space": len([i for i in all_issues if i.get("type") == "punctuation_space"]),
        "quote_closure": len([i for i in all_issues if i.get("type") == "quote_closure"]),
        "book_title": len([i for i in all_issues if i.get("type") == "book_title"]),
        "punctuation_format": len([i for i in all_issues if i.get("type") == "punctuation_format"]),
        "dialogue": len([i for i in all_issues if i.get("type") == "dialogue"]),
        "read_error": len([i for i in all_issues if i.get("type") == "read_error"]),
    }
    
    return {
        "chapters_scanned": chapters_scanned,
        "total_issues": len(all_issues),
        "stats": stats,
        "issues": all_issues
    }


def main():
    if len(sys.argv) < 2:
        print("用法: python format-validator.py <章节目录> [--output <输出文件>] [--quiet]")
        print("\n示例:")
        print("  python format-validator.py .sumeru/chapters/")
        print("  python format-validator.py .sumeru/chapters/ --quiet")
        print("  python format-validator.py .sumeru/chapters/ --output format-report.json")
        sys.exit(1)
    
    chapters_dir = sys.argv[1]
    output_file = None
    quiet = "--quiet" in sys.argv
    
    # 解析参数
    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_file = sys.argv[idx + 1]
    
    # 扫描
    if not quiet:
        print(f"正在扫描章节目录: {chapters_dir}")
    result = scan_chapters(chapters_dir)
    
    # 输出
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        if not quiet:
            print(f"格式报告已保存到: {output_file}")
    elif not quiet:
        print("\n" + "="*60)
        print("格式检查结果")
        print("="*60)
        print(f"扫描章节数: {result.get('chapters_scanned', 0)}")
        print(f"发现格式问题总数: {result.get('total_issues', 0)}")
        
        if 'stats' in result:
            stats = result['stats']
            print(f"\n问题类型统计:")
            print(f"  章节标题: {stats.get('chapter_title', 0)}")
            print(f"  段落格式: {stats.get('paragraph', 0)}")
            print(f"  标点符号: {stats.get('punctuation', 0)}")
            print(f"  标点空格: {stats.get('punctuation_space', 0)}")
            print(f"  引号闭合: {stats.get('quote_closure', 0)}")
            print(f"  书名号: {stats.get('book_title', 0)}")
            print(f"  标点格式: {stats.get('punctuation_format', 0)}")
            print(f"  对话格式: {stats.get('dialogue', 0)}")
        
        if result.get('issues'):
            print("\n前10个问题示例:")
            for i, issue in enumerate(result['issues'][:10]):
                print(f"\n  [{i+1}] {issue.get('chapter')} - {issue.get('type')}")
                print(f"      {issue.get('issue', '')}")
                print(f"      {issue.get('suggestion', '')}")
    
    # 静默模式：只输出有问题的提醒
    elif quiet and result.get('total_issues', 0) > 0:
        stats = result.get('stats', {})
        punctuation = stats.get('punctuation', 0)
        chapter_title = stats.get('chapter_title', 0)
        if punctuation > 0:
            print(f"⚠️ 发现 {punctuation} 个标点符号问题")
        if chapter_title > 0:
            print(f"⚠️ 发现 {chapter_title} 个章节标题格式问题")
    
    return result


if __name__ == "__main__":
    main()
