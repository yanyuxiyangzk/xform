# DevOps Skill

> DevOps - 构建部署
> 按需加载

---

## Skill 信息

| 属性 | 值 |
|------|-----|
| name | devops |
| description | DevOps，负责构建、部署、CI/CD配置 |
| trigger | 开发完成后调用 |

---

## 构建流程

```
接收代码 → 编译构建 → Docker镜像 → 推送到仓库
```

---

## 构建规范

### Docker镜像构建
```bash
# 构建镜像
docker build -t ruoyi-nocode-gateway:latest ./docker/Dockerfile.gateway

# 推送镜像
docker push ruoyi-nocode-gateway:latest
```

### GitHub Actions CI/CD
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
      - name: Build with Maven
        run: mvn clean package -DskipTests
      - name: Docker Build
        run: docker build -t ruoyi-nocode:latest .
```

---

## 构建完成标准

- [ ] 编译成功
- [ ] 单元测试通过
- [ ] Docker镜像构建成功
- [ ] 镜像推送到仓库成功

---

## 输出

构建完成后，通知测试工程师(Tester)进行测试。

测试通过后，通知运维工程师(Operation)进行上线部署。

---

## 使用方法

```
/skill devops
```

---

最后更新：2026-04-03