# 关系索引

> 记录实体之间的关系
> 最后更新：2026-04-03

---

## 关系类型

| 关系 | 说明 | 示例 |
|------|------|------|
| `related` | 相关 | A related B |
| `derived` | 派生 | B derived A |
| `supersedes` | 取代 | A supersedes B (旧版) |
| `blocks` | 阻塞 | A blocks B |
| `part-of` | 属于 | A part-of B (子任务) |
| `requires` | 需要 | A requires B |
| `implements` | 实现 | A implements B (设计→代码) |
| `tests` | 测试 | A tests B (测试→功能) |
| `deploys` | 部署 | A deploys B (运维→功能) |

---

## Agent 关系

```yaml
project-manager
  ├── orchestartor: manages
  ├── product-manager: manages
  ├── architect: manages
  ├── backend-dev: assigns
  ├── frontend-dev: assigns
  ├── tester: assigns
  └── operation: assigns

architect
  └── backend-dev: provides-design
  └── frontend-dev: provides-design

backend-dev
  └── frontend-dev: collaborates
```

---

## Task 关系

```yaml
PIPELINE-20260402-001 (Liquor编译)
  └── PIPELINE-20260402-002: requires
  └── PIPELINE-20260402-006: implements

PIPELINE-20260402-006 (Liquor IDE)
  ├── PIPELINE-20260402-001: requires
  └── PIPELINE-20260402-005: requires
```

---

## Memory 关系

```yaml
# 记忆关联
MEM-20260403-001 (架构决策)
  ├── derived: MEM-20260403-002 (详细设计)
  └── related: MEM-20260403-003 (相关需求)

# 项目关联
project:auto-dev
  ├── related: PIPELINE-20260402-001
  └── related: PIPELINE-20260402-002
```

---

## 关系查询

```markdown
# 查询某个实体的关系
/skill memory-ops
> 显示与PIPELINE-20260402-001相关的所有实体

# 添加关系
/skill memory-ops
> 记录A和B是related关系
```

---

最后更新：2026-04-03