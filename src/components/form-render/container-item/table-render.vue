<template>
  <div class="table-render" :class="widget.options.customClass">
    <table class="render-table" :style="tableStyle">
      <tbody>
        <tr v-for="(row, rowIndex) in widget.options.rows" :key="row.id">
          <td
            v-for="(cell, cellIndex) in row.cols"
            :key="cell.id"
            :colspan="cell.options.colspan"
            :rowspan="cell.options.rowspan"
            class="table-cell"
            v-show="!cell.merged"
          >
            <template v-for="(child, index) in cell.widgetList" :key="child.id">
              <container-item
                v-if="child.category === 'container'"
                :widget="child"
                :form-model="formModel"
                :parent-list="cell.widgetList"
                :index-of-parent-list="index"
                :parent-widget="cell"
              />
              <field-renderer
                v-else
                :field="child"
                :form-model="formModel"
                :parent-list="cell.widgetList"
                :index-of-parent-list="index"
                :parent-widget="cell"
              />
            </template>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import FieldRenderer from '../field-renderer.vue'
import ContainerItem from './index.vue'

const props = defineProps<{
  widget: any
  formModel: Record<string, any>
}>()

const tableStyle = computed(() => {
  const style: Record<string, string> = {}
  if (props.widget.options.width) {
    style.width = props.widget.options.width
  }
  if (props.widget.options.height) {
    style.height = props.widget.options.height
  }
  return style
})
</script>

<style lang="scss" scoped>
.table-render {
  width: 100%;

  .render-table {
    width: 100%;
    border-collapse: collapse;
    table-layout: fixed;

    td.table-cell {
      border: 1px solid #dcdfe6;
      padding: 8px;
      min-width: 80px;
      vertical-align: top;

      &:empty::after {
        content: '';
        display: block;
        min-height: 32px;
      }
    }
  }
}
</style>
