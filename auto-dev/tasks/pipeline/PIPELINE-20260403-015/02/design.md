# 技术方案：零代码微服务平台核心模块

> 文档编号：DESIGN-20260403-015
> 流水线：PIPELINE-20260403-015
> 版本：v1.0
> 日期：2026-04-03

---

## 1. 总体架构

### 1.1 模块划分

```
ruoyi-nocode/
├── ruoyi-nocode-form/         # 表单设计模块
│   ├── form-core/             # 核心组件
│   ├── form-designer/         # 设计器
│   └── form-renderer/         # 渲染器
├── ruoyi-nocode-workflow/     # 流程引擎模块
│   ├── workflow-core/        # 核心引擎
│   ├── workflow-designer/     # 设计器
│   └── workflow-engine/       # 执行引擎
└── ruoyi-nocode-generator/    # 代码生成模块
    ├── generator-core/        # 核心生成器
    ├── templates/             # 代码模板
    └── output/                # 输出目录
```

---

## 2. 表单设计器

### 2.1 数据模型

```java
// 表单配置
public class FormConfig {
    private String id;
    private String name;
    private String description;
    private List<FormComponent> components;
    private List<FormSection> sections;
    private Date created;
    private Date updated;
}

// 表单组件
public class FormComponent {
    private String id;
    private String type;          // text, number, select, date, switch, textarea
    private String label;
    private String placeholder;
    private String defaultValue;
    private Boolean required;
    private Map<String, Object> props;  // 组件特有属性
    private Integer sort;
}

// 组件类型定义
public enum ComponentType {
    TEXT("文本输入"),
    NUMBER("数字输入"),
    SELECT("下拉选择"),
    DATE("日期选择"),
    SWITCH("开关"),
    TEXTAREA("多行文本"),
    CHECKBOX("复选框"),
    RADIO("单选框");
}
```

### 2.2 API设计

| 接口 | 方法 | 路径 | 描述 |
|------|------|------|------|
| 创建表单 | POST | /api/form | 创建表单 |
| 获取表单 | GET | /api/form/{id} | 获取表单详情 |
| 更新表单 | PUT | /api/form/{id} | 更新表单 |
| 删除表单 | DELETE | /api/form/{id} | 删除表单 |
| 列表查询 | GET | /api/form/list | 列表查询 |
| 发布表单 | POST | /api/form/{id}/publish | 发布表单 |

### 2.3 前端结构

```typescript
// 表单设计器状态
interface FormDesignerState {
  components: FormComponent[];    // 组件列表
  selectedId: string;             // 选中组件ID
  formConfig: FormConfig;         // 表单配置
  previewMode: boolean;           // 预览模式
}

// 组件定义
interface ComponentDefinition {
  type: ComponentType;
  label: string;
  icon: string;
  defaultProps: Record<string, any>;
  propSchema: PropSchema[];        // 属性配置
}
```

---

## 3. 流程引擎

### 3.1 数据模型

```java
// 流程定义
public class WorkflowDefinition {
    private String id;
    private String name;
    private String description;
    private String processKey;          // 流程标识
    private Integer version;
    private String diagram;            // 流程图JSON
    private List<NodeDefinition> nodes;
    private List<SequenceFlow> flows;
    private Boolean suspended;
    private Date created;
}

// 节点定义
public class NodeDefinition {
    private String id;
    private String name;
    private NodeType type;             // START, USER_TASK, END
    private Integer x;                // 坐标
    private Integer y;
    private Map<String, Object> props; // 节点属性
}

// 流程实例
public class WorkflowInstance {
    private String id;
    private String definitionId;
    private String businessKey;       // 关联业务ID
    private InstanceStatus status;     // RUNNING, COMPLETED, CANCELLED
    private String currentNodeId;
    private List<HistoryRecord> history;
}
```

### 3.2 API设计

| 接口 | 方法 | 路径 | 描述 |
|------|------|------|------|
| 创建流程 | POST | /api/workflow/definition | 创建流程定义 |
| 部署流程 | POST | /api/workflow/definition/{id}/deploy | 部署流程 |
| 启动流程 | POST | /api/workflow/instance | 启动流程实例 |
| 查询实例 | GET | /api/workflow/instance/{id} | 查询实例 |
| 审批任务 | POST | /api/workflow/task/{id}/complete | 完成审批任务 |
| 获取我的任务 | GET | /api/workflow/tasks/my | 获取我的待办任务 |

### 3.3 流程图存储格式

```json
{
  "nodes": [
    {"id": "start", "type": "START", "name": "开始", "x": 100, "y": 200},
    {"id": "task1", "type": "USER_TASK", "name": "审批", "x": 300, "y": 200, "props": {"assignee": "${applicant}"}},
    {"id": "end", "type": "END", "name": "结束", "x": 500, "y": 200}
  ],
  "flows": [
    {"id": "f1", "source": "start", "target": "task1"},
    {"id": "f2", "source": "task1", "target": "end"}
  ]
}
```

---

## 4. 代码生成器

### 4.1 代码生成流程

```
表单配置 → 配置解析 → 模板选择 → 代码渲染 → 输出文件
```

### 4.2 支持的模板

| 模板 | 输出文件 |
|------|---------|
| Entity.java | 实体类 |
| Mapper.java | Mapper接口 |
| Mapper.xml | MyBatis XML |
| Service.java | 服务接口 |
| ServiceImpl.java | 服务实现 |
| Controller.java | 控制器 |
| VueList.vue | 列表页面 |
| VueForm.vue | 表单页面 |
| Api.js | 前端API |

### 4.3 代码模板示例

```java
// Entity模板
package ${package}.entity;

public class ${entityName} {
    #foreach($field in $fields)
    private ${field.javaType} ${field.name};
    #end
}
```

### 4.4 API设计

| 接口 | 方法 | 路径 | 描述 |
|------|------|------|------|
| 生成代码 | POST | /api/generator/generate | 生成代码 |
| 预览代码 | GET | /api/generator/preview/{tableId} | 预览代码 |
| 下载代码 | GET | /api/generator/download/{tableId} | 下载代码包 |
| 执行SQL | POST | /api/generator/execute | 执行生成SQL |

---

## 5. 关键技术

### 5.1 前端拖拽实现
使用 Vue3 + Element Plus + vuedraggable 实现拖拽功能。

### 5.2 流程引擎实现
使用状态机模式实现流程流转：
- 每个节点作为一个状态
- 流转条件作为状态转换规则
- 使用Liquor动态编译执行条件表达式

### 5.3 代码生成实现
使用 FreeMarker 模板引擎：
- 预定义代码模板
- 动态解析表单配置
- Liquor编译生成SQL

---

## 6. 实施计划

### Week 1: 表单设计器
- Day 1-2: 数据模型和API
- Day 3-4: 前端设计器开发
- Day 5: 预览和发布功能

### Week 2: 流程引擎
- Day 1-2: 数据模型和API
- Day 3-4: 流程设计器开发
- Day 5: 流程执行

### Week 3: 代码生成器
- Day 1-2: 模板开发
- Day 3-4: 生成器核心
- Day 5: 一键部署

---

最后更新：2026-04-03
