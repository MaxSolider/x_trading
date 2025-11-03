"""
个股超跌反弹策略
基于KDJ超卖和RSI超卖进行个股交易策略
核心逻辑：寻找短期内跌幅过大、有反弹需求的个股，属于"捡便宜"策略
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, List
from ...repositories.stock_query import StockQuery

class IndividualOversoldReboundStrategy:
    """个股超跌反弹策略类"""
    
    def __init__(self):
        """初始化策略"""
        self.stock_query = StockQuery()
        print("✅ 个股超跌反弹策略初始化成功")
    
    def calculate_kdj(self, data: pd.DataFrame, k_period: int = 9, d_period: int = 3, j_period: int = 3) -> pd.DataFrame:
        """
        计算KDJ指标
        
        Args:
            data: 包含最高价、最低价、收盘价的DataFrame
            k_period: K值计算周期
            d_period: D值计算周期
            j_period: J值计算周期
            
        Returns:
            DataFrame: 包含KDJ指标的DataFrame
        """
        if data is None or data.empty:
            return None
        
        # 确保有必要的价格列
        high_col = None
        low_col = None
        close_col = None
        
        for col in ['最高', '最高价', 'high', 'High']:
            if col in data.columns:
                high_col = col
                break
        
        for col in ['最低', '最低价', 'low', 'Low']:
            if col in data.columns:
                low_col = col
                break
        
        for col in ['收盘', '收盘价', 'close', 'Close']:
            if col in data.columns:
                close_col = col
                break
        
        if not all([high_col, low_col, close_col]):
            print("❌ 未找到必要的价格列")
            return None
        
        # 计算RSV（未成熟随机值）
        lowest_low = data[low_col].rolling(window=k_period).min()
        highest_high = data[high_col].rolling(window=k_period).max()
        
        rsv = np.where(highest_high != lowest_low, 
                      (data[close_col] - lowest_low) / (highest_high - lowest_low) * 100, 
                      50)
        
        # 计算K值
        k_value = pd.Series(rsv).ewm(alpha=1/d_period).mean()
        
        # 计算D值
        d_value = k_value.ewm(alpha=1/j_period).mean()
        
        # 计算J值
        j_value = 3 * k_value - 2 * d_value
        
        # 创建结果DataFrame
        result = data.copy()
        result['RSV'] = rsv
        result['K'] = k_value
        result['D'] = d_value
        result['J'] = j_value
        
        return result
    
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
        for col in ['收盘', '收盘价', 'close', 'Close']:
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
    
    def calculate_price_decline(self, data: pd.DataFrame, period: int = 20) -> pd.DataFrame:
        """
        计算价格跌幅
        
        Args:
            data: 包含收盘价的DataFrame
            period: 计算周期
            
        Returns:
            DataFrame: 包含价格跌幅的DataFrame
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
        
        # 计算不同周期的最高价
        high_5 = data[close_col].rolling(window=5).max()
        high_10 = data[close_col].rolling(window=10).max()
        high_20 = data[close_col].rolling(window=20).max()
        
        # 计算跌幅
        decline_5 = (high_5 - data[close_col]) / high_5 * 100
        decline_10 = (high_10 - data[close_col]) / high_10 * 100
        decline_20 = (high_20 - data[close_col]) / high_20 * 100
        
        # 创建结果DataFrame
        result = data.copy()
        result['High_5'] = high_5
        result['High_10'] = high_10
        result['High_20'] = high_20
        result['Decline_5'] = decline_5
        result['Decline_10'] = decline_10
        result['Decline_20'] = decline_20
        
        return result
    
    def generate_oversold_signals(self, data: pd.DataFrame, kdj_oversold: float = 20, 
                                 rsi_oversold: float = 30, decline_threshold: float = 15) -> pd.DataFrame:
        """
        生成超跌反弹交易信号
        
        Args:
            data: 包含技术指标的DataFrame
            kdj_oversold: KDJ超卖阈值
            rsi_oversold: RSI超卖阈值
            decline_threshold: 跌幅阈值
            
        Returns:
            DataFrame: 包含交易信号的DataFrame
        """
        if data is None or data.empty:
            return None
        
        # 检查必要的列
        required_cols = ['K', 'D', 'J', 'RSI', 'Decline_20']
        for col in required_cols:
            if col not in data.columns:
                print(f"❌ 缺少必要的列: {col}")
                return None
        
        result = data.copy()
        
        # 初始化信号列
        result['Signal'] = 0
        result['Signal_Type'] = 'HOLD'
        result['Oversold_Type'] = 'NONE'
        result['KDJ_Status'] = 'NORMAL'
        result['RSI_Status'] = 'NORMAL'
        result['Decline_Status'] = 'NORMAL'
        
        k_value = result['K']
        d_value = result['D']
        j_value = result['J']
        rsi_value = result['RSI']
        decline_20 = result['Decline_20']
        
        # 1. KDJ超卖判断
        kdj_oversold_condition = (k_value < kdj_oversold) & (d_value < kdj_oversold) & (j_value < kdj_oversold)
        
        # 2. RSI超卖判断
        rsi_oversold_condition = rsi_value < rsi_oversold
        
        # 3. 价格超跌判断
        price_oversold_condition = decline_20 > decline_threshold
        
        # 4. KDJ金叉（K线上穿D线）
        kdj_golden_cross = (k_value > d_value) & (k_value.shift(1) <= d_value.shift(1))
        
        # 5. RSI从超卖区域回升
        rsi_recovery = (rsi_value > rsi_oversold) & (rsi_value.shift(1) <= rsi_oversold)
        
        # 6. 强势超跌反弹：KDJ超卖 + RSI超卖 + 价格超跌
        strong_oversold_signal = kdj_oversold_condition & rsi_oversold_condition & price_oversold_condition
        
        # 7. KDJ金叉反弹：KDJ金叉 + RSI超卖
        kdj_rebound_signal = kdj_golden_cross & rsi_oversold_condition
        
        # 8. RSI反弹：RSI从超卖区域回升 + 价格超跌
        rsi_rebound_signal = rsi_recovery & price_oversold_condition
        
        # 9. 普通超跌：单一指标超卖
        normal_oversold_signal = (kdj_oversold_condition | rsi_oversold_condition) & price_oversold_condition
        
        # 设置信号
        result.loc[strong_oversold_signal, 'Signal'] = 2
        result.loc[strong_oversold_signal, 'Signal_Type'] = 'STRONG_BUY'
        result.loc[strong_oversold_signal, 'Oversold_Type'] = 'STRONG_OVERSOLD'
        result.loc[strong_oversold_signal, 'KDJ_Status'] = 'OVERSOLD'
        result.loc[strong_oversold_signal, 'RSI_Status'] = 'OVERSOLD'
        result.loc[strong_oversold_signal, 'Decline_Status'] = 'OVERSOLD'
        
        result.loc[kdj_rebound_signal & ~strong_oversold_signal, 'Signal'] = 2
        result.loc[kdj_rebound_signal & ~strong_oversold_signal, 'Signal_Type'] = 'STRONG_BUY'
        result.loc[kdj_rebound_signal & ~strong_oversold_signal, 'Oversold_Type'] = 'KDJ_REBOUND'
        result.loc[kdj_rebound_signal & ~strong_oversold_signal, 'KDJ_Status'] = 'GOLDEN_CROSS'
        result.loc[kdj_rebound_signal & ~strong_oversold_signal, 'RSI_Status'] = 'OVERSOLD'
        result.loc[kdj_rebound_signal & ~strong_oversold_signal, 'Decline_Status'] = 'NORMAL'
        
        result.loc[rsi_rebound_signal & ~strong_oversold_signal & ~kdj_rebound_signal, 'Signal'] = 1
        result.loc[rsi_rebound_signal & ~strong_oversold_signal & ~kdj_rebound_signal, 'Signal_Type'] = 'BUY'
        result.loc[rsi_rebound_signal & ~strong_oversold_signal & ~kdj_rebound_signal, 'Oversold_Type'] = 'RSI_REBOUND'
        result.loc[rsi_rebound_signal & ~strong_oversold_signal & ~kdj_rebound_signal, 'KDJ_Status'] = 'NORMAL'
        result.loc[rsi_rebound_signal & ~strong_oversold_signal & ~kdj_rebound_signal, 'RSI_Status'] = 'RECOVERY'
        result.loc[rsi_rebound_signal & ~strong_oversold_signal & ~kdj_rebound_signal, 'Decline_Status'] = 'OVERSOLD'
        
        result.loc[normal_oversold_signal & ~strong_oversold_signal & ~kdj_rebound_signal & ~rsi_rebound_signal, 'Signal'] = 1
        result.loc[normal_oversold_signal & ~strong_oversold_signal & ~kdj_rebound_signal & ~rsi_rebound_signal, 'Signal_Type'] = 'BUY'
        result.loc[normal_oversold_signal & ~strong_oversold_signal & ~kdj_rebound_signal & ~rsi_rebound_signal, 'Oversold_Type'] = 'NORMAL_OVERSOLD'
        result.loc[normal_oversold_signal & ~strong_oversold_signal & ~kdj_rebound_signal & ~rsi_rebound_signal, 'KDJ_Status'] = 'OVERSOLD'
        result.loc[normal_oversold_signal & ~strong_oversold_signal & ~kdj_rebound_signal & ~rsi_rebound_signal, 'RSI_Status'] = 'OVERSOLD'
        result.loc[normal_oversold_signal & ~strong_oversold_signal & ~kdj_rebound_signal & ~rsi_rebound_signal, 'Decline_Status'] = 'OVERSOLD'
        
        # 设置状态
        result.loc[kdj_oversold_condition, 'KDJ_Status'] = 'OVERSOLD'
        result.loc[rsi_oversold_condition, 'RSI_Status'] = 'OVERSOLD'
        result.loc[price_oversold_condition, 'Decline_Status'] = 'OVERSOLD'
        
        return result
    
    def analyze_stock_oversold(self, symbol: str, start_date: str = None, end_date: str = None) -> Optional[Dict[str, Any]]:
        """
        分析个股超跌反弹指标
        
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
            
            # 使用传入的数据进行分析
            return self.analyze_stock_oversold_with_data(hist_data, symbol)
            
        except Exception as e:
            print(f"❌ {symbol} 超跌反弹分析失败: {e}")
            return None
    
    def analyze_stock_oversold_with_data(self, hist_data: pd.DataFrame, symbol: str) -> Optional[Dict[str, Any]]:
        """
        使用传入的数据分析个股超跌反弹指标
        
        Args:
            hist_data: 历史数据DataFrame
            symbol: 股票代码
            
        Returns:
            Dict: 包含分析结果的字典
        """
        try:
            if hist_data is None or hist_data.empty:
                print(f"❌ {symbol} 的历史数据为空")
                return None
            
            # 计算KDJ指标
            kdj_data = self.calculate_kdj(hist_data)
            if kdj_data is None:
                return None
            
            # 计算RSI指标
            rsi_data = self.calculate_rsi(kdj_data)
            if rsi_data is None:
                return None
            
            # 计算价格跌幅
            decline_data = self.calculate_price_decline(rsi_data)
            if decline_data is None:
                return None
            
            # 生成交易信号
            signal_data = self.generate_oversold_signals(decline_data)
            if signal_data is None:
                return None
            
            # 分析结果
            latest_data = signal_data.iloc[-1]
            recent_signals = signal_data[signal_data['Signal'] != 0].tail(5)
            
            # 计算超跌强度
            oversold_strength = self._calculate_oversold_strength(signal_data)
            
            # 获取日期列名和收盘价列名
            date_col = None
            for col in ['日期', 'date', 'Date', '交易日期']:
                if col in signal_data.columns:
                    date_col = col
                    break
            
            close_col = None
            for col in ['收盘', '收盘价', 'close', 'Close']:
                if col in signal_data.columns:
                    close_col = col
                    break
            
            # 构建最近交易信号列表
            recent_signals_list = []
            if not recent_signals.empty and date_col and close_col:
                try:
                    recent_signals_list = recent_signals[[date_col, close_col, 'K', 'D', 'J', 'RSI', 'Decline_20', 'Signal', 'Signal_Type', 'Oversold_Type']].to_dict('records')
                except Exception as e:
                    print(f"⚠️ 构建最近交易信号列表失败: {e}")
                    recent_signals_list = []
            
            analysis_date = 'Unknown'
            if date_col:
                analysis_date = latest_data.get(date_col, 'Unknown')
            
            latest_close = 0
            if close_col:
                latest_close = latest_data.get(close_col, 0)
            
            analysis_result = {
                'symbol': symbol,
                'latest_close': latest_close,
                'latest_k': latest_data.get('K', 0),
                'latest_d': latest_data.get('D', 0),
                'latest_j': latest_data.get('J', 0),
                'latest_rsi': latest_data.get('RSI', 0),
                'latest_decline_20': latest_data.get('Decline_20', 0),
                'current_signal_type': latest_data.get('Signal_Type', 'HOLD'),
                'oversold_type': latest_data.get('Oversold_Type', 'NONE'),
                'kdj_status': latest_data.get('KDJ_Status', 'NORMAL'),
                'rsi_status': latest_data.get('RSI_Status', 'NORMAL'),
                'decline_status': latest_data.get('Decline_Status', 'NORMAL'),
                'oversold_strength': oversold_strength,
                'kdj_oversold': self._check_kdj_oversold(latest_data),
                'rsi_oversold': self._check_rsi_oversold(latest_data),
                'price_oversold': self._check_price_oversold(latest_data),
                'recent_signals': recent_signals_list,
                'data_points': len(signal_data),
                'analysis_date': analysis_date
            }
            
            return analysis_result
            
        except Exception as e:
            print(f"❌ {symbol} 超跌反弹分析失败: {e}")
            return None
    
    def _calculate_oversold_strength(self, data: pd.DataFrame) -> float:
        """
        计算超跌强度
        
        Args:
            data: 包含技术指标的DataFrame
            
        Returns:
            float: 超跌强度值（0-1之间）
        """
        if data is None or data.empty:
            return 0.0
        
        # 计算KDJ超卖程度
        kdj_oversold_ratio = (20 - data['K'].iloc[-1]) / 20 if data['K'].iloc[-1] < 20 else 0
        
        # 计算RSI超卖程度
        rsi_oversold_ratio = (30 - data['RSI'].iloc[-1]) / 30 if data['RSI'].iloc[-1] < 30 else 0
        
        # 计算价格超跌程度
        price_oversold_ratio = min(data['Decline_20'].iloc[-1] / 30, 1.0)  # 30%跌幅为满分
        
        # 综合超跌强度
        oversold_strength = (kdj_oversold_ratio + rsi_oversold_ratio + price_oversold_ratio) / 3
        
        return min(oversold_strength, 1.0)  # 限制在0-1之间
    
    def _check_kdj_oversold(self, data: pd.Series) -> bool:
        """
        检查KDJ超卖
        
        Args:
            data: 包含KDJ数据的Series
            
        Returns:
            bool: 是否为KDJ超卖
        """
        return data['K'] < 20 and data['D'] < 20 and data['J'] < 20
    
    def _check_rsi_oversold(self, data: pd.Series) -> bool:
        """
        检查RSI超卖
        
        Args:
            data: 包含RSI数据的Series
            
        Returns:
            bool: 是否为RSI超卖
        """
        return data['RSI'] < 30
    
    def _check_price_oversold(self, data: pd.Series) -> bool:
        """
        检查价格超跌
        
        Args:
            data: 包含价格数据的Series
            
        Returns:
            bool: 是否为价格超跌
        """
        return data['Decline_20'] > 15
    
    def get_oversold_recommendations(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """
        获取多个股票的超跌反弹推荐
        
        Args:
            symbols: 股票代码列表
            
        Returns:
            List[Dict]: 推荐结果列表
        """
        recommendations = []
        
        print(f"🔍 开始分析 {len(symbols)} 个股票的超跌反弹指标...")
        
        for symbol in symbols:
            analysis = self.analyze_stock_oversold(symbol)
            if analysis:
                recommendations.append(analysis)
        
        # 按超跌强度排序
        recommendations.sort(key=lambda x: x['oversold_strength'], reverse=True)
        
        print(f"✅ 超跌反弹分析完成，共分析 {len(recommendations)} 个股票")
        return recommendations
    
    def print_oversold_analysis(self, analysis_result: Dict[str, Any]):
        """
        打印超跌反弹分析结果
        
        Args:
            analysis_result: 分析结果字典
        """
        if not analysis_result:
            print("❌ 无分析结果可显示")
            return
        
        print(f"\n📊 {analysis_result['symbol']} 超跌反弹分析结果")
        print("=" * 60)
        print(f"分析日期: {analysis_result['analysis_date']}")
        print(f"数据点数: {analysis_result['data_points']}")
        print(f"当前收盘价: {analysis_result['latest_close']:.2f}")
        print(f"K值: {analysis_result['latest_k']:.2f}")
        print(f"D值: {analysis_result['latest_d']:.2f}")
        print(f"J值: {analysis_result['latest_j']:.2f}")
        print(f"RSI: {analysis_result['latest_rsi']:.2f}")
        print(f"20日跌幅: {analysis_result['latest_decline_20']:.2f}%")
        print(f"交易信号: {analysis_result['current_signal_type']}")
        print(f"超跌类型: {analysis_result['oversold_type']}")
        print(f"KDJ状态: {analysis_result['kdj_status']}")
        print(f"RSI状态: {analysis_result['rsi_status']}")
        print(f"跌幅状态: {analysis_result['decline_status']}")
        print(f"超跌强度: {analysis_result['oversold_strength']:.2f}")
        print(f"KDJ超卖: {'是' if analysis_result['kdj_oversold'] else '否'}")
        print(f"RSI超卖: {'是' if analysis_result['rsi_oversold'] else '否'}")
        print(f"价格超跌: {'是' if analysis_result['price_oversold'] else '否'}")
        
        if analysis_result['recent_signals']:
            print(f"\n📈 最近交易信号:")
            for signal in analysis_result['recent_signals']:
                print(f"  {signal['日期']}: {signal['Signal_Type']} (收盘价: {signal['收盘']:.2f}, 类型: {signal['Oversold_Type']})")
