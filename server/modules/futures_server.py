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
    获取国内期货主力合约行情列表（全部数据）
    """
    try:
        # 获取期货主力合约标识
        df = ak.futures_symbol_mark()
        if df is not None and not df.empty:
            # 返回全部数据
            data = df.to_dict(orient='records')
            return {"success": True, "data": data, "count": len(data)}
        return {"success": False, "error": "Failed to fetch main futures list"}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import json
    
    print("=" * 60)
    print("测试期货行情数据模块")
    print("=" * 60)
    
    # 测试1: 获取期货主力合约列表
    print("\n【测试1】获取期货主力合约列表（全部数据）")
    print("-" * 60)
    result = get_futures_main_list()
    if result.get("success"):
        print(f"✅ 成功获取 {result.get('count', 0)} 条主力合约数据")
        print("\n前5条数据预览:")
        for i, item in enumerate(result.get("data", [])[:5], 1):
            print(f"{i}. {item}")
    else:
        print(f"❌ 获取失败: {result.get('error')}")
    
    # 测试2: 获取单个期货合约实时行情
    print("\n" + "=" * 60)
    print("【测试2】获取单个期货合约实时行情")
    print("-" * 60)
    
    # 从主力合约列表中选择一个进行测试
    if result.get("success") and result.get("data"):
        test_symbol = result["data"][0].get("代码", "菜油")
        print(f"测试合约: {test_symbol}")
        print()
        
        realtime_result = get_futures_realtime(test_symbol)
        print(json.dumps(realtime_result, ensure_ascii=False, indent=2))
    else:
        # 如果获取主力合约列表失败，使用默认合约测试
        print("使用默认合约: 菜油")
        print()
        realtime_result = get_futures_realtime("菜油")
        print(json.dumps(realtime_result, ensure_ascii=False, indent=2))
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)
