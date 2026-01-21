"""
测试股票行情 MCP 工具
"""
import sys
import os

# 将项目根目录添加到路径（tests 的父目录）
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.modules import stock_server as s
import json


def test_get_stock_realtime():
    """测试获取股票实时行情"""
    print("=" * 60)
    print("测试获取股票实时行情")
    print("=" * 60)
    
    # 测试平安银行 000001
    print("\n1. 测试平安银行(000001):")
    result = s.get_stock_realtime("000001")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 测试贵州茅台 600519
    print("\n2. 测试贵州茅台(600519):")
    result = s.get_stock_realtime("600519")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 测试错误的股票代码
    print("\n3. 测试错误的股票代码(999999):")
    result = s.get_stock_realtime("999999")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 测试格式错误的股票代码
    print("\n4. 测试格式错误的股票代码(abc):")
    result = s.get_stock_realtime("abc")
    print(json.dumps(result, ensure_ascii=False, indent=2))


def test_get_stock_hist():
    """测试获取股票历史行情"""
    print("\n" + "=" * 60)
    print("测试获取股票历史行情")
    print("=" * 60)
    
    # 测试日K线，不复权
    print("\n1. 测试平安银行(000001)日K线，不复权:")
    result = s.get_stock_hist("000001", period="daily", adjust="")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 测试日K线，前复权
    print("\n2. 测试平安银行(000001)日K线，前复权:")
    result = s.get_stock_hist("000001", period="daily", adjust="qfq")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 测试周K线
    print("\n3. 测试贵州茅台(600519)周K线:")
    result = s.get_stock_hist("600519", period="weekly", adjust="")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    # 先测试实时行情
    test_get_stock_realtime()
    
    # 再测试历史行情
    test_get_stock_hist()
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
