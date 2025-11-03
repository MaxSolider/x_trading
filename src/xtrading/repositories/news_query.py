"""
新闻查询模块
基于AKShare实现多渠道聚合信息查询功能
"""

import akshare as ak
import pandas as pd
from typing import Optional, List
from ..utils.limiter.akshare_rate_limiter import rate_limit_manual


class NewsQuery:
    """新闻查询类"""
    
    def __init__(self):
        """初始化查询类"""
        print("✅ 新闻查询服务初始化成功")
    
    def get_news(self) -> Optional[pd.DataFrame]:
        """
        获取多渠道聚合新闻信息
        合并多个数据源的新闻信息并返回统一格式的数据
        
        Returns:
            DataFrame: 包含聚合信息的DataFrame，包含以下列：
                内容	object	新闻内容
                发布时间	object	发布时间
        """
        try:
            print("🔍 正在获取多渠道聚合新闻信息...")
            
            all_data = []
            #
            # # 1. 获取财经早餐-东方财富数据
            # try:
            #     rate_limit_manual()
            #     cjzc_data = ak.stock_info_cjzc_em()
            #     if cjzc_data is not None and not cjzc_data.empty:
            #         processed_data = self._process_cjzc_em(cjzc_data)
            #         all_data.append(processed_data)
            #         print(f"✅ 成功获取财经早餐-东方财富数据，共 {len(processed_data)} 条")
            #     else:
            #         print("⚠️ 财经早餐-东方财富数据为空")
            # except Exception as e:
            #     print(f"⚠️ 获取财经早餐-东方财富数据失败: {e}")
            #
            # # 2. 获取东方财富全球数据
            # try:
            #     rate_limit_manual()
            #     global_em_data = ak.stock_info_global_em()
            #     if global_em_data is not None and not global_em_data.empty:
            #         processed_data = self._process_global_em(global_em_data)
            #         all_data.append(processed_data)
            #         print(f"✅ 成功获取东方财富全球数据，共 {len(processed_data)} 条")
            #     else:
            #         print("⚠️ 东方财富全球数据为空")
            # except Exception as e:
            #     print(f"⚠️ 获取东方财富全球数据失败: {e}")
            #
            # 3. 获取新浪财经全球数据
            try:
                rate_limit_manual()
                sina_data = ak.stock_info_global_sina()
                if sina_data is not None and not sina_data.empty:
                    processed_data = self._process_global_sina(sina_data)
                    all_data.append(processed_data)
                    print(f"✅ 成功获取新浪财经全球数据，共 {len(processed_data)} 条")
                else:
                    print("⚠️ 新浪财经全球数据为空")
            except Exception as e:
                print(f"⚠️ 获取新浪财经全球数据失败: {e}")
            #
            # # 4. 获取富途牛牛全球数据
            # try:
            #     rate_limit_manual()
            #     futu_data = ak.stock_info_global_futu()
            #     if futu_data is not None and not futu_data.empty:
            #         processed_data = self._process_global_futu(futu_data)
            #         all_data.append(processed_data)
            #         print(f"✅ 成功获取富途牛牛全球数据，共 {len(processed_data)} 条")
            #     else:
            #         print("⚠️ 富途牛牛全球数据为空")
            # except Exception as e:
            #     print(f"⚠️ 获取富途牛牛全球数据失败: {e}")
            #
            # # 5. 获取同花顺全球数据
            # try:
            #     rate_limit_manual()
            #     ths_data = ak.stock_info_global_ths()
            #     if ths_data is not None and not ths_data.empty:
            #         processed_data = self._process_global_ths(ths_data)
            #         all_data.append(processed_data)
            #         print(f"✅ 成功获取同花顺全球数据，共 {len(processed_data)} 条")
            #     else:
            #         print("⚠️ 同花顺全球数据为空")
            # except Exception as e:
            #     print(f"⚠️ 获取同花顺全球数据失败: {e}")
            
            # 6. 获取财联社全球数据
            try:
                rate_limit_manual()
                cls_data = ak.stock_info_global_cls()
                if cls_data is not None and not cls_data.empty:
                    processed_data = self._process_global_cls(cls_data)
                    all_data.append(processed_data)
                    print(f"✅ 成功获取财联社全球数据，共 {len(processed_data)} 条")
                else:
                    print("⚠️ 财联社全球数据为空")
            except Exception as e:
                print(f"⚠️ 获取财联社全球数据失败: {e}")
            
            # 合并所有数据
            if all_data:
                combined_df = pd.concat(all_data, ignore_index=True)
                # 按发布时间降序排序（最新的在前）
                if '发布时间' in combined_df.columns:
                    combined_df = combined_df.sort_values('发布时间', ascending=False, na_position='last')
                print(f"✅ 成功合并多渠道数据，总计 {len(combined_df)} 条记录")
                return combined_df[['内容', '发布时间']]
            else:
                print("❌ 未能获取任何数据")
                return None
                
        except Exception as e:
            print(f"❌ 获取多渠道聚合信息失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _process_cjzc_em(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        处理财经早餐-东方财富数据
        数据结构：标题、摘要、发布时间、链接
        """
        result = pd.DataFrame()
        
        # 获取发布时间列（尝试多个可能的列名）
        time_col = None
        for col_name in ['发布时间', '时间', 'publish_time', 'time']:
            if col_name in df.columns:
                time_col = df[col_name]
                break
        
        if time_col is not None:
            result['发布时间'] = time_col.fillna('').astype(str)
        else:
            result['发布时间'] = pd.Series([''] * len(df))
        
        # 获取标题列
        title_col = None
        for col_name in ['标题', 'title']:
            if col_name in df.columns:
                title_col = df[col_name]
                break
        
        # 获取摘要列
        summary_col = None
        for col_name in ['摘要', 'summary', 'abstract']:
            if col_name in df.columns:
                summary_col = df[col_name]
                break
        
        # 处理可能的NaN值并合并
        title = title_col.fillna('').astype(str) if title_col is not None else pd.Series([''] * len(df))
        summary = summary_col.fillna('').astype(str) if summary_col is not None else pd.Series([''] * len(df))
        
        # 合并标题和摘要
        result['内容'] = (title + ' ' + summary).str.strip()
        
        return result[['内容', '发布时间']]
    
    def _process_global_em(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        处理东方财富全球数据
        数据结构：标题、摘要、发布时间、链接
        """
        result = pd.DataFrame()
        
        # 获取发布时间列（尝试多个可能的列名）
        time_col = None
        for col_name in ['发布时间', '时间', 'publish_time', 'time']:
            if col_name in df.columns:
                time_col = df[col_name]
                break
        
        if time_col is not None:
            result['发布时间'] = time_col.fillna('').astype(str)
        else:
            result['发布时间'] = pd.Series([''] * len(df))
        
        # 获取标题列
        title_col = None
        for col_name in ['标题', 'title']:
            if col_name in df.columns:
                title_col = df[col_name]
                break
        
        # 获取摘要列
        summary_col = None
        for col_name in ['摘要', 'summary', 'abstract']:
            if col_name in df.columns:
                summary_col = df[col_name]
                break
        
        # 处理可能的NaN值并合并
        title = title_col.fillna('').astype(str) if title_col is not None else pd.Series([''] * len(df))
        summary = summary_col.fillna('').astype(str) if summary_col is not None else pd.Series([''] * len(df))
        
        # 合并标题和摘要
        result['内容'] = (title + ' ' + summary).str.strip()
        
        return result[['内容', '发布时间']]
    
    def _process_global_sina(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        处理新浪财经全球数据
        数据结构：时间、内容
        """
        result = pd.DataFrame()
        
        # 获取发布时间列
        time_col = None
        for col_name in ['时间', '发布时间', 'time', 'publish_time']:
            if col_name in df.columns:
                time_col = df[col_name]
                break
        
        if time_col is not None:
            result['发布时间'] = time_col.fillna('').astype(str)
        else:
            result['发布时间'] = pd.Series([''] * len(df))
        
        # 获取内容列
        content_col = None
        for col_name in ['内容', 'content']:
            if col_name in df.columns:
                content_col = df[col_name]
                break
        
        if content_col is not None:
            result['内容'] = content_col.fillna('').astype(str)
        else:
            result['内容'] = pd.Series([''] * len(df))
        
        return result[['内容', '发布时间']]
    
    def _process_global_futu(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        处理富途牛牛全球数据
        数据结构：标题、内容、发布时间、链接
        """
        result = pd.DataFrame()
        
        # 获取发布时间列
        time_col = None
        for col_name in ['发布时间', '时间', 'publish_time', 'time']:
            if col_name in df.columns:
                time_col = df[col_name]
                break
        
        if time_col is not None:
            result['发布时间'] = time_col.fillna('').astype(str)
        else:
            result['发布时间'] = pd.Series([''] * len(df))
        
        # 获取标题列
        title_col = None
        for col_name in ['标题', 'title']:
            if col_name in df.columns:
                title_col = df[col_name]
                break
        
        # 获取内容列
        content_col = None
        for col_name in ['内容', 'content']:
            if col_name in df.columns:
                content_col = df[col_name]
                break
        
        # 处理可能的NaN值并合并
        title = title_col.fillna('').astype(str) if title_col is not None else pd.Series([''] * len(df))
        content = content_col.fillna('').astype(str) if content_col is not None else pd.Series([''] * len(df))
        
        # 合并标题和内容
        result['内容'] = (title + ' ' + content).str.strip()
        
        return result[['内容', '发布时间']]
    
    def _process_global_ths(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        处理同花顺全球数据
        数据结构：标题、内容、发布时间、链接
        """
        result = pd.DataFrame()
        
        # 获取发布时间列
        time_col = None
        for col_name in ['发布时间', '时间', 'publish_time', 'time']:
            if col_name in df.columns:
                time_col = df[col_name]
                break
        
        if time_col is not None:
            result['发布时间'] = time_col.fillna('').astype(str)
        else:
            result['发布时间'] = pd.Series([''] * len(df))
        
        # 获取标题列
        title_col = None
        for col_name in ['标题', 'title']:
            if col_name in df.columns:
                title_col = df[col_name]
                break
        
        # 获取内容列
        content_col = None
        for col_name in ['内容', 'content']:
            if col_name in df.columns:
                content_col = df[col_name]
                break
        
        # 处理可能的NaN值并合并
        title = title_col.fillna('').astype(str) if title_col is not None else pd.Series([''] * len(df))
        content = content_col.fillna('').astype(str) if content_col is not None else pd.Series([''] * len(df))
        
        # 合并标题和内容
        result['内容'] = (title + ' ' + content).str.strip()
        
        return result[['内容', '发布时间']]
    
    def _process_global_cls(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        处理财联社全球数据
        数据结构：标题、内容、发布日期、发布时间
        """
        result = pd.DataFrame()
        
        # 优先使用发布时间，如果没有则使用发布日期
        time_col = None
        for col_name in ['发布时间', 'publish_time', 'time']:
            if col_name in df.columns:
                time_col = df[col_name]
                break
        
        # 如果发布时间为空，尝试使用发布日期
        if time_col is None or time_col.isna().all():
            for col_name in ['发布日期', 'publish_date', 'date']:
                if col_name in df.columns:
                    time_col = df[col_name]
                    break
        
        if time_col is not None:
            result['发布时间'] = time_col.fillna('').astype(str)
        else:
            result['发布时间'] = pd.Series([''] * len(df))
        
        # 获取标题列
        title_col = None
        for col_name in ['标题', 'title']:
            if col_name in df.columns:
                title_col = df[col_name]
                break
        
        # 获取内容列
        content_col = None
        for col_name in ['内容', 'content']:
            if col_name in df.columns:
                content_col = df[col_name]
                break
        
        # 处理可能的NaN值并合并
        title = title_col.fillna('').astype(str) if title_col is not None else pd.Series([''] * len(df))
        content = content_col.fillna('').astype(str) if content_col is not None else pd.Series([''] * len(df))
        
        # 合并标题和内容
        result['内容'] = (title).str.strip()
        
        return result[['内容', '发布时间']]

