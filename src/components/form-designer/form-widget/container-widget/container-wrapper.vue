<template>
  <div
    class="container-wrapper"
    :class="[widget.options.customClass, { 'selected': isSelected }]"
    @click.stop="selectWidget"
  >
    <!-- Grid Container -->
    <template v-if="widget.type === 'grid'">
      <div class="grid-container" :style="{gap: widget.options.gutter + 'px'}">
        <div
          v-for="(col, colIndex) in widget.cols"
          :key="col.id"
          class="grid-col"
          :style="{width: (col.options.span / 24 * 100) + '%'}"
        >
          <draggable
            :list="col.widgetList"
            item-key="id"
            group="dragGroup"
            ghost-class="ghost"
            @end="onDragEnd"
          >
            <template #item="{ element, index }">
              <FieldWrapper
                v-if="!element.category"
                :field="element"
                :parent-list="col.widgetList"
                :index-of-parent-list="index"
                :parent-widget="col"
                :designer="designer"
              />
              <ContainerWrapper
                v-else
                :widget="element"
                :parent-list="col.widgetList"
                :index-of-parent-list="index"
                :parent-widget="col"
                :designer="designer"
              />
            </template>
          </draggable>
        </div>
      </div>
    </template>

    <!-- Tab Container -->
    <template v-else-if="widget.type === 'tab'">
      <el-tabs v-model="activeTab" @tab-click="onTabClick">
        <el-tab-pane
          v-for="(tab, tabIndex) in widget.tabs"
          :key="tab.id"
          :label="tab.options.label"
          :name="tab.options.name"
        >
          <draggable
            :list="tab.widgetList"
            item-key="id"
            group="dragGroup"
            ghost-class="ghost"
            @end="onDragEnd"
          >
            <template #item="{ element, index }">
              <FieldWrapper
                v-if="!element.category"
                :field="element"
                :parent-list="tab.widgetList"
                :index-of-parent-list="index"
                :parent-widget="tab"
                :designer="designer"
              />
              <ContainerWrapper
                v-else
                :widget="element"
                :parent-list="tab.widgetList"
                :index-of-parent-list="index"
                :parent-widget="tab"
                :designer="designer"
              />
            </template>
          </draggable>
        </el-tab-pane>
      </el-tabs>
    </template>

    <!-- SubForm Container -->
    <template v-else-if="widget.type === 'sub-form'">
      <div class="sub-form-container">
        <div class="sub-form-header">{{ widget.options.label }}</div>
        <draggable
          :list="widget.widgetList"
          item-key="id"
          group="dragGroup"
          ghost-class="ghost"
          @end="onDragEnd"
        >
          <template #item="{ element, index }">
            <FieldWrapper
              v-if="!element.category"
              :field="element"
              :parent-list="widget.widgetList"
              :index-of-parent-list="index"
              :parent-widget="widget"
              :designer="designer"
            />
          </template>
        </draggable>
      </div>
    </template>

    <!-- Table Container -->
    <template v-else-if="widget.type === 'table'">
      <div class="table-container">
        <table>
          <tbody>
            <tr v-for="(row, rowIndex) in widget.options.rows" :key="row.id">
              <td
                v-for="(cell, cellIndex) in row.cols"
                :key="cell.id"
                :colspan="cell.options.colspan"
                :rowspan="cell.options.rowspan"
                class="table-cell"
              >
                <draggable
                  v-if="!cell.merged"
                  :list="cell.widgetList"
                  item-key="id"
                  group="dragGroup"
                  ghost-class="ghost"
                  @end="onDragEnd"
                >
                  <template #item="{ element, index }">
                    <FieldWrapper
                      v-if="!element.category"
                      :field="element"
                      :parent-list="cell.widgetList"
                      :index-of-parent-list="index"
                      :parent-widget="cell"
                      :designer="designer"
                    />
                  </template>
                </draggable>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>

    <!-- Default Container -->
    <template v-else>
      <draggable
        :list="widget.widgetList"
        item-key="id"
        group="dragGroup"
        ghost-class="ghost"
        @end="onDragEnd"
      >
        <template #item="{ element, index }">
          <FieldWrapper
            v-if="!element.category"
            :field="element"
            :parent-list="widget.widgetList"
            :index-of-parent-list="index"
            :parent-widget="widget"
            :designer="designer"
          />
          <ContainerWrapper
            v-else
            :widget="element"
            :parent-list="widget.widgetList"
            :index-of-parent-list="index"
            :parent-widget="widget"
            :designer="designer"
          />
        </template>
      </draggable>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import draggable from 'vuedraggable'
import FieldWrapper from '../field-widget/field-wrapper.vue'
import ContainerWrapper from './container-wrapper.vue'
import eventBus from '@/utils/event-bus'

const props = defineProps<{
  widget: any
  parentList: any[]
  indexOfParentList: number
  parentWidget: any
  designer: any
}>()

const activeTab = ref('')

const isSelected = computed(() => props.designer.selectedId === props.widget.id)

function selectWidget() {
  props.designer.setSelected(props.widget)
  eventBus.emit('widget-selected', props.widget)
}

function onDragEnd() {
  props.designer.emitHistoryChange()
}

watch(() => props.widget.tabs, (tabs) => {
  if (tabs && tabs.length > 0) {
    const activeTabPane = tabs.find(t => t.options.active)
    activeTab.value = activeTabPane ? activeTabPane.options.name : tabs[0].options.name
  }
}, { immediate: true })

function onTabClick(tab: any) {
  if (props.widget.tabs) {
    props.widget.tabs.forEach((t: any) => {
      t.options.active = t.options.name === tab.props.name
    })
  }
}
</script>

<style lang="scss" scoped>
.container-wrapper {
  position: relative;
  min-height: 60px;
  padding: 4px;
  border: 1px dashed #dcdfe6;
  border-radius: 4px;
  margin-bottom: 4px;
  transition: border-color 0.2s;

  &:hover {
    border-color: #667eea;
  }

  &.selected {
    border-color: #667eea;
    border-style: solid;
    background: rgba(102, 126, 234, 0.05);
  }
}

.grid-container {
  display: flex;
  flex-wrap: wrap;

  .grid-col {
    min-height: 60px;
    padding: 4px;
    box-sizing: border-box;
  }
}

.sub-form-container {
  .sub-form-header {
    font-weight: bold;
    margin-bottom: 8px;
    padding: 4px 0;
    border-bottom: 1px solid #dcdfe6;
  }
}

.table-container {
  table {
    width: 100%;
    border-collapse: collapse;

    td.table-cell {
      border: 1px dashed #dcdfe6;
      padding: 8px;
      min-width: 100px;
      min-height: 60px;
      vertical-align: top;
    }
  }
}

.ghost {
  opacity: 0.5;
  background: #667eea;
}
</style>
