// API Response Types
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

export interface PageResponse<T = any> {
  list: T[]
  total: number
  page: number
  pageSize: number
}

// Upload Types
export interface UploadResponse {
  url: string
  filename: string
  size: number
  mimeType: string
}

export interface UploadRequest {
  file: File
  name: string
  action: string
  headers?: Record<string, string>
  data?: Record<string, any>
  withCredentials?: boolean
  onProgress?: (event: ProgressEvent) => void
  onSuccess?: (response: any) => void
  onError?: (error: Error) => void
}

// Data Source Types
export interface DataSourceConfig {
  type: 'static' | 'dynamic'
  url?: string
  method?: 'GET' | 'POST'
  headers?: Record<string, string>
  params?: Record<string, any>
  dataPath?: string
  labelKey?: string
  valueKey?: string
  options?: Array<{ label: string; value: any }>
}

// Remote Select Options
export interface RemoteSelectOptions {
  label: string
  value: any
  disabled?: boolean
}

// Form Validation
export interface ValidationRule {
  type: string
  message?: string
  required?: boolean
  min?: number
  max?: number
  minLength?: number
  maxLength?: number
  pattern?: string
  validator?: (rule: any, value: any, callback: any) => void
}

// Export Types
export interface ExportOptions {
  format: 'json' | 'vue' | 'html'
  includeStyle?: boolean
  fileName?: string
}

export interface CodeTemplate {
  template: string
  imports: string[]
  style?: string
}
