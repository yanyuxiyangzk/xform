# Daily Routine — 日常自动化

> 早间简报、任务管理、晚间复盘、周回顾
> 触发词：今天任务、今日计划、晚间复盘、周回顾、总结

---

## 脚本调用

```bash
# 早间简报
python scripts/daily_routine_ops.py morning-brief

# 添加任务
python scripts/daily_routine_ops.py add-task <title> [--priority N] [--project NAME]

# 列出任务
python scripts/daily_routine_ops.py list-tasks [--status STATUS]

# 完成任务
python scripts/daily_routine_ops.py complete-task <task_id>

# 晚间复盘
python scripts/daily_routine_ops.py evening-review

# 周回顾
python scripts/daily_routine_ops.py weekly-review
```

---

## 用户指令映射

| 用户表达 | 执行操作 |
|---------|---------|
| "早间简报" | `morning-brief` |
| "添加任务XXX" | `add-task "XXX" --priority 5` |
| "完成任务XXX" | `complete-task <task_id>` |
| "晚间复盘" | `evening-review` |
| "周回顾" | `weekly-review` |

---

## 优先级

| 优先级 | 标签 | 说明 |
|--------|------|------|
| 9-10 | P0 | 紧急重要 |
| 7-8 | P1 | 重要 |
| 5-6 | P2 | 一般 |
| 1-4 | P3 | 低优先级 |

---

## 脚本路径

```
auto-dev/scripts/daily_routine_ops.py
```

---

## 自动学习触发

日常任务执行后自动反思：

```bash
# 早间简报后
python scripts/auto_reflect_hook.py reflect morning-brief "早间简报完成"

# 晚间复盘后
python scripts/auto_reflect_hook.py reflect evening-review "晚间复盘完成"

# 周回顾后
python scripts/auto_reflect_hook.py reflect weekly-review "周回顾完成"

# 添加任务后
python scripts/auto_reflect_hook.py reflect task "新任务添加"
```

---

最后更新：2026-04-03
