# Auto-Dev Team 配置

> Claude Code Team 配置文件
> 用于配置多Agent协作团队

---

## 团队名称
auto-dev

## 团队描述
RuoYi-Cloud-Nocode 24小时自动开发团队

## Agent 成员

### orchestrator
- 类型: general-purpose
- 描述: 项目主控，负责自主决策和任务调度
- 定义文件: agents/orchestrator.md

### backend-dev
- 类型: general-purpose
- 描述: Java后端开发专家
- 定义文件: agents/backend-dev.md

### frontend-dev
- 类型: general-purpose
- 描述: Vue3前端开发专家
- 定义文件: agents/frontend-dev.md

### devops
- 类型: general-purpose
- 描述: 运维工程专家
- 定义文件: agents/devops.md

---

## 通信方式

- 任务分配: TaskUpdate
- 状态同步: SendMessage
- 决策请求: AskUserQuestion

---

## 启动命令

```bash
cd d:/project/aicoding/item/ainocode
claude-code --team auto-dev
```
