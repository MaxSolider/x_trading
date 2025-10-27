"""
行业板块量价策略
基于成交量与价格关系的行业板块技术分析策略
适用于行业板块的量价关系分析和趋势判断
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.font_manager import FontProperties

from ...repositories.stock.stock_query import StockQuery
from ...repositories.stock.industry_info_query import IndustryInfoQuery
from ...repositories.stock.market_overview_query import MarketOverviewQuery


class VolumePriceStrategy:
    """行业板块量价策略类
    
    专门用于分析行业板块的量价关系，提供：
    - 量价协同指标分析
    - 量价相关性计算
    - 量价背离识别
    - 动态权重评估
    - 量价关系趋势图生成
    - 移动平均线分析
    
    适用于行业板块的技术分析和投资决策支持
    """
    
    def __init__(self):
        """初始化行业板块量价策略"""
        self.industry_query = IndustryInfoQuery()
        self.market_query = MarketOverviewQuery()
        print("✅ 行业板块量价策略初始化成功")
    
    def analyze_volume_price_relationship(self, symbol: str, start_date: str, end_date: str) -> Optional[Dict[str, Any]]:
        """
        分析行业板块的量价关系
        
        Args:
            symbol: 板块代码或股票代码
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            
        Returns:
            Dict[str, Any]: 量价分析结果
        """
        try:
            print(f"🔍 开始分析板块 {symbol} 的量价关系...")
            
            # 获取行业板块历史数据
            hist_data = self.industry_query.get_board_industry_hist(symbol, start_date, end_date)
            if hist_data is None or hist_data.empty:
                print(f"❌ 板块 {symbol} 历史数据获取失败")
                return None
            
            # 计算量价关系
            volume_price_result = self._calculate_volume_price_relationship(hist_data)
            
            # 生成交易信号
            signal_result = self._generate_volume_price_signal(volume_price_result)
            
            # 整合结果
            result = {
                'symbol': symbol,
                'analysis_date': end_date,
                'data_period': f"{start_date} - {end_date}",
                'volume_price_analysis': volume_price_result,
                'trading_signal': signal_result,
                'analysis_summary': self._generate_analysis_summary(volume_price_result, signal_result)
            }
            
            print(f"✅ {symbol} 量价关系分析完成")
            return result
            
        except Exception as e:
            print(f"❌ {symbol} 量价关系分析失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _calculate_volume_price_relationship(self, hist_data: pd.DataFrame) -> Dict[str, Any]:
        """
        计算量价关系指标
        
        Args:
            hist_data: 历史数据DataFrame
            
        Returns:
            Dict[str, Any]: 量价关系分析结果
        """
        try:
            # 检测日期列名（支持 'date', '日期'）
            date_col = None
            for col in ['日期', 'date', 'Date']:
                if col in hist_data.columns:
                    date_col = col
                    break
            
            if date_col is None:
                print("❌ 未找到日期列")
                return {}
            
            # 确保数据按日期排序
            hist_data = hist_data.sort_values(date_col).reset_index(drop=True)
            
            # 检测收盘价列名（支持 'close', '收盘', '收盘价'）
            close_col = None
            for col in ['收盘', '收盘价', 'close', 'Close']:
                if col in hist_data.columns:
                    close_col = col
                    break
            
            if close_col is None:
                print("❌ 未找到收盘价列")
                return {}
            
            # 检测成交量列名（支持 'volume', '成交量'）
            volume_col = None
            for col in ['成交量', 'volume', 'Volume']:
                if col in hist_data.columns:
                    volume_col = col
                    break
            
            if volume_col is None:
                print("❌ 未找到成交量列")
                return {}
            
            # 计算价格变化
            hist_data['价格变化'] = hist_data[close_col].pct_change()
            hist_data['价格变化_abs'] = hist_data['价格变化'].abs()
            
            # 计算成交量变化
            hist_data['成交量变化'] = hist_data[volume_col].pct_change()
            hist_data['成交量变化_abs'] = hist_data['成交量变化'].abs()
            
            # 计算移动平均线
            hist_data['MA5'] = hist_data[close_col].rolling(window=5).mean()
            hist_data['MA10'] = hist_data[close_col].rolling(window=10).mean()
            hist_data['MA20'] = hist_data[close_col].rolling(window=20).mean()
            
            hist_data['VOL_MA5'] = hist_data[volume_col].rolling(window=5).mean()
            hist_data['VOL_MA10'] = hist_data[volume_col].rolling(window=10).mean()
            hist_data['VOL_MA20'] = hist_data[volume_col].rolling(window=20).mean()
            
            # 计算量价关系分类
            hist_data['量价关系'] = self._classify_volume_price_relationship(hist_data, close_col, volume_col)
            
            # 获取最新数据
            latest_data = hist_data.iloc[-1]
            
            # 计算近期量价关系统计
            recent_data = hist_data.tail(10)  # 最近10个交易日
            relationship_counts = recent_data['量价关系'].value_counts()
            
            # 计算量价强度指标
            volume_price_strength = self._calculate_volume_price_strength(hist_data, close_col, volume_col)
            
            return {
                'latest_price': float(latest_data[close_col]),
                'latest_volume': int(latest_data[volume_col]),
                'price_change_pct': float(latest_data['价格变化']) * 100,
                'volume_change_pct': float(latest_data['成交量变化']) * 100,
                'latest_relationship': latest_data['量价关系'],
                'recent_relationships': relationship_counts.to_dict(),
                'volume_price_strength': volume_price_strength,
                'ma_trend': self._analyze_ma_trend(latest_data, close_col),
                'volume_trend': self._analyze_volume_trend(latest_data, volume_col),
                'data_points': len(hist_data)
            }
            
        except Exception as e:
            print(f"❌ 量价关系计算失败: {e}")
            return {}
    
    def _classify_volume_price_relationship(self, hist_data: pd.DataFrame, close_col: str = '收盘', volume_col: str = '成交量') -> pd.Series:
        """
        分类量价关系
        
        Args:
            hist_data: 历史数据DataFrame
            
        Returns:
            pd.Series: 量价关系分类结果
        """
        relationships = []
        
        for i in range(len(hist_data)):
            if i == 0:
                relationships.append('未知')
                continue
            
            price_change = hist_data.iloc[i]['价格变化']
            volume_change = hist_data.iloc[i]['成交量变化']
            
            # 判断价格变化方向
            if price_change > 0.01:  # 涨幅超过1%
                price_direction = '升'
            elif price_change < -0.01:  # 跌幅超过1%
                price_direction = '跌'
            else:
                price_direction = '平'
            
            # 判断成交量变化方向
            if volume_change > 0.1:  # 成交量增长超过10%
                volume_direction = '增'
            elif volume_change < -0.1:  # 成交量减少超过10%
                volume_direction = '减'
            else:
                volume_direction = '平'
            
            # 组合量价关系
            relationship = f"量{volume_direction}价{price_direction}"
            relationships.append(relationship)
        
        return pd.Series(relationships, index=hist_data.index)
    
    def _calculate_volume_price_strength(self, hist_data: pd.DataFrame, close_col: str = '收盘', volume_col: str = '成交量') -> Dict[str, float]:
        """
        计算量价强度指标 - 基于四个关键评分维度
        
        Args:
            hist_data: 历史数据DataFrame
            close_col: 收盘价列名
            volume_col: 成交量列名
            
        Returns:
            Dict[str, float]: 量价强度指标
        """
        try:
            # 1. 量价协同指标
            volume_price_synergy = self._calculate_volume_price_synergy(hist_data, close_col, volume_col)
            
            # 2. 量价相关性
            volume_price_correlation = self._calculate_volume_price_correlation(hist_data, close_col, volume_col)
            
            # 3. 量价背离
            volume_price_divergence = self._calculate_volume_price_divergence(hist_data, close_col, volume_col)
            
            # 4. 动态权重
            dynamic_weight = self._calculate_dynamic_weight(hist_data, close_col, volume_col)
            
            # 综合评分计算
            comprehensive_score = self._calculate_comprehensive_score(
                volume_price_synergy, volume_price_correlation, 
                volume_price_divergence, dynamic_weight
            )
            
            return {
                'volume_price_synergy': volume_price_synergy,
                'volume_price_correlation': volume_price_correlation,
                'volume_price_divergence': volume_price_divergence,
                'dynamic_weight': dynamic_weight,
                'comprehensive_score': comprehensive_score,
                'strength_level': self._get_strength_level(comprehensive_score)
            }
            
        except Exception as e:
            print(f"❌ 量价强度计算失败: {e}")
            return {}
    
    def _calculate_volume_price_synergy(self, hist_data: pd.DataFrame, close_col: str = '收盘', volume_col: str = '成交量', n: int = 5) -> float:
        """
        计算量价协同指标
        公式：VOL * CLOSE / REF(VOL, N) * REF(CLOSE, N)
        
        Args:
            hist_data: 历史数据DataFrame
            close_col: 收盘价列名
            volume_col: 成交量列名
            n: 参考天数，默认5天
            
        Returns:
            float: 量价协同指标值
        """
        try:
            if len(hist_data) < n + 1:
                return 0.0
            
            # 获取当前和N天前的数据
            current_vol = hist_data[volume_col].iloc[-1]
            current_close = hist_data[close_col].iloc[-1]
            ref_vol = hist_data[volume_col].iloc[-(n+1)]
            ref_close = hist_data[close_col].iloc[-(n+1)]
            
            # 计算量价协同指标
            synergy = (current_vol * current_close) / (ref_vol * ref_close)
            
            # 标准化处理，使其在合理范围内
            normalized_synergy = min(max(synergy, 0.1), 10.0)  # 限制在0.1-10之间
            
            return float(normalized_synergy)
            
        except Exception as e:
            print(f"❌ 量价协同计算失败: {e}")
            return 1.0
    
    def _calculate_volume_price_correlation(self, hist_data: pd.DataFrame, close_col: str = '收盘', volume_col: str = '成交量', window: int = 20) -> float:
        """
        计算量价相关系数
        计算过去一段时间内收盘价与成交量的相关系数
        
        Args:
            hist_data: 历史数据DataFrame
            close_col: 收盘价列名
            volume_col: 成交量列名
            window: 计算窗口，默认20天
            
        Returns:
            float: 量价相关系数 (-1到1之间)
        """
        try:
            if len(hist_data) < window:
                return 0.0
            
            # 计算价格和成交量的变化率
            price_changes = hist_data[close_col].pct_change().dropna()
            volume_changes = hist_data[volume_col].pct_change().dropna()
            
            # 取最近window天的数据
            recent_price_changes = price_changes.tail(window)
            recent_volume_changes = volume_changes.tail(window)
            
            # 计算相关系数
            correlation = recent_price_changes.corr(recent_volume_changes)
            
            # 处理NaN值
            if pd.isna(correlation):
                correlation = 0.0
            
            return float(correlation)
            
        except Exception as e:
            print(f"❌ 量价相关性计算失败: {e}")
            return 0.0
    
    def _calculate_volume_price_divergence(self, hist_data: pd.DataFrame, close_col: str = '收盘', volume_col: str = '成交量') -> float:
        """
        计算量价背离率
        公式：(价格变化率 - 成交量变化率) / 价格变化率
        
        Args:
            hist_data: 历史数据DataFrame
            close_col: 收盘价列名
            volume_col: 成交量列名
            
        Returns:
            float: 量价背离率
        """
        try:
            if len(hist_data) < 2:
                return 0.0
            
            # 计算最新一天的价格和成交量变化率
            latest_price_change = hist_data[close_col].pct_change().iloc[-1]
            latest_volume_change = hist_data[volume_col].pct_change().iloc[-1]
            
            # 避免除零错误
            if abs(latest_price_change) < 0.001:
                return 0.0
            
            # 计算背离率
            divergence_rate = (latest_price_change - latest_volume_change) / latest_price_change
            
            # 标准化处理
            normalized_divergence = min(max(divergence_rate, -5.0), 5.0)  # 限制在-5到5之间
            
            return float(normalized_divergence)
            
        except Exception as e:
            print(f"❌ 量价背离计算失败: {e}")
            return 0.0
    
    def _calculate_dynamic_weight(self, hist_data: pd.DataFrame, close_col: str = '收盘', volume_col: str = '成交量', window: int = 10) -> float:
        """
        计算动态权重
        公式：交易量 * 价格变动率 / 平均交易量
        
        Args:
            hist_data: 历史数据DataFrame
            close_col: 收盘价列名
            volume_col: 成交量列名
            window: 计算平均交易量的窗口，默认10天
            
        Returns:
            float: 动态权重值
        """
        try:
            if len(hist_data) < window:
                return 1.0
            
            # 获取最新数据
            latest_volume = hist_data[volume_col].iloc[-1]
            latest_price_change = abs(hist_data[close_col].pct_change().iloc[-1])
            
            # 计算平均交易量
            avg_volume = hist_data[volume_col].tail(window).mean()
            
            # 计算动态权重
            dynamic_weight = (latest_volume * latest_price_change) / avg_volume
            
            # 标准化处理
            normalized_weight = min(max(dynamic_weight, 0.1), 10.0)  # 限制在0.1-10之间
            
            return float(normalized_weight)
            
        except Exception as e:
            print(f"❌ 动态权重计算失败: {e}")
            return 1.0
    
    def _calculate_comprehensive_score(self, synergy: float, correlation: float, 
                                     divergence: float, weight: float) -> float:
        """
        计算综合评分
        
        Args:
            synergy: 量价协同指标
            correlation: 量价相关系数
            divergence: 量价背离率
            weight: 动态权重
            
        Returns:
            float: 综合评分 (0-100)
        """
        try:
            # 各维度权重分配
            synergy_weight = 0.3      # 量价协同权重30%
            correlation_weight = 0.25  # 量价相关性权重25%
            divergence_weight = 0.25   # 量价背离权重25%
            weight_factor = 0.2       # 动态权重因子20%
            
            # 量价协同评分 (0-100)
            synergy_score = min(max((synergy - 1.0) * 50 + 50, 0), 100)
            
            # 量价相关性评分 (0-100)
            correlation_score = min(max(correlation * 50 + 50, 0), 100)
            
            # 量价背离评分 (背离越小越好，0-100)
            divergence_score = min(max(100 - abs(divergence) * 20, 0), 100)
            
            # 动态权重评分 (权重越高越好，0-100)
            weight_score = min(max((weight - 1.0) * 20 + 50, 0), 100)
            
            # 综合评分计算
            comprehensive_score = (
                synergy_score * synergy_weight +
                correlation_score * correlation_weight +
                divergence_score * divergence_weight +
                weight_score * weight_factor
            )
            
            return float(comprehensive_score)
            
        except Exception as e:
            print(f"❌ 综合评分计算失败: {e}")
            return 50.0
    
    def _get_strength_level(self, score: float) -> str:
        """
        根据综合评分获取强度等级
        
        Args:
            score: 综合评分
            
        Returns:
            str: 强度等级
        """
        if score >= 80:
            return "极强"
        elif score >= 70:
            return "强"
        elif score >= 60:
            return "较强"
        elif score >= 50:
            return "中等"
        elif score >= 40:
            return "较弱"
        elif score >= 30:
            return "弱"
        else:
            return "极弱"
    
    def _analyze_ma_trend(self, latest_data: pd.Series, close_col: str = '收盘') -> Dict[str, Any]:
        """
        分析移动平均线趋势
        
        Args:
            latest_data: 最新数据
            close_col: 收盘价列名
            
        Returns:
            Dict[str, Any]: MA趋势分析结果
        """
        try:
            ma5 = latest_data['MA5']
            ma10 = latest_data['MA10']
            ma20 = latest_data['MA20']
            current_price = latest_data[close_col]
            
            # 判断趋势方向
            if ma5 > ma10 > ma20:
                trend_direction = '上升'
                trend_strength = '强'
            elif ma5 > ma10 and ma10 > ma20:
                trend_direction = '上升'
                trend_strength = '中'
            elif ma5 < ma10 < ma20:
                trend_direction = '下降'
                trend_strength = '强'
            elif ma5 < ma10 and ma10 < ma20:
                trend_direction = '下降'
                trend_strength = '中'
            else:
                trend_direction = '震荡'
                trend_strength = '弱'
            
            # 判断价格与MA关系
            if current_price > ma5 > ma10 > ma20:
                price_position = '强势'
            elif current_price > ma20:
                price_position = '中性'
            else:
                price_position = '弱势'
            
            return {
                'trend_direction': trend_direction,
                'trend_strength': trend_strength,
                'price_position': price_position,
                'ma5': float(ma5),
                'ma10': float(ma10),
                'ma20': float(ma20)
            }
            
        except Exception as e:
            print(f"❌ MA趋势分析失败: {e}")
            return {}
    
    def _analyze_volume_trend(self, latest_data: pd.Series, volume_col: str = '成交量') -> Dict[str, Any]:
        """
        分析成交量趋势
        
        Args:
            latest_data: 最新数据
            volume_col: 成交量列名
            
        Returns:
            Dict[str, Any]: 成交量趋势分析结果
        """
        try:
            vol_ma5 = latest_data['VOL_MA5']
            vol_ma10 = latest_data['VOL_MA10']
            vol_ma20 = latest_data['VOL_MA20']
            current_volume = latest_data[volume_col]
            
            # 判断成交量趋势
            if vol_ma5 > vol_ma10 > vol_ma20:
                volume_trend = '放大'
                trend_strength = '强'
            elif vol_ma5 > vol_ma10 and vol_ma10 > vol_ma20:
                volume_trend = '放大'
                trend_strength = '中'
            elif vol_ma5 < vol_ma10 < vol_ma20:
                volume_trend = '萎缩'
                trend_strength = '强'
            elif vol_ma5 < vol_ma10 and vol_ma10 < vol_ma20:
                volume_trend = '萎缩'
                trend_strength = '中'
            else:
                volume_trend = '平稳'
                trend_strength = '弱'
            
            # 判断当前成交量水平
            if current_volume > vol_ma20 * 1.5:
                volume_level = '放量'
            elif current_volume < vol_ma20 * 0.5:
                volume_level = '缩量'
            else:
                volume_level = '正常'
            
            return {
                'volume_trend': volume_trend,
                'trend_strength': trend_strength,
                'volume_level': volume_level,
                'vol_ma5': float(vol_ma5),
                'vol_ma10': float(vol_ma10),
                'vol_ma20': float(vol_ma20)
            }
            
        except Exception as e:
            print(f"❌ 成交量趋势分析失败: {e}")
            return {}
    
    def _generate_volume_price_signal(self, volume_price_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成量价交易信号
        
        Args:
            volume_price_analysis: 量价分析结果
            
        Returns:
            Dict[str, Any]: 交易信号结果
        """
        try:
            latest_relationship = volume_price_analysis.get('latest_relationship', '未知')
            price_change_pct = volume_price_analysis.get('price_change_pct', 0)
            volume_change_pct = volume_price_analysis.get('volume_change_pct', 0)
            ma_trend = volume_price_analysis.get('ma_trend', {})
            volume_trend = volume_price_analysis.get('volume_trend', {})
            volume_price_strength = volume_price_analysis.get('volume_price_strength', {})
            
            # 根据量价关系生成信号
            signal_info = self._get_volume_price_signal_info(latest_relationship)
            
            # 计算信号强度
            signal_strength = self._calculate_signal_strength(
                latest_relationship, price_change_pct, volume_change_pct, ma_trend, volume_trend, volume_price_strength
            )
            
            # 生成操作建议
            operation_advice = self._generate_operation_advice(
                latest_relationship, signal_strength, ma_trend, volume_trend
            )
            
            return {
                'signal_type': signal_info['signal_type'],
                'market_signal': signal_info['market_signal'],
                'operation_thought': signal_info['operation_thought'],
                'signal_strength': signal_strength,
                'operation_advice': operation_advice,
                'risk_level': signal_info['risk_level'],
                'confidence': signal_info['confidence']
            }
            
        except Exception as e:
            print(f"❌ 交易信号生成失败: {e}")
            return {}
    
    def _get_volume_price_signal_info(self, relationship: str) -> Dict[str, Any]:
        """
        获取量价关系对应的信号信息
        
        Args:
            relationship: 量价关系
            
        Returns:
            Dict[str, Any]: 信号信息
        """
        signal_mapping = {
            '量增价升': {
                'signal_type': 'BUY',
                'market_signal': '资金积极入场，趋势健康，行情有望延续',
                'operation_thought': '积极买入或持股待涨',
                'risk_level': '低',
                'confidence': '高'
            },
            '量增价平': {
                'signal_type': 'NEUTRAL',
                'market_signal': '趋势可能转换。低位：资金吸筹；高位：主力派发',
                'operation_thought': '低位关注，高位警惕',
                'risk_level': '中',
                'confidence': '中'
            },
            '量平价升': {
                'signal_type': 'HOLD',
                'market_signal': '趋势可能延续，但也可能接近尾声',
                'operation_thought': '可继续持有，但需保持警惕',
                'risk_level': '中',
                'confidence': '中'
            },
            '量减价升': {
                'signal_type': 'CAUTION',
                'market_signal': '量价背离，上涨乏力，可能回调',
                'operation_thought': '考虑减仓，谨慎追高',
                'risk_level': '高',
                'confidence': '高'
            },
            '量减价跌': {
                'signal_type': 'SELL',
                'market_signal': '阴跌，卖压逐步释放，但底部未明',
                'operation_thought': '卖出信号，保持观望',
                'risk_level': '高',
                'confidence': '高'
            },
            '量增价跌': {
                'signal_type': 'PANIC',
                'market_signal': '恐慌性抛盘，可能最后一跌或下跌初期',
                'operation_thought': '低位关注，高位果断清仓',
                'risk_level': '极高',
                'confidence': '高'
            }
        }
        
        return signal_mapping.get(relationship, {
            'signal_type': 'UNKNOWN',
            'market_signal': '量价关系不明确，需要进一步观察',
            'operation_thought': '保持观望，等待明确信号',
            'risk_level': '未知',
            'confidence': '低'
        })
    
    def _calculate_signal_strength(self, relationship: str, price_change_pct: float, 
                                 volume_change_pct: float, ma_trend: Dict[str, Any], 
                                 volume_trend: Dict[str, Any], volume_price_strength: Dict[str, Any]) -> float:
        """
        计算信号强度 - 基于新的量价评分维度
        
        Args:
            relationship: 量价关系
            price_change_pct: 价格变化百分比
            volume_change_pct: 成交量变化百分比
            ma_trend: MA趋势分析
            volume_trend: 成交量趋势分析
            volume_price_strength: 量价强度指标
            
        Returns:
            float: 信号强度 (0-100)
        """
        try:
            # 获取综合评分作为基础强度
            base_strength = volume_price_strength.get('comprehensive_score', 50)
            
            # 根据量价关系调整强度
            relationship_adjustment = {
                '量增价升': 15,      # 最佳量价关系
                '量增价平': 5,       # 中性偏多
                '量平价升': 0,       # 中性
                '量减价升': -10,     # 背离信号
                '量减价跌': -15,     # 弱势信号
                '量增价跌': -20      # 恐慌信号
            }
            
            relationship_factor = relationship_adjustment.get(relationship, 0)
            
            # 根据价格变化幅度调整
            price_factor = min(abs(price_change_pct) * 1.5, 8)
            if price_change_pct < 0:
                price_factor = -price_factor
            
            # 根据成交量变化幅度调整
            volume_factor = min(abs(volume_change_pct) * 0.3, 5)
            if volume_change_pct < 0:
                volume_factor = -volume_factor
            
            # 根据MA趋势调整
            ma_factor = 0
            if ma_trend.get('trend_direction') == '上升':
                ma_factor = 3
            elif ma_trend.get('trend_direction') == '下降':
                ma_factor = -3
            
            # 根据成交量趋势调整
            volume_trend_factor = 0
            if volume_trend.get('volume_trend') == '放大':
                volume_trend_factor = 2
            elif volume_trend.get('volume_trend') == '萎缩':
                volume_trend_factor = -2
            
            # 计算最终强度
            final_strength = base_strength + relationship_factor + price_factor + volume_factor + ma_factor + volume_trend_factor
            
            # 限制在0-100范围内
            return max(0, min(100, final_strength))
            
        except Exception as e:
            print(f"❌ 信号强度计算失败: {e}")
            return 50
    
    def _generate_operation_advice(self, relationship: str, signal_strength: float, 
                                 ma_trend: Dict[str, Any], volume_trend: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成操作建议
        
        Args:
            relationship: 量价关系
            signal_strength: 信号强度
            ma_trend: MA趋势分析
            volume_trend: 成交量趋势分析
            
        Returns:
            Dict[str, Any]: 操作建议
        """
        try:
            advice = {
                'primary_action': '',
                'secondary_action': '',
                'risk_management': '',
                'timing_suggestion': '',
                'position_suggestion': ''
            }
            
            # 根据量价关系生成主要操作建议
            if relationship == '量增价升':
                advice['primary_action'] = '积极买入'
                advice['secondary_action'] = '持股待涨'
                advice['risk_management'] = '设置止损位'
                advice['timing_suggestion'] = '逢低买入'
                advice['position_suggestion'] = '可适当加仓'
            elif relationship == '量增价平':
                advice['primary_action'] = '谨慎观察'
                advice['secondary_action'] = '等待明确信号'
                advice['risk_management'] = '控制仓位'
                advice['timing_suggestion'] = '等待突破'
                advice['position_suggestion'] = '保持现有仓位'
            elif relationship == '量平价升':
                advice['primary_action'] = '继续持有'
                advice['secondary_action'] = '保持警惕'
                advice['risk_management'] = '准备减仓'
                advice['timing_suggestion'] = '关注量能变化'
                advice['position_suggestion'] = '维持仓位'
            elif relationship == '量减价升':
                advice['primary_action'] = '考虑减仓'
                advice['secondary_action'] = '谨慎追高'
                advice['risk_management'] = '及时止损'
                advice['timing_suggestion'] = '逢高减仓'
                advice['position_suggestion'] = '降低仓位'
            elif relationship == '量减价跌':
                advice['primary_action'] = '卖出观望'
                advice['secondary_action'] = '等待底部'
                advice['risk_management'] = '严格止损'
                advice['timing_suggestion'] = '及时离场'
                advice['position_suggestion'] = '空仓观望'
            elif relationship == '量增价跌':
                advice['primary_action'] = '果断清仓'
                advice['secondary_action'] = '低位关注'
                advice['risk_management'] = '避免抄底'
                advice['timing_suggestion'] = '立即离场'
                advice['position_suggestion'] = '空仓等待'
            else:
                advice['primary_action'] = '保持观望'
                advice['secondary_action'] = '等待信号'
                advice['risk_management'] = '控制风险'
                advice['timing_suggestion'] = '耐心等待'
                advice['position_suggestion'] = '维持现状'
            
            # 根据信号强度调整建议
            if signal_strength > 70:
                advice['confidence'] = '高'
            elif signal_strength > 40:
                advice['confidence'] = '中'
            else:
                advice['confidence'] = '低'
            
            return advice
            
        except Exception as e:
            print(f"❌ 操作建议生成失败: {e}")
            return {}
    
    def _generate_analysis_summary(self, volume_price_analysis: Dict[str, Any], 
                                 trading_signal: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成分析摘要
        
        Args:
            volume_price_analysis: 量价分析结果
            trading_signal: 交易信号结果
            
        Returns:
            Dict[str, Any]: 分析摘要
        """
        try:
            latest_relationship = volume_price_analysis.get('latest_relationship', '未知')
            signal_type = trading_signal.get('signal_type', 'UNKNOWN')
            signal_strength = trading_signal.get('signal_strength', 50)
            volume_price_strength = volume_price_analysis.get('volume_price_strength', {})
            
            # 获取量价评分维度信息
            synergy = volume_price_strength.get('volume_price_synergy', 1.0)
            correlation = volume_price_strength.get('volume_price_correlation', 0.0)
            divergence = volume_price_strength.get('volume_price_divergence', 0.0)
            dynamic_weight = volume_price_strength.get('dynamic_weight', 1.0)
            comprehensive_score = volume_price_strength.get('comprehensive_score', 50)
            strength_level = volume_price_strength.get('strength_level', '中等')
            
            # 生成摘要文本
            summary_text = f"当前量价关系为{latest_relationship}，"
            summary_text += f"信号类型为{signal_type}，"
            summary_text += f"综合评分为{comprehensive_score:.1f}（{strength_level}），"
            summary_text += f"信号强度为{signal_strength:.1f}。"
            summary_text += trading_signal.get('market_signal', '')
            
            return {
                'summary_text': summary_text,
                'key_points': [
                    f"量价关系: {latest_relationship}",
                    f"信号类型: {signal_type}",
                    f"综合评分: {comprehensive_score:.1f} ({strength_level})",
                    f"信号强度: {signal_strength:.1f}",
                    f"操作思路: {trading_signal.get('operation_thought', '')}"
                ],
                'volume_price_metrics': {
                    '量价协同': f"{synergy:.3f}",
                    '量价相关性': f"{correlation:.3f}",
                    '量价背离率': f"{divergence:.3f}",
                    '动态权重': f"{dynamic_weight:.3f}",
                    '综合评分': f"{comprehensive_score:.1f}",
                    '强度等级': strength_level
                },
                'risk_assessment': trading_signal.get('risk_level', '未知'),
                'confidence_level': trading_signal.get('confidence', '低')
            }
            
        except Exception as e:
            print(f"❌ 分析摘要生成失败: {e}")
            return {}
    
    def batch_analyze_stocks(self, symbols: List[str], start_date: str, end_date: str) -> Dict[str, Any]:
        """
        批量分析多个行业板块的量价关系
        
        Args:
            symbols: 板块代码或股票代码列表
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            Dict[str, Any]: 批量分析结果
        """
        try:
            print(f"🔍 开始批量分析 {len(symbols)} 个行业板块的量价关系...")
            
            results = {}
            signal_summary = {
                'BUY': [],
                'HOLD': [],
                'CAUTION': [],
                'SELL': [],
                'PANIC': [],
                'NEUTRAL': [],
                'UNKNOWN': []
            }
            
            for i, symbol in enumerate(symbols, 1):
                print(f"📊 正在分析股票 {i}/{len(symbols)}: {symbol}")
                
                result = self.analyze_volume_price_relationship(symbol, start_date, end_date)
                if result:
                    results[symbol] = result
                    
                    # 统计信号类型
                    signal_type = result.get('trading_signal', {}).get('signal_type', 'UNKNOWN')
                    signal_summary[signal_type].append(symbol)
            
            # 生成批量分析摘要
            batch_summary = {
                'total_analyzed': len(results),
                'total_requested': len(symbols),
                'success_rate': len(results) / len(symbols) * 100,
                'signal_summary': signal_summary,
                'analysis_date': end_date,
                'data_period': f"{start_date} - {end_date}"
            }
            
            print(f"✅ 批量分析完成，成功分析 {len(results)}/{len(symbols)} 只股票")
            
            return {
                'batch_summary': batch_summary,
                'individual_results': results
            }
            
        except Exception as e:
            print(f"❌ 批量分析失败: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def generate_volume_price_trend_chart(self, symbol: str, start_date: str, end_date: str, 
                                        output_dir: str = "reports/images/volume_price") -> Optional[str]:
        """
        生成行业板块近期量价关系趋势图
        
        Args:
            symbol: 板块代码或股票代码
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            output_dir: 输出目录
            
        Returns:
            Optional[str]: 生成的图表文件路径
        """
        try:
            print(f"📊 开始生成板块 {symbol} 的量价关系趋势图...")
            
            # 获取行业板块历史数据
            hist_data = self.industry_query.get_board_industry_hist(symbol, start_date, end_date)
            if hist_data is None or hist_data.empty:
                print(f"❌ 板块 {symbol} 历史数据获取失败")
                return None
            
            # 检测日期列名并排序
            date_col = None
            for col in ['日期', 'date', 'Date']:
                if col in hist_data.columns:
                    date_col = col
                    break
            
            if date_col:
                hist_data = hist_data.sort_values(date_col).reset_index(drop=True)
            else:
                hist_data = hist_data.reset_index(drop=True)
            
            # 创建输出目录
            os.makedirs(output_dir, exist_ok=True)
            
            # 生成图表
            chart_path = self._create_volume_price_chart(hist_data, symbol, end_date, output_dir)
            
            if chart_path:
                print(f"✅ {symbol} 量价关系趋势图已生成: {chart_path}")
                return chart_path
            else:
                print(f"❌ {symbol} 量价关系趋势图生成失败")
                return None
                
        except Exception as e:
            print(f"❌ 生成 {symbol} 量价关系趋势图失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _create_volume_price_chart(self, hist_data: pd.DataFrame, symbol: str, 
                                 end_date: str, output_dir: str) -> Optional[str]:
        """
        创建量价关系趋势图
        
        Args:
            hist_data: 历史数据DataFrame
            symbol: 股票代码
            end_date: 结束日期
            output_dir: 输出目录
            
        Returns:
            Optional[str]: 图表文件路径
        """
        try:
            # 设置中文字体
            plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans', 'Arial']
            plt.rcParams['axes.unicode_minus'] = False
            
            # 创建双子图
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12), height_ratios=[2, 1])
            
            # 检测日期列名（支持 'date', '日期'）
            date_col = None
            for col in ['日期', 'date', 'Date']:
                if col in hist_data.columns:
                    date_col = col
                    break
            
            # 检测收盘价列名
            close_col = None
            for col in ['收盘', '收盘价', 'close', 'Close']:
                if col in hist_data.columns:
                    close_col = col
                    break
            
            # 检测成交量列名
            volume_col = None
            for col in ['成交量', 'volume', 'Volume']:
                if col in hist_data.columns:
                    volume_col = col
                    break
            
            if date_col is None or close_col is None or volume_col is None:
                print(f"❌ 板块 {symbol} 图表数据列名不完整")
                return None
            
            # 获取原始数据
            dates = pd.to_datetime(hist_data[date_col])
            prices = hist_data[close_col]
            volumes = hist_data[volume_col]
            
            # 计算原始数据的移动平均线
            ma_periods = [5, 10, 20]  # 移动平均线周期
            price_mas = self._calculate_raw_moving_averages(prices, ma_periods)
            volume_mas = self._calculate_raw_moving_averages(volumes, ma_periods)
            
            # === 上图：价格趋势 ===
            ax1.plot(dates, prices, label='收盘价', linewidth=2, color='#1f77b4', alpha=0.8)
            
            # 绘制价格移动平均线
            ma_colors = ['#2ca02c', '#d62728', '#9467bd']  # 绿色、红色、紫色
            for i, period in enumerate(ma_periods):
                if period in price_mas:
                    ax1.plot(dates, price_mas[period], 
                           label=f'MA{period}', linewidth=1.5, 
                           color=ma_colors[i], alpha=0.7, linestyle='--')
            
            ax1.set_title(f'{symbol} 量价关系趋势图 - {end_date}', fontsize=16, fontweight='bold', pad=20)
            ax1.set_ylabel('价格', fontsize=12)
            ax1.legend(loc='upper left', fontsize=10)
            ax1.grid(True, alpha=0.3, linestyle='--')
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            ax1.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates)//10)))
            plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
            
            # === 下图：成交量趋势 ===
            ax2.bar(dates, volumes, label='成交量', color='#ff7f0e', alpha=0.6, width=0.8)
            
            # 绘制成交量移动平均线
            for i, period in enumerate(ma_periods):
                if period in volume_mas:
                    ax2.plot(dates, volume_mas[period], 
                           label=f'VOL MA{period}', linewidth=1.5, 
                           color=ma_colors[i], alpha=0.8, linestyle='--')
            
            ax2.set_xlabel('日期', fontsize=12)
            ax2.set_ylabel('成交量', fontsize=12)
            ax2.legend(loc='upper left', fontsize=10)
            ax2.grid(True, alpha=0.3, linestyle='--')
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            ax2.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates)//10)))
            plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
            
            # 添加量价关系标注
            self._add_relationship_annotations_for_raw_data(ax1, dates, prices, volumes)
            
            # 调整布局
            plt.tight_layout()
            
            # 生成文件路径
            filename = f"{symbol}_量价关系趋势图_{end_date}.png"
            chart_path = os.path.join(output_dir, filename)
            
            # 保存图表
            plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            return chart_path
            
        except Exception as e:
            print(f"❌ 创建量价关系趋势图失败: {e}")
            return None
    
    def _normalize_data(self, data: pd.Series) -> pd.Series:
        """
        对数据进行归一化处理
        公式：(当前值-区间最小值)/(区间最大值-区间最小值)
        
        Args:
            data: 待归一化的数据
            
        Returns:
            pd.Series: 归一化后的数据
        """
        try:
            min_val = data.min()
            max_val = data.max()
            
            # 避免除零错误
            if max_val == min_val:
                return pd.Series([0.5] * len(data), index=data.index)
            
            # 归一化处理
            normalized = (data - min_val) / (max_val - min_val)
            
            return normalized
            
        except Exception as e:
            print(f"❌ 数据归一化失败: {e}")
            return pd.Series([0.5] * len(data), index=data.index)
    
    def _add_volume_price_relationship_fill(self, ax, dates, normalized_prices, normalized_volumes):
        """
        添加量价关系填充区域
        
        Args:
            ax: matplotlib轴对象
            dates: 日期数据
            normalized_prices: 归一化价格
            normalized_volumes: 归一化成交量
        """
        try:
            # 计算量价关系
            price_volume_diff = normalized_prices - normalized_volumes
            
            # 量增价升区域（绿色）
            positive_mask = (normalized_volumes > normalized_prices) & (normalized_prices > 0.5)
            if positive_mask.any():
                ax.fill_between(dates, normalized_prices, normalized_volumes, 
                              where=positive_mask, alpha=0.3, color='green', 
                              label='量增价升区域')
            
            # 量减价跌区域（红色）
            negative_mask = (normalized_volumes < normalized_prices) & (normalized_prices < 0.5)
            if negative_mask.any():
                ax.fill_between(dates, normalized_prices, normalized_volumes, 
                              where=negative_mask, alpha=0.3, color='red', 
                              label='量减价跌区域')
            
            # 量价背离区域（黄色）
            divergence_mask = abs(price_volume_diff) > 0.3
            if divergence_mask.any():
                ax.fill_between(dates, normalized_prices, normalized_volumes, 
                              where=divergence_mask, alpha=0.2, color='yellow', 
                              label='量价背离区域')
            
        except Exception as e:
            print(f"❌ 添加量价关系填充区域失败: {e}")
    
    def _add_relationship_annotations(self, ax, dates, normalized_prices, normalized_volumes):
        """
        添加量价关系标注
        
        Args:
            ax: matplotlib轴对象
            dates: 日期数据
            normalized_prices: 归一化价格
            normalized_volumes: 归一化成交量
        """
        try:
            # 获取最新数据点
            latest_date = dates.iloc[-1]
            latest_price = normalized_prices.iloc[-1]
            latest_volume = normalized_volumes.iloc[-1]
            
            # 添加最新数据点标注
            ax.annotate(f'最新价格: {latest_price:.3f}', 
                       xy=(latest_date, latest_price), 
                       xytext=(10, 10), textcoords='offset points',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='blue', alpha=0.7),
                       fontsize=9, color='white')
            
            ax.annotate(f'最新成交量: {latest_volume:.3f}', 
                       xy=(latest_date, latest_volume), 
                       xytext=(10, -20), textcoords='offset points',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='orange', alpha=0.7),
                       fontsize=9, color='white')
            
            # 添加量价关系说明
            price_volume_diff = latest_price - latest_volume
            
            if price_volume_diff > 0.1:
                relationship_text = "量减价升"
                color = 'red'
            elif price_volume_diff < -0.1:
                relationship_text = "量增价跌"
                color = 'red'
            elif abs(price_volume_diff) <= 0.1:
                if latest_price > 0.5 and latest_volume > 0.5:
                    relationship_text = "量增价升"
                    color = 'green'
                elif latest_price < 0.5 and latest_volume < 0.5:
                    relationship_text = "量减价跌"
                    color = 'red'
                else:
                    relationship_text = "量价平衡"
                    color = 'blue'
            else:
                relationship_text = "量价背离"
                color = 'yellow'
            
            # 添加关系标注（居中显示）
            ax.text(0.50, 0.98, f'当前关系: {relationship_text}', 
                   transform=ax.transAxes, fontsize=12, fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.5', facecolor=color, alpha=0.8),
                   color='white', verticalalignment='top', 
                   horizontalalignment='center')
            
        except Exception as e:
            print(f"❌ 添加量价关系标注失败: {e}")
    
    def batch_generate_volume_price_charts(self, symbols: List[str], start_date: str, end_date: str,
                                          output_dir: str = "reports/images/volume_price") -> Dict[str, Any]:
        """
        批量生成行业板块量价关系趋势图
        
        Args:
            symbols: 板块代码或股票代码列表
            start_date: 开始日期
            end_date: 结束日期
            output_dir: 输出目录
            
        Returns:
            Dict[str, Any]: 批量生成结果
        """
        try:
            print(f"📊 开始批量生成 {len(symbols)} 个行业板块的量价关系趋势图...")
            
            results = {}
            success_count = 0
            
            for i, symbol in enumerate(symbols, 1):
                print(f"📈 正在生成图表 {i}/{len(symbols)}: {symbol}")
                
                chart_path = self.generate_volume_price_trend_chart(symbol, start_date, end_date, output_dir)
                
                if chart_path:
                    results[symbol] = {
                        'status': 'success',
                        'chart_path': chart_path,
                        'symbol': symbol
                    }
                    success_count += 1
                else:
                    results[symbol] = {
                        'status': 'failed',
                        'symbol': symbol,
                        'error': '图表生成失败'
                    }
            
            # 生成批量结果摘要
            batch_summary = {
                'total_requested': len(symbols),
                'total_success': success_count,
                'success_rate': success_count / len(symbols) * 100,
                'output_directory': output_dir,
                'generation_date': end_date
            }
            
            print(f"✅ 批量生成完成，成功生成 {success_count}/{len(symbols)} 个图表")
            
            return {
                'batch_summary': batch_summary,
                'individual_results': results
            }
            
        except Exception as e:
            print(f"❌ 批量生成量价关系趋势图失败: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def _calculate_normalized_moving_averages(self, normalized_data: pd.Series, periods: List[int]) -> Dict[int, pd.Series]:
        """
        计算归一化数据的移动平均线
        
        Args:
            normalized_data: 归一化后的数据
            periods: 移动平均线周期列表
            
        Returns:
            Dict[int, pd.Series]: 各周期的移动平均线数据
        """
        try:
            ma_results = {}
            
            for period in periods:
                if len(normalized_data) >= period:
                    # 计算移动平均线
                    ma_values = normalized_data.rolling(window=period).mean()
                    
                    # 保持与原始数据相同的索引和长度
                    # 前period-1个值为NaN，我们用前向填充或线性插值处理
                    ma_filled = ma_values.bfill().ffill()
                    
                    # 如果仍有NaN值，用0.5填充（归一化数据的中间值）
                    ma_filled = ma_filled.fillna(0.5)
                    
                    ma_results[period] = ma_filled
                else:
                    print(f"⚠️ 数据长度({len(normalized_data)})不足以计算MA{period}")
            
            return ma_results
            
        except Exception as e:
            print(f"❌ 计算归一化移动平均线失败: {e}")
            return {}
    
    def _calculate_raw_moving_averages(self, raw_data: pd.Series, periods: List[int]) -> Dict[int, pd.Series]:
        """
        计算原始数据的移动平均线
        
        Args:
            raw_data: 原始数据
            periods: 移动平均线周期列表
            
        Returns:
            Dict[int, pd.Series]: 各周期的移动平均线数据
        """
        try:
            ma_results = {}
            
            for period in periods:
                if len(raw_data) >= period:
                    # 计算移动平均线
                    ma_values = raw_data.rolling(window=period).mean()
                    ma_results[period] = ma_values
                else:
                    print(f"⚠️ 数据长度({len(raw_data)})不足以计算MA{period}")
            
            return ma_results
            
        except Exception as e:
            print(f"❌ 计算原始移动平均线失败: {e}")
            return {}
    
    def _add_relationship_annotations_for_raw_data(self, ax, dates, prices, volumes):
        """
        为原始数据添加量价关系标注
        
        Args:
            ax: matplotlib轴对象
            dates: 日期数据
            prices: 价格数据
            volumes: 成交量数据
        """
        try:
            # 获取最新数据点
            latest_date = dates.iloc[-1]
            latest_price = prices.iloc[-1]
            latest_volume = volumes.iloc[-1]
            
            # 计算价格变化率和成交量变化率
            if len(prices) > 1:
                price_change = (prices.iloc[-1] - prices.iloc[-2]) / prices.iloc[-2]
                volume_change = (volumes.iloc[-1] - volumes.iloc[-2]) / volumes.iloc[-2]
                
                # 判断量价关系
                if price_change > 0.01 and volume_change > 0.1:
                    relationship_text = "量增价升"
                    color = 'green'
                elif price_change < -0.01 and volume_change < -0.1:
                    relationship_text = "量减价跌"
                    color = 'red'
                elif price_change > 0.01 and volume_change < -0.1:
                    relationship_text = "量减价升"
                    color = 'orange'
                elif price_change < -0.01 and volume_change > 0.1:
                    relationship_text = "量增价跌"
                    color = 'red'
                else:
                    relationship_text = "量价平衡"
                    color = 'blue'
            else:
                relationship_text = "数据不足"
                color = 'gray'
            
            # 添加关系标注（居中显示）
            ax.text(0.50, 0.98, f'当前关系: {relationship_text}', 
                   transform=ax.transAxes, fontsize=12, fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.5', facecolor=color, alpha=0.8),
                   color='white', verticalalignment='top', 
                   horizontalalignment='center')
            
        except Exception as e:
            print(f"❌ 添加原始数据关系标注失败: {e}")
