"""
股票回测模块
基于推荐历史数据进行股票回测验证
"""

import pandas as pd
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from ...repositories.stock_query import StockQuery


class StockBacktest:
    """股票回测类"""
    
    def __init__(self):
        """初始化回测类"""
        self.stock_query = StockQuery()
        print("✅ 股票回测模块初始化成功")
    
    def load_recommendations(self, csv_path: str = None, days: int = 30) -> pd.DataFrame:
        """
        从CSV文件中加载最近N天的推荐买入股票列表
        
        Args:
            csv_path: CSV文件路径，默认为reports/history/stocks_history.csv
            days: 获取最近N天的数据，默认30天
            
        Returns:
            DataFrame: 包含股票名称、日期、推荐原因的DataFrame
        """
        try:
            if csv_path is None:
                # 获取项目根目录
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
                csv_path = os.path.join(project_root, 'reports', 'history', 'stocks_history.csv')
            
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
    
    def _get_stock_code_map(self, stock_names: List[str]) -> Dict[str, str]:
        """
        构建股票名称到代码的映射
        
        Args:
            stock_names: 股票名称列表
            
        Returns:
            Dict: {股票名称: 股票代码}
        """
        try:
            # 获取所有股票列表
            stocks_df = self.stock_query.get_all_stock()
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
            
            # 过滤只包含需要的股票
            filtered_map = {name: stock_map[name] for name in stock_names if name in stock_map}
            
            print(f"✅ 成功构建股票代码映射，共 {len(filtered_map)}/{len(stock_names)} 条匹配")
            return filtered_map
            
        except Exception as e:
            print(f"❌ 构建股票代码映射失败: {e}")
            return {}
    
    def backtest_stock(self, stock_name: str, recommend_date: str, end_date: str = None, stock_code_map: Dict[str, str] = None) -> Dict[str, Any]:
        """
        回测单个股票
        
        Args:
            stock_name: 股票名称
            recommend_date: 推荐买入日期（格式：YYYYMMDD）
            end_date: 结束日期，默认为今日（格式：YYYYMMDD）
            stock_code_map: 股票名称到代码的映射字典，可选
            
        Returns:
            Dict: 回测结果，包含各种涨跌幅指标
        """
        try:
            if end_date is None:
                end_date = datetime.now().strftime('%Y%m%d')
            
            # 获取股票代码
            stock_code = None
            if stock_code_map and stock_name in stock_code_map:
                stock_code = stock_code_map[stock_name]
            else:
                # 如果映射中没有，尝试直接搜索
                stock_code = self.stock_query.search_stock_by_name(stock_name)
            
            if stock_code is None:
                return {
                    'stock_name': stock_name,
                    'recommend_date': recommend_date,
                    'status': 'error',
                    'error': f'无法找到股票代码: {stock_name}'
                }
            
            # 获取股票日频数据
            hist_data = self.stock_query.get_historical_quotes(
                symbol=stock_code,
                start_date=recommend_date,
                end_date=end_date,
                use_db=True
            )
            
            if hist_data is None or hist_data.empty:
                return {
                    'stock_name': stock_name,
                    'stock_code': stock_code,
                    'recommend_date': recommend_date,
                    'status': 'error',
                    'error': '无法获取历史数据'
                }
            
            # 确保日期列为字符串格式，并按日期排序
            if '日期' in hist_data.columns:
                hist_data['日期'] = hist_data['日期'].astype(str)
            elif 'date' in hist_data.columns:
                hist_data['日期'] = hist_data['date'].astype(str)
            
            hist_data = hist_data.sort_values('日期').reset_index(drop=True)
            
            # 获取推荐日期的收盘价
            recommend_data = hist_data[hist_data['日期'] == recommend_date]
            if recommend_data.empty:
                # 如果没有推荐日期的数据，使用最近的数据
                recommend_data = hist_data.head(1)
                if recommend_data.empty:
                    return {
                        'stock_name': stock_name,
                        'stock_code': stock_code,
                        'recommend_date': recommend_date,
                        'status': 'error',
                        'error': '推荐日期无数据'
                    }
                actual_recommend_date = recommend_data.iloc[0]['日期']
            else:
                actual_recommend_date = recommend_date
            
            # 获取收盘价列名
            close_col = None
            for col in ['收盘', 'close', '最新价']:
                if col in hist_data.columns:
                    close_col = col
                    break
            
            if close_col is None:
                return {
                    'stock_name': stock_name,
                    'stock_code': stock_code,
                    'recommend_date': recommend_date,
                    'status': 'error',
                    'error': '无法找到收盘价列'
                }
            
            recommend_price = float(recommend_data.iloc[0][close_col])
            
            # 计算各种涨跌幅
            results = {
                'stock_name': stock_name,
                'stock_code': stock_code,
                'recommend_date': recommend_date,
                'actual_recommend_date': actual_recommend_date,
                'recommend_price': recommend_price,
                'status': 'success'
            }
            
            # 获取后续交易日的索引
            recommend_idx = hist_data[hist_data['日期'] == actual_recommend_date].index
            if len(recommend_idx) == 0:
                return {
                    'stock_name': stock_name,
                    'stock_code': stock_code,
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
            print(f"❌ 回测股票 {stock_name} 失败: {e}")
            return {
                'stock_name': stock_name,
                'recommend_date': recommend_date,
                'status': 'error',
                'error': str(e)
            }
    
    def backtest_all(self, days: int = 30, csv_path: str = None) -> List[Dict[str, Any]]:
        """
        回测所有推荐股票
        
        Args:
            days: 获取最近N天的推荐数据，默认30天
            csv_path: CSV文件路径
            
        Returns:
            List[Dict]: 所有股票的回测结果列表
        """
        try:
            # 加载推荐列表
            recommendations = self.load_recommendations(csv_path=csv_path, days=days)
            
            if recommendations.empty:
                print("⚠️ 没有找到推荐记录")
                return []
            
            # 一次性构建所有股票的代码映射，提高效率
            print("\n🔍 构建股票代码映射...")
            stock_names = recommendations['股票名称'].unique().tolist()
            stock_code_map = self._get_stock_code_map(stock_names)
            print(f"✅ 已构建 {len(stock_code_map)} 个股票的代码映射\n")
            
            results = []
            
            # 对每条推荐进行回测
            for idx, row in recommendations.iterrows():
                stock_name = row['股票名称']
                recommend_date = str(row['日期'])
                reason = row.get('推荐原因', '')
                
                print(f"\n📊 [{idx + 1}/{len(recommendations)}] 回测股票: {stock_name} (推荐日期: {recommend_date})")
                
                result = self.backtest_stock(stock_name, recommend_date, stock_code_map=stock_code_map)
                result['reason'] = reason
                
                results.append(result)
            
            print(f"\n✅ 完成所有股票回测，共 {len(results)} 条记录")
            return results
            
        except Exception as e:
            print(f"❌ 批量回测失败: {e}")
            return []


# 为了向后兼容，保留旧的类名
IndividualStockBacktest = StockBacktest
