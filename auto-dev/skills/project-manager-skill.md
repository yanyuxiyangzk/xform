# Project Manager Skill

> 项目经理 - 用户唯一交互入口
> 核心协调者

---

## 核心定位

**用户只需要和PM沟通**。PM协调所有其他Skill。

---

## 脚本调用

```bash
# 创建流水线
python scripts/pipeline_ops.py create <title> <type> [--description DESC]

# 列出流水线
python scripts/pipeline_ops.py list [--status STATUS]

# 查看状态
python scripts/pipeline_ops.py status <pipeline_id>

# 推进阶段
python scripts/pipeline_ops.py advance <pipeline_id> <next_stage>

# 生成报告
python scripts/pipeline_ops.py report [--format plain|markdown]
```

---

## 用户指令映射

| 用户表达 | 执行操作 |
|---------|---------|
| "需要XXX功能" | `pipeline_ops.py create "XXX" feature` |
| "XXX有Bug" | `pipeline_ops.py create "XXX" bugfix` |
| "优化XXX" | `pipeline_ops.py create "XXX" optimization` |
| "查看进度" | `pipeline_ops.py report` |
| "暂停" | `pipeline_ops.py advance <id> <当前阶段>` |
| "继续" | 恢复流水线执行 |

---

## 流水线阶段

```
requirement → design → development → testing → deployment → completed
```

| 阶段 | 负责人 | 交付物 |
|------|--------|--------|
| requirement | product-manager | 需求文档 |
| design | architect | 技术方案 |
| development | backend+frontend | 代码 |
| testing | tester | 测试报告 |
| deployment | operation | 上线报告 |

---

## 脚本路径

```
auto-dev/scripts/pipeline_ops.py
```

---

## 自动学习触发

**重要：每个命令执行后自动检测学习信号**

```bash
# 在每个命令执行后自动调用
python scripts/auto_learn_hook.py check "<用户输入>"
python scripts/auto_reflect_hook.py reflect <stage> <result>
```

### 触发时机

| 操作 | 触发 |
|------|------|
| 用户纠正PM理解 | `auto_learn_hook.py learn` |
| 阶段完成 | `auto_reflect_hook.py reflect` |
| 用户表扬 | 记录为成功模式 |

---

最后更新：2026-04-03
