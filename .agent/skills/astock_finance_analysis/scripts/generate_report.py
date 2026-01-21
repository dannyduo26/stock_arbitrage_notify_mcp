#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A股公司财务报告生成脚本
命令行运行：python generate_report.py "公司名称或代码"
"""
import sys
import os
import json
import logging

# 添加脚本目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from finance_analyzer import FinanceAnalyzer
from chart_generator import ChartGenerator

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('generate_report')


def generate_report(company_name: str, output_dir: str = None) -> dict:
    """
    生成公司财务分析报告
    
    Args:
        company_name: 公司名称或股票代码
        output_dir: 输出目录，默认为当前目录下的 output/<公司名称>
        
    Returns:
        包含分析结果和图表路径的字典
    """
    logger.info(f"开始分析: {company_name}")
    
    # 初始化分析器
    analyzer = FinanceAnalyzer(company_name)
    
    # 设置输出目录
    if output_dir is None:
        output_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..", "examples", "sample_output",
            f"{analyzer.stock_name}_{analyzer.stock_code}"
        )
    
    os.makedirs(output_dir, exist_ok=True)
    logger.info(f"输出目录: {output_dir}")
    
    # 获取基本信息
    basic_info = analyzer.get_basic_info()
    logger.info(f"基本信息: {basic_info}")
    
    # 计算财务指标
    metrics = analyzer.calculate_metrics()
    logger.info(f"财务指标: {metrics}")
    
    # 生成图表
    generator = ChartGenerator(analyzer)
    charts = generator.generate_all(output_dir)
    
    # 汇总结果
    result = {
        "公司名称": analyzer.stock_name,
        "股票代码": analyzer.stock_code,
        "基本信息": basic_info,
        "财务指标": metrics.get('metrics', {}),
        "生成图表": charts,
        "输出目录": output_dir,
    }
    
    # 保存JSON报告
    report_path = os.path.join(output_dir, "report.json")
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    logger.info(f"报告已保存: {report_path}")
    
    return result


def main():
    """主入口"""
    if len(sys.argv) < 2:
        print("用法: python generate_report.py <公司名称或代码>")
        print("示例: python generate_report.py 贵州茅台")
        print("      python generate_report.py 600519")
        sys.exit(1)
    
    company_name = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        result = generate_report(company_name, output_dir)
        
        print("\n" + "=" * 50)
        print(f"📊 {result['公司名称']}({result['股票代码']}) 财务分析报告")
        print("=" * 50)
        
        print("\n📈 基本信息:")
        info = result['基本信息']
        if 'error' not in info:
            print(f"  最新价: {info.get('最新价', 'N/A')} 元")
            print(f"  涨跌幅: {info.get('涨跌幅', 'N/A')}%")
            print(f"  总市值: {info.get('总市值', 0) / 1e8:.2f} 亿")
            print(f"  市盈率: {info.get('市盈率', 'N/A')}")
            print(f"  市净率: {info.get('市净率', 'N/A')}")
        
        print("\n💰 财务指标:")
        metrics = result['财务指标']
        if metrics:
            for key, value in metrics.items():
                print(f"  {key}: {value}%")
        
        print("\n📁 生成的图表:")
        for name, path in result['生成图表'].items():
            print(f"  {name}: {path}")
        
        print(f"\n✅ 报告已保存到: {result['输出目录']}")
        
    except Exception as e:
        logger.error(f"生成报告失败: {e}", exc_info=True)
        print(f"\n❌ 错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
