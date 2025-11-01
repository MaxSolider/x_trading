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
            from concurrent.futures import ThreadPoolExecutor, as_completed
            
            print(f"🔍 开始综合分析 {len(INDUSTRY_SECTORS)} 个板块的表现...")
            
            # 0. 先批量获取所有板块近120天历史数据
            print(f"\n📦 第零步：批量获取所有板块近120天历史数据...")
            industry_query = IndustryInfoQuery()
            start_date = (datetime.strptime(date, '%Y%m%d') - timedelta(days=120)).strftime('%Y%m%d')
            
            # 批量查询所有板块历史数据
            sector_data_dict = {}
            try:
                print(f"📊 正在批量获取 {len(INDUSTRY_SECTORS)} 个板块的历史数据...")
                df_all = industry_query.get_board_industry_hist(INDUSTRY_SECTORS, start_date, date)
                
                if df_all is not None and not df_all.empty:
                    # 批量查询返回的数据包含 industry 列，按 industry 分组
                    if 'industry' in df_all.columns:
                        for sector_name in INDUSTRY_SECTORS:
                            df_sector = df_all[df_all['industry'] == sector_name].copy()
                            if not df_sector.empty:
                                # 移除 industry 列
                                df_sector = df_sector.drop(columns=['industry'], errors='ignore')
                                sector_data_dict[sector_name] = df_sector
                        
                        print(f"✅ 成功批量获取 {len(sector_data_dict)}/{len(INDUSTRY_SECTORS)} 个板块的历史数据")
                    else:
                        print(f"⚠️ 批量查询返回数据格式异常，未包含 industry 列")
                else:
                    print(f"⚠️ 批量查询返回数据为空")
            except Exception as e:
                print(f"⚠️ 批量查询失败: {e}，降级为逐个查询")
                # 如果批量查询失败，降级为逐个查询
                for i, sector_name in enumerate(INDUSTRY_SECTORS, 1):
                    try:
                        print(f"📊 正在获取板块 {i}/{len(INDUSTRY_SECTORS)}: {sector_name}")
                        hist_data = industry_query.get_board_industry_hist(sector_name, start_date, date)
                        if hist_data is not None and not hist_data.empty:
                            sector_data_dict[sector_name] = hist_data
                            print(f"✅ {sector_name} 历史数据获取成功")
                        else:
                            print(f"⚠️ {sector_name} 历史数据获取失败")
                    except Exception as ex:
                        print(f"❌ {sector_name} 历史数据获取失败: {ex}")
                        continue
            
            print(f"✅ 成功获取 {len(sector_data_dict)}/{len(INDUSTRY_SECTORS)} 个板块的历史数据")
            
            # 1. 并行执行量价分析和MACD分析
            print(f"\n📊 第一步：并行执行量价分析和MACD分析...")
            with ThreadPoolExecutor(max_workers=2) as executor:
                # 提交两个分析任务
                vp_future = executor.submit(self._analyze_sector_volume_price_performance, date, sector_data_dict)
                macd_future = executor.submit(self._analyze_sector_macd_performance, date, sector_data_dict)
                
                # 等待两个任务完成
                volume_price_analysis = vp_future.result()
                macd_analysis = macd_future.result()
            
            # 2. 合并分析结果
            print(f"\n🔄 第二步：合并分析结果...")
            combined_results = self._combine_sector_analysis_results(
                volume_price_analysis, macd_analysis, date
            )
            
            # 3. 统一生成有买入信号板块的综合图片
            print(f"\n📸 第三步：统一生成有买入信号板块的综合图片...")
            combined_results = self._generate_sector_combined_charts(
                combined_results, sector_data_dict, date
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
                    
                    # 存储分析结果（不生成图片，后续统一生成）
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
            
            print(f"🔍 开始分析 {len(INDUSTRY_SECTORS)} 个板块的MACD表现...")
            
            # 初始化策略
            macd_strategy = IndustryMACDStrategy()
            
            # 存储所有板块的分析结果
            sector_results = {}
            macd_data_dict = {}  # 存储MACD计算数据，用于后续生成图片
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
                    
                    # 计算MACD数据（存储用于后续生成图片）
                    macd_data = macd_strategy.calculate_macd(hist_data)
                    if macd_data is None:
                        print(f"⚠️ {sector_name} MACD计算失败，跳过")
                        continue
                    
                    # 存储分析结果（不生成图片，后续统一生成）
                    sector_results[sector_name] = {
                        'latest_macd': macd_result['latest_macd'],
                        'latest_signal': macd_result['latest_signal'],
                        'latest_histogram': macd_result['latest_histogram'],
                        'current_signal_type': macd_result['current_signal_type'],
                        'zero_cross_status': macd_result['zero_cross_status'],
                        'analysis_date': macd_result['analysis_date']
                    }
                    # 保存MACD数据用于后续生成图片
                    macd_data_dict[sector_name] = macd_data
                    
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
            
            return {
                'status': 'success',
                'analysis_date': date,
                'total_sectors': len(INDUSTRY_SECTORS),
                'analyzed_sectors': len(sector_results),
                'sector_results': sorted_sector_results,
                'signal_summary': signal_summary,
                'macd_data_dict': macd_data_dict  # 保存MACD数据用于后续生成图片
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
    
    def _generate_sector_combined_charts(self, combined_results: Dict[str, Any], 
                                         sector_data_dict: Dict[str, pd.DataFrame], 
                                         date: str) -> Dict[str, Any]:
        """
        统一生成有买入信号板块的综合图片（量价+MACD在同一张图中）
        
        Args:
            combined_results: 合并后的板块分析结果
            sector_data_dict: 板块原始数据字典
            date: 分析日期
            
        Returns:
            Dict[str, Any]: 更新后的合并结果，包含生成的图片路径
        """
        try:
            from ...strategies.industry_sector.macd_strategy import IndustryMACDStrategy
            from ...strategies.industry_sector.volume_price_strategy import VolumePriceStrategy
            import matplotlib.pyplot as plt
            import matplotlib.dates as mdates
            
            # 创建图片保存目录
            charts_dir = "reports/images/sectors"
            os.makedirs(charts_dir, exist_ok=True)
            
            # 获取有买入信号的板块（取两个策略的并集）
            sector_results = combined_results.get('sector_results', {})
            macd_data_dict = combined_results.get('macd_data_dict', {})
            
            buy_sectors = set()
            
            # 从量价分析中获取买入信号板块
            vp_signal_summary = combined_results.get('vp_signal_summary', {})
            buy_sectors.update(vp_signal_summary.get('BUY', []))
            
            # 从MACD分析中获取买入信号板块
            macd_signal_summary = combined_results.get('macd_signal_summary', {})
            buy_sectors.update(macd_signal_summary.get('buy_signals', []))
            
            print(f"📸 找到 {len(buy_sectors)} 个有买入信号的板块，开始生成综合图片...")
            
            chart_paths = {}
            volume_price_strategy = VolumePriceStrategy()
            
            for i, sector_name in enumerate(buy_sectors, 1):
                try:
                    print(f"📊 正在生成板块 {i}/{len(buy_sectors)}: {sector_name}")
                    
                    # 获取板块数据
                    hist_data = sector_data_dict.get(sector_name)
                    if hist_data is None or hist_data.empty:
                        print(f"⚠️ {sector_name} 没有历史数据，跳过")
                        continue
                    
                    # 获取MACD数据
                    macd_data = macd_data_dict.get(sector_name)
                    if macd_data is None or macd_data.empty:
                        print(f"⚠️ {sector_name} 没有MACD数据，跳过")
                        continue
                    
                    # 生成综合图片
                    chart_path = self._create_combined_sector_chart(
                        sector_name, hist_data, macd_data, date, charts_dir, volume_price_strategy
                    )
                    
                    if chart_path:
                        chart_paths[sector_name] = chart_path
                        print(f"✅ {sector_name} 综合图表已生成: {chart_path}")
                    else:
                        print(f"⚠️ {sector_name} 综合图表生成失败")
                    
                except Exception as e:
                    print(f"❌ {sector_name} 综合图表生成失败: {e}")
                    continue
            
            # 更新合并结果，添加图片路径
            combined_results['combined_chart_paths'] = chart_paths
            
            print(f"✅ 成功生成 {len(chart_paths)}/{len(buy_sectors)} 个板块的综合图片")
            
            return combined_results
            
        except Exception as e:
            print(f"❌ 生成板块综合图片失败: {e}")
            import traceback
            traceback.print_exc()
            return combined_results
    
    def _create_combined_sector_chart(self, sector_name: str, hist_data: pd.DataFrame, 
                                      macd_data: pd.DataFrame, date: str, 
                                      output_dir: str, volume_price_strategy) -> Optional[str]:
        """
        创建板块综合图表（量价+MACD）
        
        Args:
            sector_name: 板块名称
            hist_data: 历史数据
            macd_data: MACD数据
            date: 分析日期
            output_dir: 输出目录
            volume_price_strategy: 量价策略实例
            
        Returns:
            Optional[str]: 生成的图表文件路径
        """
        try:
            import matplotlib.pyplot as plt
            import matplotlib.dates as mdates
            
            # 设置中文字体
            plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans', 'Arial']
            plt.rcParams['axes.unicode_minus'] = False
            
            # 创建四子图布局：价格+量价图，MACD图
            fig, axes = plt.subplots(2, 2, figsize=(18, 12))
            fig.suptitle(f'{sector_name} 综合分析图 - {date}', fontsize=16, fontweight='bold', y=0.995)
            
            # 检测日期列名
            date_col = None
            for col in ['日期', 'date', 'Date']:
                if col in hist_data.columns:
                    date_col = col
                    break
            
            if date_col is None:
                print(f"❌ {sector_name} 未找到日期列")
                return None
            
            # 确保数据按日期排序
            hist_data = hist_data.sort_values(date_col).reset_index(drop=True)
            dates = pd.to_datetime(hist_data[date_col])
            
            # 获取收盘价列
            close_col = None
            for col in ['收盘', '收盘价', 'close', 'Close']:
                if col in hist_data.columns:
                    close_col = col
                    break
            
            # 获取成交量列
            volume_col = None
            for col in ['成交量', 'volume', 'Volume']:
                if col in hist_data.columns:
                    volume_col = col
                    break
            
            if close_col is None or volume_col is None:
                print(f"❌ {sector_name} 未找到价格或成交量列")
                return None
            
            # === 左上：价格趋势图 ===
            ax1 = axes[0, 0]
            prices = hist_data[close_col]
            
            # 计算移动平均线
            ma_periods = [5, 10, 20]
            try:
                price_mas = volume_price_strategy._calculate_raw_moving_averages(prices, ma_periods)
            except Exception:
                price_mas = {}
            
            ax1.plot(dates, prices, label='收盘价', linewidth=2, color='#1f77b4', alpha=0.8)
            
            # 绘制移动平均线
            ma_colors = ['#2ca02c', '#d62728', '#9467bd']
            for i, period in enumerate(ma_periods):
                if period in price_mas:
                    ax1.plot(dates, price_mas[period], label=f'MA{period}', 
                            linewidth=1.5, color=ma_colors[i], alpha=0.7, linestyle='--')
            
            ax1.set_title('价格趋势', fontsize=12, fontweight='bold')
            ax1.set_ylabel('价格', fontsize=10)
            ax1.legend(loc='upper left', fontsize=8)
            ax1.grid(True, alpha=0.3)
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
            
            # === 右上：MACD价格和均线 ===
            ax2 = axes[0, 1]
            
            # 确保MACD数据和hist_data对齐（使用相同的日期）
            macd_dates = pd.to_datetime(macd_data[date_col]) if date_col in macd_data.columns else dates
            
            ax2.plot(macd_dates, macd_data[close_col], label='收盘价', linewidth=2, color='#1f77b4')
            ax2.plot(macd_dates, macd_data['EMA_Fast'], label='EMA12', linewidth=1, color='#ff7f0e', alpha=0.7)
            ax2.plot(macd_dates, macd_data['EMA_Slow'], label='EMA26', linewidth=1, color='#2ca02c', alpha=0.7)
            
            ax2.set_title('MACD价格趋势', fontsize=12, fontweight='bold')
            ax2.set_ylabel('价格', fontsize=10)
            ax2.legend(loc='upper left', fontsize=8)
            ax2.grid(True, alpha=0.3)
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
            
            # === 左下：成交量趋势 ===
            ax3 = axes[1, 0]
            volumes = hist_data[volume_col]
            
            # 计算成交量移动平均线
            try:
                volume_mas = volume_price_strategy._calculate_raw_moving_averages(volumes, ma_periods)
            except Exception:
                volume_mas = {}
            
            ax3.bar(dates, volumes, label='成交量', color='#ff7f0e', alpha=0.6, width=0.8)
            
            # 绘制成交量移动平均线
            for i, period in enumerate(ma_periods):
                if period in volume_mas:
                    ax3.plot(dates, volume_mas[period], label=f'VOL MA{period}', 
                            linewidth=1.5, color=ma_colors[i], alpha=0.8, linestyle='--')
            
            ax3.set_title('成交量趋势', fontsize=12, fontweight='bold')
            ax3.set_xlabel('日期', fontsize=10)
            ax3.set_ylabel('成交量', fontsize=10)
            ax3.legend(loc='upper left', fontsize=8)
            ax3.grid(True, alpha=0.3)
            ax3.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45)
            
            # === 右下：MACD指标 ===
            ax4 = axes[1, 1]
            ax4.plot(macd_dates, macd_data['MACD'], label='MACD', linewidth=2, color='#d62728')
            ax4.plot(macd_dates, macd_data['Signal'], label='Signal', linewidth=2, color='#9467bd')
            ax4.bar(macd_dates, macd_data['Histogram'], label='Histogram', alpha=0.6, color='#17becf')
            ax4.axhline(y=0, color='black', linestyle='-', alpha=0.3)
            
            ax4.set_title('MACD指标', fontsize=12, fontweight='bold')
            ax4.set_xlabel('日期', fontsize=10)
            ax4.set_ylabel('MACD', fontsize=10)
            ax4.legend(loc='upper left', fontsize=8)
            ax4.grid(True, alpha=0.3)
            ax4.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45)
            
            # 调整布局
            plt.tight_layout(rect=[0, 0, 1, 0.98])
            
            # 生成文件路径
            chart_path = os.path.join(output_dir, f"{sector_name}_{date}.png")
            
            # 保存图表
            plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            return chart_path
            
        except Exception as e:
            print(f"❌ 创建 {sector_name} 综合图表失败: {e}")
            import traceback
            traceback.print_exc()
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

            # 3. 获取所有股票代码和名称的映射（一次性调用）
            print(f"\n📊 第二步：获取股票代码映射...")
            from ...repositories.stock.stock_query import StockQuery
            stock_query = StockQuery()
            stock_map = self._build_stock_code_map(stock_query)
            
            if not stock_map:
                print("⚠️ 无法获取股票代码映射")
                return {
                    'status': 'no_data',
                    'message': '无法获取股票代码映射',
                    'analysis_date': date
                }
            
            print(f"✅ 成功获取股票代码映射（共 {len(stock_map)} 条）")

            # 4. 批量查询股票近120天的日频行情数据
            print(f"\n📊 第三步：批量查询股票近120天的日频行情数据...")
            stock_data_dict = self._batch_query_stock_data(stock_list, date, stock_map)
            
            if not stock_data_dict:
                print("⚠️ 未获取到股票行情数据")
                return {
                    'status': 'no_data',
                    'message': '未获取到股票行情数据',
                    'analysis_date': date
                }
            
            print(f"✅ 成功获取 {len(stock_data_dict)} 只股票的行情数据")

            # 5. 并行执行趋势追踪策略分析和超跌反弹策略分析
            print(f"\n📊 第四步：并行执行策略分析...")
            from concurrent.futures import ThreadPoolExecutor
            
            with ThreadPoolExecutor(max_workers=2) as executor:
                # 提交两个分析任务
                trend_future = executor.submit(self._analyze_stocks_with_trend_tracking, stock_list, date, stock_data_dict, stock_map)
                oversold_future = executor.submit(self._analyze_stocks_with_oversold_rebound, stock_list, date, stock_data_dict, stock_map)
                
                # 等待两个任务完成
                trend_results = trend_future.result()
                oversold_results = oversold_future.result()

            # 6. 合并两种策略的分析结果
            print(f"\n📊 第五步：合并分析结果...")
            merged_results = self._merge_strategy_results(trend_results, oversold_results, target_sectors, stock_data_dict)

            # 7. 对有买入信号的股票生成综合图表（量价+MACD）
            print(f"\n📊 第六步：生成有买入信号股票的综合图表...")
            merged_results = self._generate_stock_combined_charts(
                merged_results, stock_data_dict, date
            )

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
    
    def _build_stock_code_map(self, stock_query) -> Dict[str, str]:
        """
        构建股票名称到代码的映射字典
        
        Args:
            stock_query: StockQuery 实例
            
        Returns:
            Dict[str, str]: {股票名称: 股票代码}
        """
        try:
            # 获取所有股票列表
            stocks_df = stock_query.get_all_stock()
            if stocks_df is None or stocks_df.empty:
                print("⚠️ 获取股票列表失败")
                return {}
            
            # 查找代码列和名称列
            code_col = None
            name_col = None
            
            for col in stocks_df.columns:
                col_lower = col.lower()
                if col_lower in ('code', '代码', 'symbol'):
                    code_col = col
                elif col_lower in ('name', '名称'):
                    name_col = col
            
            if code_col is None or name_col is None:
                # 如果找不到标准列名，尝试使用前两列
                if len(stocks_df.columns) >= 2:
                    code_col = stocks_df.columns[0]
                    name_col = stocks_df.columns[1]
                else:
                    print("⚠️ 无法识别股票列表的列结构")
                    return {}
            
            # 构建映射字典
            stock_map = {}
            for _, row in stocks_df.iterrows():
                stock_code = str(row[code_col]).strip() if pd.notna(row[code_col]) else None
                stock_name = str(row[name_col]).strip() if pd.notna(row[name_col]) else None
                
                if stock_code and stock_name:
                    stock_map[stock_name] = stock_code
            
            print(f"✅ 成功构建股票代码映射，共 {len(stock_map)} 条")
            return stock_map
            
        except Exception as e:
            print(f"❌ 构建股票代码映射失败: {e}")
            return {}

    def _batch_query_stock_data(self, stock_list: List[Dict[str, str]], date: str, stock_map: Dict[str, str]) -> Dict[str, pd.DataFrame]:
        """
        批量查询股票近120天的日频行情数据
        
        Args:
            stock_list: 股票列表，格式为 [{'name': '股票名', 'sector': '板块名'}, ...]
            date: 分析日期
            stock_map: 股票名称到代码的映射字典 {股票名称: 股票代码}
            
        Returns:
            Dict[str, pd.DataFrame]: 股票代码到历史数据的映射
        """
        try:
            from ...repositories.stock.stock_query import StockQuery
            from datetime import datetime, timedelta
            
            stock_query = StockQuery()
            start_date = (datetime.strptime(date, '%Y%m%d') - timedelta(days=120)).strftime('%Y%m%d')
            
            stock_data_dict = {}
            
            # 第一步：从映射中查找股票代码
            print(f"📊 第一步：从映射中查找股票代码...")
            stock_code_map = {}  # {stock_name: stock_code}
            for i, stock_info in enumerate(stock_list, 1):
                stock_name = stock_info['name']
                try:
                    # 从映射中查找股票代码
                    stock_code = stock_map.get(stock_name)
                    if stock_code:
                        stock_code_map[stock_name] = stock_code
                        print(f"✅ [{i}/{len(stock_list)}] 找到 {stock_name} 的代码: {stock_code}")
                    else:
                        print(f"⚠️ [{i}/{len(stock_list)}] 未找到股票代码: {stock_name}")
                except Exception as e:
                    print(f"❌ [{i}/{len(stock_list)}] 查找 {stock_name} 代码失败: {e}")
            
            if not stock_code_map:
                print(f"⚠️ 未找到任何股票代码")
                return {}
            
            # 第二步：批量查询所有股票的历史数据
            print(f"\n📊 第二步：批量查询 {len(stock_code_map)} 只股票的历史数据...")
            codes = list(stock_code_map.values())
            
            try:
                # 批量查询所有股票历史数据
                df_all = stock_query.get_historical_quotes(codes, start_date, date)
                
                if df_all is not None and not df_all.empty:
                    # 批量查询返回的数据包含 code 列，按 code 分组
                    if 'code' in df_all.columns:
                        for stock_name, stock_code in stock_code_map.items():
                            df_code = df_all[df_all['code'] == stock_code].copy()
                            if not df_code.empty:
                                # 移除 code 列
                                df_code = df_code.drop(columns=['code'], errors='ignore')
                                stock_data_dict[stock_code] = df_code
                                print(f"✅ 已获取 {stock_name} ({stock_code}) 的历史数据")
                            else:
                                print(f"⚠️ 未获取到 {stock_name} ({stock_code}) 的历史数据")
                        
                        print(f"✅ 成功批量获取 {len(stock_data_dict)}/{len(stock_code_map)} 只股票的历史数据")
                    else:
                        print(f"⚠️ 批量查询返回数据格式异常，未包含 code 列")
                        # 降级为逐个查询
                        for stock_name, stock_code in stock_code_map.items():
                            try:
                                hist_data = stock_query.get_historical_quotes(stock_code, start_date, date)
                                if hist_data is not None and not hist_data.empty:
                                    stock_data_dict[stock_code] = hist_data
                                    print(f"✅ 已获取 {stock_name} ({stock_code}) 的历史数据")
                                else:
                                    print(f"⚠️ 未获取到 {stock_name} ({stock_code}) 的历史数据")
                            except Exception as e:
                                print(f"❌ 获取 {stock_name} ({stock_code}) 数据失败: {e}")
                                continue
                else:
                    print(f"⚠️ 批量查询返回数据为空，降级为逐个查询")
                    # 降级为逐个查询
                    for stock_name, stock_code in stock_code_map.items():
                        try:
                            hist_data = stock_query.get_historical_quotes(stock_code, start_date, date)
                            if hist_data is not None and not hist_data.empty:
                                stock_data_dict[stock_code] = hist_data
                                print(f"✅ 已获取 {stock_name} ({stock_code}) 的历史数据")
                            else:
                                print(f"⚠️ 未获取到 {stock_name} ({stock_code}) 的历史数据")
                        except Exception as e:
                            print(f"❌ 获取 {stock_name} ({stock_code}) 数据失败: {e}")
                            continue
            except Exception as e:
                print(f"⚠️ 批量查询失败: {e}，降级为逐个查询")
                # 如果批量查询失败，降级为逐个查询
                for stock_name, stock_code in stock_code_map.items():
                    try:
                        hist_data = stock_query.get_historical_quotes(stock_code, start_date, date)
                        if hist_data is not None and not hist_data.empty:
                            stock_data_dict[stock_code] = hist_data
                            print(f"✅ 已获取 {stock_name} ({stock_code}) 的历史数据")
                        else:
                            print(f"⚠️ 未获取到 {stock_name} ({stock_code}) 的历史数据")
                    except Exception as ex:
                        print(f"❌ 获取 {stock_name} ({stock_code}) 数据失败: {ex}")
                    continue
            
            return stock_data_dict
            
        except Exception as e:
            print(f"❌ 批量查询股票数据失败: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def _analyze_stocks_with_trend_tracking(self, stock_list, date, stock_data_dict: Dict[str, pd.DataFrame], stock_map: Dict[str, str]):
        """
        使用趋势追踪策略分析股票
        
        Args:
            stock_list: 股票列表
            date: 分析日期
            stock_data_dict: 股票数据字典，格式为 {股票代码: DataFrame}
            stock_map: 股票名称到代码的映射字典 {股票名称: 股票代码}
        
        Returns:
            Dict: 趋势追踪分析结果
        """
        try:
            from ...strategies.individual_stock.trend_tracking_strategy import IndividualTrendTrackingStrategy
            from datetime import datetime, timedelta
            
            trend_strategy = IndividualTrendTrackingStrategy()
            
            stock_results = []
            
            for i, stock_info in enumerate(stock_list, 1):
                stock_name = stock_info['name']
                try:
                    print(f"📊 [趋势追踪] 正在分析股票 {i}/{len(stock_list)}: {stock_name}")
                    
                    # 从映射中查找股票代码
                    stock_code = stock_map.get(stock_name)
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
                        # 传递所属板块信息（可能为多个）
                        if 'sectors' in stock_info:
                            analysis_result['sectors'] = stock_info['sectors']
                        elif 'sector' in stock_info:
                            analysis_result['sectors'] = [stock_info['sector']] if stock_info['sector'] else []
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
    
    def _analyze_stocks_with_oversold_rebound(self, stock_list, date, stock_data_dict: Dict[str, pd.DataFrame], stock_map: Dict[str, str]):
        """
        使用超跌反弹策略分析股票
        
        Args:
            stock_list: 股票列表
            date: 分析日期
            stock_data_dict: 股票数据字典，格式为 {股票代码: DataFrame}
            stock_map: 股票名称到代码的映射字典 {股票名称: 股票代码}
        
        Returns:
            Dict: 超跌反弹分析结果
        """
        try:
            from ...strategies.individual_stock.oversold_rebound_strategy import IndividualOversoldReboundStrategy
            from datetime import datetime, timedelta
            
            oversold_strategy = IndividualOversoldReboundStrategy()
            
            stock_results = []
            
            for i, stock_info in enumerate(stock_list, 1):
                stock_name = stock_info['name']
                try:
                    print(f"📊 [超跌反弹] 正在分析股票 {i}/{len(stock_list)}: {stock_name}")
                    
                    # 从映射中查找股票代码
                    stock_code = stock_map.get(stock_name)
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
                        # 传递所属板块信息（可能为多个）
                        if 'sectors' in stock_info:
                            analysis_result['sectors'] = stock_info['sectors']
                        elif 'sector' in stock_info:
                            analysis_result['sectors'] = [stock_info['sector']] if stock_info['sector'] else []
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
    
    def _merge_strategy_results(self, trend_results, oversold_results, target_sectors, stock_data_dict=None):
        """
        合并两种策略的分析结果
        
        Args:
            trend_results: 趋势追踪策略结果
            oversold_results: 超跌反弹策略结果
            target_sectors: 目标板块列表
            stock_data_dict: 股票数据字典（可选）
            
        Returns:
            Dict: 合并后的结果
        """
        # 获取有买入信号的股票（取两个策略结果的并集）
        buy_stocks = set()
        
        # 从趋势追踪策略中获取买入信号股票
        if trend_results.get('status') == 'success':
            trend_all = trend_results.get('all_results', [])
            for stock in trend_all:
                signal_type = stock.get('current_signal_type', 'HOLD')
                if signal_type in ['BUY', 'STRONG_BUY']:
                    stock_code = stock.get('stock_code')
                    stock_name = stock.get('stock_name')
                    if stock_code and stock_name:
                        buy_stocks.add((stock_code, stock_name))
        
        # 从超跌反弹策略中获取买入信号股票
        if oversold_results.get('status') == 'success':
            oversold_all = oversold_results.get('all_results', [])
            for stock in oversold_all:
                signal_type = stock.get('current_signal_type', 'HOLD')
                if signal_type in ['BUY', 'STRONG_BUY']:
                    stock_code = stock.get('stock_code')
                    stock_name = stock.get('stock_name')
                    if stock_code and stock_name:
                        buy_stocks.add((stock_code, stock_name))
        
        # 转换为列表格式
        buy_stocks_list = [{'stock_code': code, 'stock_name': name} for code, name in buy_stocks]
        
        return {
            'status': 'success',
            'target_sectors': target_sectors,
            'trend_tracking': trend_results,
            'oversold_rebound': oversold_results,
            'buy_stocks': buy_stocks_list,  # 买入信号股票列表（取并集）
            'summary': {
                'trend_total': trend_results.get('total_analyzed', 0),
                'oversold_total': oversold_results.get('total_analyzed', 0),
                'trend_top_10': len(trend_results.get('top_10', [])),
                'oversold_top_10': len(oversold_results.get('top_10', [])),
                'buy_stocks_count': len(buy_stocks_list)
            }
        }
    
    def _generate_stock_combined_charts(self, merged_results: Dict[str, Any], 
                                       stock_data_dict: Dict[str, pd.DataFrame], 
                                       date: str) -> Dict[str, Any]:
        """
        对有买入信号的股票生成综合图表（量价+MACD在同一张图中）
        
        Args:
            merged_results: 合并后的分析结果
            stock_data_dict: 股票数据字典，格式为 {股票代码: DataFrame}
            date: 分析日期
            
        Returns:
            Dict[str, Any]: 更新后的合并结果，包含生成的图片路径
        """
        try:
            from ...strategies.individual_stock.trend_tracking_strategy import IndividualTrendTrackingStrategy
            from ...strategies.industry_sector.volume_price_strategy import VolumePriceStrategy
            import matplotlib.pyplot as plt
            import matplotlib.dates as mdates
            
            # 创建图片保存目录
            charts_dir = "reports/images/stocks"
            os.makedirs(charts_dir, exist_ok=True)
            
            # 获取趋势追踪策略和超跌反弹策略的 top_10 股票
            trend_tracking = merged_results.get('trend_tracking', {})
            oversold_rebound = merged_results.get('oversold_rebound', {})
            
            # 收集 top_10 股票列表（去重）
            top_10_stocks = set()
            
            # 从趋势追踪策略获取 top_10
            if trend_tracking.get('status') == 'success':
                trend_top_10 = trend_tracking.get('top_10', [])
                for stock in trend_top_10:
                    stock_code = stock.get('stock_code')
                    stock_name = stock.get('stock_name')
                    if stock_code and stock_name:
                        top_10_stocks.add((stock_code, stock_name, stock.get('signal_strength', 0), 'trend'))
            
            # 从超跌反弹策略获取 top_10
            if oversold_rebound.get('status') == 'success':
                oversold_top_10 = oversold_rebound.get('top_10', [])
                for stock in oversold_top_10:
                    stock_code = stock.get('stock_code')
                    stock_name = stock.get('stock_name')
                    if stock_code and stock_name:
                        top_10_stocks.add((stock_code, stock_name, stock.get('signal_strength', 0), 'oversold'))
            
            if not top_10_stocks:
                print(f"⚠️ 未找到 top_10 股票，跳过图表生成")
                merged_results['stock_chart_paths'] = {}
                return merged_results
            
            # 转换为列表并按信号强度排序
            stocks_list = [{'stock_code': code, 'stock_name': name, 'signal_strength': strength, 'strategy': strat} 
                          for code, name, strength, strat in top_10_stocks]
            stocks_list.sort(key=lambda x: x['signal_strength'], reverse=True)
            
            print(f"📸 找到 {len(stocks_list)} 只 top_10 股票，开始生成综合图片...")
            
            chart_paths = {}
            trend_strategy = IndividualTrendTrackingStrategy()
            volume_price_strategy = VolumePriceStrategy()
            
            for i, stock_info in enumerate(stocks_list, 1):
                stock_code = stock_info['stock_code']
                stock_name = stock_info['stock_name']
                
                try:
                    print(f"📊 正在生成股票 {i}/{len(stocks_list)}: {stock_name} ({stock_code})")
                    
                    # 获取股票数据
                    hist_data = stock_data_dict.get(stock_code)
                    if hist_data is None or hist_data.empty:
                        print(f"⚠️ {stock_name} ({stock_code}) 没有历史数据，跳过")
                        continue
                    
                    # 计算MACD数据
                    macd_data = trend_strategy.calculate_macd(hist_data)
                    if macd_data is None or macd_data.empty:
                        print(f"⚠️ {stock_name} ({stock_code}) MACD计算失败，跳过")
                        continue
                    
                    # 生成综合图片
                    chart_path = self._create_combined_stock_chart(
                        stock_name, stock_code, hist_data, macd_data, date, charts_dir, volume_price_strategy
                    )
                    
                    if chart_path:
                        chart_paths[f"{stock_code}_{stock_name}"] = chart_path
                        print(f"✅ {stock_name} ({stock_code}) 综合图表已生成: {chart_path}")
                    else:
                        print(f"⚠️ {stock_name} ({stock_code}) 综合图表生成失败")
                    
                except Exception as e:
                    print(f"❌ {stock_name} ({stock_code}) 综合图表生成失败: {e}")
                    continue
            
            # 更新合并结果，添加图片路径和排序后的股票列表信息
            merged_results['stock_chart_paths'] = chart_paths
            merged_results['top_10_stocks_for_charts'] = stocks_list
            
            print(f"✅ 成功生成 {len(chart_paths)}/{len(stocks_list)} 只 top_10 股票的综合图片")
            
            return merged_results
            
        except Exception as e:
            print(f"❌ 生成股票综合图片失败: {e}")
            import traceback
            traceback.print_exc()
            merged_results['stock_chart_paths'] = {}
            return merged_results
    
    def _create_combined_stock_chart(self, stock_name: str, stock_code: str, 
                                      hist_data: pd.DataFrame, macd_data: pd.DataFrame, 
                                      date: str, output_dir: str, volume_price_strategy) -> Optional[str]:
        """
        创建股票综合图表（量价+MACD）
        
        Args:
            stock_name: 股票名称
            stock_code: 股票代码
            hist_data: 历史数据
            macd_data: MACD数据
            date: 分析日期
            output_dir: 输出目录
            volume_price_strategy: 量价策略实例
            
        Returns:
            Optional[str]: 生成的图表文件路径
        """
        try:
            import matplotlib.pyplot as plt
            import matplotlib.dates as mdates
            
            # 设置中文字体
            plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans', 'Arial']
            plt.rcParams['axes.unicode_minus'] = False
            
            # 创建四子图布局：价格+量价图，MACD图
            fig, axes = plt.subplots(2, 2, figsize=(18, 12))
            fig.suptitle(f'{stock_name} ({stock_code}) 综合分析图 - {date}', fontsize=16, fontweight='bold', y=0.995)
            
            # 检测日期列名
            date_col = None
            for col in ['日期', 'date', 'Date', '交易日期']:
                if col in hist_data.columns:
                    date_col = col
                    break
            
            if date_col is None:
                print(f"❌ {stock_name} 未找到日期列")
                return None
            
            # 确保数据按日期排序
            hist_data = hist_data.sort_values(date_col).reset_index(drop=True)
            dates = pd.to_datetime(hist_data[date_col])
            
            # 获取收盘价列
            close_col = None
            for col in ['收盘', '收盘价', 'close', 'Close']:
                if col in hist_data.columns:
                    close_col = col
                    break
            
            # 获取成交量列
            volume_col = None
            for col in ['成交量', 'volume', 'Volume']:
                if col in hist_data.columns:
                    volume_col = col
                    break
            
            if close_col is None or volume_col is None:
                print(f"❌ {stock_name} 未找到价格或成交量列")
                return None
            
            # === 左上：价格趋势图 ===
            ax1 = axes[0, 0]
            prices = hist_data[close_col]
            
            # 计算移动平均线
            ma_periods = [5, 10, 20]
            try:
                price_mas = volume_price_strategy._calculate_raw_moving_averages(prices, ma_periods)
            except Exception:
                price_mas = {}
            
            ax1.plot(dates, prices, label='收盘价', linewidth=2, color='#1f77b4', alpha=0.8)
            
            # 绘制移动平均线
            ma_colors = ['#2ca02c', '#d62728', '#9467bd']
            for i, period in enumerate(ma_periods):
                if period in price_mas:
                    ax1.plot(dates, price_mas[period], label=f'MA{period}', 
                            linewidth=1.5, color=ma_colors[i], alpha=0.7, linestyle='--')
            
            ax1.set_title('价格趋势', fontsize=12, fontweight='bold')
            ax1.set_ylabel('价格', fontsize=10)
            ax1.legend(loc='upper left', fontsize=8)
            ax1.grid(True, alpha=0.3)
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
            
            # === 右上：MACD价格和均线 ===
            ax2 = axes[0, 1]
            
            # 确保MACD数据和hist_data对齐（使用相同的日期）
            if date_col in macd_data.columns:
                macd_dates = pd.to_datetime(macd_data[date_col])
            else:
                macd_dates = dates
            
            # 从macd_data中获取收盘价（如果存在）
            if close_col in macd_data.columns:
                macd_close = macd_data[close_col]
            else:
                macd_close = prices
            
            ax2.plot(macd_dates, macd_close, label='收盘价', linewidth=2, color='#1f77b4')
            if 'EMA_Fast' in macd_data.columns:
                ax2.plot(macd_dates, macd_data['EMA_Fast'], label='EMA12', linewidth=1, color='#ff7f0e', alpha=0.7)
            if 'EMA_Slow' in macd_data.columns:
                ax2.plot(macd_dates, macd_data['EMA_Slow'], label='EMA26', linewidth=1, color='#2ca02c', alpha=0.7)
            
            ax2.set_title('MACD价格趋势', fontsize=12, fontweight='bold')
            ax2.set_ylabel('价格', fontsize=10)
            ax2.legend(loc='upper left', fontsize=8)
            ax2.grid(True, alpha=0.3)
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
            
            # === 左下：成交量趋势 ===
            ax3 = axes[1, 0]
            volumes = hist_data[volume_col]
            
            # 计算成交量移动平均线
            try:
                volume_mas = volume_price_strategy._calculate_raw_moving_averages(volumes, ma_periods)
            except Exception:
                volume_mas = {}
            
            ax3.bar(dates, volumes, label='成交量', color='#ff7f0e', alpha=0.6, width=0.8)
            
            # 绘制成交量移动平均线
            for i, period in enumerate(ma_periods):
                if period in volume_mas:
                    ax3.plot(dates, volume_mas[period], label=f'VOL MA{period}', 
                            linewidth=1.5, color=ma_colors[i], alpha=0.8, linestyle='--')
            
            ax3.set_title('成交量趋势', fontsize=12, fontweight='bold')
            ax3.set_xlabel('日期', fontsize=10)
            ax3.set_ylabel('成交量', fontsize=10)
            ax3.legend(loc='upper left', fontsize=8)
            ax3.grid(True, alpha=0.3)
            ax3.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45)
            
            # === 右下：MACD指标 ===
            ax4 = axes[1, 1]
            if 'DIF' in macd_data.columns:
                ax4.plot(macd_dates, macd_data['DIF'], label='MACD(DIF)', linewidth=2, color='#d62728')
            if 'DEA' in macd_data.columns:
                ax4.plot(macd_dates, macd_data['DEA'], label='Signal(DEA)', linewidth=2, color='#9467bd')
            if 'MACD' in macd_data.columns:
                # MACD列是柱状图（histogram = DIF - DEA）
                ax4.bar(macd_dates, macd_data['MACD'], label='Histogram', alpha=0.6, color='#17becf')
            ax4.axhline(y=0, color='black', linestyle='-', alpha=0.3)
            
            ax4.set_title('MACD指标', fontsize=12, fontweight='bold')
            ax4.set_xlabel('日期', fontsize=10)
            ax4.set_ylabel('MACD', fontsize=10)
            ax4.legend(loc='upper left', fontsize=8)
            ax4.grid(True, alpha=0.3)
            ax4.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45)
            
            # 调整布局
            plt.tight_layout(rect=[0, 0, 1, 0.98])
            
            # 生成文件路径：reports/images/stocks/{股票名称}_{日期}.png
            chart_path = os.path.join(output_dir, f"{stock_name}_{date}.png")
            
            # 保存图表
            plt.savefig(chart_path, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            return chart_path
            
        except Exception as e:
            print(f"❌ 创建 {stock_name} 综合图表失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
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
            
            # 先聚合股票 -> 所属板块集合，确保一只股票可属于多个板块
            stock_to_sectors: Dict[str, set] = {}
            
            for sector in sectors:
                stocks = get_stocks_by_sector(sector)
                if not stocks:
                    print(f"⚠️ 板块 {sector} 未找到股票列表")
                    continue
                for stock_name in stocks:
                    if stock_name not in stock_to_sectors:
                        stock_to_sectors[stock_name] = set()
                    stock_to_sectors[stock_name].add(sector)
            
            # 构建包含多板块信息的列表
            stock_list: List[Dict[str, Any]] = []
            for stock_name, sector_set in stock_to_sectors.items():
                stock_list.append({
                    'name': stock_name,
                    'sector': list(sector_set)[0] if sector_set else '',  # 兼容旧字段
                    'sectors': sorted(list(sector_set))
                })
            
            print(f"📈 从 {len(sectors)} 个板块中获取到 {len(stock_list)} 只股票（已聚合多板块归属）")
            
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
            
            # 合并信号摘要
            macd_signals = macd_analysis.get('signal_summary', {})
            vp_signals = volume_price_analysis.get('signal_summary', {})
            
            # 保存MACD数据字典（用于后续生成图片）
            macd_data_dict = macd_analysis.get('macd_data_dict', {})
            
            # 返回合并结果
            return {
                'status': 'success',
                'analysis_date': date,
                'total_sectors': len(INDUSTRY_SECTORS),
                'analyzed_sectors': len(combined_sector_results),
                'sector_results': combined_sector_results,
                'macd_signal_summary': macd_signals,
                'vp_signal_summary': vp_signals,
                'macd_analysis': macd_analysis,
                'volume_price_analysis': volume_price_analysis,
                'macd_data_dict': macd_data_dict  # 保存用于生成图片
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
