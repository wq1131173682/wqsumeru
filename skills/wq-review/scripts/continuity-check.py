#!/usr/bin/env python3
"""
wq-review 剧情一致性检查脚本
检查 consistency-rules.json 中的状态冲突

使用方法：
    python continuity-check.py <.sumeru/continuity目录> [--output <输出文件>]

输出：
    生成 continuity-report.json 包含所有发现的冲突
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any
from datetime import datetime

# 冲突检测规则
CONFLICT_RULES = {
    # 规则ID: (检测函数, 严重程度, 错误消息模板)
    "unique_location": {
        "description": "同一人物不能同时在两个地点",
        "severity": "critical",
        "check": "check_unique_location"
    },
    "destroyed_item_used": {
        "description": "已毁道具不能再次使用",
        "severity": "critical",
        "check": "check_destroyed_item_used"
    },
    "foreshadowing_recycled": {
        "description": "已标记回收的伏笔不能再次标记为active",
        "severity": "high",
        "check": "check_foreshadowing_recycled"
    },
    "character_state_regression": {
        "description": "人物状态不能无原因回退",
        "severity": "high",
        "check": "check_character_state_regression"
    },
    "power_level_consistency": {
        "description": "人物战力等级不能无原因跳跃",
        "severity": "medium",
        "check": "check_power_level_consistency"
    },
    "timeline_order": {
        "description": "事件时间线必须有序",
        "severity": "high",
        "check": "check_timeline_order"
    }
}

# 人物状态等级（用于检测回退）
CHARACTER_STATE_HIERARCHY = {
    "healthy": 0,      # 健康
    "minor_injury": 1,  # 轻伤
    "injured": 2,      # 受伤
    "seriously_injured": 3,  # 重伤
    "critical": 4,     # 危急
    "deceased": 5      # 死亡（不可逆）
}

# 战力等级（示例，可根据项目调整）
POWER_LEVEL_HIERARCHY = [
    "凡人", "武者", "大师", "宗师", "宗师巅峰",
    "元婴", "化神", "炼虚", "合体", "大乘", "渡劫"
]


def check_unique_location(data: Dict) -> List[Dict]:
    """检查同一人物不能同时在两个地点"""
    conflicts = []
    
    character_locations = data.get("character_locations", [])
    
    # 按人物分组
    locations_by_char = {}
    for item in character_locations:
        name = item.get("name")
        if name:
            if name not in locations_by_char:
                locations_by_char[name] = []
            locations_by_char[name].append(item)
    
    # 检查每个人物是否有多个不同地点
    for name, locations in locations_by_char.items():
        unique_locations = set()
        for loc in locations:
            location = loc.get("current_location")
            if location:
                unique_locations.add(location)
        
        if len(unique_locations) > 1:
            conflicts.append({
                "rule": "unique_location",
                "severity": "critical",
                "message": f"人物'{name}'同时出现在多个地点: {', '.join(unique_locations)}",
                "characters": [name],
                "locations": list(unique_locations),
                "evidence": locations
            })
    
    return conflicts


def check_destroyed_item_used(data: Dict) -> List[Dict]:
    """检查已毁道具不能再次使用"""
    conflicts = []
    
    weapons = data.get("weapons", [])
    key_items = data.get("key_items", [])
    
    # 收集已毁道具
    destroyed_items = set()
    for item in weapons:
        if item.get("status") in ["已毁", "destroyed", "broken"]:
            destroyed_items.add(item.get("item"))
    for item in key_items:
        if item.get("status") in ["已毁", "destroyed", "broken"]:
            destroyed_items.add(item.get("item"))
    
    # 检查是否有已毁道具被再次使用（通过检查所有状态）
    # 注意：这里需要结合章节正文检查，脚本只能检查规则库内部一致性
    for item in weapons:
        if item.get("item") in destroyed_items:
            # 如果已毁道具又有新的状态更新（如出现在新章节），可能是冲突
            current_chapter = item.get("current_chapter")
            destroyed_chapter = item.get("chapter_destroyed")
            if current_chapter and destroyed_chapter and current_chapter > destroyed_chapter:
                conflicts.append({
                    "rule": "destroyed_item_used",
                    "severity": "critical",
                    "message": f"已毁武器'{item.get('item')}'在第{current_chapter}章再次出现（第{destroyed_chapter}章已毁）",
                    "item": item.get("item"),
                    "destroyed_chapter": destroyed_chapter,
                    "reappeared_chapter": current_chapter,
                    "evidence": item
                })

    for item in key_items:
        if item.get("item") in destroyed_items:
            current_chapter = item.get("current_chapter")
            # key_items 没有 chapter_destroyed 字段，从 history 中推断
            destroyed_chapter = None
            for event in item.get("history", []):
                if event.get("event") in ["已毁", "destroyed", "broken", "丢失"]:
                    destroyed_chapter = event.get("chapter")
            if current_chapter and destroyed_chapter and current_chapter > destroyed_chapter:
                conflicts.append({
                    "rule": "destroyed_item_used",
                    "severity": "critical",
                    "message": f"已毁道具'{item.get('item')}'在第{current_chapter}章再次出现（第{destroyed_chapter}章已毁/丢失）",
                    "item": item.get("item"),
                    "destroyed_chapter": destroyed_chapter,
                    "reappeared_chapter": current_chapter,
                    "evidence": item
                })
    
    return conflicts


def check_foreshadowing_recycled(data: Dict) -> List[Dict]:
    """检查已标记回收的伏笔不能再次标记为active"""
    conflicts = []
    
    foreshadowing = data.get("foreshadowing", [])
    
    for fs in foreshadowing:
        status = fs.get("status")
        payoff_status = fs.get("payoff_status")
        # 已回收的伏笔：status 为 resolved/recycled，或 payoff_status 为 resolved
        is_resolved = status in ("recycled", "resolved") or payoff_status == "resolved"
        if is_resolved:
            # 检查是否有后续更新将其重新标记为active
            # 如果 resolved 的伏笔又被标记为 active，说明被重新激活
            if status == "active" and payoff_status == "resolved":
                conflicts.append({
                    "rule": "foreshadowing_recycled",
                    "severity": "high",
                    "message": f"伏笔'{fs.get('description')}'已回收但被重新激活",
                    "foreshadowing_id": fs.get("id"),
                    "evidence": fs
                })
    
    return conflicts


def check_character_state_regression(data: Dict) -> List[Dict]:
    """检查人物状态不能无原因回退"""
    conflicts = []
    
    character_state = data.get("character_state", [])
    
    # 按人物分组
    states_by_char = {}
    for item in character_state:
        name = item.get("character") or item.get("name")
        if name:
            if name not in states_by_char:
                states_by_char[name] = []
            states_by_char[name].append(item)
    
    # 按章节排序
    for name, states in states_by_char.items():
        states.sort(key=lambda x: x.get("chapter", 0))
        
        for i in range(1, len(states)):
            prev_state = states[i-1].get("status")
            curr_state = states[i].get("status")
            prev_chapter = states[i-1].get("chapter")
            curr_chapter = states[i].get("chapter")
            
            # 检查是否有状态回退
            prev_level = CHARACTER_STATE_HIERARCHY.get(prev_state, -1)
            curr_level = CHARACTER_STATE_HIERARCHY.get(curr_state, -1)
            
            # 如果当前状态比之前更健康，且没有治疗情节标记，可能是回退
            if prev_level > curr_level and curr_level >= 0:
                # 检查是否有治疗情节（healing_event 非 null/False/None）
                has_healing = states[i].get("healing_event")
                if not has_healing:
                    conflicts.append({
                        "rule": "character_state_regression",
                        "severity": "high",
                        "message": f"人物'{name}'状态从'{prev_state}'回退到'{curr_state}'（第{prev_chapter}章→第{curr_chapter}章），无治疗情节",
                        "character": name,
                        "previous_state": prev_state,
                        "current_state": curr_state,
                        "chapter_range": [prev_chapter, curr_chapter],
                        "evidence": states[i]
                    })
    
    return conflicts


def check_power_level_consistency(data: Dict) -> List[Dict]:
    """检查人物战力等级不能无原因跳跃"""
    conflicts = []
    
    character_state = data.get("character_state", [])
    
    # 按人物分组
    powers_by_char = {}
    for item in character_state:
        name = item.get("character") or item.get("name")
        power = item.get("power_level")
        if name and power:
            if name not in powers_by_char:
                powers_by_char[name] = []
            powers_by_char[name].append(item)
    
    # 检查战力跳跃
    for name, states in powers_by_char.items():
        states.sort(key=lambda x: x.get("chapter", 0))
        
        for i in range(1, len(states)):
            prev_power = states[i-1].get("power_level")
            curr_power = states[i].get("power_level")
            prev_chapter = states[i-1].get("chapter")
            curr_chapter = states[i].get("chapter")
            
            if prev_power and curr_power:
                prev_idx = POWER_LEVEL_HIERARCHY.index(prev_power) if prev_power in POWER_LEVEL_HIERARCHY else -1
                curr_idx = POWER_LEVEL_HIERARCHY.index(curr_power) if curr_power in POWER_LEVEL_HIERARCHY else -1
                
                # 如果战力跳跃超过2个等级，且没有突破情节标记
                if prev_idx >= 0 and curr_idx >= 0:
                    jump = curr_idx - prev_idx
                    if jump > 2:
                        has_breakthrough = states[i].get("breakthrough_event")
                        if not has_breakthrough:
                            conflicts.append({
                                "rule": "power_level_consistency",
                                "severity": "medium",
                                "message": f"人物'{name}'战力从'{prev_power}'跳跃到'{curr_power}'（第{prev_chapter}章→第{curr_chapter}章），无突破情节",
                                "character": name,
                                "previous_power": prev_power,
                                "current_power": curr_power,
                                "jump_level": jump,
                                "evidence": states[i]
                            })
    
    return conflicts


def check_timeline_order(data: Dict) -> List[Dict]:
    """检查事件时间线必须有序"""
    conflicts = []
    
    timeline = data.get("timeline", [])

    # 使用 sorted 避免修改原始输入数据
    sorted_timeline = sorted(timeline, key=lambda x: x.get("chapter", 0))

    for i in range(1, len(sorted_timeline)):
        prev_chapter = sorted_timeline[i-1].get("chapter")
        curr_chapter = sorted_timeline[i].get("chapter")
        prev_event = sorted_timeline[i-1].get("event")
        curr_event = sorted_timeline[i].get("event")
        
        # 检查章节号是否有序
        if prev_chapter and curr_chapter and prev_chapter > curr_chapter:
            conflicts.append({
                "rule": "timeline_order",
                "severity": "high",
                "message": f"时间线事件顺序错误：第{prev_chapter}章事件在第{curr_chapter}章事件之后",
                "events": [prev_event, curr_event],
                "chapters": [prev_chapter, curr_chapter],
                "evidence": [sorted_timeline[i-1], sorted_timeline[i]]
            })
    
    return conflicts


def run_all_checks(data: Dict) -> Dict:
    """运行所有冲突检测"""
    all_conflicts = []
    
    for rule_id, rule_info in CONFLICT_RULES.items():
        check_func_name = rule_info["check"]
        if check_func_name in globals():
            check_func = globals()[check_func_name]
            try:
                conflicts = check_func(data)
                for conflict in conflicts:
                    conflict["rule_id"] = rule_id
                    conflict["rule_description"] = rule_info["description"]
                all_conflicts.extend(conflicts)
            except Exception as e:
                all_conflicts.append({
                    "rule_id": rule_id,
                    "severity": "error",
                    "message": f"检查规则'{rule_id}'执行失败: {str(e)}",
                    "evidence": None
                })
    
    # 统计
    severity_counts = {}
    for conflict in all_conflicts:
        severity = conflict.get("severity", "unknown")
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    return {
        "total_conflicts": len(all_conflicts),
        "severity_counts": severity_counts,
        "conflicts": all_conflicts,
        "rules_checked": list(CONFLICT_RULES.keys()),
        "checked_at": datetime.now().isoformat()
    }


def normalize_rules(data: Dict) -> Dict:
    """把两套并存的 consistency-rules.json 结构归一化。

    背景：仓库里存在两种互不兼容的写法，且都有文档依据——
      A. wq-rules/SKILL.md §consistency-rules.json 格式（对象式）：
         characters{name:{status,location}} / items{} / foreshadowing{} / timeline{...}
      B. scripts/consistency-rules-template.json（数组式）：
         character_locations[] / weapons[] / key_items[] / character_state[] /
         foreshadowing[] / timeline[]

    此前脚本只认 B，导致按 A 书写的数据：
      - timeline 是 dict，被 sorted() 遍历出字符串键 → 'str' object has no attribute 'get' 崩溃
      - characters 是 dict，而检查器读 character_locations 数组 → 真正的 critical 冲突全部漏检
    这里统一转成 B 的内部形态，使两种写法都能被正确检查。
    """
    if not isinstance(data, dict):
        return data
    out = dict(data)

    # --- characters(对象) → character_locations(数组) ---
    chars = out.get("characters")
    if isinstance(chars, dict) and not out.get("character_locations"):
        locs = []
        for name, info in chars.items():
            if not isinstance(info, dict):
                continue
            loc = info.get("location")
            if loc:
                locs.append({
                    "name": name,
                    "current_location": loc,
                    "since_chapter": info.get("since_chapter"),
                    "previous_locations": info.get("previous_locations", []),
                })
        if locs:
            out["character_locations"] = locs

    # --- items(对象) → weapons/key_items(数组) ---
    items = out.get("items")
    if isinstance(items, dict):
        weapons = list(out.get("weapons") or [])
        key_items = list(out.get("key_items") or [])
        destroyed_marks = ("destroyed", "已毁", "broken", "lost", "丢失")
        for name, status in items.items():
            entry = {"item": name, "status": status, "current_chapter": None, "holder": None}
            if isinstance(status, str) and status in destroyed_marks:
                entry["destroyed_detail"] = status
            weapons.append(entry)
            key_items.append(entry)
        if not out.get("weapons"):
            out["weapons"] = weapons
        if not out.get("key_items"):
            out["key_items"] = key_items

    # --- foreshadowing(对象) → 数组 ---
    fs = out.get("foreshadowing")
    if isinstance(fs, dict):
        arr = []
        for fid, info in fs.items():
            if isinstance(info, dict):
                item = {"id": fid}
                item.update(info)
                item.setdefault("status", "active")
                item.setdefault("payoff_status", "pending")
                arr.append(item)
            else:
                arr.append({"id": fid, "status": str(info), "payoff_status": "pending"})
        out["foreshadowing"] = arr

    # --- timeline(对象) → 数组 ---
    tl = out.get("timeline")
    if isinstance(tl, dict):
        # 对象式 timeline 只承载"当前位置/当前章"，没有事件序列；
        # 转成单元素数组，避免 sorted(dict) 遍历出字符串键导致崩溃。
        out["timeline"] = [{
            "chapter": tl.get("current_chapter", 0),
            "event": tl.get("current_location", ""),
            "location": tl.get("current_location", ""),
            "characters": [],
        }]

    return out


def scan_continuity(continuity_dir: str) -> Dict:
    """扫描continuity目录中的规则文件"""
    continuity_path = Path(continuity_dir)
    
    if not continuity_path.exists():
        return {"error": f"目录不存在: {continuity_dir}"}
    
    # 读取 consistency-rules.json
    rules_file = continuity_path / "consistency-rules.json"
    
    if not rules_file.exists():
        return {"error": f"文件不存在: {rules_file}"}
    
    try:
        with open(rules_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        return {"error": f"读取文件失败: {str(e)}"}
    
    # 运行检查（先归一化，兼容对象式/数组式两套 schema）
    result = run_all_checks(normalize_rules(data))
    result["rules_file"] = str(rules_file)
    
    return result


def main() -> int:
    """退出码：0=无冲突 1=有 medium/low 2=有 critical/high 3=输入错误或规则执行失败。"""
    parser = argparse.ArgumentParser(
        description="wq-review 剧情一致性检查（读取 consistency-rules.json）")
    parser.add_argument(
        "continuity_dir", nargs="?", default=None,
        help=".sumeru/continuity 目录（分卷模式传 .sumeru/volumes/vol-N/continuity）")
    parser.add_argument(
        "--continuity-dir", dest="continuity_dir_opt", default=None,
        help="同上（别名，供分卷模式显式指定；若给出则优先于位置参数）")
    parser.add_argument(
        "--chapters", default=None,
        help="（兼容参数）本次修订涉及的章节号，逗号分隔；仅用于报告标注，"
             "一致性校验始终覆盖全量 consistency-rules.json")
    parser.add_argument("--output", default=None, help="报告输出文件（JSON）")
    parser.add_argument("--quiet", action="store_true", help="静默模式：只输出问题摘要")
    args = parser.parse_args()

    # 兼容两种写法：位置参数 或 --continuity-dir（后者优先）
    continuity_dir = args.continuity_dir_opt or args.continuity_dir
    if not continuity_dir:
        parser.error("必须给出 continuity 目录（位置参数或 --continuity-dir）")
    output_file = args.output
    quiet = args.quiet
    
    # 扫描
    if not quiet:
        print(f"正在检查剧情一致性: {continuity_dir}")
    result = scan_continuity(continuity_dir)
    
    # 输入错误必须显式失败：此前静默返回 0，父Agent会误判为"检查通过"
    if "error" in result:
        print(f"❌ 错误: {result['error']}")
        return 3

    counts = result.get("severity_counts", {})
    critical = counts.get("critical", 0)
    high = counts.get("high", 0)
    medium = counts.get("medium", 0)
    low = counts.get("low", 0)
    # 规则自身崩溃（多为 consistency-rules.json 结构与脚本不符）也视为失败
    rule_errors = counts.get("error", 0)

    # 输出
    if output_file:
        out_path = Path(output_file)
        if out_path.parent and not out_path.parent.exists():
            out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        if not quiet:
            print(f"一致性报告已保存到: {output_file}")

    if not quiet:
        print("\n" + "="*60)
        print("剧情一致性检查结果")
        print("="*60)
        print(f"检查规则数: {len(result.get('rules_checked', []))}")
        print(f"发现冲突总数: {result.get('total_conflicts', 0)}")

        if counts:
            print(f"\n冲突严重程度统计:")
            for severity in ['critical', 'high', 'medium', 'low', 'error']:
                if severity in counts:
                    print(f"  {severity}: {counts[severity]}")

        if result.get('conflicts'):
            print("\n冲突详情:")
            for i, conflict in enumerate(result['conflicts'][:10]):
                print(f"\n  [{i+1}] [{conflict.get('severity', 'unknown').upper()}] {conflict.get('rule_id')}")
                print(f"      {conflict.get('message', '')}")
    elif result.get('total_conflicts', 0) > 0:
        if critical > 0:
            print(f"🚨 发现 {critical} 个严重冲突，需立即处理")
        if high > 0:
            print(f"⚠️ 发现 {high} 个高优先级问题")

    if rule_errors > 0:
        print(f"❌ {rule_errors} 个检查规则执行失败（consistency-rules.json 结构可能不符）")
        return 3
    if critical or high:
        return 2
    if medium or low:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
