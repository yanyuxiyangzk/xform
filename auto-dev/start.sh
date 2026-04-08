#!/bin/bash

# Auto-Dev Team 启动脚本
# 用于快速启动24小时自动开发系统

echo "=========================================="
echo "  RuoYi-Cloud-Nocode 自动开发系统"
echo "=========================================="

# 检查是否在正确目录
cd "d:/project/aicoding/item/ainocode" || exit 1

echo ""
echo "[1/4] 检查目录结构..."
if [ ! -d "auto-dev" ]; then
    echo "❌ auto-dev 目录不存在"
    exit 1
fi
echo "✅ 目录结构正常"

echo ""
echo "[2/4] 检查Agent定义..."
for agent in orchestrator backend-dev frontend-dev devops; do
    if [ ! -f "auto-dev/agents/${agent}.md" ]; then
        echo "❌ ${agent}.md 不存在"
        exit 1
    fi
done
echo "✅ Agent定义完整"

echo ""
echo "[3/4] 检查任务队列..."
for file in backlog in_progress completed blocked; do
    if [ ! -f "auto-dev/tasks/${file}.md" ]; then
        echo "❌ tasks/${file}.md 不存在"
        exit 1
    fi
done
echo "✅ 任务队列就绪"

echo ""
echo "[4/4] 检查记忆系统..."
if [ ! -f "auto-dev/memory/user/profile.md" ]; then
    echo "⚠️  用户偏好未配置，将使用默认设置"
fi
if [ ! -f "auto-dev/memory/project/state.md" ]; then
    echo "⚠️  项目状态未初始化"
fi
echo "✅ 记忆系统就绪"

echo ""
echo "=========================================="
echo "  准备启动..."
echo "=========================================="
echo ""
echo "启动方式:"
echo "  1. 启动完整团队 (推荐)"
echo "     claude-code --team auto-dev"
echo ""
echo "  2. 单独启动Orchestrator"
echo "     claude-code --agent orchestrator"
echo ""
echo "  3. 查看当前任务"
echo "     cat auto-dev/tasks/backlog.md"
echo ""
echo "=========================================="
echo ""
read -p "按 Enter 键启动 Orchestrator (Ctrl+C 退出)..."

# 启动Orchestrator
echo ""
echo "🚀 启动 Orchestrator..."
claude-code --agent orchestrator
