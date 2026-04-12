# xform/sform 低代码表单设计器 - 开发计划

## 项目概述
Vue 3 + Element Plus + vuedraggable 构建的低代码表单设计器

## 当前问题分析

### Bug #1: 中间画布区域组件不显示
**根因**: `form-widget/index.vue` 中 `widgetList` 是 computed 属性，vuedraggable 的 `:list` 绑定需要直接操作响应式数组。
```javascript
// 当前代码 - 有问题
const widgetList = computed(() => props.designer.widgetList || [])
```
vuedraggable 4.x 要求直接绑定响应式数组，而不是 computed 属性。

**修复方案**: 传递 `designer.widgetList` 直接绑定，并在父组件确保响应式。

---

## 待开发功能

### Feature #1: 表单模板功能
- **配置**: `designerConfig.formTemplates: true` (已有)
- **UI**: 工具栏添加模板按钮，点击弹出模板选择对话框
- **模板来源**: 内置模板 + 用户自定义模板
- **功能**: 选择模板后加载预设的 widgetList 和 formConfig

### Feature #2: 组件市场功能
- **功能**: 类似模板，但是以组件为单位的市场
- **UI**: 左侧面板新增"组件市场" Tab 页
- **支持**: 组件搜索、分类浏览、一键添加到画布

### Feature #3: 数据源功能
- **配置**: `designerConfig.dataSourceButton: true` (已有)
- **类型**: DataSource 接口已定义 (url, method, headers, params, dataPath, labelKey, valueKey)
- **UI**: 工具栏数据源按钮，点击弹出数据源管理对话框
- **功能**: 添加/编辑/删除数据源，绑定到下拉框等组件

---

## 实现计划

### Phase 1: Bug Fix
1. 修复 `form-widget/index.vue` 中的 widgetList 绑定问题
2. 验证拖拽功能正常工作

### Phase 2: Form Templates Feature
1. 创建 `template-dialog.vue` 组件
2. 定义内置模板数据结构
3. 集成到 toolbar-panel

### Phase 3: Widget Market Feature
1. 创建 `market-panel.vue` 组件
2. 添加市场数据配置
3. 集成到 widget-panel 作为新 Tab

### Phase 4: Data Source Feature
1. 创建 `datasource-dialog.vue` 组件
2. 实现 CRUD 操作
3. 集成到 toolbar-panel

### Phase 5: Build Verification
- 运行 `npm run build` 确保无错误

---

## 文件结构变更

```
src/components/form-designer/
├── form-widget/
│   └── index.vue           # [修复] widgetList 绑定
├── toolbar-panel/
│   ├── index.vue          # [新增] 模板、数据源按钮
│   ├── template-dialog.vue    # [新增]
│   └── datasource-dialog.vue  # [新增]
├── widget-panel/
│   ├── index.vue          # [新增] 市场 Tab
│   └── market-panel.vue   # [新增]
└── setting-panel/
    └── form-setting.vue    # [修改] 数据源绑定配置
```
