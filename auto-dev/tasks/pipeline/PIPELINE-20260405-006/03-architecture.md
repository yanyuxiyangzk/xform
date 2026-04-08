# 表单设计器架构设计文档

## 1. 技术栈选型

| 类别 | 新架构 | 原项目(vform3-pro) | 优势 |
|------|--------|-------------------|------|
| UI框架 | Naive UI | Element Plus | 更轻量、组件设计更现代 |
| 状态管理 | Pinia | 手动状态管理 | 类型安全、DevTools支持、模块化 |
| 拖拽库 | vue-draggable-plus | vuedraggable | Vue3原生支持、TypeScript友好 |
| 构建工具 | Vite 5.x | Webpack | 极速HMR、更好的ESM支持 |
| 样式方案 | SCSS + CSS变量 | SCSS全局导入 | 局部作用域、主题切换更灵活 |

---

## 2. 目录结构

```
src/
├── components/
│   ├── form-designer/              # 表单设计器主组件
│   │   ├── FormDesigner.vue        # 设计器入口
│   │   ├── FormDesignerProvider.vue # 上下文提供者
│   │   ├── designer-main/          # 设计器主区域
│   │   │   ├── DesignerCanvas.vue   # 画布
│   │   │   ├── ComponentPalette.vue # 组件面板
│   │   │   └── DesignerToolbar.vue  # 工具栏
│   │   ├── designer-props/          # 属性面板
│   │   │   ├── PropertyPanel.vue    # 属性面板入口
│   │   │   ├── PropertyEditor.vue   # 属性编辑器
│   │   │   └── editors/             # 具体属性编辑器
│   │   └── designer-setttings/      # 设计器设置
│   ├── form-renderer/              # 表单渲染器
│   │   ├── FormRenderer.vue        # 渲染器入口
│   │   ├── FormRendererProvider.vue # 渲染上下文
│   │   └── FieldRenderer.vue       # 字段渲染器
│   ├── widgets/                    # 组件库
│   │   ├── field/                  # 字段组件
│   │   │   ├── InputWidget.vue
│   │   │   ├── SelectWidget.vue
│   │   │   ├── DatePickerWidget.vue
│   │   │   └── index.ts            # 自动导出
│   │   ├── container/              # 容器组件
│   │   │   ├── GridWidget.vue
│   │   │   ├── TabsWidget.vue
│   │   │   └── index.ts
│   │   └── types/                  # 组件类型定义
│   │       └── widget.interface.ts
│   └── common/                     # 公共组件
│       ├── DraggableContainer.vue
│       └── FormItemWrapper.vue
├── stores/                         # Pinia状态管理
│   ├── designerStore.ts            # 设计器状态
│   ├── widgetStore.ts              # 组件配置状态
│   ├── historyStore.ts             # 撤销/重做
│   └── schemaStore.ts              # 表单Schema状态
├── composables/                    # 组合式函数
│   ├── useDesigner.ts             # 设计器上下文
│   ├── useWidgetRegistry.ts       # 组件注册
│   ├── useDragDrop.ts             # 拖拽逻辑
│   ├── usePropertyEditor.ts       # 属性编辑
│   └── useFormRenderer.ts         # 渲染器逻辑
├── utils/                         # 工具函数
│   ├── widget-registry.ts         # 组件注册表
│   ├── property-editor-registry.ts # 属性编辑器注册表
│   ├── schema-transformer.ts      # Schema转换
│   ├── validation.ts               # 校验规则
│   └── style-generator.ts          # 样式生成
├── types/                         # 全局类型定义
│   ├── form-schema.ts             # 表单Schema类型
│   ├── widget-config.ts           # 组件配置类型
│   └── designer-context.ts         # 设计器上下文类型
├── styles/                        # 全局样式
│   ├── variables.scss             # CSS变量
│   ├── mixins.scss                # 混合宏
│   └── designer.scss              # 设计器样式
└── App.vue
```

---

## 3. 核心模块设计

### 3.1 WidgetRegistry - 组件注册机制

**设计理念**: 使用 `Symbol` 作为组件标识符，避免字符串硬编码，实现类型安全的组件注册。

```typescript
// types/widget-type.ts
export const WIDGET_TYPE = {
  // 字段组件
  INPUT: Symbol('INPUT'),
  SELECT: Symbol('SELECT'),
  DATE_PICKER: Symbol('DATE_PICKER'),
  NUMBER_INPUT: Symbol('NUMBER_INPUT'),
  TEXTAREA: Symbol('TEXTAREA'),
  RADIO: Symbol('RADIO'),
  CHECKBOX: Symbol('CHECKBOX'),
  SWITCH: Symbol('SWITCH'),
  SLIDER: Symbol('SLIDER'),
  TIME_PICKER: Symbol('TIME_PICKER'),
  UPLOAD: Symbol('UPLOAD'),

  // 容器组件
  GRID: Symbol('GRID'),
  TABS: Symbol('TABS'),
  CARD: Symbol('CARD'),
  DIVIDER: Symbol('DIVIDER'),
  COLLAPSE: Symbol('COLLAPSE'),
} as const;

export type WidgetType = typeof WIDGET_TYPE[keyof typeof WIDGET_TYPE];
```

**注册表实现**:

```typescript
// utils/widget-registry.ts
import { h, defineComponent } from 'vue';
import type { Component } from 'vue';

export interface WidgetDefinition {
  type: symbol;
  name: string;
  icon: string;
  label: string;
  category: 'field' | 'container';
  defaultProps: Record<string, any>;
  propsSchema: PropsSchema[];
 拖拽配置?: DragConfig;
}

class WidgetRegistry {
  private registry = new Map<symbol, WidgetDefinition>();
  private componentMap = new Map<symbol, Component>();

  register(definition: WidgetDefinition, component: Component): void {
    this.registry.set(definition.type, definition);
    this.componentMap.set(definition.type, component);
  }

  getDefinition(type: symbol): WidgetDefinition | undefined {
    return this.registry.get(type);
  }

  getComponent(type: symbol): Component | undefined {
    return this.componentMap.get(type);
  }

  getAllDefinitions(): WidgetDefinition[] {
    return Array.from(this.registry.values());
  }

  getByCategory(category: 'field' | 'container'): WidgetDefinition[] {
    return this.getAllDefinitions().filter(d => d.category === category);
  }
}

export const widgetRegistry = new WidgetRegistry();
```

**自动化扫描注册**:

```typescript
// composables/useWidgetRegistry.ts
export function useWidgetRegistry() {
  const fieldWidgets = import.meta.glob('@/components/widgets/field/*.vue', { eager: true });
  const containerWidgets = import.meta.glob('@/components/widgets/container/*.vue', { eager: true });

  const registerWidgets = (registry: WidgetRegistry) => {
    // 字段组件自动注册
    for (const [path, module] of Object.entries(fieldWidgets)) {
      const name = path.split('/').pop()?.replace('.vue', '') ?? '';
      const definition = createFieldDefinition(name);
      registry.register(definition, (module as any).default);
    }

    // 容器组件自动注册
    for (const [path, module] of Object.entries(containerWidgets)) {
      const name = path.split('/').pop()?.replace('.vue', '') ?? '';
      const definition = createContainerDefinition(name);
      registry.register(definition, (module as any).default);
    }
  };

  return { registerWidgets };
}
```

### 3.2 designerStore - 设计器状态管理

**使用 Pinia 进行状态管理**:

```typescript
// stores/designerStore.ts
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { FormSchema, WidgetConfig, DesignerState } from '@/types';

export const useDesignerStore = defineStore('designer', () => {
  // 状态
  const schema = ref<FormSchema | null>(null);
  const selectedWidgetId = ref<string | null>(null);
  const hoveredWidgetId = ref<string | null>(null);
  const clipboardData = ref<WidgetConfig | null>(null);
  const designerMode = ref<'design' | 'preview' | 'json'>('design');
  const canvasSize = ref({ width: 1200, height: 'auto' });

  // 计算属性
  const selectedWidget = computed(() => {
    if (!schema.value || !selectedWidgetId.value) return null;
    return findWidgetById(schema.value.widgets, selectedWidgetId.value);
  });

  const isDirty = ref(false);

  // Actions
  function setSchema(newSchema: FormSchema) {
    schema.value = newSchema;
    isDirty.value = true;
  }

  function selectWidget(widgetId: string | null) {
    selectedWidgetId.value = widgetId;
  }

  function addWidget(parentId: string | null, widget: WidgetConfig, index?: number) {
    if (!schema.value) return;

    if (parentId === null) {
      // 添加到根
      if (index !== undefined) {
        schema.value.widgets.splice(index, 0, widget);
      } else {
        schema.value.widgets.push(widget);
      }
    } else {
      // 添加到容器
      const parent = findWidgetById(schema.value.widgets, parentId);
      if (parent?.children) {
        if (index !== undefined) {
          parent.children.splice(index, 0, widget);
        } else {
          parent.children.push(widget);
        }
      }
    }
    isDirty.value = true;
  }

  function removeWidget(widgetId: string) {
    if (!schema.value) return;
    removeWidgetFromTree(schema.value.widgets, widgetId);
    if (selectedWidgetId.value === widgetId) {
      selectedWidgetId.value = null;
    }
    isDirty.value = true;
  }

  function updateWidgetProps(widgetId: string, props: Record<string, any>) {
    if (!schema.value) return;
    const widget = findWidgetById(schema.value.widgets, widgetId);
    if (widget) {
      widget.props = { ...widget.props, ...props };
      isDirty.value = true;
    }
  }

  function moveWidget(fromId: string, toId: string | null, index: number) {
    if (!schema.value) return;
    const widget = removeWidgetFromTree(schema.value.widgets, fromId);
    if (!widget) return;

    if (toId === null) {
      schema.value.widgets.splice(index, 0, widget);
    } else {
      const parent = findWidgetById(schema.value.widgets, toId);
      if (parent?.children) {
        parent.children.splice(index, 0, widget);
      }
    }
    isDirty.value = true;
  }

  return {
    // 状态
    schema,
    selectedWidgetId,
    hoveredWidgetId,
    clipboardData,
    designerMode,
    canvasSize,
    isDirty,

    // 计算属性
    selectedWidget,

    // Actions
    setSchema,
    selectWidget,
    addWidget,
    removeWidget,
    updateWidgetProps,
    moveWidget,
  };
});
```

### 3.3 PropertyEditorRegistry - 属性编辑器注册

**使用工厂模式 + TypeScript泛型**:

```typescript
// types/property-editor.ts
import type { Component } from 'vue';

export interface PropertyEditorDef {
  propType: string;  // 'string' | 'number' | 'boolean' | 'select' | 'color' | etc.
  component: Component;
  props?: Record<string, any>;
}

export const PROP_TYPE = {
  STRING: 'string',
  NUMBER: 'number',
  BOOLEAN: 'boolean',
  SELECT: 'select',
  MULTI_SELECT: 'multi-select',
  COLOR: 'color',
  FONT_SIZE: 'font-size',
  BORDER: 'border',
  SHADOW: 'shadow',
  SPACING: 'spacing',
  EVENT_HANDLER: 'event-handler',
  OPTIONS: 'options',
  DYNAMIC_EXPRESSION: 'dynamic-expression',
} as const;
```

**注册表实现**:

```typescript
// utils/property-editor-registry.ts
import type { Component } from 'vue';
import type { PropertyEditorDef } from '@/types/property-editor';

class PropertyEditorRegistry {
  private registry = new Map<string, Component>();

  register(propType: string, component: Component, options?: Record<string, any>): void {
    this.registry.set(propType, component);
  }

  get(propType: string): Component | undefined {
    return this.registry.get(propType);
  }

  has(propType: string): boolean {
    return this.registry.has(propType);
  }
}

export const propertyEditorRegistry = new PropertyEditorRegistry();

// 内置编辑器注册
import StringEditor from '@/components/designer-props/editors/StringEditor.vue';
import NumberEditor from '@/components/designer-props/editors/NumberEditor.vue';
import BooleanEditor from '@/components/designer-props/editors/BooleanEditor.vue';
import SelectEditor from '@/components/designer-props/editors/SelectEditor.vue';
import ColorEditor from '@/components/designer-props/editors/ColorEditor.vue';
import OptionsEditor from '@/components/designer-props/editors/OptionsEditor.vue';

propertyEditorRegistry.register(PROP_TYPE.STRING, StringEditor);
propertyEditorRegistry.register(PROP_TYPE.NUMBER, NumberEditor);
propertyEditorRegistry.register(PROP_TYPE.BOOLEAN, BooleanEditor);
propertyEditorRegistry.register(PROP_TYPE.SELECT, SelectEditor);
propertyEditorRegistry.register(PROP_TYPE.COLOR, ColorEditor);
propertyEditorRegistry.register(PROP_TYPE.OPTIONS, OptionsEditor);
```

**属性编辑器工厂**:

```typescript
// composables/usePropertyEditor.ts
import { computed } from 'vue';
import { propertyEditorRegistry, PROP_TYPE } from '@/utils/property-editor-registry';

export function usePropertyEditor(propType: string, options?: Record<string, any>) {
  const EditorComponent = computed(() => {
    return propertyEditorRegistry.get(propType) ?? propertyEditorRegistry.get(PROP_TYPE.STRING);
  });

  return {
    EditorComponent,
    options,
  };
}
```

### 3.4 dragDropManager - 拖拽上下文管理

**使用 vue-draggable-plus**:

```typescript
// composables/useDragDrop.ts
import { provide, inject, reactive, type InjectionKey } from 'vue';
import type { WidgetConfig, DragState } from '@/types';

interface DragDropContext {
  isDragging: boolean;
  dragData: WidgetConfig | null;
  dropTargetId: string | null;
  dropIndex: number;
}

const DRAG_DROP_KEY: InjectionKey<DragDropContext> = Symbol('dragDrop');

export function createDragDropContext() {
  return reactive<DragDropContext>({
    isDragging: false,
    dragData: null,
    dropTargetId: null,
    dropIndex: -1,
  });
}

export function provideDragDrop(context: DragDropContext) {
  provide(DRAG_DROP_KEY, context);
}

export function useDragDrop() {
  const context = inject(DRAG_DROP_KEY);
  if (!context) {
    throw new Error('useDragDrop must be used within DragDropProvider');
  }

  function startDrag(widget: WidgetConfig) {
    context.isDragging = true;
    context.dragData = widget;
  }

  function endDrag() {
    context.isDragging = false;
    context.dragData = null;
    context.dropTargetId = null;
    context.dropIndex = -1;
  }

  function setDropTarget(targetId: string | null, index: number) {
    context.dropTargetId = targetId;
    context.dropIndex = index;
  }

  return {
    ...context,
    startDrag,
    endDrag,
    setDropTarget,
  };
}
```

### 3.5 formRenderer - 表单渲染引擎

```typescript
// components/form-renderer/FormRenderer.vue
<script setup lang="ts">
import { computed, provide } from 'vue';
import { useFormRenderer } from '@/composables/useFormRenderer';
import FieldRenderer from './FieldRenderer.vue';
import type { FormSchema } from '@/types';

const props = defineProps<{
  schema: FormSchema;
  modelValue?: Record<string, any>;
  disabled?: boolean;
  readonly?: boolean;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: Record<string, any>): void;
  (e: 'fieldChange', field: string, value: any): void;
}>();

const { formData, updateField, validate, resetFields } = useFormRenderer(props.schema, props.modelValue);

provide('formRenderer', {
  formData,
  updateField,
  disabled: computed(() => props.disabled),
  readonly: computed(() => props.readonly),
});
</script>

<template>
  <n-form
    :model="formData"
    :disabled="disabled"
    @submit.prevent="handleSubmit"
  >
    <FieldRenderer
      v-for="widget in schema.widgets"
      :key="widget.id"
      :widget="widget"
    />
  </n-form>
</template>
```

---

## 4. 组件JSON Schema格式设计

```typescript
// types/form-schema.ts

export interface FormSchema {
  id: string;
  name: string;
  version: string;
  description?: string;
  props: FormProps;
  widgets: WidgetConfig[];
  events?: EventConfig[];
  rules?: ValidationRule[];
}

export interface FormProps {
  layout: 'horizontal' | 'vertical' | 'inline';
  labelWidth?: number | 'auto';
  labelAlign?: 'left' | 'right';
  hideRequiredMark?: boolean;
  size?: 'small' | 'medium' | 'large';
}

export interface WidgetConfig {
  id: string;
  type: symbol;  // 使用Symbol而非字符串
  widgetName: string;
  props: Record<string, any>;
  children?: WidgetConfig[];
  condition?: ConditionExpression;
  events?: WidgetEventConfig[];
}

export interface ConditionExpression {
  field: string;
  operator: '==' | '!=' | '>' | '<' | '>=' | '<=' | 'contains' | 'empty';
  value: any;
}

export interface EventConfig {
  name: string;
  handler: string;  // JavaScript表达式或函数名
}
```

**Schema示例**:

```json
{
  "id": "form-001",
  "name": "用户信息表单",
  "version": "1.0.0",
  "props": {
    "layout": "vertical",
    "labelWidth": 120,
    "size": "medium"
  },
  "widgets": [
    {
      "id": "grid-001",
      "type": "Symbol(GRID)",
      "widgetName": "GridWidget",
      "props": {
        "columns": 3,
        "gutter": 16
      },
      "children": [
        {
          "id": "input-001",
          "type": "Symbol(INPUT)",
          "widgetName": "InputWidget",
          "props": {
            "label": "用户名",
            "placeholder": "请输入用户名",
            "defaultValue": "",
            "disabled": false,
            "clearable": true,
            "maxlength": 50
          },
          "condition": null,
          "events": [
            {
              "name": "onChange",
              "handler": "handleUsernameChange"
            }
          ]
        },
        {
          "id": "select-001",
          "type": "Symbol(SELECT)",
          "widgetName": "SelectWidget",
          "props": {
            "label": "部门",
            "placeholder": "请选择部门",
            "options": [
              { "label": "技术部", "value": "tech" },
              { "label": "运营部", "value": "ops" }
            ],
            "multiple": false
          }
        }
      ]
    }
  ]
}
```

---

## 5. 状态管理设计

### 5.1 Pinia Store 架构

```
stores/
├── index.ts              # 统一导出
├── designerStore.ts     # 设计器状态（选中、拖拽、剪贴板）
├── schemaStore.ts        # 表单Schema状态
├── widgetStore.ts        # 组件配置状态
├── historyStore.ts       # 撤销/重做历史
└── uiStore.ts            # UI状态（面板显隐、缩放）
```

### 5.2 historyStore - 撤销/重做

```typescript
// stores/historyStore.ts
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useHistoryStore = defineStore('history', () => {
  const undoStack = ref<FormSchema[]>([]);
  const redoStack = ref<FormSchema[]>([]);
  const maxHistorySize = 50;

  const canUndo = computed(() => undoStack.value.length > 0);
  const canRedo = computed(() => redoStack.value.length > 0);

  function pushState(schema: FormSchema) {
    undoStack.value.push(JSON.parse(JSON.stringify(schema)));
    if (undoStack.value.length > maxHistorySize) {
      undoStack.value.shift();
    }
    redoStack.value = [];  // 新操作清空重做栈
  }

  function undo(): FormSchema | null {
    if (!canUndo.value) return null;
    const state = undoStack.value.pop()!;
    redoStack.value.push(state);
    return undoStack.value[undoStack.value.length - 1] ?? null;
  }

  function redo(): FormSchema | null {
    if (!canRedo.value) return null;
    const state = redoStack.value.pop()!;
    undoStack.value.push(state);
    return state;
  }

  return { canUndo, canRedo, pushState, undo, redo };
});
```

### 5.3 Provide/Inject 上下文传递

```typescript
// types/designer-context.ts
import type { InjectionKey, Ref } from 'vue';
import type { DesignerState, FormSchema, WidgetConfig } from '@/types';

export interface DesignerContext {
  state: DesignerState;
  schema: Ref<FormSchema | null>;
  selectedWidget: Ref<WidgetConfig | null>;
  actions: {
    selectWidget: (id: string | null) => void;
    addWidget: (parentId: string | null, widget: WidgetConfig, index?: number) => void;
    removeWidget: (id: string) => void;
    updateWidgetProps: (id: string, props: Record<string, any>) => void;
    moveWidget: (fromId: string, toId: string | null, index: number) => void;
  };
}

export const DESIGNER_CONTEXT_KEY: InjectionKey<DesignerContext> = Symbol('designerContext');
```

---

## 6. 关键实现细节

### 6.1 组件自动化注册

```typescript
// composables/useAutoRegister.ts
export function useAutoRegister() {
  const widgetRegistry = inject(WIDGET_REGISTRY_KEY)!;

  const fieldModules = import.meta.glob('@/components/widgets/field/*.vue', { eager: true });
  const containerModules = import.meta.glob('@/components/widgets/container/*.vue', { eager: true });

  // 字段组件自动扫描
  for (const [path, module] of Object.entries(fieldModules)) {
    const fileName = path.split('/').pop()!.replace('.vue', '');
    const widgetName = `${fileName}Widget`;
    const definition = createWidgetDefinition(widgetName, 'field');
    widgetRegistry.register(definition, (module as any).default);
  }

  // 容器组件自动扫描
  for (const [path, module] of Object.entries(containerModules)) {
    const fileName = path.split('/').pop()!.replace('.vue', '');
    const widgetName = `${fileName}Widget`;
    const definition = createWidgetDefinition(widgetName, 'container');
    widgetRegistry.register(definition, (module as any).default);
  }
}
```

### 6.2 Schema验证

```typescript
// utils/schema-transformer.ts
import { widgetRegistry } from './widget-registry';
import type { FormSchema, WidgetConfig } from '@/types';

export function validateSchema(schema: FormSchema): { valid: boolean; errors: string[] } {
  const errors: string[] = [];

  if (!schema.id) errors.push('Schema缺少id');
  if (!schema.name) errors.push('Schema缺少name');
  if (!Array.isArray(schema.widgets)) errors.push('Schema缺少widgets数组');

  for (const widget of schema.widgets) {
    validateWidget(widget, errors);
  }

  return { valid: errors.length === 0, errors };
}

function validateWidget(widget: WidgetConfig, errors: string[]): void {
  const definition = widgetRegistry.getDefinition(widget.type);
  if (!definition) {
    errors.push(`未知组件类型: ${String(widget.type)}`);
    return;
  }

  // 验证必填属性
  for (const propSchema of definition.propsSchema) {
    if (propSchema.required && !(widget.props[propSchema.name])) {
      errors.push(`组件${widget.id}缺少必填属性: ${propSchema.name}`);
    }
  }

  // 递归验证子组件
  if (widget.children) {
    for (const child of widget.children) {
      validateWidget(child, errors);
    }
  }
}
```

### 6.3 拖拽处理

```typescript
// composables/useVueDraggable.ts
import { VueDraggable } from 'vue-draggable-plus';
import { useDesignerStore } from '@/stores/designerStore';

export function useVueDraggable(options: {
  group: string;
  widget: WidgetConfig;
  parentId: string | null;
}) {
  const designerStore = useDesignerStore();

  const draggableOptions = {
    group: options.group,
    animation: 200,
    ghostClass: 'ghost',
    chosenClass: 'chosen',
    handle: '.drag-handle',
    onEnd: (evt: any) => {
      if (evt.from !== evt.to || evt.oldIndex !== evt.newIndex) {
        designerStore.moveWidget(
          evt.item.dataset.widgetId,
          options.parentId,
          evt.newIndex
        );
      }
    },
  };

  return { draggableOptions };
}
```

---

## 7. 与原项目(vform3-pro)的关键差异

| 维度 | 原项目 | 新项目 |
|------|--------|--------|
| **组件标识** | 字符串类型 `'input'` | Symbol类型 `Symbol('INPUT')` |
| **状态管理** | 手动状态 + EventBus | Pinia store + actions |
| **组件注册** | 手动全局注册 | import.meta.glob自动扫描 |
| **API风格** | Options API | Composition API + setup |
| **上下文传递** | props层层传递 | provide/inject上下文 |
| **属性编辑** | 单一编辑器组件 | 工厂模式 + 类型化编辑器 |
| **样式方案** | SCSS全局导入 | SCSS局部 + CSS变量主题 |
| **拖拽实现** | vuedraggable | vue-draggable-plus |
| **事件通信** | Vue.prototype.$bus | Pinia actions |
| **类型安全** | Partial TypeScript | 完整类型推断 |

---

## 8. CSS变量主题系统

```scss
// styles/variables.scss
:root {
  // 主题色
  --primary-color: #18a058;
  --primary-color-hover: #36c77b;
  --primary-color-pressed: #0c7a43;

  // 表单尺寸
  --form-label-width: 120px;
  --form-widget-height: 34px;

  // 画布
  --canvas-background: #f5f5f5;
  --canvas-grid-size: 20px;

  // 边框
  --border-color: #d9d9d9;
  --border-radius: 4px;

  // 阴影
  --widget-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  --widget-shadow-hover: 0 4px 16px rgba(0, 0, 0, 0.15);
  --widget-shadow-selected: 0 0 0 2px var(--primary-color);

  // 过渡
  --transition-fast: 0.15s ease;
  --transition-normal: 0.25s ease;
}
```

---

## 9. 组件配置定义示例

```typescript
// components/widgets/field/InputWidget.vue
<script setup lang="ts">
import { computed, inject } from 'vue';
import { NInput } from 'naive-ui';
import { WIDGET_TYPE } from '@/types/widget-type';
import { useWidget } from '@/composables/useWidget';

const props = defineProps<{
  id: string;
  label: string;
  placeholder?: string;
  defaultValue?: string;
  disabled?: boolean;
  clearable?: boolean;
  maxlength?: number;
}>();

const { value, onUpdate } = useWidget(props.id);
</script>

<template>
  <n-form-item :label="label">
    <n-input
      v-model:value="value"
      :placeholder="placeholder"
      :disabled="disabled"
      :clearable="clearable"
      :maxlength="maxlength"
    />
  </n-form-item>
</template>

// 组件定义
export const InputWidgetDefinition = {
  type: WIDGET_TYPE.INPUT,
  name: 'InputWidget',
  label: '输入框',
  icon: 'edit',
  category: 'field',
  defaultProps: {
    placeholder: '请输入',
    defaultValue: '',
    disabled: false,
    clearable: true,
    maxlength: undefined,
  },
  propsSchema: [
    { name: 'label', label: '标签', type: 'string', required: true },
    { name: 'placeholder', label: '占位符', type: 'string' },
    { name: 'defaultValue', label: '默认值', type: 'string' },
    { name: 'disabled', label: '禁用', type: 'boolean' },
    { name: 'clearable', label: '可清空', type: 'boolean' },
    { name: 'maxlength', label: '最大长度', type: 'number' },
  ],
};
