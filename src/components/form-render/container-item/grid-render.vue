<template>
  <el-row :gutter="widget.options.gutter" class="grid-render">
    <el-col
      v-for="col in widget.cols"
      :key="col.id"
      :span="col.options.span"
      :offset="col.options.offset || 0"
      :push="col.options.push || 0"
      :pull="col.options.pull || 0"
    >
      <template v-for="(child, index) in col.widgetList" :key="child.id">
        <container-item
          v-if="child.category === 'container'"
          :widget="child"
          :form-model="formModel"
          :parent-list="col.widgetList"
          :index-of-parent-list="index"
          :parent-widget="col"
        />
        <field-renderer
          v-else
          :field="child"
          :form-model="formModel"
          :parent-list="col.widgetList"
          :index-of-parent-list="index"
          :parent-widget="col"
        />
      </template>
    </el-col>
  </el-row>
</template>

<script setup lang="ts">
import FieldRenderer from '../field-renderer.vue'
import ContainerItem from './index.vue'

defineProps<{
  widget: any
  formModel: Record<string, any>
}>()
</script>

<style lang="scss" scoped>
.grid-render {
  width: 100%;
}
</style>
