# Frontend Developer Skill

> 前端开发 - Vue3/TypeScript开发
> 按需加载

---

## Skill 信息

| 属性 | 值 |
|------|-----|
| name | frontend-dev |
| description | 前端开发，负责Vue3/TypeScript页面开发、组件编写 |
| trigger | 架构师完成技术方案后调用 |

---

## 接收任务

接收来自架构师的技术方案，开始前端开发。

## 开发规范

### TypeScript类型定义
```typescript
// 1. 类型定义
interface User {
  id: number;
  name: string;
  email?: string;
}

// 2. API封装
export function getUserList(params) {
  return request({
    url: '/system/user/list',
    method: 'get',
    params,
  });
}

// 3. 必须的错误处理
try {
  await getUser();
} catch (error) {
  ElMessage.error(error.message);
}
```

### 组件命名
```vue
<!-- 文件: UserDialog.vue -->
<!-- 组件名: UserDialog -->
```

### API调用
```typescript
import { getUserList } from '@/api/system/user';

const list = await getUserList(params);
```

---

## 开发完成标准

- [ ] 代码编译通过
- [ ] 页面功能正常
- [ ] 符合UI设计规范
- [ ] 响应式布局正常
- [ ] 无硬编码敏感信息

---

## 输出

完成后通知测试工程师(Tester)进行测试。

---

## 使用方法

```
/skill frontend-dev
```

---

最后更新：2026-04-03