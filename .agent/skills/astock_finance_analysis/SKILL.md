---
name: astock_finance_analysis
description: 使用 akshare、pandas、matplotlib、pillow 分析A股公司财务状况，生成多维度可视化图表
---

# A股公司财务分析技能

基于A股公司名称获取财务数据并生成多维度可视化图表。

## 依赖库

- **akshare**: A股数据获取
- **pandas**: 数据处理
- **matplotlib**: 图表生成
- **pillow**: 图像处理

## 使用方法

### 1. 安装依赖

```powershell
pip install akshare pandas matplotlib pillow
```

### 2. 运行财务分析

```powershell
cd e:\OpenSource\stock\stock_arbitrage\mcp
python .agent\skills\astock_finance_analysis\scripts\generate_report.py "贵州茅台"
```

### 3. 编程调用

```python
from scripts.finance_analyzer import FinanceAnalyzer
from scripts.chart_generator import ChartGenerator

# 初始化分析器（支持公司名称或股票代码）
analyzer = FinanceAnalyzer("贵州茅台")  # 或 "600519"
print(analyzer.get_basic_info())

# 生成图表
generator = ChartGenerator(analyzer)
generator.generate_all(output_dir="./output")
```

## 生成的图表

| 图表类型       | 文件名                | 说明                 |
| -------------- | --------------------- | -------------------- |
| 财务趋势图     | `trend.png`           | 营收、净利润历年变化 |
| 盈利能力雷达图 | `radar.png`           | ROE、ROA、毛利率等   |
| 资产结构饼图   | `asset_structure.png` | 资产负债分布         |
| 综合评分图     | `score.png`           | 财务健康度评分       |

## 核心模块

- `scripts/finance_analyzer.py`: 财务数据获取与指标计算
- `scripts/chart_generator.py`: 可视化图表生成
- `scripts/generate_report.py`: 命令行生成报告脚本
