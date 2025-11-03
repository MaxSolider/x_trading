"""
回测服务类
提供板块和股票的回测服务，支持并行执行
"""

import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from ..strategies.industry_sector.backtest import SectorBacktest
from ..strategies.individual_stock.backtest import StockBacktest
from ..utils.docs.backtest_generator import BacktestReportGenerator


def _get_project_root() -> str:
    """
    获取项目根目录
    
    Returns:
        str: 项目根目录路径
    """
    # 从当前文件位置向上查找，直到找到包含 reports 目录或 pyproject.toml 的目录
    current_path = os.path.abspath(__file__)
    while True:
        parent = os.path.dirname(current_path)
        if parent == current_path:  # 到达文件系统根目录
            break
        # 检查是否包含 reports 目录或 pyproject.toml
        if os.path.exists(os.path.join(parent, 'reports')) or os.path.exists(os.path.join(parent, 'pyproject.toml')):
            return parent
        current_path = parent
    # 如果找不到，返回当前工作目录
    return os.getcwd()


class BacktestService:
    """回测服务类"""
    
    def __init__(self):
        """初始化回测服务"""
        self.sector_backtest = SectorBacktest()
        self.stock_backtest = StockBacktest()
        self.report_generator = BacktestReportGenerator()
        print("✅ 回测服务初始化成功")
    
    def run_backtest(self, days: int = 30, 
                     sectors_csv_path: str = None,
                     stocks_csv_path: str = None,
                     parallel: bool = True,
                     max_workers: int = 4) -> Dict[str, Any]:
        """
        执行完整的回测流程
        
        Args:
            days: 获取最近N天的推荐数据，默认30天
            sectors_csv_path: 板块推荐CSV文件路径
            stocks_csv_path: 股票推荐CSV文件路径
            parallel: 是否并行执行板块和股票回测，默认True
            max_workers: 并行执行的最大工作线程数，默认4
            
        Returns:
            Dict: 包含板块和股票回测结果的字典
        """
        try:
            print(f"\n{'='*60}")
            print(f"🚀 开始回测流程（最近{days}天）")
            print(f"{'='*60}\n")
            
            results = {
                'sector_results': [],
                'stock_results': [],
                'summary': {},
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            if parallel:
                # 并行执行板块和股票回测
                print("📊 并行执行板块和股票回测...\n")
                
                with ThreadPoolExecutor(max_workers=2) as executor:
                    # 提交任务
                    sector_future = executor.submit(
                        self.sector_backtest.backtest_all,
                        days=days,
                        csv_path=sectors_csv_path
                    )
                    stock_future = executor.submit(
                        self.stock_backtest.backtest_all,
                        days=days,
                        csv_path=stocks_csv_path
                    )
                    
                    # 获取结果
                    try:
                        results['sector_results'] = sector_future.result(timeout=3600)  # 1小时超时
                        print(f"\n✅ 板块回测完成，共 {len(results['sector_results'])} 条记录")
                    except Exception as e:
                        print(f"\n❌ 板块回测失败: {e}")
                        results['sector_results'] = []
                    
                    try:
                        results['stock_results'] = stock_future.result(timeout=3600)  # 1小时超时
                        print(f"\n✅ 股票回测完成，共 {len(results['stock_results'])} 条记录")
                    except Exception as e:
                        print(f"\n❌ 股票回测失败: {e}")
                        results['stock_results'] = []
            else:
                # 串行执行
                print("📊 串行执行板块和股票回测...\n")
                
                # 执行板块回测
                print("=" * 60)
                print("板块回测")
                print("=" * 60)
                results['sector_results'] = self.sector_backtest.backtest_all(
                    days=days,
                    csv_path=sectors_csv_path
                )
                
                # 执行股票回测
                print("\n" + "=" * 60)
                print("股票回测")
                print("=" * 60)
                results['stock_results'] = self.stock_backtest.backtest_all(
                    days=days,
                    csv_path=stocks_csv_path
                )
            
            # 汇总回测数据
            results['summary'] = self._summarize_results(results['sector_results'], results['stock_results'])
            
            print(f"\n{'='*60}")
            print("✅ 回测流程完成")
            print(f"{'='*60}\n")
            
            return results
            
        except Exception as e:
            print(f"❌ 回测流程执行失败: {e}")
            return {
                'sector_results': [],
                'stock_results': [],
                'summary': {},
                'error': str(e),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
    
    def _extract_strategy_type(self, reason: str) -> str:
        """
        从推荐原因中提取策略类型
        
        板块策略包括：MACD策略、量价策略、量价策略 + MACD策略
        股票策略包括：趋势追踪策略、超跌反弹策略
        
        Args:
            reason: 推荐原因字符串
            
        Returns:
            str: 策略类型
        """
        if not reason:
            return '其他'
        
        # 板块策略（优先级：组合策略 > 单个策略）
        if '量价策略' in reason and 'MACD策略' in reason:
            return '量价策略 + MACD策略'
        elif '量价策略' in reason:
            return '量价策略'
        elif 'MACD策略' in reason:
            return 'MACD策略'
        
        # 股票策略
        elif '趋势追踪策略' in reason:
            return '趋势追踪策略'
        elif '超跌反弹策略' in reason:
            return '超跌反弹策略'
        else:
            return '其他'
    
    def _calculate_stats_by_strategy(self, results: List[Dict]) -> Dict[str, Dict[str, Any]]:
        """
        按策略类型计算统计数据
        
        Args:
            results: 回测结果列表
            
        Returns:
            Dict: 按策略类型分组的统计数据
        """
        strategy_stats = {}
        
        # 按策略类型分组
        strategy_groups = {}
        for result in results:
            if result.get('status') != 'success':
                continue
            
            strategy_type = self._extract_strategy_type(result.get('reason', ''))
            if strategy_type not in strategy_groups:
                strategy_groups[strategy_type] = []
            strategy_groups[strategy_type].append(result)
        
        # 对每个策略类型计算统计值
        for strategy_type, group_results in strategy_groups.items():
            strategy_stats[strategy_type] = {}
            
            for metric in ['next_day_return', 'day2_return', 'day5_return', 'total_return', 'max_return']:
                values = [r.get(metric) for r in group_results if r.get(metric) is not None]
                if values:
                    strategy_stats[strategy_type][metric] = {
                        'count': len(values),
                        'avg': round(sum(values) / len(values), 2),
                        'max': round(max(values), 2),
                        'min': round(min(values), 2),
                        'positive': len([v for v in values if v > 0]),
                        'negative': len([v for v in values if v < 0]),
                        'positive_rate': round(len([v for v in values if v > 0]) / len(values) * 100, 2)
                    }
        
        return strategy_stats
    
    def _summarize_results(self, sector_results: List[Dict], stock_results: List[Dict]) -> Dict[str, Any]:
        """
        汇总回测结果数据
        
        Args:
            sector_results: 板块回测结果列表
            stock_results: 股票回测结果列表
            
        Returns:
            Dict: 汇总统计数据
        """
        try:
            summary = {
                'sector_stats': {},
                'stock_stats': {},
                'sector_stats_by_strategy': {},
                'stock_stats_by_strategy': {},
                'total_sectors': len(sector_results),
                'total_stocks': len(stock_results),
                'successful_sectors': 0,
                'successful_stocks': 0
            }
            
            # 统计板块数据（总体）
            if sector_results:
                successful_sectors = [r for r in sector_results if r.get('status') == 'success']
                summary['successful_sectors'] = len(successful_sectors)
                
                if successful_sectors:
                    # 计算各种指标的统计值
                    for metric in ['next_day_return', 'day2_return', 'day5_return', 'total_return', 'max_return']:
                        values = [r.get(metric) for r in successful_sectors if r.get(metric) is not None]
                        if values:
                            summary['sector_stats'][metric] = {
                                'count': len(values),
                                'avg': round(sum(values) / len(values), 2),
                                'max': round(max(values), 2),
                                'min': round(min(values), 2),
                                'positive': len([v for v in values if v > 0]),
                                'negative': len([v for v in values if v < 0]),
                                'positive_rate': round(len([v for v in values if v > 0]) / len(values) * 100, 2)
                            }
                    
                    # 按策略类型统计
                    summary['sector_stats_by_strategy'] = self._calculate_stats_by_strategy(successful_sectors)
            
            # 统计股票数据（总体）
            if stock_results:
                successful_stocks = [r for r in stock_results if r.get('status') == 'success']
                summary['successful_stocks'] = len(successful_stocks)
                
                if successful_stocks:
                    # 计算各种指标的统计值
                    for metric in ['next_day_return', 'day2_return', 'day5_return', 'total_return', 'max_return']:
                        values = [r.get(metric) for r in successful_stocks if r.get(metric) is not None]
                        if values:
                            summary['stock_stats'][metric] = {
                                'count': len(values),
                                'avg': round(sum(values) / len(values), 2),
                                'max': round(max(values), 2),
                                'min': round(min(values), 2),
                                'positive': len([v for v in values if v > 0]),
                                'negative': len([v for v in values if v < 0]),
                                'positive_rate': round(len([v for v in values if v > 0]) / len(values) * 100, 2)
                            }
                    
                    # 按策略类型统计
                    summary['stock_stats_by_strategy'] = self._calculate_stats_by_strategy(successful_stocks)
            
            return summary
            
        except Exception as e:
            print(f"❌ 汇总回测结果失败: {e}")
            return {}
    
    def generate_report(self, results: Dict[str, Any], output_dir: str = None) -> Optional[str]:
        """
        生成回测报告
        
        Args:
            results: 回测结果字典
            output_dir: 输出目录，默认为reports/backtest/
            
        Returns:
            str: 生成的报告文件路径，如果失败返回None
        """
        try:
            if output_dir is None:
                # 获取项目根目录
                project_root = _get_project_root()
                output_dir = os.path.join(project_root, 'reports', 'backtest')
            
            # 创建输出目录
            os.makedirs(output_dir, exist_ok=True)
            
            # 生成报告
            report_path = self.report_generator.generate_backtest_report(results, output_dir)
            
            if report_path:
                print(f"\n✅ 回测报告已生成: {report_path}")
                return report_path
            else:
                print(f"\n❌ 回测报告生成失败")
                return None
                
        except Exception as e:
            print(f"❌ 生成回测报告失败: {e}")
            return None
    
    def run_full_backtest(self, days: int = 30,
                          sectors_csv_path: str = None,
                          stocks_csv_path: str = None,
                          parallel: bool = True,
                          generate_report: bool = True,
                          output_dir: str = None) -> Dict[str, Any]:
        """
        执行完整的回测流程并生成报告
        
        Args:
            days: 获取最近N天的推荐数据，默认30天
            sectors_csv_path: 板块推荐CSV文件路径
            stocks_csv_path: 股票推荐CSV文件路径
            parallel: 是否并行执行，默认True
            generate_report: 是否生成报告，默认True
            output_dir: 报告输出目录
            
        Returns:
            Dict: 完整的回测结果
        """
        try:
            # 执行回测
            results = self.run_backtest(
                days=days,
                sectors_csv_path=sectors_csv_path,
                stocks_csv_path=stocks_csv_path,
                parallel=parallel
            )
            
            # 生成报告
            if generate_report:
                report_path = self.generate_report(results, output_dir)
                results['report_path'] = report_path
            
            return results
            
        except Exception as e:
            print(f"❌ 完整回测流程失败: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

