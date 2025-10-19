#!/usr/bin/env python3
"""
XTrading 启动脚本
负责环境检查、依赖管理和程序启动
"""

import sys
import os
import subprocess
import venv
from pathlib import Path


def check_and_create_venv():
    """检查并创建虚拟环境"""
    venv_path = Path("venv")
    if not venv_path.exists():
        print("📦 创建虚拟环境...")
        venv.create("venv", with_pip=True)
        print("✅ 虚拟环境创建成功")
    else:
        print("✅ 虚拟环境已存在")


def upgrade_akshare():
    """升级AKShare到最新版本"""
    print("🔄 正在升级AKShare到最新版本...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "akshare", "--upgrade", 
            "-i", "https://pypi.org/simple"
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ AKShare升级成功")
            return True
        else:
            print(f"⚠️ AKShare升级失败: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("⚠️ AKShare升级超时，继续使用当前版本")
        return False
    except Exception as e:
        print(f"⚠️ AKShare升级出错: {e}")
        return False


def main():
    """主启动函数"""
    print("🚀 AKShare股票日线数据查询工具")
    print("=" * 50)
    
    # 检查是否已经在虚拟环境中运行
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ 已在虚拟环境中运行")
        # 已经在虚拟环境中，直接运行主程序
        run_main_program()
    else:
        # 检查虚拟环境
        check_and_create_venv()
        
        # 激活虚拟环境
        venv_python = os.path.join(os.path.dirname(__file__), 'venv', 'bin', 'python')
        if os.path.exists(venv_python):
            print("🔄 使用虚拟环境中的Python...")
            # 使用虚拟环境中的Python重新运行脚本
            subprocess.run([venv_python, __file__])
            return
        else:
            print("⚠️ 虚拟环境不存在，使用系统Python运行")
            run_main_program()


def run_main_program():
    """运行主程序"""
    # 升级AKShare
    upgrade_akshare()
    print()
    
    # 添加src目录到Python路径
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    
    # 配置pandas全局显示选项
    try:
        from src.xtrading.utils.pandas.pandas_config import configure_pandas_display
        configure_pandas_display()
    except ImportError as e:
        print(f"⚠️ 无法加载pandas配置: {e}")
    
    # 导入并运行主程序
    try:
        from src.xtrading.main import main as app_main
        app_main()
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保所有依赖已正确安装")
    except Exception as e:
        print(f"❌ 启动失败: {e}")


if __name__ == "__main__":
    main()
