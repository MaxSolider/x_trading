#!/bin/bash
# XTrading 自动执行脚本卸载程序

set -e

LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
PLIST_TARGET="$LAUNCH_AGENTS_DIR/com.xtrading.auto_run.plist"

echo "🗑️  XTrading 自动执行脚本卸载程序"
echo "=" | awk '{printf "=%.0s", $1; for(i=1; i<=50; i++) printf "="; print ""}'

# 卸载服务
if [ -f "$PLIST_TARGET" ]; then
    echo "🔄 卸载 launchd 服务..."
    if launchctl list | grep -q "com.xtrading.auto_run"; then
        launchctl unload "$PLIST_TARGET" 2>/dev/null || true
        echo "✅ 服务已卸载"
    else
        echo "ℹ️  服务未运行"
    fi
    
    # 删除 plist 文件
    echo "🗑️  删除 plist 文件..."
    rm "$PLIST_TARGET"
    echo "✅ plist 文件已删除"
else
    echo "ℹ️  未找到 plist 文件，可能已经卸载"
fi

echo ""
echo "✅ 卸载完成！"

