"""
AKShare股票日线数据查询工具 - 主程序
"""

import time
from .data.db import ensure_database_exists
from .data.schema_init import initialize_database_and_tables
from .data.data_loader import DataLoader
from .strategies.industry_sector.backtest import StrategyBacktest
from .services.signal.sector_signal_service import SectorSignalService
from .services.projection.projection_service import ProjectionService
from .strategies.market_sentiment.market_sentiment_strategy import MarketSentimentStrategy
from .utils.date.date_utils import DateUtils
from .static import INDUSTRY_SECTORS, INDUSTRY_SECTORS_COUNT,INDUSTRY_CATEGORIES

def single_industry_test():
    """测试单个行业板块的策略"""
    print("🧪 单个行业板块策略测试")
    print("=" * 60)

    # 创建回测实例
    backtest = StrategyBacktest()

    strategies = ["MACD", "RSI", "BollingerBands", "MovingAverage"]
    results = backtest.compare_strategies(
        industry_name="半导体",
        strategies=strategies,
        start_date="20250101",
        end_date="20251217",
        initial_capital=100000,
        fast_period=12,
        slow_period=26,
        signal_period=9
    )
    backtest.print_backtest_results(results)


def all_industries_test():
    """运行全行业板块回测验证"""
    print("🚀 运行全行业板块策略回测验证")
    print("=" * 80)
    print(f"📊 总行业板块数量: {INDUSTRY_SECTORS_COUNT}")
    print(f"📅 回测期间: 2025-01-01 至 2025-10-17")
    print(f"💰 初始资金: ¥100,000")
    print(f"📈 测试策略: MACD, RSI, BollingerBands, MovingAverage")
    print("=" * 80)

    # 记录开始时间
    start_time = time.time()
    print(f"⏰ 开始时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}")

    # 创建回测实例
    backtest = StrategyBacktest()

    # 策略参数配置
    strategies = ["MACD", "RSI", "BollingerBands", "MovingAverage"]

    # 统计信息
    successful_tests = 0
    failed_tests = 0
    all_results = []  # 存储所有行业板块的回测结果

    # 遍历所有行业板块
    for i, industry_name in enumerate(INDUSTRY_SECTORS, 1):
        print(f"\n🔍 [{i:2d}/{INDUSTRY_SECTORS_COUNT}] 测试行业板块: {industry_name}")
        print("-" * 60)

        try:
            # 运行回测
            results = backtest.compare_strategies(
                industry_name=industry_name,
                strategies=strategies,
                start_date="20250101",
                end_date="20251017",
                initial_capital=100000,
                # MACD参数
                fast_period=12,
                slow_period=26,
                signal_period=9,
                # RSI参数
                rsi_period=14,
                oversold=30,
                overbought=70,
                # 布林带参数
                bb_period=20,
                std_dev=2,
                # 移动平均参数
                short_period=5,
                medium_period=20,
                long_period=60
            )

            if results:
                print(f"✅ {industry_name} 回测成功")
                successful_tests += 1
                # 保存回测结果
                backtest.print_backtest_results(results)
                # 添加到总结果列表
                all_results.append(results)
            else:
                print(f"⚠️ {industry_name} 回测失败 - 无数据")
                failed_tests += 1

        except Exception as e:
            print(f"❌ {industry_name} 回测异常: {str(e)[:100]}...")
            failed_tests += 1

    # 记录结束时间
    end_time = time.time()
    total_duration = end_time - start_time

    # 输出总结
    print("\n" + "=" * 80)
    print("📊 全行业板块回测验证总结")
    print("=" * 80)
    print(f"✅ 成功测试: {successful_tests} 个行业板块")
    print(f"❌ 失败测试: {failed_tests} 个行业板块")
    print(f"📈 成功率: {successful_tests / INDUSTRY_SECTORS_COUNT * 100:.1f}%")
    print(f"⏰ 开始时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}")
    print(f"⏰ 结束时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))}")
    print(f"⏱️ 总耗时: {total_duration:.1f} 秒 ({total_duration / 60:.1f} 分钟)")
    print(f"📊 平均每行业耗时: {total_duration / INDUSTRY_SECTORS_COUNT:.2f} 秒")
    print("=" * 80)

    # 生成整体回测总结报告
    if all_results:
        print("\n📊 生成整体回测总结报告...")
        print("=" * 80)
        backtest.print_backtest_summary(all_results)
        print("=" * 80)


def category_backtest_test():
    """按行业分类进行回测"""
    print("🏢 按行业分类回测测试")
    print("=" * 80)

    # 创建回测实例
    backtest = StrategyBacktest()

    # 策略参数配置
    strategies = ["MACD", "RSI", "BollingerBands", "MovingAverage"]

    # 测试指定的行业分类
    target_categories = ["金融", "能源"]  # 选择较小的分类进行测试

    print(f"🎯 目标分类: {', '.join(target_categories)}")
    print(f"📅 回测期间: 2025-01-01 至 2025-10-17")
    print(f"💰 初始资金: ¥100,000")
    print(f"📈 测试策略: {', '.join(strategies)}")

    # 计算总板块数量
    total_sectors = sum(len(INDUSTRY_CATEGORIES[cat]) for cat in target_categories)
    print(f"📊 总板块数量: {total_sectors}")
    print("=" * 80)

    # 记录开始时间
    start_time = time.time()
    print(f"⏰ 开始时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}")

    # 统计信息
    successful_tests = 0
    failed_tests = 0
    category_results = {}
    all_results = []  # 存储所有行业板块的回测结果

    # 按分类进行回测
    for category in target_categories:
        print(f"\n🏢 开始回测分类: {category}")
        print("-" * 60)

        category_results[category] = []
        sectors = INDUSTRY_CATEGORIES[category]

        for i, industry_name in enumerate(sectors, 1):
            print(f"🔍 [{i:2d}/{len(sectors)}] 测试板块: {industry_name}")

            try:
                # 运行回测
                results = backtest.compare_strategies(
                    industry_name=industry_name,
                    strategies=strategies,
                    start_date="20250101",
                    end_date="20251017",
                    initial_capital=100000,
                    # MACD参数
                    fast_period=12,
                    slow_period=26,
                    signal_period=9,
                    # RSI参数
                    rsi_period=14,
                    oversold=30,
                    overbought=70,
                    # 布林带参数
                    bb_period=20,
                    std_dev=2,
                    # 移动平均参数
                    short_period=5,
                    medium_period=20,
                    long_period=60
                )

                if results:
                    print(f"✅ {industry_name} 回测成功")
                    successful_tests += 1
                    category_results[category].extend(results)
                    # 保存回测结果
                    backtest.print_backtest_results(results)
                    # 添加到总结果列表
                    all_results.append(results)
                else:
                    print(f"⚠️ {industry_name} 回测失败 - 无数据")
                    failed_tests += 1

            except Exception as e:
                print(f"❌ {industry_name} 回测异常: {str(e)[:100]}...")
                failed_tests += 1

            print()  # 添加空行分隔

    # 记录结束时间
    end_time = time.time()
    total_duration = end_time - start_time

    # 输出总体总结
    print("\n" + "=" * 80)
    print("📊 分类回测总结")
    print("=" * 80)
    print(f"✅ 成功测试: {successful_tests} 个行业板块")
    print(f"❌ 失败测试: {failed_tests} 个行业板块")
    print(f"📈 成功率: {successful_tests / total_sectors * 100:.1f}%")
    print(f"⏰ 开始时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}")
    print(f"⏰ 结束时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))}")
    print(f"⏱️ 总耗时: {total_duration:.1f} 秒 ({total_duration / 60:.1f} 分钟)")
    print(f"📊 平均每板块耗时: {total_duration / total_sectors:.2f} 秒")

    print("=" * 80)

    # 生成整体回测总结报告
    if all_results:
        print("\n📊 生成整体回测总结报告...")
        print("=" * 80)
        backtest.print_backtest_summary(all_results)
        print("=" * 80)


def sector_signal_service_test():
    # 初始化服务
    service = SectorSignalService()
    print("✅ 服务初始化成功")

    # 测试板块列表
    test_sectors = INDUSTRY_SECTORS
    print(f"\n📊 待分析板块: {test_sectors}")
    print(f"\n🚩 分析中...")

    start_time = time.time()

    results = service.calculate_sector_signals(
        sector_list=test_sectors
    )

    end_time = time.time()
    duration = end_time - start_time

    if results:
        print(f"✅ 板块分析完成: 耗时 {duration:.2f} 秒")
        
        # 生成综合分析报告
        print("\n📄 生成综合分析报告...")
        service.print_signal_summary(results)

    else:
        print("❌ 板块信号分析失败: 无结果")
        return False


def projection_service_test():
    """测试明日股市机会策略投影服务"""
    print("🎯 明日股市机会策略投影服务测试")
    print("=" * 80)
    
    try:
        # 创建投影服务实例
        projection_service = ProjectionService()
        print("✅ 投影服务初始化成功")
        
        print("-" * 60)
        
        # 选择几个热门板块进行测试
        hot_sectors = ["半导体", "消费电子", "银行", "证券"]
        print(f"🎯 测试板块: {', '.join(hot_sectors)}")
        
        start_time = time.time()
        
        results1 = projection_service.calculate_tomorrow_opportunities(
            sector_list=hot_sectors,
            sector_strategies=["MACD", "RSI", "BollingerBands", "MovingAverage"],
            stock_strategies=["TrendTracking", "Breakout", "OversoldRebound"],
            min_buy_signals=1,  # 降低买入信号阈值
            max_stocks_per_sector=20  # 每个板块最多分析5只股票
        )
        
        end_time = time.time()

        if results1:
            # 打印汇总信息
            projection_service.print_opportunity_summary(results1)
            
            # 生成详细报告
            print("\n📄 生成详细分析报告...")
            report_file1 = projection_service.generate_opportunity_report(results1)
            if report_file1:
                print(f"✅ 报告已生成: {report_file1}")
        else:
            print("❌ 小规模测试失败: 无结果")
        
        print("\n" + "=" * 80)
        
        # 测试总结
        duration = end_time - start_time
        print("\n" + "=" * 80)
        print("🎉 明日股市机会策略投影服务测试总结")
        print("=" * 80)
        print(f"⏱️ 总测试耗时: {duration:.2f} 秒")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"❌ 投影服务测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


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
        # loader.load_industry_history_last_4m()
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
    print("🚀 XTrading 策略回测")
    print("=" * 80)
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



if __name__ == "__main__":
    main()
