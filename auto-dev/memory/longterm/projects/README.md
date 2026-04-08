# 项目记录

> 长期记忆 - 项目记录
> 最后更新：2026-04-03

---

## 项目索引

### RuoYi-Cloud-Nocode

```yaml
name: RuoYi-Cloud-Nocode
description: 零代码微服务平台
type: main-project
tech_stack:
  - Java 17
  - Spring Boot 3.2.5
  - Spring Cloud 2023.0.5
  - PF4J 3.11.1
  - Liquor 1.6.3
  - MyBatis-Plus 3.5.7
  - Sa-Token 1.37.0
  - Vue3
  - TypeScript
status: active
started: 2026-02
milestones:
  - 2026-02: 基础框架搭建
  - 2026-04-02: Liquor动态编译功能
```

---

## 项目结构

```
RuoYi-Cloud-Nocode/
├── ruoyi-nocode-gateway/      # 网关服务 (8080)
├── ruoyi-nocode-auth/         # 认证服务 (9200)
├── ruoyi-nocode-system/        # 系统服务 (9201)
├── ruoyi-nocode-common/        # 公共模块
│   └── ruoyi-nocode-common-core/  # 核心模块
├── plus-ui-ts/                # 前端Vue3项目
└── auto-dev/                  # 自动开发系统
```

---

## 项目记忆

| 日期 | 项目 | 记录 |
|------|------|------|
| 2026-04-02 | RuoYi-Cloud-Nocode | 完成Liquor即时编译功能 |
| 2026-04-02 | RuoYi-Cloud-Nocode | 完成Liquor热替换功能 |
| 2026-04-02 | RuoYi-Cloud-Nocode | 完成代码生成引擎 |
| 2026-04-02 | RuoYi-Cloud-Nocode | 完成字典管理功能 |

---

最后更新：2026-04-03