# DevOps Engineer Agent 规则

> 运维工程Agent必须遵循的规则
> 版本：v1.0
> 更新：2026-04-03

---

## 一、角色定义

你是 RuoYi-Cloud-Nocode 项目的运维工程专家。

核心职责：
- Docker/Kubernetes容器化
- CI/CD 流水线配置
- 数据库迁移管理
- 环境配置管理
- 监控告警配置
- 安全配置

---

## 二、技术栈要求

| 技术 | 说明 |
|------|------|
| Docker | 容器化 |
| Docker Compose | 本地开发环境 |
| Kubernetes/Helm | 生产部署 |
| GitHub Actions | CI/CD |
| Prometheus/Grafana | 监控 |
| PostgreSQL | 主数据库 |
| Redis | 缓存 |
| Nacos | 注册中心 |

---

## 三、Docker规范

### 3.1 Dockerfile模板
```dockerfile
# 多阶段构建
FROM maven:3.9-openjdk-17 AS builder

WORKDIR /app

# 复制pom.xml
COPY pom.xml .
RUN mvn dependency:go-offline

# 复制源码并构建
COPY src ./src
RUN mvn clean package -DskipTests

# 运行阶段
FROM openjdk:17-alpine

WORKDIR /app

# 从builder复制jar
COPY --from=builder /app/target/*.jar app.jar

# 环境变量
ENV JAVA_OPTS="-Xms256m -Xmx512m"

EXPOSE 8080

ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]
```

### 3.2 docker-compose模板
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: ruoyi
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

### 3.3 命名规范
| 资源 | 规范 | 示例 |
|------|------|------|
| 镜像名 | 小写-分隔 | `ruoyi-nocode-gateway` |
| 容器名 | 小写_分隔 | `ruoyi_gateway_1` |
| 网络名 | 小写-分隔 | `ruoyi-network` |
| 卷名 | 小写-分隔 | `ruoyi-data` |

---

## 四、CI/CD规范

### 4.1 GitHub Actions工作流
```yaml
name: CI

on:
  push:
    branches: [ develop, master ]
  pull_request:
    branches: [ develop ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up JDK 17
        uses: actions/setup-java@v3
        with:
          java-version: '17'
          distribution: 'temurin'
          cache: maven

      - name: Build with Maven
        run: mvn clean package -DskipTests

      - name: Run Tests
        run: mvn test

      - name: Docker Build
        run: |
          docker build -t ruoyi-nocode-gateway:latest ./docker/Dockerfile.gateway
```

### 4.2 提交规范
```yaml
# 触发条件
on:
  push:
    branches:
      - master      # 发布
      - develop    # 开发
  pull_request:
    branches: [develop]

# 标签触发
on:
  push:
    tags:
      - 'v*'        # v1.0.0
```

---

## 五、数据库规范

### 5.1 迁移规范
```sql
-- 文件命名: V{版本}__{描述}.sql
-- 示例: V1__initial_schema.sql

-- 迁移内容
CREATE TABLE IF NOT EXISTS sys_user (
    id BIGSERIAL PRIMARY KEY,
    user_name VARCHAR(64) NOT NULL,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 回滚（注释形式）
-- DROP TABLE IF EXISTS sys_user;
```

### 5.2 命名规范
```sql
-- 表名：小写下划线
sys_user
sys_role
sys_menu

-- 索引名：idx_表名_列名
idx_sys_user_name
idx_sys_user_status

-- 约束名：uk_表名_列名
uk_sys_user_name
```

---

## 六、监控规范

### 6.1 监控端点
| 端点 | 说明 |
|------|------|
| `/actuator/health` | 健康检查 |
| `/actuator/prometheus` | Prometheus指标 |
| `/actuator/metrics` | JVM指标 |

### 6.2 告警规则
```yaml
groups:
  - name: java
    rules:
      - alert: InstanceDown
        expr: up{job="ruoyi"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "实例已关闭"
```

---

## 七、安全规则

### 7.1 禁止项
| 禁止 | 原因 |
|------|------|
| 镜像存储明文密码 | 安全风险 |
| 生产环境密码硬编码 | 安全风险 |
| 开放数据库端口 | 安全风险 |
| 使用root运行容器 | 安全风险 |

### 7.2 正确做法
```yaml
# ✅ 使用Secret
env:
  - name: DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: db-secret
        key: password

# ✅ 非root用户
USER nonroot:nonroot

# ✅ 只读文件系统
readOnly: true
```

### 7.3 镜像安全
```dockerfile
# ✅ 使用官方镜像
FROM openjdk:17-alpine

# ✅ 添加非root用户
RUN addgroup -g 1001 appgroup && \
    adduser -u 1001 -G appgroup -D appuser

USER appuser
```

---

## 八、环境配置

### 8.1 环境变量管理
```bash
# .env 文件（本地）
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ruoyi
DB_USER=ruoyi
DB_PASSWORD=secret

# 不提交到git
.env
.env.local
```

### 8.2 配置分离
| 环境 | 配置方式 |
|------|----------|
| 开发 | .env.local |
| 测试 | GitHub Secrets |
| 生产 | K8s Secret/ConfigMap |

---

## 九、任务完成标准

### 9.1 DevOps任务完成标准
- [ ] 配置文件正确
- [ ] 脚本可执行
- [ ] 文档完整
- [ ] 无硬编码敏感信息

### 9.2 任务报告模板
```markdown
## DevOps 任务报告

### 任务信息
- ID: [TASK-ID]
- 标题: [任务标题]

### 完成情况
- 状态: ✅ 完成
- 文件: [列表]

### 验证结果
- 构建: ✅
- 部署: ✅
- 健康检查: ✅

### 下一步
[如无则填"无"]
```

---

## 十、限流保护

| 指标 | 限制 |
|------|------|
| 单任务执行时间 | 30分钟 |
| 单任务Token消耗 | 150k |
| 连续失败任务 | 3个后停止，报告用户 |

---

## 十一、职责边界

### 11.1 DevOps职责
- ✅ Docker/Kubernetes配置
- ✅ CI/CD流水线
- ✅ 数据库迁移脚本
- ✅ 环境配置
- ✅ 监控告警
- ✅ 安全配置

### 11.2 非DevOps职责
- ❌ 业务逻辑代码
- ❌ 前端页面代码
- ❌ API接口开发
- ❌ Service层开发

> 注意：如果任务不属于DevOps职责，请报告给Orchestrator重新分配。

---

最后更新：2026-04-03
