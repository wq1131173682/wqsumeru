r"""核查代码围栏奇偶，并定位未闭合围栏的位置。"""
import io
import glob

FENCE = "`" * 3

for f in sorted(glob.glob("skills/**/*.md", recursive=True)):
    lines = io.open(f, encoding="utf-8").read().split("\n")
    idx = [i for i, l in enumerate(lines, 1) if l.lstrip().startswith(FENCE)]
    if len(idx) % 2:
        print(f"ODD({len(idx)}): {f}")
        # 打印最后一个围栏附近，帮助定位未闭合处
        last = idx[-1]
        print(f"   最后一个围栏在 L{last}: {lines[last-1].strip()[:70]!r}")
        # 简单配对推断：逐对标记
        open_at = None
        for i in idx:
            if open_at is None:
                open_at = i
            else:
                open_at = None
        if open_at is not None:
            print(f"   => 疑似未闭合的开启围栏在 L{open_at}: {lines[open_at-1].strip()[:70]!r}")
        print()
print("扫描完成")
