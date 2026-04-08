# 任务队列系统

> 本目录用于持久化任务状态，支持断点续传和多Agent协作
> 最后更新：2026-04-02

---

## 目录说明

| 文件 | 说明 |
|------|------|
| `backlog.md` | 待办任务池（按优先级排序） |
| `in_progress.md` | 正在进行中的任务 |
| `completed.md` | 已完成的任务 |
| `blocked.md` | 阻塞/等待用户决策的任务 |

---

## 任务卡片格式

```markdown
# 任务卡片

## 基本信息
- ID: TASK-YYYYMMDD-NNN
- 标题: [任务标题]
- 类型: feature | bugfix | research | optimization
- 优先级: P0 | P1 | P2
- 创建时间: YYYY-MM-DD HH:mm
- 最后更新: YYYY-MM-DD HH:mm
- 负责人: orchestrator | backend-dev | frontend-dev | devops

## 任务详情
- **目标**: [清晰的目标描述]
- **验收标准**:
  - [ ] 标准1
  - [ ] 标准2
- **影响范围**: [影响的模块或功能]
- **风险等级**: 低 | 中 | 高

## 依赖关系
- 前置任务: [TASK-ID] 或 无
- 依赖任务: [TASK-ID] 或 无

## 执行记录
| 时间 | 操作 | 执行者 | 结果 |
|------|------|--------|------|
| MM-DD HH:mm | 开始 | backend-dev | - |
| MM-DD HH:mm | 完成 | backend-dev | ✅ |

## 状态
状态: pending | in_progress | completed | blocked
```

---

## 状态流转

```
                    ┌─────────────┐
                    │   创建任务   │
                    └──────┬──────┘
                           │
                           ▼
┌─────────────────────────────────────────┐
│              backlog.md                  │
│         (按优先级排序的待办池)            │
└──────────────────┬──────────────────────┘
                   │ 分配执行
                   ▼
┌─────────────────────────────────────────┐
│            in_progress.md                │
│            (正在执行的任务)               │
└──────────────────┬──────────────────────┘
                   │
       ┌───────────┼───────────┐
       │           │           │
       ▼           ▼           ▼
   ┌───────┐  ┌───────┐  ┌────────┐
   │ 完成  │  │ 阻塞  │  │  失败  │
   └───┬───┘  └───┬───┘  └───┬────┘
       │          │          │
       ▼          ▼          ▼
  completed.md  blocked.md  backlog.md
```

---

## 优先级算法

```
Priority = (Urgency × 0.4) + (Impact × 0.3) + (Readiness × 0.3)

其中：
- Urgency (紧急度): P0=10, P1=7, P2=4
- Impact (影响范围): 核心模块=10, 公共模块=7, 辅助模块=4
- Readiness (就绪度): 依赖已就绪=10, 部分就绪=6, 阻塞=2
```

---

## 创建新任务

### 自动创建（Orchestrator规划）

```markdown
当Orchestrator分析项目后，发现需要开发新功能时，
自动在backlog.md末尾添加任务卡片。
```

### 手动创建（用户指令）

```
用户可以在外部直接编辑backlog.md添加任务。
格式必须符合任务卡片规范。
```

---

## 任务操作

### 分配任务
```markdown
1. 从backlog.md取出最高优先级任务
2. 更新任务状态: pending → in_progress
3. 更新负责人: 指定执行Agent
4. 移动到in_progress.md
```

### 完成任务
```markdown
1. 更新状态: in_progress → completed
2. 记录执行时间和结果
3. 移动到completed.md
4. 更新PROJECT_RULES.md中的进度
```

### 阻塞任务
```markdown
1. 更新状态: in_progress → blocked
2. 记录阻塞原因
3. 移动到blocked.md
4. 通知Orchestrator需要用户决策
```

### 跳过任务
```markdown
1. 如果任务无法完成需要跳过
2. 更新状态: in_progress → pending
3. 更新最后时间和跳过原因
4. 移回backlog.md末尾
```

---

## 查看命令

```bash
# 查看待办任务
cat auto-dev/tasks/backlog.md

# 查看进行中任务
cat auto-dev/tasks/in_progress.md

# 查看已完成任务
cat auto-dev/tasks/completed.md

# 查看阻塞任务
cat auto-dev/tasks/blocked.md
```

---

## 注意事项

1. **ID唯一性**: TASK-ID格式为 `TASK-YYYYMMDD-NNN`，确保不重复
2. **状态同步**: 更新任务状态时，同步移动到对应文件
3. **记录完整**: 每次状态变更都要记录时间和原因
4. **验收标准**: 创建任务时必须明确验收标准
