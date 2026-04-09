<template>
  <div class="market-panel">
    <div class="search-bar">
      <el-input
        v-model="searchKeyword"
        :placeholder="i18nText('designer.market.searchPlaceholder')"
        prefix-icon="Search"
        clearable
      />
    </div>

    <el-scrollbar :style="{height: scrollHeight}">
      <div class="market-categories">
        <div
          v-for="category in filteredCategories"
          :key="category.id"
          class="market-category"
        >
          <h3 class="category-title">{{ category.name }}</h3>
          <div class="market-items">
            <div
              v-for="item in category.items"
              :key="item.id"
              class="market-item"
              @click="previewItem(item)"
            >
              <div class="item-icon">{{ item.icon }}</div>
              <div class="item-info">
                <span class="item-name">{{ item.name }}</span>
                <span class="item-desc">{{ item.description }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-scrollbar>

    <!-- Preview Dialog -->
    <el-dialog
      v-model="showPreview"
      :title="previewData?.name"
      width="70%"
      destroy-on-close
    >
      <div v-if="previewData" class="preview-content">
        <div class="preview-widgets">
          <div
            v-for="(widget, idx) in previewData.widgets"
            :key="idx"
            class="preview-widget-item"
          >
            <span class="widget-type">{{ widget.type }}</span>
            <span class="widget-label">{{ widget.options?.label }}</span>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="showPreview = false">{{ i18nText('designer.hint.cancel') }}</el-button>
        <el-button type="primary" @click="addToCanvas">{{ i18nText('designer.market.addToCanvas') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { generateId } from '@/utils/util'

const props = defineProps<{
  designer: any
}>()

const searchKeyword = ref('')
const showPreview = ref(false)
const previewData = ref<any>(null)

const scrollHeight = ref('calc(100vh - 120px)')

// 市场数据分类
const marketCategories = ref([
  {
    id: 'layout',
    name: '布局组件',
    items: [
      {
        id: 'layout-form',
        name: '基础表单布局',
        icon: '📋',
        description: '包含输入框、下拉、按钮的标准表单布局',
        widgets: [
          { type: 'input', options: { name: 'field1', label: '字段1', placeholder: '请输入' } },
          { type: 'select', options: { name: 'field2', label: '字段2', optionItems: [{ label: '选项1', value: '1' }, { label: '选项2', value: '2' }] } },
          { type: 'button', options: { name: 'submitBtn', label: '提交', labelHidden: true } }
        ]
      },
      {
        id: 'layout-two-col',
        name: '双列布局',
        icon: '📱',
        description: '左右双列的响应式布局',
        widgets: [
          { type: 'grid', category: 'container', cols: [
            { type: 'grid-col', options: { name: 'col1', span: 12 }, widgetList: [
              { type: 'input', options: { name: 'leftField', label: '左侧字段' } }
            ]},
            { type: 'grid-col', options: { name: 'col2', span: 12 }, widgetList: [
              { type: 'input', options: { name: 'rightField', label: '右侧字段' } }
            ]}
          ]}
        ]
      },
      {
        id: 'layout-tabs',
        name: '标签页布局',
        icon: '📑',
        description: '多标签页切换的内容布局',
        widgets: [
          { type: 'tab', category: 'container', tabs: [
            { options: { name: 'tab1', label: '标签1', active: true }, widgetList: [] },
            { options: { name: 'tab2', label: '标签2', active: false }, widgetList: [] }
          ]}
        ]
      }
    ]
  },
  {
    id: 'input',
    name: '输入组件组',
    items: [
      {
        id: 'input-group-text',
        name: '文本输入组',
        icon: '✏️',
        description: '多种文本输入组件组合',
        widgets: [
          { type: 'input', options: { name: 'username', label: '用户名', placeholder: '请输入用户名' } },
          { type: 'input', options: { name: 'email', label: '邮箱', placeholder: '请输入邮箱' } },
          { type: 'textarea', options: { name: 'remark', label: '备注', placeholder: '请输入备注' } }
        ]
      },
      {
        id: 'input-group-number',
        name: '数字输入组',
        icon: '🔢',
        description: '数字和范围输入组件组合',
        widgets: [
          { type: 'number', options: { name: 'age', label: '年龄', min: 0, max: 150 } },
          { type: 'slider', options: { name: 'score', label: '评分', min: 0, max: 100 } }
        ]
      }
    ]
  },
  {
    id: 'select',
    name: '选择组件组',
    items: [
      {
        id: 'select-group',
        name: '选择器组合',
        icon: '📝',
        description: '单选、多选、级联选择组合',
        widgets: [
          { type: 'radio', options: { name: 'gender', label: '性别', optionItems: [{ label: '男', value: 'male' }, { label: '女', value: 'female' }] } },
          { type: 'checkbox', options: { name: 'hobby', label: '爱好', optionItems: [{ label: '阅读', value: 'read' }, { label: '运动', value: 'sport' }] } },
          { type: 'select', options: { name: 'city', label: '城市', optionItems: [{ label: '北京', value: 'bj' }, { label: '上海', value: 'sh' }] } }
        ]
      }
    ]
  },
  {
    id: 'datetime',
    name: '日期时间组件组',
    items: [
      {
        id: 'datetime-group',
        name: '日期时间组合',
        icon: '📅',
        description: '日期、时间、日期时间选择器',
        widgets: [
          { type: 'date', options: { name: 'startDate', label: '开始日期', dateType: 'date' } },
          { type: 'time', options: { name: 'startTime', label: '开始时间' } },
          { type: 'date', options: { name: 'endDate', label: '结束日期', dateType: 'datetime' } }
        ]
      }
    ]
  },
  {
    id: 'advanced',
    name: '高级组件组',
    items: [
      {
        id: 'upload-group',
        name: '上传组件组合',
        icon: '📤',
        description: '图片、文件上传组件',
        widgets: [
          { type: 'picture-upload', options: { name: 'avatar', label: '头像上传' } },
          { type: 'file-upload', options: { name: 'attachments', label: '附件上传' } }
        ]
      },
      {
        id: 'rich-editor-group',
        name: '富文本编辑组',
        icon: '📰',
        description: '富文本编辑器',
        widgets: [
          { type: 'rich-editor', options: { name: 'content', label: '内容', minHeight: '200px' } }
        ]
      }
    ]
  }
])

const filteredCategories = computed(() => {
  if (!searchKeyword.value) {
    return marketCategories.value
  }
  const keyword = searchKeyword.value.toLowerCase()
  return marketCategories.value
    .map(cat => ({
      ...cat,
      items: cat.items.filter(item =>
        item.name.toLowerCase().includes(keyword) ||
        item.description.toLowerCase().includes(keyword)
      )
    }))
    .filter(cat => cat.items.length > 0)
})

function i18nText(key: string): string {
  const map: Record<string, string> = {
    'designer.market.searchPlaceholder': '搜索组件...',
    'designer.market.addToCanvas': '添加到画布',
    'designer.hint.cancel': '取消'
  }
  return map[key] || key
}

function previewItem(item: any) {
  previewData.value = item
  showPreview.value = true
}

function addToCanvas() {
  if (!previewData.value || !previewData.value.widgets) {
    showPreview.value = false
    return
  }

  previewData.value.widgets.forEach((widget: any) => {
    const newWidget = generateWidget(widget)
    props.designer.widgetList.push(newWidget)
    props.designer.setSelected(newWidget)
  })

  props.designer.emitHistoryChange()
  showPreview.value = false
}

function generateWidget(origin: any): any {
  const tempId = generateId()
  const baseWidget = {
    ...origin,
    id: (origin.type || '').replace(/-/g, '') + tempId,
    key: tempId,
    options: {
      ...origin.options,
      name: origin.options?.name || (origin.type || '') + tempId
    }
  }

  // 处理容器组件
  if (origin.category === 'container') {
    if (origin.type === 'grid' && origin.cols) {
      baseWidget.cols = origin.cols.map((col: any) => ({
        ...col,
        id: 'grid-col-' + generateId(),
        widgetList: (col.widgetList || []).map((w: any) => generateWidget(w))
      }))
    }
    if (origin.type === 'tab' && origin.tabs) {
      baseWidget.tabs = origin.tabs.map((tab: any) => ({
        ...tab,
        id: 'tab-pane-' + generateId(),
        widgetList: (tab.widgetList || []).map((w: any) => generateWidget(w))
      }))
    }
  }

  delete baseWidget.displayName
  return baseWidget
}
</script>

<style lang="scss" scoped>
.market-panel {
  height: 100%;
  display: flex;
  flex-direction: column;

  .search-bar {
    padding: 8px;
    border-bottom: 1px solid #EBEEF5;
  }
}

.market-categories {
  padding: 8px;

  .market-category {
    margin-bottom: 16px;

    .category-title {
      font-size: 13px;
      color: #909399;
      margin: 0 0 8px 4px;
      font-weight: normal;
    }

    .market-items {
      display: flex;
      flex-direction: column;
      gap: 6px;

      .market-item {
        display: flex;
        align-items: center;
        padding: 10px 12px;
        background: #f5f7fa;
        border-radius: 6px;
        cursor: pointer;
        transition: all 0.2s;

        &:hover {
          background: #EBEEF5;
          transform: translateX(2px);
        }

        .item-icon {
          font-size: 20px;
          margin-right: 10px;
        }

        .item-info {
          display: flex;
          flex-direction: column;

          .item-name {
            font-size: 13px;
            color: #303133;
            font-weight: 500;
          }

          .item-desc {
            font-size: 11px;
            color: #909399;
            margin-top: 2px;
          }
        }
      }
    }
  }
}

.preview-content {
  .preview-widgets {
    display: flex;
    flex-direction: column;
    gap: 8px;

    .preview-widget-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 8px 12px;
      background: #f5f7fa;
      border-radius: 4px;

      .widget-type {
        background: #667eea;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 12px;
      }

      .widget-label {
        color: #606266;
        font-size: 13px;
      }
    }
  }
}
</style>
