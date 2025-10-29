"""
市场复盘服务
提供市场复盘分析功能，包括市场总结、板块分析、个股分析和报告生成
"""

import pandas as pd
from typing import Dict, Any, Optional, List
from datetime import datetime
import os

from ...strategies.market_sentiment.market_sentiment_strategy import MarketSentimentStrategy
from ...utils.docs.market_report_generator import MarketReportGenerator
from ...utils.date.date_utils import DateUtils
from ...static.industry_sectors import get_stocks_by_category, get_industry_category
from ...strategies.individual_stock.trend_tracking_strategy import IndividualTrendTrackingStrategy

class MarketReviewService:
    """市场复盘服务类"""
    
    def __init__(self):
        """初始化市场复盘服务"""
        self.sentiment_strategy = MarketSentimentStrategy()
        self.report_generator = MarketReportGenerator()
        
        # 报告生成目录
        self.reports_dir = "reports/review"
        os.makedirs(self.reports_dir, exist_ok=True)
        
        print("✅ 市场复盘服务初始化成功")
    
    def conduct_market_review(self, date: str = None) -> Dict[str, Any]:
        """
        执行市场复盘分析
        
        Args:
            date: 复盘日期，格式为'YYYYMMDD'，默认为今天
            
        Returns:
            Dict[str, Any]: 市场复盘分析结果
        """
        try:
            if not date:
                date = DateUtils.get_recent_trading_day()
            
            print(f"🔍 开始执行 {date} 的市场复盘分析...")
            
            # 1. 市场总结
            print("📊 正在分析市场总结...")
            market_summary = self._analyze_market_summary(date)
            
            # 2. 板块分析
            print("🏢 正在分析板块表现...")
            sector_analysis = self._analyze_sector_performance(date)
            
            # 3. 个股分析
            print("🎯 正在分析个股表现...")
            # 获取有买入信号，以及中性信号TOP10板块下的所有股票，再将股票传入_analyze_stock_performance中进行分析
            stock_analysis = self._analyze_stock_performance(date, sector_analysis)
            
            # 4. 生成报告
            print("📋 正在生成复盘报告...")
            report_path = self._generate_review_report(
                date, market_summary, sector_analysis, stock_analysis
            )
            
            # 汇总结果
            result = {
                'review_date': date,
                'market_summary': market_summary,
                'sector_analysis': sector_analysis,
                'stock_analysis': stock_analysis,
                'report_path': report_path,
                'status': 'success'
            }
            
            print(f"✅ 市场复盘分析完成，报告已生成: {report_path}")
            return result
            
        except Exception as e:
            print(f"❌ 市场复盘分析失败: {e}")
            import traceback
            traceback.print_exc()
            return {
                'review_date': date,
                'status': 'failed',
                'error': str(e)
            }
    
    def _analyze_market_summary(self, date: str) -> Dict[str, Any]:
        """
        分析市场总结
        
        Args:
            date: 分析日期
            
        Returns:
            Dict[str, Any]: 市场总结分析结果
        """
        try:
            # 使用市场情绪分析策略获取市场数据
            sentiment_result = self.sentiment_strategy.analyze_market_sentiment(date)
            
            if not sentiment_result:
                return {'error': '无法获取市场情绪数据'}
            
            # 提取关键数据
            raw_data = sentiment_result.get('raw_data', {})
            sentiment_scores = sentiment_result.get('sentiment_scores', {})
            
            # 构建市场总结数据
            market_summary = {
                'analysis_date': date,
                'overall_sentiment': sentiment_result.get('overall_sentiment', 0),
                'sentiment_level': sentiment_result.get('sentiment_level', '未知'),
                'sentiment_scores': sentiment_scores,
                'key_metrics': self._extract_key_metrics(raw_data),
                'radar_chart_path': sentiment_result.get('radar_chart_path')
            }
            
            return market_summary
            
        except Exception as e:
            print(f"❌ 市场总结分析失败: {e}")
            return {'error': f'市场总结分析失败: {str(e)}'}
    
    def _extract_key_metrics(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        从原始数据中提取关键指标
        
        Args:
            raw_data: 市场情绪分析的原始数据
            
        Returns:
            Dict[str, Any]: 关键指标数据
        """
        try:
            key_metrics = {}
            
            # 市场活跃度指标
            key_metrics['market_activity'] = raw_data.get('market_activity', {})
            
            # 个股赚钱效应指标
            key_metrics['market_summary'] = raw_data.get('market_summary', {})
            key_metrics['breakout_data'] = raw_data.get('breakout_data', {})
            
            # 风险偏好指标
            key_metrics['risk_preference'] = raw_data.get('margin_data', {})
            
            # 市场参与意愿指标
            key_metrics['participation_willingness'] = raw_data.get('fund_flow_data', {})
            
            return key_metrics
            
        except Exception as e:
            print(f"❌ 提取关键指标失败: {e}")
            return {}

    def _analyze_sector_performance(self, date: str) -> Dict[str, Any]:
        """
        分析板块表现 - 计算所有板块的量价数据和MACD数据并生成趋势图

        Args:
            date: 分析日期

        Returns:
            Dict[str, Any]: 板块分析结果，包含量价分析和MACD分析结果

        """
        try:
            from ...static.industry_sectors import INDUSTRY_SECTORS
            from ...repositories.stock.industry_info_query import IndustryInfoQuery
            from datetime import datetime, timedelta
            
            print(f"🔍 开始综合分析 {len(INDUSTRY_SECTORS)} 个板块的表现...")
            
            # 0. 先批量获取所有板块近120天历史数据
            print(f"\n📦 第零步：批量获取所有板块近120天历史数据...")
            industry_query = IndustryInfoQuery()
            start_date = (datetime.strptime(date, '%Y%m%d') - timedelta(days=120)).strftime('%Y%m%d')
            
            sector_data_dict = {}
            for i, sector_name in enumerate(INDUSTRY_SECTORS, 1):
                try:
                    print(f"📊 正在获取板块 {i}/{len(INDUSTRY_SECTORS)}: {sector_name}")
                    hist_data = industry_query.get_board_industry_hist(sector_name, start_date, date)
                    if hist_data is not None and not hist_data.empty:
                        sector_data_dict[sector_name] = hist_data
                        print(f"✅ {sector_name} 历史数据获取成功")
                    else:
                        print(f"⚠️ {sector_name} 历史数据获取失败")
                except Exception as e:
                    print(f"❌ {sector_name} 历史数据获取失败: {e}")
                    continue
            
            print(f"✅ 成功获取 {len(sector_data_dict)}/{len(INDUSTRY_SECTORS)} 个板块的历史数据")
            
            # 1. 量价分析
            print(f"\n📊 第一步：进行量价分析...")
            volume_price_analysis = self._analyze_sector_volume_price_performance(date, sector_data_dict)
            
            # 2. MACD分析
            print(f"\n📈 第二步：进行MACD分析...")
            macd_analysis = self._analyze_sector_macd_performance(date, sector_data_dict)
            
            # 3. 合并分析结果
            print(f"\n🔄 第三步：合并分析结果...")
            combined_results = self._combine_sector_analysis_results(
                volume_price_analysis, macd_analysis, date
            )
            
            print(f"✅ 板块综合分析完成！")
            
            return combined_results
            
        except Exception as e:
            print(f"❌ 板块综合分析失败: {e}")
            import traceback
            traceback.print_exc()
            return {
                'status': 'failed',
                'error': str(e),
                'analysis_date': date
            }

    def _analyze_sector_volume_price_performance(self, date: str, sector_data_dict: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """
        分析板块量价表现
        
        Args:
            date: 分析日期
            sector_data_dict: 板块数据字典
            
        Returns:
            Dict[str, Any]: 量价分析结果
        """
        try:
            from ...static.industry_sectors import INDUSTRY_SECTORS
            from ...strategies.industry_sector.volume_price_strategy import VolumePriceStrategy
            
            print(f"🔍 开始分析 {len(INDUSTRY_SECTORS)} 个板块的量价表现...")
            
            # 初始化量价策略
            volume_price_strategy = VolumePriceStrategy()
            
            # 存储所有板块的量价分析结果
            sector_results = {}
            chart_paths = {}
            signal_summary = {
                'BUY': [],
                'HOLD': [],
                'CAUTION': [],
                'SELL': [],
                'PANIC': [],
                'NEUTRAL': []
            }
            
            # 计算开始日期（获取最近60个交易日的数据，确保有足够数据计算MA20）
            from datetime import datetime, timedelta
            start_date = (datetime.strptime(date, '%Y%m%d') - timedelta(days=60)).strftime('%Y%m%d')
            
            # 遍历所有板块
            for i, sector_name in enumerate(INDUSTRY_SECTORS, 1):
                try:
                    print(f"📊 正在分析板块 {i}/{len(INDUSTRY_SECTORS)}: {sector_name}")
                    
                    # 从预查询的数据中获取
                    hist_data = sector_data_dict.get(sector_name)
                    if hist_data is None or hist_data.empty:
                        print(f"⚠️ {sector_name} 没有历史数据，跳过")
                        continue
                    
                    # 使用预查询的数据进行分析
                    volume_price_result = volume_price_strategy.analyze_volume_price_relationship_with_data(
                        sector_name, hist_data, date
                    )
                    
                    if volume_price_result is None:
                        print(f"⚠️ {sector_name} 量价分析失败，跳过")
                        continue
                    
                    # 生成量价关系趋势图（使用预查询的数据）
                    chart_path = volume_price_strategy.generate_volume_price_trend_chart_with_data(
                        sector_name, hist_data, date, "reports/images/sectors/volume_price"
                    )
                    
                    if chart_path:
                        chart_paths[sector_name] = chart_path
                        print(f"✅ {sector_name} 量价关系图表已生成: {chart_path}")
                    
                    # 存储分析结果
                    trading_signal = volume_price_result.get('trading_signal', {})
                    volume_price_analysis = volume_price_result.get('volume_price_analysis', {})
                    
                    sector_results[sector_name] = {
                        'latest_price': volume_price_analysis.get('latest_price', 0),
                        'latest_volume': volume_price_analysis.get('latest_volume', 0),
                        'price_change_pct': volume_price_analysis.get('price_change_pct', 0),
                        'volume_change_pct': volume_price_analysis.get('volume_change_pct', 0),
                        'latest_relationship': volume_price_analysis.get('latest_relationship', '未知'),
                        'signal_type': trading_signal.get('signal_type', 'UNKNOWN'),
                        'signal_strength': trading_signal.get('signal_strength', 0),
                        'comprehensive_score': volume_price_analysis.get('volume_price_strength', {}).get('comprehensive_score', 0),
                        'strength_level': volume_price_analysis.get('volume_price_strength', {}).get('strength_level', '未知'),
                        'chart_path': chart_path,
                        'analysis_date': date
                    }
                    
                    # 统计信号类型
                    signal_type = trading_signal.get('signal_type', 'UNKNOWN')
                    if signal_type in signal_summary:
                        signal_summary[signal_type].append(sector_name)
                    
                except Exception as e:
                    print(f"❌ {sector_name} 量价分析失败: {e}")
                    continue
            
            # 打印分析结果摘要
            print(f"\n📊 板块量价分析完成！")
            print(f"📈 买入信号板块: {len(signal_summary['BUY'])}个")
            print(f"📉 卖出信号板块: {len(signal_summary['SELL'])}个")
            print(f"➡️ 中性信号板块: {len(signal_summary['NEUTRAL'])}个")
            
            return {
                'status': 'success',
                'analysis_date': date,
                'total_sectors': len(INDUSTRY_SECTORS),
                'analyzed_sectors': len(sector_results),
                'sector_results': sector_results,
                'chart_paths': chart_paths,
                'signal_summary': signal_summary
            }
            
        except Exception as e:
            print(f"❌ 板块量价分析失败: {e}")
            import traceback
            traceback.print_exc()
            return {
                'status': 'failed',
                'error': str(e),
                'analysis_date': date
            }

    def _analyze_sector_macd_performance(self, date: str, sector_data_dict: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """
        分析板块表现 - 计算所有板块的MACD数据并生成趋势图
        
        Args:
            date: 分析日期
            sector_data_dict: 板块数据字典
            
        Returns:
            Dict[str, Any]: 板块分析结果
        """
        try:
            from ...static.industry_sectors import INDUSTRY_SECTORS
            from ...strategies.industry_sector.macd_strategy import IndustryMACDStrategy
            from ...utils.graphics.chart_generator import ChartGenerator
            
            print(f"🔍 开始分析 {len(INDUSTRY_SECTORS)} 个板块的MACD表现...")
            
            # 初始化策略和图表生成器
            macd_strategy = IndustryMACDStrategy()
            chart_generator = ChartGenerator()
            
            # 创建MACD图表保存目录
            macd_charts_dir = f"reports/images/sectors/macd"
            os.makedirs(macd_charts_dir, exist_ok=True)
            
            # 存储所有板块的分析结果
            sector_results = {}
            chart_paths = {}
            signal_summary = {
                'buy_signals': [],
                'sell_signals': [],
                'neutral_signals': []
            }
            
            # 计算开始日期（获取最近60个交易日的数据）
            from datetime import datetime, timedelta
            start_date = (datetime.strptime(date, '%Y%m%d') - timedelta(days=120)).strftime('%Y%m%d')
            
            # 遍历所有板块
            for i, sector_name in enumerate(INDUSTRY_SECTORS, 1):
                try:
                    print(f"📊 正在分析板块 {i}/{len(INDUSTRY_SECTORS)}: {sector_name}")
                    
                    # 从预查询的数据中获取
                    hist_data = sector_data_dict.get(sector_name)
                    if hist_data is None or hist_data.empty:
                        print(f"⚠️ {sector_name} 没有历史数据，跳过")
                        continue
                    
                    # 使用预查询的数据进行分析
                    macd_result = macd_strategy.analyze_industry_macd_with_data(
                        sector_name, hist_data, date
                    )
                    
                    if macd_result is None:
                        print(f"⚠️ {sector_name} MACD分析失败，跳过")
                        continue
                    
                    # 计算MACD数据
                    macd_data = macd_strategy.calculate_macd(hist_data)
                    if macd_data is None:
                        print(f"⚠️ {sector_name} MACD计算失败，跳过")
                        continue
                    
                    # 生成MACD趋势图
                    chart_filename = f"{sector_name}_{date}.png"
                    chart_path = os.path.join(macd_charts_dir, chart_filename)
                    
                    chart_path_result = self._generate_macd_chart(
                        macd_data, sector_name, date, chart_path
                    )
                    
                    if chart_path_result:
                        chart_paths[sector_name] = chart_path_result
                        print(f"✅ {sector_name} MACD图表已生成: {chart_path_result}")
                    else:
                        print(f"⚠️ {sector_name} MACD图表生成失败")
                    
                    # 存储分析结果
                    sector_results[sector_name] = {
                        'latest_macd': macd_result['latest_macd'],
                        'latest_signal': macd_result['latest_signal'],
                        'latest_histogram': macd_result['latest_histogram'],
                        'current_signal_type': macd_result['current_signal_type'],
                        'zero_cross_status': macd_result['zero_cross_status'],
                        'chart_path': chart_path_result,
                        'analysis_date': macd_result['analysis_date']
                    }
                    
                    # 分类交易信号
                    signal_type = macd_result['current_signal_type']
                    if signal_type == 'BUY':
                        signal_summary['buy_signals'].append(sector_name)
                    elif signal_type == 'SELL':
                        signal_summary['sell_signals'].append(sector_name)
                    else:
                        signal_summary['neutral_signals'].append(sector_name)
                    
                except Exception as e:
                    print(f"❌ {sector_name} 分析失败: {e}")
                    continue
            
            # 按照信号强弱对板块进行排序
            sorted_sector_results = self._sort_sectors_by_signal_strength(sector_results)
            
            # 打印分析结果摘要
            print(f"\n📊 板块MACD分析完成！")
            print(f"📈 买入信号板块 ({len(signal_summary['buy_signals'])}个): {', '.join(signal_summary['buy_signals'][:5])}{'...' if len(signal_summary['buy_signals']) > 5 else ''}")
            print(f"📉 卖出信号板块 ({len(signal_summary['sell_signals'])}个): {', '.join(signal_summary['sell_signals'][:5])}{'...' if len(signal_summary['sell_signals']) > 5 else ''}")
            print(f"➡️ 中性信号板块 ({len(signal_summary['neutral_signals'])}个): {', '.join(signal_summary['neutral_signals'][:5])}{'...' if len(signal_summary['neutral_signals']) > 5 else ''}")
            
            print(f"\n📁 MACD图表保存路径:")
            for sector_name, chart_path in list(chart_paths.items())[:5]:
                print(f"  - {sector_name}: {chart_path}")
            if len(chart_paths) > 5:
                print(f"  ... 共{len(chart_paths)}个图表")
            
            return {
                'status': 'success',
                'analysis_date': date,
                'total_sectors': len(INDUSTRY_SECTORS),
                'analyzed_sectors': len(sector_results),
                'sector_results': sorted_sector_results,
                'chart_paths': chart_paths,
                'signal_summary': signal_summary,
                'macd_charts_dir': macd_charts_dir
            }
            
        except Exception as e:
            print(f"❌ 板块表现分析失败: {e}")
            import traceback
            traceback.print_exc()
            return {
                'status': 'failed',
                'error': str(e),
                'analysis_date': date
            }
    
    def _sort_sectors_by_signal_strength(self, sector_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        按照信号强弱对板块进行排序
        
        Args:
            sector_results: 原始板块分析结果
            
        Returns:
            Dict[str, Any]: 按信号强弱排序的板块结果
        """
        try:
            # 计算信号强度分数
            signal_scores = {}
            for sector_name, result in sector_results.items():
                macd_value = result.get('latest_macd', 0)
                histogram_value = result.get('latest_histogram', 0)
                signal_type = result.get('current_signal_type', 'NEUTRAL')
                
                # 计算综合信号强度分数
                # MACD值越大表示趋势越强，柱状图值表示动量
                base_score = abs(macd_value) + abs(histogram_value)
                
                # 根据信号类型调整分数
                if signal_type == 'BUY':
                    signal_score = base_score  # 买入信号为正分
                elif signal_type == 'SELL':
                    signal_score = -base_score  # 卖出信号为负分
                else:
                    # 中性信号也根据MACD和柱状图强度计算分数
                    # 如果MACD为正且柱状图为正，给予正分；否则给予负分
                    if macd_value > 0 and histogram_value > 0:
                        signal_score = base_score * 0.5  # 中性偏多
                    elif macd_value < 0 and histogram_value < 0:
                        signal_score = -base_score * 0.5  # 中性偏空
                    else:
                        signal_score = base_score * 0.1  # 中性
                
                signal_scores[sector_name] = {
                    'score': signal_score,
                    'macd': macd_value,
                    'histogram': histogram_value,
                    'signal_type': signal_type,
                    'result': result
                }
            
            # 按信号强度降序排序
            sorted_sectors = sorted(signal_scores.items(), 
                                  key=lambda x: x[1]['score'], 
                                  reverse=True)
            
            # 重新组织结果
            sorted_results = {
                'buy_signals': [],
                'sell_signals': [],
                'neutral_signals': [],
                'all_sectors': {}
            }
            
            for sector_name, score_data in sorted_sectors:
                signal_type = score_data['signal_type']
                result = score_data['result']
                
                # 添加信号强度信息
                result['signal_strength'] = score_data['score']
                result['signal_score'] = {
                    'macd': score_data['macd'],
                    'histogram': score_data['histogram'],
                    'strength': score_data['score']
                }
                
                # 按信号类型分类
                if signal_type == 'BUY':
                    sorted_results['buy_signals'].append({
                        'sector_name': sector_name,
                        'signal_strength': score_data['score'],
                        'macd': score_data['macd'],
                        'histogram': score_data['histogram'],
                        'result': result
                    })
                elif signal_type == 'SELL':
                    sorted_results['sell_signals'].append({
                        'sector_name': sector_name,
                        'signal_strength': score_data['score'],
                        'macd': score_data['macd'],
                        'histogram': score_data['histogram'],
                        'result': result
                    })
                else:
                    sorted_results['neutral_signals'].append({
                        'sector_name': sector_name,
                        'signal_strength': score_data['score'],
                        'macd': score_data['macd'],
                        'histogram': score_data['histogram'],
                        'result': result
                    })
                
                # 保存到all_sectors中
                sorted_results['all_sectors'][sector_name] = result
            
            return sorted_results
            
        except Exception as e:
            print(f"❌ 板块信号排序失败: {e}")
            # 如果排序失败，返回原始结果
            return {
                'buy_signals': [],
                'sell_signals': [],
                'neutral_signals': [],
                'all_sectors': sector_results
            }
    
    def _generate_macd_chart(self, macd_data: pd.DataFrame, sector_name: str, 
                           date: str, output_path: str) -> Optional[str]:
        """
        生成MACD趋势图
        
        Args:
            macd_data: MACD数据DataFrame
            sector_name: 板块名称
            date: 分析日期
            output_path: 输出文件路径
            
        Returns:
            Optional[str]: 生成的图表文件路径
        """
        try:
            import matplotlib.pyplot as plt
            import matplotlib.dates as mdates
            from datetime import datetime
            
            # 设置中文字体
            plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans', 'Arial']
            plt.rcParams['axes.unicode_minus'] = False
            
            # 创建图表
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10), height_ratios=[3, 1])
            
            # 确保有日期列
            if '日期' in macd_data.columns:
                dates = pd.to_datetime(macd_data['日期'])
            elif 'date' in macd_data.columns:
                dates = pd.to_datetime(macd_data['date'])
            else:
                dates = macd_data.index
            
            # 获取收盘价列
            close_col = None
            for col in ['收盘', '收盘价', 'close', 'Close']:
                if col in macd_data.columns:
                    close_col = col
                    break
            
            if close_col is None:
                print(f"❌ {sector_name} 未找到收盘价列")
                return None
            
            # 上图：价格和MACD线
            ax1.plot(dates, macd_data[close_col], label='收盘价', linewidth=2, color='#1f77b4')
            ax1.plot(dates, macd_data['EMA_Fast'], label='EMA12', linewidth=1, color='#ff7f0e', alpha=0.7)
            ax1.plot(dates, macd_data['EMA_Slow'], label='EMA26', linewidth=1, color='#2ca02c', alpha=0.7)
            
            ax1.set_title(f'{sector_name} MACD分析图 - {date}', fontsize=16, fontweight='bold')
            ax1.set_ylabel('价格', fontsize=12)
            ax1.legend(loc='upper left')
            ax1.grid(True, alpha=0.3)
            
            # 下图：MACD指标
            ax2.plot(dates, macd_data['MACD'], label='MACD', linewidth=2, color='#d62728')
            ax2.plot(dates, macd_data['Signal'], label='Signal', linewidth=2, color='#9467bd')
            ax2.bar(dates, macd_data['Histogram'], label='Histogram', alpha=0.6, color='#17becf')
            ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
            
            ax2.set_xlabel('日期', fontsize=12)
            ax2.set_ylabel('MACD', fontsize=12)
            ax2.legend(loc='upper left')
            ax2.grid(True, alpha=0.3)
            
            # 设置日期格式
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            
            # 旋转日期标签
            plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
            plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
            
            # 调整布局
            plt.tight_layout()
            
            # 保存图表
            plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            return output_path
            
        except Exception as e:
            print(f"❌ 生成 {sector_name} MACD图表失败: {e}")
            return None
    
    def _analyze_stock_performance(self, date: str, sector_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析个股表现
        
        Args:
            date: 分析日期
            sector_analysis: 板块分析结果
            
        Returns:
            Dict[str, Any]: 个股分析结果
        """
        try:
            print(f"🔍 开始个股分析...")
            
            # 1. 从板块分析结果中提取有买入信号和中性信号的TOP10板块
            target_sectors = self._extract_top_sectors(sector_analysis, top_n=10)
            
            if not target_sectors:
                print("⚠️ 未找到符合条件的板块")
                return {
                    'status': 'no_data',
                    'message': '未找到符合条件的板块',
                    'analysis_date': date
                }
            
            print(f"📊 已选择 {len(target_sectors)} 个目标板块进行分析")
            
            # 2. 获取待分析的股票列表
            stock_list = self._get_stocks_from_sectors(target_sectors)
            
            if not stock_list:
                print("⚠️ 未找到待分析的股票")
                return {
                    'status': 'no_data',
                    'message': '未找到待分析的股票',
                    'analysis_date': date
                }
            
            print(f"📈 找到 {len(stock_list)} 只待分析股票")

            # 3. 批量查询股票近90天的日频行情数据
            print(f"\n📊 第二步：批量查询股票近90天的日频行情数据...")
            stock_data_dict = self._batch_query_stock_data(stock_list, date)
            
            if not stock_data_dict:
                print("⚠️ 未获取到股票行情数据")
                return {
                    'status': 'no_data',
                    'message': '未获取到股票行情数据',
                    'analysis_date': date
                }
            
            print(f"✅ 成功获取 {len(stock_data_dict)} 只股票的行情数据")

            # 4. 使用IndividualTrendTrackingStrategy分析股票
            print(f"\n📊 第三步：使用趋势追踪策略分析...")
            trend_results = self._analyze_stocks_with_trend_tracking(stock_list, date, stock_data_dict)

            # 5. 使用IndividualOversoldReboundStrategy分析股票
            print(f"\n📊 第四步：使用超跌反弹策略分析...")
            oversold_results = self._analyze_stocks_with_oversold_rebound(stock_list, date, stock_data_dict)

            # 6. 合并两种策略的分析结果
            print(f"\n📊 第五步：合并分析结果...")
            merged_results = self._merge_strategy_results(trend_results, oversold_results, target_sectors)

            return merged_results
            
        except Exception as e:
            print(f"❌ 个股分析失败: {e}")
            import traceback
            traceback.print_exc()
            return {
                'status': 'failed',
                'error': str(e),
                'analysis_date': date
            }
    
    def _batch_query_stock_data(self, stock_list: List[Dict[str, str]], date: str) -> Dict[str, pd.DataFrame]:
        """
        批量查询股票近90天的日频行情数据
        
        Args:
            stock_list: 股票列表，格式为 [{'name': '股票名', 'sector': '板块名'}, ...]
            date: 分析日期
            
        Returns:
            Dict[str, pd.DataFrame]: 股票代码到历史数据的映射
        """
        try:
            from ...repositories.stock.stock_query import StockQuery
            from datetime import datetime, timedelta
            
            stock_query = StockQuery()
            start_date = (datetime.strptime(date, '%Y%m%d') - timedelta(days=120)).strftime('%Y%m%d')
            
            stock_data_dict = {}
            
            for i, stock_info in enumerate(stock_list, 1):
                stock_name = stock_info['name']
                try:
                    # 查询股票代码
                    stock_code = stock_query.search_stock_by_name(stock_name)
                    if not stock_code:
                        print(f"⚠️ 未找到股票代码: {stock_name}")
                        continue
                    
                    # 查询历史数据
                    hist_data = stock_query.get_historical_quotes(stock_code, start_date, date)
                    
                    if hist_data is not None and not hist_data.empty:
                        stock_data_dict[stock_code] = hist_data
                        print(f"✅ [{i}/{len(stock_list)}] 已获取 {stock_name} ({stock_code}) 的历史数据")
                    else:
                        print(f"⚠️ 未获取到 {stock_name} ({stock_code}) 的历史数据")
                    
                except Exception as e:
                    print(f"❌ 获取 {stock_name} 数据失败: {e}")
                    continue
            
            return stock_data_dict
            
        except Exception as e:
            print(f"❌ 批量查询股票数据失败: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def _analyze_stocks_with_trend_tracking(self, stock_list, date, stock_data_dict: Dict[str, pd.DataFrame]):
        """
        使用趋势追踪策略分析股票
        
        Args:
            stock_list: 股票列表
            date: 分析日期
            stock_data_dict: 股票数据字典，格式为 {股票代码: DataFrame}
        
        Returns:
            Dict: 趋势追踪分析结果
        """
        try:
            from ...strategies.individual_stock.trend_tracking_strategy import IndividualTrendTrackingStrategy
            from datetime import datetime, timedelta
            
            trend_strategy = IndividualTrendTrackingStrategy()
            stock_query = trend_strategy.stock_query
            
            stock_results = []
            
            for i, stock_info in enumerate(stock_list, 1):
                stock_name = stock_info['name']
                try:
                    print(f"📊 [趋势追踪] 正在分析股票 {i}/{len(stock_list)}: {stock_name}")
                    
                    stock_code = stock_query.search_stock_by_name(stock_name)
                    if not stock_code:
                        continue
                    
                    # 从stock_data_dict中获取数据
                    hist_data = stock_data_dict.get(stock_code)
                    if hist_data is None or hist_data.empty:
                        print(f"⚠️ {stock_name} ({stock_code}) 没有行情数据，跳过")
                        continue
                    
                    # 使用传入的数据进行分析
                    analysis_result = trend_strategy.analyze_stock_trend_with_data(hist_data, stock_code)
                    
                    if analysis_result:
                        signal_strength = self._calculate_buy_signal_strength(analysis_result)
                        analysis_result['stock_name'] = stock_name
                        analysis_result['stock_code'] = stock_code
                        analysis_result['signal_strength'] = signal_strength
                        stock_results.append(analysis_result)
                        print(f"✅ [趋势追踪] {stock_name} ({stock_code}) 分析完成，信号强度: {signal_strength:.2f}")
                    
                except Exception as e:
                    print(f"❌ [趋势追踪] {stock_name} 分析失败: {e}")
                    continue
            
            stock_results.sort(key=lambda x: x['signal_strength'], reverse=True)
            top_10 = stock_results[:10]
            
            print(f"✅ [趋势追踪] 分析完成！共分析 {len(stock_results)} 只股票，选出TOP10")
            
            return {
                'status': 'success',
                'total_analyzed': len(stock_results),
                'top_10': top_10,
                'all_results': stock_results
            }
            
        except Exception as e:
            print(f"❌ 趋势追踪策略分析失败: {e}")
            import traceback
            traceback.print_exc()
            return {'status': 'failed', 'error': str(e)}
    
    def _analyze_stocks_with_oversold_rebound(self, stock_list, date, stock_data_dict: Dict[str, pd.DataFrame]):
        """
        使用超跌反弹策略分析股票
        
        Args:
            stock_list: 股票列表
            date: 分析日期
            stock_data_dict: 股票数据字典，格式为 {股票代码: DataFrame}
        
        Returns:
            Dict: 超跌反弹分析结果
        """
        try:
            from ...strategies.individual_stock.oversold_rebound_strategy import IndividualOversoldReboundStrategy
            from datetime import datetime, timedelta
            
            oversold_strategy = IndividualOversoldReboundStrategy()
            stock_query = oversold_strategy.stock_query
            
            stock_results = []
            
            for i, stock_info in enumerate(stock_list, 1):
                stock_name = stock_info['name']
                try:
                    print(f"📊 [超跌反弹] 正在分析股票 {i}/{len(stock_list)}: {stock_name}")
                    
                    stock_code = stock_query.search_stock_by_name(stock_name)
                    if not stock_code:
                        continue
                    
                    # 从stock_data_dict中获取数据
                    hist_data = stock_data_dict.get(stock_code)
                    if hist_data is None or hist_data.empty:
                        print(f"⚠️ {stock_name} ({stock_code}) 没有行情数据，跳过")
                        continue
                    
                    # 使用传入的数据进行分析
                    analysis_result = oversold_strategy.analyze_stock_oversold_with_data(hist_data, stock_code)
                    
                    if analysis_result:
                        signal_strength = self._calculate_oversold_signal_strength(analysis_result)
                        analysis_result['stock_name'] = stock_name
                        analysis_result['stock_code'] = stock_code
                        analysis_result['signal_strength'] = signal_strength
                        stock_results.append(analysis_result)
                        print(f"✅ [超跌反弹] {stock_name} ({stock_code}) 分析完成，信号强度: {signal_strength:.2f}")
                    
                except Exception as e:
                    print(f"❌ [超跌反弹] {stock_name} 分析失败: {e}")
                    continue
            
            stock_results.sort(key=lambda x: x['signal_strength'], reverse=True)
            top_10 = stock_results[:10]
            
            print(f"✅ [超跌反弹] 分析完成！共分析 {len(stock_results)} 只股票，选出TOP10")
            
            return {
                'status': 'success',
                'total_analyzed': len(stock_results),
                'top_10': top_10,
                'all_results': stock_results
            }
            
        except Exception as e:
            print(f"❌ 超跌反弹策略分析失败: {e}")
            import traceback
            traceback.print_exc()
            return {'status': 'failed', 'error': str(e)}
    
    def _merge_strategy_results(self, trend_results, oversold_results, target_sectors):
        """
        合并两种策略的分析结果
        
        Returns:
            Dict: 合并后的结果
        """
        return {
            'status': 'success',
            'target_sectors': target_sectors,
            'trend_tracking': trend_results,
            'oversold_rebound': oversold_results,
            'summary': {
                'trend_total': trend_results.get('total_analyzed', 0),
                'oversold_total': oversold_results.get('total_analyzed', 0),
                'trend_top_10': len(trend_results.get('top_10', [])),
                'oversold_top_10': len(oversold_results.get('top_10', []))
            }
        }
    
    def _calculate_oversold_signal_strength(self, analysis_result):
        """
        计算超跌反弹信号强度
        
        Returns:
            float: 超跌反弹信号强度（0-100）
        """
        try:
            base_score = 0
            
            # 1. 根据信号类型给分
            signal_type = analysis_result.get('current_signal_type', 'HOLD')
            if signal_type == 'STRONG_BUY':
                base_score += 50
            elif signal_type == 'BUY':
                base_score += 30
            elif signal_type == 'HOLD':
                base_score += 10
            
            # 2. 根据超跌强度给分
            oversold_strength = analysis_result.get('oversold_strength', 0)
            base_score += oversold_strength * 20
            
            # 3. 根据KDJ超卖给分
            if analysis_result.get('kdj_oversold', False):
                base_score += 15
            
            # 4. 根据RSI超卖给分
            if analysis_result.get('rsi_oversold', False):
                base_score += 15
            
            return min(max(base_score, 0), 100)
            
        except Exception as e:
            print(f"❌ 计算超跌反弹信号强度失败: {e}")
            return 0

    
    def _extract_top_sectors(self, sector_analysis: Dict[str, Any], top_n: int = 10) -> List[str]:
        """
        从板块分析结果中提取有买入信号和中性信号的板块
        
        Args:
            sector_analysis: 板块分析结果
            top_n: 中性信号板块的提取数量（买入信号板块全部返回）
            
        Returns:
            List[str]: 板块名称列表（所有买入信号板块 + TOP N中性信号板块）
        """
        try:
            # 检查分析是否成功
            if sector_analysis.get('status') != 'success':
                print("⚠️ 板块分析未成功，无法提取板块")
                return []
            
            # 获取板块分析结果
            sector_results = sector_analysis.get('sector_results', {})
            
            if not sector_results:
                print("⚠️ 未找到板块分析结果")
                return []
            
            # 筛选有买入信号和中性信号的板块
            buy_sectors = []
            neutral_sectors = []
            
            for sector_name, sector_data in sector_results.items():
                # 检查量价信号
                vp_signal = sector_data.get('vp_signal_type', 'UNKNOWN')
                # 检查MACD信号
                macd_signal = sector_data.get('macd_signal_type', 'NEUTRAL')
                # 获取综合信号强度
                combined_strength = sector_data.get('combined_signal_strength', 0)
                
                # 买入信号：BUY 或 STRONG_BUY
                if vp_signal in ['BUY', 'STRONG_BUY'] or macd_signal == 'BUY':
                    buy_sectors.append({
                        'name': sector_name,
                        'strength': combined_strength,
                        'vp_signal': vp_signal,
                        'macd_signal': macd_signal
                    })
                # 中性信号
                elif vp_signal in ['NEUTRAL', 'HOLD'] and macd_signal == 'NEUTRAL':
                    neutral_sectors.append({
                        'name': sector_name,
                        'strength': abs(combined_strength)
                    })
            
            # 按信号强度排序
            buy_sectors.sort(key=lambda x: x['strength'], reverse=True)
            neutral_sectors.sort(key=lambda x: x['strength'], reverse=True)
            
            # 构建最终选择板块列表
            selected_sectors = []
            
            # 返回所有买入信号板块
            selected_sectors.extend([s['name'] for s in buy_sectors])
            
            # 返回TOP10信号强度的中性板块
            neutral_count = min(top_n, len(neutral_sectors))
            selected_sectors.extend([s['name'] for s in neutral_sectors[:neutral_count]])
            
            print(f"📊 选中板块详情:")
            print(f"  - 买入信号板块: {len(buy_sectors)}个")
            print(f"  - 中性信号板块(TOP{top_n}): {neutral_count}个")
            print(f"  - 选中板块: {', '.join(selected_sectors[:5])}{'...' if len(selected_sectors) > 5 else ''}")
            
            return selected_sectors
            
        except Exception as e:
            print(f"❌ 提取板块失败: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _get_stocks_from_sectors(self, sectors: List[str]) -> List[Dict[str, str]]:
        """
        从板块列表中获取股票列表
        
        Args:
            sectors: 板块名称列表
            
        Returns:
            List[Dict]: 股票信息列表，格式为 [{'name': '股票名', 'sector': '板块名'}, ...]
        """
        try:
            from ...static.industry_sectors import get_stocks_by_sector
            
            stock_list = []
            stock_set = set()  # 用于去重
            
            for sector in sectors:
                stocks = get_stocks_by_sector(sector)
                if not stocks:
                    print(f"⚠️ 板块 {sector} 未找到股票列表")
                    continue
                
                for stock_name in stocks:
                    # 使用股票名作为唯一标识
                    if stock_name not in stock_set:
                        stock_list.append({
                            'name': stock_name,
                            'sector': sector
                        })
                        stock_set.add(stock_name)
            
            print(f"📈 从 {len(sectors)} 个板块中获取到 {len(stock_list)} 只股票")
            
            return stock_list
            
        except Exception as e:
            print(f"❌ 获取股票列表失败: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _calculate_buy_signal_strength(self, analysis_result: Dict[str, Any]) -> float:
        """
        计算买入信号强度
        
        Args:
            analysis_result: 个股分析结果
            
        Returns:
            float: 买入信号强度（0-100）
        """
        try:
            # 基础分数
            base_score = 0
            
            # 1. 根据信号类型给分
            signal_type = analysis_result.get('current_signal_type', 'HOLD')
            if signal_type == 'STRONG_BUY':
                base_score += 50
            elif signal_type == 'BUY':
                base_score += 30
            elif signal_type == 'HOLD':
                base_score += 10
            
            # 2. 根据趋势强度给分（趋势强度在0-1之间）
            trend_strength = analysis_result.get('trend_strength', 0)
            base_score += trend_strength * 20
            
            # 3. 根据均线多头排列给分
            if analysis_result.get('ma_alignment', False):
                base_score += 15
            
            # 4. 根据MACD多头市场给分
            if analysis_result.get('macd_bullish', False):
                base_score += 15
            
            # 限制在0-100之间
            return min(max(base_score, 0), 100)
            
        except Exception as e:
            print(f"❌ 计算买入信号强度失败: {e}")
            return 0
    
    def _generate_review_report(self, date: str, market_summary: Dict[str, Any], 
                              sector_analysis: Dict[str, Any], 
                              stock_analysis: Dict[str, Any]) -> Optional[str]:
        """
        生成市场复盘报告
        
        Args:
            date: 复盘日期
            market_summary: 市场总结数据
            sector_analysis: 板块分析数据
            stock_analysis: 个股分析数据
            
        Returns:
            Optional[str]: 生成的报告文件路径
        """
        try:
            # 生成报告文件名
            filename = f"市场复盘报告_{date}.md"
            report_path = os.path.join(self.reports_dir, filename)
            
            # 生成报告内容
            report_content = self.report_generator.generate_market_review_content(
                date, market_summary, sector_analysis, stock_analysis
            )
            
            # 写入文件
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            return report_path
            
        except Exception as e:
            print(f"❌ 生成复盘报告失败: {e}")
            return None
    
    def _combine_sector_analysis_results(self, volume_price_analysis: Dict[str, Any], 
                                       macd_analysis: Dict[str, Any], date: str) -> Dict[str, Any]:
        """
        合并量价分析和MACD分析结果
        
        Args:
            volume_price_analysis: 量价分析结果
            macd_analysis: MACD分析结果
            date: 分析日期
            
        Returns:
            Dict[str, Any]: 合并后的分析结果
        """
        try:
            from ...static.industry_sectors import INDUSTRY_SECTORS
            
            # 检查两个分析是否成功
            vp_status = volume_price_analysis.get('status')
            macd_status = macd_analysis.get('status')
            
            if vp_status == 'failed' and macd_status == 'failed':
                return {
                    'status': 'failed',
                    'error': '量价分析和MACD分析均失败',
                    'analysis_date': date
                }
            
            # 合并板块结果
            combined_sector_results = {}
            
            # 从MACD分析获取板块列表和结果
            macd_results = macd_analysis.get('sector_results', {})
            macd_signals = macd_results.get('all_sectors', {})
            
            # 从量价分析获取板块结果
            vp_results = volume_price_analysis.get('sector_results', {})
            
            # 合并每个板块的分析结果
            for sector_name in INDUSTRY_SECTORS:
                macd_data = macd_signals.get(sector_name, {})
                vp_data = vp_results.get(sector_name, {})
                
                # 合并数据
                combined_sector_results[sector_name] = {
                    # MACD分析结果
                    'macd_value': macd_data.get('latest_macd', 0),
                    'macd_signal': macd_data.get('latest_signal', 0),
                    'macd_histogram': macd_data.get('latest_histogram', 0),
                    'macd_signal_type': macd_data.get('current_signal_type', 'NEUTRAL'),
                    'macd_zero_cross': macd_data.get('zero_cross_status', 'NONE'),
                    'macd_chart_path': macd_data.get('chart_path'),
                    'macd_signal_strength': macd_data.get('signal_strength', 0),
                    
                    # 量价分析结果
                    'vp_price': vp_data.get('latest_price', 0),
                    'vp_volume': vp_data.get('latest_volume', 0),
                    'vp_price_change': vp_data.get('price_change_pct', 0),
                    'vp_volume_change': vp_data.get('volume_change_pct', 0),
                    'vp_relationship': vp_data.get('latest_relationship', '未知'),
                    'vp_signal_type': vp_data.get('signal_type', 'UNKNOWN'),
                    'vp_signal_strength': vp_data.get('signal_strength', 0),
                    'vp_comprehensive_score': vp_data.get('comprehensive_score', 0),
                    'vp_strength_level': vp_data.get('strength_level', '未知'),
                    'vp_chart_path': vp_data.get('chart_path'),
                    
                    # 综合分析
                    'combined_signal_strength': (
                        macd_data.get('signal_strength', 0) + 
                        vp_data.get('signal_strength', 0)
                    ) / 2 if (macd_data.get('signal_strength') and vp_data.get('signal_strength')) else 0,
                    'analysis_date': date
                }
            
            # 合并图表路径
            macd_charts = macd_analysis.get('chart_paths', {})
            vp_charts = volume_price_analysis.get('chart_paths', {})
            
            # 合并信号摘要
            macd_signals = macd_analysis.get('signal_summary', {})
            vp_signals = volume_price_analysis.get('signal_summary', {})
            
            # 返回合并结果
            return {
                'status': 'success',
                'analysis_date': date,
                'total_sectors': len(INDUSTRY_SECTORS),
                'analyzed_sectors': len(combined_sector_results),
                'sector_results': combined_sector_results,
                'macd_charts': macd_charts,
                'vp_charts': vp_charts,
                'macd_signal_summary': macd_signals,
                'vp_signal_summary': vp_signals,
                'macd_analysis': macd_analysis,
                'volume_price_analysis': volume_price_analysis
            }
            
        except Exception as e:
            print(f"❌ 合并板块分析结果失败: {e}")
            import traceback
            traceback.print_exc()
            return {
                'status': 'failed',
                'error': str(e),
                'analysis_date': date
            }
    
    def print_review_summary(self, review_result: Dict[str, Any]) -> None:
        """
        打印复盘结果摘要
        
        Args:
            review_result: 复盘分析结果
        """
        try:
            print("\n" + "="*60)
            print("📋 市场复盘结果摘要")
            print("="*60)
            
            review_date = review_result.get('review_date', '未知')
            status = review_result.get('status', '未知')
            
            print(f"📅 复盘日期: {review_date}")
            print(f"📊 分析状态: {status}")
            
            if status == 'success':
                market_summary = review_result.get('market_summary', {})
                if 'error' not in market_summary:
                    overall_sentiment = market_summary.get('overall_sentiment', 0)
                    sentiment_level = market_summary.get('sentiment_level', '未知')
                    print(f"📈 综合情绪指数: {overall_sentiment:.2f}")
                    print(f"🎯 情绪等级: {sentiment_level}")
                
                report_path = review_result.get('report_path')
                if report_path:
                    print(f"📄 报告路径: {report_path}")
            else:
                error = review_result.get('error', '未知错误')
                print(f"❌ 分析失败: {error}")
            
            print("="*60)
            
        except Exception as e:
            print(f"❌ 打印复盘摘要失败: {e}")
