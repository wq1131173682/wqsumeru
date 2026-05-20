#!/usr/bin/env python3
"""
sumeru-finalize 多平台格式导出脚本
将章节内容转换为各平台的发布格式

使用方法：
    python platform-export.py <章节目录> <平台名称> [--output <输出目录>]

支持平台：qidian, tomato, jj, zongheng, 17k
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# 各平台格式规则
PLATFORM_RULES = {
    "qidian": {
        "name": "起点中文网",
        "title_format": "第{num}章 {title}",
        "indent": True,
        "indent_spaces": 2,
        "blank_line_between_paragraphs": False,
        "word_range": (3000, 5000),
        "encoding": "utf-8",
    },
    "tomato": {
        "name": "番茄小说",
        "title_format": "第{num}章 {title}",
        "indent": False,
        "indent_spaces": 0,
        "blank_line_between_paragraphs": True,
        "word_range": (2000, 3000),
        "encoding": "utf-8",
    },
    "jj": {
        "name": "晋江文学城",
        "title_format": "第{num}章 {title}",
        "indent": True,
        "indent_spaces": 2,
        "blank_line_between_paragraphs": False,
        "word_range": (2500, 4000),
        "encoding": "utf-8",
        "html_support": True,
    },
    "zongheng": {
        "name": "纵横中文网",
        "title_format": "第{num}章 {title}",
        "indent": True,
        "indent_spaces": 2,
        "blank_line_between_paragraphs": False,
        "word_range": (3000, 6000),
        "encoding": "utf-8",
    },
    "17k": {
        "name": "17K小说网",
        "title_format": "第{num}章 {title}",
        "indent": True,
        "indent_spaces": 2,
        "blank_line_between_paragraphs": False,
        "word_range": (2000, 4000),
        "encoding": "utf-8",
    },
}


def extract_chapter_info(filename: str) -> Tuple[int, str]:
    """从文件名提取章节号和标题"""
    stem = Path(filename).stem
    
    # 匹配 001-标题.md 格式
    match = re.match(r'(\d+)-(.+)', stem)
    if match:
        return int(match.group(1)), match.group(2)
    
    # 匹配 第X章标题.md 格式
    match = re.match(r'第(\d+)章\s*(.*)', stem)
    if match:
        return int(match.group(1)), match.group(2) or ""
    
    # 匹配 chapter-X.md 格式
    match = re.match(r'chapter-(\d+)', stem, re.IGNORECASE)
    if match:
        return int(match.group(1)), ""
    
    # 尝试从纯数字提取
    nums = re.findall(r'\d+', stem)
    if nums:
        return int(nums[0]), ""
    
    return 0, stem


def format_title(chapter_num: int, title: str, platform: str) -> str:
    """按平台规则格式化章节标题"""
    rules = PLATFORM_RULES.get(platform, PLATFORM_RULES["qidian"])
    fmt = rules["title_format"]
    return fmt.format(num=chapter_num, title=title).strip()


def format_paragraphs(text: str, platform: str) -> str:
    """按平台规则格式化段落"""
    rules = PLATFORM_RULES.get(platform, PLATFORM_RULES["qidian"])
    
    # 提取标题行（第一行）
    lines = text.split('\n')
    title_line = lines[0].strip() if lines else ""
    body_lines = lines[1:] if len(lines) > 1 else []
    
    # 清理正文：去除多余空行，保留段落结构
    paragraphs = []
    current_para = []
    
    for line in body_lines:
        stripped = line.strip()
        if not stripped:
            if current_para:
                paragraphs.append('\n'.join(current_para))
                current_para = []
        else:
            current_para.append(stripped)
    if current_para:
        paragraphs.append('\n'.join(current_para))
    
    # 格式化段落
    formatted_paragraphs = []
    for para in paragraphs:
        # 去除已有缩进
        para = para.lstrip()
        
        # 添加缩进
        if rules["indent"]:
            spaces = "　" if rules["indent_spaces"] == 2 else " " * rules["indent_spaces"]
            para = spaces + para
        
        formatted_paragraphs.append(para)
    
    # 组装输出
    separator = '\n\n' if rules["blank_line_between_paragraphs"] else '\n'
    
    result = title_line + '\n\n' + separator.join(formatted_paragraphs)
    return result


def export_chapter(file_path: Path, platform: str, output_dir: Path) -> Dict:
    """导出单个章节到指定平台格式"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        chapter_num, title = extract_chapter_info(file_path.name)
        formatted_title = format_title(chapter_num, title, platform)
        formatted_text = format_paragraphs(text, platform)
        
        # 替换第一行为格式化标题
        lines = formatted_text.split('\n')
        lines[0] = formatted_title
        final_text = '\n'.join(lines)
        
        # 写入输出文件
        output_file = output_dir / file_path.name
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(final_text)
        
        # 统计字数
        hanzi_pattern = re.compile(r'[\u4e00-\u9fa5]')
        word_count = len(hanzi_pattern.findall(final_text))
        
        return {
            "file": file_path.name,
            "chapter": chapter_num,
            "title": title,
            "word_count": word_count,
            "status": "success"
        }
    except Exception as e:
        return {
            "file": file_path.name,
            "status": "error",
            "error": str(e)
        }


def export_all(chapters_dir: str, platform: str, output_dir: str = None) -> Dict:
    """导出所有章节"""
    chapters_path = Path(chapters_dir)
    if not chapters_path.exists():
        return {"error": f"目录不存在: {chapters_dir}"}
    
    if platform not in PLATFORM_RULES:
        return {"error": f"不支持的平台: {platform}，支持: {', '.join(PLATFORM_RULES.keys())}"}
    
    # 设置输出目录
    if output_dir:
        out_path = Path(output_dir)
    else:
        out_path = Path(f"publish/{platform}")
    out_path.mkdir(parents=True, exist_ok=True)
    
    # 扫描章节文件
    chapter_files = []
    for ext in ['*.md', '*.txt']:
        chapter_files.extend(chapters_path.glob(ext))
    
    # 按章节号排序
    def get_num(fp):
        nums = re.findall(r'\d+', fp.stem)
        return int(nums[0]) if nums else 0
    chapter_files.sort(key=get_num)
    
    if not chapter_files:
        return {"error": f"目录中未找到章节文件: {chapters_dir}"}
    
    # 导出
    results = []
    total_words = 0
    for fp in chapter_files:
        result = export_chapter(fp, platform, out_path)
        results.append(result)
        if result.get("status") == "success":
            total_words += result.get("word_count", 0)
    
    success_count = len([r for r in results if r.get("status") == "success"])
    error_count = len([r for r in results if r.get("status") == "error"])
    
    rules = PLATFORM_RULES[platform]
    
    return {
        "platform": platform,
        "platform_name": rules["name"],
        "output_dir": str(out_path),
        "chapters_exported": success_count,
        "chapters_failed": error_count,
        "total_words": total_words,
        "word_range": rules["word_range"],
        "details": results
    }


def main():
    if len(sys.argv) < 3:
        print("用法: python platform-export.py <章节目录> <平台名称> [--output <输出目录>] [--quiet]")
        print("\n支持平台: qidian, tomato, jj, zongheng, 17k")
        print("\n示例:")
        print("  python platform-export.py chapters/ qidian")
        print("  python platform-export.py chapters/ tomato --output publish/tomato")
        print("  python platform-export.py chapters/ jj --quiet")
        sys.exit(1)
    
    chapters_dir = sys.argv[1]
    platform = sys.argv[2]
    output_dir = None
    quiet = "--quiet" in sys.argv
    
    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_dir = sys.argv[idx + 1]
    
    if not quiet:
        print(f"正在导出到 {PLATFORM_RULES.get(platform, {}).get('name', platform)} 格式...")
    
    result = export_all(chapters_dir, platform, output_dir)
    
    if "error" in result:
        print(f"错误: {result['error']}")
        sys.exit(1)
    
    if not quiet:
        print(f"\n导出完成:")
        print(f"  平台: {result['platform_name']}")
        print(f"  章节数: {result['chapters_exported']}")
        print(f"  总字数: {result['total_words']:,}")
        print(f"  输出目录: {result['output_dir']}")
        
        if result['chapters_failed'] > 0:
            print(f"  失败章节: {result['chapters_failed']}")
    
    elif quiet:
        if result['chapters_exported'] > 0:
            print(f"已导出 {result['chapters_exported']} 章到 {result['platform_name']} ({result['total_words']:,}字)")
        if result['chapters_failed'] > 0:
            print(f"警告: {result['chapters_failed']} 章导出失败")


if __name__ == "__main__":
    main()
