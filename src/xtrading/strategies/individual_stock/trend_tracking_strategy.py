"""
个股趋势追踪策略
基于均线多头排列和MACD多头市场进行个股交易策略
核心逻辑：选择已经形成明确上升趋势、处于"主升浪"的个股
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, List
from ...repositories.stock.stock_query import StockQuery

class IndividualTrendTrackingStrategy:
    """个股趋势追踪策略类"""
    
    def __init__(self):
        """初始化策略"""
        self.stock_query = StockQuery()
        print("✅ 个股趋势追踪策略初始化成功")
    
    def calculate_moving_averages(self, data: pd.DataFrame, short_period: int = 5, 
                                medium_period: int = 20, long_period: int = 60) -> pd.DataFrame:
        """
        计算移动平均线
        
        Args:
            data: 包含收盘价的DataFrame
            short_period: 短期移动平均周期（5日）
            medium_period: 中期移动平均周期（20日）
            long_period: 长期移动平均周期（60日）
            
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
        
        # 创建结果DataFrame
        result = data.copy()
        result['SMA_5'] = sma_short
        result['SMA_20'] = sma_medium
        result['SMA_60'] = sma_long
        result['EMA_5'] = ema_short
        result['EMA_20'] = ema_medium
        result['EMA_60'] = ema_long
        
        return result
    
    def calculate_macd(self, data: pd.DataFrame, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> pd.DataFrame:
        """
        计算MACD指标
        
        Args:
            data: 包含收盘价的DataFrame
            fast_period: 快线周期
            slow_period: 慢线周期
            signal_period: 信号线周期
            
        Returns:
            DataFrame: 包含MACD指标的DataFrame
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
        
        # 计算EMA
        ema_fast = data[close_col].ewm(span=fast_period).mean()
        ema_slow = data[close_col].ewm(span=slow_period).mean()
        
        # 计算MACD线（DIF）
        dif = ema_fast - ema_slow
        
        # 计算信号线（DEA）
        dea = dif.ewm(span=signal_period).mean()
        
        # 计算柱状图（MACD）
        macd_histogram = dif - dea
        
        # 创建结果DataFrame
        result = data.copy()
        result['EMA_Fast'] = ema_fast
        result['EMA_Slow'] = ema_slow
        result['DIF'] = dif
        result['DEA'] = dea
        result['MACD'] = macd_histogram
        
        return result
    
    def generate_trend_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        生成趋势追踪交易信号
        
        Args:
            data: 包含移动平均线和MACD指标的DataFrame
            
        Returns:
            DataFrame: 包含交易信号的DataFrame
        """
        if data is None or data.empty:
            return None
        
        # 检查必要的列
        required_cols = ['SMA_5', 'SMA_20', 'SMA_60', 'DIF', 'DEA']
        for col in required_cols:
            if col not in data.columns:
                print(f"❌ 缺少必要的列: {col}")
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
        result['Trend_Status'] = 'SIDEWAYS'
        result['MACD_Status'] = 'NEUTRAL'
        
        close_price = result[close_col]
        sma_5 = result['SMA_5']
        sma_20 = result['SMA_20']
        sma_60 = result['SMA_60']
        dif = result['DIF']
        dea = result['DEA']
        
        # 1. 均线多头排列判断
        ma_bullish_alignment = (sma_5 > sma_20) & (sma_20 > sma_60)
        ma_bearish_alignment = (sma_5 < sma_20) & (sma_20 < sma_60)
        
        # 2. MACD多头市场判断
        macd_bullish = (dif > dea) & (dif > 0) & (dea > 0)
        macd_bearish = (dif < dea) & (dif < 0) & (dea < 0)
        
        # 3. 价格在均线上方
        price_above_ma = close_price > sma_20
        
        # 4. 趋势追踪买入信号：均线多头排列 + MACD多头 + 价格在均线上方
        trend_buy_signal = ma_bullish_alignment & macd_bullish & price_above_ma
        
        # 5. 趋势追踪卖出信号：均线空头排列 + MACD空头
        trend_sell_signal = ma_bearish_alignment & macd_bearish
        
        # 6. 强势买入信号：所有条件都满足且MACD柱状图放大
        macd_histogram_expanding = result['MACD'] > result['MACD'].shift(1)
        strong_buy_signal = trend_buy_signal & macd_histogram_expanding
        
        # 7. 强势卖出信号：趋势转弱
        strong_sell_signal = trend_sell_signal & (result['MACD'] < result['MACD'].shift(1))
        
        # 设置信号
        result.loc[strong_buy_signal, 'Signal'] = 2
        result.loc[strong_buy_signal, 'Signal_Type'] = 'STRONG_BUY'
        result.loc[strong_buy_signal, 'Trend_Status'] = 'STRONG_BULLISH'
        result.loc[strong_buy_signal, 'MACD_Status'] = 'STRONG_BULLISH'
        
        result.loc[trend_buy_signal & ~strong_buy_signal, 'Signal'] = 1
        result.loc[trend_buy_signal & ~strong_buy_signal, 'Signal_Type'] = 'BUY'
        result.loc[trend_buy_signal & ~strong_buy_signal, 'Trend_Status'] = 'BULLISH'
        result.loc[trend_buy_signal & ~strong_buy_signal, 'MACD_Status'] = 'BULLISH'
        
        result.loc[strong_sell_signal, 'Signal'] = -2
        result.loc[strong_sell_signal, 'Signal_Type'] = 'STRONG_SELL'
        result.loc[strong_sell_signal, 'Trend_Status'] = 'STRONG_BEARISH'
        result.loc[strong_sell_signal, 'MACD_Status'] = 'STRONG_BEARISH'
        
        result.loc[trend_sell_signal & ~strong_sell_signal, 'Signal'] = -1
        result.loc[trend_sell_signal & ~strong_sell_signal, 'Signal_Type'] = 'SELL'
        result.loc[trend_sell_signal & ~strong_sell_signal, 'Trend_Status'] = 'BEARISH'
        result.loc[trend_sell_signal & ~strong_sell_signal, 'MACD_Status'] = 'BEARISH'
        
        # 设置趋势状态
        result.loc[ma_bullish_alignment, 'Trend_Status'] = 'BULLISH'
        result.loc[ma_bearish_alignment, 'Trend_Status'] = 'BEARISH'
        
        # 设置MACD状态
        result.loc[macd_bullish, 'MACD_Status'] = 'BULLISH'
        result.loc[macd_bearish, 'MACD_Status'] = 'BEARISH'
        
        return result
    
    def analyze_stock_trend(self, symbol: str, start_date: str = None, end_date: str = None) -> Optional[Dict[str, Any]]:
        """
        分析个股趋势追踪指标
        
        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            Dict: 包含分析结果的字典
        """
        try:
            # 获取个股历史数据
            hist_data = self.stock_query.get_historical_quotes(symbol, start_date, end_date)
            
            if hist_data is None or hist_data.empty:
                print(f"❌ 无法获取 {symbol} 的历史数据")
                return None
            
            # 计算移动平均线
            ma_data = self.calculate_moving_averages(hist_data)
            if ma_data is None:
                return None
            
            # 计算MACD指标
            macd_data = self.calculate_macd(ma_data)
            if macd_data is None:
                return None
            
            # 生成交易信号
            signal_data = self.generate_trend_signals(macd_data)
            if signal_data is None:
                return None
            
            # 分析结果
            latest_data = signal_data.iloc[-1]
            recent_signals = signal_data[signal_data['Signal'] != 0].tail(5)
            
            # 计算趋势强度
            trend_strength = self._calculate_trend_strength(signal_data)
            
            # 获取日期列名（兼容中英文列名）
            date_col = None
            for col in ['日期', 'date', 'Date', '交易日期']:
                if col in signal_data.columns:
                    date_col = col
                    break
            
            # 获取收盘价列名（兼容中英文列名）
            close_col = None
            for col in ['收盘', '收盘价', 'close', 'Close']:
                if col in signal_data.columns:
                    close_col = col
                    break
            
            # 构建最近交易信号列表
            recent_signals_list = []
            if not recent_signals.empty and date_col and close_col:
                try:
                    recent_signals_list = recent_signals[[date_col, close_col, 'SMA_5', 'SMA_20', 'SMA_60', 'DIF', 'DEA', 'Signal', 'Signal_Type', 'Trend_Status']].to_dict('records')
                except Exception as e:
                    print(f"⚠️ 构建最近交易信号列表失败: {e}")
                    recent_signals_list = []
            
            # 获取分析日期
            analysis_date = 'Unknown'
            if date_col:
                analysis_date = latest_data.get(date_col, 'Unknown')
            
            # 获取最新收盘价
            latest_close = 0
            if close_col:
                latest_close = latest_data.get(close_col, 0)
            
            analysis_result = {
                'symbol': symbol,
                'latest_close': latest_close,
                'latest_sma_5': latest_data.get('SMA_5', 0),
                'latest_sma_20': latest_data.get('SMA_20', 0),
                'latest_sma_60': latest_data.get('SMA_60', 0),
                'latest_dif': latest_data.get('DIF', 0),
                'latest_dea': latest_data.get('DEA', 0),
                'latest_macd': latest_data.get('MACD', 0),
                'current_signal_type': latest_data.get('Signal_Type', 'HOLD'),
                'trend_status': latest_data.get('Trend_Status', 'SIDEWAYS'),
                'macd_status': latest_data.get('MACD_Status', 'NEUTRAL'),
                'trend_strength': trend_strength,
                'ma_alignment': self._check_ma_alignment(latest_data),
                'macd_bullish': self._check_macd_bullish(latest_data),
                'recent_signals': recent_signals_list,
                'data_points': len(signal_data),
                'analysis_date': analysis_date
            }
            
            print(f"✅ {symbol} 趋势追踪分析完成")
            return analysis_result
            
        except Exception as e:
            print(f"❌ {symbol} 趋势追踪分析失败: {e}")
            return None
    
    def _calculate_trend_strength(self, data: pd.DataFrame) -> float:
        """
        计算趋势强度
        
        Args:
            data: 包含技术指标的DataFrame
            
        Returns:
            float: 趋势强度值（0-1之间）
        """
        if data is None or data.empty:
            return 0.0
        
        # 计算均线斜率
        sma_5_slope = data['SMA_5'].pct_change().rolling(5).mean().iloc[-1]
        sma_20_slope = data['SMA_20'].pct_change().rolling(5).mean().iloc[-1]
        
        # 计算MACD强度
        macd_strength = abs(data['MACD'].iloc[-1]) / data['MACD'].rolling(20).std().iloc[-1] if data['MACD'].rolling(20).std().iloc[-1] != 0 else 0
        
        # 综合趋势强度
        trend_strength = (abs(sma_5_slope) + abs(sma_20_slope) + macd_strength) / 3
        
        return min(trend_strength, 1.0)  # 限制在0-1之间
    
    def _check_ma_alignment(self, data: pd.Series) -> bool:
        """
        检查均线多头排列
        
        Args:
            data: 包含均线数据的Series
            
        Returns:
            bool: 是否为多头排列
        """
        return data['SMA_5'] > data['SMA_20'] > data['SMA_60']
    
    def _check_macd_bullish(self, data: pd.Series) -> bool:
        """
        检查MACD多头市场
        
        Args:
            data: 包含MACD数据的Series
            
        Returns:
            bool: 是否为MACD多头市场
        """
        return data['DIF'] > data['DEA'] > 0
    
    def get_trend_recommendations(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """
        获取多个股票的趋势追踪推荐
        
        Args:
            symbols: 股票代码列表
            
        Returns:
            List[Dict]: 推荐结果列表
        """
        recommendations = []
        
        print(f"🔍 开始分析 {len(symbols)} 个股票的趋势追踪指标...")
        
        for symbol in symbols:
            analysis = self.analyze_stock_trend(symbol)
            if analysis:
                recommendations.append(analysis)
        
        # 按趋势强度排序
        recommendations.sort(key=lambda x: x['trend_strength'], reverse=True)
        
        print(f"✅ 趋势追踪分析完成，共分析 {len(recommendations)} 个股票")
        return recommendations
    
    def print_trend_analysis(self, analysis_result: Dict[str, Any]):
        """
        打印趋势追踪分析结果
        
        Args:
            analysis_result: 分析结果字典
        """
        if not analysis_result:
            print("❌ 无分析结果可显示")
            return
        
        print(f"\n📊 {analysis_result['symbol']} 趋势追踪分析结果")
        print("=" * 60)
        print(f"分析日期: {analysis_result['analysis_date']}")
        print(f"数据点数: {analysis_result['data_points']}")
        print(f"当前收盘价: {analysis_result['latest_close']:.2f}")
        print(f"5日均线: {analysis_result['latest_sma_5']:.2f}")
        print(f"20日均线: {analysis_result['latest_sma_20']:.2f}")
        print(f"60日均线: {analysis_result['latest_sma_60']:.2f}")
        print(f"DIF: {analysis_result['latest_dif']:.4f}")
        print(f"DEA: {analysis_result['latest_dea']:.4f}")
        print(f"MACD: {analysis_result['latest_macd']:.4f}")
        print(f"交易信号: {analysis_result['current_signal_type']}")
        print(f"趋势状态: {analysis_result['trend_status']}")
        print(f"MACD状态: {analysis_result['macd_status']}")
        print(f"趋势强度: {analysis_result['trend_strength']:.2f}")
        print(f"均线多头排列: {'是' if analysis_result['ma_alignment'] else '否'}")
        print(f"MACD多头市场: {'是' if analysis_result['macd_bullish'] else '否'}")
        
        if analysis_result['recent_signals']:
            print(f"\n📈 最近交易信号:")
            for signal in analysis_result['recent_signals']:
                print(f"  {signal['日期']}: {signal['Signal_Type']} (收盘价: {signal['收盘']:.2f}, 趋势: {signal['Trend_Status']})")
