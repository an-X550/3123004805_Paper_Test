#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
论文查重系统性能分析脚本
学号: 3123004805
"""

import cProfile
import pstats
import sys
import os
from main import main

def profile_main():
    """对主程序进行性能分析"""
    # 设置测试参数
    test_args = [
        "main.py",
        "orig.txt", 
        "orig_0.8_add.txt",
        "result_profile.txt"
    ]
    
    # 备份原始argv
    original_argv = sys.argv
    
    try:
        # 设置测试参数
        sys.argv = test_args
        
        # 创建性能分析器
        pr = cProfile.Profile()
        
        # 开始性能分析
        pr.enable()
        
        # 运行主程序
        main()
        
        # 停止性能分析
        pr.disable()
        
        # 保存分析结果
        pr.dump_stats('profile_results.prof')
        
        # 显示分析结果
        stats = pstats.Stats(pr)
        stats.sort_stats('cumulative')
        
        print("=" * 80)
        print("论文查重系统性能分析报告")
        print("=" * 80)
        
        print("\n最耗时的10个函数:")
        stats.print_stats(10)
        
        print("\n调用次数最多的10个函数:")
        stats.sort_stats('calls')
        stats.print_stats(10)
        
        print("\n每次调用平均耗时最长的10个函数:")
        stats.sort_stats('time')
        stats.print_stats(10)
        
        # 分析内存使用情况
        try:
            import tracemalloc
            print("\n内存使用分析:")
            print("注意: 需要在程序开始时启用tracemalloc.start()来获取详细内存信息")
        except ImportError:
            print("\n内存分析工具未安装，可以安装memory_profiler获取更详细信息")
        
    finally:
        # 恢复原始argv
        sys.argv = original_argv

if __name__ == "__main__":
    profile_main()
