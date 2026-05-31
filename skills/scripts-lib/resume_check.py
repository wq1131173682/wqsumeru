#!/usr/bin/env python3
"""须弥写作 断点续写检查脚本
扫描 chapters/ 下所有文件的 SUMERU_STATUS，生成恢复报告。

用法：
    python resume_check.py <chapters目录> [--output <报告.json>] [--quiet]

返回：
    JSON 报告含：每章状态、按状态分布、缺失章节、未完成批次
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from sumeru_utils import parse_args, find_project_root, scan_status_markers, write_json


def format_status_line(status: str) -> str:
    icons = {"drafted": "✏️", "polished": "✨", "reviewed": "🔍",
             "fixed": "🔧", "finalized": "✅", "exported": "📦", "planned": "📋"}
    return icons.get(status, "❓")


def main():
    args, flags, quiet = parse_args(
        "python resume_check.py <chapters目录> [--output <报告.json>] [--quiet]", 1)
    chapters_dir = args[0]
    output = flags.get("--output")

    result = scan_status_markers(chapters_dir)

    if output:
        write_json(result, output)
        if not quiet:
            print(f"恢复报告已保存: {output}")

    if result.get("incomplete_batches"):
        for batch, info in result["incomplete_batches"].items():
            missing = info["missing"]
            completed = info["completed"]
            print(f"⚠️  批次 {batch} 未完成: 已完成 {len(completed)} 章, 缺失 {len(missing)} 章 → {missing}")
    else:
        print("✅ 所有批次完整")

    if result.get("chapters"):
        statuses = result["by_status"]
        total = result["total"]
        summary = ", ".join(f"{icon} {s}: {n}" for s, n in sorted(statuses.items())
                           if (icon := format_status_line(s)))
        print(f"📊 共 {total} 章: {summary}")

        # 检查状态链连续性
        order = ["planned", "drafted", "reviewed", "fixed", "polished", "finalized", "exported"]
        max_status = max(
            (order.index(ch["status"]) for ch in result["chapters"] if ch["status"] in order),
            default=-1
        )
        if max_status >= 0:
            current_phase = order[max_status]
            print(f"📍 当前阶段: {current_phase}")

            # 列出最后未完成的章节
            unfinished = [ch for ch in result["chapters"]
                         if order.index(ch["status"]) if ch["status"] in order < max_status]
            if unfinished:
                print(f"⏸️  可续写章节: {[ch['chapter'] for ch in unfinished]}")

    if not output:
        import json
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
