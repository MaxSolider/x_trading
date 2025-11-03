"""
热门新闻分析策略
对新闻资讯进行分词解析关键词并计算关键词出现频次
"""

import pandas as pd
from typing import Dict, Any, Optional, List
from collections import Counter
import re

try:
    import jieba
    import jieba.analyse
    JIEBA_AVAILABLE = True
except ImportError:
    JIEBA_AVAILABLE = False
    print("⚠️ jieba库未安装，新闻关键词分析功能将不可用。安装命令: pip install jieba")

from ...repositories.news_query import NewsQuery


class NewsAnalysisStrategy:
    """热门新闻分析策略类"""
    
    def __init__(self):
        """初始化新闻分析策略"""
        self.news_query = NewsQuery()
        # 初始化jieba分词
        if JIEBA_AVAILABLE:
            jieba.initialize()
        # 加载停用词（如果有停用词文件）
        self.stopwords = self._load_stopwords()
        if JIEBA_AVAILABLE:
            print("✅ 热门新闻分析策略初始化成功")
        else:
            print("⚠️ 热门新闻分析策略初始化成功（jieba未安装，部分功能不可用）")
    
    def _load_stopwords(self) -> set:
        """
        加载停用词表
        
        Returns:
            set: 停用词集合
        """
        stopwords = set()
        # 常见的停用词
        common_stopwords = {
            '的', '了', '在', '是', '我', '有', '和', '就', 
            '不', '人', '都', '一', '一个', '上', '也', '很',
            '到', '说', '要', '去', '你', '会', '着', '没有',
            '看', '好', '自己', '这', '那', '等', '与', '及',
            '年', '月', '日', '时', '分', '秒', '年', '月', '日',
            '今天', '明天', '昨天', '今年', '明年', '去年'
        }
        stopwords.update(common_stopwords)
        return stopwords
    
    def analyze_news_keywords(self, news_data: Optional[pd.DataFrame] = None, top_n: int = 50) -> Dict[str, Any]:
        """
        分析新闻关键词
        
        Args:
            news_data: 新闻数据DataFrame，如果为None则自动获取
            top_n: 返回前N个关键词，默认为50
            
        Returns:
            Dict[str, Any]: 关键词分析结果，包含：
                keywords: List[Dict] 关键词列表，每个元素包含 {'keyword': str, 'count': int}
                wordcloud_data: Dict 用于生成词云的数据
                total_keywords: int 关键词总数
                total_news: int 新闻总数
        """
        try:
            if not JIEBA_AVAILABLE:
                print("❌ jieba库未安装，无法进行关键词分析")
                return {
                    'keywords': [],
                    'wordcloud_data': {},
                    'total_keywords': 0,
                    'total_news': 0
                }
            
            # 如果没有提供新闻数据，则自动获取
            if news_data is None:
                print("🔍 正在获取新闻数据...")
                news_data = self.news_query.get_news()
            
            if news_data is None or news_data.empty:
                print("⚠️ 未获取到新闻数据")
                return {
                    'keywords': [],
                    'wordcloud_data': {},
                    'total_keywords': 0,
                    'total_news': 0
                }
            
            print(f"📰 开始分析 {len(news_data)} 条新闻的关键词...")
            
            # 提取所有新闻内容
            content_list = news_data['内容'].fillna('').astype(str).tolist()
            
            # 分词并提取关键词
            all_keywords = []
            for content in content_list:
                if content and content.strip():
                    # 使用jieba分词
                    words = self._extract_keywords(content)
                    all_keywords.extend(words)
            
            # 统计关键词频次
            keyword_counter = Counter(all_keywords)
            
            # 获取前N个关键词
            top_keywords = keyword_counter.most_common(top_n)
            
            # 构建结果
            keywords_list = [
                {'keyword': keyword, 'count': count}
                for keyword, count in top_keywords
            ]
            
            # 构建词云数据（格式：{word: weight}）
            wordcloud_data = {
                keyword: count
                for keyword, count in top_keywords
            }
            
            result = {
                'keywords': keywords_list,
                'wordcloud_data': wordcloud_data,
                'total_keywords': len(keyword_counter),
                'total_news': len(news_data)
            }
            
            print(f"✅ 关键词分析完成，共提取 {result['total_keywords']} 个唯一关键词")
            return result
            
        except Exception as e:
            print(f"❌ 关键词分析失败: {e}")
            import traceback
            traceback.print_exc()
            return {
                'keywords': [],
                'wordcloud_data': {},
                'total_keywords': 0,
                'total_news': 0
            }
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        从文本中提取关键词
        
        Args:
            text: 输入文本
            
        Returns:
            List[str]: 关键词列表
        """
        try:
            if not JIEBA_AVAILABLE:
                return []
            
            # 清理文本（移除特殊字符，保留中文、英文、数字）
            text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s]', '', text)
            
            # 使用jieba分词
            words = jieba.cut(text, cut_all=False)
            
            # 过滤停用词和短词
            keywords = []
            for word in words:
                word = word.strip()
                # 过滤条件：长度>=2，不是停用词，不是纯数字
                if (len(word) >= 2 and 
                    word not in self.stopwords and 
                    not word.isdigit() and
                    not re.match(r'^\d+$', word)):
                    keywords.append(word)
            
            return keywords
            
        except Exception as e:
            print(f"⚠️ 文本分词失败: {e}")
            return []
    
    def generate_keyword_frequency_table(self, keywords_list: List[Dict[str, Any]], max_rows: int = 30) -> pd.DataFrame:
        """
        生成关键词频次表格
        
        Args:
            keywords_list: 关键词列表
            max_rows: 最大显示行数
            
        Returns:
            DataFrame: 关键词频次表格
        """
        try:
            if not keywords_list:
                return pd.DataFrame(columns=['关键词', '出现频次'])
            
            # 构建DataFrame
            df = pd.DataFrame(keywords_list)
            df.columns = ['关键词', '出现频次']
            
            # 限制行数
            if len(df) > max_rows:
                df = df.head(max_rows)
            
            return df
            
        except Exception as e:
            print(f"❌ 生成关键词频次表格失败: {e}")
            return pd.DataFrame(columns=['关键词', '出现频次'])

