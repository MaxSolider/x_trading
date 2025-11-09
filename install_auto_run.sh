#!/bin/bash
# XTrading 自动执行脚本安装程序
# 用于配置 macOS 开机自启动和定时任务

set -e

# 获取脚本所在目录（项目根目录）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

echo "🚀 XTrading 自动执行脚本安装程序"
echo "=" | awk '{printf "=%.0s", $1; for(i=1; i<=50; i++) printf "="; print ""}'

# 1. 创建日志目录
echo "📁 创建日志目录..."
LOGS_DIR="$PROJECT_ROOT/logs"
mkdir -p "$LOGS_DIR"
echo "✅ 日志目录已创建: $LOGS_DIR"

# 2. 确保 auto_run.py 有执行权限
echo "🔧 设置 auto_run.py 执行权限..."
chmod +x "$PROJECT_ROOT/auto_run.py"
echo "✅ 执行权限已设置"

# 3. 检查虚拟环境
VENV_PYTHON="$PROJECT_ROOT/venv/bin/python"
if [ ! -f "$VENV_PYTHON" ]; then
    echo "⚠️  警告: 虚拟环境不存在，将使用系统 Python"
    PYTHON_PATH=$(which python3)
else
    PYTHON_PATH="$VENV_PYTHON"
    echo "✅ 找到虚拟环境: $VENV_PYTHON"
fi

# 4. 更新 plist 文件中的路径
echo "📝 更新 plist 配置文件..."
PLIST_SOURCE="$PROJECT_ROOT/com.xtrading.auto_run.plist"
PLIST_TEMP="$PROJECT_ROOT/com.xtrading.auto_run.plist.tmp"

# 使用 sed 替换路径（macOS 兼容）
# 转义 PROJECT_ROOT 中的特殊字符
ESCAPED_PROJECT_ROOT=$(echo "$PROJECT_ROOT" | sed 's/[[\.*^$()+?{|]/\\&/g')
ESCAPED_PYTHON_PATH=$(echo "$PYTHON_PATH" | sed 's/[[\.*^$()+?{|]/\\&/g')

# 替换项目路径
sed "s|/Users/liuzhenbing/Desktop/money/XTrading|$ESCAPED_PROJECT_ROOT|g" "$PLIST_SOURCE" > "$PLIST_TEMP"
mv "$PLIST_TEMP" "$PLIST_SOURCE"

# 更新 Python 路径（更精确的匹配）
sed -i '' "s|<string>.*/venv/bin/python</string>|<string>$ESCAPED_PYTHON_PATH</string>|g" "$PLIST_SOURCE"
sed -i '' "s|<string>.*python3</string>|<string>$ESCAPED_PYTHON_PATH</string>|g" "$PLIST_SOURCE"

echo "✅ plist 文件已更新"

# 5. 复制 plist 文件到 LaunchAgents 目录
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
PLIST_TARGET="$LAUNCH_AGENTS_DIR/com.xtrading.auto_run.plist"

echo "📋 复制 plist 文件到 LaunchAgents..."
mkdir -p "$LAUNCH_AGENTS_DIR"
cp "$PLIST_SOURCE" "$PLIST_TARGET"
echo "✅ plist 文件已复制到: $PLIST_TARGET"

# 6. 卸载旧的服务（如果存在）
echo "🔄 检查并卸载旧服务..."
if launchctl list | grep -q "com.xtrading.auto_run"; then
    launchctl unload "$PLIST_TARGET" 2>/dev/null || true
    echo "✅ 旧服务已卸载"
fi

# 7. 加载新服务
echo "🚀 加载 launchd 服务..."
launchctl load "$PLIST_TARGET"
echo "✅ 服务已加载"

# 8. 验证服务状态
echo ""
echo "=" | awk '{printf "=%.0s", $1; for(i=1; i<=50; i++) printf "="; print ""}'
echo "✅ 安装完成！"
echo ""
echo "📋 服务信息:"
echo "   - 服务名称: com.xtrading.auto_run"
echo "   - 执行时间: 每天下午 17:00"
echo "   - 日志目录: $LOGS_DIR"
echo ""
echo "🔍 查看服务状态:"
echo "   launchctl list | grep com.xtrading.auto_run"
echo ""
echo "📝 查看日志:"
echo "   tail -f $LOGS_DIR/auto_run.log"
echo ""
echo "🛑 卸载服务:"
echo "   launchctl unload $PLIST_TARGET"
echo "   rm $PLIST_TARGET"
echo ""

