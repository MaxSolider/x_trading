"""
日期工具类使用示例
演示如何使用DateUtils进行交易日相关操作
"""

from src.xtrading.utils.date.date_utils import DateUtils


def date_utils_example():
    """日期工具类使用示例"""
    print("🚀 日期工具类使用示例")
    print("=" * 50)
    
    try:
        # 1. 获取当前日期的最近交易日
        print("\n📅 获取当前日期的最近交易日...")
        recent_trading_day = DateUtils.get_recent_trading_day()
        print(f"最近的交易日: {recent_trading_day}")
        
        # 2. 获取指定日期的最近交易日
        print("\n📅 获取指定日期的最近交易日...")
        specified_date = '20251025'  # 假设这是一个周末
        recent_trading_day = DateUtils.get_recent_trading_day(date=specified_date)
        print(f"{specified_date} 的最近交易日: {recent_trading_day}")
        
        # 3. 判断指定日期是否为交易日
        print("\n📅 判断指定日期是否为交易日...")
        test_dates = ['20251020', '20251021', '20251025', '20251026']
        for test_date in test_dates:
            is_trading = DateUtils.is_trading_day(test_date)
            print(f"{test_date} 是否为交易日: {is_trading}")
        
        # 4. 获取两个日期之间的所有交易日
        print("\n📅 获取两个日期之间的所有交易日...")
        start_date = '20251020'
        end_date = '20251030'
        trading_days = DateUtils.get_trading_days_between(start_date, end_date)
        print(f"{start_date} 到 {end_date} 之间的交易日:")
        for day in trading_days:
            print(f"  - {day}")
        
        # 5. 日期格式化
        print("\n📅 日期格式化...")
        date_str = '20251020'
        formatted_date = DateUtils.format_date(date_str, '%Y%m%d', '%Y-%m-%d')
        print(f"原始日期: {date_str}")
        print(f"格式化后: {formatted_date}")
        
    except Exception as e:
        print(f"❌ 示例执行失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    date_utils_example()
