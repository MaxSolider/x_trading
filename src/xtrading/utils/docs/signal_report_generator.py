"""
信号报告生成器
负责将信号数据汇总生成markdown格式的总结报告
"""

import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from ...static.sector_strategy_params import StrategyParams


class SignalReportGenerator:
    """板块信号报告生成器类"""
    
    def __init__(self):
        """初始化报告生成器"""
        self.report_dir = "reports/sector_signals"
        os.makedirs(self.report_dir, exist_ok=True)
    
    def generate_precomputed_report(self, sections: Dict[str, Any], output_file: str = None) -> Optional[str]:
        """
        使用预计算数据生成信号报告（仅负责文档拼接，不做任何统计计算）
        
        Args:
            sections: 预先聚合好的各报告部分数据
            output_file: 输出文件路径，默认为自动生成
            
        Returns:
            Optional[str]: 生成的报告文件路径
        """
        if not sections:
            print("❌ 无预计算数据可生成报告")
            return None
        
        # 生成文件名
        if output_file is None:
            now = datetime.now()
            date_str = now.strftime('%Y%m%d')
            time_str = now.strftime('%H%M%S')
            output_file = os.path.join(self.report_dir, f"板块信号报告_{date_str}_{time_str}.md")
        
        # 生成报告内容（严格基于入参拼接）
        content = []
        content.append("# 板块信号综合分析报告")
        content.append("")
        content.append("> 本报告包含板块信号分析报告和汇总报告两部分内容")
        content.append("")
        
        # 目录
        content.extend(self._generate_table_of_contents())
        
        # 汇总报告
        content.append("# 📊 汇总报告")
        content.append("")
        content.extend(self._render_basic_info(sections.get('meta', {})))
        content.extend(self._render_overall_summary(sections.get('overall_summary', {})))
        content.extend(self._render_strategy_distribution(sections.get('strategy_distribution', {})))
        content.extend(self._render_category_analysis(sections.get('category_analysis', {})))
        content.append("---")
        content.append("")
        
        # 详细分析
        content.append("# 📈 详细分析报告")
        content.append("")
        content.extend(self._render_sector_details(sections.get('sector_details', {})))
        content.extend(self._render_appendix(sections.get('appendix', {})))
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("\n".join(content))
            print(f"✅ 综合信号报告已生成: {output_file}")
            return output_file
        except Exception as e:
            print(f"❌ 生成报告文件失败: {e}")
            return None

    def _generate_table_of_contents(self) -> List[str]:
        """生成目录"""
        content = []
        
        content.append("## 📋 目录")
        content.append("")
        content.append("### 📊 汇总报告")
        content.append("- [基本信息](#基本信息)")
        content.append("- [整体汇总](#整体汇总)")
        content.append("- [策略信号分布](#策略信号分布)")
        content.append("- [板块分类分析](#板块分类分析)")
        content.append("")
        content.append("### 📈 详细分析报告")
        content.append("- [板块明细](#板块明细)")
        content.append("- [附录：板块分类信息](#附录板块分类信息)")
        content.append("")
        content.append("---")
        content.append("")
        
        return content

    def _render_basic_info(self, meta: Dict[str, Any]) -> List[str]:
        """根据预计算的meta信息渲染基本信息（仅拼接）"""
        content = []
        content.append("## 📋 基本信息")
        content.append("")
        content.append(f"- **计算时间**: {meta.get('calculation_time', 'Unknown')}")
        content.append(f"- **板块数量**: {meta.get('total_sectors', 0)}")
        strategies_used = meta.get('strategies_used', [])
        content.append(f"- **使用策略**: {', '.join(strategies_used)}")
        date_range = meta.get('date_range', {})
        if date_range:
            content.append(f"- **分析期间**: {date_range.get('start_date', '')} 至 {date_range.get('end_date', '')}")
        content.append("")
        return content

    def _render_overall_summary(self, summary: Dict[str, Any]) -> List[str]:
        """根据预计算的整体汇总数据渲染（仅拼接）"""
        content = []
        content.append("## 📈 整体汇总")
        content.append("")
        successful_sectors = summary.get('successful_sectors', 0)
        failed_sectors = summary.get('failed_sectors', 0)
        total_signals = summary.get('total_signals', {'买入': 0, '卖出': 0, '持有': 0, '强势买入': 0, '强势卖出': 0, '错误': 0})
        content.append("| 分类 | 数量 |")
        content.append("|------|------|")
        content.append(f"| 成功分析板块 | {successful_sectors} |")
        content.append(f"| 失败板块 | {failed_sectors} |")
        content.append(f"| 买入信号 | {total_signals.get('买入', 0)} |")
        content.append(f"| 卖出信号 | {total_signals.get('卖出', 0)} |")
        content.append(f"| 持有信号 | {total_signals.get('持有', 0)} |")
        content.append(f"| 强势买入 | {total_signals.get('强势买入', 0)} |")
        content.append(f"| 强势卖出 | {total_signals.get('强势卖出', 0)} |")
        content.append(f"| 错误信号 | {total_signals.get('错误', 0)} |")
        content.append("")
        return content

    def _render_strategy_distribution(self, data: Dict[str, Any]) -> List[str]:
        """根据预计算的策略信号分布渲染（仅拼接）"""
        content = []
        content.append("## 📊 策略信号分布")
        content.append("")
        strategies_used = data.get('strategies_used', [])
        strategy_signal_counts = data.get('strategy_signal_counts', {})
        content.append("| 信号类型 | " + " | ".join(strategies_used) + " |")
        content.append("|----------|" + "|".join(["------"] * len(strategies_used)) + "|")
        for signal_type in ['买入', '卖出', '持有', '强势买入', '强势卖出', '错误']:
            row = [signal_type]
            for strategy in strategies_used:
                row.append(str(strategy_signal_counts.get(strategy, {}).get(signal_type, 0)))
            content.append("| " + " | ".join(row) + " |")
        content.append("")
        return content

    def _render_sector_details(self, data: Dict[str, Any]) -> List[str]:
        """根据预计算的板块明细渲染（仅拼接）"""
        content = []
        content.append("## 🏢 板块明细")
        content.append("")
        strategies_used = data.get('strategies_used', [])
        rows = data.get('rows', [])
        content.append("| 板块名称 | 分类 | " + " | ".join(strategies_used) + " |")
        content.append("|----------|------|" + "|".join(["------"] * len(strategies_used)) + "|")
        for row in rows:
            sector_name = row.get('sector_name', '-')
            category = row.get('category', '-')
            values = [sector_name, category]
            signals = row.get('signals', {})
            for strategy in strategies_used:
                values.append(signals.get(strategy, '-'))
            content.append("| " + " | ".join(values) + " |")
        content.append("")
        return content

    def _render_category_analysis(self, data: Dict[str, Any]) -> List[str]:
        """根据预计算的分类分析渲染（仅拼接）"""
        content = []
        content.append("## 🏷️ 板块分类分析")
        content.append("")
        strategies_used = data.get('strategies_used', [])
        categories = data.get('categories', {})
        if categories:
            content.append("### 📊 分类信号统计")
            content.append("")
            header = ["分类", "板块数量"]
            for strategy in strategies_used:
                header.extend([f"{strategy}-买入", f"{strategy}-卖出"])
            content.append("| " + " | ".join(header) + " |")
            content.append("|" + "|".join(["------"] * len(header)) + "|")
            
            # 按买入卖出信号总量降序排序
            sorted_categories = sorted(categories.items(), key=lambda x: x[1].get('total_buy_sell_signals', 0), reverse=True)
            
            for category, stats in sorted_categories:
                row = [category, str(len(stats.get('sectors', [])))]
                strategy_signals = stats.get('strategy_signals', {})
                for strategy in strategies_used:
                    buy_count = strategy_signals.get(strategy, {}).get('买入', 0)
                    sell_count = strategy_signals.get(strategy, {}).get('卖出', 0)
                    row.extend([str(buy_count), str(sell_count)])
                content.append("| " + " | ".join(row) + " |")
            content.append("")
        else:
            content.append("暂无板块分类数据")
            content.append("")
        return content

    def _render_appendix(self, data: Dict[str, Any]) -> List[str]:
        """根据预计算的数据渲染附录（仅拼接）"""
        content = []
        content.append("## 📋 附录：板块分类信息")
        content.append("")
        category_sectors = data.get('category_sectors', {})
        if category_sectors:
            content.append("| 分类 | 板块数量 | 包含板块 |")
            content.append("|------|----------|----------|")
            for category, sectors in category_sectors.items():
                content.append(f"| {category} | {len(sectors)} | {', '.join(sectors)} |")
            content.append("")
        else:
            content.append("暂无板块分类数据")
            content.append("")
        return content