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

## 【新增】必需的质量工具配置

### 必需的工具配置文件

前端项目必须包含以下配置文件：

| 文件 | 用途 | 必须 |
|------|------|------|
| `.eslintrc.js` | ESLint 配置 | ✅ |
| `.prettierrc` | Prettier 配置 | ✅ |
| `.editorconfig` | 编辑器统一配置 | ✅ |
| `vitest.config.ts` | 测试框架配置 | ✅ |
| `.gitattributes` | Git 统一换行符 | ✅ |

### 必需的质量 npm scripts

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "lint": "eslint src --ext .vue,.ts,.js,.jsx,.tsx --no-fix",
    "lint:fix": "eslint src --ext .vue,.ts,.js,.jsx,.tsx --fix",
    "type-check": "vue-tsc --noEmit",
    "test": "vitest",
    "test:run": "vitest run"
  }
}
```

### ESLint 配置示例 (.eslintrc.js)

```javascript
module.exports = {
  root: true,
  env: {
    browser: true,
    es2021: true,
    node: true,
    'vue/setup-compiler-macros': true,
  },
  extends: [
    'plugin:vue/vue3-essential',
    'plugin:vue/vue3-recommended',
    'plugin:@typescript-eslint/recommended',
    'prettier',
    'plugin:prettier/recommended',
  ],
  parserOptions: {
    ecmaVersion: 'latest',
    parser: '@typescript-eslint/parser',
    sourceType: 'module',
  },
  plugins: ['vue', '@typescript-eslint', 'prettier', 'import'],
  rules: {
    'vue/multi-word-component-names': 'off',
    'vue/require-default-prop': 'off',
    'prettier/prettier': 'error',
    '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
    '@typescript-eslint/no-explicit-any': 'warn',
    'no-console': ['warn', { allow: ['warn', 'error'] }],
  },
}
```

### Prettier 配置示例 (.prettierrc)

```json
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 100,
  "bracketSpacing": true,
  "arrowParens": "always",
  "endOfLine": "lf",
  "vueIndentScriptAndStyle": false
}
```

### EditorConfig 配置示例 (.editorconfig)

```ini
root = true

[*]
charset = utf-8
end_of_line = lf
indent_style = space
indent_size = 2
insert_final_newline = true
trim_trailing_whitespace = true

[*.md]
trim_trailing_whitespace = false
```

### GitAttributes 配置示例 (.gitattributes)

```ini
* text=auto eol=lf
*.bat text eol=crlf
```

### Vitest 配置示例 (vitest.config.ts)

```typescript
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  test: {
    globals: true,
    environment: 'happy-dom',
    include: ['src/**/*.{test,spec}.{ts,tsx,js,jsx}'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      reportsDirectory: 'coverage',
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
```

### Git Hook 规范

```bash
# ✅ pre-commit 只运行 lint（检查）
npm run lint

# ❌ 禁止在 pre-commit 中运行 lint:fix
npm run lint:fix  # 禁止！会自动修改代码
```

---

## 开发完成标准

- [ ] 代码编译通过 (`npm run build`)
- [ ] ESLint 检查通过 (`npm run lint`)
- [ ] TypeScript 类型检查通过 (`npm run type-check`)
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