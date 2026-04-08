# Memory Operations Skill - 记忆操作

> 记忆读写技能 - 调用Python脚本实际读写记忆文件
> 按需加载，负责记忆的存储、搜索、列表、统计

---

## 核心能力

当用户说以下内容时，自动触发记忆操作：

| 用户表达 | 触发操作 | 命令 |
|---------|---------|------|
| "记住..." | store | `python memory_ops.py store <分类> <标题> <内容>` |
| "搜索记忆..." | search | `python memory_ops.py search <关键词>` |
| "查看记忆" | list | `python memory_ops.py list [--limit N]` |
| "记忆统计" | stats | `python memory_ops.py stats` |
| "记录日志" | daily-log | `python memory_ops.py daily-log <类型> <内容>` |

---

## 分类路径

```
episodic/          - 情节记忆（30天）
  daily-logs/      - 每日日志
  inbox/           - 临时收集
  captures/        - 片段捕获

working/           - 工作记忆（30天）
  sessions/        - 会话记录
  tasks/           - 任务
  decisions/       - 决策

longterm/          - 长期记忆（永久）
  knowledge/       - 知识库
    tech/          - 技术知识
    domain/        - 领域知识
  projects/        - 项目记录
  reference/       - 参考资料
```

---

## store 命令

**命令格式：**
```bash
python memory_ops.py store <category> <title> <content> [--tags TAG] [--importance N]
```

**示例：**
```bash
# 存储项目记忆
python memory_ops.py store "longterm/projects" "Liquor编译功能" "实现了Java源码动态编译" --tags "liquor,compiler" --importance 8

# 存储技术知识
python memory_ops.py store "longterm/knowledge/tech" "Spring Boot 3.x新特性" "记录Spring Boot 3.x的重要新特性" --tags "springboot,java" --importance 7
```

---

## search 命令

**命令格式：**
```bash
python memory_ops.py search <query> [--limit N]
```

**示例：**
```bash
python memory_ops.py search "liquor" --limit 5
```

---

## list 命令

**命令格式：**
```bash
python memory_ops.py list [--category CATEGORY] [--limit N]
```

**示例：**
```bash
python memory_ops.py list --category longterm/projects --limit 10
```

---

## stats 命令

**命令格式：**
```bash
python memory_ops.py stats
```

---

## daily-log 命令

**命令格式：**
```bash
python memory_ops.py daily-log <type> <entry>
```

**类型：**
- `done` - 今日完成
- `todo` - 明日计划
- `decision` - 决策记录
- `idea` - 想法
- `meeting` - 会议
- `note` - 备注

**示例：**
```bash
python memory_ops.py daily-log done "完成Liquor热替换功能"
python memory_ops.py daily-log decision "采用Liquor作为动态编译方案"
```

---

## 重要性指南

| 分数 | 标准 | 示例 |
|------|------|------|
| 9-10 | 业务关键 | 核心技术选型、重大决策 |
| 7-8 | 核心决策 | 架构决策、关键功能 |
| 5-6 | 有用参考 | 技术笔记、一般记录 |
| 1-4 | 临时 | 快速笔记 |

---

## 使用示例

```
用户: 记住 Liquor 编译功能实现了

→ 解析意图: store
→ 构建命令:
  python memory_ops.py store "longterm/projects" "Liquor编译功能" "实现了Java源码动态编译" --tags "liquor,compiler" --importance 8

---

用户: 搜索 liquor 相关的记忆

→ 解析意图: search
→ 构建命令:
  python memory_ops.py search "liquor" --limit 5

---

用户: 记录今天完成了用户模块

→ 解析意图: daily-log
→ 构建命令:
  python memory_ops.py daily-log done "完成用户模块"
```

---

## 脚本路径

```
auto-dev/scripts/memory_ops.py
```

---

## 自动学习触发

记忆操作后，检查是否需要自我改进：

```bash
# 存储重要记忆后
python scripts/auto_reflect_hook.py reflect memory "重要记忆已存储"

# 查看统计
python scripts/self_improve_ops.py stats
```

---

最后更新：2026-04-03
