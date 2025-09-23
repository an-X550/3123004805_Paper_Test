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
    
    @classmethod
    def setUpClass(cls):
        """在所有测试开始前显示项目功能说明"""
        print("\n" + "=" * 80)
        print("论文查重系统 - 学号: 3123004805")
        print("=" * 80)
        print()
        print("项目功能：")
        print("给出一个原文文件和一个在这份原文上经过了增删改的抄袭版论文的文件，")
        print("在答案文件中输出其重复率。")
        print()
        print("示例：")
        print("原文示例：今天是星期天，天气晴，今天晚上我要去看电影。")
        print("抄袭版示例：今天是周天，天气晴朗，我晚上要去看电影。")
        print()
        print("使用方法：")
        print("python main.py [原文文件绝对路径] [抄袭版文件绝对路径] [答案文件绝对路径]")
        print()
        print("输入输出规范：")
        print("-从命令行参数给出：论文原文的文件的绝对路径")
        print("-从命令行参数给出：抄袭版论文的文件的绝对路径")
        print("-从命令行参数给出：输出的答案文件的绝对路径")
        print("-答案文件输出浮点型结果，精确到小数点后两位")
        print()
        print("测试数据路径：")
        print("C:\\Users\\panda\\Desktop\\test_data\\")
        print()
        print("实际使用示例：")
        print("python main.py C:\\Users\\panda\\Desktop\\test_data\\orig.txt  C:\\Users\\panda\\Desktop\\test_data\\orig_0.8_add.txt  C:\\Users\\panda\\Desktop\\test_data\\result.txt")
        print()
        print("开始运行单元测试:")
        print("=" * 80)

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
        # 捕获stderr输出，避免在测试时显示错误信息
        import io
        import contextlib
        
        stderr_capture = io.StringIO()
        with contextlib.redirect_stderr(stderr_capture):
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
        self.assertEqual(result, tuple())

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
        print(f"\n   示例重复率结果: {result}%")
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

    def test_16_large_text_processing(self):
        """测试用例16: 大文本处理性能测试"""
        # 创建较大的测试文本
        large_text = "这是一个测试文本。" * 1000  # 约8000字符
        words = preprocess_text(large_text)
        self.assertGreater(len(words), 0)
        # 验证处理时间合理（这里只验证功能正确性）
        self.assertIsInstance(words, (list, tuple))

    def test_17_edge_case_similarity(self):
        """测试用例17: 边界情况相似度测试"""
        # 测试完全相同但顺序不同的词频
        freq1 = {"word1": 3, "word2": 2, "word3": 1}
        freq2 = {"word3": 1, "word1": 3, "word2": 2}
        similarity = compute_cosine_similarity(freq1, freq2)
        self.assertAlmostEqual(similarity, 1.0, places=5)

    def test_18_unicode_handling(self):
        """测试用例18: Unicode字符处理"""
        # 测试各种Unicode字符
        unicode_text = "测试文本包含emoji😀和特殊符号★☆以及中文标点，。！？"
        words = preprocess_text(unicode_text)
        # 验证能正确处理Unicode字符
        self.assertIsInstance(words, (list, tuple))
        # 验证包含中文字符
        chinese_words = [word for word in words if any('\u4e00' <= c <= '\u9fff' for c in word)]
        self.assertGreater(len(chinese_words), 0)

    @classmethod
    def tearDownClass(cls):
        """在所有测试结束后显示实际重复率计算结果"""
        print("\n" + "=" * 80)
        print("论文查重系统 - 重复率计算演示")
        print("=" * 80)
        print()
        
        # 测试数据路径
        test_data_path = r"C:\Users\panda\Desktop\test_data"
        orig_file = os.path.join(test_data_path, "orig.txt")
        
        # 定义所有测试文件
        test_files = [
            ("orig_0.8_add.txt", "添加版本"),
            ("orig_0.8_del.txt", "删除版本"),
            ("orig_0.8_dis_1.txt", "替换1%版本"),
            ("orig_0.8_dis_10.txt", "替换10%版本"),
            ("orig_0.8_dis_15.txt", "替换15%版本")
        ]
        
        if os.path.exists(orig_file):
            print("使用实际测试数据计算重复率:")
            print(f"原文文件: {orig_file}")
            print()
            
            # 备份原始argv
            original_argv = sys.argv
            
            for i, (test_file, description) in enumerate(test_files, 1):
                plagiarized_file = os.path.join(test_data_path, test_file)
                
                if os.path.exists(plagiarized_file):
                    print(f"测试用例 {i}: {description}")
                    print(f"抄袭版文件: {plagiarized_file}")
                    
                    # 创建结果文件
                    result_file = os.path.join(tempfile.gettempdir(), f"result_{i}.txt")
                    
                    try:
                        # 设置命令行参数
                        sys.argv = ['main.py', orig_file, plagiarized_file, result_file]
                        
                        # 运行主程序
                        main()
                        
                        # 读取结果
                        if os.path.exists(result_file):
                            with open(result_file, 'r', encoding='utf-8') as f:
                                similarity = f.read().strip()
                            print(f"重复率结果: {similarity}%")
                            print(f"答案文件内容: {similarity}")
                        else:
                            print("ERROR:结果文件未生成")
                        
                    except Exception as e:
                        print(f"计算出错: {e}")
                    
                    print("-" * 60)
                else:
                    print(f"测试用例 {i}: {description}")
                    print(f"ERROR:文件不存在 {plagiarized_file}")
                    print("-" * 60)
            
            # 恢复原始argv
            sys.argv = original_argv
        else:
            print("测试数据文件不存在，使用示例数据:")
            
            # 使用示例数据
            temp_dir = tempfile.mkdtemp()
            orig_file = os.path.join(temp_dir, "demo_orig.txt")
            plagiarized_file = os.path.join(temp_dir, "demo_plagiarized.txt")
            result_file = os.path.join(temp_dir, "demo_result.txt")
            
            # 创建示例文件
            original_content = "今天是星期天，天气晴，今天晚上我要去看电影。"
            plagiarized_content = "今天是周天，天气晴朗，我晚上要去看电影。"
            
            with open(orig_file, 'w', encoding='utf-8') as f:
                f.write(original_content)
            with open(plagiarized_file, 'w', encoding='utf-8') as f:
                f.write(plagiarized_content)
            
            print(f" 原文: {original_content}")
            print(f" 抄袭版: {plagiarized_content}")
            print()
            
            try:
                # 备份原始argv
                original_argv = sys.argv
                
                # 设置命令行参数
                sys.argv = ['main.py', orig_file, plagiarized_file, result_file]
                
                # 运行主程序
                main()
                
                # 读取结果
                if os.path.exists(result_file):
                    with open(result_file, 'r', encoding='utf-8') as f:
                        similarity = f.read().strip()
                    print(f" 重复率结果: {similarity}%")
                    print(f" 答案文件内容: {similarity}")
                
                # 恢复原始argv
                sys.argv = original_argv
                
                # 清理临时文件
                shutil.rmtree(temp_dir, ignore_errors=True)
                
            except Exception as e:
                print(f"计算出错: {e}")
                sys.argv = original_argv
                shutil.rmtree(temp_dir, ignore_errors=True)
        
        print()
        print("重复率计算完成!")
        print("=" * 80)


if __name__ == '__main__':
    unittest.main(verbosity=2)
