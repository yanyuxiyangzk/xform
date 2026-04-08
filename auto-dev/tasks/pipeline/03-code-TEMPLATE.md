# 代码开发报告模板

> 存储路径：tasks/pipeline/{PIPELINE-ID}/03-code.md
> 由 backend-dev + frontend-dev 创建

---

## ⚠️ 质量门禁（强制）

**在所有质量门禁通过之前，不得进入测试阶段！**

### Dev 门禁自检

| 门禁 | 命令 | 通过标准 | 实际结果 |
|------|------|----------|----------|
| 编译通过 | `mvn compile -q` | 退出码=0 | _ |
| 测试通过 | `mvn test -q` | 退出码=0 | _ |
| 规范检查 | `mvn checkstyle:check -q` | 退出码=0 | _ |
| 无P0漏洞 | 代码扫描 | 0个P0 | _ |
| 无P1漏洞 | 代码扫描 | 0个P1 | _ |

**自检命令：**
```bash
cd d:/project/aicoding/item/ainocode/ruoyi-nocode
JAVA_HOME="D:/Program Files/Java/jdk-17.0.6" mvn compile -q && mvn test -q && echo "✅ DEV门禁通过"
```

### Reviewer 门禁

| 迭代 | 审核人 | 时间 | 结果 | 说明 |
|------|--------|------|------|------|
| 1/3 | reviewer | - | PENDING | 等待审核 |
| 2/3 | reviewer | - | - |（如需）|
| 3/3 | reviewer | - | - |（如需）|

**门禁结果：**
- [ ] APPROVED - 进入测试阶段
- [ ] REVISION_REQUESTED - 返回开发修复
- [ ] REJECTED - 通知PM人工介入

---

## 基本信息

| 属性 | 值 |
|------|-----|
| 需求编号 | PIPELINE-{YYYYMMDD}-{NNN} |
| 需求名称 | {需求名称} |
| 开发负责人 | {backend-dev} + {frontend-dev} |
| 开始时间 | {时间} |
| 完成时间 | {时间} |
| 代码仓库 | {仓库地址} |

---

## 代码提交记录

### 后端提交

| 提交人 | 时间 | 提交信息 | Commit ID |
|--------|------|----------|-----------|
| backend-dev | - | - | - |

### 前端提交

| 提交人 | 时间 | 提交信息 | Commit ID |
|--------|------|----------|-----------|
| frontend-dev | - | - | - |

---

## 后端开发

### 代码结构

```
{模块名}/
├── src/main/java/{package}/
│   ├── controller/
│   │   └── {Entity}Controller.java
│   ├── service/
│   │   ├── {Entity}Service.java
│   │   └── impl/{Entity}ServiceImpl.java
│   ├── mapper/{Entity}Mapper.java
│   ├── entity/{Entity}.java
│   └── dto/{Entity}DTO.java
├── src/main/resources/mapper/
│   └── {Entity}Mapper.xml
└── src/test/java/{package}/
    └── {Entity}ServiceTest.java
```

### 核心代码

#### Controller
```java
@RestController
@RequestMapping("/api/{entity}")
public class {Entity}Controller {

    @Resource
    private {Entity}Service {entity}Service;

    @GetMapping("/list")
    public R<List<{Entity}DTO>> list({Entity}Query query) {
        return R.ok({entity}Service.selectList(query));
    }

    @PostMapping
    public R<Void> add(@RequestBody {Entity}DTO dto) {
        return R.ok({entity}Service.insert(dto));
    }
}
```

#### Service
```java
public interface {Entity}Service {
    R<List<{Entity}DTO>> selectList({Entity}Query query);
    R<Void> insert({Entity}DTO dto);
}
```

---

## 前端开发

### 代码结构

```
{模块}/
├── src/
│   ├── api/
│   │   └── {entity}.js
│   ├── views/
│   │   └── {entity}/
│   │       ├── index.vue
│   │       └── components/
│   ├── store/
│   └── types/
```

### 核心代码

#### API
```javascript
export function listEntity(query) {
  return request({
    url: '/api/{entity}/list',
    method: 'get',
    params: query
  })
}
```

#### Vue页面
```vue
<template>
  <div class="entity-container">
    <el-table :data="tableData">
      <el-table-column prop="name" label="名称" />
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { listEntity } from '@/api/{entity}'

const tableData = ref([])

onMounted(async () => {
  const res = await listEntity()
  tableData.value = res.data
})
</script>
```

---

## 接口对照

| 接口路径 | 方法 | 后端状态 | 前端状态 | 联调状态 |
|----------|------|----------|----------|----------|
| /api/{entity}/list | GET | - | - | 待联调 |
| /api/{entity} | POST | - | - | 待联调 |

---

## 数据库变更

```sql
-- 如有DDL变更，记录于此
ALTER TABLE {table_name} ADD COLUMN {column_name} {type};
```

---

## 测试用例

| 用例编号 | 描述 | 后端 | 前端 |
|----------|------|------|------|
| TC-001 | 列表查询 | - | - |
| TC-002 | 新增数据 | - | - |
| TC-003 | 编辑数据 | - | - |
| TC-004 | 删除数据 | - | - |

---

## 构建状态

| 环境 | 状态 | 镜像版本 | 构建时间 |
|------|------|----------|----------|
| DEV | - | - | - |
| TEST | - | - | - |

---

## 代码审查

### 审核状态

| 迭代 | 审核人 | 时间 | 结果 | 关键问题 |
|------|--------|------|------|----------|
| - | reviewer | - | PENDING | - |

### 审核详情

#### 审核标准（严格模式）
- [ ] 编译成功，无错误（`mvn compile` 退出码=0）
- [ ] 单元测试通过率 ≥ 90%
- [ ] **无P0安全漏洞**（SQL注入、硬编码密码、不安全反序列化等）
- [ ] 无P1安全漏洞（XSS、CSRF、路径遍历等）
- [ ] 无硬编码密钥/密码/凭证
- [ ] 命名规范符合RULES.md
- [ ] 必要的Javadoc注释
- [ ] `mvn checkstyle:check` 通过

#### 迭代记录

**迭代 1/3**
- 时间：
- 结果：
- 问题列表：
  - 无

**迭代 2/3**（如需）
- 时间：
- 结果：
- 问题列表：

**迭代 3/3**（如需）
- 时间：
- 结果：
- 问题列表：

---

## 自检清单（提交前必须全部通过）

- [ ] `mvn compile -q` 通过（无错误）
- [ ] `mvn test -q` 通过（测试通过率≥90%）
- [ ] `mvn checkstyle:check -q` 通过
- [ ] 已添加单元测试（覆盖率≥70%）
- [ ] 无安全漏洞（SQL注入、XSS、硬编码密码等）
- [ ] 已完成接口联调
- [ ] API文档已更新
- [ ] 日志记录完整
- [ ] 异常处理完善
- [ ] **禁止使用 `-DskipTests` 或 `-Dmaven.test.skip=true`**

---

## 备注与问题

{开发过程中遇到的问题及解决方案}

---

最后更新：{时间}
