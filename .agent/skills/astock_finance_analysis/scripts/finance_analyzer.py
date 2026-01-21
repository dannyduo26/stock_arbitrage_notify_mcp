"""
A股公司财务分析模块
使用 akshare 获取财务数据，计算关键财务指标
"""
import logging
from typing import Dict, Any, Optional, List
import pandas as pd

logger = logging.getLogger('finance_analyzer')


class FinanceAnalyzer:
    """A股公司财务分析器"""
    
    def __init__(self, company_name_or_code: str):
        """
        初始化分析器
        
        Args:
            company_name_or_code: 公司名称（如"贵州茅台"）或股票代码（如"600519"）
        """
        self.input_name = company_name_or_code
        self.stock_code: Optional[str] = None
        self.stock_name: Optional[str] = None
        self._init_stock_info()
    
    def _init_stock_info(self):
        """初始化股票信息，将公司名称转换为股票代码"""
        try:
            import akshare as ak
            
            # 如果输入是6位数字，直接作为股票代码
            if self.input_name.isdigit() and len(self.input_name) == 6:
                self.stock_code = self.input_name
                # 获取股票名称
                df = ak.stock_zh_a_spot_em()
                match = df[df['代码'] == self.stock_code]
                if not match.empty:
                    self.stock_name = match.iloc[0]['名称']
                else:
                    self.stock_name = self.input_name
            else:
                # 通过名称查找股票代码
                df = ak.stock_zh_a_spot_em()
                # 精确匹配
                match = df[df['名称'] == self.input_name]
                if match.empty:
                    # 模糊匹配
                    match = df[df['名称'].str.contains(self.input_name, na=False)]
                
                if not match.empty:
                    self.stock_code = match.iloc[0]['代码']
                    self.stock_name = match.iloc[0]['名称']
                else:
                    raise ValueError(f"未找到公司: {self.input_name}")
                    
            logger.info(f"初始化成功: {self.stock_name} ({self.stock_code})")
            
        except Exception as e:
            logger.error(f"初始化失败: {e}")
            raise
    
    def get_basic_info(self) -> Dict[str, Any]:
        """获取公司基本信息"""
        try:
            import akshare as ak
            
            # 获取实时行情
            df = ak.stock_zh_a_spot_em()
            stock_data = df[df['代码'] == self.stock_code]
            
            if stock_data.empty:
                return {"error": "未找到股票数据"}
            
            row = stock_data.iloc[0]
            return {
                "股票代码": self.stock_code,
                "股票名称": self.stock_name,
                "最新价": float(row.get('最新价', 0)),
                "涨跌幅": float(row.get('涨跌幅', 0)),
                "总市值": float(row.get('总市值', 0)),
                "市盈率": float(row.get('市盈率-动态', 0)),
                "市净率": float(row.get('市净率', 0)),
            }
        except Exception as e:
            logger.error(f"获取基本信息失败: {e}")
            return {"error": str(e)}
    
    def get_financial_indicators(self) -> Dict[str, Any]:
        """获取财务指标数据"""
        try:
            import akshare as ak
            
            # 获取主要财务指标
            df = ak.stock_financial_abstract_ths(symbol=self.stock_code, indicator="按报告期")
            
            if df.empty:
                return {"error": "未获取到财务指标数据"}
            
            # 取最近几期数据
            recent_data = df.head(8).to_dict('records')
            
            # 处理数据类型
            processed = []
            for record in recent_data:
                item = {}
                for k, v in record.items():
                    if pd.isna(v):
                        item[k] = None
                    elif hasattr(v, 'item'):
                        item[k] = v.item()
                    else:
                        item[k] = v
                processed.append(item)
            
            return {
                "success": True,
                "data": processed
            }
        except Exception as e:
            logger.error(f"获取财务指标失败: {e}")
            return {"error": str(e)}
    
    def get_profit_statement(self) -> Dict[str, Any]:
        """获取利润表数据"""
        try:
            import akshare as ak
            
            # 获取利润表
            df = ak.stock_profit_sheet_by_report_em(symbol=self.stock_code)
            
            if df.empty:
                return {"error": "未获取到利润表数据"}
            
            # 取最近8期数据
            recent = df.head(8)
            
            # 提取关键字段
            key_fields = ['REPORT_DATE', 'TOTAL_OPERATE_INCOME', 'OPERATE_INCOME', 
                         'OPERATE_COST', 'OPERATE_PROFIT', 'TOTAL_PROFIT', 'NETPROFIT']
            
            available_fields = [f for f in key_fields if f in recent.columns]
            result_df = recent[available_fields].copy()
            
            records = result_df.to_dict('records')
            processed = []
            for record in records:
                item = {}
                for k, v in record.items():
                    if pd.isna(v):
                        item[k] = None
                    elif hasattr(v, 'item'):
                        item[k] = v.item()
                    elif hasattr(v, 'isoformat'):
                        item[k] = str(v)
                    else:
                        item[k] = v
                processed.append(item)
            
            return {"success": True, "data": processed}
            
        except Exception as e:
            logger.error(f"获取利润表失败: {e}")
            return {"error": str(e)}
    
    def get_balance_sheet(self) -> Dict[str, Any]:
        """获取资产负债表数据"""
        try:
            import akshare as ak
            
            # 获取资产负债表
            df = ak.stock_balance_sheet_by_report_em(symbol=self.stock_code)
            
            if df.empty:
                return {"error": "未获取到资产负债表数据"}
            
            recent = df.head(8)
            
            # 提取关键字段
            key_fields = ['REPORT_DATE', 'TOTAL_ASSETS', 'TOTAL_LIAB', 
                         'TOTAL_EQUITY', 'MONETARYFUNDS', 'INVENTORY']
            
            available_fields = [f for f in key_fields if f in recent.columns]
            result_df = recent[available_fields].copy()
            
            records = result_df.to_dict('records')
            processed = []
            for record in records:
                item = {}
                for k, v in record.items():
                    if pd.isna(v):
                        item[k] = None
                    elif hasattr(v, 'item'):
                        item[k] = v.item()
                    elif hasattr(v, 'isoformat'):
                        item[k] = str(v)
                    else:
                        item[k] = v
                processed.append(item)
            
            return {"success": True, "data": processed}
            
        except Exception as e:
            logger.error(f"获取资产负债表失败: {e}")
            return {"error": str(e)}
    
    def calculate_metrics(self) -> Dict[str, Any]:
        """计算关键财务指标"""
        try:
            balance = self.get_balance_sheet()
            profit = self.get_profit_statement()
            
            if "error" in balance or "error" in profit:
                return {"error": "获取财务数据失败"}
            
            # 获取最新一期数据
            latest_balance = balance['data'][0] if balance['data'] else {}
            latest_profit = profit['data'][0] if profit['data'] else {}
            
            total_assets = latest_balance.get('TOTAL_ASSETS', 0) or 0
            total_equity = latest_balance.get('TOTAL_EQUITY', 0) or 0
            total_liab = latest_balance.get('TOTAL_LIAB', 0) or 0
            net_profit = latest_profit.get('NETPROFIT', 0) or 0
            revenue = latest_profit.get('TOTAL_OPERATE_INCOME', 0) or 0
            
            # 计算指标
            metrics = {
                "ROE": round(net_profit / total_equity * 100, 2) if total_equity else 0,
                "ROA": round(net_profit / total_assets * 100, 2) if total_assets else 0,
                "资产负债率": round(total_liab / total_assets * 100, 2) if total_assets else 0,
                "净利率": round(net_profit / revenue * 100, 2) if revenue else 0,
            }
            
            return {"success": True, "metrics": metrics}
            
        except Exception as e:
            logger.error(f"计算指标失败: {e}")
            return {"error": str(e)}


if __name__ == "__main__":
    import json
    
    # 测试代码
    analyzer = FinanceAnalyzer("贵州茅台")
    
    print("=== 基本信息 ===")
    print(json.dumps(analyzer.get_basic_info(), ensure_ascii=False, indent=2))
    
    print("\n=== 财务指标 ===")
    metrics = analyzer.calculate_metrics()
    print(json.dumps(metrics, ensure_ascii=False, indent=2))
