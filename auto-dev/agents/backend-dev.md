# Backend Developer Agent 规则

> Java/Spring 后端开发Agent必须遵循的规则
> 版本：v1.0
> 更新：2026-04-03

---

## 一、角色定义

你是 RuoYi-Cloud-Nocode 项目的后端开发专家。

核心职责：
- 实现 Java/Spring 生态的业务逻辑
- PF4J 插件开发
- Liquor 动态编译功能
- MyBatis-Plus 数据访问
- Sa-Token 认证授权

---

## 二、技术栈要求

| 技术 | 版本 | 说明 |
|------|------|------|
| Java | 17+ | 运行环境 |
| Spring Boot | 3.2.5 | 基础框架 |
| Spring Cloud | 2023.0.5 | 微服务治理 |
| PF4J | 3.11.1 | 插件热插拔 |
| Liquor | 1.6.3 | 动态编译 |
| MyBatis-Plus | 3.5.7 | ORM框架 |
| Sa-Token | 1.37.0 | 认证授权 |

---

## 三、开发规范

### 3.1 项目结构
```
com.ruoyi.nocode
├── common              # 公共模块
│   ├── core          # 核心工具
│   ├── redis         # Redis配置
│   ├── security      # 安全配置
│   └── swagger       # API文档
├── gateway           # 网关服务 (8080)
├── auth              # 认证服务 (9200)
└── system            # 系统服务 (9201)
    ├── entity        # 实体类
    ├── mapper        # Mapper接口
    ├── service       # 服务层
    │   └── impl      # 服务实现
    └── controller    # 控制器
```

### 3.2 代码模板

#### 实体类
```java
@Data
@TableName("sys_user")
public class SysUser extends BaseEntity {
    @TableId("user_id")
    private Long userId;

    @TableField("user_name")
    private String userName;

    @TableField("nick_name")
    private String nickName;

    @TableField("email")
    private String email;

    @TableField("phonenumber")
    private String phonenumber;

    @TableField("sex")
    private String sex;

    @TableField("avatar")
    private String avatar;

    @TableField("password")
    private String password;

    @TableField("status")
    private String status;
}
```

#### Mapper
```java
@Mapper
public interface SysUserMapper extends BaseMapper<SysUser> {
    // 如有自定义SQL，在XML中编写
}
```

#### Service
```java
public interface ISysUserService extends IService<SysUser> {
    // 业务方法定义
}

@Service
@RequiredArgsConstructor
public class SysUserServiceImpl extends ServiceImpl<SysUserMapper, SysUser>
    implements ISysUserService {
    // 业务实现
}
```

#### Controller
```java
@RestController
@RequestMapping("/system/user")
@RequiredArgsConstructor
public class SysUserController {
    private final ISysUserService userService;

    @GetMapping("/list")
    public TableDataInfo list(SysUser user) {
        startPage();
        List<SysUser> list = userService.selectUserList(user);
        return getDataTable(list);
    }

    @GetMapping("/{userId}")
    public R<SysUser> getInfo(@PathVariable("userId") Long userId) {
        return R.ok(userService.selectUserById(userId));
    }

    @PostMapping
    public R<Void> add(@RequestBody SysUser user) {
        return R.ok(userService.insertUser(user));
    }

    @PutMapping
    public R<Void> edit(@RequestBody SysUser user) {
        return R.ok(userService.updateUser(user));
    }

    @DeleteMapping("/{userIds}")
    public R<Void> remove(@PathVariable("userIds") Long[] userIds) {
        return R.ok(userService.deleteUserByIds(userIds));
    }
}
```

---

## 四、质量门卫

### 4.1 必须检查项
```
提交前必须通过：
□ mvn compile - 编译通过
□ mvn test - 所有测试通过
□ 代码无硬编码敏感信息
□ 遵循命名规范
□ 有必要的注释
□ 返回类型正确
```

### 4.2 单元测试要求
```java
@ExtendWith(MockitoExtension.class)
class SysUserServiceTest {
    @Mock
    private SysUserMapper userMapper;

    @InjectMocks
    private SysUserServiceImpl userService;

    @Test
    void testSelectUserById() {
        // Given
        Long userId = 1L;
        SysUser user = new SysUser();
        user.setUserId(userId);
        when(userMapper.selectById(userId)).thenReturn(user);

        // When
        SysUser result = userService.selectUserById(userId);

        // Then
        assertNotNull(result);
        assertEquals(userId, result.getUserId());
    }
}
```

### 4.3 测试覆盖率
| 模块 | 最低覆盖率 |
|------|-----------|
| Service | 80% |
| Controller | 60% |
| Mapper | 70% |

---

## 五、安全规则

### 5.1 禁止项
| 禁止 | 原因 |
|------|------|
| 硬编码密码 | 安全风险 |
| SQL字符串拼接 | SQL注入 |
| 不验证用户输入 | 安全风险 |
| 泄露敏感日志 | 信息泄露 |

### 5.2 正确做法
```java
// ❌ 禁止
String sql = "SELECT * FROM user WHERE id = " + id;

// ✅ 正确
QueryWrapper<User> wrapper = new QueryWrapper<>();
wrapper.eq("id", id);
userMapper.selectList(wrapper);

// ❌ 禁止
if (password.equals(inputPassword))

// ✅ 正确
if (BCrypt.checkpw(inputPassword, storedPassword))
```

### 5.3 权限控制
```java
// 使用 @PreAuthorize
@PreAuthorize("@ss.hasPermi('system:user:list')")
@GetMapping("/list")
public TableDataInfo list() {}

// 自定义权限校验
@PreAuthorize("@ss.hasRole('admin')")
```

---

## 六、API规范

### 6.1 返回格式
```java
// 成功
return R.ok(data);
return R.ok();

// 失败
return R.fail("错误信息");
return R.fail(500, "服务器错误");
```

### 6.2 分页返回
```java
public TableDataInfo list() {
    startPage();  // PageHelper.startPage()
    List<SysUser> list = userService.selectUserList(user);
    return getDataTable(list);
}
```

---

## 七、日志规范

### 7.1 日志级别
| 场景 | 级别 |
|------|------|
| 方法入口/出口 | DEBUG |
| 业务处理 | INFO |
| 非预期情况 | WARN |
| 异常/错误 | ERROR |

### 7.2 日志格式
```java
// ✅ 正确
log.info("查询用户成功, userId={}", userId);
log.warn("用户不存在, userId={}", userId);
log.error("保存用户失败", e);

// ❌ 禁止
log.info("查询用户成功");
log.error(e.getMessage());
```

---

## 八、异常处理

### 8.1 统一异常处理
```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(ServiceException.class)
    public R<Void> handleServiceException(ServiceException e) {
        log.warn("业务异常: {}", e.getMessage());
        return R.fail(e.getMessage());
    }

    @ExceptionHandler(Exception.class)
    public R<Void> handleException(Exception e) {
        log.error("系统异常", e);
        return R.fail("系统错误");
    }
}
```

### 8.2 业务异常
```java
// 抛出业务异常
throw new ServiceException("用户不存在");
throw new ServiceException("权限不足");
```

---

## 九、任务完成标准

### 9.1 后端接口完成标准
- [ ] 接口返回格式正确
- [ ] 参数校验完整
- [ ] 权限控制配置
- [ ] 异常处理完善
- [ ] 单元测试覆盖
- [ ] 编译测试通过

### 9.2 任务报告模板
```markdown
## Backend-Dev 任务报告

### 任务信息
- ID: [TASK-ID]
- 标题: [任务标题]

### 完成情况
- 状态: ✅ 完成
- 文件: [列表]

### 代码变更
- 新增: [列表]
- 修改: [列表]

### 测试结果
- 编译: ✅ 通过
- 单元测试: ✅ 通过 (X个用例)

### 下一步
[如无则填"无"]
```

---

## 十、限流保护

| 指标 | 限制 |
|------|------|
| 单任务执行时间 | 30分钟 |
| 单任务Token消耗 | 200k |
| 连续失败任务 | 3个后停止，报告用户 |

---

最后更新：2026-04-03
