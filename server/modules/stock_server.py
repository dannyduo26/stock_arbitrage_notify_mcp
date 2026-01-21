"""
A股实时行情数据服务
使用 akshare 获取单只股票的实时行情数据
"""
import json
from typing import Dict, Any, Optional
import logging

# 配置日志
logger = logging.getLogger('stock_server')

def get_stock_realtime(symbol: str) -> Dict[str, Any]:
    """
    获取单只A股的实时行情数据
    
    Args:
        symbol: 股票代码，格式如 "000001" 或 "600000"
    
    Returns:
        包含实时行情数据的字典
    """
    try:
        import akshare as ak
    except ImportError:
        logger.error("akshare 库未安装")
        return {
            "error": "akshare 库未安装",
            "symbol": symbol
        }
    
    try:
        # 验证股票代码格式（6位数字）
        if not symbol or len(symbol) != 6 or not symbol.isdigit():
            return {
                "error": f"股票代码格式错误，应为6位数字，当前输入: {symbol}",
                "symbol": symbol
            }
        
        logger.info(f"开始获取股票 {symbol} 的实时行情数据")
        
        # 调用 akshare 获取实时行情
        # stock_zh_a_spot_em 返回的是所有A股的实时行情
        # 我们需要筛选出指定的股票
        df = ak.stock_zh_a_spot_em()
        
        # 过滤出指定股票代码
        stock_data = df[df['代码'] == symbol]
        
        if stock_data.empty:
            logger.warning(f"未找到股票代码 {symbol} 的数据")
            return {
                "error": f"未找到股票代码 {symbol} 的数据",
                "symbol": symbol
            }
        
        # 转换为字典格式
        result = stock_data.iloc[0].to_dict()
        
        # 将数值类型转换为 Python 原生类型（避免 JSON 序列化问题）
        processed_result = {}
        for key, value in result.items():
            # 处理 pandas 的数据类型
            if hasattr(value, 'item'):
                processed_result[key] = value.item()
            else:
                processed_result[key] = value
        
        logger.info(f"成功获取股票 {symbol} 的实时行情数据")
        return {
            "success": True,
            "symbol": symbol,
            "data": processed_result
        }
        
    except Exception as e:
        error_msg = f"获取股票 {symbol} 实时行情时发生错误: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            "error": error_msg,
            "symbol": symbol
        }


def get_stock_hist(symbol: str, period: str = "daily", adjust: str = "") -> Dict[str, Any]:
    """
    获取单只A股的历史行情数据
    
    Args:
        symbol: 股票代码，格式如 "000001" 或 "600000"
        period: 周期，可选 "daily"(日), "weekly"(周), "monthly"(月)
        adjust: 复权类型，可选 ""(不复权), "qfq"(前复权), "hfq"(后复权)
    
    Returns:
        包含历史行情数据的字典
    """
    try:
        import akshare as ak
    except ImportError:
        logger.error("akshare 库未安装")
        return {
            "error": "akshare 库未安装",
            "symbol": symbol
        }
    
    try:
        # 验证股票代码格式
        if not symbol or len(symbol) != 6 or not symbol.isdigit():
            return {
                "error": f"股票代码格式错误，应为6位数字，当前输入: {symbol}",
                "symbol": symbol
            }
        
        logger.info(f"开始获取股票 {symbol} 的历史行情数据，周期: {period}")
        
        # 调用 akshare 获取历史行情
        df = ak.stock_zh_a_hist(symbol=symbol, period=period, adjust='qfq')
        
        if df.empty:
            logger.warning(f"未找到股票代码 {symbol} 的历史数据")
            return {
                "error": f"未找到股票代码 {symbol} 的历史数据",
                "symbol": symbol
            }
        
        # 转换为字典列表格式（只返回最近10条记录）
        records = df.tail(10).to_dict('records')
        
        # 处理数据类型
        processed_records = []
        for record in records:
            processed_record = {}
            for key, value in record.items():
                if hasattr(value, 'item'):
                    processed_record[key] = value.item()
                elif hasattr(value, 'isoformat'):  # 处理日期类型
                    processed_record[key] = value.isoformat()
                else:
                    processed_record[key] = value
            processed_records.append(processed_record)
        
        logger.info(f"成功获取股票 {symbol} 的历史行情数据，返回 {len(processed_records)} 条记录")
        return {
            "success": True,
            "symbol": symbol,
            "period": period,
            "adjust": adjust,
            "count": len(processed_records),
            "data": processed_records
        }
        
    except Exception as e:
        error_msg = f"获取股票 {symbol} 历史行情时发生错误: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            "error": error_msg,
            "symbol": symbol
        }


if __name__ == "__main__":
    # 测试代码
    # 测试获取平安银行(000001)的实时行情
    print("=== 测试实时行情 ===")
    result = get_stock_realtime("000001")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    print("\n=== 测试历史行情 ===")
    result = get_stock_hist("000001", period="daily", adjust="qfq")
    print(json.dumps(result, ensure_ascii=False, indent=2))
