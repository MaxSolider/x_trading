#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将backtest目录下的英文文件夹和文件名重命名为中文名称
解决Windows下中文文件名乱码问题
"""

import os
import shutil
from pathlib import Path

# 文件夹名称映射表
FOLDER_MAPPING = {
    # 一级分类
    'agriculture': '农业',
    'basic_materials': '基础材料',
    'construction': '建筑',
    'consumer': '消费',
    'energy': '能源',
    'environmental': '环保',
    'finance': '金融',
    'healthcare': '医疗',
    'industry': '工业',
    'others': '其他',
    'technology': '科技',
    
    # 农业子分类
    'agricultural_processing': '农产品加工',
    'livestock': '畜牧业',
    'planting_forestry': '种植林业',
    
    # 基础材料子分类
    'agrochemicals': '农用化工',
    'chemical_fibers': '化纤',
    'chemical_pharmaceuticals': '化学制药',
    'chemical_products': '化工产品',
    'chemical_raw_materials': '化工原料',
    'coal_mining_processing': '煤炭开采加工',
    'energy_metals': '能源金属',
    'industrial_metals': '工业金属',
    'metal_new_materials': '金属新材料',
    'minor_metals': '小金属',
    'non_metallic_materials': '非金属材料',
    'petroleum_processing_trade': '石油加工贸易',
    'precious_metals': '贵金属',
    'rubber_products': '橡胶制品',
    'steel': '钢铁',
    
    # 建筑子分类
    'building_decoration': '建筑装饰',
    'building_materials': '建筑材料',
    
    # 消费子分类
    'beauty_care': '美容护理',
    'beverage_manufacturing': '饮料制造',
    'black_goods': '黑色家电',
    'clothing_textiles': '服装纺织',
    'consumer_electronics': '消费电子',
    'cultural_media': '文化传媒',
    'film_cinema': '影视院线',
    'food_processing': '食品加工',
    'home_goods': '家居用品',
    'kitchen_bathroom_appliances': '厨卫电器',
    'liquor': '酒类',
    'paper_making': '造纸',
    'retail': '零售',
    'small_appliances': '小家电',
    'tourism_hotels': '旅游酒店',
    'trade': '贸易',
    'white_goods': '白色家电',
    
    # 能源子分类
    'batteries': '电池',
    'gas': '燃气',
    'oil_gas_extraction_services': '油气开采服务',
    'power': '电力',
    
    # 环保子分类
    'environmental_equipment': '环保设备',
    'environmental_governance': '环保治理',
    
    # 金融子分类
    'banking': '银行',
    'diversified_finance': '多元金融',
    'insurance': '保险',
    'securities': '证券',
    
    # 医疗子分类
    'biological_products': '生物制品',
    'medical_devices': '医疗器械',
    'medical_services': '医疗服务',
    'pharmaceutical_commerce': '医药商业',
    'traditional_medicine': '中药',
    
    # 工业子分类
    'airport_shipping': '机场航运',
    'automation_equipment': '自动化设备',
    'automotive_parts': '汽车零部件',
    'automotive_services_others': '汽车服务其他',
    'automotive_vehicles': '汽车整车',
    'construction_machinery': '工程机械',
    'military_equipment': '军工装备',
    'motors': '电机',
    'other_power_equipment': '其他电力设备',
    'photovoltaic_equipment': '光伏设备',
    'port_shipping': '港口航运',
    'power_grid_equipment': '电网设备',
    'rail_transit_equipment': '轨道交通设备',
    'road_rail_transport': '公路铁路运输',
    'specialized_equipment': '专用设备',
    'wind_power_equipment': '风电设备',
    
    # 其他子分类
    'comprehensive': '综合',
    'education': '教育',
    'gaming': '游戏',
    'general_equipment': '通用设备',
    'logistics': '物流',
    'military_electronics': '军工电子',
    'other_social_services': '其他社会服务',
    'packaging_printing': '包装印刷',
    'plastic_products': '塑料制品',
    'real_estate': '房地产',
    'textile_manufacturing': '纺织制造',
    
    # 科技子分类
    'communication_equipment': '通信设备',
    'communication_services': '通信服务',
    'components': '元器件',
    'computer_equipment': '计算机设备',
    'electronic_chemicals': '电子化学品',
    'internet_ecommerce': '互联网电商',
    'it_services': 'IT服务',
    'optical_optoelectronics': '光学光电子',
    'other_electronics': '其他电子',
    'semiconductors': '半导体',
    'software_development': '软件开发',
}

# 文件名映射表
FILE_MAPPING = {
    '回测报告.md': '回测报告.md',
    '收益率数据明细表.xlsx': '收益率数据明细表.xlsx',
    '每日收益率折线图.png': '每日收益率折线图.png',
    '累计收益率折线图.png': '累计收益率折线图.png',
}

def rename_folders_and_files(root_path):
    """
    递归重命名文件夹和文件
    """
    root_path = Path(root_path)
    
    # 首先处理文件夹
    for item in root_path.rglob('*'):
        if item.is_dir():
            old_name = item.name
            if old_name in FOLDER_MAPPING:
                new_name = FOLDER_MAPPING[old_name]
                new_path = item.parent / new_name
                
                print(f"重命名文件夹: {item} -> {new_path}")
                try:
                    item.rename(new_path)
                except Exception as e:
                    print(f"重命名文件夹失败 {item}: {e}")
    
    # 然后处理文件
    for item in root_path.rglob('*'):
        if item.is_file():
            old_name = item.name
            if old_name in FILE_MAPPING:
                new_name = FILE_MAPPING[old_name]
                new_path = item.parent / new_name
                
                print(f"重命名文件: {item} -> {new_path}")
                try:
                    item.rename(new_path)
                except Exception as e:
                    print(f"重命名文件失败 {item}: {e}")

def create_backup_and_rename(backtest_path):
    """
    创建备份并执行重命名
    """
    backtest_path = Path(backtest_path)
    backup_path = backtest_path.parent / f"{backtest_path.name}_backup"
    
    print(f"创建备份目录: {backup_path}")
    if backup_path.exists():
        shutil.rmtree(backup_path)
    shutil.copytree(backtest_path, backup_path)
    
    print("开始重命名...")
    rename_folders_and_files(backtest_path)
    print("重命名完成！")

def main():
    """
    主函数
    """
    # 设置backtest目录路径
    backtest_path = Path(__file__).parent / "tests" / "backtest"
    
    if not backtest_path.exists():
        print(f"错误: 找不到目录 {backtest_path}")
        return
    
    print(f"准备重命名目录: {backtest_path}")
    print("这将把英文文件夹和文件名转换为中文名称")
    print("原目录将被备份")
    
    # 确认操作
    confirm = input("是否继续？(y/N): ").strip().lower()
    if confirm != 'y':
        print("操作已取消")
        return
    
    create_backup_and_rename(backtest_path)

if __name__ == "__main__":
    main()
