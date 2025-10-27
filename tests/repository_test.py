import sys
import os
import time
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# 加载pandas默认配置（pandas_config.py会自动配置）
from xtrading.utils.pandas import pandas_config

from xtrading.repositories.stock.stock_query import StockQuery
from xtrading.utils.rules.stock_code_utils import StockCodeUtils
from xtrading.utils.data.data_output_utils import DataOutputUtils
from xtrading.repositories.stock.market_overview_query import MarketOverviewQuery
from xtrading.repositories.stock.industry_info_query import IndustryInfoQuery
from xtrading.repositories.stock.concept_info_query import ConceptInfoQuery
from xtrading.static.industry_sectors import INDUSTRY_SECTORS

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

    # stocks = ["002948","002185","300308", "920509", "688617"]
    # stocks = ["002948", "688617"]

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
    #     data_output.print_data_details(query.get_historical_quotes(symbol, '20250723', '20251021'), symbol + "股票历史行情")
    # data_output.print_data_details(query.get_historical_quotes('002948', '20251001', '20251021'), "002948" + "股票历史行情")

    # 查询股票实时行情
    # for symbol in stocks:
    #     data_output.print_data_details(query.get_realtime_quotes(symbol), symbol + "股票实时行情")

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
    # data_output.print_data(industry_query.get_board_industry_hist('半导体', '20251001', '20251017'), "行业板块日频行情")

    # 查询行业板块成分股

    # 查询行业板块日频行情
    # data_output.print_data(industry_query.get_board_industry_hist('半导体', '20251001', '20251017'), "行业板块日频行情")

    # 查询概念板块列表
    # data_output.print_data(concept_query.get_board_concept_name(), '概念板块列表')

    # 查询概念板块概况
    # data_output.print_data(concept_query.get_board_concept_info('算力租赁'), '概念板块概况')

    # 查询概念板块日频行情
    # data_output.print_data(concept_query.get_board_concept_index('算力租赁', '20251001', '20251017'), '概念板块日频行情')

    # 查询市场概况
    # data_output.print_data(market_query.get_market_summary('20251023'), '大盘行情')

    # 获取市场涨停股
    # data_output.print_data(market_query.get_limit_up_stocks('20251023'), '大盘涨停股数据')

    # 获取赚钱效应数据
    # data_output.print_data(market_query.get_market_activity(), '大盘赚钱效应数据')

    # 获取两融账户信息
    # data_output.print_data(market_query.get_margin_account_info(), '两融账户数据')

    # 获取北向资金数据
    data_output.print_data(market_query.get_northbound_funds_data(), '北向资金数据')

    # 获取向上突破股票数据
    # data_output.print_data(query.get_upward_breakout_stocks(), '向上突破股票数据')

    # 获取向下突破股票数据
    # data_output.print_data(query.get_downward_breakout_stocks(), '向下突破股票数据')

    # 获取量价齐升股票数据
    # data_output.print_data(query.get_volume_price_up_stocks(), '量价齐升股票数据')

    # 获取量价齐跌股票数据
    # data_output.print_data(query.get_volume_price_down_stocks(), '量价齐跌股票数据')

    # 获取创新高股票数据
    # data_output.print_data(query.get_new_high_stocks(), '创新高股票数据')

    # 获取创新低股票数据
    # data_output.print_data(query.get_new_low_stocks(), '创新低股票数据')

    # 获取连续上涨股票数据
    # data_output.print_data(query.get_consecutive_up_stocks(), '连续上涨股票数据')

    # 获取连续下跌股票数据
    # data_output.print_data(query.get_consecutive_down_stocks(), '连续下跌股票数据')

    # 获取持续放量股票数据
    # data_output.print_data(query.get_volume_expand_stocks(), '持续放量股票数据')

    # 获取持续缩量股票数据
    # data_output.print_data(query.get_volume_shrink_stocks(), '持续缩量股票数据')

if __name__ == '__main__':
    main()
