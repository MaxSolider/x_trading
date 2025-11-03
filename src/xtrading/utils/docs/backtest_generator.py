"""
回测报告生成器
负责生成回测报告的Markdown内容
"""

import os
from typing import Dict, Any, Optional
from datetime import datetime


class BacktestReportGenerator:
    """回测报告生成器类"""
    
    def __init__(self):
        """初始化回测报告生成器"""
        pass
    
    def generate_backtest_report(self, results: Dict[str, Any], output_dir: str) -> Optional[str]:
        """
        生成回测报告
        
        Args:
            results: 回测结果字典，包含sector_results、stock_results和summary
            output_dir: 输出目录
            
        Returns:
            str: 生成的报告文件路径，如果失败返回None
        """
        try:
            # 生成报告内容
            content = self._build_report_content(results)
            
            # 保存报告 - 使用日期格式 YYYYMMDD
            today = datetime.now().strftime('%Y%m%d')
            report_filename = f"回测报告_{today}.md"
            report_path = os.path.join(output_dir, report_filename)
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return report_path
            
        except Exception as e:
            print(f"❌ 生成回测报告失败: {e}")
            return None
    
    def _build_report_content(self, results: Dict[str, Any]) -> str:
        """
        构建报告内容
        
        Args:
            results: 回测结果字典
            
        Returns:
            str: 报告内容
        """
        try:
            content = []
            
            # 报告标题
            content.append("# 回测报告")
            content.append("")
            content.append(f"**生成时间**: {results.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}")
            content.append("")
            
            # 目录
            content.extend(self._build_table_of_contents())
            content.append("")
            
            # 汇总统计部分
            content.extend(self._build_summary_section(results.get('summary', {})))
            
            # 板块回测结果部分
            content.extend(self._build_sector_results_section(results.get('sector_results', [])))
            
            # 股票回测结果部分
            content.extend(self._build_stock_results_section(results.get('stock_results', [])))
            
            # 风险提示
            content.extend(self._build_risk_warning_section())
            
            return "\n".join(content)
            
        except Exception as e:
            print(f"❌ 构建报告内容失败: {e}")
            return f"# 回测报告\n\n❌ 报告生成失败: {str(e)}"
    
    def _build_table_of_contents(self) -> list:
        """构建目录"""
        content = []
        content.append("## 📑 目录")
        content.append("")
        content.append("- [汇总统计](#汇总统计)")
        content.append("  - [总体统计](#总体统计)")
        content.append("  - [按策略类型统计](#按策略类型统计)")
        content.append("- [板块回测结果](#板块回测结果)")
        content.append("- [股票回测结果](#股票回测结果)")
        content.append("- [风险提示](#风险提示)")
        return content
    
    def _build_summary_section(self, summary: Dict[str, Any]) -> list:
        """
        构建汇总统计部分
        
        Args:
            summary: 汇总统计数据
            
        Returns:
            list: 汇总统计部分内容
        """
        content = []
        content.append("## 📊 汇总统计")
        content.append("")
        
        # 总体统计
        total_sectors = summary.get('total_sectors', 0)
        total_stocks = summary.get('total_stocks', 0)
        successful_sectors = summary.get('successful_sectors', 0)
        successful_stocks = summary.get('successful_stocks', 0)
        
        content.append("### 总体统计")
        content.append("")
        content.append(f"- **板块回测总数**: {total_sectors}")
        content.append(f"- **板块回测成功数**: {successful_sectors}")
        content.append(f"- **板块回测成功率**: {round(successful_sectors / total_sectors * 100, 2) if total_sectors > 0 else 0}%")
        content.append("")
        content.append(f"- **股票回测总数**: {total_stocks}")
        content.append(f"- **股票回测成功数**: {successful_stocks}")
        content.append(f"- **股票回测成功率**: {round(successful_stocks / total_stocks * 100, 2) if total_stocks > 0 else 0}%")
        content.append("")
        
        # 板块统计（总体）
        sector_stats = summary.get('sector_stats', {})
        if sector_stats:
            content.extend(self._build_stats_table('板块', sector_stats))
        
        # 股票统计（总体）
        stock_stats = summary.get('stock_stats', {})
        if stock_stats:
            content.extend(self._build_stats_table('股票', stock_stats))
        
        # 按策略类型统计
        content.append("### 按策略类型统计")
        content.append("")
        
        # 板块按策略类型统计
        sector_stats_by_strategy = summary.get('sector_stats_by_strategy', {})
        if sector_stats_by_strategy:
            content.append("#### 板块按策略类型统计")
            content.append("")
            for strategy_type, stats in sector_stats_by_strategy.items():
                content.append(f"##### {strategy_type}")
                content.append("")
                content.extend(self._build_stats_table('', stats, show_title=False))
                content.append("")
        
        # 股票按策略类型统计
        stock_stats_by_strategy = summary.get('stock_stats_by_strategy', {})
        if stock_stats_by_strategy:
            content.append("#### 股票按策略类型统计")
            content.append("")
            for strategy_type, stats in stock_stats_by_strategy.items():
                content.append(f"##### {strategy_type}")
                content.append("")
                content.extend(self._build_stats_table('', stats, show_title=False))
                content.append("")
        
        return content
    
    def _build_stats_table(self, name: str, stats: Dict[str, Any], show_title: bool = True) -> list:
        """
        构建统计表格
        
        Args:
            name: 统计对象名称（板块/股票）
            stats: 统计数据字典
            show_title: 是否显示标题
            
        Returns:
            list: 统计表格内容
        """
        content = []
        if show_title and name:
            content.append(f"### {name}收益率统计")
            content.append("")
        
        # 指标名称映射
        metric_names = {
            'next_day_return': '次日涨跌幅',
            'day2_return': '2日累计涨跌幅',
            'day5_return': '5日累计涨跌幅',
            'total_return': '至今累计涨跌幅',
            'max_return': '最高累计涨跌幅'
        }
        
        # 创建表格
        content.append(f"| 指标 | 样本数 | 平均收益率 | 最大收益率 | 最小收益率 | 上涨数 | 下跌数 | 上涨率 |")
        content.append(f"|------|--------|------------|------------|------------|--------|--------|--------|")
        
        for metric_key, metric_name in metric_names.items():
            if metric_key in stats:
                stat = stats[metric_key]
                avg = stat.get('avg', 0)
                max_val = stat.get('max', 0)
                min_val = stat.get('min', 0)
                positive = stat.get('positive', 0)
                negative = stat.get('negative', 0)
                positive_rate = stat.get('positive_rate', 0)
                count = stat.get('count', 0)
                
                content.append(
                    f"| {metric_name} | {count} | {avg:.2f}% | {max_val:.2f}% | {min_val:.2f}% | "
                    f"{positive} | {negative} | {positive_rate:.2f}% |"
                )
        
        content.append("")
        return content
    
    def _build_sector_results_section(self, sector_results: list) -> list:
        """
        构建板块回测结果部分
        
        Args:
            sector_results: 板块回测结果列表
            
        Returns:
            list: 板块回测结果部分内容
        """
        content = []
        content.append("## 📈 板块回测结果")
        content.append("")
        
        if not sector_results:
            content.append("暂无板块回测数据")
            content.append("")
            return content
        
        # 按状态分类
        successful = [r for r in sector_results if r.get('status') == 'success']
        failed = [r for r in sector_results if r.get('status') != 'success']
        
        # 成功回测结果按推荐原因分组
        if successful:
            # 按推荐原因分组
            results_by_reason = {}
            for result in successful:
                reason = result.get('reason', '未分类')
                if reason not in results_by_reason:
                    results_by_reason[reason] = []
                results_by_reason[reason].append(result)
            
            # 为每个推荐原因创建单独的表格
            for reason, reason_results in sorted(results_by_reason.items()):
                content.append(f"### {reason} ({len(reason_results)}条)")
                content.append("")
                content.extend(self._build_sector_table(reason_results))
                content.append("")
        
        if failed:
            content.append(f"### 失败回测 ({len(failed)})")
            content.append("")
            content.extend(self._build_failed_table(failed, 'sector'))
            content.append("")
        
        return content
    
    def _build_stock_results_section(self, stock_results: list) -> list:
        """
        构建股票回测结果部分
        
        Args:
            stock_results: 股票回测结果列表
            
        Returns:
            list: 股票回测结果部分内容
        """
        content = []
        content.append("## 📊 股票回测结果")
        content.append("")
        
        if not stock_results:
            content.append("暂无股票回测数据")
            content.append("")
            return content
        
        # 按状态分类
        successful = [r for r in stock_results if r.get('status') == 'success']
        failed = [r for r in stock_results if r.get('status') != 'success']
        
        # 成功回测结果按推荐原因分组
        if successful:
            # 按推荐原因分组
            results_by_reason = {}
            for result in successful:
                reason = result.get('reason', '未分类')
                if reason not in results_by_reason:
                    results_by_reason[reason] = []
                results_by_reason[reason].append(result)
            
            # 为每个推荐原因创建单独的表格
            for reason, reason_results in sorted(results_by_reason.items()):
                content.append(f"### {reason} ({len(reason_results)}条)")
                content.append("")
                content.extend(self._build_stock_table(reason_results))
                content.append("")
        
        if failed:
            content.append(f"### 失败回测 ({len(failed)})")
            content.append("")
            content.extend(self._build_failed_table(failed, 'stock'))
            content.append("")
        
        return content
    
    def _build_sector_table(self, results: list) -> list:
        """
        构建板块结果表格
        
        Args:
            results: 板块回测结果列表
            
        Returns:
            list: 表格内容
        """
        content = []
        content.append("| 板块名称 | 推荐日期 | 推荐原因 | 次日涨跌幅 | 2日涨跌幅 | 5日涨跌幅 | 至今涨跌幅 | 最高涨跌幅 | 最高涨跌幅日期 |")
        content.append("|----------|----------|----------|------------|-----------|-----------|------------|------------|----------------|")
        
        for result in results:
            sector_name = result.get('sector_name', '')
            recommend_date = result.get('recommend_date', '')
            reason = result.get('reason', '')
            next_day = self._format_return(result.get('next_day_return'))
            day2 = self._format_return(result.get('day2_return'))
            day5 = self._format_return(result.get('day5_return'))
            total = self._format_return(result.get('total_return'))
            max_return = self._format_return(result.get('max_return'))
            max_date = result.get('max_return_date', '')
            
            content.append(
                f"| {sector_name} | {recommend_date} | {reason} | {next_day} | {day2} | {day5} | "
                f"{total} | {max_return} | {max_date} |"
            )
        
        return content
    
    def _build_stock_table(self, results: list) -> list:
        """
        构建股票结果表格
        
        Args:
            results: 股票回测结果列表
            
        Returns:
            list: 表格内容
        """
        content = []
        content.append("| 股票名称 | 股票代码 | 推荐日期 | 推荐原因 | 次日涨跌幅 | 2日涨跌幅 | 5日涨跌幅 | 至今涨跌幅 | 最高涨跌幅 | 最高涨跌幅日期 |")
        content.append("|----------|----------|----------|----------|------------|-----------|-----------|------------|------------|----------------|")
        
        for result in results:
            stock_name = result.get('stock_name', '')
            stock_code = result.get('stock_code', '')
            recommend_date = result.get('recommend_date', '')
            reason = result.get('reason', '')
            next_day = self._format_return(result.get('next_day_return'))
            day2 = self._format_return(result.get('day2_return'))
            day5 = self._format_return(result.get('day5_return'))
            total = self._format_return(result.get('total_return'))
            max_return = self._format_return(result.get('max_return'))
            max_date = result.get('max_return_date', '')
            
            content.append(
                f"| {stock_name} | {stock_code} | {recommend_date} | {reason} | {next_day} | {day2} | {day5} | "
                f"{total} | {max_return} | {max_date} |"
            )
        
        return content
    
    def _build_failed_table(self, results: list, type: str) -> list:
        """
        构建失败结果表格
        
        Args:
            results: 失败回测结果列表
            type: 类型（'sector' 或 'stock'）
            
        Returns:
            list: 表格内容
        """
        content = []
        if type == 'sector':
            content.append("| 板块名称 | 推荐日期 | 错误信息 |")
            content.append("|----------|----------|----------|")
            for result in results:
                sector_name = result.get('sector_name', '')
                recommend_date = result.get('recommend_date', '')
                error = result.get('error', '未知错误')
                content.append(f"| {sector_name} | {recommend_date} | {error} |")
        else:
            content.append("| 股票名称 | 推荐日期 | 错误信息 |")
            content.append("|----------|----------|----------|")
            for result in results:
                stock_name = result.get('stock_name', '')
                recommend_date = result.get('recommend_date', '')
                error = result.get('error', '未知错误')
                content.append(f"| {stock_name} | {recommend_date} | {error} |")
        
        return content
    
    def _format_return(self, value: Optional[float]) -> str:
        """
        格式化收益率
        
        Args:
            value: 收益率值
            
        Returns:
            str: 格式化后的字符串
        """
        if value is None:
            return '-'
        return f"{value:.2f}%"
    
    def _build_risk_warning_section(self) -> list:
        """构建风险提示部分"""
        content = []
        content.append("## ⚠️ 风险提示")
        content.append("")
        content.append("1. **历史回测结果不代表未来表现**：本报告基于历史数据回测，市场环境变化可能导致未来表现与历史回测结果存在差异。")
        content.append("")
        content.append("2. **数据准确性**：回测结果依赖于数据质量和完整性，数据缺失或错误可能影响回测结果的准确性。")
        content.append("")
        content.append("3. **交易成本未考虑**：回测结果未考虑实际交易中的手续费、印花税等交易成本，实际收益可能低于回测结果。")
        content.append("")
        content.append("4. **市场风险**：投资有风险，入市需谨慎。本报告仅供参考，不构成投资建议。")
        content.append("")
        content.append("5. **策略局限性**：不同策略在不同市场环境下的表现可能存在差异，单一策略可能无法适应所有市场情况。")
        content.append("")
        return content

