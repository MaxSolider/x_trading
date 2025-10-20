"""
行业板块移动平均策略
基于移动平均线进行行业板块交易策略
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, List
from ...repositories.stock.industry_info_query import IndustryInfoQuery

class IndustryMovingAverageStrategy:
    """行业板块移动平均策略类"""
    
    def __init__(self):
        """初始化策略"""
        self.industry_query = IndustryInfoQuery()
        print("✅ 行业板块移动平均策略初始化成功")
    
    def calculate_moving_averages(self, data: pd.DataFrame, short_period: int = 5, 
                                 medium_period: int = 20, long_period: int = 60) -> pd.DataFrame:
        """
        计算移动平均线
        
        Args:
            data: 包含收盘价的DataFrame
            short_period: 短期移动平均周期
            medium_period: 中期移动平均周期
            long_period: 长期移动平均周期
            
        Returns:
            DataFrame: 包含移动平均线的DataFrame
        """
        if data is None or data.empty:
            return None
        
        # 确保有收盘价列
        close_col = None
        for col in ['收盘', '收盘价', 'close', 'Close']:
            if col in data.columns:
                close_col = col
                break
        
        if close_col is None:
            print("❌ 未找到收盘价列")
            return None
        
        # 计算不同周期的移动平均线
        sma_short = data[close_col].rolling(window=short_period).mean()
        sma_medium = data[close_col].rolling(window=medium_period).mean()
        sma_long = data[close_col].rolling(window=long_period).mean()
        
        # 计算指数移动平均线
        ema_short = data[close_col].ewm(span=short_period).mean()
        ema_medium = data[close_col].ewm(span=medium_period).mean()
        ema_long = data[close_col].ewm(span=long_period).mean()
        
        # 计算移动平均线之间的距离
        ma_spread_short_medium = sma_short - sma_medium
        ma_spread_medium_long = sma_medium - sma_long
        ma_spread_short_long = sma_short - sma_long
        
        # 创建结果DataFrame
        result = data.copy()
        result['SMA_Short'] = sma_short
        result['SMA_Medium'] = sma_medium
        result['SMA_Long'] = sma_long
        result['EMA_Short'] = ema_short
        result['EMA_Medium'] = ema_medium
        result['EMA_Long'] = ema_long
        result['MA_Spread_Short_Medium'] = ma_spread_short_medium
        result['MA_Spread_Medium_Long'] = ma_spread_medium_long
        result['MA_Spread_Short_Long'] = ma_spread_short_long
        
        return result
    
    def generate_ma_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        生成移动平均交易信号
        
        Args:
            data: 包含移动平均线的DataFrame
            
        Returns:
            DataFrame: 包含交易信号的DataFrame
        """
        if data is None or data.empty or 'SMA_Short' not in data.columns:
            return None
        
        result = data.copy()
        
        # 确保有收盘价列
        close_col = None
        for col in ['收盘', '收盘价', 'close', 'Close']:
            if col in data.columns:
                close_col = col
                break
        
        if close_col is None:
            return None
        
        # 初始化信号列
        result['Signal'] = 0
        result['Signal_Type'] = 'HOLD'
        result['MA_Trend'] = 'SIDEWAYS'
        
        close_price = result[close_col]
        sma_short = result['SMA_Short']
        sma_medium = result['SMA_Medium']
        sma_long = result['SMA_Long']
        
        # 金叉信号（短期线上穿中期线）
        golden_cross_short_medium = (sma_short > sma_medium) & (sma_short.shift(1) <= sma_medium.shift(1))
        result.loc[golden_cross_short_medium, 'Signal'] = 1
        result.loc[golden_cross_short_medium, 'Signal_Type'] = 'BUY'
        result.loc[golden_cross_short_medium, 'MA_Trend'] = 'BULLISH'
        
        # 死叉信号（短期线下穿中期线）
        death_cross_short_medium = (sma_short < sma_medium) & (sma_short.shift(1) >= sma_medium.shift(1))
        result.loc[death_cross_short_medium, 'Signal'] = -1
        result.loc[death_cross_short_medium, 'Signal_Type'] = 'SELL'
        result.loc[death_cross_short_medium, 'MA_Trend'] = 'BEARISH'
        
        # 中期线上穿长期线（强势买入）
        golden_cross_medium_long = (sma_medium > sma_long) & (sma_medium.shift(1) <= sma_long.shift(1))
        result.loc[golden_cross_medium_long, 'Signal'] = 2
        result.loc[golden_cross_medium_long, 'Signal_Type'] = 'STRONG_BUY'
        result.loc[golden_cross_medium_long, 'MA_Trend'] = 'STRONG_BULLISH'
        
        # 中期线下穿长期线（强势卖出）
        death_cross_medium_long = (sma_medium < sma_long) & (sma_medium.shift(1) >= sma_long.shift(1))
        result.loc[death_cross_medium_long, 'Signal'] = -2
        result.loc[death_cross_medium_long, 'Signal_Type'] = 'STRONG_SELL'
        result.loc[death_cross_medium_long, 'MA_Trend'] = 'STRONG_BEARISH'
        
        # 价格上穿移动平均线
        price_above_ma = (close_price > sma_medium) & (close_price.shift(1) <= sma_medium.shift(1))
        result.loc[price_above_ma, 'Signal'] = 1
        result.loc[price_above_ma, 'Signal_Type'] = 'BUY'
        result.loc[price_above_ma, 'MA_Trend'] = 'BULLISH'
        
        # 价格下穿移动平均线
        price_below_ma = (close_price < sma_medium) & (close_price.shift(1) >= sma_medium.shift(1))
        result.loc[price_below_ma, 'Signal'] = -1
        result.loc[price_below_ma, 'Signal_Type'] = 'SELL'
        result.loc[price_below_ma, 'MA_Trend'] = 'BEARISH'
        
        # 判断趋势方向
        bullish_trend = (sma_short > sma_medium) & (sma_medium > sma_long)
        bearish_trend = (sma_short < sma_medium) & (sma_medium < sma_long)
        
        result.loc[bullish_trend, 'MA_Trend'] = 'BULLISH'
        result.loc[bearish_trend, 'MA_Trend'] = 'BEARISH'
        
        return result
    
    def analyze_industry_ma(self, industry_name: str, start_date: str = None, end_date: str = None,
                          short_period: int = 5, medium_period: int = 20, long_period: int = 60) -> Optional[Dict[str, Any]]:
        """
        分析行业板块移动平均指标
        
        Args:
            industry_name: 行业板块名称
            start_date: 开始日期
            end_date: 结束日期
            short_period: 短期移动平均周期
            medium_period: 中期移动平均周期
            long_period: 长期移动平均周期
            
        Returns:
            Dict: 包含分析结果的字典
        """
        try:

            # 获取行业板块历史数据
            hist_data = self.industry_query.get_board_industry_hist(industry_name, start_date, end_date)
            
            if hist_data is None or hist_data.empty:
                print(f"❌ 无法获取 {industry_name} 的历史数据")
                return None
            
            # 计算移动平均线
            ma_data = self.calculate_moving_averages(hist_data, short_period, medium_period, long_period)
            if ma_data is None:
                return None
            
            # 生成交易信号
            signal_data = self.generate_ma_signals(ma_data)
            if signal_data is None:
                return None
            
            # 分析结果
            latest_data = signal_data.iloc[-1]
            recent_signals = signal_data[signal_data['Signal'] != 0].tail(5)
            
            # 计算移动平均线统计信息
            ma_spread_values = signal_data['MA_Spread_Short_Medium'].dropna()
            ma_spread_mean = ma_spread_values.mean()
            ma_spread_std = ma_spread_values.std()
            
            analysis_result = {
                'industry_name': industry_name,
                'latest_close': latest_data.get('收盘', latest_data.get('收盘价', latest_data.get('close', latest_data.get('Close', 0)))),
                'latest_sma_short': latest_data['SMA_Short'],
                'latest_sma_medium': latest_data['SMA_Medium'],
                'latest_sma_long': latest_data['SMA_Long'],
                'latest_ema_short': latest_data['EMA_Short'],
                'latest_ema_medium': latest_data['EMA_Medium'],
                'latest_ema_long': latest_data['EMA_Long'],
                'latest_ma_spread': latest_data['MA_Spread_Short_Medium'],
                'current_signal_type': latest_data['Signal_Type'],
                'ma_trend': latest_data['MA_Trend'],
                'ma_spread_mean': ma_spread_mean,
                'ma_spread_std': ma_spread_std,
                'short_period': short_period,
                'medium_period': medium_period,
                'long_period': long_period,
                'recent_signals': recent_signals[['日期', '收盘', 'SMA_Short', 'SMA_Medium', 'SMA_Long', 'Signal', 'Signal_Type', 'MA_Trend']].to_dict('records') if not recent_signals.empty else [],
                'data_points': len(signal_data),
                'analysis_date': latest_data.get('日期', 'Unknown')
            }
            
            print(f"✅ {industry_name} 移动平均分析完成")
            return analysis_result
            
        except Exception as e:
            print(f"❌ {industry_name} 移动平均分析失败: {e}")
            return None
    
    def get_ma_recommendations(self, industry_names: List[str], short_period: int = 5,
                             medium_period: int = 20, long_period: int = 60) -> List[Dict[str, Any]]:
        """
        获取多个行业板块的移动平均推荐
        
        Args:
            industry_names: 行业板块名称列表
            short_period: 短期移动平均周期
            medium_period: 中期移动平均周期
            long_period: 长期移动平均周期
            
        Returns:
            List[Dict]: 推荐结果列表
        """
        recommendations = []
        
        print(f"🔍 开始分析 {len(industry_names)} 个行业板块的移动平均指标...")
        
        for industry_name in industry_names:
            analysis = self.analyze_industry_ma(industry_name, short_period=short_period,
                                              medium_period=medium_period, long_period=long_period)
            if analysis:
                recommendations.append(analysis)
        
        # 按信号强度排序（绝对值越大越重要）
        recommendations.sort(key=lambda x: abs(x['latest_ma_spread']), reverse=True)
        
        print(f"✅ 移动平均分析完成，共分析 {len(recommendations)} 个行业板块")
        return recommendations
    
    def print_ma_analysis(self, analysis_result: Dict[str, Any]):
        """
        打印移动平均分析结果
        
        Args:
            analysis_result: 分析结果字典
        """
        if not analysis_result:
            print("❌ 无分析结果可显示")
            return
        
        print(f"\n📊 {analysis_result['industry_name']} 移动平均分析结果")
        print("=" * 60)
        print(f"分析日期: {analysis_result['analysis_date']}")
        print(f"数据点数: {analysis_result['data_points']}")
        print(f"当前收盘价: {analysis_result['latest_close']:.2f}")
        print(f"短期移动平均({analysis_result['short_period']}日): {analysis_result['latest_sma_short']:.2f}")
        print(f"中期移动平均({analysis_result['medium_period']}日): {analysis_result['latest_sma_medium']:.2f}")
        print(f"长期移动平均({analysis_result['long_period']}日): {analysis_result['latest_sma_long']:.2f}")
        print(f"移动平均价差: {analysis_result['latest_ma_spread']:.2f}")
        print(f"交易信号: {analysis_result['current_signal_type']}")
        print(f"趋势方向: {analysis_result['ma_trend']}")
        print(f"价差均值: {analysis_result['ma_spread_mean']:.2f}")
        print(f"价差标准差: {analysis_result['ma_spread_std']:.2f}")
        
        if analysis_result['recent_signals']:
            print(f"\n📈 最近交易信号:")
            for signal in analysis_result['recent_signals']:
                print(f"  {signal['日期']}: {signal['Signal_Type']} (收盘价: {signal['收盘']:.2f}, 趋势: {signal['MA_Trend']})")
