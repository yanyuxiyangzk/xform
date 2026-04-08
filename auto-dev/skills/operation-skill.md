# Operation Skill

> 运维工程师 - 部署运维
> 按需加载

---

## Skill 信息

| 属性 | 值 |
|------|-----|
| name | operation |
| description | 运维，负责环境部署、监控配置、上线发布、运维监控 |
| trigger | 测试通过后调用 |

---

## 上线流程

```
接收测试报告 → 环境准备 → 部署发布 → 监控配置 → 上线确认
```

---

## 上线检查清单

```markdown
# 上线检查清单

## 1. 环境准备
- [ ] 生产环境服务器就绪
- [ ] 数据库迁移脚本准备
- [ ] 配置文件准备
- [ ] 备份完成

## 2. 部署
- [ ] 拉取最新镜像
- [ ] 执行数据库迁移
- [ ] 停止旧服务
- [ ] 启动新服务
- [ ] 健康检查通过

## 3. 监控配置
- [ ] Prometheus指标采集
- [ ] Grafana看板配置
- [ ] 日志收集配置
- [ ] 告警规则配置

## 4. 验证
- [ ] 功能验证
- [ ] 性能验证
- [ ] 监控数据正常
```

---

## 部署命令

### Docker Compose
```bash
docker-compose up -d
docker-compose logs -f
```

### Kubernetes
```bash
kubectl apply -f deployment.yaml
kubectl get pods -n ruoyi
kubectl logs -f deployment/xxx -n ruoyi
```

### Helm
```bash
helm install ruoyi ./helm/ruoyi -n ruoyi
helm upgrade ruoyi ./helm/ruoyi -n ruoyi
```

---

## 上线报告模板

```markdown
# 上线报告 YYYY-MM-DD

## 上线信息
- 项目名称：
- 上线版本：
- 上线时间：
- 上线人员：operation

## 上线内容
- [ ] 功能1
- [ ] 功能2

## 健康检查
- [ ] API接口正常
- [ ] 数据库连接正常
- [ ] 缓存服务正常

## 监控状态
- [ ] 指标采集正常
- [ ] 日志收集正常
- [ ] 告警正常

## 结论
✅ 上线成功 / ❌ 上线失败

## 回滚方案
[如有问题，如何回滚]
```

---

## 使用方法

```
/skill operation
```

---

最后更新：2026-04-03