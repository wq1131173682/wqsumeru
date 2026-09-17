#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""修复技能安装点中的「孤儿」：实体目录应改为指向权威源的 Junction。

背景
----
`~/.qwen/skills` 下 11 个 wq-* 是 Junction，指向 `~/.agents/skills/<name>`
（多端共享一份）；只有 `wq-revise` 是实体目录，属于孤儿。

危害
----
孤儿是独立副本，不随 `~/.agents/skills` 更新；每次同步都要单独维护，
否则会长期停留在旧版本（本次即发现它滞后）。

策略（安全优先）
----------------
1. 校验孤儿内容是否与权威源完全一致（仅比对两者共有的相对路径）；
   若存在「源里没有的文件」或「内容不同」，默认**拒绝**处理并报告，
   除非显式传 --force。
2. 先把孤儿目录改名备份到 `<name>.orphan-backup-<ts>`，再建链接；
   链接创建失败则立即回滚备份。
3. 幂等：目标已是链接时跳过；孤儿不存在时跳过。
"""
from __future__ import annotations

import argparse
import filecmp
import shutil
import subprocess
import sys
import time
from pathlib import Path

HOME = Path.home()


def is_link(p: Path) -> bool:
    """识别符号链接与 Windows Junction。"""
    if p.is_symlink():
        return True
    if hasattr(p, "is_junction"):
        try:
            return p.is_junction()
        except OSError:
            return False
    return False


def rel_files(root: Path) -> set:
    return {p.relative_to(root).as_posix()
            for p in root.rglob("*") if p.is_file()}


def make_junction(link: Path, target: Path) -> None:
    """用 mklink /J 创建 Windows Junction（不需要管理员权限）。"""
    r = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(link), str(target)],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise RuntimeError(f"mklink 失败: {r.stderr.strip() or r.stdout.strip()}")


def main() -> int:
    ap = argparse.ArgumentParser(description="把孤儿实体目录改为指向权威源的 Junction")
    ap.add_argument("--root", default=str(HOME / ".qwen" / "skills"),
                    help="待修复的技能根（默认 ~/.qwen/skills）")
    ap.add_argument("--source", default=str(HOME / ".agents" / "skills"),
                    help="权威源根（默认 ~/.agents/skills）")
    ap.add_argument("--only", default="wq-revise", help="只处理指定技能（默认 wq-revise）")
    ap.add_argument("--force", action="store_true",
                    help="即使孤儿内容与源不一致也强制替换")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    root = Path(args.root).expanduser()
    source = Path(args.source).expanduser()
    target = source / args.only
    entry = root / args.only

    print(f"根      : {root}")
    print(f"权威源  : {source}")
    print(f"目标技能: {args.only}")
    print()

    if not target.exists():
        print(f"❌ 权威源不存在: {target}")
        return 1

    if is_link(entry):
        print(f"ℹ️ 已是链接，无需处理: {entry}")
        return 0

    if not entry.exists():
        print(f"ℹ️ 条目不存在（可能已被清理），无需处理: {entry}")
        return 0

    # 1) 内容比对
    src_f = rel_files(target)
    orph_f = rel_files(entry)
    only_orphan = sorted(orph_f - src_f)
    common = sorted(src_f & orph_f)
    differ = [f for f in common
              if not filecmp.cmp(target / f, entry / f, shallow=False)]

    print("=== 内容比对 ===")
    print(f"  源文件        : {len(src_f)}")
    print(f"  孤儿文件      : {len(orph_f)}")
    print(f"  仅孤儿有      : {only_orphan or '无'}")
    print(f"  内容不同      : {differ or '无'}")

    risky = only_orphan or differ
    if risky and not args.force:
        print()
        print("❌ 存在源中没有或内容不同的文件，默认拒绝处理。")
        print("   请人工确认后加 --force，或先备份。")
        return 1
    if risky:
        print()
        print("⚠️ 已用 --force，将忽略差异并继续。")

    if args.dry_run:
        print()
        print("(dry-run) 将执行：备份孤儿 → 删除 → 创建 Junction")
        return 0

    # 2) 备份
    #    备份**不放在技能根下**：根目录会被 DSH 扫描为技能条目，
    #    无 SKILL.md 的目录会污染目录/报错。放到 _skill-backups/。
    ts = time.strftime("%Y%m%d-%H%M%S")
    backup_dir = root.parent / "_skill-backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup = backup_dir / f"{args.only}.orphan-backup-{ts}"
    print()
    print("=== 执行 ===")
    shutil.move(str(entry), str(backup))
    print(f"  已备份 -> {backup.name}")

    # 3) 链接（失败回滚）
    try:
        make_junction(entry, target)
        print(f"  已创建 Junction: {entry} -> {target}")
    except Exception as e:  # noqa: BLE001
        print(f"  ❌ 链接失败: {e}")
        shutil.move(str(backup), str(entry))
        print("  已回滚备份")
        return 1

    # 4) 校验
    if not is_link(entry):
        print("  ❌ 链接校验失败")
        return 1
    probe = entry / "SKILL.md"
    if not probe.exists():
        print("  ❌ 链接穿透失败：SKILL.md 不可达")
        return 1
    print(f"  ✅ 校验通过，链接穿透可达 SKILL.md")
    print(f"  备份保留: {backup}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
