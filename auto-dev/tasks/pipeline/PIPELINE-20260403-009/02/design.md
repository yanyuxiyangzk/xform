# 技术方案：auto-dev自我完善

> 文档编号：DESIGN-20260403-009
> 流水线：PIPELINE-20260403-009
> 版本：v1.0
> 日期：2026-04-03

---

## 1. 总体架构

### 1.1 当前架构

```
Skills (Markdown) → 调用 → Scripts (Python)
                              ↓
                         Memory Files
```

### 1.2 优化后架构

```
┌─────────────────────────────────────────────────────┐
│                    Skills (Prompt)                  │
│              理解意图，生成命令调用                   │
└───────────────────────┬─────────────────────────────┘
                        │ 调用
                        ▼
┌─────────────────────────────────────────────────────┐
│                   Scripts (Python)                   │
│  pipeline_ops.py    orchestrator_ops.py             │
│  memory_ops.py      self_improve_ops.py             │
│  task_ops.py        knowledge_sync_ops.py           │
└───────────────────────┬─────────────────────────────┘
                        │ 执行
                        ▼
┌─────────────────────────────────────────────────────┐
│                  Memory (Files + DB)                │
│  ┌─────────────────┐  ┌─────────────────────────┐  │
│  │ 3-Layer Memory  │  │  Self-Improving Memory  │  │
│  │ episodic/       │  │  HOT/WARM/COLD         │  │
│  │ working/       │  │  memory.md             │  │
│  │ longterm/     │  │  corrections.md        │  │
│  └─────────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

---

## 2. 核心模块设计

### 2.1 自动学习触发器

**位置**：每个Skill处理完用户请求后自动触发

**触发条件**：
1. 用户纠正 ("不对，应该...")
2. 阶段完成
3. 发现错误

**执行流程**：
```python
#伪代码
def auto_learn(user_input, context):
    if is_correction(user_input):
        call("self_improve_ops.py learn", user_input)
    elif is_stage_complete(context):
        call("self_improve_ops.py reflect", context)
```

### 2.2 自我反思触发器

**位置**：pipeline每个阶段完成后自动触发

**触发时机**：
| 阶段 | 触发时机 | 反思内容 |
|------|---------|---------|
| 需求分析 | 生成需求文档后 | 需求理解是否有偏差 |
| 技术设计 | 生成设计方案后 | 设计是否合理 |
| 开发 | 代码提交后 | 是否有代码质量问题 |
| 测试 | 测试报告生成后 | 是否有遗漏 |
| 部署 | 上线后 | 是否有部署问题 |

### 2.3 记忆自动分层

**提升规则**：
| 从 | 到 | 条件 |
|----|----|------|
| episodic | working | access_count >= 5 AND age > 7天 |
| working | longterm | importance >= 7 OR access_count >= 10 |

**降级规则**：
| 从 | 到 | 条件 |
|----|----|------|
| working | episodic | age > 30天 AND importance < 5 |
| longterm | working | age > 90天 AND no reference |

---

## 3. 模块清单

### 3.1 新增模块

| 模块 | 文件 | 功能 |
|------|------|------|
| 学习触发器 | `auto_learn_hook.py` | 自动检测学习信号 |
| 反思触发器 | `auto_reflect_hook.py` | 阶段完成后自动反思 |
| 记忆守护 | `memory_daemon.py` | 定时执行遗忘/归档 |

### 3.2 优化模块

| 模块 | 优化内容 |
|------|---------|
| 所有Skills | 增加自动调用self_improve的指令 |
| pipeline_ops.py | 增加阶段完成自动触发 |
| orchestrator_ops.py | 增加心跳检查 |

---

## 4. 接口设计

### 4.1 自动学习接口

```python
# auto_learn_hook.py
def auto_learn(correction: str, context: str) -> str:
    """
    自动学习触发
    - correction: 用户的纠正内容
    - context: 发生纠正的上下文
    - return: 学习记录ID
    """
    call("self_improve_ops.py learn", correction, context)
```

### 4.2 自动反思接口

```python
# auto_reflect_hook.py
def auto_reflect(stage: str, result: str, issue: str = None) -> str:
    """
    自动反思触发
    - stage: 完成的阶段
    - result: 执行结果
    - issue: 发现的问题（可选）
    """
    reflection = f"{stage}完成: {result}"
    if issue:
        reflection += f", 问题: {issue}"
    call("self_improve_ops.py reflect", stage, reflection, get_lesson())
```

---

## 5. 数据流

### 5.1 学习数据流

```
用户纠正
    ↓
Skill识别意图
    ↓
调用 auto_learn_hook
    ↓
调用 self_improve_ops.py learn
    ↓
写入 self-improving/corrections.md
    ↓
3次重复后 → promote to memory.md (HOT)
```

### 5.2 反思数据流

```
Pipeline阶段完成
    ↓
Orchestrator检测
    ↓
调用 auto_reflect_hook
    ↓
调用 self_improve_ops.py reflect
    ↓
写入 self-improving/memory.md (Active Patterns)
    ↓
定期 → promote to Confirmed Preferences
```

---

## 6. 配置文件

### 6.1 auto-dev配置

```yaml
# auto-dev/config.yaml
auto_improve:
  enabled: true
  auto_learn: true
  auto_reflect: true
  auto_archive: true

  triggers:
    on_correction: true
    on_stage_complete: true
    on_error: true

  promotion:
    min_count: 3
    min_days: 7

  archive:
    older_than_days: 90
    min_importance: 5

heartbeat:
  interval_minutes: 10
  check_changes: true
```

---

## 7. 实施计划

### Phase 1: 基础激活 (今天)
- [x] 创建流水线 PIPELINE-20260403-009
- [x] 完成需求文档
- [ ] 完成技术方案
- [ ] 实现 auto_learn_hook.py
- [ ] 实现 auto_reflect_hook.py

### Phase 2: 集成测试 (明天)
- [ ] 所有Skills增加自动学习触发
- [ ] pipeline阶段完成自动反思
- [ ] 测试完整流程

### Phase 3: 优化完善 (本周)
- [ ] 记忆自动分层
- [ ] 遗忘机制激活
- [ ] 周报自动生成

---

## 8. 风险与应对

| 风险 | 影响 | 应对 |
|------|------|------|
| 学习噪音 | 记忆不准确 | 只记录显式纠正 |
| 过度反思 | token浪费 | 定期总结，不累积 |
| 遗忘有用记忆 | 知识丢失 | 设置最低重要性阈值 |

---

最后更新：2026-04-03
