# 项目级 Claude Code 配置

## 项目记忆
项目记忆文件位于 `memory/` 目录，包含三层结构：
- `project_overview.md` — 项目概述和架构
- `tech_stack.md` — 技术栈详情
- `form_render_architecture.md` — 表单渲染核心架构

**首次对话时先阅读记忆文件**，使用：`Invoke the Skill tool with skill: "memory"`

## 重要规则

### auto-dev 目录
`auto-dev/` 目录是 Claude Code 的自动开发工具目录，**禁止提交到 git**。
确保 `.gitignore` 中已包含 `auto-dev/`。

### 表单渲染组件
- `src/components/form-render/field-widget/` — 预览模式使用的独立字段组件
- `src/components/form-render/container-item/field-renderer.vue` — 设计器内嵌字段渲染器
- **不要混用这两套组件**

### 表单数据模型
- `formDataModel` 定义在 `src/components/form-render/index.vue`
- 是一个 `reactive({})` 对象
- 用户输入通过 `v-model="formModel[field.options.name]"` 绑定

## 工作流程提示

1. 修改表单相关代码前，先阅读 `memory/form_render_architecture.md`
2. 使用 `memory` skill 查看项目记忆
3. auto-dev 目录是本地临时目录，不需要提交
