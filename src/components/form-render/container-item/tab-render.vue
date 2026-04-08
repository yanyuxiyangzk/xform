<template>
  <el-tabs
    v-model="activeTabName"
    :type="widget.options.tabType || 'border-card'"
    :tab-position="widget.options.tabPosition || 'top'"
    class="tab-render"
  >
    <el-tab-pane
      v-for="tab in widget.tabs"
      :key="tab.id"
      :label="tab.options.label"
      :name="tab.options.name"
      :lazy="true"
    >
      <template v-for="(child, index) in tab.widgetList" :key="child.id">
        <container-item
          v-if="child.category === 'container'"
          :widget="child"
          :form-model="formModel"
          :parent-list="tab.widgetList"
          :index-of-parent-list="index"
          :parent-widget="tab"
        />
        <field-renderer
          v-else
          :field="child"
          :form-model="formModel"
          :parent-list="tab.widgetList"
          :index-of-parent-list="index"
          :parent-widget="tab"
        />
      </template>
    </el-tab-pane>
  </el-tabs>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import FieldRenderer from '../field-renderer.vue'
import ContainerItem from './index.vue'

const props = defineProps<{
  widget: any
  formModel: Record<string, any>
}>()

const activeTabName = ref('')

watch(() => props.widget.tabs, (tabs) => {
  if (tabs && tabs.length > 0) {
    const activeTab = tabs.find((t: any) => t.options.active)
    activeTabName.value = activeTab ? activeTab.options.name : tabs[0].options.name
  }
}, { immediate: true })
</script>

<style lang="scss" scoped>
.tab-render {
  width: 100%;
}
</style>
