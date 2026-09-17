r"""核对章节任务卡「格式块字段数」与「必填校验清单字段数」是否一致。"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
p = ROOT / "skills/wq-outline/SKILL.md"
t = p.read_text(encoding="utf-8")
lines = t.split("\n")

# 取 L53 之后的第一个 json 代码块
start = None
for i, ln in enumerate(lines):
    if ln.strip().startswith("```json") and i > 50:
        start = i
        break
end = None
for j in range(start + 1, len(lines)):
    if lines[j].strip().startswith("```"):
        end = j
        break

block = "\n".join(lines[start + 1:end])
schema_keys = re.findall(r'^\s*"([A-Za-z_]+)"\s*:', block, re.M)
optional = [k for k in schema_keys
            if re.search(rf'"{k}"\s*:.*可选', block)]

print(f"schema block: L{start+1}-L{end+1}")
print(f"SCHEMA_KEYS_COUNT = {len(schema_keys)}")
for i, k in enumerate(schema_keys, 1):
    mark = "  (标注可选)" if k in optional else ""
    print(f"  {i:2d}. {k}{mark}")

# 必填清单行
req_line = next((ln for ln in lines if "个必填字段" in ln), None)
req = re.findall(r"`([a-zA-Z_]+)`", req_line) if req_line else []
print()
print(f"REQUIRED_LIST_COUNT = {len(req)}")
print(f"REQUIRED = {req}")

print()
only_schema = [k for k in schema_keys if k not in req]
only_req = [k for k in req if k not in schema_keys]
print(f"仅在 schema、不在必填清单（{len(only_schema)}）: {only_schema}")
print(f"  其中已标注可选: {[k for k in only_schema if k in optional]}")
print(f"  其中未标注可选: {[k for k in only_schema if k not in optional]}")
print(f"仅在必填清单、不在 schema（{len(only_req)}）: {only_req}")
