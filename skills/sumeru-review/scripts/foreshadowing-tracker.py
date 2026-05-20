#!/usr/bin/env python3
"""
sumeru-review 伏笔追踪脚本
追踪伏笔的设置、推进、回收状态

使用方法：
    python foreshadowing-tracker.py <.sumeru/continuity目录> [--output <输出文件>]

输出：
    生成 foreshadowing-report.json 包含伏笔状态报告
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List
from datetime import datetime


def analyze_foreshadowing(data: Dict, current_chapter: int = 0) -> Dict:
    """分析伏笔状态"""
    foreshadowing = data.get("foreshadowing", [])
    
    if not foreshadowing:
        return {
            "total": 0,
            "active": 0,
            "pending": 0,
            "recycled": 0,
            "overdue": [],
            "foreshadowing": []
        }
    
    # 分类统计
    active = []
    pending = []
    recycled = []
    overdue = []
    
    for fs in foreshadowing:
        status = fs.get("status", "active")
        fs_id = fs.get("id", "unknown")
        description = fs.get("description", "")
        first_appeared = fs.get("first_appeared", 0)
        expected_payoff = fs.get("expected_payoff_chapter", 0)
        importance = fs.get("importance", "medium")
        
        fs_info = {
            "id": fs_id,
            "description": description,
            "status": status,
            "first_appeared": first_appeared,
            "expected_payoff_chapter": expected_payoff,
            "importance": importance,
            "chapters_referenced": fs.get("related_chapters", []),
            "chapter_gap": current_chapter - first_appeared if current_chapter > 0 else 0
        }
        
        if status == "active":
            active.append(fs_info)
            # 检查是否 overdue
            if expected_payoff > 0 and current_chapter > expected_payoff:
                overdue.append({
                    **fs_info,
                    "overdue_chapters": current_chapter - expected_payoff
                })
        elif status == "pending":
            pending.append(fs_info)
        elif status in ["recycled", "resolved"]:
            recycled.append(fs_info)
    
    # 按重要性排序
    importance_order = {"high": 0, "medium": 1, "low": 2}
    active.sort(key=lambda x: importance_order.get(x["importance"], 1))
    overdue.sort(key=lambda x: importance_order.get(x["importance"], 1))
    
    return {
        "total": len(foreshadowing),
        "active": len(active),
        "pending": len(pending),
        "recycled": len(recycled),
        "overdue_count": len(overdue),
        "overdue": overdue,
        "active_list": active,
        "pending_list": pending,
        "recycled_list": recycled,
        "recommendations": generate_recommendations(active, overdue, current_chapter)
    }


def generate_recommendations(active: List, overdue: List, current_chapter: int) -> List[str]:
    """生成伏笔管理建议"""
    recommendations = []
    
    #  overdue 伏笔提醒
    if overdue:
        high_priority = [fs for fs in overdue if fs.get("importance") == "high"]
        if high_priority:
            recommendations.append(f"⚠️ 紧急：{len(high_priority)}个高优先级伏笔已过期，建议尽快回收")
            for fs in high_priority[:3]:
                recommendations.append(f"   - {fs['description']}（期望回收：第{fs['expected_payoff_chapter']}章，已过期{fs['overdue_chapters']}章）")
    
    # 活跃伏笔过多提醒
    if len(active) > 10:
        recommendations.append(f"📌 注意：当前有{len(active)}个活跃伏笔，建议适当回收部分低优先级伏笔")
    
    # 新伏笔建议
    if len(active) > 0:
        recent_active = [fs for fs in active if fs.get("chapter_gap", 0) < 5]
        if len(recent_active) > 3:
            recommendations.append(f"💡 建议：近期设置了{len(recent_active)}个新伏笔，可在第{current_chapter + 10}章左右安排回收")
    
    if not recommendations:
        recommendations.append("✅ 伏笔管理状态良好")
    
    return recommendations


def scan_foreshadowing(continuity_dir: str, current_chapter: int = 0) -> Dict:
    """扫描伏笔数据"""
    continuity_path = Path(continuity_dir)
    
    if not continuity_path.exists():
        return {"error": f"目录不存在: {continuity_dir}"}
    
    rules_file = continuity_path / "consistency-rules.json"
    
    if not rules_file.exists():
        return {"error": f"文件不存在: {rules_file}"}
    
    try:
        with open(rules_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        return {"error": f"读取文件失败: {str(e)}"}
    
    result = analyze_foreshadowing(data, current_chapter)
    result["rules_file"] = str(rules_file)
    result["current_chapter"] = current_chapter
    result["analyzed_at"] = datetime.now().isoformat()
    
    return result


def main():
    if len(sys.argv) < 2:
        print("用法: python foreshadowing-tracker.py <.sumeru/continuity目录> [当前章节号] [--output <输出文件>]")
        print("\n示例:")
        print("  python foreshadowing-tracker.py .sumeru/continuity 50")
        print("  python foreshadowing-tracker.py .sumeru/continuity --output foreshadowing-report.json")
        sys.exit(1)
    
    continuity_dir = sys.argv[1]
    current_chapter = 0
    output_file = None
    
    # 解析参数
    for i, arg in enumerate(sys.argv):
        if arg == "--output" and i + 1 < len(sys.argv):
            output_file = sys.argv[i + 1]
        elif arg.isdigit() and current_chapter == 0:
            current_chapter = int(arg)
    
    # 扫描
    print(f"正在追踪伏笔状态: {continuity_dir} (当前章节: {current_chapter})")
    result = scan_foreshadowing(continuity_dir, current_chapter)
    
    # 输出
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"伏笔报告已保存到: {output_file}")
    else:
        print("\n" + "="*60)
        print("伏笔追踪报告")
        print("="*60)
        
        if "error" in result:
            print(f"错误: {result['error']}")
            return
        
        print(f"伏笔总数: {result.get('total', 0)}")
        print(f"  活跃: {result.get('active', 0)}")
        print(f"  待回收: {result.get('pending', 0)}")
        print(f"  已回收: {result.get('recycled', 0)}")
        
        if result.get('overdue_count', 0) > 0:
            print(f"\n⚠️ 过期伏笔: {result['overdue_count']}个")
            for fs in result.get('overdue', [])[:5]:
                print(f"   - [{fs.get('importance', 'unknown').upper()}] {fs.get('description')}")
                print(f"     期望回收: 第{fs.get('expected_payoff_chapter', 'N/A')}章，已过期{fs.get('overdue_chapters', 0)}章")
        
        print("\n管理建议:")
        for rec in result.get('recommendations', []):
            print(f"  {rec}")
    
    return result


if __name__ == "__main__":
    main()
