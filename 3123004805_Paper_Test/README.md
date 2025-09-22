# 论文查重系统

**学号**: 3123004805

## 项目简介

基于余弦相似度算法的论文查重系统，能够检测两篇文档之间的相似程度。

## 使用方法

### 基本用法

```bash
python main.py [原文文件] [抄袭版文件] [结果文件]
```

### 示例

```bash
python main.py orig.txt orig_0.8_add.txt result.txt
```

执行后，结果文件中将包含相似度百分比（保留两位小数）。

## 测试数据

项目包含以下测试文件：

- `orig.txt` - 原文文档
- `orig_0.8_add.txt` - 增加内容版本
- `orig_0.8_del.txt` - 删除内容版本  
- `orig_0.8_dis_1.txt` - 替换1%内容版本
- `orig_0.8_dis_10.txt` - 替换10%内容版本
- `orig_0.8_dis_15.txt` - 替换15%内容版本

## 运行测试

```bash
python test_main.py          # 完整测试 (15个用例)
python test_simple.py        # 简化测试 (4个用例)
```

## 算法说明

使用余弦相似度算法计算文档相似度：

```
similarity = (A · B) / (|A| × |B|)
```

其中A、B为两个文档的词频向量。

## 项目文件

- `main.py` - 完整版主程序
- `main_simple.py` - 简化版主程序
- `test_main.py` - 完整版单元测试
- `test_simple.py` - 简化版单元测试
- `requirements.txt` - 依赖包列表

## 系统要求

- Python 3.7+
- 支持中英文混合文档处理