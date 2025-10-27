"""
个股突破买入策略
基于价格突破关键压力位、放量配合和布林带突破进行个股交易策略
核心逻辑：选择股价突破关键压力位（如前期高点、整理平台、年线）的个股，意味着上涨空间被打开
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, List
from ...repositories.stock.stock_query import StockQuery

class IndividualBreakoutStrategy:
    """个股突破买入策略类"""
    
    def __init__(self):
        """初始化策略"""
        self.stock_query = StockQuery()
        print("✅ 个股突破买入策略初始化成功")
    
    def calculate_bollinger_bands(self, data: pd.DataFrame, period: int = 20, std_dev: float = 2.0) -> pd.DataFrame:
        """
        计算布林带指标
        
        Args:
            data: 包含收盘价的DataFrame
            period: 移动平均周期
            std_dev: 标准差倍数
            
        Returns:
            DataFrame: 包含布林带指标的DataFrame
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
        
        # 计算移动平均线
        sma = data[close_col].rolling(window=period).mean()
        
        # 计算标准差
        std = data[close_col].rolling(window=period).std()
        
        # 计算上轨和下轨
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        # 计算布林带宽度
        bb_width = np.where(sma != 0, (upper_band - lower_band) / sma, 0)
        
        # 计算价格在布林带中的位置
        band_width = upper_band - lower_band
        bb_position = np.where(band_width != 0, (data[close_col] - lower_band) / band_width, 0.5)
        
        # 创建结果DataFrame
        result = data.copy()
        result['SMA'] = sma
        result['Upper_Band'] = upper_band
        result['Lower_Band'] = lower_band
        result['BB_Width'] = bb_width
        result['BB_Position'] = bb_position
        
        return result
    
    def calculate_volume_ratio(self, data: pd.DataFrame, period: int = 5) -> pd.DataFrame:
        """
        计算量比指标
        
        Args:
            data: 包含成交量的DataFrame
            period: 计算周期
            
        Returns:
            DataFrame: 包含量比指标的DataFrame
        """
        if data is None or data.empty:
            return None
        
        # 确保有成交量列
        volume_col = None
        for col in ['成交量', 'volume', 'Volume']:
            if col in data.columns:
                volume_col = col
                break
        
        if volume_col is None:
            print("❌ 未找到成交量列")
            return None
        
        # 计算平均成交量
        avg_volume = data[volume_col].rolling(window=period).mean()
        
        # 计算量比
        volume_ratio = np.where(avg_volume != 0, data[volume_col] / avg_volume, 1.0)
        
        # 创建结果DataFrame
        result = data.copy()
        result['Avg_Volume'] = avg_volume
        result['Volume_Ratio'] = volume_ratio
        
        return result
    
    def calculate_resistance_levels(self, data: pd.DataFrame, lookback_period: int = 60) -> pd.DataFrame:
        """
        计算阻力位
        
        Args:
            data: 包含价格数据的DataFrame
            lookback_period: 回望周期
            
        Returns:
            DataFrame: 包含阻力位的DataFrame
        """
        if data is None or data.empty:
            return None
        
        # 确保有最高价列
        high_col = None
        for col in ['最高', '最高价', 'high', 'High']:
            if col in data.columns:
                high_col = col
                break
        
        if high_col is None:
            print("❌ 未找到最高价列")
            return None
        
        # 计算不同周期的最高价
        resistance_20 = data[high_col].rolling(window=20).max()
        resistance_60 = data[high_col].rolling(window=60).max()
        resistance_120 = data[high_col].rolling(window=120).max()
        
        # 计算年线（250日均线）
        year_line = data['收盘'].rolling(window=250).mean()
        
        # 创建结果DataFrame
        result = data.copy()
        result['Resistance_20'] = resistance_20
        result['Resistance_60'] = resistance_60
        result['Resistance_120'] = resistance_120
        result['Year_Line'] = year_line
        
        return result
    
    def generate_breakout_signals(self, data: pd.DataFrame, volume_threshold: float = 1.2) -> pd.DataFrame:
        """
        生成突破买入交易信号
        
        Args:
            data: 包含技术指标的DataFrame
            volume_threshold: 量比阈值
            
        Returns:
            DataFrame: 包含交易信号的DataFrame
        """
        if data is None or data.empty:
            return None
        
        # 检查必要的列
        required_cols = ['收盘', 'Upper_Band', 'Volume_Ratio', 'Resistance_20', 'Resistance_60', 'Year_Line']
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
        result['Breakout_Type'] = 'NONE'
        result['Volume_Status'] = 'NORMAL'
        
        close_price = result[close_col]
        upper_band = result['Upper_Band']
        volume_ratio = result['Volume_Ratio']
        resistance_20 = result['Resistance_20']
        resistance_60 = result['Resistance_60']
        year_line = result['Year_Line']
        
        # 1. 布林带上轨突破
        bollinger_breakout = (close_price > upper_band) & (close_price.shift(1) <= upper_band.shift(1))
        
        # 2. 20日阻力位突破
        resistance_20_breakout = (close_price > resistance_20) & (close_price.shift(1) <= resistance_20.shift(1))
        
        # 3. 60日阻力位突破
        resistance_60_breakout = (close_price > resistance_60) & (close_price.shift(1) <= resistance_60.shift(1))
        
        # 4. 年线突破
        year_line_breakout = (close_price > year_line) & (close_price.shift(1) <= year_line.shift(1))
        
        # 5. 放量确认
        volume_confirmation = volume_ratio > volume_threshold
        
        # 6. 强势突破：布林带上轨突破 + 放量
        strong_bollinger_breakout = bollinger_breakout & volume_confirmation
        
        # 7. 重要阻力位突破：60日阻力位突破 + 放量
        important_resistance_breakout = resistance_60_breakout & volume_confirmation
        
        # 8. 年线突破：年线突破 + 放量
        year_line_breakout_confirmed = year_line_breakout & volume_confirmation
        
        # 9. 多重突破：同时突破多个阻力位
        multi_breakout = (resistance_20_breakout | resistance_60_breakout) & volume_confirmation
        
        # 设置信号
        result.loc[strong_bollinger_breakout, 'Signal'] = 2
        result.loc[strong_bollinger_breakout, 'Signal_Type'] = 'STRONG_BUY'
        result.loc[strong_bollinger_breakout, 'Breakout_Type'] = 'BOLLINGER_BREAKOUT'
        result.loc[strong_bollinger_breakout, 'Volume_Status'] = 'HIGH'
        
        result.loc[important_resistance_breakout, 'Signal'] = 2
        result.loc[important_resistance_breakout, 'Signal_Type'] = 'STRONG_BUY'
        result.loc[important_resistance_breakout, 'Breakout_Type'] = 'RESISTANCE_BREAKOUT'
        result.loc[important_resistance_breakout, 'Volume_Status'] = 'HIGH'
        
        result.loc[year_line_breakout_confirmed, 'Signal'] = 2
        result.loc[year_line_breakout_confirmed, 'Signal_Type'] = 'STRONG_BUY'
        result.loc[year_line_breakout_confirmed, 'Breakout_Type'] = 'YEAR_LINE_BREAKOUT'
        result.loc[year_line_breakout_confirmed, 'Volume_Status'] = 'HIGH'
        
        result.loc[multi_breakout & ~strong_bollinger_breakout & ~important_resistance_breakout & ~year_line_breakout_confirmed, 'Signal'] = 1
        result.loc[multi_breakout & ~strong_bollinger_breakout & ~important_resistance_breakout & ~year_line_breakout_confirmed, 'Signal_Type'] = 'BUY'
        result.loc[multi_breakout & ~strong_bollinger_breakout & ~important_resistance_breakout & ~year_line_breakout_confirmed, 'Breakout_Type'] = 'MULTI_BREAKOUT'
        result.loc[multi_breakout & ~strong_bollinger_breakout & ~important_resistance_breakout & ~year_line_breakout_confirmed, 'Volume_Status'] = 'HIGH'
        
        # 普通突破信号（无放量确认）
        result.loc[bollinger_breakout & ~volume_confirmation, 'Signal'] = 1
        result.loc[bollinger_breakout & ~volume_confirmation, 'Signal_Type'] = 'BUY'
        result.loc[bollinger_breakout & ~volume_confirmation, 'Breakout_Type'] = 'BOLLINGER_BREAKOUT'
        result.loc[bollinger_breakout & ~volume_confirmation, 'Volume_Status'] = 'NORMAL'
        
        result.loc[resistance_20_breakout & ~volume_confirmation, 'Signal'] = 1
        result.loc[resistance_20_breakout & ~volume_confirmation, 'Signal_Type'] = 'BUY'
        result.loc[resistance_20_breakout & ~volume_confirmation, 'Breakout_Type'] = 'RESISTANCE_20_BREAKOUT'
        result.loc[resistance_20_breakout & ~volume_confirmation, 'Volume_Status'] = 'NORMAL'
        
        # 设置成交量状态
        result.loc[volume_ratio > volume_threshold, 'Volume_Status'] = 'HIGH'
        result.loc[volume_ratio < 0.8, 'Volume_Status'] = 'LOW'
        
        return result
    
    def analyze_stock_breakout(self, symbol: str, start_date: str = None, end_date: str = None) -> Optional[Dict[str, Any]]:
        """
        分析个股突破买入指标
        
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
            
            # 计算布林带指标
            bb_data = self.calculate_bollinger_bands(hist_data)
            if bb_data is None:
                return None
            
            # 计算量比指标
            volume_data = self.calculate_volume_ratio(bb_data)
            if volume_data is None:
                return None
            
            # 计算阻力位
            resistance_data = self.calculate_resistance_levels(volume_data)
            if resistance_data is None:
                return None
            
            # 生成交易信号
            signal_data = self.generate_breakout_signals(resistance_data)
            if signal_data is None:
                return None
            
            # 分析结果
            latest_data = signal_data.iloc[-1]
            recent_signals = signal_data[signal_data['Signal'] != 0].tail(5)
            
            # 计算突破强度
            breakout_strength = self._calculate_breakout_strength(signal_data)
            
            analysis_result = {
                'symbol': symbol,
                'latest_close': latest_data.get('收盘', latest_data.get('收盘价', latest_data.get('close', latest_data.get('Close', 0)))),
                'latest_upper_band': latest_data['Upper_Band'],
                'latest_resistance_20': latest_data['Resistance_20'],
                'latest_resistance_60': latest_data['Resistance_60'],
                'latest_year_line': latest_data['Year_Line'],
                'latest_volume_ratio': latest_data['Volume_Ratio'],
                'current_signal_type': latest_data['Signal_Type'],
                'breakout_type': latest_data['Breakout_Type'],
                'volume_status': latest_data['Volume_Status'],
                'breakout_strength': breakout_strength,
                'bollinger_position': self._check_bollinger_position(latest_data),
                'resistance_distance': self._calculate_resistance_distance(latest_data),
                'recent_signals': recent_signals[['日期', '收盘', 'Upper_Band', 'Resistance_20', 'Resistance_60', 'Volume_Ratio', 'Signal', 'Signal_Type', 'Breakout_Type']].to_dict('records') if not recent_signals.empty else [],
                'data_points': len(signal_data),
                'analysis_date': latest_data.get('日期', 'Unknown')
            }
            
            print(f"✅ {symbol} 突破买入分析完成")
            return analysis_result
            
        except Exception as e:
            print(f"❌ {symbol} 突破买入分析失败: {e}")
            return None
    
    def _calculate_breakout_strength(self, data: pd.DataFrame) -> float:
        """
        计算突破强度
        
        Args:
            data: 包含技术指标的DataFrame
            
        Returns:
            float: 突破强度值（0-1之间）
        """
        if data is None or data.empty:
            return 0.0
        
        # 计算价格突破幅度
        close_price = data['收盘']
        upper_band = data['Upper_Band']
        resistance_60 = data['Resistance_60']
        
        # 布林带突破幅度
        bb_breakout_ratio = (close_price - upper_band) / upper_band if upper_band.iloc[-1] != 0 else 0
        
        # 阻力位突破幅度
        resistance_breakout_ratio = (close_price - resistance_60) / resistance_60 if resistance_60.iloc[-1] != 0 else 0
        
        # 量比强度
        volume_strength = min(data['Volume_Ratio'].iloc[-1] / 2.0, 1.0)  # 量比2倍为满分
        
        # 综合突破强度
        breakout_strength = (abs(bb_breakout_ratio) + abs(resistance_breakout_ratio) + volume_strength) / 3
        
        return min(breakout_strength, 1.0)  # 限制在0-1之间
    
    def _check_bollinger_position(self, data: pd.Series) -> str:
        """
        检查布林带位置
        
        Args:
            data: 包含布林带数据的Series
            
        Returns:
            str: 布林带位置状态
        """
        close_price = data.get('收盘', 0)
        upper_band = data.get('Upper_Band', 0)
        lower_band = data.get('Lower_Band', 0)
        
        if close_price > upper_band:
            return 'ABOVE_UPPER'
        elif close_price < lower_band:
            return 'BELOW_LOWER'
        else:
            return 'WITHIN_BANDS'
    
    def _calculate_resistance_distance(self, data: pd.Series) -> float:
        """
        计算距离阻力位的距离
        
        Args:
            data: 包含价格数据的Series
            
        Returns:
            float: 距离阻力位的百分比
        """
        close_price = data.get('收盘', 0)
        resistance_60 = data.get('Resistance_60', 0)
        
        if resistance_60 == 0:
            return 0.0
        
        return (close_price - resistance_60) / resistance_60 * 100
    
    def get_breakout_recommendations(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """
        获取多个股票的突破买入推荐
        
        Args:
            symbols: 股票代码列表
            
        Returns:
            List[Dict]: 推荐结果列表
        """
        recommendations = []
        
        print(f"🔍 开始分析 {len(symbols)} 个股票的突破买入指标...")
        
        for symbol in symbols:
            analysis = self.analyze_stock_breakout(symbol)
            if analysis:
                recommendations.append(analysis)
        
        # 按突破强度排序
        recommendations.sort(key=lambda x: x['breakout_strength'], reverse=True)
        
        print(f"✅ 突破买入分析完成，共分析 {len(recommendations)} 个股票")
        return recommendations
    
    def print_breakout_analysis(self, analysis_result: Dict[str, Any]):
        """
        打印突破买入分析结果
        
        Args:
            analysis_result: 分析结果字典
        """
        if not analysis_result:
            print("❌ 无分析结果可显示")
            return
        
        print(f"\n📊 {analysis_result['symbol']} 突破买入分析结果")
        print("=" * 60)
        print(f"分析日期: {analysis_result['analysis_date']}")
        print(f"数据点数: {analysis_result['data_points']}")
        print(f"当前收盘价: {analysis_result['latest_close']:.2f}")
        print(f"布林带上轨: {analysis_result['latest_upper_band']:.2f}")
        print(f"20日阻力位: {analysis_result['latest_resistance_20']:.2f}")
        print(f"60日阻力位: {analysis_result['latest_resistance_60']:.2f}")
        print(f"年线: {analysis_result['latest_year_line']:.2f}")
        print(f"量比: {analysis_result['latest_volume_ratio']:.2f}")
        print(f"交易信号: {analysis_result['current_signal_type']}")
        print(f"突破类型: {analysis_result['breakout_type']}")
        print(f"成交量状态: {analysis_result['volume_status']}")
        print(f"突破强度: {analysis_result['breakout_strength']:.2f}")
        print(f"布林带位置: {analysis_result['bollinger_position']}")
        print(f"距离阻力位: {analysis_result['resistance_distance']:.2f}%")
        
        if analysis_result['recent_signals']:
            print(f"\n📈 最近交易信号:")
            for signal in analysis_result['recent_signals']:
                print(f"  {signal['日期']}: {signal['Signal_Type']} (收盘价: {signal['收盘']:.2f}, 类型: {signal['Breakout_Type']})")
