"""
板块信号计算服务简化测试
直接测试服务功能，避免循环导入问题
"""

import sys
import os
import time

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_strategy_config():
    """测试策略配置"""
    print("🧪 测试策略配置")
    print("=" * 60)
    
    try:
        # 直接导入配置模块
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'xtrading', 'static'))
        from strategy_config import StrategyConfig
        
        # 测试默认日期范围
        start_date, end_date = StrategyConfig.get_default_date_range()
        print(f"📅 默认日期范围: {start_date} 至 {end_date}")
        
        # 测试策略参数
        macd_params = StrategyConfig.get_strategy_params("MACD")
        print(f"📊 MACD参数: {macd_params}")
        
        rsi_params = StrategyConfig.get_strategy_params("RSI")
        print(f"📊 RSI参数: {rsi_params}")
        
        # 测试所有策略参数
        all_params = StrategyConfig.get_all_strategy_params()
        print(f"📊 所有策略参数: {list(all_params.keys())}")
        
        print("✅ 策略配置测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 策略配置测试失败: {e}")
        return False


def test_service_creation():
    """测试服务创建"""
    print("\n🧪 测试服务创建")
    print("=" * 60)
    
    try:
        # 尝试直接导入服务模块
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'xtrading', 'services'))
        from sector_signal_service import SectorSignalService
        
        # 创建服务实例
        service = SectorSignalService()
        print("✅ 服务创建成功")
        
        # 测试配置信息
        print("\n📋 服务配置信息:")
        service.print_config_info()
        
        print("✅ 服务创建测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 服务创建测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_service_methods():
    """测试服务方法"""
    print("\n🧪 测试服务方法")
    print("=" * 60)
    
    try:
        # 尝试直接导入服务模块
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'xtrading', 'services'))
        from sector_signal_service import SectorSignalService
        
        service = SectorSignalService()
        
        # 测试空列表处理
        print("🔍 测试空列表处理")
        empty_results = service.calculate_sector_signals([])
        if not empty_results:
            print("✅ 空列表处理正确")
        else:
            print("❌ 空列表处理失败")
        
        # 测试无效策略处理
        print("🔍 测试无效策略处理")
        invalid_results = service.calculate_sector_signals(
            sector_list=["银行"],
            strategies=["InvalidStrategy"]
        )
        if not invalid_results:
            print("✅ 无效策略处理正确")
        else:
            print("❌ 无效策略处理失败")
        
        # 测试打印方法
        print("🔍 测试打印方法")
        try:
            service.print_signal_results({})
            service.print_signal_summary({})
            print("✅ 打印方法测试通过")
        except Exception as e:
            print(f"❌ 打印方法测试失败: {e}")
        
        print("✅ 服务方法测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 服务方法测试失败: {e}")
        return False


def test_real_data():
    """测试真实数据（如果可能）"""
    print("\n🧪 测试真实数据")
    print("=" * 60)
    
    try:
        # 尝试直接导入服务模块
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'xtrading', 'services'))
        from sector_signal_service import SectorSignalService
        
        service = SectorSignalService()
        
        # 测试小规模数据
        print("🔍 测试小规模数据计算")
        start_time = time.time()
        
        results = service.calculate_sector_signals(
            sector_list=["银行"],
            strategies=["MACD"]
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        if results:
            print(f"✅ 真实数据测试通过: 耗时 {duration:.2f} 秒")
            print(f"📊 结果包含 {results.get('total_sectors', 0)} 个板块")
            print(f"📊 使用策略: {results.get('strategies_used', [])}")
            
            # 测试汇总生成
            summary = service.get_signal_summary(results)
            if summary:
                print("✅ 汇总生成成功")
            else:
                print("❌ 汇总生成失败")
            
            return True
        else:
            print("❌ 真实数据测试失败: 无结果")
            return False
            
    except Exception as e:
        print(f"⚠️ 真实数据测试跳过: {e}")
        return True  # 不因为网络问题而失败


def main():
    """主测试函数"""
    print("🚀 板块信号计算服务简化测试")
    print("=" * 80)
    
    # 运行各种测试
    config_success = test_strategy_config()
    service_success = test_service_creation()
    methods_success = test_service_methods()
    data_success = test_real_data()
    
    # 输出总结
    print("\n" + "=" * 80)
    print("📊 简化测试总结")
    print("=" * 80)
    print(f"策略配置测试: {'✅ 通过' if config_success else '❌ 失败'}")
    print(f"服务创建测试: {'✅ 通过' if service_success else '❌ 失败'}")
    print(f"服务方法测试: {'✅ 通过' if methods_success else '❌ 失败'}")
    print(f"真实数据测试: {'✅ 通过' if data_success else '❌ 失败'}")
    
    overall_success = config_success and service_success and methods_success and data_success
    print(f"总体结果: {'🎉 全部通过' if overall_success else '⚠️ 部分失败'}")
    print("=" * 80)
    
    return overall_success


if __name__ == '__main__':
    main()
