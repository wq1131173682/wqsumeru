#!/usr/bin/env python3
r"""安装后校验：比对仓库 skills/ 与各安装根的字节一致性。

校验内容：
  1. 每个技能目录的文件集合一致（无缺失、无多余）
  2. 每个文件内容哈希一致
  3. 无 __pycache__ / .pyc 等不应安装的内容
  4. 每个技能有 SKILL.md 且 frontmatter 含 name/description
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "skills"

TARGETS = [
    ("本机 user-agents", Path.home() / ".agents" / "skills"),
    ("DSH user-dsh", Path.home() / ".dsh" / "skills"),
]

EXCLUDE_DIRS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".git"}
EXCLUDE_SUFFIX = {".pyc", ".pyo", ".pyd"}


def rel_files(root: Path) -> dict[str, str]:
    """返回 {相对路径: sha256}，跳过排除项。"""
    out = {}
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        if any(part in EXCLUDE_DIRS for part in p.parts) or p.suffix.lower() in EXCLUDE_SUFFIX:
            continue
        out[p.relative_to(root).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


def main() -> int:
    skills = sorted(d for d in SRC.iterdir() if d.is_dir() and d.name.startswith("wq-"))
    print(f"源：{SRC}（{len(skills)} 个技能）")
    print()

    rc = 0
    for label, target in TARGETS:
        print("=" * 74)
        print(f"【{label}】{target}")
        print("=" * 74)
        if not target.exists():
            print("  ❌ 目标目录不存在")
            rc = 1
            continue

        all_ok = True
        total_files = 0
        for sk in skills:
            src_files = rel_files(sk)
            dst_dir = target / sk.name
            total_files += len(src_files)
            if not dst_dir.exists():
                print(f"  ❌ {sk.name}: 未安装")
                all_ok = False
                continue
            dst_files = rel_files(dst_dir)

            missing = sorted(set(src_files) - set(dst_files))
            extra = sorted(set(dst_files) - set(src_files))
            diff = sorted(f for f in set(src_files) & set(dst_files)
                          if src_files[f] != dst_files[f])

            if missing or extra or diff:
                all_ok = False
                print(f"  ❌ {sk.name}: 缺失{len(missing)} 多余{len(extra)} 内容不同{len(diff)}")
                for f in missing[:5]:
                    print(f"        - 缺 {f}")
                for f in extra[:5]:
                    print(f"        + 多 {f}")
                for f in diff[:5]:
                    print(f"        ~ 异 {f}")
            else:
                # frontmatter 校验
                f = dst_dir / "SKILL.md"
                head = f.read_text(encoding="utf-8", errors="replace")[:800]
                m = re.match(r"^---\r?\n(.*?)\r?\n---", head, re.S)
                fm = m.group(1) if m else ""
                has = bool(re.search(r"^name:\s*\S", fm, re.M)) and \
                      bool(re.search(r"^description:\s*\S", fm, re.M))
                if has:
                    print(f"  ✅ {sk.name:20s} {len(src_files)} 文件一致")
                else:
                    print(f"  ❌ {sk.name:20s} frontmatter 缺 name/description")
                    all_ok = False

        # 检查不应存在的缓存
        pyc = [p for p in target.rglob("*.pyc") if any(s.name in p.parts for s in skills)]
        pycache = [p for p in target.rglob("__pycache__") if any(s.name in p.parts for s in skills)]
        if pyc or pycache:
            print(f"  ⚠️ 存在 __pycache__({len(pycache)}) / .pyc({len(pyc)})")
        else:
            print("  ✅ 无 __pycache__ / .pyc 残留")

        print(f"  ── {len(skills)} 技能 / {total_files} 文件："
              f"{'全部一致 ✅' if all_ok else '存在差异 ❌'}")
        print()
        if not all_ok:
            rc = 1

    return rc


if __name__ == "__main__":
    sys.exit(main())
