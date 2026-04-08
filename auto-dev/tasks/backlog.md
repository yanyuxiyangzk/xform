# 开发任务池

> 按优先级排序的待办任务列表（由Product Manager维护）
> 最后更新：2026-04-04

---

## 任务角色归属

| 角色 | 负责任务类型 |
|------|-------------|
| backend-dev | Java接口、Service、Mapper、Entity |
| frontend-dev | Vue页面、组件、API调用 |
| ui-designer | 界面设计、UX优化、样式规范 |
| tester | 测试用例、测试执行、缺陷报告 |
| devops | Docker、K8s、CI/CD、部署配置 |
| operation | 监控、运维、环境维护 |

---

## P0 - 紧急任务

### TASK-20260404-001
- **标题**: 修复JDK17+Lombok编译问题
- **类型**: bugfix
- **优先级**: P0
- **负责人**: backend-dev
- **状态**: pending
- **影响模块**:
  - `nocode-api-generator/nocode-api-admin`
  - `ruoyi-nocode/ruoyi-nocode-system`
- **问题描述**:
  - JDK17下Lombok注解处理器无法正常生成getter/setter/log字段
  - 代码使用了JDK9+特性(List.of(), Map.of(), Optional.isEmpty())但项目target为JDK8
- **根因**:
  - JDK17模块系统与Lombok 1.18.30/1.18.32的annotation processor不兼容
  - pom.xml中未正确配置annotationProcessorPaths
- **解决方案**:
  1. 升级Lombok到1.18.34+ (更好的JDK17支持)
  2. 或在pom.xml中正确配置maven-compiler-plugin的annotationProcessorPaths
  3. 将代码中的JDK9+特性替换为JDK8兼容写法
- **验收标准**:
  - [ ] nocode-api-admin `mvn compile` 成功
  - [ ] ruoyi-nocode-system `mvn compile` 成功
  - [ ] 所有单元测试通过

### TASK-20260403-001
- **标题**: [P0任务标题]
- **类型**: feature
- **优先级**: P0
- **负责人**: [角色]
- **状态**: pending
- **验收标准**:
  - [ ]
- **影响范围**:
- **风险等级**:

---

## P1 - 重要任务

### TASK-20260403-002
- **标题**: [P1任务标题]
- **类型**: feature
- **优先级**: P1
- **负责人**: [角色]
- **状态**: pending
- **验收标准**:
  - [ ]
- **影响范围**:
- **风险等级**:

---

## 任务模板

```markdown
# 任务卡片

## 基本信息
- ID: TASK-YYYYMMDD-NNN
- 标题: [任务标题]
- 类型: feature | bugfix | test | devops | optimization
- 优先级: P0 | P1 | P2
- 创建时间: YYYY-MM-DD HH:mm
- 最后更新: YYYY-MM-DD HH:mm
- 负责人: backend-dev | frontend-dev | ui-designer | tester | devops | operation

## 任务详情
- **目标**: [清晰的目标描述]
- **验收标准**:
  - [ ] 标准1
  - [ ] 标准2
- **影响范围**: [影响的模块或功能]
- **风险等级**: 低 | 中 | 高

## 依赖关系
- 前置任务: [TASK-ID] 或 无
- 依赖任务: [TASK-ID] 或 无

## 状态
状态: pending | in_progress | completed | blocked
```

---

## 已完成任务

### TASK-20260402-001 ~ TASK-20260402-006
- ✅ Liquor即时编译
- ✅ Liquor类热替换
- ✅ 代码生成引擎
- ✅ 字典管理功能
- ✅ 沙箱执行环境
- ✅ 动态编译IDE
