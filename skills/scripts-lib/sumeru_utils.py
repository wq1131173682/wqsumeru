#!/usr/bin/env python3
"""须弥写作 Python 脚本共享工具：参数解析、文件扫描、中文统计、路径兼容、状态追踪"""

import json, os, re, sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any


# ── 参数解析 ──────────────────────────────────────────────

def parse_args(usage: str, min_args: int = 2,
               extra_flags: Optional[List[str]] = None) -> Tuple[List[str], Dict[str, str], bool]:
    flags = {f: None for f in (extra_flags or [])}
    flags['--output'] = None
    quiet = '--quiet' in sys.argv
    positional = []
    i = 1
    while i < len(sys.argv):
        a = sys.argv[i]
        if a == '--quiet': i += 1; continue
        elif a in flags:
            flags[a] = sys.argv[i + 1] if i + 1 < len(sys.argv) else None
            i += 2
        else:
            positional.append(a); i += 1
    if len(positional) < min_args:
        print(f"用法: {usage}"); sys.exit(1)
    return positional, flags, quiet


# ── 文件扫描 ──────────────────────────────────────────────

def scan_chapter_files(chapters_dir: str) -> List[Path]:
    ch_path = Path(chapters_dir)
    files = []
    for ext in ['*.md', '*.txt']:
        files.extend(ch_path.glob(ext))
    files.sort(key=lambda fp: int(re.findall(r'\d+', fp.stem)[0]) if re.findall(r'\d+', fp.stem) else 0)
    return files


# ── 章节读取 ──────────────────────────────────────────────

def read_chapter(file_path: Path) -> Optional[Dict]:
    """读取章节，返回 {num, title, body}；自动剥离 SUMERU_STATUS"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        lines = text.split('\n')
        if lines and 'SUMERU_STATUS' in lines[0]:
            lines = lines[1:]
        if not lines:
            return None
        stem = file_path.stem
        m = re.match(r'(\d+)-(.+)', stem)
        if m:
            num, title = int(m.group(1)), m.group(2)
        else:
            m = re.match(r'第(\d+)章\s*(.*)', stem)
            num = int(m.group(1)) if m else (int(re.findall(r'\d+', stem)[0]) if re.findall(r'\d+', stem) else 0)
            title = m.group(2) if m else ""
        first = lines[0].strip()
        body_start = 1 if re.search(r'第\d+章', first) else 0
        return {"num": num, "title": title, "body": '\n'.join(lines[body_start:]).strip()}
    except Exception as e:
        print(f"  读取失败 {file_path.name}: {e}")
        return None


# ── 旧路径兼容 ────────────────────────────────────────────

PATH_MAP = {
    # (canonical, [old_paths])
    "outlines/chapters.json": [".sumeru/outline/chapter-outlines.json"],
    ".sumeru/issues.md":      [".sumeru/issues/index.json"],
    "plan.md":                ["docs/requirements.md", "docs/glossary.md", "ideas/"],
}

def resolve_path(project_root: str, canonical: str,
                 old_paths: Optional[List[str]] = None) -> Tuple[Optional[Path], bool]:
    """解析路径：优先 canonical，fallback 到旧路径

    Args:
        project_root: 项目根目录
        canonical: canonical 相对路径
        old_paths: 旧路径列表（可选；不传时从 PATH_MAP 查找）

    Returns:
        (找到的路径, 是否旧路径)
    """
    root = Path(project_root)
    cp = root / canonical
    if cp.exists():
        return cp, False

    paths = old_paths or PATH_MAP.get(canonical, [])
    for op in paths:
        full = root / op
        if full.exists():
            return full, True
        # 支持目录 fallback（如 ideas/ 目录）
        if full.is_dir():
            return full, True

    return None, False


def resolve_json(project_root: str, canonical: str,
                 old_paths: Optional[List[str]] = None) -> Optional[Dict]:
    """读取 JSON 文件，支持旧路径 fallback

    返回解析后的 dict，如文件不存在返回 None
    """
    found, is_old = resolve_path(project_root, canonical, old_paths)
    if not found:
        return None
    try:
        with open(found, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


# ── SUMERU_STATUS 解析 ────────────────────────────────────

STATUS_RE = re.compile(
    r'<!--\s*SUMERU_STATUS:\s*'
    r'chapter=(\d+),\s*status=(\w+)'
    r'(,\s*\w+=[^,]+)*'
    r'\s*-->'
)

STATUS_KV_RE = re.compile(r'(\w+)=([^,\s]+)')

def parse_status_line(line: str) -> Optional[Dict]:
    """解析 SUMERU_STATUS 注释行"""
    m = STATUS_RE.match(line.strip())
    if not m:
        return None
    result = {"chapter": int(m.group(1)), "status": m.group(2)}
    # 提取 batch 和 timestamp 等额外字段（从全文提取键值对）
    for k, v in STATUS_KV_RE.findall(line):
        if k in ("batch", "timestamp"):
            result[k] = v
    return result


def scan_status_markers(chapters_dir: str) -> Dict[str, Any]:
    """扫描 chapters/ 下所有文件的 SUMERU_STATUS，生成恢复报告

    Returns:
        {
            "total": N,
            "by_status": {"drafted": N, "polished": N, ...},
            "chapters": [{"num": 1, "status": "drafted", "batch": "001", ...}, ...],
            "latest_batch": "003",
            "missing": [缺失的章节号],
            "incomplete_batches": {"001": [已完成章节], "002": [缺失章节]},
        }
    """
    files = scan_chapter_files(chapters_dir)
    chapters = []
    for fp in files:
        try:
            with open(fp, 'r', encoding='utf-8') as f:
                first_line = f.readline()
            info = parse_status_line(first_line)
            if info:
                info["file"] = str(fp)
                chapters.append(info)
        except Exception:
            pass

    chapters.sort(key=lambda c: c["chapter"])
    total = len(chapters)
    by_status = {}
    for ch in chapters:
        s = ch["status"]
        by_status[s] = by_status.get(s, 0) + 1

    # 批次分析
    batches = {}
    for ch in chapters:
        b = ch.get("batch", "unknown")
        batches.setdefault(b, []).append(ch["chapter"])
    incomplete = {}
    for b, chs in batches.items():
        expected = max(chs) - min(chs) + 1 if chs else 1
        if len(chs) < expected:
            missing_in_batch = [n for n in range(min(chs), max(chs) + 1) if n not in chs]
            incomplete[b] = {"completed": chs, "missing": missing_in_batch}

    return {
        "total": total,
        "by_status": by_status,
        "chapters": chapters,
        "latest_batch": max(batches.keys()) if batches else None,
        "incomplete_batches": incomplete or None,
    }


# ── 工具函数 ──────────────────────────────────────────────

def count_cjk(text: str) -> int:
    return len(re.findall(r'[\u4e00-\u9fff]', text))


def sanitize_filename(title: str) -> str:
    return re.sub(r'[\\/:*?"<>|]', '', title).strip() or 'untitled'


def write_json(data: Dict, path: Optional[str]) -> None:
    if path:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def find_project_root(start: str = None) -> Optional[str]:
    """从当前或指定目录向上查找项目根（含 .sumeru/project.json 或 plan.md）"""
    cwd = Path(start or os.getcwd()).resolve()
    for parent in [cwd] + list(cwd.parents):
        markers = [parent / ".sumeru/project.json", parent / "plan.md",
                   parent / "outline.md", parent / "chapters"]
        if any(m.exists() for m in markers):
            return str(parent)
    return None
