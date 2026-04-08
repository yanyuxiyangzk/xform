# Knowledge Refiner — 知识精炼

> 记忆优化、去重、归档
> 触发词：整理记忆、知识整理、去重、优化记忆、合并

---

## 脚本调用

```bash
# 执行精炼（预览）
python scripts/knowledge_refine_ops.py refine

# 执行精炼（实际执行）
python scripts/knowledge_refine_ops.py refine --execute

# 查找重复
python scripts/knowledge_refine_ops.py dedup [--threshold N]

# 合并记忆
python scripts/knowledge_refine_ops.py merge <primary_id> <duplicate_id>

# 归档过时记忆
python scripts/knowledge_refine_ops.py archive [--dry-run]

# 重建索引
python scripts/knowledge_refine_ops.py reindex
```

---

## 安全规则

1. **永不自动删除** — 始终显示候选并获得用户批准
2. **先预览后执行** — 归档始终预览
3. **合并前备份** — 被合并的记忆移到archive

---

## 使用示例

```
用户: 检查记忆重复
→ dedup --threshold 0.5

用户: 合并这两条记忆
→ merge MEM-20260403-001 MEM-20260403-002

用户: 整理我的记忆
→ refine --execute
```

---

## 脚本路径

```
auto-dev/scripts/knowledge_refine_ops.py
```

---

## 自动学习触发

知识精炼后自动反思：

```bash
# 执行精炼
python scripts/knowledge_refine_ops.py refine --execute

# 归档后
python scripts/auto_reflect_hook.py reflect knowledge-refine "知识归档完成"

# 查重后
python scripts/auto_reflect_hook.py reflect dedup "重复检查完成"
```

---

最后更新：2026-04-03
