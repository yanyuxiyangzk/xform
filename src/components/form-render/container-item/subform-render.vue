<template>
  <div class="subform-render" :class="widget.options.customClass">
    <div class="subform-header" v-if="widget.options.label">
      <span class="subform-title">{{ widget.options.label }}</span>
    </div>

    <div class="subform-content">
      <div v-if="!subFormData || subFormData.length === 0" class="empty-subform">
        {{ emptyText }}
      </div>

      <template v-else>
        <div v-for="(row, rowIndex) in subFormData" :key="rowIndex" class="subform-row">
          <div class="row-number" v-if="widget.options.showRowNumber">{{ rowIndex + 1 }}</div>
          <template v-for="(child, index) in widget.widgetList" :key="child.id">
            <field-renderer
              v-if="child.formItemFlag"
              :field="child"
              :form-model="row"
              :parent-list="subFormData"
              :index-of-parent-list="rowIndex"
              :parent-widget="widget"
              :sub-form-name="widget.options.name"
              :sub-form-row-index="rowIndex"
            />
          </template>
          <div class="row-actions" v-if="!readonly">
            <el-button size="small" link type="danger" @click="deleteRow(rowIndex)">
              {{ deleteText }}
            </el-button>
          </div>
        </div>
      </template>

      <div v-if="!readonly && widget.options.showBlankRow" class="subform-actions">
        <el-button size="small" type="primary" plain @click="addRow">
          {{ addText }}
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, inject } from 'vue'
import { deepClone } from '@/utils/util'
import FieldRenderer from '../field-renderer.vue'

const props = defineProps<{
  widget: any
  formModel: Record<string, any>
}>()

const readonly = inject('getReadMode', () => false)

const subFormData = computed(() => {
  const name = props.widget.options.name
  return props.formModel[name] || []
})

const emptyText = '暂无数据'
const addText = '添加'
const deleteText = '删除'

function addRow() {
  const name = props.widget.options.name
  const newRow: Record<string, any> = {}
  props.widget.widgetList?.forEach((item: any) => {
    if (item.formItemFlag) {
      newRow[item.options.name] = deepClone(item.options.defaultValue)
    }
  })
  if (!props.formModel[name]) {
    props.formModel[name] = []
  }
  props.formModel[name].push(newRow)
}

function deleteRow(index: number) {
  const name = props.widget.options.name
  if (props.formModel[name] && props.formModel[name].length > index) {
    props.formModel[name].splice(index, 1)
  }
}
</script>

<style lang="scss" scoped>
.subform-render {
  .subform-header {
    margin-bottom: 12px;
    font-weight: 500;
    font-size: 14px;
  }

  .subform-content {
    border: 1px solid #dcdfe6;
    border-radius: 4px;
    padding: 12px;
    background: #fafafa;
  }

  .empty-subform {
    text-align: center;
    color: #909399;
    padding: 30px 0;
  }

  .subform-row {
    display: flex;
    align-items: flex-start;
    padding: 12px 0;
    border-bottom: 1px solid #ebeef5;
    gap: 8px;

    &:last-child {
      border-bottom: none;
    }

    .row-number {
      width: 30px;
      text-align: center;
      color: #909399;
      font-size: 12px;
      line-height: 32px;
    }

    .row-actions {
      display: flex;
      align-items: center;
      margin-left: auto;
    }
  }

  .subform-actions {
    margin-top: 12px;
    text-align: center;
  }
}
</style>
