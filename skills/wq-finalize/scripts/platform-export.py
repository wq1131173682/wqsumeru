#!/usr/bin/env python3
"""
wq-finalize 通用格式导出脚本
将章节内容导出为 md/txt/clean 格式（分章 + 整文 + 正本），支持按卷导出。

使用方法：
    python platform-export.py <章节目录> <格式|repair> [--output <输出目录>] [--project <项目根目录>]

格式: md, txt, clean (正本)
repair: 按新规则重新导出 .sumeru/publish/

按卷导出: 当 project 根目录下 outlines/chapters.json 包含 volume 字段时自动启用
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# ── 卷信息读取 ──────────────────────────────────────────────

def load_volume_info(project_root: Path) -> Optional[Dict[int, int]]:
    """从 outlines/chapters.json 读取卷信息，返回 {章节号: 卷号} 映射"""
    # 尝试新旧路径
    for candidates in [
        project_root / "outlines" / "chapters.json",
        project_root / ".sumeru" / "outlines" / "chapters.json",
    ]:
        if candidates.exists():
            try:
                with open(candidates, "r", encoding="utf-8-sig") as f:
                    data = json.load(f)
                chapters_list = data.get("chapters") or data.get("outlines") or []
                if isinstance(chapters_list, list) and len(chapters_list) > 0:
                    vol_map = {}
                    has_vol = False
                    for ch in chapters_list:
                        if not isinstance(ch, dict):
                            continue
                        ch_num = ch.get("num") or ch.get("chapter")
                        vol = ch.get("volume") or ch.get("vol")
                        if ch_num is not None and vol is not None:
                            vol_map[int(ch_num)] = int(vol)
                            has_vol = True
                    if has_vol:
                        return vol_map
            except (json.JSONDecodeError, Exception):
                pass
    return None


def get_volumes_from_outline(outline_path: Path) -> Optional[Dict[int, int]]:
    """从 outline.md 解析卷信息（正则匹配），作为兜底方案"""
    if not outline_path.exists():
        return None
    try:
        with open(outline_path, "r", encoding="utf-8-sig") as f:
            content = f.read()
    except Exception:
        return None

    vol_map = {}
    current_vol = None

    # 匹配 "第X卷" 和后续的章节范围，如: 第1卷 (第1-10章)
    for line in content.split("\n"):
        line = line.strip()
        # 匹配卷标题: ## 第1卷 XXX
        vol_match = re.search(r"第(\d+)卷", line)
        if vol_match:
            current_vol = int(vol_match.group(1))
            # 尝试从同行的章节范围提取: 第1-10章
            range_match = re.search(r"第(\d+)[-~至,，](\d+)章", line)
            if range_match:
                for n in range(int(range_match.group(1)), int(range_match.group(2)) + 1):
                    vol_map[n] = current_vol
        elif current_vol is not None:
            # 尝试从独立行匹配章节范围
            range_match = re.search(r"第(\d+)[-~至,，](\d+)章", line)
            if range_match:
                for n in range(int(range_match.group(1)), int(range_match.group(2)) + 1):
                    vol_map[n] = current_vol

    return vol_map if vol_map else None


def get_volume_name(volume_num: int, project_root: Optional[Path] = None) -> str:
    """获取卷名称，用于目录命名"""
    if project_root:
        outline_path = project_root / "outline.md"
        if not outline_path.exists():
            outline_path = project_root / ".sumeru" / "outline.md"
        if outline_path.exists():
            try:
                with open(outline_path, "r", encoding="utf-8-sig") as f:
                    content = f.read()
                # 匹配: ## 第X卷 XXX
                pattern = rf"第{volume_num}卷\s+(.+?)(?:\n|$)"
                match = re.search(pattern, content)
                if match:
                    name = match.group(1).strip().rstrip("#").strip()
                    if name:
                        return name
            except Exception:
                pass
    # 默认卷名
    vol_names = {1: "一", 2: "二", 3: "三", 4: "四", 5: "五",
                 6: "六", 7: "七", 8: "八", 9: "九", 10: "十"}
    cname = vol_names.get(volume_num, str(volume_num))
    return f"第{cname}卷"


# ── 章节读取 ──────────────────────────────────────────────

def read_chapter(file_path: Path) -> Optional[Dict]:
    """读取单个章节文件，返回章节信息"""
    try:
        with open(file_path, "r", encoding="utf-8-sig") as f:
            text = f.read()

        lines = text.split("\n")

        # 剥离 SUMERU_STATUS 注释（第一行）
        has_status = False
        if lines and "SUMERU_STATUS" in lines[0]:
            has_status = True
            lines = lines[1:]

        if not lines:
            return None

        # 去掉第一行标题（如果有），避免重复
        first_line = lines[0].strip()
        body_start = 1 if re.search(r"第\d+章", first_line) else 0

        # 从文件名提取章节号和标题
        stem = file_path.stem
        chapter_num = 0
        title = ""

        match = re.match(r"(\d+)-(.+)", stem)
        if match:
            chapter_num = int(match.group(1))
            title = match.group(2)
        else:
            match = re.match(r"第(\d+)章\s*(.*)", stem)
            if match:
                chapter_num = int(match.group(1))
                title = match.group(2) or ""
            else:
                nums = re.findall(r"\d+", stem)
                if nums:
                    chapter_num = int(nums[0])

        return {
            "num": chapter_num,
            "title": title,
            "body": "\n".join(lines[body_start:]).strip(),
            "has_status": has_status,
        }
    except Exception as e:
        print(f"  读取失败 {file_path.name}: {e}")
        return None


def get_chapter_files(chapters_dir: Path) -> List[Path]:
    """获取排序后的章节文件列表"""
    files = []
    for ext in ["*.md", "*.txt"]:
        files.extend(chapters_dir.glob(ext))

    def sort_key(fp):
        nums = re.findall(r"\d+", fp.stem)
        return int(nums[0]) if nums else 0

    files.sort(key=sort_key)
    return files


def format_title(chapter: Dict) -> str:
    """生成章节标题行"""
    if chapter["title"]:
        return f"第{chapter['num']}章 {chapter['title']}"
    return f"第{chapter['num']}章"


# ── 导出核心 ──────────────────────────────────────────────

def export_chapters(chapters: List[Dict], out_dir: Path, fmt: str, clean_md: bool = True) -> List[Path]:
    """分章导出：每个章节独立文件，第一行仅标题"""
    ch_dir = out_dir / "chapters"
    ch_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for ch in chapters:
        padded = f"{ch['num']:03d}"
        file_path = ch_dir / f"{padded}.{fmt}"

        # 清理md语法（保留纯文本）
        body = clean_markdown_syntax(ch["body"]) if clean_md else ch["body"]
        content = format_title(ch) + "\n\n" + body

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        results.append(file_path)

    return results


def export_full(chapters: List[Dict], out_dir: Path, fmt: str, clean_md: bool = True) -> Path:
    """整文导出：所有章节合并为一个文件，章节之间空行分隔"""
    parts = []
    for ch in chapters:
        # 清理md语法（保留纯文本）
        body = clean_markdown_syntax(ch["body"]) if clean_md else ch["body"]
        parts.append(format_title(ch) + "\n\n" + body)

    full_text = "\n\n".join(parts)

    out_dir.mkdir(parents=True, exist_ok=True)
    file_path = out_dir / f"full.{fmt}"

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(full_text)

    return file_path


def group_chapters_by_volume(
    chapters: List[Dict], volume_map: Dict[int, int]
) -> Dict[int, List[Dict]]:
    """按卷分组章节"""
    vol_groups: Dict[int, List[Dict]] = {}
    for ch in chapters:
        vol = volume_map.get(ch["num"], 0)
        if vol not in vol_groups:
            vol_groups[vol] = []
        vol_groups[vol].append(ch)
    # 每卷内部保持排序
    for vol in vol_groups:
        vol_groups[vol].sort(key=lambda c: c["num"])
    return vol_groups


def export_volume(
    vol_num: int, chapters: List[Dict], base_dir: Path, fmt: str, clean_md: bool = True
) -> Dict:
    """导出单卷内容（分章 + 整文）"""
    vol_dir = base_dir / f"vol-{vol_num:03d}"
    vol_dir.mkdir(parents=True, exist_ok=True)

    chapter_files = export_chapters(chapters, vol_dir, fmt, clean_md)
    full_file = export_full(chapters, vol_dir, fmt, clean_md)

    total_words = sum(
        len(re.findall(r"[\u4e00-\u9fff]", ch["body"])) for ch in chapters
    )

    return {
        "volume": vol_num,
        "chapters": len(chapters),
        "total_words": total_words,
        "chapter_files": [str(f) for f in chapter_files],
        "full_file": str(full_file),
        "output_dir": str(vol_dir),
    }


def clean_body(body: str) -> str:
    """清理正文：去除可能的残留 SUMERU_STATUS 注释"""
    lines = body.split("\n")
    while lines and "SUMERU_STATUS" in lines[0]:
        lines = lines[1:]
    return "\n".join(lines).strip()


def clean_markdown_syntax(text: str) -> str:
    """清理Markdown语法，保留纯文本（用于小说平台上传）"""
    # 移除加粗
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    # 移除斜体
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    # 移除删除线
    text = re.sub(r'~~(.+?)~~', r'\1', text)
    # 移除行内代码
    text = re.sub(r'`(.+?)`', r'\1', text)
    # 移除标题标记（保留内容）
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # 移除分割线
    text = re.sub(r'^[-*_]{3,}\s*$', '', text, flags=re.MULTILINE)
    # 移除引用标记
    text = re.sub(r'^>\s*', '', text, flags=re.MULTILINE)
    # 移除无序列表标记
    text = re.sub(r'^[-*+]\s+', '', text, flags=re.MULTILINE)
    # 移除有序列表标记
    text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE)
    # 移除图片（必须在链接之前，否则链接正则会先吃掉图片的[]部分）
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    # 移除链接，保留文本
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)
    # 清理多余空行
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text


# ── 主导出逻辑 ──────────────────────────────────────────────

def export_all(
    chapters_dir: str,
    fmt: str,
    output_dir: str = None,
    project_root: str = None,
) -> Dict:
    """执行完整导出（分章 + 整文 + 按卷 + 正本）"""
    ch_path = Path(chapters_dir)
    if not ch_path.exists():
        return {"error": f"目录不存在: {chapters_dir}"}

    if fmt not in ("md", "txt", "clean"):
        return {"error": f"不支持的格式: {fmt}，支持: md, txt, clean"}

    out_path = Path(output_dir) if output_dir else Path(".sumeru/publish")
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

    result = {
        "format": fmt,
        "chapters": len(chapters),
        "total_words": 0,
    }

    # ── 读取卷信息 ──
    volume_map = None
    if project_root:
        proj_path = Path(project_root)
        volume_map = load_volume_info(proj_path)
        if volume_map is None:
            # 尝试从 outline.md 兜底
            outline_path = proj_path / "outline.md"
            if not outline_path.exists():
                outline_path = proj_path / ".sumeru" / "outline.md"
            volume_map = get_volumes_from_outline(outline_path)

    has_volumes = volume_map is not None and len(volume_map) > 0

    # ── clean 格式（正本）──
    if fmt == "clean":
        clean_dir = out_path / "clean"
        clean_dir.mkdir(parents=True, exist_ok=True)
        result["output_dir"] = str(clean_dir)

        # 正本：将每章正文清理后直接写入
        clean_chapters = []
        for ch in chapters:
            clean_body_text = clean_body(ch["body"])
            clean_chapters.append({
                "num": ch["num"],
                "title": ch["title"],
                "body": clean_body_text,
            })

        # 分章正本（clean格式不清理md语法，保留原始内容）
        ch_files = export_chapters(clean_chapters, clean_dir, "md", clean_md=False)
        # 整文正本
        full_file = export_full(clean_chapters, clean_dir, "md", clean_md=False)

        # 按卷正本
        vol_results = None
        if has_volumes:
            vol_groups = group_chapters_by_volume(clean_chapters, volume_map)
            vol_results = []
            for vol_num in sorted(vol_groups.keys()):
                vresult = export_volume(vol_num, vol_groups[vol_num], clean_dir, "md", clean_md=False)
                vol_results.append(vresult)
            result["volumes"] = vol_results

        total_words = sum(
            len(re.findall(r"[\u4e00-\u9fff]", ch["body"])) for ch in clean_chapters
        )

        result.update({
            "total_words": total_words,
            "chapter_files": [str(f) for f in ch_files],
            "full_file": str(full_file),
        })
        return result

    # ── md / txt 格式 ──
    # 格式子目录: .sumeru/publish/md/ 或 .sumeru/publish/txt/
    fmt_dir = out_path / fmt
    fmt_dir.mkdir(parents=True, exist_ok=True)
    result["output_dir"] = str(fmt_dir)

    # 分章导出（清理md语法，保留纯文本）
    chapter_files = export_chapters(chapters, fmt_dir, fmt, clean_md=True)

    # 整文导出
    full_file = export_full(chapters, fmt_dir, fmt, clean_md=True)

    # 按卷导出
    vol_results = None
    if has_volumes:
        vol_groups = group_chapters_by_volume(chapters, volume_map)
        vol_results = []
        for vol_num in sorted(vol_groups.keys()):
            vresult = export_volume(vol_num, vol_groups[vol_num], fmt_dir, fmt, clean_md=True)
            vol_results.append(vresult)
        result["volumes"] = vol_results

    total_words = sum(
        len(re.findall(r"[\u4e00-\u9fff]", ch["body"])) for ch in chapters
    )

    result.update({
        "total_words": total_words,
        "chapter_files": [str(f) for f in chapter_files],
        "full_file": str(full_file),
    })

    return result


# ── 修复模式 ──────────────────────────────────────────────

def repair(chapters_dir: str, output_dir: str = None, project_root: str = None) -> Dict:
    """修复已有导出：按新技能规则重新导出（md + txt + clean）"""
    out_path = Path(output_dir) if output_dir else Path(".sumeru/publish")
    out_path.mkdir(parents=True, exist_ok=True)

    results = {}
    for fmt in ("md", "txt", "clean"):
        result = export_all(chapters_dir, fmt, str(out_path), project_root)
        results[fmt] = result

    return results


# ── CLI ──────────────────────────────────────────────────

def pretty_print_result(result: Dict):
    """友好打印导出结果"""
    fmt = result.get("format", "?").upper()
    error = result.get("error")
    if error:
        print(f"错误: {error}")
        return

    chapters = result.get("chapters", 0)
    words = result.get("total_words", 0)
    full_file = result.get("full_file", "")
    output_dir = result.get("output_dir", "")

    print(f"导出完成 ({fmt}):")
    print(f"  章节数: {chapters}")
    print(f"  总字数: {words:,}")
    print(f"  整文文件: {full_file}")
    print(f"  分章目录: {output_dir}\\chapters\\")

    volumes = result.get("volumes")
    if volumes:
        print(f"  按卷导出:")
        for vol in volumes:
            vol_dir = vol.get("output_dir", "")
            vol_ch = vol.get("chapters", 0)
            vol_words = vol.get("total_words", 0)
            print(f"    vol-{vol['volume']:03d}: {vol_ch} 章, {vol_words:,} 字 -> {vol_dir}")


def main():
    if len(sys.argv) < 3:
        print("用法: python platform-export.py <章节目录> <格式|repair> [--output <输出目录>] [--project <项目根目录>] [--quiet]")
        print()
        print("格式: md, txt, clean")
        print("  md:    Markdown 格式导出（.sumeru/publish/md/）")
        print("  txt:   纯文本格式导出（.sumeru/publish/txt/）")
        print("  clean: 正本导出（.sumeru/publish/clean/，清理 SUMERU_STATUS 注释）")
        print("  repair: 按新规则重新导出 md + txt + clean")
        print()
        print("示例:")
        print("  python platform-export.py .sumeru/chapters/ md")
        print("  python platform-export.py .sumeru/chapters/ txt --output .sumeru/publish")
        print("  python platform-export.py .sumeru/chapters/ md --project .")
        print("  python platform-export.py .sumeru/chapters/ clean")
        print("  python platform-export.py .sumeru/chapters/ repair")
        print("  python platform-export.py .sumeru/chapters/ repair --project .")
        sys.exit(1)

    chapters_dir = sys.argv[1]
    fmt = sys.argv[2]
    output_dir = None
    project_root = None
    quiet = "--quiet" in sys.argv

    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_dir = sys.argv[idx + 1]

    if "--project" in sys.argv:
        idx = sys.argv.index("--project")
        if idx + 1 < len(sys.argv):
            project_root = sys.argv[idx + 1]

    if fmt == "repair":
        result = repair(chapters_dir, output_dir, project_root)
        if not quiet:
            for f, info in result.items():
                if "error" in info:
                    print(f"  {f}: {info['error']}")
                else:
                    vols = info.get("volumes")
                    vol_info = f", {len(vols)} 卷" if vols else ""
                    print(f"  {f}: {info['chapters']} 章{vol_info}, {info['total_words']:,} 字 -> {info['full_file']}")
        else:
            # quiet: 一行摘要
            parts = []
            for f, info in result.items():
                if "error" not in info:
                    parts.append(f"{f}({info['chapters']}章,{info['total_words']:,}字)")
            print(f"修复完成: {' | '.join(parts)}")
        return

    result = export_all(chapters_dir, fmt, output_dir, project_root)

    if "error" in result:
        print(f"错误: {result['error']}")
        sys.exit(1)

    if not quiet:
        pretty_print_result(result)
    else:
        vols = result.get("volumes")
        vol_info = f", {len(vols)} 卷" if vols else ""
        print(f"已导出 {result['chapters']} 章{vol_info} ({result['format'].upper()}, {result['total_words']:,}字)")


if __name__ == "__main__":
    main()
