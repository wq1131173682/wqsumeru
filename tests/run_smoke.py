#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WQ 写作技能集 · 冒烟测试套件
================================================================
目的：守住关键 bug 修复不回归，验证核心脚本可在最小样本上跑通。

运行：
    python tests/run_smoke.py
    python -m pytest tests/run_smoke.py        # 如装了 pytest

覆盖：
    1. text_utils 共享模块（P1-1/P1-2 中文双引号对话提取回归守卫）
    2. anti-ai-scan.py 在样本章节上退出码合法（0/1/2）
    3. format-validator.py / spell-check.py / sensitive-word-filter.py 可跑通
    4. continuity-check.py / foreshadowing-tracker.py 在空 continuity 上不崩

新增功能需补对应测试用例（README 约定：所有新增功能需含测试用例）。
"""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS = REPO / "skills"
FIXTURES = REPO / "tests" / "fixtures"
CHAPTERS = FIXTURES / "chapters"

_passed = 0
_failed = 0


def check(name: str, cond: bool, detail: str = ""):
    global _passed, _failed
    if cond:
        _passed += 1
        print(f"  PASS  {name}")
    else:
        _failed += 1
        print(f"  FAIL  {name}  {detail}")


# ---------------------------------------------------------------------------
# 1. text_utils 回归守卫
# ---------------------------------------------------------------------------
def test_text_utils_dialogue_chinese_quotes():
    """P1-1/P1-2 守卫：中文双引号 “” 必须被识别为对话。"""
    shared = SKILLS / "wq-rules" / "scripts"
    sys.path.insert(0, str(shared))
    import text_utils  # noqa: E402

    # 中文双引号对话（“你好啊。”含句号共 4 字符）
    d1 = text_utils.extract_dialogue_chars('他说：“你好啊。”')
    check("chinese-quote dialogue recognized", d1 == 4, f"got {d1}")

    # 直角引号
    d2 = text_utils.extract_dialogue_chars('她答「嗯」。')
    check("corner-quote dialogue recognized", d2 == 1, f"got {d2}")

    # 英文双引号
    d3 = text_utils.extract_dialogue_chars('He said "hi".')
    check("english-quote dialogue recognized", d3 == 2, f"got {d3}")

    # 句子切分
    s = text_utils.split_sentences("第一句。第二句！第三句？")
    check("split_sentences 3 sentences", len(s) == 3, f"got {len(s)}")

    # 章节文件递归扫描
    files = list(text_utils.iter_chapter_files(CHAPTERS))
    check("iter_chapter_files finds fixture", len(files) >= 1, f"got {len(files)}")


# ---------------------------------------------------------------------------
# 2. anti-ai-scan.py 跑通
# ---------------------------------------------------------------------------
def test_anti_ai_scan_runs():
    import subprocess
    out = REPO / "tests" / "_tmp_review"
    out.mkdir(exist_ok=True)
    script = SKILLS / "wq-review" / "scripts" / "anti-ai-scan.py"
    proc = subprocess.run(
        [sys.executable, str(script), str(CHAPTERS), "--output", str(out), "--quiet"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(REPO),
    )
    check("anti-ai-scan exit code in {0,1,2,3}", proc.returncode in (0, 1, 2, 3),
          f"exit={proc.returncode} stderr={proc.stderr[:200]}")
    # 中文双引号样本不应触发 narrative_low_dialogue 误报（P1-1 守卫）
    # 此处只确保不崩；误报判定在文本断言里

    # v1.4.4: 字数不足触发 exit 3
    short_dir = REPO / "tests" / "_tmp_short"
    short_dir.mkdir(exist_ok=True)
    (short_dir / "001-短.md").write_text("第1章 短\n\n很小的内容。", encoding="utf-8")
    # 创建临时 project.json 设定字数目标 2000
    tmp_proj = REPO / "tests" / "_tmp_proj"
    tmp_proj.mkdir(exist_ok=True)
    (tmp_proj / "project.json").write_text('{"chapterWordRange": [2000, 3000]}', encoding="utf-8")
    proc3 = subprocess.run(
        [sys.executable, str(script), str(short_dir), "--project", str(tmp_proj), "--output", str(out), "--quiet"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(REPO),
    )
    check("anti-ai-scan exit 3 on word shortage", proc3.returncode == 3,
          f"expected 3, got {proc3.returncode} stderr={proc3.stderr[:200]}")
    shutil.rmtree(short_dir, ignore_errors=True)
    shutil.rmtree(tmp_proj, ignore_errors=True)


# ---------------------------------------------------------------------------
# 3. finalize 脚本可跑通
# ---------------------------------------------------------------------------
def test_finalize_scripts_run():
    import subprocess
    scripts = SKILLS / "wq-finalize" / "scripts"
    out = REPO / "tests" / "_tmp_finalize"
    out.mkdir(exist_ok=True)
    for name in ("format-validator.py", "spell-check.py"):
        script = scripts / name
        if not script.exists():
            check(f"{name} exists", False, "missing")
            continue
        proc = subprocess.run(
            [sys.executable, str(script), str(CHAPTERS), "--output", str(out), "--quiet"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(REPO),
        )
        # 退出码 0/1 视为可跑通（2 也可能，但最小样本不应阻断）
        ok = proc.returncode in (0, 1, 2)
        check(f"{name} runs", ok, f"exit={proc.returncode} stderr={proc.stderr[:200]}")


# ---------------------------------------------------------------------------
# 4. continuity/foreshadowing 脚本在空数据上不崩
# ---------------------------------------------------------------------------
def test_continuity_scripts_dont_crash():
    import subprocess
    empty = REPO / "tests" / "_tmp_continuity"
    (empty).mkdir(exist_ok=True)
    (empty / "consistency-rules.json").write_text("{}", encoding="utf-8")
    scripts = SKILLS / "wq-review" / "scripts"
    for name in ("continuity-check.py", "foreshadowing-tracker.py"):
        script = scripts / name
        if not script.exists():
            check(f"{name} exists", False)
            continue
        proc = subprocess.run(
            [sys.executable, str(script), str(empty), "--quiet"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(REPO),
        )
        # 空数据应优雅处理，不抛未捕获异常（exit 0/1 可接受，-15/1 崩溃不可）
        crashed = proc.returncode not in (0, 1, 2)
        check(f"{name} no crash on empty", not crashed,
              f"exit={proc.returncode} stderr={proc.stderr[:200]}")


# ---------------------------------------------------------------------------
# 5. platform-export 新结构守卫（v1.4.3：md/txt 直写、无 chapters/、无 clean）
# ---------------------------------------------------------------------------
def test_platform_export_structure():
    import subprocess
    import shutil
    out = REPO / "tests" / "_tmp_export"
    if out.exists():
        shutil.rmtree(out, ignore_errors=True)
    script = SKILLS / "wq-finalize" / "scripts" / "platform-export.py"
    proc = subprocess.run(
        [sys.executable, str(script), str(CHAPTERS), "md", "--output", str(out), "--quiet"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(REPO),
    )
    check("platform-export md exit 0", proc.returncode == 0, f"exit={proc.returncode} stderr={proc.stderr[:200]}")
    md_dir = out / "md"
    # 章节文件直接在 md/ 下，文件名 第001章-XXX.md
    ch_files = [f.name for f in md_dir.glob("第*.md")] if md_dir.exists() else []
    check("chapter file named 第001章-标题.md directly in md/", len(ch_files) >= 1, f"got {ch_files}")
    # 不应再有 chapters/ 子目录
    check("no chapters/ subfolder", not (md_dir / "chapters").exists(), "chapters/ still present")
    # full.md 整文存在
    check("full.md present", (md_dir / "full.md").exists(), "missing full.md")
    # clean/ 不应再生成
    check("no clean/ folder", not (out / "clean").exists(), "clean/ still present")
    # repair 模式清理旧结构
    old_md = out / "md"
    (old_md / "chapters").mkdir(exist_ok=True)
    (old_md / "chapters" / "001.md").write_text("x", encoding="utf-8")
    (out / "clean").mkdir(exist_ok=True)
    (out / "clean" / "full.md").write_text("x", encoding="utf-8")
    proc2 = subprocess.run(
        [sys.executable, str(script), str(CHAPTERS), "repair", "--output", str(out), "--quiet"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(REPO),
    )
    check("repair exit 0", proc2.returncode == 0, f"exit={proc2.returncode}")
    check("repair removed clean/", not (out / "clean").exists(), "clean/ remained")
    check("repair removed chapters/ subfolder", not (old_md / "chapters").exists(), "chapters/ remained")
    shutil.rmtree(out, ignore_errors=True)


def main():
    print("WQ 写作技能集 · 冒烟测试")
    print("=" * 50)
    tests = [
        test_text_utils_dialogue_chinese_quotes,
        test_anti_ai_scan_runs,
        test_finalize_scripts_run,
        test_continuity_scripts_dont_crash,
        test_platform_export_structure,
    ]
    for t in tests:
        print(f"\n[{t.__name__}]")
        try:
            t()
        except Exception as e:
            global _failed
            _failed += 1
            print(f"  ERROR {t.__name__} raised {type(e).__name__}: {e}")
    print("\n" + "=" * 50)
    print(f"结果: {_passed} passed, {_failed} failed")
    # 清理临时目录
    import shutil
    for d in ("_tmp_review", "_tmp_finalize", "_tmp_continuity"):
        p = REPO / "tests" / d
        if p.exists():
            shutil.rmtree(p, ignore_errors=True)
    return 0 if _failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
