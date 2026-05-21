#!/usr/bin/env python3
"""
sumeru-finalize 敏感词检测脚本
对小说章节进行三级敏感内容检测

使用方法：
    python sensitive-word-filter.py <章节目录> [--output <输出文件>] [--level <1|2|3>] [--custom <自定义词库>]

词库来源：
    1. 默认加载 skills/sumeru-finalize/sensitive-words.json
    2. 可通过 --custom 参数指定自定义词库文件
    3. 用户可在 sensitive-words.json 的 "custom" 字段中添加自定义词

输出：
    生成 error-report.json 包含所有发现的敏感内容
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Any

# 默认词库路径
DEFAULT_WORDLIB_PATH = Path(__file__).parent / "sensitive-words.json"


def load_wordlib(custom_path: str = None) -> Dict[str, Any]:
    """加载敏感词库"""
    wordlib_path = custom_path if custom_path else str(DEFAULT_WORDLIB_PATH)
    
    if not os.path.exists(wordlib_path):
        print(f"⚠️ 词库文件不存在: {wordlib_path}，使用内置默认词库")
        return get_default_wordlib()
    
    try:
        with open(wordlib_path, 'r', encoding='utf-8') as f:
            wordlib = json.load(f)
        
        # 合并自定义词
        if "custom" in wordlib:
            for level in ["level1", "level2", "level3"]:
                if level in wordlib.get("custom", {}):
                    custom_words = wordlib["custom"][level]
                    if level in wordlib:
                        wordlib[level]["categories"]["custom"] = custom_words
        
        return wordlib
    except json.JSONDecodeError as e:
        print(f"⚠️ 词库文件JSON解析失败: {e}，使用内置默认词库")
        return get_default_wordlib()


def get_default_wordlib() -> Dict[str, Any]:
    """内置默认词库（降级方案）"""
    return {
        "level1": {
            "categories": {
                "political": ["分裂国家", "颠覆国家", "反动", "反革命"],
                "pornographic": ["淫秽", "色情", "裸体", "性交", "性器官"],
                "violence_terror": ["恐怖主义", "极端主义", "自杀", "自焚"],
                "drugs": ["毒品", "贩毒", "吸毒", "海洛因", "冰毒", "大麻"],
                "gambling": ["赌博", "赌钱", "赌场"],
            }
        },
        "level2": {
            "categories": {
                "gore": ["血腥", "残杀", "肢解", "碎尸", "虐杀"],
                "vulgar": ["傻逼", "屌丝", "绿茶婊", "脑残"],
                "medical": ["手术台", "解剖", "尸检"],
                "minors": ["未成年", "幼女", "萝莉"],
            }
        },
        "level3": {
            "categories": {
                "internet_slang": ["yyds", "绝绝子", "破防", "emo"],
                "controversial": ["女权", "男权", "性别对立"],
                "redundancy": ["真的真的", "非常非常", "特别特别"],
            }
        },
        "context_sensitive": {
            "words": ["杀人灭口", "血腥场面", "尸体遍地", "血流成河", "自杀身亡", "性暗示"]
        }
    }


def detect_sensitive_words(text: str, chapter_id: str, wordlib: Dict, level: int = 3) -> List[Dict]:
    """检测文本中的敏感词"""
    findings = []
    
    # 检测各级敏感词
    for lvl in range(1, level + 1):
        key = f"level{lvl}"
        if key not in wordlib:
            continue
        
        categories = wordlib[key].get("categories", {})
        action = wordlib[key].get("action", "建议修改")
        
        for category, words in categories.items():
            for word in words:
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
                        "category": category,
                        "position": match.start(),
                        "word": word,
                        "context": context,
                        "action": action,
                        "requires_context_check": False
                    })
    
    # 标记需要上下文判断的词
    context_words = wordlib.get("context_sensitive", {}).get("words", [])
    for word in context_words:
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


def scan_chapters(chapters_dir: str, wordlib: Dict, level: int = 3) -> Dict:
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
            
            findings = detect_sensitive_words(text, chapter_id, wordlib, level)
            all_findings.extend(findings)
        except Exception as e:
            all_findings.append({
                "chapter": chapter_id,
                "type": "read_error",
                "severity": "high",
                "error": str(e),
                "requires_context_check": False
            })
    
    for file_path in chapters_path.glob("**/*.txt"):
        chapters_scanned += 1
        chapter_id = file_path.stem
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            findings = detect_sensitive_words(text, chapter_id, wordlib, level)
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
    
    # 分离待定项
    pending_items = [f for f in all_findings if f.get("requires_context_check")]
    
    return {
        "chapters_scanned": chapters_scanned,
        "total_findings": len(all_findings),
        "stats": stats,
        "findings": all_findings,
        "pending_items": pending_items[:20],
        "pending_count": len(pending_items),
        "wordlib_version": wordlib.get("version", "unknown")
    }


def main():
    if len(sys.argv) < 2:
        print("用法: python sensitive-word-filter.py <章节目录> [--output <输出文件>] [--level <1|2|3>] [--custom <词库路径>] [--quiet]")
        print("\n示例:")
        print("  python sensitive-word-filter.py chapters/")
        print("  python sensitive-word-filter.py chapters/ --level 2")
        print("  python sensitive-word-filter.py chapters/ --custom my-words.json")
        print("  python sensitive-word-filter.py chapters/ --quiet")
        sys.exit(1)
    
    chapters_dir = sys.argv[1]
    output_file = None
    level = 3
    quiet = "--quiet" in sys.argv
    custom_path = None
    
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
    
    if "--custom" in sys.argv:
        idx = sys.argv.index("--custom")
        if idx + 1 < len(sys.argv):
            custom_path = sys.argv[idx + 1]
    
    # 加载词库
    wordlib = load_wordlib(custom_path)
    
    # 扫描
    if not quiet:
        print(f"正在扫描章节目录: {chapters_dir} (检测级别: {level})")
        if custom_path:
            print(f"使用自定义词库: {custom_path}")
    result = scan_chapters(chapters_dir, wordlib, level)
    
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
