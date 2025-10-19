import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from xtrading.strategies.industry_sector.backtest import StrategyBacktest
from xtrading.static import INDUSTRY_SECTORS, INDUSTRY_SECTORS_COUNT

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

                backtest.print_backtest_results(results)

                # 输出简要结果
                print(f"📊 {industry_name} 策略表现:")
                for result in results:
                    strategy_name = result['strategy_name']
                    total_return = result['total_return']
                    sharpe_ratio = result['sharpe_ratio']
                    print(f"   {strategy_name}: 总收益 {total_return:.2f}%, 夏普比率 {sharpe_ratio:.4f}")
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
    print(f"📈 成功率: {successful_tests/INDUSTRY_SECTORS_COUNT*100:.1f}%")
    print(f"⏰ 开始时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}")
    print(f"⏰ 结束时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))}")
    print(f"⏱️ 总耗时: {total_duration:.1f} 秒 ({total_duration/60:.1f} 分钟)")
    print(f"📊 平均每行业耗时: {total_duration/INDUSTRY_SECTORS_COUNT:.2f} 秒")
    print("=" * 80)

if __name__ == '__main__':
    all_industries_test()