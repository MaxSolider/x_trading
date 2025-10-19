"""
行业板块布林带策略
基于布林带指标进行行业板块交易策略
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, List
from ...repositories.stock.industry_info_query import IndustryInfoQuery

class IndustryBollingerBandsStrategy:
    """行业板块布林带策略类"""
    
    def __init__(self):
        """初始化策略"""
        self.industry_query = IndustryInfoQuery()
        print("✅ 行业板块布林带策略初始化成功")
    
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
        for col in ['收盘价', 'close', 'Close']:
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
        bb_width = (upper_band - lower_band) / sma
        
        # 计算价格在布林带中的位置
        bb_position = (data[close_col] - lower_band) / (upper_band - lower_band)
        
        # 创建结果DataFrame
        result = data.copy()
        result['SMA'] = sma
        result['Upper_Band'] = upper_band
        result['Lower_Band'] = lower_band
        result['BB_Width'] = bb_width
        result['BB_Position'] = bb_position
        
        return result
    
    def generate_bollinger_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        生成布林带交易信号
        
        Args:
            data: 包含布林带指标的DataFrame
            
        Returns:
            DataFrame: 包含交易信号的DataFrame
        """
        if data is None or data.empty or 'Upper_Band' not in data.columns:
            return None
        
        result = data.copy()
        
        # 确保有收盘价列
        close_col = None
        for col in ['收盘价', 'close', 'Close']:
            if col in data.columns:
                close_col = col
                break
        
        if close_col is None:
            return None
        
        # 初始化信号列
        result['Signal'] = 0
        result['Signal_Type'] = 'HOLD'
        result['BB_Status'] = 'NORMAL'
        
        close_price = result[close_col]
        upper_band = result['Upper_Band']
        lower_band = result['Lower_Band']
        sma = result['SMA']
        bb_position = result['BB_Position']
        
        # 价格触及下轨（买入信号）
        lower_touch = (close_price <= lower_band) & (close_price.shift(1) > lower_band.shift(1))
        result.loc[lower_touch, 'Signal'] = 1
        result.loc[lower_touch, 'Signal_Type'] = 'BUY'
        result.loc[lower_touch, 'BB_Status'] = 'LOWER_TOUCH'
        
        # 价格触及上轨（卖出信号）
        upper_touch = (close_price >= upper_band) & (close_price.shift(1) < upper_band.shift(1))
        result.loc[upper_touch, 'Signal'] = -1
        result.loc[upper_touch, 'Signal_Type'] = 'SELL'
        result.loc[upper_touch, 'BB_Status'] = 'UPPER_TOUCH'
        
        # 价格从下轨反弹
        lower_bounce = (close_price > lower_band) & (close_price.shift(1) <= lower_band.shift(1)) & (close_price.shift(2) <= lower_band.shift(2))
        result.loc[lower_bounce, 'Signal'] = 1
        result.loc[lower_bounce, 'Signal_Type'] = 'BUY'
        result.loc[lower_bounce, 'BB_Status'] = 'LOWER_BOUNCE'
        
        # 价格从上轨回落
        upper_fall = (close_price < upper_band) & (close_price.shift(1) >= upper_band.shift(1)) & (close_price.shift(2) >= upper_band.shift(2))
        result.loc[upper_fall, 'Signal'] = -1
        result.loc[upper_fall, 'Signal_Type'] = 'SELL'
        result.loc[upper_fall, 'BB_Status'] = 'UPPER_FALL'
        
        # 布林带收窄（波动性降低）
        bb_squeeze = (result['BB_Width'] < result['BB_Width'].rolling(20).mean() * 0.8)
        result.loc[bb_squeeze, 'BB_Status'] = 'SQUEEZE'
        
        # 布林带扩张（波动性增加）
        bb_expansion = (result['BB_Width'] > result['BB_Width'].rolling(20).mean() * 1.2)
        result.loc[bb_expansion, 'BB_Status'] = 'EXPANSION'
        
        return result
    
    def analyze_industry_bollinger(self, industry_name: str, start_date: str = None, end_date: str = None,
                                period: int = 20, std_dev: float = 2.0) -> Optional[Dict[str, Any]]:
        """
        分析行业板块布林带指标
        
        Args:
            industry_name: 行业板块名称
            start_date: 开始日期
            end_date: 结束日期
            period: 移动平均周期
            std_dev: 标准差倍数
            
        Returns:
            Dict: 包含分析结果的字典
        """
        try:

            # 获取行业板块历史数据
            hist_data = self.industry_query.get_board_industry_hist(industry_name, start_date, end_date)
            
            if hist_data is None or hist_data.empty:
                print(f"❌ 无法获取 {industry_name} 的历史数据")
                return None
            
            # 计算布林带指标
            bb_data = self.calculate_bollinger_bands(hist_data, period, std_dev)
            if bb_data is None:
                return None
            
            # 生成交易信号
            signal_data = self.generate_bollinger_signals(bb_data)
            if signal_data is None:
                return None
            
            # 分析结果
            latest_data = signal_data.iloc[-1]
            recent_signals = signal_data[signal_data['Signal'] != 0].tail(5)
            
            # 计算布林带统计信息
            bb_width_values = signal_data['BB_Width'].dropna()
            bb_width_mean = bb_width_values.mean()
            bb_width_std = bb_width_values.std()
            
            bb_position_values = signal_data['BB_Position'].dropna()
            bb_position_mean = bb_position_values.mean()
            
            analysis_result = {
                'industry_name': industry_name,
                'latest_close': latest_data.get('收盘价', latest_data.get('close', latest_data.get('Close', 0))),
                'latest_sma': latest_data['SMA'],
                'latest_upper_band': latest_data['Upper_Band'],
                'latest_lower_band': latest_data['Lower_Band'],
                'latest_bb_width': latest_data['BB_Width'],
                'latest_bb_position': latest_data['BB_Position'],
                'current_signal_type': latest_data['Signal_Type'],
                'bb_status': latest_data['BB_Status'],
                'bb_width_mean': bb_width_mean,
                'bb_width_std': bb_width_std,
                'bb_position_mean': bb_position_mean,
                'period': period,
                'std_dev': std_dev,
                'recent_signals': recent_signals[['日期', '收盘价', 'SMA', 'Upper_Band', 'Lower_Band', 'Signal', 'Signal_Type', 'BB_Status']].to_dict('records') if not recent_signals.empty else [],
                'data_points': len(signal_data),
                'analysis_date': latest_data.get('日期', 'Unknown')
            }
            
            print(f"✅ {industry_name} 布林带分析完成")
            return analysis_result
            
        except Exception as e:
            print(f"❌ {industry_name} 布林带分析失败: {e}")
            return None
    
    def get_bollinger_recommendations(self, industry_names: List[str], period: int = 20, 
                                    std_dev: float = 2.0) -> List[Dict[str, Any]]:
        """
        获取多个行业板块的布林带推荐
        
        Args:
            industry_names: 行业板块名称列表
            period: 移动平均周期
            std_dev: 标准差倍数
            
        Returns:
            List[Dict]: 推荐结果列表
        """
        recommendations = []
        
        print(f"🔍 开始分析 {len(industry_names)} 个行业板块的布林带指标...")
        
        for industry_name in industry_names:
            analysis = self.analyze_industry_bollinger(industry_name, period=period, std_dev=std_dev)
            if analysis:
                recommendations.append(analysis)
        
        # 按布林带位置偏离程度排序（距离0.5越远越重要）
        recommendations.sort(key=lambda x: abs(x['latest_bb_position'] - 0.5), reverse=True)
        
        print(f"✅ 布林带分析完成，共分析 {len(recommendations)} 个行业板块")
        return recommendations
    
    def print_bollinger_analysis(self, analysis_result: Dict[str, Any]):
        """
        打印布林带分析结果
        
        Args:
            analysis_result: 分析结果字典
        """
        if not analysis_result:
            print("❌ 无分析结果可显示")
            return
        
        print(f"\n📊 {analysis_result['industry_name']} 布林带分析结果")
        print("=" * 60)
        print(f"分析日期: {analysis_result['analysis_date']}")
        print(f"数据点数: {analysis_result['data_points']}")
        print(f"当前收盘价: {analysis_result['latest_close']:.2f}")
        print(f"移动平均线: {analysis_result['latest_sma']:.2f}")
        print(f"上轨: {analysis_result['latest_upper_band']:.2f}")
        print(f"下轨: {analysis_result['latest_lower_band']:.2f}")
        print(f"布林带宽度: {analysis_result['latest_bb_width']:.4f}")
        print(f"布林带位置: {analysis_result['latest_bb_position']:.2f}")
        print(f"交易信号: {analysis_result['current_signal_type']}")
        print(f"布林带状态: {analysis_result['bb_status']}")
        print(f"布林带宽度均值: {analysis_result['bb_width_mean']:.4f}")
        print(f"布林带位置均值: {analysis_result['bb_position_mean']:.2f}")
        
        if analysis_result['recent_signals']:
            print(f"\n📈 最近交易信号:")
            for signal in analysis_result['recent_signals']:
                print(f"  {signal['日期']}: {signal['Signal_Type']} (收盘价: {signal['收盘价']:.2f}, 状态: {signal['BB_Status']})")
