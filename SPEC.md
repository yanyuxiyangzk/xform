# XForm - Low-Code Form Designer

## 1. Project Overview

**Project Name:** XForm
**Version:** 1.0.0
**Type:** Vue 3 Low-Code Form Designer

XForm is a professional low-code form design tool that enables developers to create forms through drag-and-drop interface without writing code. It provides real-time preview, JSON export, and code generation capabilities.

## 2. Core Features

| Feature | Description |
|---------|-------------|
| Drag-Drop Design | Visual drag-and-drop form building |
| 20+ Field Types | Input, Select, Date, Upload, etc. |
| Container Components | Grid, Table, Tabs, SubForm |
| Property Panel | Real-time component configuration |
| JSON Export | Export form as JSON schema |
| Code Export | Generate Vue/HTML code |
| Internationalization | Chinese/English support |
| Layout Support | PC / Pad / H5 responsive |

## 3. Technical Stack

| Layer | Technology | Version |
|-------|------------|---------|
| Framework | Vue 3 | 3.2.26+ |
| UI Library | Element Plus | 2.2.2+ |
| Build Tool | Vite | 2.7.3+ |
| Language | TypeScript | 4.7.4+ |
| Styling | Sass | 1.45.0+ |
| State | mitt (Event Bus) | 3.0.0+ |
| Drag-Drop | SortableJS | 1.14.0+ |

## 4. Project Structure

```
xform/
├── src/
│   ├── components/
│   │   ├── form-designer/      # Form Designer Module
│   │   │   ├── designer.js     # Designer state management
│   │   │   ├── index.vue       # Designer entry
│   │   │   ├── form-widget/    # Canvas widget rendering
│   │   │   ├── widget-panel/   # Left component panel
│   │   │   ├── setting-panel/  # Right property panel
│   │   │   └── toolbar-panel/  # Top toolbar
│   │   ├── form-render/        # Form Renderer Module
│   │   │   ├── index.vue       # Renderer entry
│   │   │   └── container-item/ # Container components
│   │   └── code-editor/        # Ace code editor
│   ├── utils/                  # Utility functions
│   ├── lang/                   # i18n language files
│   ├── stores/                 # Pinia stores
│   ├── types/                  # TypeScript types
│   ├── styles/                 # Global styles
│   ├── App.vue                 # Root component
│   └── main.ts                 # Entry file
├── package.json
├── vite.config.ts
├── tsconfig.json
└── index.html
```

## 5. Module Architecture

### 5.1 Form Designer
- **widget-panel**: Displays available components, supports drag to canvas
- **toolbar-panel**: Undo/redo, preview, import/export actions
- **setting-panel**: Component property configuration
- **form-widget**: Canvas rendering of form structure

### 5.2 Form Renderer
- Parses formJson and recursively renders components
- Supports data binding and validation
- Event handling and dynamic updates

## 6. Data Model

### 6.1 Form JSON Structure
```json
{
  "widgetList": [...],
  "formConfig": {
    "modelName": "formData",
    "refName": "xForm",
    "labelWidth": 80,
    "labelPosition": "left",
    "layoutType": "PC",
    "jsonVersion": 3
  }
}
```

### 6.2 Widget Structure
```json
{
  "type": "input",
  "icon": "text-field",
  "category": "field",
  "formItemFlag": true,
  "options": {
    "name": "field1",
    "label": "Username",
    "placeholder": "Enter username",
    "disabled": false,
    "hidden": false,
    "required": false
  }
}
```

## 7. UI Theme

### Color Palette
- Primary: #409EFF (Blue)
- Success: #67C23A (Green)
- Warning: #E6A23C (Orange)
- Danger: #F56C6C (Red)
- Info: #909399 (Gray)

### Layout
- Left Panel: 260px (Widget Panel)
- Center: Flexible (Form Canvas)
- Right Panel: 300px (Property Panel)
- Header: 48px (Toolbar)
- Logo Header: 48px (Optional)

## 8. Internationalization

Supported Languages:
- zh-CN: Chinese (Simplified)
- en-US: English

## 9. Export Formats

1. **JSON**: Form configuration schema
2. **Vue Code**: Vue 2/3 component code
3. **HTML Code**: Standalone HTML file

## 10. Component Categories

### Containers
- Grid (24-column grid layout)
- Table (Spreadsheet-like layout)
- Tabs (Tab navigation)
- SubForm (Repeatable form rows)

### Basic Fields
- Input (Text, Number, Password)
- Textarea
- Select / Multiple Select
- Radio / Checkbox
- Date / DateRange
- Time / TimeRange
- Switch
- Slider
- Rate
- Cascader
- Color Picker

### Advanced Fields
- Rich Text Editor
- File Upload
- Image Upload
- Button
- Divider
- Static Text
- HTML Content
- Slot

## 11. Version

- JSON Schema Version: 3
- Project Version: 1.0.0
