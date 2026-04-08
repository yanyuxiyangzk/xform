<template>
  <div class="container-item" :class="widget.options.customClass">
    <!-- Grid Container -->
    <grid-render
      v-if="widget.type === 'grid'"
      :widget="widget"
      :form-model="formModel"
    />

    <!-- Tab Container -->
    <tab-render
      v-else-if="widget.type === 'tab'"
      :widget="widget"
      :form-model="formModel"
    />

    <!-- SubForm Container -->
    <subform-render
      v-else-if="widget.type === 'sub-form'"
      :widget="widget"
      :form-model="formModel"
    />

    <!-- Table Container -->
    <table-render
      v-else-if="widget.type === 'table'"
      :widget="widget"
      :form-model="formModel"
    />

    <!-- Default Container (for nested containers) -->
    <template v-else>
      <template v-for="(child, index) in widget.widgetList" :key="child.id">
        <container-item
          v-if="child.category === 'container'"
          :widget="child"
          :form-model="formModel"
          :parent-list="widget.widgetList"
          :index-of-parent-list="index"
          :parent-widget="widget"
        />
        <field-renderer
          v-else
          :field="child"
          :form-model="formModel"
          :parent-list="widget.widgetList"
          :index-of-parent-list="index"
          :parent-widget="widget"
        />
      </template>
    </template>
  </div>
</template>

<script setup lang="ts">
import GridRender from './grid-render.vue'
import TabRender from './tab-render.vue'
import SubformRender from './subform-render.vue'
import TableRender from './table-render.vue'
import FieldRenderer from '../field-renderer.vue'

const props = defineProps<{
  widget: any
  formModel: Record<string, any>
  parentList?: any[]
  indexOfParentList?: number
  parentWidget?: any
}>()
</script>

<style lang="scss" scoped>
.container-item {
  width: 100%;
  min-height: 32px;
}
</style>
