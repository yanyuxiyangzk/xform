# Self-Improving Skill — 自我反思 + 自我批评 + 自我学习 + 自我组织

> 越用越聪明的记忆系统
> Agent评估自己的输出，捕捉错误，永久改进
> 触发词：反思、复盘、自查、改进、学习

---

## 核心定位

**越用越聪明的自我改进系统**。每次工作后反思，捕捉错误，从修正中学习，永久保存改进。

---

## 触发场景

| 场景 | 示例 | 操作 |
|------|------|------|
| 用户纠正 | "不对，应该这样做..." | `learn` 记录修正 |
| 完成重要工作 | 刚完成一个功能 | `reflect` 自我反思 |
| 发现错误 | 意识到自己有问题 | `learn` + `reflect` |
| 重复错误 | 第N次被纠正同样的问题 | `promote` 到确认 |
| 用户表扬 | "这样很好，继续" | 记录为成功模式 |

---

## 脚本调用

```bash
# 记录修正/学习
python scripts/self_improve_ops.py learn "不用X，应该用Y" --type technical --context "开发中"

# 自我反思
python scripts/self_improve_ops.py reflect "<任务类型>" "<反思内容>" "<改进点>"

# 查看统计
python scripts/self_improve_ops.py stats

# 搜索记忆
python scripts/self_improve_ops.py search <关键词>

# 提升层级 (3次重复后确认)
python scripts/self_improve_ops.py promote <entry_id>

# 归档不活跃条目
python scripts/self_improve_ops.py archive <entry_id>

# 心跳检查
python scripts/self_improve_ops.py heartbeat

# 显示记忆
python scripts/self_improve_ops.py show [--tier HOT|WARM|COLD]
```

---

## 层级架构

```
🔥 HOT (memory.md)         ≤100行，始终加载
   └── Confirmed Preferences - 用户确认的偏好
   └── Active Patterns       - 活跃模式

🌡️ WARM (projects/ + domains/)
   └── projects/{name}.md   - 项目特定模式
   └── domains/code.md      - 技术模式
   └── domains/comms.md     - 沟通模式

❄️ COLD (archive/)         归档，长期保留
```

---

## 学习信号

### ✅ 记录（显式修正）
```
- "No, that's not right..."
- "Actually, it should be..."
- "I prefer X, not Y"
- "Always do X for me"
- "Never do Y"
```

### ✅ 记录（偏好信号）
```
- "I like when you..."
- "Remember that I always..."
- "For this project, use..."
```

### ❌ 不记录
- 一次性的指令
- 特定上下文的指点
- 假设性讨论

---

## 自我反思格式

完成重要工作后，调用 reflect：

```bash
python self_improve_ops.py reflect "任务类型" "反思内容" "改进点"
```

示例：
```bash
python self_improve_ops.py reflect "完成Liquor编译功能" \
  "编译成功但调试信息不够详细" \
  "以后实现编译功能时同时输出调试信息"
```

---

## 升级规则

| 次数 | 状态 | 操作 |
|------|------|------|
| 1次修正 | tentative | 观察 |
| 2次修正 | emerging | 继续观察 |
| 3次修正 | pending | 请求确认 |
| 确认后 | confirmed | 永久保存 |

---

## 与现有记忆系统融合

```
auto-dev/memory/      ← 3层记忆系统（事实、上下文）
auto-dev/self-improving/ ← 自我改进记忆（执行质量）

分工：
- memory/     → 事件、决策、上下文（事实性）
- self-improving/ → 偏好、工作流、改进（执行质量）
```

---

## 用户指令映射

| 用户说 | 执行 |
|--------|------|
| "记住这个偏好..." | `learn --type preference` |
| "反思一下刚才的工作" | `reflect` |
| "你之前犯过什么错" | `search 错误` |
| "看看我的学习记录" | `show --tier HOT` |
| "我之前的模式是什么" | `show --tier WARM` |

---

## 集成到开发流程

在每个pipeline阶段后自动触发：

```
需求分析完成 → self-improve → 记录需求理解偏差
技术设计完成 → self-improve → 记录设计方案问题
开发完成     → self-improve → 记录代码质量问题
测试完成     → self-improve → 记录测试遗漏
上线完成     → self-improve → 记录部署问题
```

---

## 脚本路径

```
auto-dev/scripts/self_improve_ops.py
auto-dev/self-improving/
  ├── memory.md          # HOT层
  ├── corrections.md     # 修正日志
  ├── index.md          # 索引
  ├── heartbeat-state.md # 心跳状态
  ├── projects/          # 项目记忆
  ├── domains/          # 领域记忆
  └── archive/          # 归档
```

---

## 自动学习触发

自我改进系统是**越用越聪明**的核心，所有Skills都应调用它：

```bash
# 每次用户纠正后
python scripts/auto_learn_hook.py learn "<纠正内容>" --type TYPE --context CONTEXT

# 每个阶段完成后
python scripts/auto_reflect_hook.py reflect <stage> "<结果>"

# 心跳检查
python scripts/auto_heartbeat.py check

# 归档检查
python scripts/auto_archive_hook.py check
```

### 核心价值

1. **学习信号自动捕获** - 每次纠正自动记录
2. **反思自动生成** - 每次完成自动总结
3. **模式自动提炼** - 3次重复自动确认
4. **遗忘自动归档** - 低价值自动清理

---

最后更新：2026-04-03
