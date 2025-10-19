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
