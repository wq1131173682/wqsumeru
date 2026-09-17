#!/usr/bin/env python3
r"""把 skills/ 下的 wq-* 技能安装到本机技能根目录。

依据 DSH 权威技能根目录表（来自 app.asar 内 @deepseek-ai/dsh-skill-filesystem 文档）：

  | Rank | 来源            | 路径                        |
  |------|-----------------|-----------------------------|
  | 100  | project-dsh     | <projectRoot>/.dsh/skills   |
  | 200  | project-agents  | <projectRoot>/.agents/skills|
  | 300  | custom          | Config.customSkillDirs      |
  | 400  | user-dsh        | <dshHome>/skills   (~/.dsh/skills)     |
  | 500  | user-agents     | <agentsHome>/skills (~/.agents/skills) |

用法:
    python tools/install-skills.py                 # 安装到默认两个根
    python tools/install-skills.py --dry-run       # 只预览
    python tools/install-skills.py --target ~/.dsh/skills
    python tools/install-skills.py --clean         # 先删目标下同名目录再复制

默认目标：
    ~/.agents/skills   （本机共享 agent 根，供 Claude Code / opencode 等）
    ~/.dsh/skills      （DSH 用户根）
"""
from __future__ import annotations

import argparse
import filecmp
import hashlib
import re
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "skills"

# 不安装的内容
EXCLUDE_DIRS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".git"}
EXCLUDE_SUFFIX = {".pyc", ".pyo", ".pyd"}
EXCLUDE_NAMES = {".DS_Store", "Thumbs.db", "desktop.ini"}

DEFAULT_TARGETS = [
    ("本机（user-agents）", Path.home() / ".agents" / "skills"),
    ("DSH（user-dsh）", Path.home() / ".dsh" / "skills"),
]


def should_skip(p: Path) -> bool:
    return (
        any(part in EXCLUDE_DIRS for part in p.parts)
        or p.suffix.lower() in EXCLUDE_SUFFIX
        or p.name in EXCLUDE_NAMES
    )


def sha16(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def is_link_like(p: Path) -> bool:
    """判断是否为软链 / Junction（Windows）。"""
    if p.is_symlink():
        return True
    if hasattr(p, "is_junction"):
        try:
            return p.is_junction()
        except OSError:
            return False
    return False


def remove_existing(dst_dir: Path) -> str:
    """安全移除已存在的目标条目。

    必须区分三种情形（Windows 上尤其重要）：
      - 符号链接 / Junction：只删链接本身，**绝不递归删除**（否则会连带删掉真实源目录）
      - 普通目录：递归删除
      - 普通文件：直接删除
    返回处理说明。
    """
    if is_link_like(dst_dir):
        # 只删链接本身。用 rmdir 处理目录型链接，unlink 处理文件型链接。
        try:
            dst_dir.rmdir()
        except OSError:
            dst_dir.unlink()
        return "删除软链"
    if dst_dir.is_dir():
        shutil.rmtree(dst_dir)
        return "删除目录"
    dst_dir.unlink()
    return "删除文件"


def copy_skill(src_dir: Path, dst_root: Path, clean: bool, dry: bool,
               break_links: bool = False) -> dict:
    """把一个技能目录复制到目标根，返回统计信息。

    break_links=False（默认）：目标若是软链/Junction，**保留链接**并写入穿透
    （内容落到链接指向的真实目录，与共享一份的部署方式兼容）。
    break_links=True：把链接替换为独立副本。
    """
    dst_dir = dst_root / src_dir.name
    src_files = [p for p in src_dir.rglob("*") if p.is_file() and not should_skip(p)]

    link = is_link_like(dst_dir)
    existed = dst_dir.exists() or link
    cmp_dir = dst_dir.resolve() if link else dst_dir

    changed = []
    if existed and cmp_dir.exists():
        for p in src_files:
            rel = p.relative_to(src_dir)
            d = cmp_dir / rel
            if not d.exists() or not filecmp.cmp(p, d, shallow=False):
                changed.append(rel.as_posix())
        dst_files = [p for p in cmp_dir.rglob("*")
                     if p.is_file() and not should_skip(p)]
        extra = [p.relative_to(cmp_dir).as_posix() for p in dst_files
                 if not (src_dir / p.relative_to(cmp_dir)).exists()]
    else:
        changed = [p.relative_to(src_dir).as_posix() for p in src_files]
        extra = []

    action = ""
    if not dry:
        if existed and clean and not (link and not break_links):
            action = remove_existing(dst_dir)
        dst_dir.mkdir(parents=True, exist_ok=True)
        for p in src_files:
            rel = p.relative_to(src_dir)
            d = dst_dir / rel
            d.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, d)

    return {
        "skill": src_dir.name,
        "files": len(src_files),
        "existed": existed,
        "changed": len(changed),
        "extra": extra,
        "is_link": link,
        "link_kept": link and not break_links,
        "action": action,
        "skill_md": (src_dir / "SKILL.md").exists(),
    }


def verify_frontmatter(root: Path) -> list[str]:
    """检查已安装技能的 frontmatter 是否含 name/description。"""
    problems = []
    for sk in sorted(p for p in root.iterdir() if p.is_dir()):
        f = sk / "SKILL.md"
        if not f.exists():
            problems.append(f"{sk.name}: 缺 SKILL.md")
            continue
        head = f.read_text(encoding="utf-8", errors="replace")[:800]
        m = re.match(r"^---\r?\n(.*?)\r?\n---", head, re.S)
        if not m:
            problems.append(f"{sk.name}: frontmatter 缺失/未闭合")
            continue
        fm = m.group(1)
        if not re.search(r"^name:\s*\S", fm, re.M):
            problems.append(f"{sk.name}: frontmatter 缺 name")
        if not re.search(r"^description:\s*\S", fm, re.M):
            problems.append(f"{sk.name}: frontmatter 缺 description")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description="安装 wq-* 技能到本机技能根目录")
    ap.add_argument("--target", action="append", default=None,
                    help="自定义目标根（可多次）；省略则用默认两个根")
    ap.add_argument("--dry-run", action="store_true", help="只预览不写入")
    ap.add_argument("--clean", action="store_true",
                    help="先删除目标下同名技能目录再复制（清除陈旧文件）；"
                         "软链/Junction 默认保留，见 --break-links")
    ap.add_argument("--break-links", action="store_true",
                    help="把目标中指向别处的软链/Junction 替换为独立副本"
                         "（默认保留链接，写入穿透到链接指向处）")
    args = ap.parse_args()

    if not SRC.exists():
        print(f"❌ 找不到源目录: {SRC}")
        return 1

    skills = sorted(d for d in SRC.iterdir()
                    if d.is_dir() and d.name.startswith("wq-"))
    if not skills:
        print(f"❌ {SRC} 下没有 wq-* 技能目录")
        return 1

    if args.target:
        targets = [("自定义", Path(t).expanduser()) for t in args.target]
    else:
        targets = DEFAULT_TARGETS

    print(f"源：{SRC}")
    print(f"技能：{len(skills)} 个 -> {', '.join(d.name for d in skills)}")
    print(f"目标：{len(targets)} 个")
    for label, t in targets:
        print(f"   - {label}: {t}")
    print()

    rc = 0
    for label, target in targets:
        print("=" * 74)
        print(f"【{label}】{target}")
        print("=" * 74)
        if args.dry_run:
            print("  (dry-run：不写入)")
        try:
            target.mkdir(parents=True, exist_ok=True)
        except Exception as e:  # noqa: BLE001
            print(f"  ❌ 无法创建目标目录: {e}")
            rc = 1
            continue

        total_files = total_changed = 0
        extras_all = []
        links = 0
        for sk in skills:
            info = copy_skill(sk, target, args.clean, args.dry_run,
                              args.break_links)
            total_files += info["files"]
            total_changed += info["changed"]
            extras_all.extend(f"{info['skill']}/{e}" for e in info["extra"])
            if info["is_link"]:
                links += 1
            if not info["existed"]:
                flag = "新装"
            elif info["changed"]:
                flag = f"更新 {info['changed']}"
            else:
                flag = "已最新"
            if info["action"]:
                flag += f"（{info['action']}）"
            if info["link_kept"]:
                flag += " [软链保留]"
            print(f"  {info['skill']:20s} files={info['files']:3d}  {flag}")

        print(f"  ── 合计 {len(skills)} 技能 / {total_files} 文件 / "
              f"{total_changed} 个文件有变化")
        if links:
            print(f"  ℹ️ {links} 个目标是指向别处的软链/Junction"
                  + ("（已保留链接，内容写入穿透）" if not args.break_links
                     else "（已按 --break-links 转为独立副本）"))
        if extras_all:
            print(f"  ⚠️ 目标中存在源里没有的文件（{len(extras_all)} 个，"
                  f"加 --clean 可清除）：")
            for e in extras_all[:10]:
                print(f"       - {e}")

        if not args.dry_run:
            problems = verify_frontmatter(target)
            # 只校验 wq-* （目标根可能还有别的技能）
            problems = [p for p in problems if p.split(":")[0].startswith("wq-")]
            if problems:
                print("  ❌ frontmatter 校验失败：")
                for p in problems:
                    print(f"       - {p}")
                rc = 1
            else:
                print(f"  ✅ frontmatter 校验通过（{len(skills)} 个 wq-* 技能）")
        print()

    return rc


if __name__ == "__main__":
    sys.exit(main())
