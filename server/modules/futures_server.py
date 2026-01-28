import akshare as ak
import pandas as pd
import logging
from typing import Dict, Any, List

logger = logging.getLogger('arbitrage-suite')

def get_futures_realtime(symbol: str, market: str = "CF") -> Dict[str, Any]:
    """
    使用 akshare 获取国内期货实时行情数据
    
    Args:
        symbol: 期货合约代码，如 "V2205"（PVC2205）, "ZC2505"（动力煤2505）
        market: 市场类型，"CF"表示商品期货，"FF"表示金融期货，默认"CF"
        
    Returns:
        Dict 包含行情数据或错误信息
    """
    try:
        symbol = symbol.upper()
        # akshare 的 futures_zh_spot 接口
        # 目标地址: https://finance.sina.com.cn/futuremarket/
        df = ak.futures_zh_spot(symbol=symbol, market=market, adjust='0')
        
        if df is not None and not df.empty:
            # 返回列表格式，与 get_futures_main_list 保持一致
            data = df.to_dict(orient='records')
            return {"success": True, "data": data, "count": len(data)}
        else:
            return {"success": False, "error": f"No data found for symbol {symbol}"}
            
    except Exception as e:
        logger.error(f"Error fetching futures data for {symbol}: {str(e)}")
        return {"success": False, "error": str(e)}

def get_futures_main_list() -> Dict[str, Any]:
    """
    获取国内期货主力合约行情列表（全部数据）
    使用 futures_zh_spot 获取所有商品期货（大商所、上期所、郑商所、广期所）和金融期货（中金所）主力合约实时行情
    """
    try:
        # 获取各交易所主力合约代码
        dce_text = ak.match_main_contract(symbol="dce")      # 大连商品交易所
        czce_text = ak.match_main_contract(symbol="czce")    # 郑州商品交易所
        shfe_text = ak.match_main_contract(symbol="shfe")    # 上海期货交易所
        gfex_text = ak.match_main_contract(symbol="gfex")    # 广州期货交易所
        cffex_text = ak.match_main_contract(symbol="cffex")  # 中国金融期货交易所
        
        # 订阅所有商品期货主力合约
        cf_df = ak.futures_zh_spot(
            symbol=",".join([dce_text, czce_text, shfe_text, gfex_text]),
            market="CF",
            adjust='0'
        )
        
        # 订阅所有金融期货主力合约
        ff_df = ak.futures_zh_spot(
            symbol=cffex_text,
            market="FF",
            adjust='0'
        )
        
        # 合并商品期货和金融期货数据
        all_data = []
        if cf_df is not None and not cf_df.empty:
            all_data.extend(cf_df.to_dict(orient='records'))
        if ff_df is not None and not ff_df.empty:
            all_data.extend(ff_df.to_dict(orient='records'))
        
        if all_data:
            return {"success": True, "data": all_data, "count": len(all_data)}
        return {"success": False, "error": "Failed to fetch main futures list"}
    except Exception as e:
        logger.error(f"Error fetching futures main list: {str(e)}")
        return {"success": False, "error": str(e)}

def get_futures_financial_list() -> Dict[str, Any]:
    """
    获取国内金融期货主力合约行情列表（中金所）
    使用 futures_zh_spot 获取中金所所有金融期货主力合约实时行情
    """
    try:
        # 获取中金所主力合约代码
        cffex_text = ak.match_main_contract(symbol="cffex")  # 中国金融期货交易所
        
        # 订阅所有金融期货主力合约
        df = ak.futures_zh_spot(
            symbol=cffex_text,
            market="FF",
            adjust='0'
        )
        
        if df is not None and not df.empty:
            # 返回全部数据
            data = df.to_dict(orient='records')
            return {"success": True, "data": data, "count": len(data)}
        return {"success": False, "error": "Failed to fetch financial futures list"}
    except Exception as e:
        logger.error(f"Error fetching financial futures list: {str(e)}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import json
    
    print("=" * 60)
    print("测试期货行情数据模块")
    print("=" * 60)
    
    # 测试1: 获取期货主力合约列表（商品+金融）
    print("\n【测试1】获取期货主力合约列表（商品期货+金融期货全部数据）")
    print("-" * 60)
    result = get_futures_main_list()
    if result.get("success"):
        print(f"✅ 成功获取 {result.get('count', 0)} 条主力合约数据")
        print("\n前10条数据预览:")
        for i, item in enumerate(result.get("data", [])[:10], 1):
            print(f"{i}. {item}")
    else:
        print(f"❌ 获取失败: {result.get('error')}")
    
    # 测试1.1: 单独获取金融期货列表
    print("\n" + "=" * 60)
    print("【测试1.1】获取金融期货主力合约列表（仅中金所）")
    print("-" * 60)
    ff_result = get_futures_financial_list()
    if ff_result.get("success"):
        print(f"✅ 成功获取 {ff_result.get('count', 0)} 条金融期货主力合约数据")
        print("\n全部金融期货数据:")
        for i, item in enumerate(ff_result.get("data", []), 1):
            print(f"{i}. {item}")
    else:
        print(f"❌ 获取失败: {ff_result.get('error')}")
    
    # 测试菜油
    print("\n测试合约: V2605")
    print("-" * 40)
    realtime_result = get_futures_realtime("V2605", market="CF")
    if realtime_result.get("success"):
        print(f"✅ 成功获取 {realtime_result.get('count', 0)} 条主力合约数据")
        print("\n前10条数据预览:")
        for i, item in enumerate(realtime_result.get("data", [])[:10], 1):
            print(f"{i}. {item}")
    else:
        print(f"❌ 获取失败: {realtime_result.get('error')}")
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)
