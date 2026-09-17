r"""冒烟测试：确认每个技能脚本能被 Python 解析并响应 --help。

这也顺带暴露「SKILL.md 里写了却跑不起来」的脚本。
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
scripts = sorted((ROOT / "skills").rglob("scripts/*.py"))

print(f"found {len(scripts)} scripts under skills/**/scripts\n")
bad = []
for s in scripts:
    rel = s.relative_to(ROOT).as_posix()
    try:
        r = subprocess.run(
            [sys.executable, "-X", "utf8", str(s), "--help"],
            capture_output=True, timeout=60,
        )
        err = r.stderr.decode("utf-8", errors="replace")
        out = r.stdout.decode("utf-8", errors="replace")
        if r.returncode == 0:
            status = "OK"
        else:
            status = f"RC={r.returncode}"
            first_err = next((l for l in err.splitlines() if l.strip()), "")
            bad.append((rel, r.returncode, first_err))
    except subprocess.TimeoutExpired:
        status = "TIMEOUT"
        bad.append((rel, "TIMEOUT", ""))
        out = ""
    nlines = len(out.splitlines())
    print(f"{status:10s} {rel:52s} help_lines={nlines}")

print()
if bad:
    print("=== FAILURES ===")
    for rel, rc, e in bad:
        print(f"  {rel}\n      rc={rc}  err={e[:200]}")
else:
    print("所有脚本均可解析并响应 --help")
