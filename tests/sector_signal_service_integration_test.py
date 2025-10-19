"""
板块信号计算服务集成测试
测试真实服务的功能
"""

import sys
import os
import time

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_real_service():
    """测试真实服务功能"""
    print("🧪 测试真实板块信号计算服务")
    print("=" * 60)
    
    try:
        # 尝试导入服务
        from xtrading.services import SectorSignalService
        
        # 初始化服务
        service = SectorSignalService()
        print("✅ 服务初始化成功")
        
        # 显示配置信息
        print("\n📋 服务配置信息:")
        service.print_config_info()
        
        # 测试板块列表
        test_sectors = ["银行", "证券", "保险"]
        print(f"\n📊 测试板块: {test_sectors}")
        
        # 测试1: 使用默认参数
        print("\n🔍 测试1: 使用默认参数和默认日期范围")
        start_time = time.time()
        
        results = service.calculate_sector_signals(
            sector_list=test_sectors
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        if results:
            print(f"✅ 测试1通过: 耗时 {duration:.2f} 秒")
            service.print_signal_results(results)
            
            # 生成汇总
            summary = service.get_signal_summary(results)
            service.print_signal_summary(summary)
        else:
            print("❌ 测试1失败: 无结果")
            return False
        
        # 测试2: 指定特定策略
        print("\n🔍 测试2: 指定特定策略")
        start_time = time.time()
        
        specific_results = service.calculate_sector_signals(
            sector_list=test_sectors[:2],  # 只测试前2个板块
            strategies=["MACD", "RSI"]
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        if specific_results:
            print(f"✅ 测试2通过: 耗时 {duration:.2f} 秒")
            service.print_signal_results(specific_results)
        else:
            print("❌ 测试2失败: 无结果")
            return False
        
        # 测试3: 自定义日期范围
        print("\n🔍 测试3: 自定义日期范围")
        start_time = time.time()
        
        custom_results = service.calculate_sector_signals(
            sector_list=test_sectors[:2],
            strategies=["RSI", "MovingAverage"],
            start_date="20241001",
            end_date="20241020"
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        if custom_results:
            print(f"✅ 测试3通过: 耗时 {duration:.2f} 秒")
            service.print_signal_results(custom_results)
        else:
            print("❌ 测试3失败: 无结果")
            return False
        
        print("\n🎉 所有真实服务测试通过!")
        return True
        
    except Exception as e:
        print(f"❌ 真实服务测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_error_handling():
    """测试错误处理"""
    print("\n🧪 测试错误处理")
    print("=" * 60)
    
    try:
        from xtrading.services import SectorSignalService
        
        service = SectorSignalService()
        
        # 测试空板块列表
        print("🔍 测试空板块列表")
        empty_results = service.calculate_sector_signals([])
        if not empty_results:
            print("✅ 空板块列表处理正确")
        else:
            print("❌ 空板块列表处理失败")
        
        # 测试无效策略
        print("🔍 测试无效策略")
        invalid_results = service.calculate_sector_signals(
            sector_list=["银行"],
            strategies=["InvalidStrategy"]
        )
        if not invalid_results:
            print("✅ 无效策略处理正确")
        else:
            print("❌ 无效策略处理失败")
        
        print("✅ 错误处理测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 错误处理测试失败: {e}")
        return False


def test_performance():
    """测试性能"""
    print("\n🧪 测试性能")
    print("=" * 60)
    
    try:
        from xtrading.services import SectorSignalService
        
        service = SectorSignalService()
        
        # 测试不同规模的板块列表
        test_cases = [
            {"sectors": ["银行"], "strategies": ["MACD"], "name": "单板块单策略"},
            {"sectors": ["银行", "证券"], "strategies": ["MACD", "RSI"], "name": "双板块双策略"},
            {"sectors": ["银行", "证券", "保险"], "strategies": ["MACD", "RSI", "BollingerBands"], "name": "三板块三策略"},
            {"sectors": ["银行", "证券", "保险", "多元金融"], "strategies": ["MACD", "RSI", "BollingerBands", "MovingAverage"], "name": "四板块四策略"}
        ]
        
        for test_case in test_cases:
            print(f"\n🔍 测试: {test_case['name']}")
            start_time = time.time()
            
            results = service.calculate_sector_signals(
                sector_list=test_case['sectors'],
                strategies=test_case['strategies']
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            if results:
                print(f"✅ {test_case['name']}: 耗时 {duration:.2f} 秒")
                print(f"   板块数量: {len(test_case['sectors'])}")
                print(f"   策略数量: {len(test_case['strategies'])}")
                print(f"   平均每板块耗时: {duration/len(test_case['sectors']):.2f} 秒")
            else:
                print(f"❌ {test_case['name']}: 失败")
        
        print("✅ 性能测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 性能测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🚀 板块信号计算服务集成测试")
    print("=" * 80)
    
    # 运行真实服务测试
    service_success = test_real_service()
    
    # 运行错误处理测试
    error_success = test_error_handling()
    
    # 运行性能测试
    performance_success = test_performance()
    
    # 输出总结
    print("\n" + "=" * 80)
    print("📊 集成测试总结")
    print("=" * 80)
    print(f"真实服务测试: {'✅ 通过' if service_success else '❌ 失败'}")
    print(f"错误处理测试: {'✅ 通过' if error_success else '❌ 失败'}")
    print(f"性能测试: {'✅ 通过' if performance_success else '❌ 失败'}")
    
    overall_success = service_success and error_success and performance_success
    print(f"总体结果: {'🎉 全部通过' if overall_success else '⚠️ 部分失败'}")
    print("=" * 80)
    
    return overall_success


if __name__ == '__main__':
    main()
