# Graph Report - D:/project/aicoding/item/xform  (2026-04-09)

## Corpus Check
- Large corpus: 238 files · ~89,243 words. Semantic extraction will be expensive (many Claude tokens). Consider running on a subfolder, or use --no-semantic to run AST-only.

## Summary
- 908 nodes · 1585 edges · 78 communities detected
- Extraction: 54% EXTRACTED · 46% INFERRED · 0% AMBIGUOUS · INFERRED: 722 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## God Nodes (most connected - your core abstractions)
1. `PipelineRunner` - 37 edges
2. `SelfHealer` - 31 edges
3. `TeamLauncher` - 26 edges
4. `MemoryTierManager` - 25 edges
5. `ThemeManager` - 20 edges
6. `SelfImproveOps` - 19 edges
7. `ModelEscalation` - 18 edges
8. `NotificationOps` - 18 edges
9. `WidgetPackageManager` - 18 edges
10. `AutoHeartbeat` - 17 edges

## Surprising Connections (you probably didn't know these)
- `触发学习         返回学习记录ID` --uses--> `SelfImproveOps`  [INFERRED]
  auto-dev\scripts\auto_learn_hook.py → auto-dev\scripts\self_improve_ops.py
- `触发反思         返回反思记录ID` --uses--> `SelfImproveOps`  [INFERRED]
  auto-dev\scripts\auto_reflect_hook.py → auto-dev\scripts\self_improve_ops.py
- `PipelineRunner` --uses--> `MemoryTierManager`  [INFERRED]
  auto-dev\scripts\pipeline_runner.py → auto-dev\memory\memory_tier_manager.py
- `[GUARDIAN] 检查团队结构是否正确创建         支持两种团队配置:         1. Claude Code CLI 团队: ~/.clau` --uses--> `MemoryTierManager`  [INFERRED]
  auto-dev\scripts\pipeline_runner.py → auto-dev\memory\memory_tier_manager.py
- `[MEMORY] 自动记忆层级管理         在关键节点调用，保持记忆层健康` --uses--> `MemoryTierManager`  [INFERRED]
  auto-dev\scripts\pipeline_runner.py → auto-dev\memory\memory_tier_manager.py

## Hyperedges (group relationships)
- **Pipeline Stages** — requirement_stage, design_stage, development_stage, testing_stage, deployment_stage [EXTRACTED 1.00]
- **Form Designer Architecture** — form_designer, form_renderer, form_components, widget_registry, designer_store [EXTRACTED 0.90]
- **Tech Stack** — tech_spring_boot, tech_spring_cloud, tech_pf4j, tech_liquor, tech_vue3, tech_redis [EXTRACTED 1.00]
- **Memory Tiers** — hot_memory, warm_memory, cold_memory, episodic_memory, working_memory, longterm_memory [EXTRACTED 1.00]
- **Agent Team** — backend_dev, frontend_dev, tester, architect, product_manager, devops [EXTRACTED 0.95]
- **xform Architecture** — xform, form_designer, form_renderer, widget_registry, form_schema [EXTRACTED 0.90]

## Communities

### Community 0 - "Memory Tier Management"
Cohesion: 0.04
Nodes (27): main(), MemoryTierManager, 降低记忆层级 (hot -> warm -> cold), 提升记忆层级 (cold -> warm -> hot), main(), PipelineRunner, [GUARDIAN] 检查团队结构是否正确创建         支持两种团队配置:         1. Claude Code CLI 团队: ~/.clau, [MEMORY] 自动记忆层级管理         在关键节点调用，保持记忆层健康 (+19 more)

### Community 1 - "Quality Gate System"
Cohesion: 0.09
Nodes (22): BaseChecker, CheckItem, CodeStyleChecker, color_print(), Colors, CommandExecutor, CompileChecker, ConfigLoader (+14 more)

### Community 2 - "Code Generation"
Cohesion: 0.06
Nodes (25): generateContainerTemplate(), generateFieldTemplate(), generateFormCode(), generateFormData(), generateFormMethods(), generateFormStyles(), generateFormTemplate(), generateGridTemplate() (+17 more)

### Community 3 - "Code Review Tools"
Cohesion: 0.07
Nodes (21): Enum, CheckResult, color_text(), Colors, CommandExecutor, ComplexityChecker, ConfigLoader, HardcodedSecretChecker (+13 more)

### Community 4 - "Security Scanning"
Cohesion: 0.08
Nodes (15): color_text(), Colors, CommandExecutor, ConfigLoader, DependencyAnalyzeChecker, ForbiddenDepsChecker, HardcodedSecretScanner, main() (+7 more)

### Community 5 - "Agent Spawner"
Cohesion: 0.08
Nodes (26): AgentSpawner, _detect_claude_cli(), main(), 启动单个Agent          Args:             role: Agent角色 (backend-dev, frontend-dev, e, 启动完整团队          Args:             team_name: 团队名称          Returns:, 动态检测 claude-code CLI 路径, Architect Agent, Backend Developer Agent (+18 more)

### Community 6 - "Self-Improvement Hooks"
Cohesion: 0.09
Nodes (12): AutoLearnHook, main(), 检查用户输入是否包含学习信号         返回: (is_correction, pattern_type), 触发学习         返回学习记录ID, AutoReflectHook, main(), 触发反思         返回反思记录ID, COLD memory (+4 more)

### Community 7 - "API Layer"
Cohesion: 0.09
Nodes (13): isArray(), isObj(), Component Market Feature, addContainerWidgetSchema(), createBussinessSourceEditor(), createDataTargetEditor(), createValueSourceEditor(), loadExtensions() (+5 more)

### Community 8 - "Telemetry"
Cohesion: 0.14
Nodes (8): generate_span_id(), generate_trace_id(), get_telemetry(), log_event(), Telemetry, TelemetryEvent, TelemetryLevel, trace()

### Community 9 - "Hook Installation"
Cohesion: 0.16
Nodes (10): color_text(), Colors, ConfigLoader, GitHooksManager, HookConfig, HookInstaller, HookType, main() (+2 more)

### Community 10 - "Model Escalation"
Cohesion: 0.16
Nodes (7): main(), ModelEscalation, 记录卡死状态          Returns:             (should_escalate: bool, reason: str), 记录超时          Returns:             (should_escalate: bool, reason: str), 检查是否应升级模型          Returns:             (should_escalate: bool, reason: str), 执行模型升级          Returns:             (success: bool, message: str), 记录错误          Returns:             (should_escalate: bool, reason: str)

### Community 11 - "Theme Manager"
Cohesion: 0.16
Nodes (1): ThemeManager

### Community 12 - "Data Adapter"
Cohesion: 0.13
Nodes (7): isArray(), isContainer(), isField(), isObj(), getWidgetValue(), LinkWidgetUtils, setValueTotParam()

### Community 13 - "Heartbeat Monitoring"
Cohesion: 0.25
Nodes (4): AutoHeartbeat, color_text(), Colors, main()

### Community 14 - "Notifications"
Cohesion: 0.2
Nodes (3): main(), NotificationOps, 发送通知          Args:             event_type: 事件类型             message: 消息内容

### Community 15 - "Dev Runner"
Cohesion: 0.25
Nodes (6): AutoDevRunner, color_text(), Colors, IntentRecognizer, main(), print_banner()

### Community 16 - "Export Utilities"
Cohesion: 0.17
Nodes (17): buildContainerHtml(), buildFieldHtml(), buildWidgetHtml(), downloadFile(), exportFormJson(), exportHtml(), exportVueSFC(), generateFormDataObj() (+9 more)

### Community 17 - "Widget Package Manager"
Cohesion: 0.17
Nodes (2): generateId(), WidgetPackageManager

### Community 18 - "Orchestrator Ops"
Cohesion: 0.21
Nodes (3): main(), OrchestratorOps, TimeWindowChecker

### Community 19 - "Pace Control"
Cohesion: 0.24
Nodes (5): main(), PaceController, 检查是否可以启动新任务          Returns:             (can_start: bool, reason: str), 记录任务开始          Returns:             (success: bool, message: str), 记录任务结束          Args:             task_id: 任务ID             status: completed /

### Community 20 - "Checkpoint Ops"
Cohesion: 0.24
Nodes (4): CheckpointOps, main(), 从checkpoint恢复          Returns:             checkpoint数据，如恢复失败返回None, 保存checkpoint          Args:             data: checkpoint数据，如不提供则从当前运行状态构建

### Community 21 - "Knowledge Refiner"
Cohesion: 0.25
Nodes (2): KnowledgeRefineOps, main()

### Community 22 - "Tech Stack & Pipelines"
Cohesion: 0.12
Nodes (17): Java/Spring Boot, MySQL, Online Form Designer, PIPELINE-20260405-011, RuoYi-Cloud-Nocode Project, Redis, Frontend Developer Skill, Liquor Dynamic Compiler (+9 more)

### Community 23 - "Knowledge Sync"
Cohesion: 0.31
Nodes (2): KnowledgeSyncOps, main()

### Community 24 - "Daily Routine"
Cohesion: 0.3
Nodes (2): DailyRoutineOps, main()

### Community 25 - "Memory Operations"
Cohesion: 0.23
Nodes (6): episodic memory, knowledge_sync_ops.py, longterm memory, main(), MemoryOps, working memory

### Community 26 - "Guardian Agent"
Cohesion: 0.32
Nodes (3): GuardianAgent, main(), 写代码前的强制检查         必须返回 (can_write, message)

### Community 27 - "Harness Core"
Cohesion: 0.4
Nodes (2): HarnessCore, main()

### Community 28 - "Pipeline Ops"
Cohesion: 0.38
Nodes (2): main(), PipelineOps

### Community 29 - "Designer Store"
Cohesion: 0.22
Nodes (10): Pinia designerStore, Form Components, Form Designer, Form Renderer, 零代码微服务平台核心模块, 在线表单设计器, xform重构, vform3-pro (+2 more)

### Community 30 - "Schema Validator"
Cohesion: 0.42
Nodes (2): main(), SchemaValidator

### Community 31 - "Property Registration"
Cohesion: 0.31
Nodes (6): registerAdvancedProperty(), registerAPEditor(), registerCommonProperty(), registerCPEditor(), registerEPEditor(), registerEventProperty()

### Community 32 - "Dashboard Server"
Cohesion: 0.29
Nodes (4): DashboardHandler, get_local_ip(), main(), SimpleHTTPRequestHandler

### Community 33 - "Archive Hook"
Cohesion: 0.52
Nodes (2): AutoArchiveHook, main()

### Community 34 - "i18n"
Cohesion: 0.33
Nodes (2): getLocale(), t()

### Community 35 - "i18n Utils"
Cohesion: 0.5
Nodes (0): 

### Community 36 - "Validators"
Cohesion: 0.5
Nodes (0): 

### Community 37 - "User Management"
Cohesion: 0.67
Nodes (3): Pipeline 20260408-031, Role Permission Management, User Management

### Community 38 - "Ref Exposure Hook"
Cohesion: 1.0
Nodes (0): 

### Community 39 - "DevOps Docker"
Cohesion: 1.0
Nodes (2): DevOps Skill, Docker

### Community 40 - "Zero Code Platform"
Cohesion: 1.0
Nodes (2): 零代码微服务平台完整开发, auto-dev自我完善需求

### Community 41 - "Pipeline Pairs"
Cohesion: 1.0
Nodes (2): Pipeline 20260407-020, Pipeline 20260407-021

### Community 42 - "Backlog Management"
Cohesion: 1.0
Nodes (2): Product Backlog, Sprint Backlog

### Community 43 - "Community 43"
Cohesion: 1.0
Nodes (0): 

### Community 44 - "Community 44"
Cohesion: 1.0
Nodes (0): 

### Community 45 - "Community 45"
Cohesion: 1.0
Nodes (1): 加载配置文件          Args:             config_path: 配置文件路径             project_root:

### Community 46 - "Community 46"
Cohesion: 1.0
Nodes (0): 

### Community 47 - "Community 47"
Cohesion: 1.0
Nodes (0): 

### Community 48 - "Community 48"
Cohesion: 1.0
Nodes (1): Auto-Dev Team

### Community 49 - "Community 49"
Cohesion: 1.0
Nodes (1): UI Designer Agent

### Community 50 - "Community 50"
Cohesion: 1.0
Nodes (1): DevOps Agent

### Community 51 - "Community 51"
Cohesion: 1.0
Nodes (1): Auto-Dev Harness

### Community 52 - "Community 52"
Cohesion: 1.0
Nodes (1): memory-ops Skill

### Community 53 - "Community 53"
Cohesion: 1.0
Nodes (1): task-analyzer Skill

### Community 54 - "Community 54"
Cohesion: 1.0
Nodes (1): Architect Skill

### Community 55 - "Community 55"
Cohesion: 1.0
Nodes (1): Backend Developer Skill

### Community 56 - "Community 56"
Cohesion: 1.0
Nodes (1): Guardian Skill

### Community 57 - "Community 57"
Cohesion: 1.0
Nodes (1): Exception Handler Skill

### Community 58 - "Community 58"
Cohesion: 1.0
Nodes (1): FormSchema

### Community 59 - "Community 59"
Cohesion: 1.0
Nodes (1): Naive UI

### Community 60 - "Community 60"
Cohesion: 1.0
Nodes (1): vue-draggable-plus

### Community 61 - "Community 61"
Cohesion: 1.0
Nodes (1): PIPELINE-20260405-012

### Community 62 - "Community 62"
Cohesion: 1.0
Nodes (1): PIPELINE-20260405-013

### Community 63 - "Community 63"
Cohesion: 1.0
Nodes (1): Pipeline 20260408-023

### Community 64 - "Community 64"
Cohesion: 1.0
Nodes (1): Pipeline 20260408-024

### Community 65 - "Community 65"
Cohesion: 1.0
Nodes (1): Pipeline 20260408-025

### Community 66 - "Community 66"
Cohesion: 1.0
Nodes (1): Pipeline 20260408-026

### Community 67 - "Community 67"
Cohesion: 1.0
Nodes (1): Pipeline 20260408-027

### Community 68 - "Community 68"
Cohesion: 1.0
Nodes (1): Pipeline 20260408-028

### Community 69 - "Community 69"
Cohesion: 1.0
Nodes (1): Pipeline 20260408-029

### Community 70 - "Community 70"
Cohesion: 1.0
Nodes (1): Pipeline 20260408-030

### Community 71 - "Community 71"
Cohesion: 1.0
Nodes (1): Checkpoint+Stuck+Selfheal

### Community 72 - "Community 72"
Cohesion: 1.0
Nodes (1): Dashboard Feature

### Community 73 - "Community 73"
Cohesion: 1.0
Nodes (1): CLI Progress Feature

### Community 74 - "Community 74"
Cohesion: 1.0
Nodes (1): History Feature

### Community 75 - "Community 75"
Cohesion: 1.0
Nodes (1): Pipeline 20260408-032

### Community 76 - "Community 76"
Cohesion: 1.0
Nodes (1): Pipeline 20260408-033

### Community 77 - "Community 77"
Cohesion: 1.0
Nodes (1): Theme System

## Knowledge Gaps
- **102 isolated node(s):** `提升记忆层级 (cold -> warm -> hot)`, `降低记忆层级 (hot -> warm -> cold)`, `动态检测 claude-code CLI 路径`, `启动单个Agent          Args:             role: Agent角色 (backend-dev, frontend-dev, e`, `启动完整团队          Args:             team_name: 团队名称          Returns:` (+97 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Ref Exposure Hook`** (2 nodes): `useRefExpose.ts`, `useRefExpose()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `DevOps Docker`** (2 nodes): `DevOps Skill`, `Docker`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Zero Code Platform`** (2 nodes): `零代码微服务平台完整开发`, `auto-dev自我完善需求`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Pipeline Pairs`** (2 nodes): `Pipeline 20260407-020`, `Pipeline 20260407-021`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Backlog Management`** (2 nodes): `Product Backlog`, `Sprint Backlog`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 43`** (1 nodes): `playwright.config.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 44`** (1 nodes): `vite.config.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 45`** (1 nodes): `加载配置文件          Args:             config_path: 配置文件路径             project_root:`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 46`** (1 nodes): `env.d.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 47`** (1 nodes): `app.spec.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 48`** (1 nodes): `Auto-Dev Team`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 49`** (1 nodes): `UI Designer Agent`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 50`** (1 nodes): `DevOps Agent`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 51`** (1 nodes): `Auto-Dev Harness`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 52`** (1 nodes): `memory-ops Skill`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 53`** (1 nodes): `task-analyzer Skill`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 54`** (1 nodes): `Architect Skill`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 55`** (1 nodes): `Backend Developer Skill`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 56`** (1 nodes): `Guardian Skill`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 57`** (1 nodes): `Exception Handler Skill`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 58`** (1 nodes): `FormSchema`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 59`** (1 nodes): `Naive UI`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 60`** (1 nodes): `vue-draggable-plus`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 61`** (1 nodes): `PIPELINE-20260405-012`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 62`** (1 nodes): `PIPELINE-20260405-013`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 63`** (1 nodes): `Pipeline 20260408-023`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 64`** (1 nodes): `Pipeline 20260408-024`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 65`** (1 nodes): `Pipeline 20260408-025`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 66`** (1 nodes): `Pipeline 20260408-026`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 67`** (1 nodes): `Pipeline 20260408-027`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 68`** (1 nodes): `Pipeline 20260408-028`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 69`** (1 nodes): `Pipeline 20260408-029`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 70`** (1 nodes): `Pipeline 20260408-030`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 71`** (1 nodes): `Checkpoint+Stuck+Selfheal`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 72`** (1 nodes): `Dashboard Feature`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 73`** (1 nodes): `CLI Progress Feature`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 74`** (1 nodes): `History Feature`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 75`** (1 nodes): `Pipeline 20260408-032`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 76`** (1 nodes): `Pipeline 20260408-033`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 77`** (1 nodes): `Theme System`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Orchestrator` connect `Agent Spawner` to `Quality Gate System`, `Checkpoint Ops`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `PipelineRunner` (e.g. with `main()` and `SelfHealer`) actually correct?**
  _`PipelineRunner` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `SelfHealer` (e.g. with `main()` and `PipelineRunner`) actually correct?**
  _`SelfHealer` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `TeamLauncher` (e.g. with `main()` and `PipelineRunner`) actually correct?**
  _`TeamLauncher` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `MemoryTierManager` (e.g. with `main()` and `PipelineRunner`) actually correct?**
  _`MemoryTierManager` has 14 INFERRED edges - model-reasoned connections that need verification._
- **What connects `提升记忆层级 (cold -> warm -> hot)`, `降低记忆层级 (hot -> warm -> cold)`, `动态检测 claude-code CLI 路径` to the rest of the system?**
  _102 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Memory Tier Management` be split into smaller, more focused modules?**
  _Cohesion score 0.04 - nodes in this community are weakly interconnected._