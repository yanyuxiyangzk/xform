<template>
  <el-dialog
    v-model="dialogVisible"
    :title="i18nText('designer.toolbar.dataSource')"
    width="900px"
    destroy-on-close
  >
    <div class="datasource-container">
      <div class="toolbar">
        <el-button type="primary" @click="addDataSource">{{ i18nText('designer.toolbar.addDataSource') }}</el-button>
      </div>

      <el-table :data="dataSourceList" border stripe>
        <el-table-column prop="name" :label="i18nText('designer.datasource.name')" width="150" />
        <el-table-column prop="type" :label="i18nText('designer.datasource.type')" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.type === 'static'" size="small">{{ i18nText('designer.datasource.static') }}</el-tag>
            <el-tag v-else-if="row.type === 'dynamic'" type="success" size="small">{{ i18nText('designer.datasource.dynamic') }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="url" :label="i18nText('designer.datasource.url')" min-width="200">
          <template #default="{ row }">
            <span v-if="row.type === 'dynamic'">{{ row.url }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="method" :label="i18nText('designer.datasource.method')" width="80">
          <template #default="{ row }">
            <el-tag v-if="row.type === 'dynamic'" :type="row.method === 'GET' ? 'success' : 'warning'" size="small">
              {{ row.method }}
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column :label="i18nText('designer.datasource.actions')" width="150" fixed="right">
          <template #default="{ row, $index }">
            <el-button link type="primary" size="small" @click="editDataSource(row, $index)">{{ i18nText('designer.hint.edit') }}</el-button>
            <el-button link type="danger" size="small" @click="deleteDataSource($index)">{{ i18nText('designer.hint.delete') }}</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- Add/Edit Dialog -->
    <el-dialog
      v-model="showEditDialog"
      :title="isEdit ? i18nText('designer.toolbar.editDataSource') : i18nText('designer.toolbar.addDataSource')"
      width="600px"
      append-to-body
      destroy-on-close
    >
      <el-form :model="formData" label-width="100px">
        <el-form-item :label="i18nText('designer.datasource.name')" required>
          <el-input v-model="formData.name" :placeholder="i18nText('designer.datasource.namePlaceholder')" />
        </el-form-item>
        <el-form-item :label="i18nText('designer.datasource.type')" required>
          <el-radio-group v-model="formData.type" @change="onTypeChange">
            <el-radio value="static">{{ i18nText('designer.datasource.static') }}</el-radio>
            <el-radio value="dynamic">{{ i18nText('designer.datasource.dynamic') }}</el-radio>
          </el-radio-group>
        </el-form-item>

        <template v-if="formData.type === 'dynamic'">
          <el-form-item :label="i18nText('designer.datasource.url')" required>
            <el-input v-model="formData.url" placeholder="https://api.example.com/data" />
          </el-form-item>
          <el-form-item :label="i18nText('designer.datasource.method')">
            <el-radio-group v-model="formData.method">
              <el-radio value="GET">GET</el-radio>
              <el-radio value="POST">POST</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item :label="i18nText('designer.datasource.dataPath')">
            <el-input v-model="formData.dataPath" placeholder="data.items" />
          </el-form-item>
          <el-form-item :label="i18nText('designer.datasource.labelKey')">
            <el-input v-model="formData.labelKey" placeholder="label" />
          </el-form-item>
          <el-form-item :label="i18nText('designer.datasource.valueKey')">
            <el-input v-model="formData.valueKey" placeholder="value" />
          </el-form-item>
        </template>

        <template v-else>
          <el-form-item :label="i18nText('designer.datasource.staticOptions')">
            <div class="static-options-editor">
              <el-row v-for="(opt, idx) in formData.options" :key="idx" :gutter="8" class="option-row">
                <el-col :span="10">
                  <el-input v-model="opt.label" :placeholder="i18nText('designer.datasource.label')" />
                </el-col>
                <el-col :span="10">
                  <el-input v-model="opt.value" :placeholder="i18nText('designer.datasource.value')" />
                </el-col>
                <el-col :span="4">
                  <el-button link type="danger" @click="removeOption(idx)">×</el-button>
                </el-col>
              </el-row>
              <el-button link type="primary" @click="addOption">+ {{ i18nText('designer.datasource.addOption') }}</el-button>
            </div>
          </el-form-item>
        </template>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">{{ i18nText('designer.hint.cancel') }}</el-button>
        <el-button type="primary" @click="saveDataSource">{{ i18nText('designer.hint.confirm') }}</el-button>
      </template>
    </el-dialog>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'

const props = defineProps<{
  modelValue: boolean
  designer: any
}>()

const emit = defineEmits(['update:modelValue'])

const dialogVisible = ref(false)
const showEditDialog = ref(false)
const isEdit = ref(false)
const editingIndex = ref(-1)

const defaultFormData = () => ({
  id: '',
  name: '',
  type: 'static' as 'static' | 'dynamic',
  url: '',
  method: 'GET' as 'GET' | 'POST',
  dataPath: 'data',
  labelKey: 'label',
  valueKey: 'value',
  options: [{ label: '', value: '' }]
})

const formData = reactive<any>(defaultFormData())

watch(() => props.modelValue, (val) => {
  dialogVisible.value = val
  if (val) {
    loadDataSources()
  }
})

watch(dialogVisible, (val) => {
  emit('update:modelValue', val)
})

function loadDataSources() {
  if (!props.designer.formConfig.dataSources) {
    props.designer.formConfig.dataSources = []
  }
}

function i18nText(key: string): string {
  const map: Record<string, string> = {
    'designer.toolbar.dataSource': '数据源管理',
    'designer.toolbar.addDataSource': '新增数据源',
    'designer.toolbar.editDataSource': '编辑数据源',
    'designer.datasource.name': '名称',
    'designer.datasource.type': '类型',
    'designer.datasource.static': '静态数据',
    'designer.datasource.dynamic': '动态数据',
    'designer.datasource.url': '接口地址',
    'designer.datasource.method': '请求方式',
    'designer.datasource.dataPath': '数据路径',
    'designer.datasource.labelKey': '标签字段',
    'designer.datasource.valueKey': '值字段',
    'designer.datasource.actions': '操作',
    'designer.datasource.namePlaceholder': '请输入数据源名称',
    'designer.datasource.staticOptions': '静态选项',
    'designer.datasource.addOption': '添加选项',
    'designer.datasource.label': '显示文本',
    'designer.datasource.value': '对应值',
    'designer.hint.edit': '编辑',
    'designer.hint.delete': '删除',
    'designer.hint.cancel': '取消',
    'designer.hint.confirm': '确定'
  }
  return map[key] || key
}

function getDataSourceList() {
  return props.designer.formConfig.dataSources || []
}

function addDataSource() {
  isEdit.value = false
  editingIndex.value = -1
  Object.assign(formData, defaultFormData())
  showEditDialog.value = true
}

function editDataSource(row: any, index: number) {
  isEdit.value = true
  editingIndex.value = index
  Object.assign(formData, JSON.parse(JSON.stringify(row)))
  showEditDialog.value = true
}

function deleteDataSource(index: number) {
  getDataSourceList().splice(index, 1)
}

function onTypeChange() {
  if (formData.type === 'static' && formData.options.length === 0) {
    formData.options = [{ label: '', value: '' }]
  }
}

function addOption() {
  formData.options.push({ label: '', value: '' })
}

function removeOption(index: number) {
  formData.options.splice(index, 1)
}

function saveDataSource() {
  if (!formData.name) {
    alert('请输入数据源名称')
    return
  }

  if (formData.type === 'static') {
    formData.options = formData.options.filter((o: any) => o.label && o.value)
  }

  if (isEdit.value) {
    getDataSourceList()[editingIndex.value] = JSON.parse(JSON.stringify(formData))
  } else {
    formData.id = 'ds_' + Date.now()
    getDataSourceList().push(JSON.parse(JSON.stringify(formData)))
  }

  showEditDialog.value = false
}
</script>

<style lang="scss" scoped>
.datasource-container {
  .toolbar {
    margin-bottom: 16px;
  }
}

.static-options-editor {
  .option-row {
    margin-bottom: 8px;
  }
}
</style>
