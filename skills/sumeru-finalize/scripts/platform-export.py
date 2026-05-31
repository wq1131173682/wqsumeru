#!/usr/bin/env python3
"""
sumeru-finalize 通用格式导出脚本
将章节内容导出为 md/txt 格式（分章 + 整文），不区分平台

使用方法：
    python platform-export.py <章节目录> <格式|repair> [--output <输出目录>]

格式: md, txt
repair: 按新规则重新导出 publish/
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional


def read_chapter(file_path: Path) -> Optional[Dict]:
    """读取单个章节文件，返回章节信息"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()

        lines = text.split('\n')

        # 剥离 SUMERU_STATUS 注释（第一行）
        if lines and 'SUMERU_STATUS' in lines[0]:
            lines = lines[1:]

        if not lines:
            return None

        # 去掉第一行标题（如果有），避免重复
        # 匹配格式如：第1章 标题、# 第1章 标题、第1章标题
        first_line = lines[0].strip()
        body_start = 1 if re.search(r'第\d+章', first_line) else 0

        # 从文件名提取章节号和标题
        stem = file_path.stem
        chapter_num = 0
        title = ""

        match = re.match(r'(\d+)-(.+)', stem)
        if match:
            chapter_num = int(match.group(1))
            title = match.group(2)
        else:
            match = re.match(r'第(\d+)章\s*(.*)', stem)
            if match:
                chapter_num = int(match.group(1))
                title = match.group(2) or ""
            else:
                nums = re.findall(r'\d+', stem)
                if nums:
                    chapter_num = int(nums[0])

        return {
            "num": chapter_num,
            "title": title,
            "body": '\n'.join(lines[body_start:]).strip(),
        }
    except Exception as e:
        print(f"  读取失败 {file_path.name}: {e}")
        return None


def get_chapter_files(chapters_dir: Path) -> List[Path]:
    """获取排序后的章节文件列表"""
    files = []
    for ext in ['*.md', '*.txt']:
        files.extend(chapters_dir.glob(ext))

    def sort_key(fp):
        nums = re.findall(r'\d+', fp.stem)
        return int(nums[0]) if nums else 0

    files.sort(key=sort_key)
    return files


def format_title(chapter: Dict) -> str:
    """生成章节标题行"""
    if chapter["title"]:
        return f"第{chapter['num']}章 {chapter['title']}"
    return f"第{chapter['num']}章"


def export_chapters(chapters: List[Dict], out_dir: Path, fmt: str) -> List[Path]:
    """分章导出：每个章节独立文件，第一行仅标题"""
    ch_dir = out_dir / "chapters"
    ch_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for ch in chapters:
        padded = f"{ch['num']:03d}"
        file_path = ch_dir / f"{padded}.{fmt}"

        content = format_title(ch) + '\n\n' + ch["body"]

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        results.append(file_path)

    return results


def export_full(chapters: List[Dict], out_dir: Path, fmt: str) -> Path:
    """整文导出：所有章节合并为一个文件，章节之间空行分隔"""
    parts = []
    for ch in chapters:
        parts.append(format_title(ch) + '\n\n' + ch["body"])

    full_text = '\n\n'.join(parts)

    out_dir.mkdir(parents=True, exist_ok=True)
    file_path = out_dir / f"full.{fmt}"

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(full_text)

    return file_path


def export_all(chapters_dir: str, fmt: str, output_dir: str = None) -> Dict:
    """执行完整导出（分章 + 整文）"""
    ch_path = Path(chapters_dir)
    if not ch_path.exists():
        return {"error": f"目录不存在: {chapters_dir}"}

    if fmt not in ('md', 'txt'):
        return {"error": f"不支持的格式: {fmt}，支持: md, txt"}

    out_path = Path(output_dir) if output_dir else Path("publish")
    out_path.mkdir(parents=True, exist_ok=True)

    files = get_chapter_files(ch_path)
    if not files:
        return {"error": f"目录中未找到章节文件: {chapters_dir}"}

    chapters = []
    for fp in files:
        ch = read_chapter(fp)
        if ch:
            chapters.append(ch)

    chapters.sort(key=lambda c: c["num"])

    if not chapters:
        return {"error": "没有可导出的章节"}

    # 分章导出
    chapter_files = export_chapters(chapters, out_path, fmt)

    # 整文导出
    full_file = export_full(chapters, out_path, fmt)

    total_words = sum(len(re.findall(r'[\u4e00-\u9fff]', ch["body"])) for ch in chapters)

    return {
        "format": fmt,
        "output_dir": str(out_path),
        "chapters": len(chapters),
        "total_words": total_words,
        "chapter_files": [str(f) for f in chapter_files],
        "full_file": str(full_file),
    }


def repair(chapters_dir: str, output_dir: str = None) -> Dict:
    """修复已有导出：按新技能规则重新导出（md + txt）"""
    out_path = Path(output_dir) if output_dir else Path("publish")
    out_path.mkdir(parents=True, exist_ok=True)

    results = {}
    for fmt in ('md', 'txt'):
        result = export_all(chapters_dir, fmt, str(out_path))
        results[fmt] = result

    return results


def main():
    if len(sys.argv) < 3:
        print("用法: python platform-export.py <章节目录> <格式|repair> [--output <输出目录>] [--quiet]")
        print("\n格式: md, txt")
        print("repair: 按新规则重新导出 md + txt")
        print("\n示例:")
        print("  python platform-export.py chapters/ md")
        print("  python platform-export.py chapters/ txt --output publish")
        print("  python platform-export.py chapters/ repair")
        sys.exit(1)

    chapters_dir = sys.argv[1]
    fmt = sys.argv[2]
    output_dir = None
    quiet = "--quiet" in sys.argv

    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_dir = sys.argv[idx + 1]

    if fmt == "repair":
        result = repair(chapters_dir, output_dir)
        md_info = result.get("md", {})
        txt_info = result.get("txt", {})

        if "error" in md_info and "error" in txt_info:
            print(f"错误: 修复失败")
            if "error" in md_info:
                print(f"  md: {md_info['error']}")
            if "error" in txt_info:
                print(f"  txt: {txt_info['error']}")
            sys.exit(1)

        if not quiet:
            print("修复完成:")
            if "error" not in md_info:
                print(f"  md: {md_info['chapters']} 章, {md_info['total_words']:,} 字 -> {md_info['full_file']}")
            if "error" not in txt_info:
                print(f"  txt: {txt_info['chapters']} 章, {txt_info['total_words']:,} 字 -> {txt_info['full_file']}")
        return

    result = export_all(chapters_dir, fmt, output_dir)

    if "error" in result:
        print(f"错误: {result['error']}")
        sys.exit(1)

    if not quiet:
        print(f"导出完成 ({result['format'].upper()}):")
        print(f"  章节数: {result['chapters']}")
        print(f"  总字数: {result['total_words']:,}")
        print(f"  分章文件: {result['output_dir']}\\chapters\\")
        print(f"  整文文件: {result['full_file']}")
    else:
        print(f"已导出 {result['chapters']} 章 ({result['format'].upper()}, {result['total_words']:,}字)")


if __name__ == "__main__":
    main()
