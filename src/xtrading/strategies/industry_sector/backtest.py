"""
行业板块回测模块
基于推荐历史数据进行板块回测验证
"""

import pandas as pd
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from ...repositories.industry_info_query import IndustryInfoQuery
from ...utils.date.date_utils import DateUtils


class SectorBacktest:
    """行业板块回测类"""
    
    def __init__(self):
        """初始化回测类"""
        self.industry_query = IndustryInfoQuery()
        self.date_utils = DateUtils()
        print("✅ 行业板块回测模块初始化成功")
    
    def load_recommendations(self, csv_path: str = None, days: int = 30) -> pd.DataFrame:
        """
        从CSV文件中加载最近N天的推荐买入板块列表
        
        Args:
            csv_path: CSV文件路径，默认为reports/history/sectors_history.csv
            days: 获取最近N天的数据，默认30天
            
        Returns:
            DataFrame: 包含板块名称、日期、推荐原因的DataFrame
        """
        try:
            if csv_path is None:
                # 获取项目根目录
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
                csv_path = os.path.join(project_root, 'reports', 'history', 'sectors_history.csv')
            
            if not os.path.exists(csv_path):
                print(f"❌ CSV文件不存在: {csv_path}")
                return pd.DataFrame()
            
            # 读取CSV文件
            df = pd.read_csv(csv_path)
            
            # 确保日期列为字符串格式
            if '日期' in df.columns:
                df['日期'] = df['日期'].astype(str)
                
                # 获取最近N天的数据
                today = datetime.now()
                cutoff_date = (today - timedelta(days=days)).strftime('%Y%m%d')
                
                # 过滤日期
                df = df[df['日期'] >= cutoff_date]
                
                print(f"✅ 成功加载 {len(df)} 条推荐记录（最近{days}天）")
                return df
            else:
                print(f"❌ CSV文件中未找到'日期'列")
                return pd.DataFrame()
                
        except Exception as e:
            print(f"❌ 加载推荐列表失败: {e}")
            return pd.DataFrame()
    
    def backtest_sector(self, sector_name: str, recommend_date: str, end_date: str = None) -> Dict[str, Any]:
        """
        回测单个板块
        
        Args:
            sector_name: 板块名称
            recommend_date: 推荐买入日期（格式：YYYYMMDD）
            end_date: 结束日期，默认为今日（格式：YYYYMMDD）
            
        Returns:
            Dict: 回测结果，包含各种涨跌幅指标
        """
        try:
            if end_date is None:
                end_date = datetime.now().strftime('%Y%m%d')
            
            # 获取板块日频数据
            hist_data = self.industry_query.get_board_industry_hist(
                symbol=sector_name,
                start_date=recommend_date,
                end_date=end_date,
                use_db=True
            )
            
            if hist_data is None or hist_data.empty:
                return {
                    'sector_name': sector_name,
                    'recommend_date': recommend_date,
                    'status': 'error',
                    'error': '无法获取历史数据'
                }
            
            # 确保日期列为字符串格式，并按日期排序
            # 统一日期列名
            if '日期' not in hist_data.columns:
                if 'date' in hist_data.columns:
                    hist_data = hist_data.rename(columns={'date': '日期'})
                elif isinstance(hist_data.index, pd.DatetimeIndex):
                    hist_data = hist_data.reset_index()
                    if 'index' in hist_data.columns:
                        hist_data = hist_data.rename(columns={'index': '日期'})
            
            # 转换日期为字符串格式 YYYYMMDD
            if '日期' in hist_data.columns:
                hist_data['日期'] = hist_data['日期'].astype(str)
                # 处理不同的日期格式：YYYY-MM-DD -> YYYYMMDD
                hist_data['日期'] = hist_data['日期'].str.replace('-', '').str.replace('/', '').str[:8]
            else:
                return {
                    'sector_name': sector_name,
                    'recommend_date': recommend_date,
                    'status': 'error',
                    'error': '无法找到日期列'
                }
            
            hist_data = hist_data.sort_values('日期').reset_index(drop=True)
            
            # 确保推荐日期也是 YYYYMMDD 格式
            recommend_date_clean = recommend_date.replace('-', '').replace('/', '')[:8]
            
            # 获取推荐日期的收盘价
            recommend_data = hist_data[hist_data['日期'] == recommend_date_clean]
            if recommend_data.empty:
                # 如果没有推荐日期的数据，使用最近的数据
                recommend_data = hist_data.head(1)
                if recommend_data.empty:
                    return {
                        'sector_name': sector_name,
                        'recommend_date': recommend_date,
                        'status': 'error',
                        'error': '推荐日期无数据'
                    }
                actual_recommend_date = recommend_data.iloc[0]['日期']
            else:
                actual_recommend_date = recommend_date_clean
            
            # 获取收盘价列名（支持多种可能的列名）
            close_col = None
            possible_close_cols = ['收盘价', '收盘', 'close', '最新价', 'Close', 'CLOSE']
            for col in possible_close_cols:
                if col in hist_data.columns:
                    close_col = col
                    break
            
            if close_col is None:
                # 如果找不到，打印可用的列名以便调试
                available_cols = list(hist_data.columns)
                return {
                    'sector_name': sector_name,
                    'recommend_date': recommend_date,
                    'status': 'error',
                    'error': f'无法找到收盘价列，可用列名: {available_cols}'
                }
            
            recommend_price = float(recommend_data.iloc[0][close_col])
            
            # 计算各种涨跌幅
            results = {
                'sector_name': sector_name,
                'recommend_date': recommend_date,
                'actual_recommend_date': actual_recommend_date,
                'recommend_price': recommend_price,
                'status': 'success'
            }
            
            # 获取后续交易日的索引
            actual_recommend_date_clean = actual_recommend_date.replace('-', '').replace('/', '')[:8]
            recommend_idx = hist_data[hist_data['日期'] == actual_recommend_date_clean].index
            if len(recommend_idx) == 0:
                return {
                    'sector_name': sector_name,
                    'recommend_date': recommend_date,
                    'status': 'error',
                    'error': '无法找到推荐日期在数据中的位置'
                }
            
            recommend_idx = recommend_idx[0]
            total_days = len(hist_data) - recommend_idx - 1
            
            # 1. 次日涨跌幅
            if recommend_idx + 1 < len(hist_data):
                next_day_data = hist_data.iloc[recommend_idx + 1]
                next_day_price = float(next_day_data[close_col])
                next_day_return = ((next_day_price - recommend_price) / recommend_price) * 100
                results['next_day_return'] = round(next_day_return, 2)
                results['next_day_date'] = next_day_data['日期']
            else:
                results['next_day_return'] = None
                results['next_day_date'] = None
            
            # 2. 2日累计涨跌幅
            if recommend_idx + 2 < len(hist_data):
                day2_data = hist_data.iloc[recommend_idx + 2]
                day2_price = float(day2_data[close_col])
                day2_return = ((day2_price - recommend_price) / recommend_price) * 100
                results['day2_return'] = round(day2_return, 2)
                results['day2_date'] = day2_data['日期']
            else:
                results['day2_return'] = None
                results['day2_date'] = None
            
            # 3. 5日累计涨跌幅
            if recommend_idx + 5 < len(hist_data):
                day5_data = hist_data.iloc[recommend_idx + 5]
                day5_price = float(day5_data[close_col])
                day5_return = ((day5_price - recommend_price) / recommend_price) * 100
                results['day5_return'] = round(day5_return, 2)
                results['day5_date'] = day5_data['日期']
            else:
                results['day5_return'] = None
                results['day5_date'] = None
            
            # 4. 至今累计涨跌幅
            if recommend_idx + 1 < len(hist_data):
                last_data = hist_data.iloc[-1]
                last_price = float(last_data[close_col])
                total_return = ((last_price - recommend_price) / recommend_price) * 100
                results['total_return'] = round(total_return, 2)
                results['total_days'] = total_days
                results['end_date'] = last_data['日期']
            else:
                results['total_return'] = None
                results['total_days'] = 0
                results['end_date'] = None
            
            # 5. 最高累计涨跌幅（遍历所有日期，计算累计涨跌幅，找最大值）
            if recommend_idx + 1 < len(hist_data):
                max_return = None
                max_return_date = None
                max_idx = None
                
                # 遍历推荐日期之后的所有日期，计算累计涨跌幅
                for i in range(recommend_idx + 1, len(hist_data)):
                    current_price = float(hist_data.iloc[i][close_col])
                    current_return = ((current_price - recommend_price) / recommend_price) * 100
                    
                    # 记录累计涨跌幅最大的日期
                    if max_return is None or current_return > max_return:
                        max_return = current_return
                        max_return_date = hist_data.iloc[i]['日期']
                        max_idx = i
                
                if max_return is not None:
                    results['max_return'] = round(max_return, 2)
                    results['max_return_date'] = max_return_date
                else:
                    results['max_return'] = None
                    results['max_return_date'] = None
            else:
                results['max_return'] = None
                results['max_return_date'] = None
            
            return results
            
        except Exception as e:
            print(f"❌ 回测板块 {sector_name} 失败: {e}")
            return {
                'sector_name': sector_name,
                'recommend_date': recommend_date,
                'status': 'error',
                'error': str(e)
            }
    
    def backtest_all(self, days: int = 30, csv_path: str = None) -> List[Dict[str, Any]]:
        """
        回测所有推荐板块
        
        Args:
            days: 获取最近N天的推荐数据，默认30天
            csv_path: CSV文件路径
            
        Returns:
            List[Dict]: 所有板块的回测结果列表
        """
        try:
            # 加载推荐列表
            recommendations = self.load_recommendations(csv_path=csv_path, days=days)
            
            if recommendations.empty:
                print("⚠️ 没有找到推荐记录")
                return []
            
            results = []
            
            # 对每条推荐进行回测
            for idx, row in recommendations.iterrows():
                sector_name = row['板块名称']
                recommend_date = str(row['日期'])
                reason = row.get('推荐原因', '')
                
                print(f"\n📊 [{idx + 1}/{len(recommendations)}] 回测板块: {sector_name} (推荐日期: {recommend_date})")
                
                result = self.backtest_sector(sector_name, recommend_date)
                result['reason'] = reason
                
                results.append(result)
            
            print(f"\n✅ 完成所有板块回测，共 {len(results)} 条记录")
            return results
            
        except Exception as e:
            print(f"❌ 批量回测失败: {e}")
            return []


# 为了向后兼容，保留旧的类名
StrategyBacktest = SectorBacktest
