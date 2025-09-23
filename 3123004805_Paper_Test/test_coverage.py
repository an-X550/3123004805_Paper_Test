#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试覆盖率分析脚本
学号: 3123004805
"""

import subprocess
import sys
import os

def run_coverage_analysis():
    """运行测试覆盖率分析"""
    
    print("=" * 80)
    print("📊 论文查重系统 - 测试覆盖率分析")
    print("=" * 80)
    print()
    
    try:
        # 检查是否安装了coverage
        try:
            import coverage
            print("✅ coverage 模块已安装")
        except ImportError:
            print("❌ coverage 模块未安装，正在安装...")
            subprocess.run([sys.executable, "-m", "pip", "install", "coverage"], 
                         check=True, capture_output=True)
            print("✅ coverage 模块安装完成")
        
        print("\n🔍 开始运行测试覆盖率分析...")
        
        # 清理之前的覆盖率数据
        if os.path.exists('.coverage'):
            os.remove('.coverage')
        
        # 运行测试并收集覆盖率数据
        print("\n📋 运行单元测试...")
        result = subprocess.run([
            sys.executable, "-m", "coverage", "run", 
            "--source=main", "test_main.py"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print("❌ 测试执行失败:")
            print(result.stderr)
            return
        
        print("✅ 测试执行成功")
        
        # 生成覆盖率报告
        print("\n📈 生成覆盖率报告...")
        
        # 控制台报告
        report_result = subprocess.run([
            sys.executable, "-m", "coverage", "report", "-m"
        ], capture_output=True, text=True)
        
        if report_result.returncode == 0:
            print("\n📊 覆盖率报告:")
            print("-" * 60)
            print(report_result.stdout)
        
        # HTML报告
        try:
            html_result = subprocess.run([
                sys.executable, "-m", "coverage", "html"
            ], capture_output=True, text=True)
            
            if html_result.returncode == 0:
                print("✅ HTML覆盖率报告已生成到 htmlcov/ 目录")
                print("   打开 htmlcov/index.html 查看详细报告")
            else:
                print("⚠️  HTML报告生成失败")
        except Exception as e:
            print(f"⚠️  HTML报告生成出错: {e}")
        
        # 分析覆盖率数据
        print("\n🎯 覆盖率分析:")
        analyze_coverage_data(report_result.stdout)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 执行失败: {e}")
    except Exception as e:
        print(f"❌ 发生错误: {e}")

def analyze_coverage_data(report_output):
    """分析覆盖率数据"""
    
    lines = report_output.strip().split('\n')
    
    # 寻找总覆盖率
    total_coverage = None
    for line in lines:
        if 'TOTAL' in line:
            parts = line.split()
            if len(parts) >= 4 and parts[-1].endswith('%'):
                total_coverage = parts[-1]
                break
    
    if total_coverage:
        coverage_value = int(total_coverage.rstrip('%'))
        
        print(f"📊 总体覆盖率: {total_coverage}")
        
        if coverage_value >= 90:
            print("🏆 优秀! 覆盖率达到90%以上")
        elif coverage_value >= 80:
            print("✅ 良好! 覆盖率达到80%以上")
        elif coverage_value >= 70:
            print("⚠️  一般，建议提高覆盖率到80%以上")
        else:
            print("❌ 覆盖率偏低，需要增加更多测试用例")
    
    # 分析未覆盖的行
    print("\n📋 覆盖率详细分析:")
    for line in lines:
        if 'main.py' in line:
            parts = line.split()
            if len(parts) >= 6:
                file_name = parts[0]
                statements = parts[1]
                missing = parts[2]
                coverage_pct = parts[3]
                
                print(f"  文件: {file_name}")
                print(f"  语句数: {statements}")
                print(f"  未覆盖: {missing}")
                print(f"  覆盖率: {coverage_pct}")
                
                if len(parts) > 4 and parts[4] != '':
                    print(f"  未覆盖行号: {parts[4]}")
    
    print("\n💡 改进建议:")
    print("1. 为未覆盖的代码行编写对应的测试用例")
    print("2. 测试边界条件和异常情况")
    print("3. 增加集成测试覆盖完整流程")
    print("4. 考虑添加性能测试和压力测试")

def main():
    """主函数"""
    run_coverage_analysis()

if __name__ == "__main__":
    main()
