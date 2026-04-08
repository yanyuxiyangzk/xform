# Backend Developer Skill

> 后端开发 - Java/Spring开发
> 按需加载

---

## Skill 信息

| 属性 | 值 |
|------|-----|
| name | backend-dev |
| description | 后端开发，负责Java/Spring业务逻辑、接口开发 |
| trigger | 架构师完成技术方案后调用 |

---

## 接收任务

接收来自架构师的技术方案，开始后端开发。

## 开发规范

### 代码规范
```java
// 1. 类注释
/**
 * 用户服务类
 *
 * @author auto-dev
 */

// 2. 方法注释
/**
 * 根据ID获取用户
 *
 * @param id 用户ID
 * @return 用户信息
 */

// 3. 必须使用的注解
@Entity           // 实体类
@TableName        // MyBatis-Plus
@RestController   // REST控制器
@Service         // 服务类
@RequiredArgsConstructor
@PreAuthorize    // 权限控制
```

### 返回格式
```java
// 成功
return R.ok(data);
return R.ok();

// 失败
return R.fail("错误信息");
```

### 分页返回
```java
public TableDataInfo list() {
    startPage();
    List<SysUser> list = userService.selectUserList(user);
    return getDataTable(list);
}
```

---

## 开发完成标准（强制门禁）

**以下所有条件必须全部满足，否则不得提交代码：**

| 门禁 | 命令 | 通过标准 |
|------|------|----------|
| ✅ 编译通过 | `mvn compile -q` | 退出码=0，无error |
| ✅ 单元测试通过 | `mvn test -q` | 退出码=0，失败率≤10% |
| ✅ 代码规范检查 | `mvn checkstyle:check -q` | 退出码=0 |
| ✅ 无P0/P1漏洞 | `mvn spotbugs:check -q`（如有配置） | 无P0/P1问题 |

**禁止使用 `-DskipTests` 或 `-Dmaven.test.skip=true` 绕过测试！**

### 自检脚本

```bash
# 在项目根目录执行自检（必须全部通过）
cd d:/project/aicoding/item/ainocode/ruoyi-nocode
JAVA_HOME="D:/Program Files/Java/jdk-17.0.6" mvn compile -q && \
JAVA_HOME="D:/Program Files/Java/jdk-17.0.6" mvn test -q && \
echo "✅ 质量门禁全部通过"
```

### 常见问题处理

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| Lombok没生成getter/setter | JDK17+Lombok不兼容 | 使用 `@Getter @Setter` 显式注解，或升级Lombok版本 |
| Liquor编译失败 | 类加载器隔离问题 | 检查 IsolatedClassLoaderUtil 配置 |
| 测试用例失败 | 逻辑错误或环境问题 | 修复代码，不允许跳过 |

---

## 输出

所有门禁通过后，通知测试工程师(Tester)进行测试，并附上：
- `mvn compile` 输出
- `mvn test` 测试报告摘要
- 代码变更列表

---

## 使用方法

```
/skill backend-dev
```

---

最后更新：2026-04-03