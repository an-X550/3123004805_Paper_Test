#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版单元测试
学号: 3123004805
"""

import unittest
import os
import tempfile
import sys
from main_simple import (
    read_file, preprocess_text, calculate_word_frequency,
    compute_cosine_similarity, main
)


class TestPaperCheckerSimple(unittest.TestCase):
    """简化版测试类"""

    def setUp(self):
        """测试准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file1 = os.path.join(self.temp_dir, "test1.txt")
        self.test_file2 = os.path.join(self.temp_dir, "test2.txt")
        self.result_file = os.path.join(self.temp_dir, "result.txt")

    def tearDown(self):
        """清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_file(self, file_path, content):
        """创建测试文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def test_preprocess_text(self):
        """测试文本预处理"""
        text = "今天是星期天，天气晴朗。"
        words = preprocess_text(text)
        self.assertGreater(len(words), 0)
        self.assertIn("今天", words)

    def test_word_frequency(self):
        """测试词频计算"""
        words = ["苹果", "香蕉", "苹果"]
        freq = calculate_word_frequency(words)
        self.assertEqual(freq["苹果"], 2)
        self.assertEqual(freq["香蕉"], 1)

    def test_cosine_similarity(self):
        """测试相似度计算"""
        freq1 = {"苹果": 2, "香蕉": 1}
        freq2 = {"苹果": 2, "香蕉": 1}
        similarity = compute_cosine_similarity(freq1, freq2)
        self.assertAlmostEqual(similarity, 1.0, places=5)

    def test_main_function(self):
        """测试主函数"""
        content1 = "今天是星期天，天气晴朗。"
        content2 = "今天是周日，天气很好。"
        
        self.create_test_file(self.test_file1, content1)
        self.create_test_file(self.test_file2, content2)
        
        # 备份sys.argv
        original_argv = sys.argv[:]
        
        try:
            sys.argv = ['test', self.test_file1, self.test_file2, self.result_file]
            main()
            
            # 检查结果文件
            self.assertTrue(os.path.exists(self.result_file))
            
            with open(self.result_file, 'r') as f:
                result = float(f.read())
            
            self.assertGreaterEqual(result, 0.0)
            self.assertLessEqual(result, 100.0)
            
        finally:
            sys.argv = original_argv


def run_simple_tests():
    """运行简化测试"""
    print("🧪 运行简化版单元测试")
    print("=" * 40)
    
    # 运行测试
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestPaperCheckerSimple)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 显示结果
    if result.wasSuccessful():
        print("\n✅ 所有测试通过!")
    else:
        print(f"\n❌ 测试失败: {len(result.failures)} 个失败, {len(result.errors)} 个错误")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    run_simple_tests()
