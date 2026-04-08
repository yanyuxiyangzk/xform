# 外部参考文档

> 存储技术文档链接、项目参考资料

---

## 技术文档

### 核心框架

| 技术 | 文档链接 |
|------|---------|
| Spring Boot | https://spring.io/projects/spring-boot |
| Spring Cloud | https://spring.io/projects/spring-cloud |
| PF4J | https://pf4j.org/ |
| Liquor | https://github.com/noear/liquor |
| MyBatis-Plus | https://baomidou.com/ |
| Sa-Token | https://sa-token.cc/ |

### 前端框架

| 技术 | 文档链接 |
|------|---------|
| Vue3 | https://vuejs.org/ |
| TypeScript | https://www.typescriptlang.org/ |
| Element Plus | https://element-plus.org/ |
| Vite | https://vitejs.dev/ |

### 基础设施

| 技术 | 文档链接 |
|------|---------|
| Docker | https://docs.docker.com/ |
| Nacos | https://nacos.io/ |
| PostgreSQL | https://www.postgresql.org/ |
| Redis | https://redis.io/ |

---

## 项目文档

- [RuoYi-Cloud-Nocode 项目记忆](../.iflow/PROJECT_MEMORY.md)
- [项目开发规则](../.iflow/PROJECT_RULES.md)

---

## 经验参考

### PF4J插件开发

```markdown
关键点：
1. 插件必须实现 Plugin 接口
2. 使用 @Extension 注解定义扩展点
3. 插件打包为 .zip 文件
4. 使用 PluginManager 管理生命周期
```

### Liquor动态编译

```markdown
关键点：
1. Liquor 使用 javax.tools.JavaCompiler
2. 编译后的类通过自定义ClassLoader加载
3. 需要处理编译错误和类冲突
4. 建议配合SecurityManager实现沙箱
```

---

## 更新日志

| 日期 | 更新内容 |
|------|---------|
| 2026-04-02 | 初始化参考文档 |
