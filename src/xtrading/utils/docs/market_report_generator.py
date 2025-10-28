"""
市场报告生成器
负责生成市场复盘报告的Markdown内容
"""

from typing import Dict, Any, Optional
from datetime import datetime


class MarketReportGenerator:
    """市场报告生成器类"""
    
    def __init__(self):
        """初始化市场报告生成器"""
        pass
    
    def generate_market_review_content(self, date: str, market_summary: Dict[str, Any],
                                     sector_analysis: Dict[str, Any], 
                                     stock_analysis: Dict[str, Any]) -> str:
        """
        生成市场复盘报告内容
        
        Args:
            date: 复盘日期
            market_summary: 市场总结数据
            sector_analysis: 板块分析数据
            stock_analysis: 个股分析数据
            
        Returns:
            str: 报告内容
        """
        try:
            content = []
            
            # 报告标题
            content.append(f"# 市场复盘报告 - {date}")
            content.append("")
            content.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            content.append("")
            
            # 目录
            content.extend(self._build_table_of_contents())
            content.append("")
            
            # 市场总结部分
            content.extend(self._build_market_summary_section(market_summary))
            
            # 板块分析部分
            content.extend(self._build_sector_analysis_section(sector_analysis))
            
            # 个股分析部分
            content.extend(self._build_stock_analysis_section(stock_analysis))
            
            # 风险提示
            content.extend(self._build_risk_warning_section())
            
            return "\n".join(content)
            
        except Exception as e:
            print(f"❌ 构建报告内容失败: {e}")
            return f"# 市场复盘报告 - {date}\n\n❌ 报告生成失败: {str(e)}"
    
    def _build_market_summary_section(self, market_summary: Dict[str, Any]) -> list:
        """
        构建市场总结部分
        
        Args:
            market_summary: 市场总结数据
            
        Returns:
            list: 市场总结部分内容
        """
        content = []
        content.append("## 📊 市场总结")
        content.append("")
        
        if 'error' not in market_summary:
            # 综合情绪指数
            overall_sentiment = market_summary.get('overall_sentiment', 0)
            sentiment_level = market_summary.get('sentiment_level', '未知')
            content.append(f"**综合情绪指数**: {overall_sentiment:.2f}")
            content.append(f"**情绪等级**: {sentiment_level}")
            content.append("")

            # 雷达图
            radar_chart_path = market_summary.get('radar_chart_path')
            if radar_chart_path:
                content.extend(self._build_radar_chart_section(radar_chart_path))

            # 各维度情绪分数
            sentiment_scores = market_summary.get('sentiment_scores', {})
            if sentiment_scores:
                content.extend(self._build_sentiment_scores_section(sentiment_scores))
            
            # 关键指标
            key_metrics = market_summary.get('key_metrics', {})
            if key_metrics:
                content.extend(self._build_key_metrics_section(key_metrics))
            
        else:
            content.append(f"❌ 市场总结分析失败: {market_summary.get('error', '未知错误')}")
            content.append("")
        
        return content
    
    def _build_sentiment_scores_section(self, sentiment_scores: Dict[str, float]) -> list:
        """
        构建情绪分数部分（表格形式）
        
        Args:
            sentiment_scores: 情绪分数数据
            
        Returns:
            list: 情绪分数部分内容
        """
        content = []
        content.append("### 情绪维度分析")
        content.append("")
        
        # 创建表格
        content.append("| 维度 | 分析结果 |")
        content.append("|------|----------|")
        
        # 维度映射
        dimension_mapping = {
            'market_activity': '市场活跃度',
            'profit_effect': '个股赚钱效应', 
            'risk_preference': '风险偏好',
            'participation_willingness': '市场参与意愿'
        }
        
        # 生成表格行
        for dimension_key, dimension_name in dimension_mapping.items():
            score = sentiment_scores.get(dimension_key, 0)
            content.append(f"| {dimension_name} | {score:.2f} |")
        
        content.append("")
        return content
    
    def _build_key_metrics_section(self, key_metrics: Dict[str, Any]) -> list:
        """
        构建关键指标部分
        
        Args:
            key_metrics: 关键指标数据
            
        Returns:
            list: 关键指标部分内容
        """
        content = []
        content.append("### 关键市场指标")
        content.append("")
        
        # 市场活跃度
        market_activity = key_metrics.get('market_activity')
        if market_activity is not None and not market_activity.empty:
            content.extend(self._build_market_activity_section(market_activity))
        
        # 个股赚钱效应（使用market_summary数据）
        profit_effect = key_metrics.get('market_summary')
        if profit_effect is not None and not profit_effect.empty:
            content.extend(self._build_profit_effect_section(profit_effect))
        
        # 风险偏好
        risk_preference = key_metrics.get('risk_preference')
        if risk_preference is not None and not risk_preference.empty:
            content.extend(self._build_risk_preference_section(risk_preference, key_metrics))
        
        # 市场参与意愿
        participation = key_metrics.get('participation_willingness')
        if participation is not None and not participation.empty:
            content.extend(self._build_participation_section(participation))
        
        return content
    
    def _build_market_activity_section(self, market_activity) -> list:
        """
        构建市场活跃度部分
        
        Args:
            market_activity: 市场活跃度数据（DataFrame）
            
        Returns:
            list: 市场活跃度部分内容
        """
        content = []
        content.append("#### 市场活跃度")
        
        try:
            if not market_activity.empty:
                # 获取第一行数据
                row = market_activity.iloc[0]
                
                # 涨停股数量
                limit_up_count = row.get('涨停', 0)
                content.append(f"- **涨停股数量**: {int(limit_up_count)}")
                
                # 上涨比例
                rise_ratio = row.get('上涨比例', 0)
                content.append(f"- **上涨比例**: {rise_ratio:.2f}%")
                
                # 下跌比例
                fall_ratio = row.get('下跌比例', 0)
                content.append(f"- **下跌比例**: {fall_ratio:.2f}%")
                
                # 平盘比例
                flat_ratio = row.get('平盘比例', 0)
                content.append(f"- **平盘比例**: {flat_ratio:.2f}%")
            else:
                content.append("- **数据**: 暂无数据")
        except Exception as e:
            content.append(f"- **错误**: 数据处理失败 - {str(e)}")
        
        content.append("")
        return content
    
    def _build_profit_effect_section(self, profit_effect) -> list:
        """
        构建个股赚钱效应部分
        
        Args:
            profit_effect: 赚钱效应数据（DataFrame）
            
        Returns:
            list: 赚钱效应部分内容
        """
        content = []
        content.append("#### 个股赚钱效应")
        
        try:
            if not profit_effect.empty:
                # 计算总成交金额
                total_turnover = profit_effect['成交金额'].sum()
                content.append(f"- **市场总成交金额**: {total_turnover:,.0f} 亿元")
                
                # 计算平均换手率
                avg_turnover_rate = profit_effect['流通换手率'].mean()
                content.append(f"- **平均流通换手率**: {avg_turnover_rate:.2f}%")
                
                # 各板块成交金额
                content.append("- **各板块成交金额**:")
                for _, row in profit_effect.iterrows():
                    category = row['证券类别']
                    turnover = row['成交金额']
                    content.append(f"  - {category}: {turnover:,.0f} 亿元")
            else:
                content.append("- **数据**: 暂无数据")
        except Exception as e:
            content.append(f"- **错误**: 数据处理失败 - {str(e)}")
        
        content.append("")
        return content
    
    def _build_risk_preference_section(self, risk_preference, key_metrics=None) -> list:
        """
        构建风险偏好部分
        
        Args:
            risk_preference: 风险偏好数据（DataFrame）
            key_metrics: 关键指标数据，用于获取流通市值
            
        Returns:
            list: 风险偏好部分内容
        """
        content = []
        content.append("#### 风险偏好")
        
        try:
            if not risk_preference.empty:
                # 获取最新数据（最后一行）
                latest_data = risk_preference.iloc[-1]
                
                # 融资余额
                margin_balance = latest_data.get('融资余额', 0)
                content.append(f"- **融资余额**: {margin_balance:,.0f} 亿元")
                
                # 融券余额
                short_balance = latest_data.get('融券余额', 0)
                content.append(f"- **融券余额**: {short_balance:,.0f} 亿元")
                
                # 两融余额
                total_margin = margin_balance + short_balance
                content.append(f"- **两融余额**: {total_margin:,.0f} 亿元")
                
                # 平均维持担保比例
                avg_ratio = latest_data.get('平均维持担保比例', 0)
                content.append(f"- **平均维持担保比例**: {avg_ratio:.2f}%")

                # 两融余额占流通市值占比
                if key_metrics and 'market_summary' in key_metrics:
                    market_summary_df = key_metrics['market_summary']
                    if not market_summary_df.empty:
                        # 计算总流通市值
                        total_circulating_market_cap = market_summary_df['流通市值'].sum()
                        # 计算占比
                        margin_ratio = (total_margin / total_circulating_market_cap) * 100
                        content.append(f"- **两融余额占流通市值占比**: {margin_ratio:.2f}%")

            else:
                content.append("- **数据**: 暂无数据")
        except Exception as e:
            content.append(f"- **错误**: 数据处理失败 - {str(e)}")
        
        content.append("")
        return content
    
    def _build_participation_section(self, participation) -> list:
        """
        构建市场参与意愿部分
        
        Args:
            participation: 参与意愿数据（DataFrame）
            
        Returns:
            list: 参与意愿部分内容
        """
        content = []
        content.append("#### 市场参与意愿")
        
        try:
            if not participation.empty:
                # 获取最新数据（最后一行）
                latest_data = participation.iloc[-1]
                
                # 大单净流入占比
                large_net_inflow_ratio = latest_data.get('大单净流入-净占比', 0)
                content.append(f"- **大单净流入占比**: {large_net_inflow_ratio:.2f}%")
                
                # 中单净流入占比
                medium_net_inflow_ratio = latest_data.get('中单净流入-净占比', 0)
                content.append(f"- **中单净流入占比**: {medium_net_inflow_ratio:.2f}%")
                
                # 小单净流入占比
                small_net_inflow_ratio = latest_data.get('小单净流入-净占比', 0)
                content.append(f"- **小单净流入占比**: {small_net_inflow_ratio:.2f}%")
                
                # 上证收盘价
                shanghai_close = latest_data.get('上证-收盘价', 0)
                content.append(f"- **上证收盘价**: {shanghai_close:.2f}")
                
                # 上证涨跌幅
                shanghai_change = latest_data.get('上证-涨跌幅', 0)
                content.append(f"- **上证涨跌幅**: {shanghai_change:.2f}%")
            else:
                content.append("- **数据**: 暂无数据")
        except Exception as e:
            content.append(f"- **错误**: 数据处理失败 - {str(e)}")
        
        content.append("")
        return content
    
    def _build_radar_chart_section(self, radar_chart_path: str) -> list:
        """
        构建雷达图部分
        
        Args:
            radar_chart_path: 雷达图文件路径
            
        Returns:
            list: 雷达图部分内容
        """
        content = []
        content.append("### 📈 市场情绪综合分析图")
        content.append("")
        
        # 将绝对路径转换为相对路径
        if radar_chart_path:
            # 提取文件名
            import os
            filename = os.path.basename(radar_chart_path)
            # 使用相对路径
            relative_path = f"../images/sentiment/{filename}"
            content.append(f"![市场情绪综合分析图]({relative_path})")
            content.append("")
            content.append(f"*图表说明：上图展示了{radar_chart_path.split('_')[-1].split('.')[0]}的市场情绪综合分析，包括雷达图和趋势分析。*")
        else:
            content.append("❌ 综合分析图生成失败")
        
        content.append("")
        return content
    
    def _build_sector_analysis_section(self, sector_analysis: Dict[str, Any]) -> list:
        """
        构建板块分析部分
        
        Args:
            sector_analysis: 板块分析数据
            
        Returns:
            list: 板块分析部分内容
        """
        content = []
        content.append("## 🏢 板块分析")
        content.append("")
        
        if sector_analysis.get('status') == 'success':
            # 获取分析结果
            macd_analysis = sector_analysis.get('macd_analysis', {})
            volume_price_analysis = sector_analysis.get('volume_price_analysis', {})
            
            # 一、量价分析结果
            content.extend(self._build_volume_price_analysis_section(volume_price_analysis))
            
            # 二、MACD分析结果
            content.extend(self._build_macd_analysis_section(macd_analysis))
            
        elif sector_analysis.get('status') == 'framework':
            content.append("🚧 板块分析功能正在开发中...")
        else:
            content.append("❌ 板块分析失败")
            error = sector_analysis.get('error', '未知错误')
            content.append(f"**错误信息**: {error}")
        
        content.append("")
        return content
    
    def _build_volume_price_analysis_section(self, volume_price_analysis: Dict[str, Any]) -> list:
        """
        构建量价分析部分
        
        Args:
            volume_price_analysis: 量价分析数据
            
        Returns:
            list: 量价分析部分内容
        """
        content = []
        content.append("### 📊 量价分析")
        content.append("")
        
        if volume_price_analysis.get('status') == 'success':
            sector_results = volume_price_analysis.get('sector_results', {})
            signal_summary = volume_price_analysis.get('signal_summary', {})
            
            # 对信号列表按涨幅均值进行排序
            buy_signals = self._sort_volume_price_signals(signal_summary.get('BUY', []), sector_results)
            sell_signals = self._sort_volume_price_signals(signal_summary.get('SELL', []), sector_results)
            neutral_signals = self._sort_volume_price_signals(signal_summary.get('NEUTRAL', []), sector_results)
            
            # 买入信号板块
            if buy_signals:
                content.extend(self._build_volume_price_buy_signals_section(sector_results, buy_signals))
            
            # 卖出信号板块
            content.extend(self._build_volume_price_sell_signals_section(sector_results, sell_signals))
            
            # 中性信号板块（TOP10）
            if neutral_signals:
                content.extend(self._build_volume_price_neutral_signals_section(sector_results, neutral_signals))
            
            # 量价关系趋势图
            vp_charts = volume_price_analysis.get('chart_paths', {})
            if vp_charts:
                # 买入信号板块量价图表
                if buy_signals:
                    content.extend(self._build_volume_price_charts_section(buy_signals, vp_charts, "买入信号板块"))
                
                # 中性信号板块量价图表（TOP10）
                if neutral_signals:
                    top_10_neutral = neutral_signals[:10]
                    content.extend(self._build_volume_price_charts_section(top_10_neutral, vp_charts, "中性信号板块（TOP10）"))
        else:
            content.append("❌ 量价分析失败")
            
        content.append("")
        return content
    
    def _sort_volume_price_signals(self, signals: list, sector_results: dict) -> list:
        """
        对量价信号列表按照涨幅均值进行排序
        
        Args:
            signals: 信号板块名称列表
            sector_results: 板块分析结果
            
        Returns:
            list: 排序后的板块名称列表
        """
        def get_avg_change(sector_name: str) -> float:
            """计算板块的涨幅均值"""
            sector_data = sector_results.get(sector_name, {})
            volume_change = sector_data.get('volume_change_pct', 0)
            price_change = sector_data.get('price_change_pct', 0)
            return (volume_change + price_change) / 2
        
        # 按涨幅均值从大到小排序
        sorted_signals = sorted(signals, key=lambda x: get_avg_change(x), reverse=True)
        return sorted_signals
    
    def _build_macd_analysis_section(self, macd_analysis: Dict[str, Any]) -> list:
        """
        构建MACD分析部分
        
        Args:
            macd_analysis: MACD分析数据
            
        Returns:
            list: MACD分析部分内容
        """
        content = []
        content.append("### 📈 MACD分析")
        content.append("")
        
        if macd_analysis.get('status') == 'success':
            sector_results = macd_analysis.get('sector_results', {})
            all_sectors = sector_results.get('all_sectors', {})
            signal_summary = macd_analysis.get('signal_summary', {})
            
            # 买入信号板块
            buy_signals = signal_summary.get('buy_signals', [])
            if buy_signals:
                content.extend(self._build_macd_buy_signals_section(buy_signals, all_sectors))
            
            # 卖出信号板块
            sell_signals = signal_summary.get('sell_signals', [])
            content.extend(self._build_macd_sell_signals_section(sell_signals, all_sectors))
            
            # 中性信号板块（TOP10）
            neutral_signals = signal_summary.get('neutral_signals', [])
            if neutral_signals:
                content.extend(self._build_macd_neutral_signals_section(neutral_signals, all_sectors))
            
            # MACD趋势图
            macd_charts = macd_analysis.get('chart_paths', {})
            if macd_charts:
                # 买入信号板块MACD图表
                if buy_signals:
                    content.extend(self._build_macd_charts_section_for_sectors(buy_signals, macd_charts, "买入信号板块"))
                
                # 中性信号板块MACD图表（TOP10）
                if neutral_signals:
                    top_10_neutral = neutral_signals[:10]
                    content.extend(self._build_macd_charts_section_for_sectors(top_10_neutral, macd_charts, "中性信号板块（TOP10）"))
        else:
            content.append("❌ MACD分析失败")
            
        content.append("")
        return content
    
    def _build_stock_analysis_section(self, stock_analysis: Dict[str, Any]) -> list:
        """
        构建个股分析部分
        
        Args:
            stock_analysis: 个股分析数据
            
        Returns:
            list: 个股分析部分内容
        """
        content = []
        content.append("## 🎯 个股分析")
        content.append("")
        
        status = stock_analysis.get('status')
        
        if status == 'framework':
            content.append("🚧 个股分析功能正在开发中...")
        elif status == 'no_data':
            content.append(f"⚠️ {stock_analysis.get('message', '无数据')}")
        elif status == 'failed':
            content.append(f"❌ 个股分析失败: {stock_analysis.get('error', '未知错误')}")
        elif status == 'success':
            # 显示分析概览
            summary = stock_analysis.get('summary', {})
            target_sectors = stock_analysis.get('target_sectors', [])
            trend_tracking = stock_analysis.get('trend_tracking', {})
            oversold_rebound = stock_analysis.get('oversold_rebound', {})
            
            content.append(f"**趋势追踪策略分析**: {summary.get('trend_total', 0)}只股票")
            content.append(f"**超跌反弹策略分析**: {summary.get('oversold_total', 0)}只股票")
            content.append(f"**分析板块数量**: {len(target_sectors)}个")
            content.append("")
            
            if target_sectors:
                content.append(f"**目标板块**: {', '.join(target_sectors[:8])}{'...' if len(target_sectors) > 8 else ''}")
                content.append("")
            
            # === 趋势追踪策略结果 ===
            if trend_tracking.get('status') == 'success':
                content.append("## 📈 趋势追踪策略 - TOP10股票")
                content.append("")
                
                top_stocks = trend_tracking.get('top_10', [])
                if top_stocks:
                    table_data = [["排名", "股票名称", "信号类型", "趋势状态", "信号强度", "最新价", "趋势强度"]]
                    
                    for i, stock in enumerate(top_stocks[:10], 1):
                        stock_name = stock.get('stock_name', stock.get('symbol', '未知'))
                        signal_type = stock.get('current_signal_type', 'HOLD')
                        trend_status = stock.get('trend_status', 'SIDEWAYS')
                        signal_strength = stock.get('signal_strength', 0)
                        latest_close = stock.get('latest_close', 0)
                        trend_strength = stock.get('trend_strength', 0)
                        
                        table_data.append([
                            str(i),
                            stock_name,
                            signal_type,
                            trend_status,
                            f"{signal_strength:.1f}",
                            f"{latest_close:.2f}",
                            f"{trend_strength:.2f}"
                        ])
                    
                    content.append(self._generate_markdown_table(table_data))
                    content.append("")
                
                # 详细分析前3只
                if top_stocks:
                    content.append("### 详细分析")
                    content.append("")
                    for i, stock in enumerate(top_stocks[:3], 1):
                        stock_name = stock.get('stock_name', stock.get('symbol', '未知'))
                        content.append(f"#### {i}. {stock_name}")
                        content.append("")
                        content.append(f"- **信号类型**: {stock.get('current_signal_type', 'HOLD')}")
                        content.append(f"- **趋势状态**: {stock.get('trend_status', 'SIDEWAYS')}")
                        content.append(f"- **信号强度**: {stock.get('signal_strength', 0):.1f}")
                        content.append(f"- **最新收盘价**: {stock.get('latest_close', 0):.2f}")
                        content.append("")
            
            # === 超跌反弹策略结果 ===
            if oversold_rebound.get('status') == 'success':
                content.append("## 📉 超跌反弹策略 - TOP10股票")
                content.append("")
                
                top_stocks = oversold_rebound.get('top_10', [])
                if top_stocks:
                    table_data = [["排名", "股票名称", "信号类型", "超跌类型", "信号强度", "最新价", "超跌强度"]]
                    
                    for i, stock in enumerate(top_stocks[:10], 1):
                        stock_name = stock.get('stock_name', stock.get('symbol', '未知'))
                        signal_type = stock.get('current_signal_type', 'HOLD')
                        oversold_type = stock.get('oversold_type', 'NONE')
                        signal_strength = stock.get('signal_strength', 0)
                        latest_close = stock.get('latest_close', 0)
                        oversold_strength = stock.get('oversold_strength', 0)
                        
                        table_data.append([
                            str(i),
                            stock_name,
                            signal_type,
                            oversold_type,
                            f"{signal_strength:.1f}",
                            f"{latest_close:.2f}",
                            f"{oversold_strength:.2f}"
                        ])
                    
                    content.append(self._generate_markdown_table(table_data))
                    content.append("")
                
                # 详细分析前3只
                if top_stocks:
                    content.append("### 详细分析")
                    content.append("")
                    for i, stock in enumerate(top_stocks[:3], 1):
                        stock_name = stock.get('stock_name', stock.get('symbol', '未知'))
                        content.append(f"#### {i}. {stock_name}")
                        content.append("")
                        content.append(f"- **信号类型**: {stock.get('current_signal_type', 'HOLD')}")
                        content.append(f"- **超跌类型**: {stock.get('oversold_type', 'NONE')}")
                        content.append(f"- **信号强度**: {stock.get('signal_strength', 0):.1f}")
                        content.append(f"- **KDJ状态**: {stock.get('kdj_status', 'NORMAL')}")
                        content.append(f"- **RSI状态**: {stock.get('rsi_status', 'NORMAL')}")
                        content.append("")
        else:
            content.append("📊 个股分析数据")
        
        content.append("")
        return content
    
    def _generate_markdown_table(self, data: list) -> str:
        """
        生成Markdown格式的表格
        
        Args:
            data: 表格数据，格式为 [[header1, header2, ...], [row1, row2, ...], ...]
            
        Returns:
            str: Markdown格式的表格字符串
        """
        if not data or len(data) < 2:
            return ""
        
        lines = []
        
        # 表头
        header = "| " + " | ".join(data[0]) + " |"
        lines.append(header)
        
        # 分隔符
        separator = "| " + " | ".join(["---"] * len(data[0])) + " |"
        lines.append(separator)
        
        # 数据行
        for row in data[1:]:
            row_str = "| " + " | ".join(str(cell) for cell in row) + " |"
            lines.append(row_str)
        
        return "\n".join(lines)
    
    def _build_risk_warning_section(self) -> list:
        """
        构建风险提示部分
        
        Returns:
            list: 风险提示部分内容
        """
        content = []
        content.append("## ⚠️ 风险提示")
        content.append("")
        content.append("本报告仅供学习和研究使用，不构成投资建议。投资有风险，入市需谨慎。")
        content.append("")
        return content
    
    def _build_table_of_contents(self) -> list:
        """
        构建目录部分
        
        Returns:
            list: 目录部分内容
        """
        content = []
        content.append("## 📋 目录")
        content.append("")
        content.append("- [📊 市场总结](#-市场总结)")
        content.append("  - [📈 市场情绪综合分析图](#-市场情绪综合分析图)")
        content.append("  - [情绪维度分析](#情绪维度分析)")
        content.append("  - [关键市场指标](#关键市场指标)")
        content.append("    - [市场活跃度](#市场活跃度)")
        content.append("    - [个股赚钱效应](#个股赚钱效应)")
        content.append("    - [风险偏好](#风险偏好)")
        content.append("    - [市场参与意愿](#市场参与意愿)")
        content.append("- [🏢 板块分析](#-板块分析)")
        content.append("- [🎯 个股分析](#-个股分析)")
        content.append("- [⚠️ 风险提示](#️-风险提示)")
        content.append("")
        return content
    
    def _build_buy_signals_section(self, buy_signals: list) -> list:
        """
        构建买入信号板块部分
        
        Args:
            buy_signals: 买入信号板块列表
            
        Returns:
            list: 买入信号板块部分内容
        """
        content = []
        content.append("### 📈 买入信号板块")
        content.append("")
        content.append(f"**信号数量**: {len(buy_signals)}个")
        content.append("")
        
        if buy_signals:
            content.append("| 排名 | 板块名称 | 信号强度 | MACD值 | 柱状图 |")
            content.append("|------|----------|----------|--------|--------|")
            
            for i, signal in enumerate(buy_signals, 1):
                sector_name = signal['sector_name']
                strength = signal['signal_strength']
                macd = signal['macd']
                histogram = signal['histogram']
                content.append(f"| {i} | {sector_name} | {strength:.4f} | {macd:.4f} | {histogram:.4f} |")
        
        content.append("")
        return content
    
    def _build_sell_signals_section(self, sell_signals: list) -> list:
        """
        构建卖出信号板块部分
        
        Args:
            sell_signals: 卖出信号板块列表
            
        Returns:
            list: 卖出信号板块部分内容
        """
        content = []
        content.append("### 📉 卖出信号板块")
        content.append("")
        content.append(f"**信号数量**: {len(sell_signals)}个")
        content.append("")
        
        if sell_signals:
            content.append("| 排名 | 板块名称 | 信号强度 | MACD值 | 柱状图 |")
            content.append("|------|----------|----------|--------|--------|")
            
            for i, signal in enumerate(sell_signals, 1):
                sector_name = signal['sector_name']
                strength = signal['signal_strength']
                macd = signal['macd']
                histogram = signal['histogram']
                content.append(f"| {i} | {sector_name} | {strength:.4f} | {macd:.4f} | {histogram:.4f} |")
        else:
            content.append("✅ 暂无卖出信号板块")
        
        content.append("")
        return content
    
    def _build_neutral_signals_section(self, neutral_signals: list) -> list:
        """
        构建中性信号板块部分（TOP10）
        
        Args:
            neutral_signals: 中性信号板块列表
            
        Returns:
            list: 中性信号板块部分内容
        """
        content = []
        content.append("### ➡️ 中性信号板块（信号强度TOP10）")
        content.append("")
        content.append(f"**总数量**: {len(neutral_signals)}个")
        content.append("")
        
        # 取前10个
        top_10_signals = neutral_signals[:10]
        
        if top_10_signals:
            content.append("| 排名 | 板块名称 | 信号强度 | MACD值 | 柱状图 |")
            content.append("|------|----------|----------|--------|--------|")
            
            for i, signal in enumerate(top_10_signals, 1):
                sector_name = signal['sector_name']
                strength = signal['signal_strength']
                macd = signal['macd']
                histogram = signal['histogram']
                content.append(f"| {i} | {sector_name} | {strength:.4f} | {macd:.4f} | {histogram:.4f} |")
        
        content.append("")
        return content
    
    def _build_macd_charts_section(self, signals: list, chart_paths: dict, section_title: str = "MACD图表") -> list:
        """
        构建MACD图表展示部分
        
        Args:
            signals: 信号板块列表（买入/卖出/中性）
            chart_paths: 图表路径字典
            section_title: 部分标题
            
        Returns:
            list: MACD图表部分内容
        """
        content = []
        content.append(f"### 📊 {section_title}MACD图表")
        content.append("")
        
        # 显示板块图表
        displayed_charts = 0
        max_charts = 6  # 最多显示6个图表
        
        for signal in signals:
            if displayed_charts >= max_charts:
                break
                
            sector_name = signal['sector_name']
            chart_path = chart_paths.get(sector_name)
            
            if chart_path:
                # 获取图表文件名
                import os
                filename = os.path.basename(chart_path)
                relative_path = f"../images/sectors/macd/{filename}"
                
                content.append(f"#### {sector_name}")
                content.append("")
                content.append(f"![{sector_name} MACD分析图]({relative_path})")
                content.append("")
                
                # 添加技术指标说明
                strength = signal['signal_strength']
                macd = signal['macd']
                histogram = signal['histogram']
                content.append(f"**技术指标**: 信号强度={strength:.4f}, MACD={macd:.4f}, 柱状图={histogram:.4f}")
                content.append("")
                
                displayed_charts += 1
        
        if displayed_charts == 0:
            content.append(f"❌ 暂无{section_title}的MACD图表")
        
        content.append("")
        return content
    
    def _build_volume_price_buy_signals_section(self, sector_results: dict, buy_signals: list) -> list:
        """构建量价分析买入信号板块表格"""
        content = []
        content.append("#### 📈 买入信号板块")
        content.append("")
        content.append(f"**信号数量**: {len(buy_signals)}个")
        content.append("")
        
        if buy_signals:
            content.append("| 排名 | 板块名称 | 量价关系 | 成交量 | 价格 |")
            content.append("|------|----------|----------|--------|------|")
            
            for i, sector_name in enumerate(buy_signals, 1):
                sector_data = sector_results.get(sector_name, {})
                relationship = sector_data.get('latest_relationship', '未知')
                volume_change = sector_data.get('volume_change_pct', 0)
                price_change = sector_data.get('price_change_pct', 0)
                content.append(f"| {i} | {sector_name} | {relationship} | {volume_change:.2f}% | {price_change:.2f}% |")
        
        content.append("")
        return content
    
    def _build_volume_price_sell_signals_section(self, sector_results: dict, sell_signals: list) -> list:
        """构建量价分析卖出信号板块表格"""
        content = []
        content.append("#### 📉 卖出信号板块")
        content.append("")
        content.append(f"**信号数量**: {len(sell_signals)}个")
        content.append("")
        
        if sell_signals:
            content.append("| 排名 | 板块名称 | 量价关系 | 成交量 | 价格 |")
            content.append("|------|----------|----------|--------|------|")
            
            for i, sector_name in enumerate(sell_signals, 1):
                sector_data = sector_results.get(sector_name, {})
                relationship = sector_data.get('latest_relationship', '未知')
                volume_change = sector_data.get('volume_change_pct', 0)
                price_change = sector_data.get('price_change_pct', 0)
                content.append(f"| {i} | {sector_name} | {relationship} | {volume_change:.2f}% | {price_change:.2f}% |")
        else:
            content.append("✅ 暂无卖出信号板块")
        
        content.append("")
        return content
    
    def _build_volume_price_neutral_signals_section(self, sector_results: dict, neutral_signals: list) -> list:
        """构建量价分析中性信号板块表格（TOP10）"""
        content = []
        content.append("#### ➡️ 中性信号板块（TOP10）")
        content.append("")
        content.append(f"**总数量**: {len(neutral_signals)}个")
        content.append("")
        
        top_10_signals = neutral_signals[:10]
        
        if top_10_signals:
            content.append("| 排名 | 板块名称 | 量价关系 | 成交量 | 价格 |")
            content.append("|------|----------|----------|--------|------|")
            
            for i, sector_name in enumerate(top_10_signals, 1):
                sector_data = sector_results.get(sector_name, {})
                relationship = sector_data.get('latest_relationship', '未知')
                volume_change = sector_data.get('volume_change_pct', 0)
                price_change = sector_data.get('price_change_pct', 0)
                content.append(f"| {i} | {sector_name} | {relationship} | {volume_change:.2f}% | {price_change:.2f}% |")
        
        content.append("")
        return content
    
    def _build_volume_price_charts_section(self, signals: list, chart_paths: dict, section_title: str) -> list:
        """构建量价关系趋势图展示部分"""
        content = []
        content.append(f"### 📊 {section_title}量价关系趋势图")
        content.append("")
        
        displayed_charts = 0
        max_charts = 6
        
        for sector_name in signals:
            if displayed_charts >= max_charts:
                break
            
            chart_path = chart_paths.get(sector_name)
            if chart_path:
                import os
                filename = os.path.basename(chart_path)
                relative_path = f"../images/sectors/volume_price/{filename}"
                
                content.append(f"#### {sector_name}")
                content.append("")
                content.append(f"![{sector_name} 量价关系趋势图]({relative_path})")
                content.append("")
                displayed_charts += 1
        
        if displayed_charts == 0:
            content.append(f"❌ 暂无{section_title}的量价关系趋势图")
        
        content.append("")
        return content
    
    def _build_macd_buy_signals_section(self, buy_signals: list, all_sectors: dict) -> list:
        """构建MACD分析买入信号板块表格"""
        content = []
        content.append("#### 📈 买入信号板块")
        content.append("")
        content.append(f"**信号数量**: {len(buy_signals)}个")
        content.append("")
        
        if buy_signals:
            content.append("| 排名 | 板块名称 | MACD值 | 柱状图 | 信号强度 |")
            content.append("|------|----------|--------|--------|----------|")
            
            for i, sector_name in enumerate(buy_signals, 1):
                sector_data = all_sectors.get(sector_name, {})
                macd_value = sector_data.get('latest_macd', 0)
                histogram = sector_data.get('latest_histogram', 0)
                strength = sector_data.get('signal_strength', 0)
                content.append(f"| {i} | {sector_name} | {macd_value:.4f} | {histogram:.4f} | {strength:.4f} |")
        
        content.append("")
        return content
    
    def _build_macd_sell_signals_section(self, sell_signals: list, all_sectors: dict) -> list:
        """构建MACD分析卖出信号板块表格"""
        content = []
        content.append("#### 📉 卖出信号板块")
        content.append("")
        content.append(f"**信号数量**: {len(sell_signals)}个")
        content.append("")
        
        if sell_signals:
            content.append("| 排名 | 板块名称 | MACD值 | 柱状图 | 信号强度 |")
            content.append("|------|----------|--------|--------|----------|")
            
            for i, sector_name in enumerate(sell_signals, 1):
                sector_data = all_sectors.get(sector_name, {})
                macd_value = sector_data.get('latest_macd', 0)
                histogram = sector_data.get('latest_histogram', 0)
                strength = sector_data.get('signal_strength', 0)
                content.append(f"| {i} | {sector_name} | {macd_value:.4f} | {histogram:.4f} | {strength:.4f} |")
        else:
            content.append("✅ 暂无卖出信号板块")
        
        content.append("")
        return content
    
    def _build_macd_neutral_signals_section(self, neutral_signals: list, all_sectors: dict) -> list:
        """构建MACD分析中性信号板块表格（TOP10）"""
        content = []
        content.append("#### ➡️ 中性信号板块（TOP10）")
        content.append("")
        content.append(f"**总数量**: {len(neutral_signals)}个")
        content.append("")
        
        top_10_signals = neutral_signals[:10]
        
        if top_10_signals:
            content.append("| 排名 | 板块名称 | MACD值 | 柱状图 | 信号强度 |")
            content.append("|------|----------|--------|--------|----------|")
            
            for i, sector_name in enumerate(top_10_signals, 1):
                sector_data = all_sectors.get(sector_name, {})
                macd_value = sector_data.get('latest_macd', 0)
                histogram = sector_data.get('latest_histogram', 0)
                strength = sector_data.get('signal_strength', 0)
                content.append(f"| {i} | {sector_name} | {macd_value:.4f} | {histogram:.4f} | {strength:.4f} |")
        
        content.append("")
        return content
    
    def _build_macd_charts_section_for_sectors(self, signals: list, chart_paths: dict, section_title: str) -> list:
        """构建MACD图表展示部分（针对板块列表）"""
        content = []
        content.append(f"### 📊 {section_title}MACD图表")
        content.append("")
        
        displayed_charts = 0
        max_charts = 6
        
        for sector_name in signals:
            if displayed_charts >= max_charts:
                break
            
            chart_path = chart_paths.get(sector_name)
            if chart_path:
                import os
                filename = os.path.basename(chart_path)
                relative_path = f"../images/sectors/macd/{filename}"
                
                content.append(f"#### {sector_name}")
                content.append("")
                content.append(f"![{sector_name} MACD分析图]({relative_path})")
                content.append("")
                displayed_charts += 1
        
        if displayed_charts == 0:
            content.append(f"❌ 暂无{section_title}的MACD图表")
        
        content.append("")
        return content
