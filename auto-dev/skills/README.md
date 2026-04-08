# Auto-Dev Skills 索引

> Claude Code Skills - 按需加载
> 流水线自动化开发系统 + 3层记忆系统

---

## Skill 列表

### 核心Skills（常驻）

| Skill | 角色 | 用途 | 触发方式 |
|-------|------|------|----------|
| **project-manager-skill** | 项目经理 | 用户唯一入口，协调流水线 | 默认加载 |
| **orchestrator-skill** | 协调者 | 监控全流程，处理并行，处理异常 | 常驻 |
| **memory-ops** | 记忆操作 | 记忆存储、搜索、整理 | /skill memory-ops |
| **knowledge-sync** | 知识同步 | 双向同步记忆系统 | /skill knowledge-sync |
| **daily-routine** | 日常自动化 | 早间简报、晚间复盘、周回顾 | /skill daily-routine |

### 工作Skills（按需加载）

| Skill | 角色 | 用途 | 触发方式 |
|-------|------|------|----------|
| product-manager-skill | 产品经理 | 需求分析 | /skill product-manager |
| architect-skill | 架构师 | 技术方案设计 | /skill architect |
| backend-dev-skill | 后端开发 | Java/Spring开发 | /skill backend-dev |
| frontend-dev-skill | 前端开发 | Vue3/TypeScript开发 | /skill frontend-dev |
| tester-skill | 测试工程师 | 测试用例，缺陷报告 | /skill tester |
| devops-skill | DevOps | 构建部署，CI/CD | /skill devops |
| operation-skill | 运维 | 环境部署，监控上线 | /skill operation |

### 辅助Skills（按需加载）

| Skill | 用途 | 触发方式 |
|-------|------|----------|
| knowledge-refiner | 记忆精炼，去重、归档 | /skill knowledge-refiner |
| task-analyzer | 任务分析、分解、执行 | /skill task-analyzer |
| self-improving | 自我反思、自我学习、越用越聪明 | /skill self-improving |

---

## 3层记忆系统

```
┌─────────────────────────────────────────────────────────────────┐
│                        长期记忆 (永久)                            │
│  knowledge/  projects/  reference/                              │
│                        │                                          │
│                        │ 层级提升                                 │
│                        ▼                                         │
├─────────────────────────────────────────────────────────────────┤
│                        工作记忆 (30天)                           │
│  sessions/  tasks/  decisions/                                   │
│                        │                                          │
│                        │ 层级提升                                 │
│                        ▼                                         │
├─────────────────────────────────────────────────────────────────┤
│                        情节记忆 (30天)                           │
│  daily-logs/  inbox/  captures/                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                   自我改进记忆 (越用越聪明)                       │
│  memory.md (HOT) → projects/ + domains/ (WARM) → archive/ (COLD)│
│  从每次工作/修正中学习，永久改进                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 记忆系统目录结构

```
auto-dev/memory/
├── MEMORY_INDEX.md              # 记忆系统说明
├── episodic/                   # 情节记忆 (30天)
│   ├── daily-logs/            # 每日日志
│   ├── inbox/                 # 临时存储
│   └── captures/             # 片段记忆
├── working/                   # 工作记忆 (30天)
│   ├── sessions/             # 会话记录
│   ├── tasks/               # 任务
│   └── decisions/           # 决策记录
├── longterm/                  # 长期记忆 (永久)
│   ├── knowledge/            # 知识库
│   ├── projects/            # 项目记录
│   └── reference/           # 参考资料
├── entities/                  # 实体索引 ⭐
│   ├── AGENTS.md           # Agent实体
│   ├── SKILLS.md           # Skill实体
│   ├── TASKS.md            # 任务实体
│   └── RELATIONS.md         # 关系索引
└── graph/                    # 知识图谱 ⭐
    └── INDEX.md
```

---

## Skill 使用示例

```bash
# 项目管理（默认入口）
/skill project-manager
> 需要XXX功能

# 记忆操作
/skill memory-ops
> 记住这个：XXX
> 搜索关于"XXX"的记忆
> 显示记忆结构

# 知识同步
/skill knowledge-sync
> 同步记忆状态

# 日常自动化
/skill daily-routine
> 早间简报
> 晚间复盘
> 周回顾

# 任务分析
/skill task-analyzer
> 分析任务：XXX

# 知识精炼
/skill knowledge-refiner
> 整理记忆
> 检查重复
```

---

## 完整Skill文件

```
auto-dev/skills/
├── README.md                    # 本文件
├── project-manager-skill.md   # 项目经理
├── orchestrator-skill.md        # 协调者
├── memory-ops.md              # 记忆操作 ⭐
├── knowledge-sync.md           # 知识同步 ⭐
├── daily-routine.md           # 日常自动化 ⭐
├── knowledge-refiner.md        # 知识精炼 ⭐
├── task-analyzer.md           # 任务分析 ⭐
├── self-improving.md           # 自我改进 ⭐
├── product-manager-skill.md    # 产品经理
├── architect-skill.md         # 架构师
├── backend-dev-skill.md       # 后端开发
├── frontend-dev-skill.md      # 前端开发
├── tester-skill.md           # 测试工程师
├── devops-skill.md           # DevOps
├── operation-skill.md        # 运维
└── exception-handler-skill.md # 异常处理
```

---

最后更新：2026-04-03