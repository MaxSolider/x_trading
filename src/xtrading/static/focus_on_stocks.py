"""
重点关注股票
"""

# 重点关注股票列表
FOCUS_ON_STOCKS = [
    "银之杰",
    "高新发展",
    "信维通信",
    "汇金股份"
]

# 行业板块总数
FOCUS_ON_STOCKS_COUNT = len(FOCUS_ON_STOCKS)

def get_focus_on_stocks():
    """
    获取重点关注股票列表
    
    Returns:
        list: 重点关注股票名称列表
    """
    return FOCUS_ON_STOCKS.copy()
