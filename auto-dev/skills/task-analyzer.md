# Task Analyzer — 任务分析与执行

> 分解复杂任务、智能路由、自主执行
> 触发词：分析任务、制定计划、执行、自动处理、分解任务

---

## Skill 信息

| 属性 | 值 |
|------|-----|
| name | task-analyzer |
| description | 任务分析器，分解复杂任务并自主执行 |
| trigger | 分析任务/制定计划/执行/自动处理/分解任务 |

---

## 核心能力

当用户说以下内容时，调用Python脚本执行：

| 用户表达 | 触发操作 | 命令 |
|---------|---------|------|
| "创建任务..." | create | `python task_ops.py create <标题> <描述>` |
| "列出任务" | list | `python task_ops.py list [--status STATUS]` |
| "更新任务状态" | update | `python task_ops.py update <task_id> --status <状态>` |
| "分析任务..." | analyze | `python task_ops.py analyze <任务描述>` |
| "分解任务" | breakdown | `python task_ops.py breakdown <task_id>` |

---

## create 命令

**命令格式：**
```bash
python task_ops.py create <title> <description> [--priority N] [--type TYPE] [--owner NAME]
```

**参数说明：**
- `title`: 任务标题
- `description`: 任务描述
- `--priority`: 优先级1-10（可选，默认5）
- `--type`: 类型 - feature/bugfix/optimization/refactor/docs/test
- `--owner`: 负责人（可选）

**示例：**
```bash
python task_ops.py create "完成用户模块" "实现用户CRUD功能" --priority 8 --type feature
python task_ops.py create "修复登录问题" "用户反馈登录失败" --priority 9 --type bugfix
```

---

## list 命令

**命令格式：**
```bash
python task_ops.py list [--status STATUS] [--limit N]
```

**状态选项：**
- `pending` - 待处理
- `in_progress` - 进行中
- `completed` - 已完成
- `blocked` - 阻塞
- `cancelled` - 已取消

**示例：**
```bash
python task_ops.py list --limit 10
python task_ops.py list --status in_progress
python task_ops.py list --status pending --limit 20
```

---

## update 命令

**命令格式：**
```bash
python task_ops.py update <task_id> --status <new_status>
```

**示例：**
```bash
python task_ops.py update TASK-20260403-001 --status in_progress
python task_ops.py update TASK-20260403-001 --status completed
```

---

## analyze 命令

**命令格式：**
```bash
python task_ops.py analyze <task_description>
```

**示例：**
```bash
python task_ops.py analyze "需要实现一个用户登录功能，包括注册、登录、找回密码"
```

**输出示例：**
```
📊 任务分析: 需要实现一个用户登录功能
============================================================
复杂度: medium
建议优先级: P5
建议类型: feature
所需技能: java, database

建议子任务:
  1. 需求澄清与确认
  2. 技术方案设计
  3. 数据库/接口设计
  4. 代码实现
  5. 单元测试
  6. 联调测试
  7. 功能验证
  8. 文档更新
```

---

## breakdown 命令

**命令格式：**
```bash
python task_ops.py breakdown <task_id>
```

**示例：**
```bash
python task_ops.py breakdown TASK-20260403-001
```

**说明：** 根据任务类型自动分解为多个子任务，并创建子任务。

---

## 优先级说明

| 优先级 | 标识 | 说明 |
|--------|------|------|
| 9-10 | P0 | 紧急重要，业务关键 |
| 7-8 | P1 | 重要任务 |
| 5-6 | P2 | 一般任务 |
| 1-4 | P3 | 低优先级 |

---

## 任务路由

根据分析结果，路由到对应Agent：

| 任务类型 | 路由到 | 说明 |
|----------|--------|------|
| 需求分析 | product-manager | 需求文档编写 |
| 技术设计 | architect | 架构设计 |
| 后端开发 | backend-dev | Java/Spring |
| 前端开发 | frontend-dev | Vue3/TS |
| 测试 | tester | 测试用例 |
| 部署 | devops | CI/CD |
| 上线 | operation | 运维 |

---

## 任务分解模式

```
1. 顺序模式：Context → Collect → Analyze → Generate → Deliver
2. 并行模式：TaskA ∥ TaskB ∥ TaskC → Merge → Deliver
3. 树形模式：Root → Sub1 → Sub1.1, Sub1.2 → 汇总
4. 流水线：Input → Stage1 → Stage2 → Stage3 → Output
5. 验证循环：Do → Verify → Fix → Verify → Done
```

---

## 使用示例

```
用户: 创建一个任务，实现商品模块的增删改查

→ 解析意图: create
→ 构建命令:
  python task_ops.py create "商品模块CRUD" "实现商品的增删改查功能" --priority 7 --type feature

---

用户: 分析一下这个需求：实现订单支付功能

→ 解析意图: analyze
→ 构建命令:
  python task_ops.py analyze "实现订单支付功能，支持多种支付方式"

输出:
  复杂度: medium
  建议优先级: P6
  建议类型: feature
  建议子任务: [需求确认, 技术方案, 数据库设计, ...]

---

用户: 分解 TASK-20260403-001 这个任务

→ 解析意图: breakdown
→ 构建命令:
  python task_ops.py breakdown TASK-20260403-001

输出:
  ✅ 任务已分解: TASK-20260403-001
  生成 8 个子任务
```

---

## 脚本路径

```
auto-dev/scripts/task_ops.py
```

---

## 自动学习触发

任务分析后自动反思：

```bash
# 任务分析
python scripts/task_ops.py analyze "<任务>"

# 任务分解
python scripts/task_ops.py breakdown <task_id>

# 分析后反思
python scripts/auto_reflect_hook.py reflect task-analysis "任务分析完成"
```

---

最后更新：2026-04-03
