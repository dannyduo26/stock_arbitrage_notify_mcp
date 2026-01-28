import akshare as ak
import pandas as pd
import logging
from typing import Dict, Any, List

logger = logging.getLogger('arbitrage-suite')

def get_futures_realtime(symbol: str) -> Dict[str, Any]:
    """
    使用 akshare 获取国内期货实时行情数据
    
    Args:
        symbol: 期货合约代码，如 "RB2505", "AG2604"
        
    Returns:
        Dict 包含行情数据或错误信息
    """
    try:
        symbol = symbol.upper()
        # akshare 的 futures_zh_realtime 接口
        df = ak.futures_zh_realtime(symbol=symbol)
        
        if df is not None and not df.empty:
            data = df.to_dict(orient='records')[0]
            # 标准化输出
            return {
                "success": True,
                "symbol": symbol,
                "name": data.get('name', ''),
                "price": float(data.get('last', 0)),
                "open": float(data.get('open', 0)),
                "high": float(data.get('high', 0)),
                "low": float(data.get('low', 0)),
                "volume": int(data.get('volume', 0)),
                "position": int(data.get('hold', data.get('position', 0))),
                "time": data.get('time', '')
            }
        else:
            # 尝试 display_main 作为备选
            df_main = ak.futures_display_main_sina()
            if df_main is not None:
                # 注意：列名可能是中文
                match = df_main[df_main['代码'] == symbol]
                if not match.empty:
                    row = match.iloc[0].to_dict()
                    return {
                        "success": True,
                        "symbol": symbol,
                        "name": row.get('名称', symbol),
                        "price": float(row.get('最新价', 0)),
                        "change": float(row.get('涨跌', 0)),
                        "volume": int(row.get('成交量', 0))
                    }
            
            return {"success": False, "error": f"No data found for symbol {symbol}"}
            
    except Exception as e:
        logger.error(f"Error fetching futures data for {symbol}: {str(e)}")
        return {"success": False, "error": str(e)}

def get_futures_main_list() -> Dict[str, Any]:
    """
    获取国内期货主力合约行情列表
    """
    try:
        df = ak.futures_display_main_sina()
        if df is not None and not df.empty:
            # 只取前 20 条避免返回过多
            data = df.head(20).to_dict(orient='records')
            return {"success": True, "data": data}
        return {"success": False, "error": "Failed to fetch main futures list"}
    except Exception as e:
        return {"success": False, "error": str(e)}
