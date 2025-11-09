#!/usr/bin/env python3
"""
自动执行脚本
判断当天是否为交易日，如果是则在下午5点执行 run.py
"""

import sys
import os
import subprocess
import datetime
from pathlib import Path

# 添加 src 目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'src'))

try:
    from xtrading.utils.date.date_utils import DateUtils
except ImportError as e:
    print(f"❌ 导入 DateUtils 失败: {e}")
    print("请确保在项目根目录下运行此脚本")
    sys.exit(1)


def is_today_trading_day() -> bool:
    """
    判断今天是否为交易日
    
    Returns:
        bool: 是否为交易日
    """
    try:
        # 获取今天的日期，格式为 YYYYMMDD
        today = datetime.datetime.now().strftime('%Y%m%d')
        
        # 使用 DateUtils 判断是否为交易日
        is_trading = DateUtils.is_trading_day(today)
        
        print(f"📅 今天是 {today}，是否为交易日: {'是' if is_trading else '否'}")
        return is_trading
    except Exception as e:
        print(f"❌ 判断交易日失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def execute_run_py():
    """
    执行 run.py 脚本
    """
    try:
        run_py_path = project_root / 'run.py'
        
        if not run_py_path.exists():
            print(f"❌ 找不到 run.py 文件: {run_py_path}")
            return False
        
        print(f"🚀 开始执行 run.py...")
        print("=" * 50)
        
        # 使用虚拟环境中的 Python 执行 run.py
        venv_python = project_root / 'venv' / 'bin' / 'python'
        
        if venv_python.exists():
            # 使用虚拟环境中的 Python
            result = subprocess.run(
                [str(venv_python), str(run_py_path)],
                cwd=str(project_root),
                capture_output=False
            )
        else:
            # 使用系统 Python
            result = subprocess.run(
                [sys.executable, str(run_py_path)],
                cwd=str(project_root),
                capture_output=False
            )
        
        if result.returncode == 0:
            print("=" * 50)
            print("✅ run.py 执行成功")
            return True
        else:
            print("=" * 50)
            print(f"⚠️ run.py 执行完成，返回码: {result.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ 执行 run.py 失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("=" * 50)
    print("🤖 自动执行脚本启动")
    print(f"⏰ 当前时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # 判断是否为交易日
    if not is_today_trading_day():
        print("ℹ️ 今天不是交易日，跳过执行")
        return
    
    # 执行 run.py
    print("\n✅ 今天是交易日，开始执行 run.py...")
    execute_run_py()


if __name__ == "__main__":
    main()

