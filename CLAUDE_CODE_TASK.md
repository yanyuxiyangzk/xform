## 任务：XForm 低代码表单设计器 - 组件市场开发

### 项目信息
- 项目路径：D:\project\aicoding\item\xform
- 技术栈：Vue 3 + TypeScript + Element Plus + Vite + Sass
- 项目类型：低代码表单可视化设计器

### 项目结构
```
xform/
├── src/
│   ├── components/
│   │   ├── form-designer/       # 表单设计器
│   │   │   ├── designer.ts      # 设计器状态管理
│   │   │   ├── index.vue        # 设计器入口
│   │   │   ├── form-widget/     # 画布组件渲染
│   │   │   ├── widget-panel/    # 左侧组件面板
│   │   │   ├── setting-panel/   # 右侧属性面板
│   │   │   └── toolbar-panel/   # 顶部工具栏
│   │   └── form-render/        # 表单渲染器
│   ├── extension/              # 扩展组件（data-wrapper, edit-table, tree-view）
│   ├── utils/                   # 工具函数
│   ├── lang/                    # 国际化
│   ├── styles/                  # 样式（含theme/主题系统）
│   │   └── theme/               # 主题系统
│   └── types/                   # TypeScript类型
├── package.json
├── vite.config.ts
└── SPEC.md
```

### 需求背景
XForm 是一款 Vue 3 低代码表单设计器，已经完成了：
- ✅ 自定义主题系统（theme/目录）
- ✅ 扩展组件机制（extension/目录）

现在需要开发 **组件市场** 功能，让开发者可以打包、分享、安装自定义组件。

### 需要开发的功能：组件市场

根据 PRD v3.2 规划，组件市场包括：

#### 功能清单
1. **组件打包导出**
   - 将自定义组件打包为 .xform-widget 文件（本质是 zip/json）
   - 包含组件Schema、渲染器、图标资源
   - 支持导出组件包

2. **组件包导入安装**
   - 导入 .xform-widget 文件
   - 解析并验证组件包
   - 一键安装到设计器

3. **组件管理面板**
   - 显示已安装的自定义组件
   - 支持禁用/启用组件
   - 支持卸载组件

4. **组件市场UI（本地模拟）**
   - 组件列表展示（内置示例组件）
   - 组件分类（容器、字段、布局）
   - 组件搜索
   - 组件详情查看

### 技术方案

#### 1. 组件包格式 (.xform-widget)
```typescript
interface WidgetPackage {
  id: string                    // 组件唯一标识
  name: string                  // 组件显示名称
  version: string               // 版本号
  author: string                // 作者
  description: string           // 描述
  category: 'container' | 'field' | 'layout'  // 分类
  icon: string                 // 图标名称
  schema: WidgetSchema          // 组件Schema（用于设计器）
  renderer: string              // 渲染器组件代码（Vue SFC）
  preview?: string             // 预览图（base64）
  tags: string[]               // 标签
  createdAt: string             // 创建时间
}
```

#### 2. 文件结构
```
src/
├── components/
│   └── form-designer/
│       └── widget-panel/
│           └── component-market/      # 新增：组件市场
│               ├── index.vue         # 组件市场主面板
│               ├── market-list.vue    # 市场组件列表
│               ├── installed-list.vue # 已安装组件
│               ├── widget-card.vue   # 组件卡片
│               └── install-dialog.vue # 安装确认对话框
├── extension/                        # 已有扩展机制
├── styles/theme/                     # 已有主题系统
└── utils/
    └── widget-package.ts             # 新增：组件包工具
```

#### 3. 实现细节

**WidgetPackageManager 类** (`utils/widget-package.ts`):
```typescript
class WidgetPackageManager {
  // 导出组件包
  exportPackage(widget: WidgetSchema, rendererCode: string): WidgetPackage
  
  // 导入安装组件
  importPackage(jsonStr: string): WidgetPackage
  
  // 获取已安装组件
  getInstalledPackages(): WidgetPackage[]
  
  // 卸载组件
  uninstallPackage(id: string): void
  
  // 启用/禁用组件
  togglePackage(id: string, enabled: boolean): void
}
```

**存储**:
- localStorage 存储已安装组件列表
- 组件渲染器代码使用 localStorage 或 IndexedDB 存储（大文本）

#### 4. 与现有系统的集成

**组件面板集成**:
- 在 widget-panel 添加"组件市场"入口按钮
- 点击打开组件市场面板（抽屉/Dialog）

**扩展机制利用**:
- 复用 extension-loader.ts 的 addContainerWidgetSchema
- 复用 registerContainerWidget/registerContainerItem 注册组件

**主题系统利用**:
- 组件市场UI使用主题变量保持一致性

### 开发要求
1. 遵循项目现有代码规范（Vue 3 Composition API + TypeScript）
2. 组件包格式要可扩展，便于后续支持npm包发布
3. UI要使用Element Plus组件，保持与设计器风格一致
4. 提供示例组件包演示功能（至少1个）
5. 支持拖拽导入组件包文件

### 验收标准
- [ ] 可以在组件面板中打开组件市场
- [ ] 可以浏览（本地模拟的）组件列表
- [ ] 可以搜索组件
- [ ] 可以导出自定义组件为 .xform-widget 文件
- [ ] 可以导入安装 .xform-widget 文件
- [ ] 可以查看已安装组件列表
- [ ] 可以禁用/卸载已安装组件
- [ ] 安装的组件可以在设计器中使用

### 输出要求
完成开发后，输出：
1. 新增/修改的文件列表
2. 组件市场的使用说明
3. 代码测试验证结果
