"""
AKShare股票日线数据查询工具 - 主程序
"""

import time
from .data.db import ensure_database_exists
from .data.schema_init import initialize_database_and_tables
from .data.data_loader import DataLoader
from .strategies.market_sentiment.market_sentiment_strategy import MarketSentimentStrategy
from .services.backtest_service import BacktestService
from .utils.date.date_utils import DateUtils
from .static import INDUSTRY_SECTORS, INDUSTRY_SECTORS_COUNT,INDUSTRY_CATEGORIES


def test_market_sentiment_analysis():
    """测试市场情绪分析功能"""
    print("🧪 开始测试市场情绪分析功能...")

    try:
        # 创建市场情绪分析策略实例
        sentiment_strategy = MarketSentimentStrategy()

        # 分析市场情绪
        print("\n📊 正在分析市场情绪...")
        sentiment_result = sentiment_strategy.analyze_market_sentiment()

    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


def test_market_review_service():
    """测试市场复盘服务功能"""
    print("🧪 开始测试市场复盘服务功能...")

    try:
        # 创建市场复盘服务实例
        from src.xtrading.services.review.market_review_service import MarketReviewService
        review_service = MarketReviewService()

        # 执行市场复盘分析
        print("\n📊 正在执行市场复盘分析...")
        review_result = review_service.conduct_market_review()

        # 打印复盘结果摘要
        review_service.print_review_summary(review_result)

    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

def test_backtest():
    # 执行完整回测并生成报告
    try:
        service = BacktestService()
        results = service.run_full_backtest(
            days=30,  # 最近30天的推荐
            parallel=True,  # 并行执行
            generate_report=True  # 生成报告
        )
    except Exception as e:
        print(f"❌ 完整回测并生成报告失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_loader_service():
    """测试数据加载服务"""
    print("🧪 开始测试数据加载服务...")
    try:
        # 1) 初始化数据库与表
        ensure_database_exists()
        initialize_database_and_tables()

        # 2) 创建数据加载器
        loader = DataLoader()
        print("✅ 数据加载器初始化成功")

        # 3) 执行加载：行业与股票近3个月数据
        start_ts = time.time()
        print("📥 开始加载行业板块近4个月数据...")
        loader.load_industry_history_last_4m()
        print("✅ 行业板块数据加载完成")

        print("📥 开始加载股票近4个月数据...")
        loader.load_stock_history_last_4m()
        print("✅ 股票数据加载完成")

        duration = time.time() - start_ts
        print(f"⏱️ 总耗时: {duration:.2f} 秒")
        return True
    except Exception as e:
        print(f"❌ 测试数据加载服务失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    # 按板块分类进行回测
    # category_backtest_test()

    # 对所有板块进行回测
    # all_industries_test()

    # 测试板块信号
    # sector_signal_service_test()

    # 测试预测服务
    # projection_service_test()

    # 测试市场情绪分析
    # test_market_sentiment_analysis()
    
    # 测试市场复盘服务
    test_market_review_service()
    
    # 测试日期工具类
    # print(DateUtils.get_recent_trading_day('20251026'))

    # 测试数据加载服务
    # test_data_loader_service()

    # 运行回测服务
    # test_backtest()



if __name__ == "__main__":
    main()
