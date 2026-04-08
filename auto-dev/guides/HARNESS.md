# Auto-Dev Harness Architecture

## 架构概览

```
┌─────────────────────────────────────────────────────────────────┐
│                         Auto-Dev 2.0                              │
│                      Harness Engineering                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────┐         ┌─────────────┐                        │
│   │   Guides    │ ────── │   Sensors   │                        │
│   │  (引导层)   │         │  (感知层)   │                        │
│   │  前馈控制   │ ←───── │  反馈控制   │                        │
│   └─────────────┘         └─────────────┘                        │
│         ↑                       ↓                                │
│         │                       │                                │
│         └───────────┬───────────┘                                │
│                     ↓                                            │
│            ┌─────────────────┐                                    │
│            │     Memory     │                                    │
│            │   (记忆层)      │                                    │
│            └─────────────────┘                                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 目录结构

```
auto-dev/
├── guides/                     # 引导层 (Guides)
│   ├── rules/                 # 规则约束
│   │   ├── CLAUDE.md
│   │   ├── RULES.md
│   │   └── domain-rules/     # 领域规则
│   ├── tools/                 # 工具能力
│   │   ├── scripts/          # CLI 脚本
│   │   └── skills/           # Skill 定义
│   └── schemas/               # 类型化约束
│       ├── pipeline.schema.json
│       ├── memory.schema.json
│       ├── agent.schema.json
│       └── task.schema.json
│
├── sensors/                    # 感知层 (Sensors)
│   ├── static/               # 静态校验
│   │   ├── rule_guard.py     # 规则守卫
│   │   ├── quality_gate.py    # 质量门禁
│   │   └── reviewer.py       # 代码审核
│   └── runtime/              # 运行观测
│       ├── checkpoint_ops.py  # 断点持久化
│       ├── auto_heartbeat.py  # 心跳监控
│       └── telemetry/         # 遥测系统
│
├── memory/                    # 记忆层
│   ├── hot/                  # 热记忆 (≤100行，始终加载)
│   ├── warm/                 # 温记忆 (≤200行，按需加载)
│   └── cold/                 # 冷记忆 (归档)
│
└── scripts/                   # 核心脚本
    ├── pipeline_runner.py     # 流水线运行器
    ├── agent_spawner.py       # Agent 启动器
    ├── orchestrator_ops.py    # 编排器
    └── start_dev.py           # 入口
```

## Guides (引导层)

为编码智能体提供**前馈 (feedforward)** 约束与工具：

### 规则约束
- `CLAUDE.md` - Claude Code 启动配置
- `RULES.md` - 开发规则
- `domain-rules/` - 领域特定规则

### 工具能力
- `scripts/` - 45+ CLI 脚本
- `skills/` - 13 Skill 定义

### 类型化约束
- JSON Schema 校验
- 编译期错误发现
- 结构化输出保证

## Sensors (感知层)

为编码智能体提供**反馈 (feedback)** 运行时监控与纠错：

### 静态校验
- `rule_guard.py` - 规则守卫 (StuckDetector + SelfHealer)
- `quality_gate.py` - 质量门禁 (编译 + 测试 + 安全)
- `reviewer.py` - 代码审核 (最多3次迭代)

### 运行观测
- `checkpoint_ops.py` - 断点保存/恢复
- `auto_heartbeat.py` - 10分钟心跳守护
- `telemetry/` - 全链路可观测 (日志 + 追踪 + 指标)

## Memory (记忆层)

三层记忆自动管理：

| 层级 | 容量 | 加载方式 | 用途 |
|------|------|---------|------|
| HOT | ≤100行 | 始终加载 | 全局规则、最近状态 |
| WARM | ≤200行 | 按需加载 | 项目知识、决策记录 |
| COLD | 无限制 | 需要时加载 | 历史归档、长期积累 |

### 层级管理策略
- **promote**: cold → warm → hot (访问频率增加)
- **demote**: hot → warm → cold (访问频率降低)
- **compact**: 热层超限时自动整理
- **cleanup**: 冷层定期清理 (默认90天)

## 闭环逻辑

```
1. Guides 提供前馈约束
   ↓
2. Agent 执行开发任务
   ↓
3. Sensors 收集运行时数据
   ↓
4. Quality Gate 质量检查
   ↓
5. Reviewer 代码审核 (最多3次)
   ↓
6. 通过 → Memory 记录
   ↓
7. 失败 → SelfHealer 自愈 / 模型升级
   ↓
8. 阻塞 → 人工介入
```

## 核心流程

### 自动化开发流程
```
start_dev.py auto "需求描述"
    ↓
pipeline_runner.py init
    ↓
agent_spawner.py spawn-team dev-team
    ↓
Pipeline Stages:
  requirement → design → development → testing → deployment
    ↓
Quality Gate (每个阶段后)
    ↓
Reviewer (development 后, 最多3次迭代)
    ↓
Checkpoint Save (定期 + 完成时)
    ↓
Auto Heartbeat (持续监控)
```

### 质量门禁检查项
1. 编译检查 (mvn compile)
2. 测试检查 (mvn test, ≥90% 通过率)
3. 安全扫描 (dependency-analyze, spotbugs)
4. 代码风格 (checkstyle)
5. 禁止操作检查 (删除核心文件等 P0 违规)

### 异常处理
| 等级 | 条件 | 处理 |
|------|------|------|
| P0 | 安全违规、删除核心 | 立即停止 |
| P1 | 编译失败、测试失败 | 阻止通过 |
| P2 | 命名不规范 | 警告 |

## 全链路可观测

```
日志 (Logs)
├── 级别: DEBUG, INFO, WARN, ERROR, CRITICAL
├── 分类: trace, metric, event, error
└── 输出: JSONL 文件

追踪 (Traces)
├── Trace ID: 全局唯一请求链
├── Span ID: 父子跨度
└── 树形结构展示

指标 (Metrics)
├── Counter: 事件计数
├── Gauge: 当前值
├── Histogram: 分布
└── Summary: 聚合统计
```

## 版本
- 更新: 2026-04-06
- 架构: Harness Engineering v2.0
