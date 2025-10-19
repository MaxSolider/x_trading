"""
AKShare股票日线数据查询工具 - 主程序
"""

import subprocess
import sys
from .utils.pandas_config import configure_pandas_display
from .utils.stock_code_utils import StockCodeUtils
from .utils.data_output_utils import DataOutputUtils
from .repositories.stock.industry_info_query import IndustryInfoQuery
from .repositories.stock.market_overview_query import MarketOverviewQuery
from .repositories.stock.stock_query import StockQuery

def main():
    """主函数"""
    # 配置pandas全局显示选项
    configure_pandas_display()

    # 初始化查询工具
    print("==============")
    try:
        query = StockQuery()
        data_output = DataOutputUtils()
        market_query = MarketOverviewQuery()
        industry_query = IndustryInfoQuery()

        print("✅ AKShare服务初始化成功")
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return

    
    # print("🚀 AKShare股票日线数据查询工具")
    # print("=" * 50)

    # 查询行业板块成分股
    data_output.print_data(industry_query.get_board_industry_cons('半导体'), '行业板块成分股')



def query_single_stock(query):
    """查询单个股票"""
    print("\n📊 查询单个股票日线数据")
    print("-" * 30)



def query_common_stocks(query):
    """查询常用股票"""
    print("\n📊 查询常用股票日线数据")
    print("-" * 30)


def query_multiple_stocks(query):
    """批量查询多个股票"""
    print("\n📊 批量查询多个股票")
    print("-" * 30)


if __name__ == "__main__":
    main()
