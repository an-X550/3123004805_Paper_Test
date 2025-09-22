#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
论文查重系统单元测试
学号: 3123004805
"""

import unittest
import os
import tempfile
import sys
import shutil
from unittest.mock import patch

from main import (
    read_file, preprocess_text, calculate_word_frequency,
    compute_cosine_similarity, write_result, validate_arguments, main
)


class TestPaperChecker(unittest.TestCase):
    """论文查重工具的单元测试类"""

    def setUp(self):
        """测试前的准备工作"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_file = os.path.join(self.temp_dir, "original.txt")
        self.plagiarized_file = os.path.join(self.temp_dir, "plagiarized.txt")
        self.result_file = os.path.join(self.temp_dir, "result.txt")

    def tearDown(self):
        """测试后的清理工作"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_file(self, file_path: str, content: str, encoding: str = 'utf-8'):
        """创建测试文件"""
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)

    def read_result_file(self) -> float:
        """读取结果文件内容"""
        with open(self.result_file, 'r', encoding='utf-8') as f:
            return float(f.read())

    def test_01_read_file_success(self):
        """测试用例1: 成功读取文件"""
        content = "测试内容"
        self.create_test_file(self.original_file, content)
        result = read_file(self.original_file)
        self.assertEqual(result, content)

    def test_02_read_file_not_exist(self):
        """测试用例2: 读取不存在的文件"""
        non_exist_file = os.path.join(self.temp_dir, "non_exist.txt")
        with self.assertRaises(SystemExit):
            read_file(non_exist_file)

    def test_03_preprocess_text_normal(self):
        """测试用例3: 正常文本预处理"""
        text = "今天是星期天，天气晴，今天晚上我要去看电影。"
        words = preprocess_text(text)
        self.assertIn("今天", words)
        self.assertIn("星期", words)
        # 停用词"是"应该被过滤掉，不会出现在双字符分词中

    def test_04_preprocess_text_empty(self):
        """测试用例4: 空文本预处理"""
        result = preprocess_text("")
        self.assertEqual(result, [])

    def test_05_calculate_word_frequency(self):
        """测试用例5: 词频计算"""
        words = ["苹果", "香蕉", "苹果", "橙子", "苹果"]
        freq = calculate_word_frequency(words)
        self.assertEqual(freq["苹果"], 3)
        self.assertEqual(freq["香蕉"], 1)

    def test_06_cosine_similarity_identical(self):
        """测试用例6: 完全相同文档的余弦相似度"""
        freq1 = {"苹果": 2, "香蕉": 1}
        freq2 = {"苹果": 2, "香蕉": 1}
        similarity = compute_cosine_similarity(freq1, freq2)
        self.assertAlmostEqual(similarity, 1.0, places=5)

    def test_07_cosine_similarity_no_common(self):
        """测试用例7: 无共同词汇的余弦相似度"""
        freq1 = {"苹果": 2}
        freq2 = {"橙子": 1}
        similarity = compute_cosine_similarity(freq1, freq2)
        self.assertEqual(similarity, 0.0)

    def test_08_cosine_similarity_empty(self):
        """测试用例8: 空文档的余弦相似度"""
        freq1 = {"苹果": 2}
        freq2 = {}
        similarity = compute_cosine_similarity(freq1, freq2)
        self.assertEqual(similarity, 0.0)

    def test_09_write_result(self):
        """测试用例9: 写入结果文件"""
        similarity = 0.8756
        write_result(self.result_file, similarity)
        self.assertTrue(os.path.exists(self.result_file))
        result = self.read_result_file()
        self.assertEqual(result, 87.56)

    def test_10_validate_arguments_success(self):
        """测试用例10: 有效参数验证"""
        self.create_test_file(self.original_file, "原文")
        self.create_test_file(self.plagiarized_file, "抄袭版")
        args = ["main.py", self.original_file, self.plagiarized_file, self.result_file]
        orig, plag, result = validate_arguments(args)
        self.assertEqual(orig, self.original_file)

    def test_11_integration_identical_texts(self):
        """测试用例11: 完全相同文本的集成测试"""
        content = "今天是星期天，天气晴，今天晚上我要去看电影。"
        self.create_test_file(self.original_file, content)
        self.create_test_file(self.plagiarized_file, content)
        
        with patch('sys.argv', ['main.py', self.original_file, 
                                self.plagiarized_file, self.result_file]):
            main()
        
        result = self.read_result_file()
        self.assertEqual(result, 100.00)

    def test_12_integration_partial_similarity(self):
        """测试用例12: 部分相似文本的集成测试"""
        original = "今天是星期天，天气晴，今天晚上我要去看电影。"
        plagiarized = "今天是周天，天气晴朗，我晚上要去看电影。"
        
        self.create_test_file(self.original_file, original)
        self.create_test_file(self.plagiarized_file, plagiarized)
        
        with patch('sys.argv', ['main.py', self.original_file, 
                                self.plagiarized_file, self.result_file]):
            main()
        
        result = self.read_result_file()
        self.assertGreater(result, 50.0)
        self.assertLess(result, 100.0)

    def test_13_mixed_language(self):
        """测试用例13: 中英文混合文本"""
        text = "Python是一种编程语言，very popular。"
        words = preprocess_text(text)
        self.assertIn("python", words)
        self.assertIn("编程", words)
        # popular可能与very连在一起，检查是否存在包含popular的词
        has_popular = any("popular" in word for word in words)
        self.assertTrue(has_popular)

    def test_14_special_characters(self):
        """测试用例14: 特殊字符处理"""
        text = "测试@#$%文本！！！"
        words = preprocess_text(text)
        # 检查是否包含测试相关的双字符组合
        word_str = ''.join(words)
        self.assertTrue("测试" in word_str or "试文" in words or "文本" in word_str)

    def test_15_different_encodings(self):
        """测试用例15: 不同编码处理"""
        content = "中文测试"
        gbk_file = os.path.join(self.temp_dir, "gbk.txt")
        self.create_test_file(gbk_file, content, 'gbk')
        result = read_file(gbk_file)
        self.assertEqual(result, content)


if __name__ == '__main__':
    unittest.main(verbosity=2)
