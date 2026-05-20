#!/usr/bin/env python3
"""
sumeru-finalize 敏感词检测脚本
对小说章节进行三级敏感内容检测

使用方法：
    python sensitive-word-filter.py <章节目录> [--output <输出文件>] [--level <1|2|3>]

输出：
    生成 error-report.json 包含所有发现的敏感内容
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List

# 敏感词库（三级分类）
# 注意：实际使用时应根据项目需求扩展和更新词库

SENSITIVE_WORDS = {
    # 一级敏感（必须修改）- 违反法律法规、政治敏感、色情淫秽、暴力恐怖等
    "level1": [
        # 政治敏感
        "分裂国家", "颠覆国家", "反动", "反革命",
        # 色情淫秽
        "淫秽", "色情", "裸体", "性交", "性器官",
        # 暴力恐怖
        "恐怖主义", "极端主义", "自杀", "自焚",
        # 毒品
        "毒品", "贩毒", "吸毒", "海洛因", "冰毒", "大麻",
        # 赌博
        "赌博", "赌钱", "赌场",
    ],
    
    # 二级敏感（建议修改）- 血腥暴力、低俗、医疗等
    "level2": [
        # 血腥暴力
        "血腥", "残杀", "肢解", "碎尸", "虐杀",
        # 低俗用语
        "傻逼", "屌丝", "绿茶婊", "脑残",
        # 医疗（可能引起不适）
        "手术台", "解剖", "尸检",
        # 未成年人不当内容
        "未成年", "幼女", "萝莉",
    ],
    
    # 三级敏感（优化建议）- 网络用语、争议话题等
    "level3": [
        # 网络热梗（过度使用影响阅读）
        "yyds", "绝绝子", "破防", "emo",
        # 争议话题
        "女权", "男权", "性别对立",
        # 重复冗余
        "真的真的", "非常非常", "特别特别",
    ],
}

# 需要上下文判断的敏感词（待定项）
CONTEXT_SENSITIVE_WORDS = [
    "杀人", "死亡", "尸体", "血", "刀", "枪",
    "打", "杀", "死", "亡",
    "爱情", "恋爱", "亲密",
    "权力", "政治", "政府",
]


def detect_sensitive_words(text: str, chapter_id: str, level: int = 3) -> List[Dict]:
    """检测文本中的敏感词"""
    findings = []
    
    # 检测各级敏感词
    for lvl in range(1, level + 1):
        key = f"level{lvl}"
        if key not in SENSITIVE_WORDS:
            continue
            
        for word in SENSITIVE_WORDS[key]:
            # 使用正则匹配，支持部分匹配
            pattern = re.compile(re.escape(word), re.IGNORECASE)
            for match in pattern.finditer(text):
                start = max(0, match.start() - 30)
                end = min(len(text), match.end() + 30)
                context = text[start:end]
                
                findings.append({
                    "chapter": chapter_id,
                    "type": "sensitive_word",
                    "severity": "high" if lvl == 1 else ("medium" if lvl == 2 else "low"),
                    "level": lvl,
                    "position": match.start(),
                    "word": word,
                    "context": context,
                    "action": "必须修改" if lvl == 1 else ("建议修改" if lvl == 2 else "优化建议"),
                    "requires_context_check": False
                })
    
    # 标记需要上下文判断的词
    for word in CONTEXT_SENSITIVE_WORDS:
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        for match in pattern.finditer(text):
            start = max(0, match.start() - 30)
            end = min(len(text), match.end() + 30)
            context = text[start:end]
            
            findings.append({
                "chapter": chapter_id,
                "type": "sensitive_word",
                "severity": "pending",
                "level": 0,
                "position": match.start(),
                "word": word,
                "context": context,
                "action": "需要上下文判断",
                "requires_context_check": True
            })
    
    return findings


def scan_chapters(chapters_dir: str, level: int = 3) -> Dict:
    """扫描章节目录中的所有文件"""
    all_findings = []
    chapters_scanned = 0
    
    chapters_path = Path(chapters_dir)
    if not chapters_path.exists():
        return {"error": f"目录不存在: {chapters_dir}", "chapters_scanned": 0}
    
    for file_path in chapters_path.glob("**/*.md"):
        chapters_scanned += 1
        chapter_id = file_path.stem
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            findings = detect_sensitive_words(text, chapter_id, level)
            all_findings.extend(findings)
            
        except Exception as e:
            all_findings.append({
                "chapter": chapter_id,
                "type": "read_error",
                "severity": "high",
                "error": str(e),
                "requires_context_check": False
            })
    
    # 统计
    stats = {
        "level1": len([f for f in all_findings if f.get("level") == 1]),
        "level2": len([f for f in all_findings if f.get("level") == 2]),
        "level3": len([f for f in all_findings if f.get("level") == 3]),
        "pending": len([f for f in all_findings if f.get("requires_context_check")]),
    }
    
    # 分离待定项（需要子Agent处理）
    pending_items = [f for f in all_findings if f.get("requires_context_check")]
    
    return {
        "chapters_scanned": chapters_scanned,
        "total_findings": len(all_findings),
        "stats": stats,
        "findings": all_findings,
        "pending_items": pending_items[:20],  # 最多返回20个待定项
        "pending_count": len(pending_items)
    }


def main():
    if len(sys.argv) < 2:
        print("用法: python sensitive-word-filter.py <章节目录> [--output <输出文件>] [--level <1|2|3>] [--quiet]")
        print("\n示例:")
        print("  python sensitive-word-filter.py chapters/")
        print("  python sensitive-word-filter.py chapters/ --level 2")
        print("  python sensitive-word-filter.py chapters/ --quiet")
        sys.exit(1)
    
    chapters_dir = sys.argv[1]
    output_file = None
    level = 3
    quiet = "--quiet" in sys.argv
    
    # 解析参数
    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_file = sys.argv[idx + 1]
    
    if "--level" in sys.argv:
        idx = sys.argv.index("--level")
        if idx + 1 < len(sys.argv):
            try:
                level = int(sys.argv[idx + 1])
                level = max(1, min(3, level))
            except ValueError:
                pass
    
    # 扫描
    if not quiet:
        print(f"正在扫描章节目录: {chapters_dir} (检测级别: {level})")
    result = scan_chapters(chapters_dir, level)
    
    # 输出
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        if not quiet:
            print(f"检测报告已保存到: {output_file}")
    elif not quiet:
        print("\n" + "="*60)
        print("敏感词检测结果")
        print("="*60)
        print(f"扫描章节数: {result.get('chapters_scanned', 0)}")
        print(f"发现敏感内容总数: {result.get('total_findings', 0)}")
        
        if 'stats' in result:
            stats = result['stats']
            print(f"\n敏感级别统计:")
            print(f"  一级（必须修改）: {stats.get('level1', 0)}")
            print(f"  二级（建议修改）: {stats.get('level2', 0)}")
            print(f"  三级（优化建议）: {stats.get('level3', 0)}")
            print(f"  待定项（需上下文判断）: {stats.get('pending', 0)}")
        
        if result.get('findings'):
            print("\n前10个发现示例:")
            for i, finding in enumerate(result['findings'][:10]):
                severity = finding.get('severity', 'unknown')
                word = finding.get('word', '')
                action = finding.get('action', '')
                print(f"\n  [{i+1}] {finding.get('chapter')} - {severity} - '{word}'")
                print(f"      处理建议: {action}")
    
    # 静默模式：只输出有问题的提醒
    elif quiet and result.get('total_findings', 0) > 0:
        stats = result.get('stats', {})
        level1 = stats.get('level1', 0)
        level2 = stats.get('level2', 0)
        if level1 > 0:
            print(f"🚨 发现 {level1} 个一级敏感内容，必须修改")
        if level2 > 0:
            print(f"⚠️ 发现 {level2} 个二级敏感内容，建议修改")
    
    return result


if __name__ == "__main__":
    main()
