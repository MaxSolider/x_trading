"""
行业板块MACD策略
基于MACD指标进行行业板块交易策略
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, List
from ...repositories.industry_info_query import IndustryInfoQuery

class IndustryMACDStrategy:
    """行业板块MACD策略类"""
    
    def __init__(self):
        """初始化策略"""
        self.industry_query = IndustryInfoQuery()
        print("✅ 行业板块MACD策略初始化成功")
    
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
        
        # 计算MACD线
        macd_line = ema_fast - ema_slow
        
        # 计算信号线
        signal_line = macd_line.ewm(span=signal_period).mean()
        
        # 计算柱状图
        histogram = macd_line - signal_line
        
        # 创建结果DataFrame
        result = data.copy()
        result['EMA_Fast'] = ema_fast
        result['EMA_Slow'] = ema_slow
        result['MACD'] = macd_line
        result['Signal'] = signal_line
        result['Histogram'] = histogram
        
        return result
    
    def generate_macd_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        生成MACD交易信号
        
        Args:
            data: 包含MACD指标的DataFrame
            
        Returns:
            DataFrame: 包含交易信号的DataFrame
        """
        if data is None or data.empty or 'MACD' not in data.columns:
            return None
        
        result = data.copy()
        
        # 初始化信号列
        result['Signal'] = 0
        result['Signal_Type'] = 'HOLD'
        
        # 计算MACD和信号线的交叉
        macd = result['MACD']
        signal = result['Signal']
        
        # 金叉信号（买入）
        golden_cross = (macd > signal) & (macd.shift(1) <= signal.shift(1))
        result.loc[golden_cross, 'Signal'] = 1
        result.loc[golden_cross, 'Signal_Type'] = 'BUY'
        
        # 死叉信号（卖出）
        death_cross = (macd < signal) & (macd.shift(1) >= signal.shift(1))
        result.loc[death_cross, 'Signal'] = -1
        result.loc[death_cross, 'Signal_Type'] = 'SELL'
        
        # MACD零轴突破
        zero_cross_up = (macd > 0) & (macd.shift(1) <= 0)
        zero_cross_down = (macd < 0) & (macd.shift(1) >= 0)
        
        result.loc[zero_cross_up, 'Zero_Cross'] = 'UP'
        result.loc[zero_cross_down, 'Zero_Cross'] = 'DOWN'
        
        return result
    
    def analyze_industry_macd(self, industry_name: str, start_date: str = None, end_date: str = None) -> Optional[Dict[str, Any]]:
        """
        分析行业板块MACD指标
        
        Args:
            industry_name: 行业板块名称
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            Dict: 包含分析结果的字典
        """
        try:
            # 获取行业板块历史数据
            hist_data = self.industry_query.get_board_industry_hist(industry_name, start_date, end_date)
            
            if hist_data is None or hist_data.empty:
                print(f"❌ 无法获取 {industry_name} 的历史数据")
                return None
            
            # 计算MACD指标
            macd_data = self.calculate_macd(hist_data)
            if macd_data is None:
                return None
            
            # 生成交易信号
            signal_data = self.generate_macd_signals(macd_data)
            if signal_data is None:
                return None
            
            # 分析结果
            latest_data = signal_data.iloc[-1]
            recent_signals = signal_data[signal_data['Signal'] != 0].tail(5)
            
            # 获取日期列名
            date_col = None
            for col in ['日期', 'date', 'Date']:
                if col in recent_signals.columns:
                    date_col = col
                    break
            
            # 构建recent_signals列表
            recent_signals_list = []
            if not recent_signals.empty and date_col:
                try:
                    recent_signals_list = recent_signals[[date_col, 'MACD', 'Signal', 'Signal_Type']].to_dict('records')
                except Exception as e:
                    print(f"⚠️ 构建recent_signals列表失败: {e}")
                    recent_signals_list = []
            
            analysis_result = {
                'industry_name': industry_name,
                'latest_macd': latest_data['MACD'],
                'latest_signal': latest_data['Signal'],
                'latest_histogram': latest_data['Histogram'],
                'current_signal_type': latest_data['Signal_Type'],
                'zero_cross_status': latest_data.get('Zero_Cross', 'NONE'),
                'recent_signals': recent_signals_list,
                'data_points': len(signal_data),
                'analysis_date': latest_data.get(date_col if date_col else '日期', 'Unknown')
            }
            
            print(f"✅ {industry_name} MACD分析完成")
            return analysis_result
            
        except Exception as e:
            print(f"❌ {industry_name} MACD分析失败: {e}")
            return None
    
    def analyze_industry_macd_with_data(self, industry_name: str, hist_data: pd.DataFrame, end_date: str) -> Optional[Dict[str, Any]]:
        """
        使用传入的数据分析行业板块MACD指标
        
        Args:
            industry_name: 行业板块名称
            hist_data: 历史数据DataFrame
            end_date: 结束日期
            
        Returns:
            Dict: 包含分析结果的字典
        """
        try:
            if hist_data is None or hist_data.empty:
                print(f"❌ {industry_name} 历史数据为空")
                return None
            
            # 计算MACD指标
            macd_data = self.calculate_macd(hist_data)
            if macd_data is None:
                return None
            
            # 生成交易信号
            signal_data = self.generate_macd_signals(macd_data)
            if signal_data is None:
                return None
            
            # 分析结果
            latest_data = signal_data.iloc[-1]
            recent_signals = signal_data[signal_data['Signal'] != 0].tail(5)
            
            # 获取日期列名
            date_col = None
            for col in ['日期', 'date', 'Date']:
                if col in recent_signals.columns:
                    date_col = col
                    break
            
            # 构建recent_signals列表
            recent_signals_list = []
            if not recent_signals.empty and date_col:
                try:
                    recent_signals_list = recent_signals[[date_col, 'MACD', 'Signal', 'Signal_Type']].to_dict('records')
                except Exception as e:
                    print(f"⚠️ 构建recent_signals列表失败: {e}")
                    recent_signals_list = []
            
            analysis_result = {
                'industry_name': industry_name,
                'latest_macd': latest_data['MACD'],
                'latest_signal': latest_data['Signal'],
                'latest_histogram': latest_data['Histogram'],
                'current_signal_type': latest_data['Signal_Type'],
                'zero_cross_status': latest_data.get('Zero_Cross', 'NONE'),
                'recent_signals': recent_signals_list,
                'data_points': len(signal_data),
                'analysis_date': end_date
            }
            
            print(f"✅ {industry_name} MACD分析完成")
            return analysis_result
            
        except Exception as e:
            print(f"❌ {industry_name} MACD分析失败: {e}")
            return None
    
    def get_macd_recommendations(self, industry_names: List[str]) -> List[Dict[str, Any]]:
        """
        获取多个行业板块的MACD推荐
        
        Args:
            industry_names: 行业板块名称列表
            
        Returns:
            List[Dict]: 推荐结果列表
        """
        recommendations = []
        
        print(f"🔍 开始分析 {len(industry_names)} 个行业板块的MACD指标...")
        
        for industry_name in industry_names:
            analysis = self.analyze_industry_macd(industry_name)
            if analysis:
                recommendations.append(analysis)
        
        # 按MACD值排序
        recommendations.sort(key=lambda x: abs(x['latest_macd']), reverse=True)
        
        print(f"✅ MACD分析完成，共分析 {len(recommendations)} 个行业板块")
        return recommendations
    
    def print_macd_analysis(self, analysis_result: Dict[str, Any]):
        """
        打印MACD分析结果
        
        Args:
            analysis_result: 分析结果字典
        """
        if not analysis_result:
            print("❌ 无分析结果可显示")
            return
        
        print(f"\n📊 {analysis_result['industry_name']} MACD分析结果")
        print("=" * 60)
        print(f"分析日期: {analysis_result['analysis_date']}")
        print(f"数据点数: {analysis_result['data_points']}")
        print(f"当前MACD: {analysis_result['latest_macd']:.4f}")
        print(f"当前信号线: {analysis_result['latest_signal']:.4f}")
        print(f"当前柱状图: {analysis_result['latest_histogram']:.4f}")
        print(f"交易信号: {analysis_result['current_signal_type']}")
        print(f"零轴状态: {analysis_result['zero_cross_status']}")
        
        if analysis_result['recent_signals']:
            print(f"\n📈 最近交易信号:")
            for signal in analysis_result['recent_signals']:
                print(f"  {signal['日期']}: {signal['Signal_Type']} (MACD: {signal['MACD']:.4f})")
