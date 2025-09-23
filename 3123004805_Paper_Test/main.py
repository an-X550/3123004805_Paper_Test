#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
论文查重系统主程序
学号: 3123004805

使用方法: python main.py [原文文件] [抄袭版论文的文件] [答案文件]
"""

import sys
import os
import re
import math
import string
from collections import defaultdict
from typing import Dict, List, Tuple
from functools import lru_cache

# 预编译正则表达式以提高性能
ENGLISH_PATTERN = re.compile(r'[a-zA-Z]+')
CHINESE_REMOVAL_PATTERN = re.compile(r'[a-zA-Z\s]+')

# 预定义停用词集合
STOPWORDS = frozenset({
    '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', 
    '一个', '上', '也', '到', '说', '要', '去', '你', '会', '着', '没有', 
    '看', '好', '自己', '这', '那', '他', '她', '它', '我们', '你们', 
    '他们', '她们', '它们', '这个', '那个', '什么', '怎么', '为什么',
    '但是', '然后', '所以', '因为', '如果', '虽然', '可是', '不过',
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 
    'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 
    'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did'
})

# 预定义标点符号转换表
PUNCTUATION = string.punctuation + "，。、；：？！''""（）【】《》〈〉「」『』〔〕…—·\n\t\r "
TRANSLATOR = str.maketrans('', '', PUNCTUATION)


def read_file(file_path: str) -> str:
    """
    读取文件内容
    
    Args:
        file_path (str): 文件路径
        
    Returns:
        str: 文件内容
        
    Raises:
        SystemExit: 文件读取失败时退出程序
    """
    if not os.path.exists(file_path):
        print(f"错误: 文件不存在 {file_path}", file=sys.stderr)
        sys.exit(1)
        
    try:
        # 尝试多种编码方式读取文件
        encodings = ['utf-8', 'gbk', 'gb2312', 'utf-16']
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        
        # 如果所有编码都失败，抛出异常
        raise UnicodeDecodeError("无法解码文件")
        
    except Exception as e:
        print(f"读取文件错误: {e}", file=sys.stderr)
        sys.exit(1)


@lru_cache(maxsize=128)
def preprocess_text(text: str) -> Tuple[str, ...]:
    """
    文本预处理：去除标点符号、分词、去除停用词
    优化版本：使用缓存和预编译正则表达式提高性能
    
    Args:
        text (str): 原始文本
        
    Returns:
        Tuple[str, ...]: 处理后的词元组（用于缓存）
    """
    if not text.strip():
        return tuple()
    
    # 去除标点符号和特殊字符，转为小写
    cleaned_text = text.translate(TRANSLATOR).lower()
    
    words = []
    
    # 提取英文单词 - 优化：直接过滤长度和停用词
    english_words = [
        word for word in ENGLISH_PATTERN.findall(cleaned_text) 
        if len(word) >= 2 and word not in STOPWORDS
    ]
    words.extend(english_words)
    
    # 对中文进行双字符分词
    chinese_text = CHINESE_REMOVAL_PATTERN.sub('', cleaned_text)
    chinese_len = len(chinese_text)
    
    # 批量处理中文双字符分词 - 优化：使用列表推导式
    chinese_bigrams = [
        chinese_text[i:i+2] 
        for i in range(chinese_len - 1)
        if ('\u4e00' <= chinese_text[i] <= '\u9fff' and 
            '\u4e00' <= chinese_text[i+1] <= '\u9fff' and
            chinese_text[i:i+2] not in STOPWORDS)
    ]
    
    words.extend(chinese_bigrams)
    
    # 返回元组以支持缓存
    return tuple(words)


def calculate_word_frequency(words: List[str]) -> Dict[str, int]:
    """
    计算词频
    
    Args:
        words (List[str]): 词列表
        
    Returns:
        Dict[str, int]: 词频字典
    """
    word_freq = defaultdict(int)
    for word in words:
        word_freq[word] += 1
    return dict(word_freq)


def compute_cosine_similarity(freq1: Dict[str, int], freq2: Dict[str, int]) -> float:
    """
    计算余弦相似度
    
    Args:
        freq1 (Dict[str, int]): 第一个文档的词频
        freq2 (Dict[str, int]): 第二个文档的词频
        
    Returns:
        float: 余弦相似度值 (0-1)
    """
    # 如果任一文档为空，返回0
    if not freq1 or not freq2:
        return 0.0
    
    # 获取所有独特的词
    all_words = set(freq1.keys()).union(set(freq2.keys()))
    
    if not all_words:
        return 0.0
    
    # 计算点积
    dot_product = 0
    for word in all_words:
        dot_product += freq1.get(word, 0) * freq2.get(word, 0)
    
    # 计算向量的模
    magnitude1 = math.sqrt(sum(count ** 2 for count in freq1.values()))
    magnitude2 = math.sqrt(sum(count ** 2 for count in freq2.values()))
    
    # 避免除以零
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    
    # 计算余弦相似度
    cosine_sim = dot_product / (magnitude1 * magnitude2)
    
    # 确保结果在[0, 1]范围内
    return max(0.0, min(1.0, cosine_sim))


def compute_jaccard_similarity(freq1: Dict[str, int], freq2: Dict[str, int]) -> float:
    """
    计算Jaccard相似度作为辅助指标
    
    Args:
        freq1 (Dict[str, int]): 第一个文档的词频
        freq2 (Dict[str, int]): 第二个文档的词频
        
    Returns:
        float: Jaccard相似度值 (0-1)
    """
    set1 = set(freq1.keys())
    set2 = set(freq2.keys())
    
    if not set1 and not set2:
        return 1.0
    
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    
    if union == 0:
        return 0.0
    
    return intersection / union


def write_result(result_path: str, similarity: float) -> None:
    """
    将结果写入文件
    
    Args:
        result_path (str): 结果文件路径
        similarity (float): 相似度值
        
    Raises:
        SystemExit: 文件写入失败时退出程序
    """
    try:
        # 确保目录存在
        result_dir = os.path.dirname(result_path)
        if result_dir and not os.path.exists(result_dir):
            os.makedirs(result_dir)
            
        # 转换为百分比并保留两位小数
        similarity_percent = round(similarity * 100, 2)
        
        with open(result_path, 'w', encoding='utf-8') as f:
            f.write(f"{similarity_percent:.2f}")
            
    except Exception as e:
        print(f"写入文件错误: {e}", file=sys.stderr)
        sys.exit(1)


def validate_arguments(args: List[str]) -> Tuple[str, str, str]:
    """
    验证命令行参数
    
    Args:
        args (List[str]): 命令行参数列表
        
    Returns:
        Tuple[str, str, str]: (原文路径, 抄袭版路径, 结果路径)
        
    Raises:
        SystemExit: 参数无效时退出程序
    """
    if len(args) != 4:
        print("用法: python main.py [原文文件] [抄袭版论文的文件] [答案文件]", file=sys.stderr)
        print("示例: python main.py C:\\Users\\panda\\Desktop\\test_data\\orig.txt C:\\Users\\panda\\Desktop\\test_data\\copy.txt result.txt", file=sys.stderr)
        sys.exit(1)
    
    original_path = args[1]
    plagiarized_path = args[2]
    result_path = args[3]
    
    # 检查输入文件是否存在
    if not os.path.exists(original_path):
        print(f"错误: 原文文件不存在 {original_path}", file=sys.stderr)
        sys.exit(1)
        
    if not os.path.exists(plagiarized_path):
        print(f"错误: 抄袭版文件不存在 {plagiarized_path}", file=sys.stderr)
        sys.exit(1)
    
    return original_path, plagiarized_path, result_path


def main() -> None:
    """
    主函数
    
    如果在PyCharm中运行，请配置运行参数：
    Run → Edit Configurations → Parameters: C:\\Users\\panda\\Desktop\\test_data\\orig.txt C:\\Users\\panda\\Desktop\\test_data\\orig_0.8_add.txt result.txt
    """
    try:
        # 如果没有参数且在IDE中运行，提供友好提示
        if len(sys.argv) == 1:
            print("PyCharm用户提示:")
            print("请配置运行参数: Run → Edit Configurations → Parameters")
            print("示例参数: C:\\Users\\panda\\Desktop\\test_data\\orig.txt C:\\Users\\panda\\Desktop\\test_data\\orig_0.8_add.txt result.txt")
            print()
            print("或者运行 pycharm_quick_start.py 进行快速测试")
            print("=" * 50)
        
        # 验证命令行参数
        original_path, plagiarized_path, result_path = validate_arguments(sys.argv)
        
        # 读取文件内容
        original_text = read_file(original_path)
        plagiarized_text = read_file(plagiarized_path)
        
        # 文本预处理
        original_words = list(preprocess_text(original_text))
        plagiarized_words = list(preprocess_text(plagiarized_text))
        
        # 计算词频
        original_freq = calculate_word_frequency(original_words)
        plagiarized_freq = calculate_word_frequency(plagiarized_words)
        
        # 计算相似度
        cosine_sim = compute_cosine_similarity(original_freq, plagiarized_freq)
        
        # 写入结果文件
        write_result(result_path, cosine_sim)
        
    except KeyboardInterrupt:
        print("\n程序被用户中断", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"程序执行错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()