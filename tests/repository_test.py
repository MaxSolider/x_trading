import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from xtrading.repositories.stock.stock_query import StockQuery
from xtrading.utils.stock_code_utils import StockCodeUtils
from xtrading.utils.data_output_utils import DataOutputUtils
from xtrading.repositories.stock.market_overview_query import MarketOverviewQuery
from xtrading.repositories.stock.industry_info_query import IndustryInfoQuery
from xtrading.repositories.stock.concept_info_query import ConceptInfoQuery

def main():
    """主函数"""
    # 初始化查询工具
    print("==============")
    try:
        query = StockQuery()
        data_output = DataOutputUtils()
        market_query = MarketOverviewQuery()
        industry_query = IndustryInfoQuery()
        concept_query = ConceptInfoQuery()

        print("✅ AKShare服务初始化成功")
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return

    # stocks = ["688098","002185","300308", "920509", "688617"]

    # 查询股票基础信息
    # for symbol in stocks:
    #     query.print_data_summary(query.get_stock_basic_info(symbol), symbol + "股票基础信息")

    # 查询公司规模信息
    # for symbol in stocks:
    #     query.print_data_summary(query.get_company_scale(symbol), symbol + "公司规模信息")

    # 查询公司主营构成信息
    # for symbol in stocks:
    #     data_output.print_data_details(query.get_main_business_composition(symbol), symbol + "公司主营构成信息")

    # 查询股票历史行情
    # for symbol in stocks:
    #     data_output.print_data_details(query.get_historical_quotes(symbol), symbol + "股票历史行情")

    # 查询股票最近日内分笔数据
    # for symbol in stocks:
    #     data_output.print_data_details(query.get_intraday_tick_data(symbol), symbol + "最近日内分笔数据")

    # 查询股票最近日内分时数据
    # for symbol in stocks:
    #     data_output.print_data_details(query.get_intraday_time_data(symbol, '20251017'), symbol + "日内分时数据")

    # 查询股票筹码分布数据
    # for symbol in stocks:
    #     data_output.print_data_details(query.get_chip_distribution(symbol), symbol + "筹码分布数据")

    # 查询股票筹码分布数据
    # data_output.print_data(market_query.get_sse_deal_daily('20251017'), "上证市场成交概况")
    # data_output.print_data(market_query.get_szse_summary('20251017'), "深证市场成交概况")
    # all_market = market_query.get_market_summary_all('20251017')
    # data_output.print_data(all_market['sse_deal_daily'], "深证市场成交概况")
    # data_output.print_data(all_market['szse_summary'], "上证市场成交概况")

    # 查询行业板块列表
    # data_output.print_data(industry_query.get_board_industry_name(), "行业板块列表")

    # 查询行业板块实时行情
    # data_output.print_data(industry_query.get_board_industry_spot('半导体'), "行业板块实时行情")

    # 查询行业板块日频行情
    data_output.print_data(industry_query.get_board_industry_hist('半导体', '20251001', '20251017'), "行业板块日频行情")


    # 查询行业板块日频行情
    # data_output.print_data(industry_query.get_board_industry_hist('半导体', '20251001', '20251017'), "行业板块日频行情")

    # 查询概念板块列表
    # data_output.print_data(concept_query.get_board_concept_name(), '概念板块列表')

    # 查询概念板块概况
    # data_output.print_data(concept_query.get_board_concept_info('算力租赁'), '概念板块概况')

    # 查询概念板块日频行情
    # data_output.print_data(concept_query.get_board_concept_index('算力租赁', '20251001', '20251017'), '概念板块日频行情')

if __name__ == '__main__':
    main()