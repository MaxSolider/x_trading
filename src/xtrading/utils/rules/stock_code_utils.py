"""
股票代码工具类
提供股票代码相关的工具方法
"""

import re
from typing import Optional, Dict, List, Tuple


class StockCodeUtils:
    """股票代码工具类"""
    
    # 市场代码规则定义 (基于最新A股代码规则)
    MARKET_RULES = {
        'SH': {
            'name': '上海证券交易所',
            'patterns': [
                r'^60[0-5]\d{3}$',  # 主板：600, 601, 603, 605开头
                r'^68[8-9]\d{3}$',       # 科创板：688开头
                r'^900\d{3}$',       # B股：900开头
            ],
            'prefix': 'SH',
            'lower_prefix': 'sh'
        },
        'SZ': {
            'name': '深圳证券交易所',
            'patterns': [
                r'^00[0-3]\d{3}$',   # 主板：000, 001, 002, 003开头
                r'^30[0-2]\d{3}$',    # 创业板：300, 301，302开头
                r'^200\d{3}$',        # B股：200开头
            ],
            'prefix': 'SZ',
            'lower_prefix': 'sz'
        },
        'BJ': {
            'name': '北京证券交易所',
            'patterns': [
                r'^920\d{3}$',       # 北交所：920开头
                r'^83\d{4}$',        # 北交所：83开头
                r'^87\d{4}$',        # 北交所：87开头
                r'^88\d{4}$',        # 北交所：88开头
                r'^82\d{4}$',        # 北交所：82开头
                r'^889\d{3}$',       # 北交所：889开头
            ],
            'prefix': 'BJ',
            'lower_prefix': 'bj'
        }
    }
    
    def __init__(self):
        """初始化工具类"""

    def detect_market(self, stock_code: str) -> Optional[str]:
        """
        根据股票代码判断所属市场
        
        Args:
            stock_code: 股票代码 (如: 000001, 600000, 688001)
            
        Returns:
            str: 市场代码 (SH/SZ/BJ) 或 None
        """
        if not stock_code or not isinstance(stock_code, str):
            print("❌ 股票代码不能为空且必须是字符串")
            return None
        
        # 清理股票代码，移除空格和特殊字符
        clean_code = re.sub(r'[^\d]', '', stock_code)
        
        if not clean_code:
            print("❌ 股票代码格式无效")
            return None
        
        # 检查每个市场的规则
        for market_code, market_info in self.MARKET_RULES.items():
            for pattern in market_info['patterns']:
                if re.match(pattern, clean_code):
                    return market_code
        
        print(f"❌ 无法识别股票代码 {stock_code} 所属市场")
        return None
    
    def add_market_prefix(self, stock_code: str, lower_case: bool) -> Optional[str]:
        """
        为股票代码增加市场前缀
        
        Args:
            stock_code: 股票代码 (如: 000001, 600000)
            
        Returns:
            str: 带市场前缀的股票代码 (如: SZ000001, SH600000) 或 None
        """
        market = self.detect_market(stock_code)
        if market:
            market_info = self.MARKET_RULES[market]
            if lower_case:
                prefix = market_info['lower_prefix']
            else:
                prefix = market_info['prefix']
            clean_code = re.sub(r'[^\d]', '', stock_code)
            result = f"{prefix}{clean_code}"
            return result
        else:
            print(f"❌ 无法为股票代码 {stock_code} 添加市场前缀")
            return None
    
    def remove_market_prefix(self, stock_code: str) -> Optional[str]:
        """
        移除股票代码的市场前缀
        
        Args:
            stock_code: 带前缀的股票代码 (如: SZ000001, SH600000)
            
        Returns:
            str: 不带前缀的股票代码 (如: 000001, 600000) 或 None
        """
        if not stock_code or not isinstance(stock_code, str):
            print("❌ 股票代码不能为空且必须是字符串")
            return None
        
        # 匹配市场前缀并移除
        for market_code, market_info in self.MARKET_RULES.items():
            prefix = market_info['prefix']
            pattern = f"^{prefix}(\\d+)$"
            match = re.match(pattern, stock_code.upper())
            if match:
                clean_code = match.group(1)
                return clean_code
        
        print(f"❌ 股票代码 {stock_code} 没有有效的市场前缀")
        return None
    
    def validate_stock_code(self, stock_code: str) -> bool:
        """
        验证股票代码格式是否正确
        
        Args:
            stock_code: 股票代码
            
        Returns:
            bool: 是否有效
        """
        if not stock_code or not isinstance(stock_code, str):
            return False
        
        # 清理代码
        clean_code = re.sub(r'[^\d]', '', stock_code)
        
        # 检查是否为6位数字
        if not re.match(r'^\d{6}$', clean_code):
            return False
        
        # 检查是否属于已知市场
        return self.detect_market(clean_code) is not None
    
    def get_market_info(self, market_code: str) -> Optional[Dict]:
        """
        获取市场信息
        
        Args:
            market_code: 市场代码 (SH/SZ/BJ)
            
        Returns:
            Dict: 市场信息字典
        """
        if market_code in self.MARKET_RULES:
            return self.MARKET_RULES[market_code].copy()
        return None
    
    def get_all_markets(self) -> List[str]:
        """
        获取所有支持的市场代码
        
        Returns:
            List[str]: 市场代码列表
        """
        return list(self.MARKET_RULES.keys())
    
    def batch_detect_market(self, stock_codes: List[str]) -> Dict[str, Optional[str]]:
        """
        批量检测股票代码所属市场
        
        Args:
            stock_codes: 股票代码列表
            
        Returns:
            Dict[str, Optional[str]]: 股票代码到市场代码的映射
        """
        results = {}
        for code in stock_codes:
            results[code] = self.detect_market(code)
        return results
    
    def batch_add_prefix(self, stock_codes: List[str], lower_case: bool) -> Dict[str, Optional[str]]:
        """
        批量添加市场前缀
        
        Args:
            stock_codes: 股票代码列表
            
        Returns:
            Dict[str, Optional[str]]: 股票代码到带前缀代码的映射
        """
        results = {}
        for code in stock_codes:
            results[code] = self.add_market_prefix(code, lower_case)
        return results
    
    def get_stock_type(self, stock_code: str) -> Optional[str]:
        """
        获取股票类型
        
        Args:
            stock_code: 股票代码
            
        Returns:
            str: 股票类型 (主板/创业板/科创板/北交所/B股)
        """
        market = self.detect_market(stock_code)
        if not market:
            return None
        
        clean_code = re.sub(r'[^\d]', '', stock_code)
        
        if market == 'SH':
            if re.match(r'^60[0-5]\d{3}$', clean_code):
                return '主板'
            elif re.match(r'^688\d{3}$', clean_code):
                return '科创板'
            elif re.match(r'^900\d{3}$', clean_code):
                return 'B股'
        elif market == 'SZ':
            if re.match(r'^00[0-3]\d{3}$', clean_code):
                return '主板'
            elif re.match(r'^30[0-1]\d{3}$', clean_code):
                return '创业板'
            elif re.match(r'^200\d{3}$', clean_code):
                return 'B股'
        elif market == 'BJ':
            return '北交所'
        
        return '未知'

