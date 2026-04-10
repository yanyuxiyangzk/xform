<template>
  <el-dialog
    v-model="dialogVisible"
    :title="i18nText('designer.toolbar.formTemplate')"
    width="800px"
    destroy-on-close
  >
    <div class="template-container">
      <el-row :gutter="16">
        <el-col
          v-for="tpl in templateList"
          :key="tpl.id"
          :span="8"
          class="template-item"
          @click="selectTemplate(tpl)"
        >
          <el-card shadow="hover" :class="{ selected: selectedId === tpl.id }">
            <div class="template-preview">
              <div class="preview-placeholder">{{ tpl.name }}</div>
            </div>
            <div class="template-info">
              <h4>{{ tpl.name }}</h4>
              <p>{{ tpl.description }}</p>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    <template #footer>
      <el-button @click="dialogVisible = false">{{ i18nText('designer.hint.cancel') }}</el-button>
      <el-button type="primary" :disabled="!selectedId" @click="confirmTemplate">{{ i18nText('designer.hint.confirm') }}</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { deepClone } from '@/utils/util'

const props = defineProps<{
  modelValue: boolean
  designer: any
}>()

const emit = defineEmits(['update:modelValue'])

const dialogVisible = ref(false)
const selectedId = ref<string | null>(null)

watch(() => props.modelValue, (val) => {
  dialogVisible.value = val
  if (val) {
    selectedId.value = null
  }
})

watch(dialogVisible, (val) => {
  emit('update:modelValue', val)
})

// 内置模板列表
const templateList = ref([
  {
    id: 'blank',
    name: '空白表单',
    description: '从空白表单开始创建',
    widgetList: [],
    formConfig: null
  },
  {
    id: 'contact',
    name: '联系人信息',
    description: '包含姓名、手机、邮箱等联系信息字段',
    widgetList: [
      {
        id: 'grid' + Date.now(),
        key: 'grid' + Date.now(),
        type: 'grid',
        category: 'container',
        cols: [
          {
            id: 'grid-col-1',
            type: 'grid-col',
            options: { name: 'gridCol1', span: 12 },
            widgetList: [
              {
                id: 'input' + Date.now(),
                key: 'input' + Date.now(),
                type: 'input',
                formItemFlag: true,
                options: {
                  name: 'name',
                  label: '姓名',
                  placeholder: '请输入姓名',
                  labelWidth: 80,
                  labelPosition: 'left'
                }
              }
            ]
          },
          {
            id: 'grid-col-2',
            type: 'grid-col',
            options: { name: 'gridCol2', span: 12 },
            widgetList: [
              {
                id: 'input' + (Date.now() + 1),
                key: 'input' + (Date.now() + 1),
                type: 'input',
                formItemFlag: true,
                options: {
                  name: 'phone',
                  label: '手机号',
                  placeholder: '请输入手机号',
                  labelWidth: 80,
                  labelPosition: 'left'
                }
              }
            ]
          }
        ],
        options: { name: 'grid1', hidden: false, customClass: '', gutter: 0 }
      },
      {
        id: 'input' + (Date.now() + 2),
        key: 'input' + (Date.now() + 2),
        type: 'input',
        formItemFlag: true,
        options: {
          name: 'email',
          label: '邮箱',
          placeholder: '请输入邮箱地址',
          labelWidth: 80,
          labelPosition: 'left'
        }
      }
    ],
    formConfig: {
      modelName: 'formData',
      refName: 'xForm',
      labelWidth: 80,
      labelPosition: 'left',
      size: 'default',
      labelAlign: 'label-left-align',
      layoutType: 'PC'
    }
  },
  {
    id: 'survey',
    name: '调查问卷',
    description: '适合市场调研、用户反馈收集',
    widgetList: [
      {
        id: 'input' + Date.now(),
        key: 'input' + Date.now(),
        type: 'input',
        formItemFlag: true,
        options: {
          name: 'title',
          label: '问卷标题',
          placeholder: '请输入问卷标题',
          labelWidth: 80
        }
      },
      {
        id: 'textarea' + Date.now(),
        key: 'textarea' + Date.now(),
        type: 'textarea',
        formItemFlag: true,
        options: {
          name: 'description',
          label: '问卷说明',
          placeholder: '请输入问卷说明',
          labelWidth: 80
        }
      },
      {
        id: 'radio' + Date.now(),
        key: 'radio' + Date.now(),
        type: 'radio',
        formItemFlag: true,
        options: {
          name: 'satisfaction',
          label: '总体满意度',
          labelWidth: 100,
          optionItems: [
            { label: '非常满意', value: '5' },
            { label: '满意', value: '4' },
            { label: '一般', value: '3' },
            { label: '不满意', value: '2' },
            { label: '非常不满意', value: '1' }
          ]
        }
      },
      {
        id: 'checkbox' + Date.now(),
        key: 'checkbox' + Date.now(),
        type: 'checkbox',
        formItemFlag: true,
        options: {
          name: 'interests',
          label: '感兴趣的领域',
          labelWidth: 100,
          optionItems: [
            { label: '前端开发', value: 'frontend' },
            { label: '后端开发', value: 'backend' },
            { label: '移动开发', value: 'mobile' },
            { label: '数据分析', value: 'data' }
          ]
        }
      }
    ],
    formConfig: {
      modelName: 'formData',
      refName: 'xForm',
      labelWidth: 100,
      labelPosition: 'left',
      size: 'default',
      labelAlign: 'label-left-align',
      layoutType: 'PC'
    }
  },
  {
    id: 'order',
    name: '订单信息',
    description: '包含商品、数量、联系方式等订单字段',
    widgetList: [
      {
        id: 'input' + Date.now(),
        key: 'input' + Date.now(),
        type: 'input',
        formItemFlag: true,
        options: {
          name: 'orderNo',
          label: '订单号',
          placeholder: '请输入订单号',
          labelWidth: 80
        }
      },
      {
        id: 'number' + Date.now(),
        key: 'number' + Date.now(),
        type: 'number',
        formItemFlag: true,
        options: {
          name: 'quantity',
          label: '数量',
          placeholder: '1',
          min: 1,
          max: 100
        }
      },
      {
        id: 'select' + Date.now(),
        key: 'select' + Date.now(),
        type: 'select',
        formItemFlag: true,
        options: {
          name: 'status',
          label: '订单状态',
          labelWidth: 80,
          optionItems: [
            { label: '待处理', value: 'pending' },
            { label: '处理中', value: 'processing' },
            { label: '已完成', value: 'completed' },
            { label: '已取消', value: 'cancelled' }
          ]
        }
      },
      {
        id: 'date' + Date.now(),
        key: 'date' + Date.now(),
        type: 'date',
        formItemFlag: true,
        options: {
          name: 'deliveryDate',
          label: '期望交付日期',
          labelWidth: 120,
          dateType: 'date'
        }
      }
    ],
    formConfig: {
      modelName: 'formData',
      refName: 'xForm',
      labelWidth: 100,
      labelPosition: 'left',
      size: 'default',
      labelAlign: 'label-left-align',
      layoutType: 'PC'
    }
  },
  {
    id: 'registration',
    name: '活动报名',
    description: '适用于会议、活动、培训的报名表单',
    widgetList: [
      {
        id: 'input' + Date.now(),
        key: 'input' + Date.now(),
        type: 'input',
        formItemFlag: true,
        options: {
          name: 'name',
          label: '姓名',
          placeholder: '请输入真实姓名',
          labelWidth: 80
        }
      },
      {
        id: 'input' + (Date.now() + 1),
        key: 'input' + (Date.now() + 1),
        type: 'input',
        formItemFlag: true,
        options: {
          name: 'phone',
          label: '手机号',
          placeholder: '请输入手机号',
          labelWidth: 80
        }
      },
      {
        id: 'select' + Date.now(),
        key: 'select' + Date.now(),
        type: 'select',
        formItemFlag: true,
        options: {
          name: 'event',
          label: '报名场次',
          labelWidth: 80,
          optionItems: [
            { label: '上午场 (9:00-12:00)', value: 'morning' },
            { label: '下午场 (14:00-17:00)', value: 'afternoon' },
            { label: '晚场 (19:00-21:00)', value: 'evening' }
          ]
        }
      },
      {
        id: 'switch' + Date.now(),
        key: 'switch' + Date.now(),
        type: 'switch',
        formItemFlag: true,
        options: {
          name: 'needMeal',
          label: '是否需要用餐',
          activeText: '是',
          inactiveText: '否'
        }
      }
    ],
    formConfig: {
      modelName: 'formData',
      refName: 'xForm',
      labelWidth: 100,
      labelPosition: 'left',
      size: 'default',
      labelAlign: 'label-left-align',
      layoutType: 'PC'
    }
  }
])

function i18nText(key: string): string {
  const map: Record<string, string> = {
    'designer.toolbar.formTemplate': '表单模板',
    'designer.hint.cancel': '取消',
    'designer.hint.confirm': '确定'
  }
  return map[key] || key
}

function selectTemplate(tpl: any) {
  selectedId.value = tpl.id
}

function confirmTemplate() {
  const tpl = templateList.value.find(t => t.id === selectedId.value)
  if (tpl) {
    props.designer.clearDesigner(true)
    if (tpl.widgetList.length > 0) {
      props.designer.loadFormJson({
        widgetList: deepClone(tpl.widgetList),
        formConfig: deepClone(tpl.formConfig)
      })
    } else {
      props.designer.initDesigner()
    }
  }
  dialogVisible.value = false
}
</script>

<style lang="scss" scoped>
.template-container {
  max-height: 60vh;
  overflow-y: auto;
}

.template-item {
  margin-bottom: 16px;
  cursor: pointer;

  .el-card {
    transition: all 0.3s;

    &.selected {
      border-color: #667eea;
      background: rgba(102, 126, 234, 0.05);
    }

    &:hover {
      border-color: #667eea;
    }
  }

  .template-preview {
    height: 80px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 12px;

    .preview-placeholder {
      color: white;
      font-size: 14px;
      font-weight: bold;
    }
  }

  .template-info {
    h4 {
      margin: 0 0 8px 0;
      font-size: 14px;
      color: #303133;
    }

    p {
      margin: 0;
      font-size: 12px;
      color: #909399;
    }
  }
}
</style>
