<template>
  <div class="form-widget-wrapper" :class="layoutClass">
    <div class="form-widget-canvas" v-if="widgetList.length === 0">
      <div class="empty-canvas-hint">
        <span>请从左侧面板拖拽组件到此区域</span>
      </div>
    </div>

    <div v-else class="widget-list-container">
      <template v-for="(widget, index) in widgetList" :key="widget.id">
        <!-- Container Widget -->
        <template v-if="widget.category === 'container'">
          <container-wrapper
            :widget="widget"
            :parent-list="widgetList"
            :index-of-parent-list="index"
            :parent-widget="null"
            :designer="designer"
          />
        </template>
        <!-- Field Widget -->
        <template v-else>
          <field-wrapper
            :field="widget"
            :parent-list="widgetList"
            :index-of-parent-list="index"
            :parent-widget="null"
            :designer="designer"
          />
        </template>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, provide } from 'vue'
import ContainerWrapper from './container-widget/container-wrapper.vue'
import FieldWrapper from './field-widget/field-wrapper.vue'
import eventBus from '@/utils/event-bus'

const props = defineProps<{
  designer: any
  formConfig: any
  globalDsv: any
}>()

const widgetList = computed(() => props.designer.widgetList || [])

const layoutClass = computed(() => {
  const layoutType = props.designer.formConfig?.layoutType || 'PC'
  return {
    'pc-layout': layoutType === 'PC',
    'pad-layout': layoutType === 'Pad',
    'h5-layout': layoutType === 'H5',
  }
})

provide('getGlobalDsv', () => props.globalDsv)
provide('getDesignerConfig', () => ({}))
provide('previewState', false)
provide('getReadMode', () => false)

eventBus.on('widget-selected', (widget: any) => {
  props.designer.setSelected(widget)
})
</script>

<style lang="scss" scoped>
.form-widget-wrapper {
  min-height: 100%;
  padding: 8px;

  &.pc-layout {
    // PC layout styles
  }

  &.pad-layout {
    max-width: 960px;
    margin: 0 auto;
  }

  &.h5-layout {
    max-width: 420px;
    margin: 0 auto;
  }
}

.form-widget-canvas {
  min-height: 400px;
  border: 2px dashed #dcdfe6;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fafafa;

  .empty-canvas-hint {
    color: #909399;
    font-size: 14px;
  }
}

.widget-list-container {
  min-height: 100%;
}
</style>
