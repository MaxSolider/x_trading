"""
多行业板块总结报告生成器
负责生成多行业板块的策略回测总结报告
整合了市场分析、策略排行、风险收益分析、异动检测汇总和投资建议功能
"""

import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime


class SectorsSummaryGenerator:
    """多行业板块总结报告生成器 - 整合多行业板块总结报告生成的所有功能"""
    
    def __init__(self):
        """初始化多行业板块总结报告生成器"""
        pass
    
    def generate_summary_report(self,
                              all_results: List[List[Dict[str, Any]]],
                              summary_dir: str,
                              timestamp: str,
                              market_analysis: str,
                              sector_analysis: str,
                              industry_analysis: str,
                              strategy_ranking: str,
                              risk_return_analysis: str,
                              anomaly_summary: str,
                              investment_recommendations: str) -> str:
        """
        生成多行业板块回测总结报告
        
        Args:
            all_results: 多个行业板块的回测结果列表
            summary_dir: 总结报告保存目录
            timestamp: 时间戳
            market_analysis: 市场整体分析
            sector_analysis: 板块分类分析
            industry_analysis: 行业明细分析
            strategy_ranking: 策略表现排行
            risk_return_analysis: 风险收益分析
            anomaly_summary: 异动检测汇总
            investment_recommendations: 投资建议
            
        Returns:
            str: 生成的报告文件路径
        """
        if not all_results:
            raise ValueError("无回测数据可总结")
        
        # 生成带时间戳的文件名
        filename = f"{summary_dir}/多板块策略回测总结_{timestamp}.md"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                # 写入报告标题
                f.write(f"# 多行业板块策略回测总结报告\n\n")
                f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**回测板块数量**: {len(all_results)}\n")
                f.write(f"**总策略数量**: {sum(len(results) for results in all_results)}\n\n")
                
                # 1. 市场整体分析
                f.write("## 📊 市场整体分析\n\n")
                f.write(market_analysis)
                f.write("\n")
                
                # 2. 板块分类分析
                f.write("## 🏢 板块分类分析\n\n")
                f.write(sector_analysis)
                f.write("\n")
                
                # 3. 行业明细分析
                f.write("## 📈 行业明细分析\n\n")
                f.write(industry_analysis)
                f.write("\n")
                
                # 4. 策略表现排行
                f.write("## 🏆 策略表现排行\n\n")
                f.write(strategy_ranking)
                f.write("\n")
                
                # 5. 风险收益分析
                f.write("## ⚖️ 风险收益分析\n\n")
                f.write(risk_return_analysis)
                f.write("\n")
                
                # 6. 异动检测汇总
                f.write("## 🚨 异动检测汇总\n\n")
                f.write(anomaly_summary)
                f.write("\n")
                
                # 7. 投资建议
                f.write("## 💡 投资建议\n\n")
                f.write(investment_recommendations)
                f.write("\n")
            
            return filename
            
        except Exception as e:
            raise Exception(f"生成整体回测报告失败: {e}")
    
    def generate_market_overall_analysis(self, market_stats: Dict[str, Any]) -> str:
        """
        生成市场整体分析
        
        Args:
            market_stats: 市场整体统计指标，由MarketCalculator计算提供
            
        Returns:
            str: 格式化的市场整体分析文档内容
        """
        if not market_stats or market_stats.get('total_strategies', 0) == 0:
            return "无数据可分析"
        
        analysis = []
        
        # 使用表格展示市场概况
        analysis.append(f"### 📈 市场概况\n\n")
        market_overview_data = [
            {
                '指标': '回测板块数量',
                '数值': f"{market_stats['total_industries']} 个",
                '说明': '参与回测的行业板块总数'
            },
            {
                '指标': '总策略数量',
                '数值': f"{market_stats['total_strategies']} 个",
                '说明': '所有策略实例的总数'
            },
            {
                '指标': '策略胜率',
                '数值': f"{market_stats['win_rate']:.1%}",
                '说明': '获得正收益的策略比例'
            },
            {
                '指标': '超越基准比例',
                '数值': f"{market_stats['benchmark_beating_rate']:.1%}",
                '说明': '收益率超过10%的策略比例'
            }
        ]
        
        market_overview_df = pd.DataFrame(market_overview_data)
        analysis.append(market_overview_df.to_markdown(index=False))
        analysis.append("\n\n")
        
        # 使用表格展示收益率统计
        analysis.append(f"### 📊 收益率统计\n\n")
        
        returns_stats_data = [
            {
                '指标': '平均总收益率',
                '数值': f"{market_stats['avg_total_return']:.2%}",
                '说明': '所有策略的平均表现'
            },
            {
                '指标': '中位数总收益率',
                '数值': f"{market_stats['median_total_return']:.2%}",
                '说明': '策略收益率的中位数'
            },
            {
                '指标': '最佳策略收益率',
                '数值': f"{market_stats['best_return']:.2%}",
                '说明': f"{market_stats['best_strategy']['industry_name']} - {market_stats['best_strategy']['strategy_name']}"
            },
            {
                '指标': '最差策略收益率',
                '数值': f"{market_stats['worst_return']:.2%}",
                '说明': f"{market_stats['worst_strategy']['industry_name']} - {market_stats['worst_strategy']['strategy_name']}"
            }
        ]
        
        returns_stats_df = pd.DataFrame(returns_stats_data)
        analysis.append(returns_stats_df.to_markdown(index=False))
        analysis.append("\n")
        
        return "".join(analysis)
    
    def generate_sector_category_analysis(self, category_stats: List[Dict[str, Any]]) -> str:
        """
        生成板块分类分析
        
        Args:
            category_stats: 板块分类统计指标列表，由MarketCalculator计算提供
            
        Returns:
            str: 格式化的板块分类分析文档内容
        """
        if not category_stats:
            return "无数据可分析"
        
        analysis = []
        
        # 使用表格展示板块分类表现对比
        analysis.append(f"### 🏢 板块分类表现对比\n\n")
        category_comparison_data = []
        
        for stats in category_stats:
            category_comparison_data.append({
                '排名': f"#{stats['ranking']}",
                '板块分类': stats['category'],
                '包含板块数': f"{stats['industry_count']} 个",
                '策略数量': f"{stats['strategy_count']} 个",
                '平均总收益率': f"{stats['avg_return']:.2%}",
                '平均夏普比率': f"{stats['avg_sharpe']:.4f}",
                '平均最大回撤': f"{stats['avg_drawdown']:.2%}",
                '策略胜率': f"{stats['win_rate']:.1%}"
            })
        
        category_comparison_df = pd.DataFrame(category_comparison_data)
        analysis.append(category_comparison_df.to_markdown(index=False))
        analysis.append("\n")
        
        return "".join(analysis)
    
    def generate_industry_detail_analysis(self, industry_stats: List[Dict[str, Any]], 
                                        industry_win_rates: Dict[str, float]) -> str:
        """
        生成行业明细分析
        
        Args:
            industry_stats: 行业统计指标列表，由MarketCalculator计算提供
            industry_win_rates: 各行业胜率字典，由MarketCalculator计算提供
            
        Returns:
            str: 格式化的行业明细分析文档内容
        """
        if not industry_stats:
            return "无数据可分析"
        
        analysis = []
        
        # 使用表格展示行业表现排行榜
        analysis.append(f"### 📈 行业表现排行榜\n\n")
        industry_ranking_data = []
        
        for i, stats in enumerate(industry_stats, 1):
            industry_name = stats['industry']
            win_rate = industry_win_rates.get(industry_name, 0.0)
            
            industry_ranking_data.append({
                '排名': f"#{i}",
                '行业板块': stats['industry'],
                '分类': stats['category'],
                '策略数量': f"{stats['strategy_count']} 个",
                '平均总收益率': f"{stats['avg_return']:.2%}",
                '平均夏普比率': f"{stats['avg_sharpe']:.4f}",
                '平均最大回撤': f"{stats['avg_drawdown']:.2%}",
                '策略胜率': f"{win_rate:.1%}",
                '最佳策略': f"{stats['best_strategy']} ({stats['best_return']:.2%})"
            })
        
        industry_ranking_df = pd.DataFrame(industry_ranking_data)
        analysis.append(industry_ranking_df.to_markdown(index=False))
        analysis.append("\n\n")
        
        # 使用表格展示Top 10行业详细分析（合并表格）
        analysis.append(f"### 🏆 Top 10 行业详细分析\n\n")
        top_industries = industry_stats[:10]
        
        # 创建合并的表格数据
        top10_combined_data = []
        for i, stats in enumerate(top_industries, 1):
            top10_combined_data.append({
                '排名': f"#{i}",
                '行业板块': stats['industry'],
                '分类': stats['category'],
                '策略数量': f"{stats['strategy_count']} 个",
                '平均总收益率': f"{stats['avg_return']:.2%}",
                '平均夏普比率': f"{stats['avg_sharpe']:.4f}",
                '平均最大回撤': f"{stats['avg_drawdown']:.2%}",
                '最佳策略': f"{stats['best_strategy']} ({stats['best_return']:.2%})",
                '最差策略': f"{stats['worst_strategy']} ({stats['worst_return']:.2%})"
            })
        
        top10_combined_df = pd.DataFrame(top10_combined_data)
        analysis.append(top10_combined_df.to_markdown(index=False))
        analysis.append("\n")
        
        return "".join(analysis)
    
    def generate_strategy_ranking(self, strategy_ranking_data: Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]) -> str:
        """
        生成策略表现排行
        
        Args:
            strategy_ranking_data: 策略排行数据元组，包含(策略排行列表, 策略类型统计列表)，由MarketCalculator计算提供
            
        Returns:
            str: 格式化的策略表现排行文档内容
        """
        all_strategies, strategy_type_data = strategy_ranking_data
        
        if not all_strategies:
            return "无策略数据可分析"
        
        analysis = []
        
        # 使用表格展示策略表现排行榜（Top 20）
        analysis.append(f"### 🏆 策略表现排行榜（Top 20）\n\n")
        top_strategies = all_strategies[:20]
        
        strategy_ranking_data = []
        for i, strategy in enumerate(top_strategies, 1):
            strategy_ranking_data.append({
                '排名': f"#{i}",
                '策略名称': strategy['strategy_name'],
                '行业板块': strategy['industry_name'],
                '总收益率': f"{strategy['total_return']:.2%}",
                '年化收益率': f"{strategy['annualized_return']:.2%}",
                '夏普比率': f"{strategy['sharpe_ratio']:.4f}",
                '最大回撤': f"{strategy['max_drawdown']:.2%}",
                '交易次数': f"{strategy['total_trades']} 次"
            })
        
        strategy_ranking_df = pd.DataFrame(strategy_ranking_data)
        analysis.append(strategy_ranking_df.to_markdown(index=False))
        analysis.append("\n\n")
        
        # 使用表格展示策略类型表现统计
        analysis.append(f"### 📊 策略类型表现统计\n\n")
        
        strategy_type_table_data = []
        for stats in strategy_type_data:
            strategy_type_table_data.append({
                '策略类型': stats['strategy_type'],
                '实例数量': f"{stats['count']} 个",
                '平均收益率': f"{stats['avg_return']:.2%}",
                '最佳收益率': f"{stats['max_return']:.2%}",
                '最差收益率': f"{stats['min_return']:.2%}",
                '胜率': f"{stats['win_rate']:.1%}"
            })
        
        strategy_type_df = pd.DataFrame(strategy_type_table_data)
        analysis.append(strategy_type_df.to_markdown(index=False))
        analysis.append("\n")
        
        return "".join(analysis)
    
    def generate_risk_return_analysis(self, risk_return_stats: Dict[str, Any]) -> str:
        """
        生成风险收益分析
        
        Args:
            risk_return_stats: 风险收益统计指标，由MarketCalculator计算提供
            
        Returns:
            str: 格式化的风险收益分析文档内容
        """
        if not risk_return_stats:
            return "无数据可分析"
        
        analysis = []
        
        returns_distribution = risk_return_stats.get('returns_distribution', {})
        risk_distribution = risk_return_stats.get('risk_distribution', {})
        quadrant_analysis = risk_return_stats.get('quadrant_analysis', {})
        
        # 使用表格展示收益率分布
        analysis.append(f"### 📊 收益率分布\n\n")
        returns_distribution_data = [
            {
                '指标': '收益率范围',
                '数值': f"{returns_distribution.get('min_return', 0):.2%} ~ {returns_distribution.get('max_return', 0):.2%}",
                '说明': '策略收益率的最小值和最大值'
            },
            {
                '指标': '收益率标准差',
                '数值': f"{returns_distribution.get('std_return', 0):.2%}",
                '说明': '收益率离散程度'
            },
            {
                '指标': '收益率偏度',
                '数值': f"{returns_distribution.get('skewness', 0):.4f}",
                '说明': '收益率分布的不对称性'
            },
            {
                '指标': '收益率峰度',
                '数值': f"{returns_distribution.get('kurtosis', 0):.4f}",
                '说明': '收益率分布的尖锐程度'
            }
        ]
        
        returns_distribution_df = pd.DataFrame(returns_distribution_data)
        analysis.append(returns_distribution_df.to_markdown(index=False))
        analysis.append("\n\n")
        
        # 使用表格展示风险分布
        analysis.append(f"### ⚠️ 风险分布\n\n")
        volatility_range = risk_distribution.get('volatility_range', (0, 0))
        max_drawdown_range = risk_distribution.get('max_drawdown_range', (0, 0))
        sharpe_range = risk_distribution.get('sharpe_range', (0, 0))
        
        risk_distribution_data = [
            {
                '风险指标': '波动率',
                '范围': f"{volatility_range[0]:.2%} ~ {volatility_range[1]:.2%}",
                '平均值': f"{risk_distribution.get('volatility_mean', 0):.2%}",
                '风险等级': '中等'
            },
            {
                '风险指标': '最大回撤',
                '范围': f"{max_drawdown_range[0]:.2%} ~ {max_drawdown_range[1]:.2%}",
                '平均值': f"{risk_distribution.get('max_drawdown_mean', 0):.2%}",
                '风险等级': '中等'
            },
            {
                '风险指标': '夏普比率',
                '范围': f"{sharpe_range[0]:.4f} ~ {sharpe_range[1]:.4f}",
                '平均值': f"{risk_distribution.get('sharpe_mean', 0):.4f}",
                '风险等级': '中等'
            }
        ]
        
        risk_distribution_df = pd.DataFrame(risk_distribution_data)
        analysis.append(risk_distribution_df.to_markdown(index=False))
        analysis.append("\n\n")
        
        # 使用表格展示风险收益象限分析
        analysis.append(f"### 🎯 风险收益象限分析\n\n")
        
        def format_strategy_details(strategies):
            if not strategies:
                return "无"
            details = []
            for s in strategies[:3]:  # 只显示前3个
                details.append(f"{s['industry_name']}-{s['strategy_name']}({s['total_return']:.1%})")
            if len(strategies) > 3:
                details.append(f"...等{len(strategies)}个")
            return ", ".join(details)
        
        total_strategies = quadrant_analysis.get('total_strategies', 0)
        if total_strategies > 0:
            high_return_high_risk = quadrant_analysis.get('high_return_high_risk', {})
            high_return_low_risk = quadrant_analysis.get('high_return_low_risk', {})
            low_return_high_risk = quadrant_analysis.get('low_return_high_risk', {})
            low_return_low_risk = quadrant_analysis.get('low_return_low_risk', {})
            
            quadrant_data = [
                {
                    '象限': '高收益高风险',
                    '策略数量': f"{high_return_high_risk.get('count', 0)} 个",
                    '占比': f"{high_return_high_risk.get('count', 0)/total_strategies:.1%}",
                    '特征': '收益和风险都较高',
                    '建议': '适合风险偏好较高的投资者',
                    '明细': format_strategy_details(high_return_high_risk.get('strategies', []))
                },
                {
                    '象限': '高收益低风险',
                    '策略数量': f"{high_return_low_risk.get('count', 0)} 个",
                    '占比': f"{high_return_low_risk.get('count', 0)/total_strategies:.1%}",
                    '特征': '理想投资组合',
                    '建议': '优先推荐',
                    '明细': format_strategy_details(high_return_low_risk.get('strategies', []))
                },
                {
                    '象限': '低收益高风险',
                    '策略数量': f"{low_return_high_risk.get('count', 0)} 个",
                    '占比': f"{low_return_high_risk.get('count', 0)/total_strategies:.1%}",
                    '特征': '收益低但风险高',
                    '建议': '不推荐',
                    '明细': format_strategy_details(low_return_high_risk.get('strategies', []))
                },
                {
                    '象限': '低收益低风险',
                    '策略数量': f"{low_return_low_risk.get('count', 0)} 个",
                    '占比': f"{low_return_low_risk.get('count', 0)/total_strategies:.1%}",
                    '特征': '保守型投资',
                    '建议': '适合风险厌恶型投资者',
                    '明细': format_strategy_details(low_return_low_risk.get('strategies', []))
                }
            ]
            
            quadrant_df = pd.DataFrame(quadrant_data)
            analysis.append(quadrant_df.to_markdown(index=False))
            analysis.append("\n")
        
        return "".join(analysis)
    
    def generate_anomaly_summary(self, all_anomalies: List[str]) -> str:
        """
        生成异动检测汇总
        
        Args:
            all_anomalies: 所有异动信息列表，由上层分析器提供
            
        Returns:
            str: 格式化的异动检测汇总文档内容
        """
        analysis = []
        
        analysis.append(f"### 异动检测汇总\n\n")
        
        if not all_anomalies:
            analysis.append("✅ 未检测到明显异动情况\n\n")
        else:
            analysis.append(f"🚨 共检测到 {len(all_anomalies)} 个异动情况：\n\n")
            
            # 按类型分类异动
            sector_anomalies = [a for a in all_anomalies if '板块异动' in a]
            strategy_anomalies = [a for a in all_anomalies if '策略异动' in a]
            
            if sector_anomalies:
                analysis.append(f"#### 板块异动 ({len(sector_anomalies)}个)\n")
                for anomaly in sector_anomalies:
                    analysis.append(f"- {anomaly.strip()}\n")
                analysis.append("\n")
            
            if strategy_anomalies:
                analysis.append(f"#### 策略异动 ({len(strategy_anomalies)}个)\n")
                for anomaly in strategy_anomalies:
                    analysis.append(f"- {anomaly.strip()}\n")
                analysis.append("\n")
        
        return "".join(analysis)
    
    def generate_investment_recommendations(self, recommendation_data: Tuple[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]) -> str:
        """
        生成投资建议
        
        Args:
            recommendation_data: 投资建议数据元组，包含(推荐策略列表, 各行业最佳策略字典)，由MarketCalculator计算提供
            
        Returns:
            str: 格式化的投资建议文档内容
        """
        best_strategies, industry_best = recommendation_data
        
        if not best_strategies:
            return "无策略数据可分析"
        
        analysis = []
        
        analysis.append(f"### 💡 投资建议\n\n")
        
        # 使用表格展示推荐策略（Top 5）
        analysis.append(f"#### 🏆 推荐策略（Top 5）\n\n")
        top5_data = []
        for i, strategy in enumerate(best_strategies, 1):
            top5_data.append({
                '排名': f"#{i}",
                '策略名称': strategy['strategy_name'],
                '行业板块': strategy['industry_name'],
                '总收益率': f"{strategy['total_return']:.2%}",
                '夏普比率': f"{strategy['sharpe_ratio']:.4f}",
                '最大回撤': f"{strategy['max_drawdown']:.2%}",
                '交易次数': f"{strategy['total_trades']} 次"
            })
        
        top5_df = pd.DataFrame(top5_data)
        analysis.append(top5_df.to_markdown(index=False))
        analysis.append("\n\n")
        
        # 使用表格展示各行业推荐策略
        analysis.append(f"#### 🏢 各行业推荐策略\n\n")
        industry_recommendations_data = []
        for industry, strategy in industry_best.items():
            industry_recommendations_data.append({
                '行业板块': industry,
                '推荐策略': strategy['strategy_name'],
                '总收益率': f"{strategy['total_return']:.2%}",
                '夏普比率': f"{strategy['sharpe_ratio']:.4f}",
                '最大回撤': f"{strategy['max_drawdown']:.2%}",
                '交易次数': f"{strategy['total_trades']} 次"
            })
        
        industry_recommendations_df = pd.DataFrame(industry_recommendations_data)
        analysis.append(industry_recommendations_df.to_markdown(index=False))
        analysis.append("\n")
        
        return "".join(analysis)
