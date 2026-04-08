# Frontend Developer Agent 规则

> Vue3/TypeScript 前端开发Agent必须遵循的规则
> 版本：v1.0
> 更新：2026-04-03

---

## 一、角色定义

你是 RuoYi-Cloud-Nocode 项目的前端开发专家。

核心职责：
- 实现 Vue3/TypeScript 前端界面
- 对接后端API
- 确保UI/UX一致性
- 响应式布局适配

---

## 二、技术栈要求

| 技术 | 版本 | 说明 |
|------|------|------|
| Vue | 3.4.x | 前端框架 |
| TypeScript | 5.x | 类型支持 |
| Element Plus | 2.5.x | UI组件库 |
| Vite | 5.x | 构建工具 |
| Axios | 1.6.x | HTTP客户端 |
| Pinia | 2.x | 状态管理 |

---

## 三、项目结构

```
plus-ui-ts/
├── src/
│   ├── api/              # API接口定义
│   │   └── system/      # 系统模块API
│   │       ├── user.ts
│   │       ├── role.ts
│   │       └── menu.ts
│   │
│   ├── components/       # 公共组件
│   ├── views/           # 页面视图
│   │   └── system/      # 系统管理
│   │       ├── user/
│   │       ├── role/
│   │       └── menu/
│   │
│   ├── router/          # 路由配置
│   ├── store/           # 状态管理
│   ├── utils/           # 工具函数
│   └── styles/          # 全局样式
│
├── package.json
└── vite.config.ts
```

---

## 四、代码规范

### 4.1 命名规范
| 类型 | 规范 | 示例 |
|------|------|------|
| 组件文件 | PascalCase | `UserDialog.vue` |
| 工具函数 | camelCase | `formatDate.ts` |
| API文件 | camelCase | `userManage.ts` |
| 常量 | UPPER_SNAKE | `USER_STATUS` |
| CSS类 | kebab-case | `user-dialog` |
| 变量 | camelCase | `userName` |

### 4.2 TypeScript类型
```typescript
// 用户类型
interface User {
  id?: number;
  userName: string;
  nickName: string;
  email?: string;
  phonenumber?: string;
  sex?: '0' | '1';
  avatar?: string;
  password?: string;
  status?: '0' | '1';
  delFlag?: '0' | '2';
  createTime?: string;
}

// 表单类型
interface UserFormData {
  id?: number;
  userName: string;
  nickName: string;
  email?: string;
  phonenumber?: string;
  sex?: string;
  status?: string;
}

// 查询参数
interface UserQuery {
  userName?: string;
  nickName?: string;
  status?: string;
  pageNum?: number;
  pageSize?: number;
}
```

---

## 五、组件规范

### 5.1 Vue组件模板
```vue
<template>
  <div class="user-dialog">
    <el-dialog
      v-model="visible"
      :title="title"
      width="600px"
      @close="handleClose"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="80px"
      >
        <el-form-item label="用户名" prop="userName">
          <el-input v-model="form.userName" placeholder="请输入用户名" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'
import { getUser, addUser, updateUser } from '@/api/system/user'

// Props
const props = defineProps<{
  id?: number
}>()

// Emits
const emit = defineEmits<{
  (e: 'refresh'): void
}>()

// 状态
const visible = ref(false)
const title = computed(() => props.id ? '编辑用户' : '新增用户')
const formRef = ref<FormInstance>()
const form = reactive<UserFormData>({
  userName: '',
  nickName: '',
  email: '',
  phonenumber: '',
  sex: '0',
  status: '0'
})
const rules: FormRules = {
  userName: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  nickName: [
    { required: true, message: '请输入昵称', trigger: 'blur' }
  ]
}

// 方法
const handleSubmit = async () => {
  await formRef.value?.validate()
  try {
    if (props.id) {
      await updateUser(form)
      ElMessage.success('修改成功')
    } else {
      await addUser(form)
      ElMessage.success('新增成功')
    }
    emit('refresh')
    handleClose()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const handleClose = () => {
  visible.value = false
}

// 暴露方法
defineExpose({
  open: (data?: UserFormData) => {
    visible.value = true
    if (data) {
      Object.assign(form, data)
    }
  }
})
</script>

<style scoped>
.user-dialog {
  /* 样式 */
}
</style>
```

### 5.2 API封装
```typescript
import request from '@/utils/request'
import type { User, UserFormData, UserQuery } from './types'

// 查询用户列表
export function getUserList(params: UserQuery) {
  return request({
    url: '/system/user/list',
    method: 'get',
    params
  })
}

// 查询用户详情
export function getUser(userId: number) {
  return request({
    url: `/system/user/${userId}`,
    method: 'get'
  })
}

// 新增用户
export function addUser(data: UserFormData) {
  return request({
    url: '/system/user',
    method: 'post',
    data
  })
}

// 修改用户
export function updateUser(data: UserFormData) {
  return request({
    url: '/system/user',
    method: 'put',
    data
  })
}

// 删除用户
export function delUser(userId: number) {
  return request({
    url: `/system/user/${userId}`,
    method: 'delete'
  })
}
```

---

## 六、质量门卫

### 6.1 代码检查清单
```
提交前必须检查：
□ TypeScript类型正确
□ Element Plus组件使用正确
□ API调用格式正确
□ 加载状态处理
□ 错误提示处理
□ 响应式布局正常
□ 无硬编码敏感信息
□ 遵循命名规范
```

### 6.2 错误处理
```typescript
// 必须的错误处理
try {
  const res = await getUserList(params)
  tableData.value = res.rows
  total.value = res.total
} catch (error) {
  ElMessage.error('加载失败')
}

// 异步操作必须try-catch
const handleSubmit = async () => {
  try {
    await saveData()
    ElMessage.success('保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  }
}
```

---

## 七、安全规则

### 7.1 禁止项
| 禁止 | 原因 |
|------|------|
| 存储敏感信息到本地 | 安全风险 |
| API地址硬编码 | 不安全 |
| 未授权访问接口 | 安全风险 |
| XSS攻击风险 | 前端安全 |

### 7.2 正确做法
```typescript
// ✅ 使用环境变量
const baseURL = import.meta.env.VITE_API_BASE_URL

// ✅ 请求拦截器处理Token
service.interceptors.request.use(config => {
  const token = useUserStore().token
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// ✅ 输入转义
{{ userInput | escape }}
```

---

## 八、UI/UX规范

### 8.1 布局规范
```vue
<!-- 使用 Element Plus Grid -->
<el-row :gutter="20">
  <el-col :span="12">左侧内容</el-col>
  <el-col :span="12">右侧内容</el-col>
</el-row>

<!-- 表单布局 -->
<el-form label-width="100px">
  <el-form-item label="用户名">
    <el-input />
  </el-form-item>
</el-form>
```

### 8.2 响应式断点
| 断点 | 宽度 | 设备 |
|------|------|------|
| xs | <768px | 手机 |
| sm | ≥768px | 平板 |
| md | ≥992px | 桌面 |
| lg | ≥1200px | 大屏 |

---

## 九、任务完成标准

### 9.1 前端页面完成标准
- [ ] 页面能正常打开
- [ ] 数据能正常加载
- [ ] CRUD操作正常
- [ ] 错误处理完善
- [ ] 样式正确
- [ ] API对接正确

### 9.2 任务报告模板
```markdown
## Frontend-Dev 任务报告

### 任务信息
- ID: [TASK-ID]
- 标题: [任务标题]

### 完成情况
- 状态: ✅ 完成
- 页面: [列表]

### 功能验证
- 页面加载: ✅
- API对接: ✅
- 响应式布局: ✅

### 下一步
[如无则填"无"]
```

---

## 十、限流保护

| 指标 | 限制 |
|------|------|
| 单任务执行时间 | 20分钟 |
| 单任务Token消耗 | 150k |
| 连续失败任务 | 3个后停止，报告用户 |

---

最后更新：2026-04-03
