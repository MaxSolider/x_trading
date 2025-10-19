"""
AKShare股票日线数据查询工具 - 主程序
"""

import time
from .strategies.industry_sector.backtest import StrategyBacktest
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


def main():
    """主函数"""
    print("🚀 XTrading 策略回测")
    print("=" * 80)
    # 按板块分类进行回测
    # category_backtest_test()

    # 对所有板块进行回测
    all_industries_test()


if __name__ == "__main__":
    main()
