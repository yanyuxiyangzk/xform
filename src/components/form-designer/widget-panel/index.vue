<template>
  <el-container class="panel-container">
    <el-tabs v-model="activeTab" style="height: 100%; width: 100%; overflow: hidden">
      <el-tab-pane :label="i18nText('designer.hint.widgetSetting')" name="1">
        <el-scrollbar class="setting-scrollbar" :style="{height: scrollerHeight}">
          <el-collapse v-model="activeNames" class="widget-collapse">
            <el-collapse-item name="1" :title="i18nText('designer.containerTitle')">
              <draggable
                tag="ul"
                :list="containers"
                item-key="key"
                :group="{name: 'dragGroup', pull: 'clone', put: false}"
                :clone="handleWidgetClone"
                ghost-class="ghost"
                :sort="false"
                @end="onContainerDragEnd"
              >
                <template #item="{ element: ctn }">
                  <li class="widget-item" :title="ctn.displayName" @dblclick="addContainerByDbClick(ctn)">
                    <span>{{ i18nWidget(ctn.type) }}</span>
                  </li>
                </template>
              </draggable>
            </el-collapse-item>

            <el-collapse-item name="2" :title="i18nText('designer.basicFieldTitle')">
              <draggable
                tag="ul"
                :list="basicFields"
                item-key="key"
                :group="{name: 'dragGroup', pull: 'clone', put: false}"
                :clone="handleWidgetClone"
                ghost-class="ghost"
                :sort="false"
              >
                <template #item="{ element: fld }">
                  <li class="widget-item" :title="fld.displayName" @dblclick="addFieldByDbClick(fld)">
                    <span>{{ i18nWidget(fld.type) }}</span>
                  </li>
                </template>
              </draggable>
            </el-collapse-item>

            <el-collapse-item name="3" :title="i18nText('designer.advancedFieldTitle')">
              <draggable
                tag="ul"
                :list="advancedFields"
                item-key="key"
                :group="{name: 'dragGroup', pull: 'clone', put: false}"
                :clone="handleWidgetClone"
                ghost-class="ghost"
                :sort="false"
              >
                <template #item="{ element: fld }">
                  <li class="widget-item" :title="fld.displayName" @dblclick="addFieldByDbClick(fld)">
                    <span>{{ i18nWidget(fld.type) }}</span>
                  </li>
                </template>
              </draggable>
            </el-collapse-item>
          </el-collapse>
        </el-scrollbar>
      </el-tab-pane>

      <el-tab-pane :label="i18nText('designer.market.title')" name="2">
        <MarketPanel :designer="designer" />
      </el-tab-pane>

      <el-tab-pane :label="i18nText('designer.template.title')" name="3">
        <TemplatePanel :designer="designer" />
      </el-tab-pane>
    </el-tabs>
  </el-container>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, inject } from 'vue'
import draggable from 'vuedraggable'
import { containers as CONS, basicFields as BFS, advancedFields as AFS } from './widgetsConfig'
import { generateId } from '@/utils/util'
import MarketPanel from './market-panel.vue'
import TemplatePanel from './template-panel.vue'

const props = defineProps<{
  designer: any
}>()

const activeTab = ref('1')
const scrollerHeight = ref('0')
const activeNames = ref(['1', '2', '3'])
const containers = ref<any[]>([])
const basicFields = ref<any[]>([])
const advancedFields = ref<any[]>([])

function i18nText(key: string): string {
  const map: Record<string, string> = {
    'designer.hint.widgetSetting': '组件配置',
    'designer.market.title': '组件市场',
    'designer.template.title': '表单模板',
    'designer.containerTitle': '容器组件',
    'designer.basicFieldTitle': '基础字段',
    'designer.advancedFieldTitle': '高级字段',
  }
  return map[key] || key
}

function i18nWidget(type: string): string {
  const map: Record<string, string> = {
    'grid': '栅格',
    'table': '表格',
    'tab': '标签页',
    'sub-form': '子表单',
    'input': '输入框',
    'textarea': '文本域',
    'number': '数字',
    'select': '下拉选择',
    'radio': '单选',
    'checkbox': '多选',
    'date': '日期',
    'time': '时间',
    'switch': '开关',
    'slider': '滑块',
    'rate': '评分',
    'cascader': '级联',
    'color': '颜色',
    'button': '按钮',
    'divider': '分割线',
    'static-text': '静态文本',
    'html-text': 'HTML',
    'picture-upload': '图片上传',
    'file-upload': '文件上传',
    'rich-editor': '富文本',
    'slot': '插槽',
  }
  return map[type] || type
}

function loadWidgets() {
  containers.value = CONS.map(con => ({
    key: generateId(),
    ...con,
    displayName: i18nWidget(con.type),
  }))

  basicFields.value = BFS.map(fld => ({
    key: generateId(),
    ...fld,
    displayName: i18nWidget(fld.type),
  }))

  advancedFields.value = AFS.map(fld => ({
    key: generateId(),
    ...fld,
    displayName: i18nWidget(fld.type),
  }))
}

function handleWidgetClone(origin: any) {
  if (origin.category === 'container') {
    return props.designer.copyNewContainerWidget(origin)
  }
  return props.designer.copyNewFieldWidget(origin)
}

function onContainerDragEnd() {
  // console.log('Drag end')
}

function addContainerByDbClick(container: any) {
  props.designer.addContainerByDbClick(container)
}

function addFieldByDbClick(widget: any) {
  props.designer.addFieldByDbClick(widget)
}

onMounted(() => {
  loadWidgets()
  scrollerHeight.value = window.innerHeight - 56 + 'px'
})
</script>

<style lang="scss" scoped>
.panel-container {
  padding: 0;
}

.setting-scrollbar {
  :deep(.el-scrollbar__wrap) {
    overflow-x: hidden;
  }
}

.widget-collapse {
  border-top-width: 0;

  :deep(.el-collapse-item__header) {
    margin-left: 8px;
    font-style: italic;
    font-weight: bold;
  }

  :deep(.el-collapse-item__content) {
    padding-bottom: 6px;

    ul {
      padding-left: 10px;
      margin: 0;
      padding-inline-start: 10px;

      &:after {
        content: '';
        display: block;
        clear: both;
      }

      li.widget-item {
        display: inline-block;
        height: 28px;
        line-height: 28px;
        width: 115px;
        float: left;
        margin: 2px 6px 6px 0;
        cursor: move;
        white-space: nowrap;
        text-overflow: ellipsis;
        overflow: hidden;
        background: #f1f2f3;
        padding: 0 8px;

        &:hover {
          background: #EBEEF5;
          outline: 1px solid #667eea;
        }
      }
    }
  }
}

.ghost {
  opacity: 0.5;
  background: #667eea;
}
</style>
