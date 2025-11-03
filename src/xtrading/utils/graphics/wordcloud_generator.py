"""
词云生成工具
提供词云图生成功能，用于新闻关键词可视化
"""

import os
from typing import Dict, Any, Optional
from datetime import datetime
import warnings


class WordCloudGenerator:
    """词云生成器工具类"""
    
    def __init__(self):
        """初始化词云生成器"""
        self._check_wordcloud_available()
    
    def _check_wordcloud_available(self):
        """检查wordcloud库是否可用"""
        try:
            import wordcloud
            self.wordcloud_available = True
        except ImportError:
            print("⚠️ wordcloud库未安装，词云功能将不可用。安装命令: pip install wordcloud")
            self.wordcloud_available = False
    
    def _find_chinese_font(self) -> Optional[str]:
        """
        查找可用的中文字体路径
        
        Returns:
            Optional[str]: 中文字体文件路径，如果未找到则返回None
        """
        try:
            import matplotlib.font_manager as fm
            import platform
            
            # 按优先级排序的字体列表（macOS 优先）
            if platform.system() == 'Darwin':  # macOS
                preferred_fonts = [
                    'STHeiti', 'PingFang SC', 'PingFang TC', 'PingFang HK',
                    'Hiragino Sans GB', 'Heiti SC', 'STSong', 'STKaiti'
                ]
            elif platform.system() == 'Windows':
                preferred_fonts = [
                    'SimHei', 'Microsoft YaHei', 'SimSun', 'KaiTi', 'FangSong'
                ]
            else:  # Linux
                preferred_fonts = [
                    'WenQuanYi Micro Hei', 'Noto Sans CJK SC', 
                    'WenQuanYi Zen Hei', 'AR PL UMing CN'
                ]
            
            # 添加通用字体
            all_fonts = preferred_fonts + [
                'Arial Unicode MS', 'SimHei', 'Microsoft YaHei'
            ]
            
            found_fonts = {}
            
            # 遍历所有字体，收集匹配的字体
            for font in fm.fontManager.ttflist:
                font_name_lower = font.name.lower()
                for preferred in all_fonts:
                    if preferred.lower() in font_name_lower:
                        if os.path.exists(font.fname):
                            # 避免重复添加相同路径的字体
                            if font.fname not in found_fonts.values():
                                found_fonts[preferred] = font.fname
                                break
            
            # 按优先级返回第一个找到的字体
            for preferred in preferred_fonts:
                if preferred in found_fonts:
                    font_path = found_fonts[preferred]
                    print(f"✅ 找到中文字体: {preferred} ({font_path})")
                    return font_path
            
            # 如果没有找到优先字体，返回任意找到的中文字体
            if found_fonts:
                first_font = list(found_fonts.items())[0]
                print(f"✅ 找到中文字体（备用）: {first_font[0]} ({first_font[1]})")
                return first_font[1]
            
            # 最后的备用方案：查找包含中文相关关键词的字体
            for font in fm.fontManager.ttflist:
                font_name_lower = font.name.lower()
                if any(keyword in font_name_lower for keyword in ['hei', 'song', 'kai', 'fang', 'ming', 'sc', 'tc']):
                    if os.path.exists(font.fname):
                        print(f"✅ 找到中文字体（备用）: {font.name} ({font.fname})")
                        return font.fname
            
            print("⚠️ 未找到中文字体，将使用默认字体（可能无法正确显示中文）")
            return None
            
        except Exception as e:
            print(f"⚠️ 查找中文字体失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def generate_wordcloud(self, 
                          word_freq: Dict[str, int],
                          output_path: str,
                          title: str = "关键词词云",
                          width: int = 1200,
                          height: int = 800,
                          max_words: int = 200) -> Optional[str]:
        """
        生成词云图
        
        Args:
            word_freq: 词频字典 {词: 频次}
            output_path: 输出文件路径
            title: 图表标题
            width: 图片宽度
            height: 图片高度
            max_words: 最大显示词数
            
        Returns:
            str: 生成的图片文件路径，失败时返回None
        """
        try:
            if not self.wordcloud_available:
                print("❌ wordcloud库未安装，无法生成词云图")
                return None
            
            from wordcloud import WordCloud
            import matplotlib.pyplot as plt
            import matplotlib
            # 使用非交互式后端
            matplotlib.use('Agg')
            
            # 设置matplotlib中文字体
            plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'STHeiti', 'PingFang SC', 'Arial Unicode MS', 'DejaVu Sans', 'Arial']
            plt.rcParams['axes.unicode_minus'] = False
            
            if not word_freq:
                print("❌ 词频数据为空，无法生成词云图")
                return None
            
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            # 查找中文字体路径
            font_path = self._find_chinese_font()
            
            # 创建词云对象
            wordcloud_params = {
                'width': width,
                'height': height,
                'background_color': 'white',
                'max_words': max_words,
                'relative_scaling': 0.5,
                'colormap': 'viridis',
                'prefer_horizontal': 0.7,
                'min_font_size': 10,
                'max_font_size': 100
            }
            
            # 如果找到中文字体，则指定字体路径
            if font_path:
                wordcloud_params['font_path'] = font_path
            else:
                print("⚠️ 未指定中文字体路径，词云可能无法正确显示中文")
            
            wordcloud = WordCloud(**wordcloud_params)
            
            # 生成词云
            wordcloud.generate_from_frequencies(word_freq)
            
            # 创建图形
            plt.figure(figsize=(12, 8))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.title(title, fontsize=16, fontweight='bold', pad=20)
            plt.tight_layout(pad=0)
            
            # 保存图片
            plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            print(f"✅ 词云图已保存: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ 生成词云图失败: {e}")
            import traceback
            traceback.print_exc()
            return None

