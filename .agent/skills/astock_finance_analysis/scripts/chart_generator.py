"""
A股公司财务可视化图表生成模块
使用 matplotlib 生成多维度财务分析图表
"""
import os
import logging
from typing import Dict, Any, List, Optional
import matplotlib.pyplot as plt
import matplotlib
import numpy as np

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
matplotlib.rcParams['axes.unicode_minus'] = False

logger = logging.getLogger('chart_generator')


class ChartGenerator:
    """财务图表生成器"""
    
    def __init__(self, analyzer):
        """
        初始化图表生成器
        
        Args:
            analyzer: FinanceAnalyzer 实例
        """
        self.analyzer = analyzer
        self.stock_name = analyzer.stock_name
        self.stock_code = analyzer.stock_code
    
    def generate_all(self, output_dir: str = "./output") -> Dict[str, str]:
        """
        生成所有图表
        
        Args:
            output_dir: 输出目录
            
        Returns:
            生成的图表文件路径字典
        """
        os.makedirs(output_dir, exist_ok=True)
        
        charts = {}
        
        # 生成各类图表
        try:
            charts['trend'] = self.generate_trend_chart(output_dir)
        except Exception as e:
            logger.error(f"生成趋势图失败: {e}")
            
        try:
            charts['radar'] = self.generate_radar_chart(output_dir)
        except Exception as e:
            logger.error(f"生成雷达图失败: {e}")
            
        try:
            charts['asset_structure'] = self.generate_asset_pie_chart(output_dir)
        except Exception as e:
            logger.error(f"生成资产结构图失败: {e}")
            
        try:
            charts['score'] = self.generate_score_chart(output_dir)
        except Exception as e:
            logger.error(f"生成评分图失败: {e}")
        
        return charts
    
    def generate_trend_chart(self, output_dir: str) -> str:
        """生成财务趋势图（营收、净利润）"""
        profit_data = self.analyzer.get_profit_statement()
        
        if "error" in profit_data:
            raise ValueError(profit_data["error"])
        
        data = profit_data['data']
        
        # 提取数据（倒序显示，从早到晚）
        dates = [str(d.get('REPORT_DATE', ''))[:10] for d in data][::-1]
        revenue = [float(d.get('TOTAL_OPERATE_INCOME', 0) or 0) / 1e8 for d in data][::-1]
        net_profit = [float(d.get('NETPROFIT', 0) or 0) / 1e8 for d in data][::-1]
        
        # 创建图表
        fig, ax1 = plt.subplots(figsize=(12, 6))
        
        x = np.arange(len(dates))
        width = 0.35
        
        # 柱状图 - 营收
        bars1 = ax1.bar(x - width/2, revenue, width, label='营业收入', color='#4285f4', alpha=0.8)
        bars2 = ax1.bar(x + width/2, net_profit, width, label='净利润', color='#34a853', alpha=0.8)
        
        ax1.set_xlabel('报告期', fontsize=12)
        ax1.set_ylabel('金额（亿元）', fontsize=12)
        ax1.set_title(f'{self.stock_name}({self.stock_code}) 财务趋势', fontsize=14, fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(dates, rotation=45, ha='right')
        ax1.legend(loc='upper left')
        ax1.grid(axis='y', alpha=0.3)
        
        # 添加数值标签
        for bar in bars1:
            height = bar.get_height()
            ax1.annotate(f'{height:.1f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3), textcoords="offset points",
                        ha='center', va='bottom', fontsize=8)
        
        plt.tight_layout()
        
        output_path = os.path.join(output_dir, 'trend.png')
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        logger.info(f"趋势图已保存: {output_path}")
        return output_path
    
    def generate_radar_chart(self, output_dir: str) -> str:
        """生成盈利能力雷达图"""
        metrics_data = self.analyzer.calculate_metrics()
        
        if "error" in metrics_data:
            raise ValueError(metrics_data["error"])
        
        metrics = metrics_data['metrics']
        
        # 雷达图数据
        categories = ['ROE', 'ROA', '资产负债率', '净利率']
        values = [
            min(abs(metrics.get('ROE', 0)), 50),  # 限制最大值
            min(abs(metrics.get('ROA', 0)), 30),
            min(abs(metrics.get('资产负债率', 0)), 100),
            min(abs(metrics.get('净利率', 0)), 50),
        ]
        
        # 闭合雷达图
        values += values[:1]
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]
        
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
        
        # 绘制雷达图
        ax.fill(angles, values, color='#4285f4', alpha=0.25)
        ax.plot(angles, values, color='#4285f4', linewidth=2, marker='o')
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=12)
        ax.set_title(f'{self.stock_name} 盈利能力分析', fontsize=14, fontweight='bold', pad=20)
        
        # 添加数值标注
        for angle, value, cat in zip(angles[:-1], values[:-1], categories):
            ax.annotate(f'{value:.1f}%', xy=(angle, value), fontsize=10,
                       ha='center', va='bottom')
        
        output_path = os.path.join(output_dir, 'radar.png')
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        logger.info(f"雷达图已保存: {output_path}")
        return output_path
    
    def generate_asset_pie_chart(self, output_dir: str) -> str:
        """生成资产结构饼图"""
        balance_data = self.analyzer.get_balance_sheet()
        
        if "error" in balance_data:
            raise ValueError(balance_data["error"])
        
        data = balance_data['data'][0] if balance_data['data'] else {}
        
        total_equity = float(data.get('TOTAL_EQUITY', 0) or 0) / 1e8
        total_liab = float(data.get('TOTAL_LIAB', 0) or 0) / 1e8
        
        # 创建饼图
        fig, ax = plt.subplots(figsize=(10, 8))
        
        sizes = [total_equity, total_liab]
        labels = [f'股东权益\n{total_equity:.1f}亿', f'负债\n{total_liab:.1f}亿']
        colors = ['#34a853', '#ea4335']
        explode = (0.05, 0)
        
        wedges, texts, autotexts = ax.pie(sizes, explode=explode, labels=labels, colors=colors,
                                          autopct='%1.1f%%', shadow=True, startangle=90,
                                          textprops={'fontsize': 12})
        
        ax.set_title(f'{self.stock_name} 资产结构', fontsize=14, fontweight='bold')
        ax.axis('equal')
        
        output_path = os.path.join(output_dir, 'asset_structure.png')
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        logger.info(f"资产结构图已保存: {output_path}")
        return output_path
    
    def generate_score_chart(self, output_dir: str) -> str:
        """生成财务健康评分图"""
        metrics_data = self.analyzer.calculate_metrics()
        basic_info = self.analyzer.get_basic_info()
        
        if "error" in metrics_data:
            raise ValueError(metrics_data["error"])
        
        metrics = metrics_data['metrics']
        
        # 计算各维度得分（0-100）
        roe = metrics.get('ROE', 0)
        roa = metrics.get('ROA', 0)
        debt_ratio = metrics.get('资产负债率', 0)
        net_margin = metrics.get('净利率', 0)
        
        scores = {
            '盈利能力': min(max(roe * 3, 0), 100),
            '资产效率': min(max(roa * 5, 0), 100),
            '财务安全': max(100 - debt_ratio, 0),
            '利润质量': min(max(net_margin * 2, 0), 100),
        }
        
        # 总分
        total_score = sum(scores.values()) / len(scores)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # 左侧：各维度得分条形图
        categories = list(scores.keys())
        values = list(scores.values())
        colors = ['#4285f4', '#34a853', '#fbbc04', '#ea4335']
        
        bars = ax1.barh(categories, values, color=colors, alpha=0.8)
        ax1.set_xlim(0, 100)
        ax1.set_xlabel('得分', fontsize=12)
        ax1.set_title('各维度评分', fontsize=14, fontweight='bold')
        ax1.axvline(x=60, color='gray', linestyle='--', alpha=0.5, label='及格线')
        
        for bar, val in zip(bars, values):
            ax1.text(val + 2, bar.get_y() + bar.get_height()/2, f'{val:.0f}',
                    va='center', fontsize=11)
        
        # 右侧：综合评分仪表盘
        theta = np.linspace(0, np.pi, 100)
        r = 0.8
        ax2.plot(r * np.cos(theta), r * np.sin(theta), 'k-', linewidth=2)
        
        # 评分指针
        score_angle = np.pi * (1 - total_score / 100)
        ax2.arrow(0, 0, 0.6 * np.cos(score_angle), 0.6 * np.sin(score_angle),
                 head_width=0.08, head_length=0.05, fc='#ea4335', ec='#ea4335')
        
        # 刻度
        for i in range(0, 101, 20):
            angle = np.pi * (1 - i / 100)
            ax2.text(0.9 * np.cos(angle), 0.9 * np.sin(angle), str(i),
                    ha='center', va='center', fontsize=10)
        
        ax2.text(0, -0.2, f'{total_score:.0f}分', ha='center', fontsize=24, fontweight='bold')
        ax2.text(0, -0.4, self._get_rating(total_score), ha='center', fontsize=14)
        ax2.set_xlim(-1.2, 1.2)
        ax2.set_ylim(-0.6, 1.1)
        ax2.set_aspect('equal')
        ax2.axis('off')
        ax2.set_title(f'{self.stock_name} 财务健康度', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        output_path = os.path.join(output_dir, 'score.png')
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        logger.info(f"评分图已保存: {output_path}")
        return output_path
    
    def _get_rating(self, score: float) -> str:
        """根据分数返回评级"""
        if score >= 80:
            return "优秀 ⭐⭐⭐⭐⭐"
        elif score >= 60:
            return "良好 ⭐⭐⭐⭐"
        elif score >= 40:
            return "一般 ⭐⭐⭐"
        elif score >= 20:
            return "较差 ⭐⭐"
        else:
            return "风险 ⭐"


if __name__ == "__main__":
    from finance_analyzer import FinanceAnalyzer
    
    analyzer = FinanceAnalyzer("贵州茅台")
    generator = ChartGenerator(analyzer)
    
    charts = generator.generate_all("./output")
    print("生成的图表:")
    for name, path in charts.items():
        print(f"  {name}: {path}")
