#!/usr/bin/env python3
"""
wq-finalize 错别字检查脚本
扫描小说章节中的常见错别字和拼写错误

使用方法：
    python spell-check.py <章节目录> [--output <输出文件>]

输出：
    生成 error-report.json 包含所有发现的错别字
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

_CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"

def _load_spell_errors() -> Dict[str, str]:
    defaults = {
        "在现": "再现",
        "做用": "作用",
        "象象": "现象",
        "在见": "再见",
        "做业": "作业",
        "做文": "作文",
        "象前": "向前",
        "象往": "向往",
        "做战": "作战",
        "做手": "着手",
        "做风": "作风",
        "做秀": "作秀",
        "做古": "作古",
        "做乱": "作乱",
        "做孽": "作孽",
        "做死": "作死",
        "做怪": "作怪",
        "做寿": "作寿",
        "做媒": "作媒",
        "做准": "作准",
        "做数": "作数",
        "做兴": "作兴",
        "再所不惜": "在所不惜",
        "再接再励": "再接再厉",
        "按步就班": "按部就班",
        "一愁莫展": "一筹莫展",
        "穿流不息": "川流不息",
        "谈笑风声": "谈笑风生",
        "金壁辉煌": "金碧辉煌",
        "美仑美奂": "美轮美奂",
        "迫不急待": "迫不及待",
        "不径而走": "不胫而走",
        "名列前矛": "名列前茅",
        "黄梁美梦": "黄粱美梦",
        "蛛丝蚂迹": "蛛丝马迹",
        "默守成规": "墨守成规",
        "委屈求全": "委曲求全",
        "走头无路": "走投无路",
        "一诺千斤": "一诺千金",
        "天翻地复": "天翻地覆",
        "一股作气": "一鼓作气",
        "悬梁刺骨": "悬梁刺股",
        "世外桃园": "世外桃源",
        "名门旺族": "名门望族",
        "额首称庆": "额手称庆",
        "旁证博引": "旁征博引",
        "草管人命": "草菅人命",
        "峻工": "竣工",
        "痉孪": "痉挛",
        "修茸": "修葺",
        "亲睐": "青睐",
        "磬竹难书": "罄竹难书",
        "入场卷": "入场券",
        "声名雀起": "声名鹊起",
        "发韧": "发轫",
        "眩耀": "炫耀",
        "九洲": "九州",
        "大才小用": "大材小用",
        "鬼鬼崇崇": "鬼鬼祟祟",
        "金榜提名": "金榜题名",
        "趋之若骛": "趋之若鹜",
        "迁徒": "迁徙",
        "洁白无暇": "洁白无瑕",
        "天崖": "天涯",
        "萎糜不振": "萎靡不振",
        "沉缅": "沉湎",
        "名信片": "明信片",
        "沤心沥血": "呕心沥血",
        "凭添": "平添",
        "出奇不意": "出其不意",
    }
    try:
        cfg_file = _CONFIG_DIR / "spell-dict.json"
        if cfg_file.exists():
            data = json.loads(cfg_file.read_text("utf-8"))
            external = data.get("spelling_errors", {})
            if external:
                merged = dict(defaults)
                merged.update(external)
                return merged
    except Exception:
        pass
    return defaults

SPELLING_ERRORS: Dict[str, str] = _load_spell_errors()

# 重复字检测模式
REPEATED_CHARS_PATTERN = re.compile(r'(.)\1{2,}')

# 允许重复的字符白名单（合法用法）
REPEATED_CHARS_WHITELIST = {
    "\u2026",   # …（省略号，常写作……）
    "\u2014",   # —（破折号，常写作——）
    "哈", "嘿", "呵", "啊", "嗯", "呃", "哇", "咦",   # 常见拟声词
}

# 共享标点规则配置
_SHARED_PUNCT_RULES_PATH = _CONFIG_DIR / "punctuation-rules.json"

def _load_punctuation_errors() -> Dict[str, str]:
    """加载共享标点重复检测规则（与 format-validator.py 共享同一配置）"""
    defaults = {
        "，，": "，", "。。": "。", "！！": "！", "？？": "？",
        '""': '"', "：：": "：", "；；": "；",
    }
    try:
        if _SHARED_PUNCT_RULES_PATH.exists():
            data = json.loads(_SHARED_PUNCT_RULES_PATH.read_text("utf-8"))
            return data.get("punctuation_errors", defaults)
    except Exception:
        pass
    return defaults

# 标点符号错误模式（共享配置）
PUNCTUATION_ERRORS: Dict[str, str] = _load_punctuation_errors()


def check_spell_errors(text: str, chapter_id: str) -> List[Dict]:
    """检查文本中的错别字"""
    errors = []
    
    # 检查常见错别字
    for wrong, correct in SPELLING_ERRORS.items():
        if wrong in text:
            # 找到所有出现位置
            for match in re.finditer(re.escape(wrong), text):
                start = max(0, match.start() - 20)
                end = min(len(text), match.end() + 20)
                context = text[start:end]
                
                errors.append({
                    "chapter": chapter_id,
                    "type": "spelling",
                    "severity": "medium",
                    "position": match.start(),
                    "wrong": wrong,
                    "correct": correct,
                    "context": context,
                    "suggestion": f"将'{wrong}'改为'{correct}'"
                })
    
    # 检查重复字
    for match in REPEATED_CHARS_PATTERN.finditer(text):
        char = match.group(1)
        # 跳过白名单中的合法重复字符
        if char in REPEATED_CHARS_WHITELIST:
            continue
        start = max(0, match.start() - 10)
        end = min(len(text), match.end() + 10)
        context = text[start:end]
        
        errors.append({
            "chapter": chapter_id,
            "type": "repeated_char",
            "severity": "low",
            "position": match.start(),
            "wrong": match.group(),
            "correct": char,
            "context": context,
            "suggestion": f"删除重复字符'{char}'"
        })
    
    # 检查标点符号重复
    for wrong, correct in PUNCTUATION_ERRORS.items():
        if wrong in text:
            for match in re.finditer(re.escape(wrong), text):
                start = max(0, match.start() - 10)
                end = min(len(text), match.end() + 10)
                context = text[start:end]
                
                errors.append({
                    "chapter": chapter_id,
                    "type": "punctuation",
                    "severity": "medium",
                    "position": match.start(),
                    "wrong": wrong,
                    "correct": correct,
                    "context": context,
                    "suggestion": f"将'{wrong}'改为'{correct}'"
                })
    
    return errors


def scan_chapters(chapters_dir: str) -> Dict:
    """扫描章节目录中的所有文件"""
    all_errors = []
    chapters_scanned = 0
    
    chapters_path = Path(chapters_dir)
    if not chapters_path.exists():
        return {"error": f"目录不存在: {chapters_dir}", "chapters_scanned": 0}
    
    # 支持 .md 和 .txt 文件
    for file_path in chapters_path.glob("**/*.md"):
        chapters_scanned += 1
        chapter_id = file_path.stem  # 文件名（不含扩展名）
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            errors = check_spell_errors(text, chapter_id)
            all_errors.extend(errors)
            
        except Exception as e:
            all_errors.append({
                "chapter": chapter_id,
                "type": "read_error",
                "severity": "high",
                "error": str(e),
                "suggestion": "检查文件编码或权限"
            })
    
    # 也扫描 .txt 文件
    for file_path in chapters_path.glob("**/*.txt"):
        chapters_scanned += 1
        chapter_id = file_path.stem
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            errors = check_spell_errors(text, chapter_id)
            all_errors.extend(errors)
            
        except Exception as e:
            all_errors.append({
                "chapter": chapter_id,
                "type": "read_error",
                "severity": "high",
                "error": str(e),
                "suggestion": "检查文件编码或权限"
            })
    
    # 统计
    error_stats = {
        "spelling": len([e for e in all_errors if e.get("type") == "spelling"]),
        "repeated_char": len([e for e in all_errors if e.get("type") == "repeated_char"]),
        "punctuation": len([e for e in all_errors if e.get("type") == "punctuation"]),
        "read_error": len([e for e in all_errors if e.get("type") == "read_error"]),
    }
    
    return {
        "chapters_scanned": chapters_scanned,
        "total_errors": len(all_errors),
        "error_stats": error_stats,
        "errors": all_errors
    }


def main():
    if len(sys.argv) < 2:
        print("用法: python spell-check.py <章节目录> [--output <输出文件>] [--quiet]")
        print("\n示例:")
        print("  python spell-check.py .sumeru/chapters/")
        print("  python spell-check.py .sumeru/chapters/ --quiet")
        sys.exit(1)
    
    chapters_dir = sys.argv[1]
    output_file = None
    quiet = "--quiet" in sys.argv
    
    # 解析参数
    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_file = sys.argv[idx + 1]
    
    # 扫描
    if not quiet:
        print(f"正在扫描章节目录: {chapters_dir}")
    result = scan_chapters(chapters_dir)
    
    # 输出
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        if not quiet:
            print(f"错误报告已保存到: {output_file}")
    elif not quiet:
        print("\n" + "="*60)
        print("错别字检查结果")
        print("="*60)
        print(f"扫描章节数: {result.get('chapters_scanned', 0)}")
        print(f"发现错误总数: {result.get('total_errors', 0)}")
        
        if 'error_stats' in result:
            stats = result['error_stats']
            print(f"\n错误类型统计:")
            print(f"  错别字: {stats.get('spelling', 0)}")
            print(f"  重复字符: {stats.get('repeated_char', 0)}")
            print(f"  标点错误: {stats.get('punctuation', 0)}")
        
        if result.get('errors'):
            print("\n前10个错误示例:")
            for i, error in enumerate(result['errors'][:10]):
                print(f"\n  [{i+1}] {error.get('chapter')} - {error.get('type')}")
                print(f"      {error.get('suggestion', '')}")
                if 'context' in error:
                    print(f"      上下文: ...{error['context']}...")
    
    # 静默模式：只输出有错误时的提醒
    elif quiet and result.get('total_errors', 0) > 0:
        stats = result.get('error_stats', {})
        spelling = stats.get('spelling', 0)
        if spelling > 0:
            print(f"⚠️ 发现 {spelling} 个错别字")
    
    return result


if __name__ == "__main__":
    main()
