"""
日期工具类
提供交易日相关的日期处理功能
"""

import datetime
from typing import Optional
from chncal import get_recent_tradeday


class DateUtils:
    """日期工具类"""
    
    @staticmethod
    def get_recent_trading_day(date: Optional[str] = None) -> str:
        """
        获取最近的交易日日期，返回格式为YYYYMMDD
        
        Args:
            date: 可选参数，指定日期（字符串格式：YYYYMMDD），默认为当前日期
            
        Returns:
            str: 最近的交易日日期，格式为YYYYMMDD
            
        Raises:
            ValueError: 当日期格式不正确时抛出异常
        """
        try:
            if date is None:
                # 获取当前日期
                date_obj = datetime.datetime.now()
            else:
                # 验证日期格式并转换为datetime对象
                try:
                    date_obj = datetime.datetime.strptime(date, '%Y%m%d')
                except ValueError:
                    raise ValueError("日期格式应为YYYYMMDD")
            
            # 检查是否为周末，如果是周末则向前调整到周五
            weekday = date_obj.weekday()  # 0=Monday, 6=Sunday
            if weekday >= 5:  # Saturday=5, Sunday=6
                # 调整到周五
                days_to_subtract = weekday - 4
                date_obj = date_obj - datetime.timedelta(days=days_to_subtract)
            
            # 获取最近的交易日，使用datetime对象而不是字符串
            recent_trading_day = get_recent_tradeday(date=date_obj, dirt='pre')
            
            # 将日期格式化为YYYYMMDD
            # get_recent_tradeday返回的是datetime.date对象，有strftime方法
            return recent_trading_day.strftime('%Y%m%d')
            
        except Exception as e:
            print(f"❌ 获取最近交易日失败: {e}")
            # 如果chncal库调用失败，返回当前日期作为备选
            return datetime.datetime.now().strftime('%Y%m%d')
    
    @staticmethod
    def is_trading_day(date: str) -> bool:
        """
        判断指定日期是否为交易日
        
        Args:
            date: 日期字符串，格式为YYYYMMDD
            
        Returns:
            bool: 是否为交易日
        """
        try:
            # 验证日期格式并转换为datetime对象
            date_obj = datetime.datetime.strptime(date, '%Y%m%d')
            
            # 检查是否为周末，如果是周末则直接返回False
            weekday = date_obj.weekday()  # 0=Monday, 6=Sunday
            if weekday >= 5:  # Saturday=5, Sunday=6
                return False
            
            # 获取该日期的最近交易日，使用datetime对象
            recent_trading_day = get_recent_tradeday(date=date_obj, dirt='pre')
            
            # 如果最近交易日就是该日期本身，说明是交易日
            return recent_trading_day.strftime('%Y%m%d') == date
            
        except Exception as e:
            print(f"❌ 判断交易日失败: {e}")
            return False
    
    @staticmethod
    def get_trading_days_between(start_date: str, end_date: str) -> list:
        """
        获取两个日期之间的所有交易日
        
        Args:
            start_date: 开始日期，格式为YYYYMMDD
            end_date: 结束日期，格式为YYYYMMDD
            
        Returns:
            list: 交易日列表，格式为YYYYMMDD
        """
        try:
            # 验证日期格式
            start_dt = datetime.datetime.strptime(start_date, '%Y%m%d')
            end_dt = datetime.datetime.strptime(end_date, '%Y%m%d')
            
            trading_days = []
            current_date = start_dt
            
            while current_date <= end_dt:
                current_date_str = current_date.strftime('%Y%m%d')
                if DateUtils.is_trading_day(current_date_str):
                    trading_days.append(current_date_str)
                current_date += datetime.timedelta(days=1)
            
            return trading_days
            
        except Exception as e:
            print(f"❌ 获取交易日列表失败: {e}")
            return []
    
    @staticmethod
    def format_date(date_str: str, input_format: str = '%Y%m%d', output_format: str = '%Y-%m-%d') -> str:
        """
        格式化日期字符串
        
        Args:
            date_str: 输入日期字符串
            input_format: 输入格式，默认为'%Y%m%d'
            output_format: 输出格式，默认为'%Y-%m-%d'
            
        Returns:
            str: 格式化后的日期字符串
        """
        try:
            date_obj = datetime.datetime.strptime(date_str, input_format)
            return date_obj.strftime(output_format)
        except Exception as e:
            print(f"❌ 日期格式化失败: {e}")
            return date_str
