# Auto-Dev Team 开发规则

> 本项目所有Agent必须遵循的开发规则
> 版本：v2.0（整合trae-rules，适配Claude Code）
> 更新：2026-04-03

---

> 📌 **规则来源说明**
> 本规则整合自 [trae-rules](https://github.com/yanyuxiyangzk/trae-rules)，已适配 Claude Code Team/Agent/Cron 工具链使用。

---

## 一、核心开发原则（需求规范）

### 1.1 代码质量优先
- 所有代码必须通过编译 `mvn compile`
- 所有新功能必须包含单元测试
- 单元测试覆盖率不低于 70%
- 遵循 SOLID 原则和项目代码风格

### 1.2 【TRAE-RULES】代码生成规范
| 规则 | 要求 |
|------|------|
| 生成完整可运行代码 | 不允许占位符、TODO、缺失逻辑 |
| 复用现有API | 创建新接口前必须先复用现有接口 |
| 最小化新增依赖 | 优先使用项目现有依赖 |
| 验证API存在 | 不发明不存在的API或方法 |
| 第一次就完全修复 | 解决根本原因，不迭代尝试 |
| 确保代码成功编译 | 所有代码必须能编译/运行 |

### 1.3 提交规范
- 提交前必须运行测试
- 提交信息格式：`[类型] 简短描述`
  - `[feat]` 新功能
  - `[fix]` Bug修复
  - `[refactor]` 重构
  - `[docs]` 文档
  - `[test]` 测试
  - `[chore]` 构建/工具
- 不提交敏感信息（密码、密钥等）
- 不提交 IDE 配置文件

### 1.4 分支管理
- 开发分支：`develop`
- 发布分支：`master`
- 功能分支：`feature/xxx`
- 修复分支：`fix/xxx`
- **禁止直接推送 master/main**

---

## 二、安全规则

### 2.1 【TRAE-RULES】输入验证与清理
- 验证所有用户输入、API 参数、文件上传
- 使用白名单验证，不要黑名单
- 清理 HTML/SQL/命令注入风险字符
- 验证数据类型、长度、格式、范围

### 2.2 【TRAE-RULES】敏感数据保护
- 密码使用 bcrypt/Argon2 单向哈希，加盐
- 敏感数据加密存储
- 使用 HTTPS/TLS 传输敏感数据
- 不在日志、URL中暴露敏感数据

### 2.3 【TRAE-RULES】API安全
- 实施速率限制（Rate Limiting）
- 使用 API 密钥或 JWT 令牌认证
- 验证 Content-Type
- 限制请求大小

### 2.4 【TRAE-RULES】会话管理安全
- 会话 ID 随机生成，不可预测
- 设置会话超时（空闲30分钟，绝对24小时）
- Cookie 设置 HttpOnly、Secure、SameSite 属性

### 2.5 绝对禁止
| 禁止项 | 原因 | 违规处理 |
|--------|------|----------|
| 删除 `.git` 目录 | 版本控制丢失 | 立即停止 |
| 删除核心架构文件 | PF4J/Liquor核心 | 立即停止 |
| 修改数据库密码 | 安全风险 | 立即停止 |
| 强制推送到 master | 版本控制风险 | 立即停止 |
| 执行外部未验证脚本 | 安全风险 | 立即停止 |
| 硬编码密钥/密码 | 安全风险 | 立即停止 |
| 使用root运行容器 | 安全风险 | 立即停止 |

### 2.6 敏感信息处理
```markdown
必须使用环境变量：
- 数据库密码 → ${DB_PASSWORD}
- JWT密钥 → ${JWT_SECRET}
- API密钥 → ${API_KEY}

禁止硬编码：
❌ password = "123456"
✅ password = System.getenv("DB_PASSWORD")
```

---

## 三、代码规范

### 3.1 【TRAE-RULES】命名规范
| 类型 | 规范 | 示例 |
|------|------|------|
| Java类 | PascalCase | `UserService` |
| Java方法 | camelCase | `getUserById` |
| Java变量 | camelCase | `userName` |
| Java常量 | UPPER_SNAKE | `MAX_RETRY_COUNT` |
| 数据库表 | 小写下划线 | `sys_user` |
| 数据库列 | 小写下划线 | `user_name` |
| Vue组件 | PascalCase | `UserDialog.vue` |
| CSS类 | kebab-case | `user-dialog` |
| API路径 | 小写连字符 | `/user/login` |
| 环境变量 | UPPER_SNAKE | `DB_PASSWORD` |
| 文件名 | kebab-case | `user-dialog.vue` |

### 3.2 Java代码规范
```java
// 1. 类注释
/**
 * 用户服务类
 *
 * @author auto-dev
 * @date 2026-04-03
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
@Autowired       // 依赖注入
@PreAuthorize    // 权限控制

// 4. 返回类型
单条: R<T>
分页: TableDataInfo
列表: R<List<T>>
```

### 3.3 【TRAE-RULES】错误处理规范
- 始终处理错误，绝不静默失败
- 对异步操作使用 try-catch
- 使用足够的上下文记录错误
- 向用户返回有意义的错误消息
- 不要在错误消息中暴露敏感信息

```java
// ✅ 正确
try {
  await saveUser(data);
} catch (error) {
  logger.error('Failed to save user', { userId: data.id, error });
  throw new DatabaseError('Unable to save user data');
}

// ❌ 错误 - 静默失败
try {
  await saveUser(data);
} catch (error) {
  // Silent failure
}
```

### 3.4 前端代码规范
```typescript
// 1. 类型定义
interface User {
  id: number;
  name: string;
  email?: string;
}

// 2. 组件命名
// 文件: UserDialog.vue
// 组件名: UserDialog

// 3. API封装
export function getUserList(params) {
  return request({
    url: '/system/user/list',
    method: 'get',
    params,
  });
}

// 4. 必须的错误处理
try {
  await getUser();
} catch (error) {
  ElMessage.error(error.message);
}
```

---

## 四、【TRAE-RULES】工作流程规范

### 4.1 变更日志管理
- 在 CHANGELOG.md 中记录所有重要变更
- 包含版本号、日期和变更描述
- 遵循 "Keep a Changelog" 格式

### 4.2 版本号管理
- 遵循语义化版本（MAJOR.MINOR.PATCH）
- MAJOR：破坏性变更
- MINOR：新功能（向后兼容）
- PATCH：错误修复

### 4.3 破坏性变更协议
- 清楚地记录所有破坏性变更
- 为用户提供迁移指南
- 提升 MAJOR 版本号

### 4.4 依赖更新策略
- 定期审查依赖更新
- 在生产环境固定确切版本（不使用 ^ 或 ~）
- 运行安全审计（npm audit、pip-audit）
- 立即更新安全关键依赖

---

## 五、【TRAE-RULES】安全规范（OWASP Top 10）

### 5.1 防护项目
1. Broken Access Control - 访问控制失效
2. Cryptographic Failures - 加密失败
3. Injection - 注入攻击
4. Insecure Design - 不安全设计
5. Security Misconfiguration - 安全配置错误
6. Vulnerable Components - 易受攻击的组件
7. Authentication Failures - 认证失败
8. Data Integrity Failures - 数据完整性失败
9. Logging Failures - 日志记录失败
10. SSRF - 服务端请求伪造

### 5.2 关键防护措施
- 使用 CSP (Content Security Policy) 头
- 启用 CORS 策略
- 设置安全的 Cookie 属性（HttpOnly、Secure、SameSite）
- 防止点击劫持（X-Frame-Options）

### 5.3 【TRAE-RULES】日志安全
- 日志中禁止记录：密码、令牌、密钥、信用卡号、身份证
- 记录安全事件：登录失败、权限拒绝、异常访问

```java
// ❌ 错误（泄露密码）
logger.info(`用户登录: ${email}, 密码: ${password}`);

// ✅ 正确（安全日志）
logger.info(`用户登录成功: ${email}`);
logger.warn(`登录失败: ${email}, IP: ${req.ip}`);
```

---

## 六、质量门卫

### 6.1 代码检查清单
```
提交前必须通过：
□ mvn compile - 编译检查
□ mvn test - 单元测试
□ mvn checkstyle:check - 代码格式
□ 无硬编码敏感信息
□ 提交信息格式正确
□ 符合TRAE-RULES命名规范
```

### 6.2 单元测试要求
```java
// 1. 必须测试的方法
- Service层的所有 public 方法
- Controller层的关键接口
- 工具类的静态方法

// 2. 测试覆盖率
- 核心业务逻辑 > 80%
- 普通代码 > 60%

// 3. 测试命名
@Test
public void testGetUserById_Success() {}
@Test
public void testGetUserById_NotFound() {}
```

### 6.3 代码审查触发条件
| 情况 | 必须审查 |
|------|----------|
| 修改核心架构 | ✅ |
| 修改数据库Schema | ✅ |
| 新增API接口 | ✅ |
| 修改认证逻辑 | ✅ |
| 常规Bug修复 | ⏭️ 可跳过 |

---

## 七、API设计规范

### 7.1 RESTful规范
| 操作 | 方法 | 路径 | 返回 |
|------|------|------|------|
| 查询列表 | GET | `/xxx/list` | TableDataInfo |
| 查询详情 | GET | `/xxx/{id}` | R<T> |
| 新增 | POST | `/xxx` | R<?> |
| 修改 | PUT | `/xxx` | R<?> |
| 删除 | DELETE | `/xxx/{ids}` | R<?> |

### 7.2 响应格式
```json
// 成功
{
  "code": 200,
  "msg": "操作成功",
  "data": {}
}

// 分页
{
  "code": 200,
  "msg": "操作成功",
  "rows": [],
  "total": 100,
  "pageNum": 1,
  "pageSize": 10
}

// 错误
{
  "code": 500,
  "msg": "服务器内部错误"
}
```

### 7.3 HTTP状态码
| 状态码 | 含义 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 500 | 服务器错误 |

---

## 八、Git提交规范

### 8.1 提交信息格式
```
[类型] 简短描述

详细说明（可选）

Closes #issue
```

### 8.2 提交类型
| 类型 | 说明 |
|------|------|
| feat | 新功能 |
| fix | Bug修复 |
| docs | 文档 |
| style | 格式（不影响代码） |
| refactor | 重构 |
| perf | 性能优化 |
| test | 测试 |
| chore | 构建/工具 |

### 8.3 提交示例
```
[feat] 添加用户管理模块

- 新增SysUser实体
- 实现CRUD接口
- 添加Vue页面

Closes #123
```

---

## 九、数据库规范

### 9.1 表设计
```sql
-- 必须包含字段
id          BIGINT PRIMARY KEY AUTO_INCREMENT,
create_by   VARCHAR(64) DEFAULT '' COMMENT '创建者',
create_time DATETIME COMMENT '创建时间',
update_by   VARCHAR(64) DEFAULT '' COMMENT '更新者',
update_time DATETIME COMMENT '更新时间',
remark      VARCHAR(500) DEFAULT NULL COMMENT '备注',
del_flag    CHAR(1) DEFAULT '0' COMMENT '删除标志',

-- 必须包含索引
INDEX idx_del_flag (del_flag),
INDEX idx_create_time (create_time)
```

### 9.2 命名规范
```sql
-- 表名：模块_实体
sys_user          -- 用户表
sys_role          -- 角色表
sys_menu          -- 菜单表

-- 约束命名
uk_table_column   -- 唯一约束
idx_table_column  -- 普通索引
fk_table_ref      -- 外键
```

---

## 十、文档规范

### 10.1 必须文档
| 文档 | 说明 |
|------|------|
| README.md | 项目说明 |
| API.md | 接口文档 |
| DEPLOY.md | 部署文档 |

### 10.2 代码注释
- 公共类必须注释
- 复杂逻辑必须注释
- API接口必须注释参数和返回值

---

## 十一、【TRAE-RULES】文件上传安全

- 验证文件类型（MIME type 和扩展名双重验证）
- 限制文件大小
- 存储在非 Web 目录或使用对象存储
- 随机重命名文件，不使用原始文件名

---

## 十二、【TRAE-RULES】依赖安全管理

| 命令 | 说明 |
|------|------|
| npm audit | Node.js 安全扫描 |
| pip-audit | Python 安全扫描 |
| mvn dependency:analyze | Maven 依赖分析 |

- 不使用已知漏洞的依赖版本
- 固定依赖版本，避免自动更新引入漏洞
- 最小化依赖数量

---

## 十三、违规处理

### 13.1 规则违反
| 级别 | 违反情况 | 处理 |
|------|----------|------|
| P0 | 安全违规、删除核心代码 | 立即停止，报告用户 |
| P1 | 违反代码规范、缺少测试 | 要求修复后才能合并 |
| P2 | 轻微违规 | 警告，限期修复 |

### 13.2 回退机制
```
发现违规代码 → 立即停止 → 回退代码 → 报告用户 → 等待指示
```

---

## 十四、限流保护

| 指标 | 限制 |
|------|------|
| 单任务执行时间 | 30分钟 |
| 单任务Token消耗 | 150k |
| 连续失败任务 | 3个后停止，报告用户 |

---

## 十五、持续更新

本规则文件将根据项目发展持续更新，更新时需用户确认。

**整合的规则来源**（适配 Claude Code）：
- auto-dev v1.0 原始规则
- trae-rules/requirements-spec（13条需求规范）
- trae-rules/security-spec（12条安全规范）
- trae-rules/workflow-spec（12条工作流规范，启用6条）
- trae-rules/naming-conventions（12条命名约定，启用6条）

**Claude Code 适配说明**：
- 使用 @RULES.md 引用本规则文件
- 使用 Agent/Team/Cron 工具实现多Agent并行
- 遵循 Claude Code CLI 使用习惯

最后更新：2026-04-03
