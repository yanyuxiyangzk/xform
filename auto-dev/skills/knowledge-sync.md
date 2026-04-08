# Knowledge Sync — 知识同步

> 双向同步记忆系统
> 触发词：同步记忆、知识同步、同步状态

---

## 脚本调用

```bash
# 执行同步（预览）
python scripts/knowledge_sync_ops.py sync --dry-run

# 执行同步（执行）
python scripts/knowledge_sync_ops.py sync

# 层级提升
python scripts/knowledge_sync_ops.py upgrade [--by-importance N] [--by-access N]

# 归档
python scripts/knowledge_sync_ops.py archive [--older-than DAYS] [--dry-run]

# 统计
python scripts/knowledge_sync_ops.py stats

# 健康检查
python scripts/knowledge_sync_ops.py health
```

---

## 同步方向

```
情节记忆 ──→ 工作记忆 ──→ 长期记忆
```

---

## 升级规则

| 方向 | 条件 |
|------|------|
| 情节 → 工作 | access_count > 5 AND age > 7天 |
| 工作 → 长期 | importance >= 7 OR access_count > 10 |

---

## 归档规则

- episodic层：age > 30天 且 importance < 5 → 归档候选

---

## 脚本路径

```
auto-dev/scripts/knowledge_sync_ops.py
```

---

## 自动学习触发

知识同步后自动反思：

```bash
# 执行同步
python scripts/knowledge_sync_ops.py sync

# 层级提升后
python scripts/auto_reflect_hook.py reflect knowledge-sync "层级同步完成"

# 健康检查
python scripts/self_improve_ops.py stats
```

---

最后更新：2026-04-03
