"""
行业板块RSI策略
基于RSI指标进行行业板块交易策略
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, List
from ...repositories.stock.industry_info_query import IndustryInfoQuery

class IndustryRSIStrategy:
    """行业板块RSI策略类"""
    
    def __init__(self):
        """初始化策略"""
        self.industry_query = IndustryInfoQuery()
        print("✅ 行业板块RSI策略初始化成功")
    
    def calculate_rsi(self, data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        计算RSI指标
        
        Args:
            data: 包含收盘价的DataFrame
            period: RSI计算周期
            
        Returns:
            DataFrame: 包含RSI指标的DataFrame
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
        
        # 计算价格变化
        price_change = data[close_col].diff()
        
        # 分离上涨和下跌
        gains = price_change.where(price_change > 0, 0)
        losses = -price_change.where(price_change < 0, 0)
        
        # 计算平均收益和平均损失
        avg_gains = gains.rolling(window=period).mean()
        avg_losses = losses.rolling(window=period).mean()
        
        # 计算RS（避免除零错误）
        rs = np.where(avg_losses != 0, avg_gains / avg_losses, np.inf)
        
        # 计算RSI
        rsi = 100 - (100 / (1 + rs))
        
        # 创建结果DataFrame
        result = data.copy()
        result['Price_Change'] = price_change
        result['Gains'] = gains
        result['Losses'] = losses
        result['Avg_Gains'] = avg_gains
        result['Avg_Losses'] = avg_losses
        result['RS'] = rs
        result['RSI'] = rsi
        
        return result
    
    def generate_rsi_signals(self, data: pd.DataFrame, oversold: float = 30, overbought: float = 70) -> pd.DataFrame:
        """
        生成RSI交易信号
        
        Args:
            data: 包含RSI指标的DataFrame
            oversold: 超卖阈值
            overbought: 超买阈值
            
        Returns:
            DataFrame: 包含交易信号的DataFrame
        """
        if data is None or data.empty or 'RSI' not in data.columns:
            return None
        
        result = data.copy()
        
        # 初始化信号列
        result['Signal'] = 0
        result['Signal_Type'] = 'HOLD'
        result['RSI_Status'] = 'NORMAL'
        
        rsi = result['RSI']
        
        # 超卖信号（买入）
        oversold_signal = (rsi < oversold) & (rsi.shift(1) >= oversold)
        result.loc[oversold_signal, 'Signal'] = 1
        result.loc[oversold_signal, 'Signal_Type'] = 'BUY'
        result.loc[oversold_signal, 'RSI_Status'] = 'OVERSOLD'
        
        # 超买信号（卖出）
        overbought_signal = (rsi > overbought) & (rsi.shift(1) <= overbought)
        result.loc[overbought_signal, 'Signal'] = -1
        result.loc[overbought_signal, 'Signal_Type'] = 'SELL'
        result.loc[overbought_signal, 'RSI_Status'] = 'OVERBOUGHT'
        
        # RSI从超卖区域回升
        rsi_recovery = (rsi > oversold) & (rsi.shift(1) <= oversold) & (rsi.shift(2) <= oversold)
        result.loc[rsi_recovery, 'Signal'] = 1
        result.loc[rsi_recovery, 'Signal_Type'] = 'BUY'
        result.loc[rsi_recovery, 'RSI_Status'] = 'RECOVERY'
        
        # RSI从超买区域回落
        rsi_decline = (rsi < overbought) & (rsi.shift(1) >= overbought) & (rsi.shift(2) >= overbought)
        result.loc[rsi_decline, 'Signal'] = -1
        result.loc[rsi_decline, 'Signal_Type'] = 'SELL'
        result.loc[rsi_decline, 'RSI_Status'] = 'DECLINE'
        
        return result
    
    def analyze_industry_rsi(self, industry_name: str, start_date: str = None, end_date: str = None, 
                           period: int = 14, oversold: float = 30, overbought: float = 70) -> Optional[Dict[str, Any]]:
        """
        分析行业板块RSI指标
        
        Args:
            industry_name: 行业板块名称
            start_date: 开始日期
            end_date: 结束日期
            period: RSI计算周期
            oversold: 超卖阈值
            overbought: 超买阈值
            
        Returns:
            Dict: 包含分析结果的字典
        """
        try:

            # 获取行业板块历史数据
            hist_data = self.industry_query.get_board_industry_hist(industry_name, start_date, end_date)
            
            if hist_data is None or hist_data.empty:
                print(f"❌ 无法获取 {industry_name} 的历史数据")
                return None
            
            # 计算RSI指标
            rsi_data = self.calculate_rsi(hist_data, period)
            if rsi_data is None:
                return None
            
            # 生成交易信号
            signal_data = self.generate_rsi_signals(rsi_data, oversold, overbought)
            if signal_data is None:
                return None
            
            # 分析结果
            latest_data = signal_data.iloc[-1]
            recent_signals = signal_data[signal_data['Signal'] != 0].tail(5)
            
            # 计算RSI统计信息
            rsi_values = signal_data['RSI'].dropna()
            rsi_mean = rsi_values.mean()
            rsi_std = rsi_values.std()
            
            analysis_result = {
                'industry_name': industry_name,
                'latest_rsi': latest_data['RSI'],
                'current_signal_type': latest_data['Signal_Type'],
                'rsi_status': latest_data['RSI_Status'],
                'rsi_mean': rsi_mean,
                'rsi_std': rsi_std,
                'oversold_threshold': oversold,
                'overbought_threshold': overbought,
                'recent_signals': recent_signals[['日期', 'RSI', 'Signal', 'Signal_Type', 'RSI_Status']].to_dict('records') if not recent_signals.empty else [],
                'data_points': len(signal_data),
                'analysis_date': latest_data.get('日期', 'Unknown')
            }
            
            print(f"✅ {industry_name} RSI分析完成")
            return analysis_result
            
        except Exception as e:
            print(f"❌ {industry_name} RSI分析失败: {e}")
            return None
    
    def get_rsi_recommendations(self, industry_names: List[str], period: int = 14, 
                              oversold: float = 30, overbought: float = 70) -> List[Dict[str, Any]]:
        """
        获取多个行业板块的RSI推荐
        
        Args:
            industry_names: 行业板块名称列表
            period: RSI计算周期
            oversold: 超卖阈值
            overbought: 超买阈值
            
        Returns:
            List[Dict]: 推荐结果列表
        """
        recommendations = []
        
        print(f"🔍 开始分析 {len(industry_names)} 个行业板块的RSI指标...")
        
        for industry_name in industry_names:
            analysis = self.analyze_industry_rsi(industry_name, period=period, 
                                               oversold=oversold, overbought=overbought)
            if analysis:
                recommendations.append(analysis)
        
        # 按RSI偏离程度排序（距离50越远越重要）
        recommendations.sort(key=lambda x: abs(x['latest_rsi'] - 50), reverse=True)
        
        print(f"✅ RSI分析完成，共分析 {len(recommendations)} 个行业板块")
        return recommendations
    
    def print_rsi_analysis(self, analysis_result: Dict[str, Any]):
        """
        打印RSI分析结果
        
        Args:
            analysis_result: 分析结果字典
        """
        if not analysis_result:
            print("❌ 无分析结果可显示")
            return
        
        print(f"\n📊 {analysis_result['industry_name']} RSI分析结果")
        print("=" * 60)
        print(f"分析日期: {analysis_result['analysis_date']}")
        print(f"数据点数: {analysis_result['data_points']}")
        print(f"当前RSI: {analysis_result['latest_rsi']:.2f}")
        print(f"RSI均值: {analysis_result['rsi_mean']:.2f}")
        print(f"RSI标准差: {analysis_result['rsi_std']:.2f}")
        print(f"交易信号: {analysis_result['current_signal_type']}")
        print(f"RSI状态: {analysis_result['rsi_status']}")
        print(f"超卖阈值: {analysis_result['oversold_threshold']}")
        print(f"超买阈值: {analysis_result['overbought_threshold']}")
        
        if analysis_result['recent_signals']:
            print(f"\n📈 最近交易信号:")
            for signal in analysis_result['recent_signals']:
                print(f"  {signal['日期']}: {signal['Signal_Type']} (RSI: {signal['RSI']:.2f}, 状态: {signal['RSI_Status']})")
