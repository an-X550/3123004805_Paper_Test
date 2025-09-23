#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码质量检查脚本
学号: 3123004805
"""

import ast
import os
import re
from typing import List, Dict, Tuple

def analyze_code_quality(file_path: str) -> Dict[str, any]:
    """分析代码质量"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 解析AST
    tree = ast.parse(content)
    
    # 分析结果
    results = {
        'file_size': len(content),
        'line_count': len(content.split('\n')),
        'function_count': 0,
        'class_count': 0,
        'docstring_coverage': 0,
        'complexity_score': 0,
        'type_hints_coverage': 0,
        'issues': []
    }
    
    # 统计函数和类
    functions = []
    classes = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions.append(node)
            results['function_count'] += 1
        elif isinstance(node, ast.ClassDef):
            classes.append(node)
            results['class_count'] += 1
    
    # 检查文档字符串覆盖率
    functions_with_docstring = 0
    for func in functions:
        if ast.get_docstring(func):
            functions_with_docstring += 1
    
    if functions:
        results['docstring_coverage'] = (functions_with_docstring / len(functions)) * 100
    
    # 检查类型提示覆盖率
    functions_with_hints = 0
    for func in functions:
        has_return_hint = func.returns is not None
        has_arg_hints = any(arg.annotation is not None for arg in func.args.args)
        if has_return_hint or has_arg_hints:
            functions_with_hints += 1
    
    if functions:
        results['type_hints_coverage'] = (functions_with_hints / len(functions)) * 100
    
    # 简单的复杂度分析（基于嵌套层数）
    max_depth = 0
    for node in ast.walk(tree):
        depth = get_node_depth(node, tree)
        max_depth = max(max_depth, depth)
    
    results['complexity_score'] = max_depth
    
    # 检查常见问题
    results['issues'] = check_code_issues(content)
    
    return results

def get_node_depth(node, tree) -> int:
    """获取节点嵌套深度"""
    depth = 0
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            if child is node:
                depth += 1
                break
    return depth

def check_code_issues(content: str) -> List[str]:
    """检查代码问题"""
    issues = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines, 1):
        # 检查行长度
        if len(line) > 88:
            issues.append(f"第{i}行过长 ({len(line)}字符)")
        
        # 检查TODO/FIXME
        if 'TODO' in line or 'FIXME' in line:
            issues.append(f"第{i}行包含TODO/FIXME")
        
        # 检查硬编码的数字
        magic_numbers = re.findall(r'\b\d{2,}\b', line)
        for num in magic_numbers:
            if int(num) > 10 and 'line' not in line.lower():
                issues.append(f"第{i}行可能包含数字: {num}")
    
    return issues

def generate_quality_report(file_path: str):
    """生成代码质量报告"""
    
    print("=" * 80)
    print("论文查重系统 - 代码质量分析报告")
    print("=" * 80)
    print()
    
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return
    
    try:
        results = analyze_code_quality(file_path)
        
        print(f"分析文件: {file_path}")
        print(f"文件大小: {results['file_size']} 字符")
        print(f"代码行数: {results['line_count']} 行")
        print(f"函数数量: {results['function_count']} 个")
        print(f"类数量: {results['class_count']} 个")
        print()
        
        # 质量指标
        print("质量指标:")
        print("-" * 40)
        
        docstring_score = results['docstring_coverage']
        print(f"文档字符串覆盖率: {docstring_score:.1f}%", end="")
        if docstring_score >= 90:
            print(" 优秀")
        elif docstring_score >= 70:
            print(" 良好")
        else:
            print(" 需改进")
        
        hints_score = results['type_hints_coverage']
        print(f"类型提示覆盖率: {hints_score:.1f}%", end="")
        if hints_score >= 90:
            print(" 优秀")
        elif hints_score >= 70:
            print(" 良好")
        else:
            print(" 需改进")
        
        complexity = results['complexity_score']
        print(f"代码复杂度: {complexity}", end="")
        if complexity <= 5:
            print(" 简单")
        elif complexity <= 10:
            print("  中等")
        else:
            print(" 复杂")
        
        print()
        
        # 问题列表
        issues = results['issues']
        if issues:
            print("发现的问题:")
            print("-" * 40)
            for issue in issues[:10]:  # 只显示前10个问题
                print(f"  • {issue}")
            
            if len(issues) > 10:
                print(f"  ... 还有 {len(issues) - 10} 个问题")
        else:
            print("未发现明显问题")
        
        print()
        
        # 总体评分
        total_score = calculate_total_score(results)
        print(f"总体评分: {total_score:.1f}/100")
        
        if total_score >= 90:
            print("代码质量优秀！")
        elif total_score >= 80:
            print("代码质量良好")
        elif total_score >= 70:
            print(" 代码质量一般，建议改进")
        else:
            print("代码质量需要大幅改进")
        
        print()
        print("改进建议:")
        print("-" * 40)
        
        if docstring_score < 90:
            print("  • 为所有函数添加完整的文档字符串")
        
        if hints_score < 90:
            print("  • 为函数参数和返回值添加类型提示")
        
        if complexity > 5:
            print("  • 考虑将复杂函数拆分为更小的函数")
        
        if len(issues) > 0:
            print("  • 修复代码中发现的问题")
        
        print("  • 使用专业工具进行更详细的分析")
        
    except Exception as e:
        print(f"分析失败: {e}")

def calculate_total_score(results: Dict[str, any]) -> float:
    """计算总体评分"""
    
    # 权重分配
    weights = {
        'docstring': 0.3,
        'type_hints': 0.3,
        'complexity': 0.2,
        'issues': 0.2
    }
    
    # 各项得分
    docstring_score = results['docstring_coverage']
    hints_score = results['type_hints_coverage']
    
    # 复杂度得分（反向）
    complexity = results['complexity_score']
    complexity_score = max(0, 100 - complexity * 10)
    
    # 问题得分（反向）
    issues_count = len(results['issues'])
    issues_score = max(0, 100 - issues_count * 5)
    
    # 加权总分
    total_score = (
        docstring_score * weights['docstring'] +
        hints_score * weights['type_hints'] +
        complexity_score * weights['complexity'] +
        issues_score * weights['issues']
    )
    
    return total_score

def main():
    """主函数"""
    generate_quality_report('main.py')

if __name__ == "__main__":
    main()
