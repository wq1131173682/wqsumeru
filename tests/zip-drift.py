r"""发布产物漂移检查：wqskills.zip 与仓库源码是否一致。

wqskills.zip 是分发给用户的安装包；若它与源码不一致，
用户拿到的是旧版本。
"""
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZIP = ROOT / "wqskills.zip"

zf = zipfile.ZipFile(ZIP)
infos = zf.infolist()
names = [i.filename.replace("\\", "/") for i in infos]

print(f"zip = {ZIP.name}")
print(f"entries = {len(names)}")
print(f"zip mtime = {max(i.date_time for i in infos) if infos else '-'}")

pyc = [n for n in names if "__pycache__" in n or n.endswith(".pyc")]
print(f"__pycache__/.pyc entries in zip = {len(pyc)}")
if pyc[:5]:
    for n in pyc[:5]:
        print(f"   {n}")

print()
print("=== SKILL.md: disk vs zip ===")
hdr = f"{'file':34s} {'disk_lines':>10s} {'zip_lines':>9s} {'IDENTICAL':>9s}"
print(hdr)
print("-" * len(hdr))

stale = []
missing = []
for disk in sorted((ROOT / "skills").rglob("SKILL.md")):
    rel = disk.relative_to(ROOT).as_posix()
    dtext = disk.read_bytes().replace(b"\r\n", b"\n")
    dlines = dtext.count(b"\n") + 1
    hit = [n for n in names if n == rel or n.endswith(rel)]
    if not hit:
        missing.append(rel)
        print(f"{rel:34s} {dlines:10d} {'-':>9s} {'MISSING':>9s}")
        continue
    ztext = zf.read(hit[0]).replace(b"\r\n", b"\n")
    zlines = ztext.count(b"\n") + 1
    same = "YES" if ztext == dtext else "NO"
    if same == "NO":
        stale.append((rel, dlines, zlines, zlines - dlines))
    print(f"{rel:34s} {dlines:10d} {zlines:9d} {same:>9s}")

print()
print("=== 汇总 ===")
print(f"disk 有、zip 无: {len(missing)}")
for m in missing:
    print(f"   MISSING {m}")
print(f"内容不一致(STALE): {len(stale)}")
for rel, dl, zl, delta in stale:
    print(f"   STALE {rel}: disk={dl} zip={zl} delta={delta:+d}")

# 全量文件对比（不只 SKILL.md）
print()
print("=== 全量文件对比 ===")
disk_files = {
    p.relative_to(ROOT).as_posix()
    for p in (ROOT / "skills").rglob("*")
    if p.is_file() and "__pycache__" not in p.parts
}
zip_files = {n for n in names if not n.endswith("/")}
only_disk = sorted(disk_files - zip_files)
only_zip = sorted(zip_files - disk_files)
print(f"disk-only: {len(only_disk)}")
for f in only_disk[:20]:
    print(f"   + {f}")
print(f"zip-only: {len(only_zip)}")
for f in only_zip[:20]:
    print(f"   - {f}")

diff_content = []
for rel in sorted(disk_files & zip_files):
    db = (ROOT / rel).read_bytes().replace(b"\r\n", b"\n")
    zb = zf.read(rel).replace(b"\r\n", b"\n") if rel in names else None
    if zb is not None and zb != db:
        diff_content.append(rel)
print(f"同名但内容不同: {len(diff_content)}")
for f in diff_content[:25]:
    print(f"   ~ {f}")
zf.close()
