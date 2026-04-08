# 运行日志

> 本目录存储自动开发系统的运行日志
> 按日期组织，支持按时间追溯

---

## 目录结构

```
logs/
├── daily/                      # 每日日志
│   ├── 2026-04-02-orchestrator.log
│   ├── 2026-04-02-backend-dev.log
│   ├── 2026-04-02-frontend-dev.log
│   └── 2026-04-02-devops.log
│
└── README.md                  # 本文件
```

---

## 日志格式

```markdown
# [时间戳] [日志级别] [来源] 消息

# 示例
[2026-04-02 10:00:00] [INFO] [orchestrator] 开始检查任务队列
[2026-04-02 10:00:01] [INFO] [orchestrator] 发现待办任务: TASK-20260402-001
[2026-04-02 10:00:02] [INFO] [orchestrator] 分配任务给 backend-dev
[2026-04-02 10:05:00] [INFO] [backend-dev] 开始执行 TASK-20260402-001
...
```

---

## 日志级别

| 级别 | 说明 | 使用场景 |
|------|------|---------|
| DEBUG | 调试信息 | 开发调试 |
| INFO | 一般信息 | 正常流程记录 |
| WARN | 警告 | 需要注意但不阻塞 |
| ERROR | 错误 | 出现错误需要处理 |
| CRITICAL | 严重 | 必须立即处理 |

---

## 查看日志

```bash
# 查看今日Orchestrator日志
cat logs/daily/$(date +%Y-%m-%d)-orchestrator.log

# 实时跟踪日志
tail -f logs/daily/2026-04-02-orchestrator.log

# 搜索错误
grep "ERROR" logs/daily/2026-04-02-orchestrator.log

# 查看指定时间范围
grep "10:00" logs/daily/2026-04-02-orchestrator.log
```

---

## 日志保留

- 每日日志保留最近 30 天
- 30天前的日志自动归档或删除
- ERROR及以上日志永久保留

---

## 健康检查指标

通过日志可以观察：

| 指标 | 正常表现 | 异常表现 |
|------|---------|---------|
| 循环频率 | 每10分钟一次 | 长时间无记录 |
| 错误率 | 偶尔ERROR | 连续ERROR |
| 任务流转 | 有完成记录 | 任务一直in_progress |
