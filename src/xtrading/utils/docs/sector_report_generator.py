"""
行业板块报告生成器
负责生成单个行业板块的策略回测报告
整合了分析结论生成、异动检测、数据分析和Markdown报告生成功能
"""

import os
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime
from ...static import ReportDirectoryConfig


class SectorReportGenerator:
    """行业板块报告生成器 - 整合单个行业板块报告生成的所有功能"""
    
    def __init__(self):
        """初始化行业板块报告生成器"""
        pass
    
    def generate_sector_report(self, 
                             results: List[Dict[str, Any]], 
                             reports_dir: str,
                             category: str,
                             industry_name: str,
                             timestamp: str,
                             comprehensive_data: List[Dict[str, Any]],
                             daily_data: List[Dict[str, Any]],
                             cumulative_data: List[Dict[str, Any]],
                             daily_summary_data: List[Dict[str, Any]],
                             cumulative_summary_data: List[Dict[str, Any]],
                             analysis_conclusion: str) -> str:
        """
        生成单个行业板块的Markdown报告
        
        Args:
            results: 回测结果列表
            reports_dir: 报告保存目录
            category: 行业分类
            industry_name: 行业名称
            timestamp: 时间戳
            comprehensive_data: 综合结果表数据
            daily_data: 日收益明细数据
            cumulative_data: 累计收益明细数据
            daily_summary_data: 日收益统计摘要数据
            cumulative_summary_data: 累计收益统计摘要数据
            analysis_conclusion: 分析结论
            
        Returns:
            str: 生成的报告文件路径
        """
        if not results:
            raise ValueError("无数据可生成报告")
        
        # 生成带时间戳的文件名
        filename = f"{reports_dir}/{category}_{industry_name}_{timestamp}.md"
        
        # 生成图片的相对路径
        backtest_date = datetime.now().strftime('%Y%m%d')
        daily_chart_path = f"../../../images/{backtest_date}/{category}_{industry_name}_每日收益率_{timestamp}.png"
        cumulative_chart_path = f"../../../images/{backtest_date}/{category}_{industry_name}_累计收益率_{timestamp}.png"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                # 写入报告标题
                f.write(f"# 策略回测结果报告\n\n")
                f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**行业板块**: {industry_name}\n")
                f.write(f"**回测期间**: {results[0]['start_date']} 至 {results[0]['end_date']}\n")
                f.write(f"**策略数量**: {len(results)}\n\n")

                # 写入分析结论
                f.write("## 📈 分析结论\n\n")
                f.write(analysis_conclusion)
                f.write("\n")

                # 写入综合结果表
                f.write("## 📊 综合结果表\n\n")
                if comprehensive_data:
                    comprehensive_df = pd.DataFrame(comprehensive_data)
                    f.write(comprehensive_df.to_markdown(index=False))
                    f.write("\n\n")

                # 插入每日收益率折线图
                f.write("## 📊 每日收益率走势图\n\n")
                f.write(f"![每日收益率走势图]({daily_chart_path})\n\n")
                f.write(f"*图1: {industry_name}板块每日收益率走势对比*\n\n")

                # 插入累计收益率折线图
                f.write("## 📈 累计收益率走势图\n\n")
                f.write(f"![累计收益率走势图]({cumulative_chart_path})\n\n")
                f.write(f"*图2: {industry_name}板块累计收益率走势对比*\n\n")

                # 写入日收益明细表
                f.write("## 📅 日收益明细表\n\n")
                if daily_data:
                    daily_df = pd.DataFrame(daily_data)
                    f.write(daily_df.to_markdown(index=False))
                    f.write("\n\n")
                
                # 写入日收益统计摘要
                f.write("## 📊 日收益统计摘要\n\n")
                if daily_summary_data:
                    summary_df = pd.DataFrame(daily_summary_data)
                    f.write(summary_df.to_markdown(index=False))
                    f.write("\n\n")
                
                # 写入累计收益明细表
                f.write("## 📈 累计收益明细表\n\n")
                if cumulative_data:
                    cumulative_df = pd.DataFrame(cumulative_data)
                    f.write(cumulative_df.to_markdown(index=False))
                    f.write("\n\n")
                
                # 写入累计收益统计摘要
                f.write("## 📊 累计收益统计摘要\n\n")
                if cumulative_summary_data:
                    cumulative_summary_df = pd.DataFrame(cumulative_summary_data)
                    f.write(cumulative_summary_df.to_markdown(index=False))
                    f.write("\n\n")
            
            return filename
            
        except Exception as e:
            raise Exception(f"保存Markdown报告失败: {e}")
    
    def generate_analysis_conclusion(
        self, 
        results: List[Dict[str, Any]], 
        anomaly_alerts: Optional[List[str]] = None
    ) -> str:
        """
        生成分析结论文档内容
        
        Args:
            results: 回测结果列表，包含已计算好的各项指标
            anomaly_alerts: 异动提醒信息列表，由上层分析器提供
            
        Returns:
            str: 格式化的分析结论文档内容
        """
        if not results:
            return "无数据可分析"
        
        conclusion = []
        
        # 策略表现分析
        conclusion.append(self._generate_strategy_performance_section(results))
        
        # 交易活跃度分析
        conclusion.append(self._generate_trading_activity_section(results))
        
        # 异动提醒分析
        conclusion.append(self._generate_anomaly_alerts_section(anomaly_alerts))
        
        # 风险分析
        conclusion.append(self._generate_risk_analysis_section(results))

        return "".join(conclusion)
    
    def _generate_strategy_performance_section(self, results: List[Dict[str, Any]]) -> str:
        """生成策略表现分析部分"""
        if not results:
            return ""
        
        # 找出表现最好的策略
        best_strategy = max(results, key=lambda x: x['total_return'])
        worst_strategy = min(results, key=lambda x: x['total_return'])
        
        section = []
        section.append("### 策略表现分析\n")
        section.append(f"- **最佳策略**: {best_strategy['strategy_name']} (总收益率: {best_strategy['total_return']:.2%})\n")
        section.append(f"- **最差策略**: {worst_strategy['strategy_name']} (总收益率: {worst_strategy['total_return']:.2%})\n")
        
        return "".join(section)
    
    def _generate_trading_activity_section(self, results: List[Dict[str, Any]]) -> str:
        """生成交易活跃度分析部分"""
        if not results:
            return ""
        
        # 交易活跃度分析
        active_strategies = [r for r in results if r['total_trades'] > 0]
        inactive_strategies = [r for r in results if r['total_trades'] == 0]
        
        section = []
        section.append("### 交易活跃度分析\n")
        section.append(f"- **活跃策略**: {len(active_strategies)} 个\n")
        section.append(f"- **非活跃策略**: {len(inactive_strategies)} 个\n")
        
        if active_strategies:
            most_active = max(active_strategies, key=lambda x: x['total_trades'])
            section.append(f"- **最活跃策略**: {most_active['strategy_name']} (交易次数: {most_active['total_trades']})\n")
        
        return "".join(section)
    
    def _generate_anomaly_alerts_section(self, anomaly_alerts: Optional[List[str]]) -> str:
        """生成异动提醒分析部分"""
        section = []
        section.append("### 🚨 异动提醒分析\n")
        
        if anomaly_alerts:
            section.extend(anomaly_alerts)
        else:
            section.append("- 未检测到明显异动情况\n")
        
        return "".join(section)
    
    def _generate_risk_analysis_section(self, results: List[Dict[str, Any]]) -> str:
        """生成风险分析部分"""
        if not results:
            return ""
        
        section = []
        section.append("### 风险分析\n")
        
        for result in results:
            section.append(f"- **{result['strategy_name']}**: 最大回撤 {result['max_drawdown']:.2%}, 夏普比率 {result['sharpe_ratio']:.4f}\n")
        
        return "".join(section)
    
    def generate_anomaly_alerts(self, sector_metrics: Dict[str, Any], strategy_metrics: List[Dict[str, Any]]) -> List[str]:
        """
        根据计算结果生成异动提醒信息
        
        Args:
            sector_metrics: 板块异动指标（由 AnomalyCalculator 计算）
            strategy_metrics: 策略异动指标列表（由 AnomalyCalculator 计算）
            
        Returns:
            List[str]: 异动提醒信息列表
        """
        alerts = []
        
        # 生成板块异动提醒
        sector_alerts = self._generate_sector_alerts(sector_metrics)
        alerts.extend(sector_alerts)
        
        # 生成策略异动提醒
        strategy_alerts = self._generate_strategy_alerts(strategy_metrics)
        alerts.extend(strategy_alerts)
        
        return alerts
    
    def _generate_sector_alerts(self, sector_metrics: Dict[str, Any]) -> List[str]:
        """
        生成板块异动提醒
        
        Args:
            sector_metrics: 板块异动指标
            
        Returns:
            List[str]: 板块异动提醒列表
        """
        alerts = []
        
        if not sector_metrics.get('has_anomaly', False):
            return alerts
        
        industry_name = sector_metrics.get('industry_name', '')
        metrics = sector_metrics.get('metrics', {})
        
        # 波动率异常提醒
        if sector_metrics.get('volatility_anomaly', False):
            recent_std = metrics.get('recent_std', 0)
            overall_std = metrics.get('overall_std', 0)
            alerts.append(f"- **板块异动**: {industry_name} 近两周波动率异常 (近期: {recent_std:.2%}, 整体: {overall_std:.2%})\n")
        
        # 收益率偏离提醒
        if sector_metrics.get('return_deviation_anomaly', False):
            recent_mean = metrics.get('recent_mean', 0)
            overall_mean = metrics.get('overall_mean', 0)
            deviation_direction = metrics.get('deviation_direction', '')
            
            if deviation_direction == 'up':
                alerts.append(f"- **板块异动**: {industry_name} 近两周收益率显著上升 (近期: {recent_mean:.2%}, 整体: {overall_mean:.2%})\n")
            else:
                alerts.append(f"- **板块异动**: {industry_name} 近两周收益率显著下降 (近期: {recent_mean:.2%}, 整体: {overall_mean:.2%})\n")
        
        # 极端波动提醒
        if sector_metrics.get('extreme_volatility_anomaly', False):
            max_extreme = metrics.get('max_extreme', 0)
            min_extreme = metrics.get('min_extreme', 0)
            alerts.append(f"- **板块异动**: {industry_name} 近两周出现极端波动 (最大单日: {max_extreme:.2%}, 最小单日: {min_extreme:.2%})\n")
        
        # 大幅波动提醒
        if sector_metrics.get('high_volatility_anomaly', False):
            max_daily_volatility = metrics.get('max_daily_volatility', 0)
            alerts.append(f"- **板块异动**: {industry_name} 近两周出现大幅波动 (最大单日: {max_daily_volatility:.2%})\n")
        
        # 频繁波动提醒
        if sector_metrics.get('frequent_volatility_anomaly', False):
            volatility_frequency = metrics.get('volatility_frequency', 0)
            alerts.append(f"- **板块异动**: {industry_name} 近两周波动频繁 (方向变化频率: {volatility_frequency:.1%})\n")
        
        return alerts
    
    def _generate_strategy_alerts(self, strategy_metrics: List[Dict[str, Any]]) -> List[str]:
        """
        生成策略异动提醒
        
        Args:
            strategy_metrics: 策略异动指标列表
            
        Returns:
            List[str]: 策略异动提醒列表
        """
        alerts = []
        
        for strategy_metric in strategy_metrics:
            if not strategy_metric.get('has_anomaly', False):
                continue
            
            strategy_name = strategy_metric.get('strategy_name', '')
            metrics = strategy_metric.get('metrics', {})
            
            # 波动率异常提醒
            if strategy_metric.get('volatility_anomaly', False):
                strategy_std = metrics.get('strategy_recent_std', 0)
                overall_std = metrics.get('overall_std', 0)
                alerts.append(f"- **策略异动**: {strategy_name} 近两周波动率异常 (策略: {strategy_std:.2%}, 板块: {overall_std:.2%})\n")
            
            # 收益率偏离提醒
            if strategy_metric.get('return_deviation_anomaly', False):
                strategy_mean = metrics.get('strategy_recent_mean', 0)
                overall_mean = metrics.get('overall_mean', 0)
                deviation_direction = metrics.get('deviation_direction', '')
                
                if deviation_direction == 'up':
                    alerts.append(f"- **策略异动**: {strategy_name} 近两周收益率显著超越板块 (策略: {strategy_mean:.2%}, 板块: {overall_mean:.2%})\n")
                else:
                    alerts.append(f"- **策略异动**: {strategy_name} 近两周收益率显著低于板块 (策略: {strategy_mean:.2%}, 板块: {overall_mean:.2%})\n")
            
            # 极端表现提醒
            if strategy_metric.get('extreme_performance_anomaly', False):
                max_extreme = metrics.get('max_extreme', 0)
                min_extreme = metrics.get('min_extreme', 0)
                alerts.append(f"- **策略异动**: {strategy_name} 近两周出现极端表现 (最大单日: {max_extreme:.2%}, 最小单日: {min_extreme:.2%})\n")
            
            # 大幅波动提醒
            if strategy_metric.get('high_volatility_anomaly', False):
                max_strategy_volatility = metrics.get('max_strategy_volatility', 0)
                alerts.append(f"- **策略异动**: {strategy_name} 近两周出现大幅波动 (最大单日: {max_strategy_volatility:.2%})\n")
            
            # 相关性异常提醒
            if strategy_metric.get('correlation_anomaly', False):
                correlation = metrics.get('correlation', 0)
                alerts.append(f"- **策略异动**: {strategy_name} 与板块走势相关性异常 (相关系数: {correlation:.3f})\n")
        
        return alerts
    
    def get_comprehensive_data(self, results: List[Dict[str, Any]], 
                             sector_performance: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        获取综合结果表数据
        
        Args:
            results: 回测结果列表
            sector_performance: 板块表现数据（由上层计算后传入）
            
        Returns:
            List[Dict[str, Any]]: 综合结果数据
        """
        comprehensive_data = []
        
        # 添加板块实际表现数据
        if sector_performance:
            comprehensive_data.append({
                '策略名称': '板块实际表现',
                '初始资金': f"¥{sector_performance['initial_capital']:,.0f}",
                '最终价值': f"¥{sector_performance['final_value']:,.0f}",
                '总收益率': f"{sector_performance['total_return']:.2%}",
                '年化收益率': f"{sector_performance['annualized_return']:.2%}",
                '波动率': f"{sector_performance['volatility']:.2%}",
                '夏普比率': f"{sector_performance['sharpe_ratio']:.4f}",
                '最大回撤': f"{sector_performance['max_drawdown']:.2%}",
                '总交易次数': 'N/A',
                '买入次数': 'N/A',
                '卖出次数': 'N/A',
                '总交易金额': 'N/A',
                '平均交易金额': 'N/A',
                '交易频率': 'N/A',
                '数据点数': sector_performance['data_points']
            })
        
        # 添加各策略数据
        for result in results:
            trade_stats = result.get('trade_statistics', {})
            
            comprehensive_data.append({
                '策略名称': result['strategy_name'],
                '初始资金': f"¥{result['initial_capital']:,.0f}",
                '最终价值': f"¥{result['final_value']:,.0f}",
                '总收益率': f"{result['total_return']:.2%}",
                '年化收益率': f"{result['annualized_return']:.2%}",
                '波动率': f"{result['volatility']:.2%}",
                '夏普比率': f"{result['sharpe_ratio']:.4f}",
                '最大回撤': f"{result['max_drawdown']:.2%}",
                '总交易次数': result['total_trades'],
                '买入次数': trade_stats.get('buy_trades', 0),
                '卖出次数': trade_stats.get('sell_trades', 0),
                '总交易金额': f"¥{trade_stats.get('total_trade_amount', 0):,.0f}",
                '平均交易金额': f"¥{trade_stats.get('avg_trade_amount', 0):,.0f}",
                '交易频率': f"{trade_stats.get('trading_frequency', 0):.2f}",
                '数据点数': result['data_points']
            })
        
        return comprehensive_data
    
    def get_daily_returns_data(self, results: List[Dict[str, Any]], 
                              sector_daily_returns: Optional[List[float]] = None,
                              historical_data: Optional[pd.DataFrame] = None) -> List[Dict[str, Any]]:
        """
        获取日收益明细数据
        
        Args:
            results: 回测结果列表
            sector_daily_returns: 板块日收益率序列（由上层计算后传入）
            historical_data: 历史数据（用于获取日期信息）
            
        Returns:
            List[Dict[str, Any]]: 日收益明细数据
        """
        if not results:
            return []
        
        daily_data = []
        
        # 获取数据长度
        data_length = len(results[0].get('portfolio_values', []))
        if sector_daily_returns:
            data_length = len(sector_daily_returns)
        
        for i in range(data_length):
            # 获取日期信息
            date_str = f'Day_{i}'
            if historical_data is not None and not historical_data.empty:
                if i < len(historical_data):
                    date_str = historical_data.iloc[i].get('日期', f'Day_{i}')
            
            # 初始化行数据
            row_data = {
                '日期': date_str,
                '板块实际收益率': f"{sector_daily_returns[i] * 100:.2f}%" if sector_daily_returns and i < len(sector_daily_returns) else "0.00%"
            }
            
            # 添加每个策略的日收益率
            for result in results:
                strategy_name = result['strategy_name']
                strategy_daily_returns = result.get('daily_returns', [])
                
                # 获取策略日收益率
                strategy_daily_return = "0.00%"
                if strategy_daily_returns and i < len(strategy_daily_returns):
                    strategy_daily_return = f"{strategy_daily_returns[i] * 100:.2f}%"
                
                row_data[f'{strategy_name}收益率'] = strategy_daily_return
            
            daily_data.append(row_data)
        
        return daily_data
    
    def get_cumulative_returns_data(self, results: List[Dict[str, Any]], 
                                  sector_cumulative_returns: Optional[List[float]] = None,
                                  historical_data: Optional[pd.DataFrame] = None) -> List[Dict[str, Any]]:
        """
        获取每日累计收益率数据
        
        Args:
            results: 回测结果列表
            sector_cumulative_returns: 板块累计收益率序列（由上层计算后传入）
            historical_data: 历史数据（用于获取日期信息）
            
        Returns:
            List[Dict[str, Any]]: 累计收益明细数据
        """
        if not results:
            return []
        
        cumulative_data = []
        
        # 获取数据长度
        data_length = len(results[0].get('portfolio_values', []))
        if sector_cumulative_returns:
            data_length = len(sector_cumulative_returns)
        
        for i in range(data_length):
            # 获取日期信息
            date_str = f'Day_{i}'
            if historical_data is not None and not historical_data.empty:
                if i < len(historical_data):
                    date_str = historical_data.iloc[i].get('日期', f'Day_{i}')
            
            # 初始化行数据
            row_data = {
                '日期': date_str,
                '板块累计收益率': f"{sector_cumulative_returns[i] * 100:.2f}%" if sector_cumulative_returns and i < len(sector_cumulative_returns) else "0.00%"
            }
            
            # 添加每个策略的累计收益率
            for result in results:
                strategy_name = result['strategy_name']
                strategy_cumulative_returns = result.get('cumulative_returns', [])
                
                # 获取策略累计收益率
                strategy_cumulative_return = "0.00%"
                if strategy_cumulative_returns and i < len(strategy_cumulative_returns):
                    strategy_cumulative_return = f"{strategy_cumulative_returns[i] * 100:.2f}%"
                
                row_data[f'{strategy_name}累计收益率'] = strategy_cumulative_return
            
            cumulative_data.append(row_data)
        
        return cumulative_data
    
    def get_daily_returns_summary_data(self, daily_data: List[Dict[str, Any]], 
                                     results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        获取日收益统计摘要数据
        
        Args:
            daily_data: 日收益明细数据
            results: 回测结果列表
            
        Returns:
            List[Dict[str, Any]]: 日收益统计摘要数据
        """
        if not daily_data:
            return []
        
        summary_data = []
        
        # 板块实际收益率统计
        sector_returns = []
        for val in daily_data:
            try:
                sector_returns.append(float(val['板块实际收益率'].replace('%', '')))
            except:
                sector_returns.append(0.0)
        
        summary_data.append({
            '指标': '板块实际收益率',
            '平均日收益率': f"{sum(sector_returns) / len(sector_returns):.2f}%",
            '最大日收益率': f"{max(sector_returns):.2f}%",
            '最小日收益率': f"{min(sector_returns):.2f}%",
            '正收益天数': f"{len([r for r in sector_returns if r > 0])}天",
            '负收益天数': f"{len([r for r in sector_returns if r < 0])}天"
        })
        
        # 各策略收益率统计
        for result in results:
            strategy_name = result['strategy_name']
            col_name = f'{strategy_name}收益率'
            
            if col_name in daily_data[0] if daily_data else False:
                strategy_returns = []
                for val in daily_data:
                    try:
                        strategy_returns.append(float(val[col_name].replace('%', '')))
                    except:
                        strategy_returns.append(0.0)
                
                summary_data.append({
                    '指标': f'{strategy_name}收益率',
                    '平均日收益率': f"{sum(strategy_returns) / len(strategy_returns):.2f}%",
                    '最大日收益率': f"{max(strategy_returns):.2f}%",
                    '最小日收益率': f"{min(strategy_returns):.2f}%",
                    '正收益天数': f"{len([r for r in strategy_returns if r > 0])}天",
                    '负收益天数': f"{len([r for r in strategy_returns if r < 0])}天"
                })
        
        return summary_data
    
    def get_cumulative_returns_summary_data(self, cumulative_data: List[Dict[str, Any]], 
                                           results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        获取累计收益统计摘要数据
        
        Args:
            cumulative_data: 累计收益明细数据
            results: 回测结果列表
            
        Returns:
            List[Dict[str, Any]]: 累计收益统计摘要数据
        """
        if not cumulative_data:
            return []
        
        summary_data = []
        
        # 板块实际累计收益率统计
        sector_cumulative = []
        for val in cumulative_data:
            try:
                sector_cumulative.append(float(val['板块累计收益率'].replace('%', '')))
            except:
                sector_cumulative.append(0.0)
        
        summary_data.append({
            '指标': '板块累计收益率',
            '最终累计收益率': f"{sector_cumulative[-1]:.2f}%",
            '最大累计收益率': f"{max(sector_cumulative):.2f}%",
            '最小累计收益率': f"{min(sector_cumulative):.2f}%",
            '累计收益波动': f"{max(sector_cumulative) - min(sector_cumulative):.2f}%",
            '收益稳定性': f"{'稳定' if max(sector_cumulative) - min(sector_cumulative) < 20 else '波动'}"
        })
        
        # 各策略累计收益率统计
        for result in results:
            strategy_name = result['strategy_name']
            col_name = f'{strategy_name}累计收益率'
            
            if col_name in cumulative_data[0] if cumulative_data else False:
                strategy_cumulative = []
                for val in cumulative_data:
                    try:
                        strategy_cumulative.append(float(val[col_name].replace('%', '')))
                    except:
                        strategy_cumulative.append(0.0)
                
                summary_data.append({
                    '指标': f'{strategy_name}累计收益率',
                    '最终累计收益率': f"{strategy_cumulative[-1]:.2f}%",
                    '最大累计收益率': f"{max(strategy_cumulative):.2f}%",
                    '最小累计收益率': f"{min(strategy_cumulative):.2f}%",
                    '累计收益波动': f"{max(strategy_cumulative) - min(strategy_cumulative):.2f}%",
                    '收益稳定性': f"{'稳定' if max(strategy_cumulative) - min(strategy_cumulative) < 20 else '波动'}"
                })
        
        return summary_data
