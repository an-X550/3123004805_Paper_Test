#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
论文查重系统 - 简化版
学号: 3123004805

使用方法: python main_simple.py [原文文件] [抄袭版文件] [结果文件]
"""

import sys
import os
import re
import math
from collections import defaultdict


def read_file(file_path):
    """读取文件内容"""
    if not os.path.exists(file_path):
        print(f"错误: 文件不存在 {file_path}")
        sys.exit(1)
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='gbk') as f:
                return f.read()
        except Exception as e:
            print(f"文件读取错误: {e}")
            sys.exit(1)


def preprocess_text(text):
    """文本预处理和分词"""
    if not text.strip():
        return []
    
    # 去除标点符号
    text = re.sub(r'[^\u4e00-\u9fff\w\s]', '', text)
    text = text.lower()
    
    # 提取中英文词汇
    words = []
    
    # 英文单词
    english_words = re.findall(r'[a-zA-Z]{2,}', text)
    words.extend(english_words)
    
    # 中文双字符分词
    chinese_text = re.sub(r'[a-zA-Z\s]+', '', text)
    for i in range(len(chinese_text) - 1):
        bigram = chinese_text[i:i+2]
        if len(bigram) == 2:
            words.append(bigram)
    
    # 去除停用词
    stopwords = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '要', '去', '你', '会', '着'}
    words = [word for word in words if word not in stopwords and len(word) >= 2]
    
    return words


def calculate_word_frequency(words):
    """计算词频"""
    freq = defaultdict(int)
    for word in words:
        freq[word] += 1
    return dict(freq)


def compute_cosine_similarity(freq1, freq2):
    """计算余弦相似度"""
    if not freq1 or not freq2:
        return 0.0
    
    # 获取所有词汇
    all_words = set(freq1.keys()).union(set(freq2.keys()))
    
    # 计算点积
    dot_product = sum(freq1.get(word, 0) * freq2.get(word, 0) for word in all_words)
    
    # 计算向量模长
    magnitude1 = math.sqrt(sum(count ** 2 for count in freq1.values()))
    magnitude2 = math.sqrt(sum(count ** 2 for count in freq2.values()))
    
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    
    return dot_product / (magnitude1 * magnitude2)


def write_result(result_path, similarity):
    """写入结果文件"""
    try:
        with open(result_path, 'w', encoding='utf-8') as f:
            f.write(f"{similarity:.2f}")
    except Exception as e:
        print(f"写入文件错误: {e}")
        sys.exit(1)


def main():
    """主函数"""
    # 检查命令行参数
    if len(sys.argv) != 4:
        print("用法: python main_simple.py [原文文件] [抄袭版文件] [结果文件]")
        print("示例: python main_simple.py orig.txt orig_0.8_add.txt result.txt")
        print()
        print("PyCharm用户:")
        print("   右键文件 → Run → Edit Configurations → Parameters:")
        print("   orig.txt orig_0.8_add.txt result.txt")
        sys.exit(1)
    
    # 获取文件路径
    original_path = sys.argv[1]
    plagiarized_path = sys.argv[2] 
    result_path = sys.argv[3]
    
    try:
        # 读取文件
        original_text = read_file(original_path)
        plagiarized_text = read_file(plagiarized_path)
        
        # 文本预处理
        original_words = preprocess_text(original_text)
        plagiarized_words = preprocess_text(plagiarized_text)
        
        # 计算词频
        original_freq = calculate_word_frequency(original_words)
        plagiarized_freq = calculate_word_frequency(plagiarized_words)
        
        # 计算相似度
        similarity = compute_cosine_similarity(original_freq, plagiarized_freq)
        
        # 转换为百分比
        similarity_percent = similarity * 100
        
        # 写入结果
        write_result(result_path, similarity_percent)
        
        print(f"查重完成")
        print(f"原文: {original_path}")
        print(f"对比: {plagiarized_path}")
        print(f"相似度: {similarity_percent:.2f}%")
        print(f"结果文件: {result_path}")
        
    except Exception as e:
        print(f"程序执行错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
