---
name: core-mental-model-engine
id: "core-mental-model-engine"
layer: "L0"
name_zh: "思维框架引擎"
name_en: "Mental Model Engine"
version: "1.4.0"
description: 根据当前决策场景，从18个心智模型中选择匹配模型，输出结构化推理链。v1.4.0场景映射扩展至9场景(user_interaction/industry_adaptation/conflict_resolution)。全程内化运行，不向用户解释模型本身。
agent_created: true
trigger_keywords: ["core-mental-model-engine", "心智模型引擎", "L0推理引擎"]
dependencies: []
---

# 思维框架引擎 (Mental Model Engine)

> **层级**: L0 | **版本**: 1.4.0 | **ID**: `core-mental-model-engine`
> **编排关系**: 本skill由 `team-orchestrator` 按需自动加载执行，属于全域专家团构建skills系统的内部组件，用户不应直接触发。

## 概述

根据当前决策场景，从18个心智模型中选择匹配模型，输出结构化推理链。全程内化运行，不向用户解释模型本身，体现在提问深度、方案严谨度和输出结构中。

## 触发条件

当检测到以下关键词或场景时自动激活：推理, 决策, 分析, 判断, 为什么, 推理链, 思维模型

## 输入规范 (input_schema)

```json
{
  "type": "object",
  "properties": {
    "scene": {
      "type": "string",
      "enum": [
        "need_analysis",
        "architecture",
        "compliance",
        "quality",
        "degradation",
        "domain_adaptation",
        "user_interaction",
        "industry_adaptation",
        "conflict_resolution"
      ],
      "description": "决策场景类型"
    },
    "context": {
      "type": "string",
      "description": "当前对话上下文和阶段状态"
    },
    "decision_point": {
      "type": "string",
      "description": "具体决策问题描述"
    }
  },
  "required": [
    "scene",
    "context",
    "decision_point"
  ]
}
```

## 输出规范 (output_schema)

```json
{
  "type": "object",
  "properties": {
    "model_used": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "激活的心智模型列表"
    },
    "reasoning_chain": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "因为...所以...的推理路径"
    },
    "conclusion": {
      "type": "string",
      "description": "推理结论"
    },
    "confidence": {
      "type": "string",
      "enum": [
        "high",
        "medium",
        "low"
      ],
      "description": "置信度"
    }
  },
  "required": [
    "model_used",
    "reasoning_chain",
    "conclusion",
    "confidence"
  ]
}
```

## 工具声明 (tool_declarations)

本Skill无外部工具依赖，纯提示词可执行。

## 18心智模型×激活场景完整映射表

| # | 模型 | 定义 | 激活场景 | 使用约束 |
|---|---------|------|---------|---------|
| 1 | 交付物倒推 | 从终端交付物反推所需角色、能力和工具 | S4锚定、S5架构设计 | 必须在角色定义之前完成交付物定义 |
| 2 | 反向思维 | 从失败/最坏情况倒推防护策略 | 降级决策、失败模式预演 | 不得单独使用，需配合正向推理 |
| 3 | 系统思维 | 识别系统各要素间的因果和反馈关系 | S5架构设计、数据流设计 | 必须画出完整数据流 |
| 4 | MECE结构化 | 互斥且穷尽地划分 | S5角色划分、5.2角色层自检 | 三问必须全部通过 |
| 5 | CoT链式推理 | 逐步展示推理过程 | 每阶段推理过程展示 | 每个核心决策点必须展示推理路径 |
| 6 | ToT思维树 | 并行探索多条推理路径 | 多方案比较、歧义消解 | 至少比较2条路径才能做决策 |
| 7 | 产品思维 | 以用户价值和产品可行性为判断基准 | S4交付物定义、用户层自检 | 不得脱离用户需求做纯技术优化 |
| 8 | 用户思维 | 从终端用户视角审视所有产出 | 5.6用户层自检、话术设计 | 所有用户可见内容必须通过用户思维审视 |
| 9 | 5-Why根因分析 | 连续追问5层"为什么"找到根因 | 需求深潜S1、故障归因 | 最多3轮追问 |
| 10 | 第一性原理 | 回到最基本的事实重新推理 | 领域消歧S2、复杂度评估 | 必须从事实出发 |
| 11 | 反脆弱 | 设计使系统从冲击中获益的机制 | 降级策略设计、异常处理 | 必须设计恢复路径 |
| 12 | 批判思维 | 对每个结论寻找反驳证据 | 合规审查、质量自检 | 不得接受未经审视的结论 |
| 13 | 领域适配思维 | 根据领域特性调整策略和方法 | S2领域分类、条件激活逻辑 | 必须先确认领域类型 |
| 14 | 合规思维 | 以合规为不可绕过的硬约束 | 全部合规协议 | 合规不可降级 |
| 15 | 辩证思维 | 在对立观点中寻找更高层次的综合 | P0/P1问题修复、矛盾消解 | 不得取折中，必须找到综合方案 |
| 16 | ReAct | 推理-行动交替循环 | 8阶段交互流程 | 每个行动后必须观察结果再推理 |
| 17 | 数据安全思维 | 以数据安全为设计前提 | 数据安全层、高敏感度领域 | 禁止敏感数据外发 |
| 18 | 平台工程思维 | 以平台能力边界为设计约束 | S7/S8平台适配 | 必须验证平台可行性才能输出 |

## 执行逻辑

根据决策场景类型选择激活的心智模型子集：
(1) need_analysis → 5-Why + 第一性原理
(2) architecture → 交付物倒推 + 系统思维 + MECE + ToT + 平台工程思维
(3) compliance → 批判思维 + 合规思维 + 辩证思维
(4) quality → 5-Why + 批判思维 + 反向思维
(5) degradation → 反脆弱 + 反向思维
(6) domain_adaptation → 领域适配思维 + 产品思维
(7) user_interaction → 用户思维 + 产品思维 + CoT链式推理（v1.4.0新增）
(8) industry_adaptation → 领域适配思维 + 第一性原理 + 批判思维（v1.4.0新增）
(9) conflict_resolution → 辩证思维 + 批判思维 + 第一性原理（v1.4.0新增）

18心智模型清单：
1.交付物倒推 2.反向思维 3.系统思维 4.MECE结构化 5.CoT链式推理
6.ToT思维树 7.产品思维 8.用户思维 9.5-Why根因分析 10.第一性原理
11.反脆弱 12.批判思维 13.领域适配思维 14.合规思维 15.辩证思维
16.ReAct 17.数据安全思维 18.平台工程思维

核心约束：不向用户解释思维模型本身；体现在提问深度、方案严谨度、输出结构中；每个核心决策点展示推理路径(CoT)

## Few-shot 示例

### 示例 1

**输入**:
```json
{
  "scene": "architecture",
  "context": "用户需要构建小红书内容团队",
  "decision_point": "角色划分方案选择"
}
```

**输出**:
```json
{
  "model_used": [
    "交付物倒推",
    "MECE结构化",
    "系统思维"
  ],
  "reasoning_chain": [
    "1.先确定终端交付物(小红书图文+私域话术)",
    "2.每个交付物分配唯一第一责任人",
    "3.从交付物反推能力→定义角色",
    "4.MECE三问校验覆盖性/独立性/唯一性"
  ],
  "conclusion": "推荐3角色Team型架构：视觉角色+文案角色+合规审查员",
  "confidence": "high"
}
```

### 示例 2

**输入**:
```json
{
  "scene": "compliance",
  "context": "A型内容传播领域，涉及医疗健康科普",
  "decision_point": "内容合规审查标准"
}
```

**输出**:
```json
{
  "model_used": [
    "合规思维",
    "批判思维",
    "5-Why根因分析"
  ],
  "reasoning_chain": [
    "1.医疗健康属强监管行业",
    "2.5-Why追问：为什么需要合规→避免误导患者→可能违法→必须审查",
    "3.批判思维：列出10项检查清单"
  ],
  "conclusion": "激活4.1-4.5全协议，禁用词下限≥8个",
  "confidence": "high"
}
```

### 示例 3

**输入**:
```json
{
  "scene": "degradation",
  "context": "工具链中ComfyUI不可用，需要视觉产出降级方案",
  "decision_point": "视觉产出降级策略"
}
```

**输出**:
```json
{
  "model_used": [
    "反脆弱",
    "反向思维",
    "平台工程思维"
  ],
  "reasoning_chain": [
    "1.反向思维：假设视觉产出完全失败→纯文字+占位图",
    "2.反脆弱：3档降级策略使系统在工具不可用时仍能运行",
    "3.从最坏倒推：无工具→纯描述→手动+快照→完整自动化",
    "4.平台工程思维：验证每档降级可行性"
  ],
  "conclusion": "3档降级：ComfyUI可用→手动生成→纯描述占位",
  "confidence": "medium"
}
```

## 知识库挂载点 (knowledge_base_mount_points)


> **⚠️ 挂载点说明**：以下 `file://` 路径为概念性挂载点（conceptual mount points），用于声明本 skill 的知识库依赖结构。它们不是物理文件路径，不需要实际加载文件。执行时请直接依据本 SKILL.md 正文中的规则定义和伪代码逻辑工作。
- **[static]** `file://mental-models/18-models-definitions` — 18心智模型定义与激活映射表
- **[static]** `file://mental-models/failure-modes` — 8类失败模式预枚举
- **[dynamic]** `file://stage-context/current-decisions` — 当前阶段决策上下文

## 依赖关系

无前置依赖。

## 18心智模型完整定义

| 模型 | 定义 | 激活场景 |
| --- | --- | --- |
| 交付物倒推 | 先定义终端交付物，再倒推角色、能力、工具和数据流；禁止先按职位想角色。 | S4/S5/专家包结构设计 |
| 反向思维 | 从失败、误用、无法交付的终点倒推风险和阻断点。 | 降级决策、失败模式预演 |
| 系统思维 | 把角色、工具、数据、反馈看成相互制约的系统。 | S5数据流、S7全局机制 |
| MECE结构化 | 确保覆盖完整、职责独立、责任唯一。 | 角色划分、质量自检 |
| CoT链式推理 | 用因果链记录关键判断，必须能追溯到输入字段。 | 每个核心决策点 |
| ToT思维树 | 并行比较多个可行方案，再按维度收敛。 | 歧义消解、多方案架构比较 |
| 产品思维 | 关注用户能否理解、采用、持续使用交付物。 | S4交付物定义、S8交付确认 |
| 用户思维 | 用用户熟悉语言解释抽象概念，降低交互负担。 | S1提问、用户层自检 |
| 5-Why根因分析 | 最多三轮追问表层需求背后的真实目标。 | 需求深潜、故障归因 |
| 第一性原理 | 拆到不可再拆的事实、约束和目标。 | 领域消歧、复杂度评估 |
| 反脆弱 | 提前设计失败后如何降级、恢复、学习。 | 异常处理、自动化触发 |
| 批判思维 | 主动寻找反例、漏洞、未经验证的断言。 | 合规审查、质量门控 |
| 领域适配思维 | 按A-F领域类型激活不同协议和反馈回路。 | S2分类、S5反馈设计 |
| 合规思维 | 按法规、平台规则、服务规则、品牌规则排序检查。 | 内容和行业合规 |
| 辩证思维 | 处理速度与质量、自动化与人工审批等冲突。 | 通道选择、修复优先级 |
| ReAct | 每阶段观察输入、执行动作、检查结果、推进或回退。 | 八阶段流程 |
| 数据安全思维 | 最小化数据暴露，标注流向和敏感等级。 | S6工具链、S7机制 |
| 平台工程思维 | 把同一逻辑落成目标平台可导入文件和配置。 | L3适配、S8执行 |

```text
FUNCTION select_mental_models(scene, context, decision_point):
    ASSERT scene IN [need_analysis, architecture, compliance, quality, degradation, domain_adaptation]
    candidate_models = map_scene_to_models(scene)
    IF decision_point contains multi_option_choice:
        candidate_models.append("ToT思维树")
    IF context contains regulated_domain:
        candidate_models.extend(["合规思维", "批判思维"])
    IF context contains tool_or_platform_failure:
        candidate_models.extend(["反脆弱", "平台工程思维"])
    reasoning_chain = []
    FOR model IN unique(candidate_models):
        step = apply_model_without_explaining_model_name(model, context, decision_point)
        reasoning_chain.append(step)
    ASSERT reasoning_chain references input facts
    RETURN {model_used, reasoning_chain, conclusion, confidence}
```

## 详细执行逻辑

```text
FUNCTION activate_mental_models(context, decision_point):

    # === 18心智模型注册表 ===
    models = {
        "deliverable_backward": "§2.1 交付物倒推",
        "reverse_thinking": "§2.2 逆向思维",
        "systems_thinking": "§2.3 系统思维",
        "structured_mece": "§2.4 结构化MECE",
        "chain_of_thought": "§2.5 思维链",
        "tree_of_thought": "§2.6 思维树",
        "product_thinking": "§2.7 产品思维",
        "user_thinking": "§2.8 用户思维",
        "five_why": "§2.9 5-Why",
        "first_principles": "§2.10 第一性原理",
        "antifragile": "§2.11 反脆弱",
        "critical_thinking": "§2.12 批判思维",
        "domain_adaptation": "§2.13 领域适配",
        "compliance_thinking": "§2.14 合规思维",
        "dialectical": "§2.15 辩证思维",
        "react_framework": "§2.16 ReAct",
        "data_security": "§2.17 数据安全",
        "platform_engineering": "§2.18 平台工程"
    }

    # === Step 1: 按决策点类型选择激活的模型子集 ===
    IF decision_point.type == "architecture_design":
        ACTIVATE: deliverable_backward, systems_thinking, structured_mece,
                  tree_of_thought, platform_engineering
    ELIF decision_point.type == "risk_assessment":
        ACTIVATE: reverse_thinking, antifragile, critical_thinking, compliance_thinking
    ELIF decision_point.type == "user_interaction":
        ACTIVATE: user_thinking, five_why, chain_of_thought
    ELIF decision_point.type == "domain_analysis":
        ACTIVATE: domain_adaptation, first_principles, five_why
    ELIF decision_point.type == "conflict_resolution":
        ACTIVATE: dialectical, first_principles, critical_thinking
    ELIF decision_point.type == "quality_check":
        ACTIVATE: five_why, critical_thinking, reverse_thinking
    ELIF decision_point.type == "degradation":
        ACTIVATE: antifragile, reverse_thinking, platform_engineering
    ELIF decision_point.type == "compliance_review":
        ACTIVATE: compliance_thinking, critical_thinking, dialectical
    ELSE:
        ACTIVATE: ALL (full spectrum reasoning)

    # === Step 2: 上下文补充激活 ===
    IF context contains regulated_domain:
        EXTEND: compliance_thinking, critical_thinking
    IF context contains multi_option_choice:
        EXTEND: tree_of_thought
    IF context contains tool_or_platform_failure:
        EXTEND: antifragile, platform_engineering
    IF context contains user_ambiguity:
        EXTEND: user_thinking, five_why
    IF context contains data_sensitivity:
        EXTEND: data_security

    # === Step 3: 核心行为约束（内化，不向用户解释模型本身）===
    CONSTRAINT: 不向用户解释思维模型本身
    CONSTRAINT: 体现在提问深度、方案严谨度、输出结构中
    CONSTRAINT: 每个核心决策点展示推理路径（CoT）

    # === Step 4: 推理链构建 ===
    reasoning_chain = []
    FOR model IN unique(activated_models):
        step = apply_model_without_explaining_model_name(model, context, decision_point)
        reasoning_chain.append(step)

    # === Step 5: 置信度评估 ===
    IF all_evidence_supports(reasoning_chain):
        confidence = "high"
    ELIF contradictory_evidence_exists(reasoning_chain):
        confidence = "low"
        APPEND alternatives_from(tree_of_thought)
    ELSE:
        confidence = "medium"

    # === Step 6: 互斥模型处理 ===
    IF "compliance_thinking" IN activated AND "product_thinking" IN activated:
        # 合规优先原则：合规不可降级
        priority_order = ["compliance_thinking", "product_thinking"]
    IF "data_security" IN activated AND "domain_adaptation" IN activated:
        # 数据安全为硬约束
        priority_order = ["data_security", "domain_adaptation"]

    ASSERT reasoning_chain references input facts
    ASSERT NOT empty(reasoning_chain)

    RETURN {model_used, reasoning_chain, conclusion, confidence}


# === 子函数：按场景映射模型 ===
FUNCTION map_scene_to_models(scene):
    SCENE_MAP = {
        "need_analysis": ["five_why", "first_principles"],
        "architecture": ["deliverable_backward", "systems_thinking", "structured_mece", "tree_of_thought", "platform_engineering"],
        "compliance": ["compliance_thinking", "critical_thinking", "dialectical"],
        "quality": ["five_why", "critical_thinking", "reverse_thinking"],
        "degradation": ["antifragile", "reverse_thinking", "platform_engineering"],
        "domain_adaptation": ["domain_adaptation", "product_thinking", "first_principles"],
        "user_interaction": ["user_thinking", "product_thinking", "chain_of_thought"],
        "industry_adaptation": ["domain_adaptation", "first_principles", "critical_thinking"],
        "conflict_resolution": ["dialectical", "critical_thinking", "first_principles"]
    }
    RETURN SCENE_MAP.get(scene, ["chain_of_thought"])


# === 子函数：执行模型但不解释模型名 ===
FUNCTION apply_model_without_explaining_model_name(model, context, decision_point):
    # 模型效果体现在推理过程中，而非命名
    IF model == "deliverable_backward":
        step = "从终端交付物反推：" + identify_deliverables_first(context)
    ELIF model == "five_why":
        step = "追问根因：" + drill_root_cause(decision_point, max_rounds=3)
    ELIF model == "structured_mece":
        step = "MECE校验：" + verify_coverage_independence_uniqueness(context)
    ELIF model == "reverse_thinking":
        step = "从失败倒推：" + identify_failure_first(context, decision_point)
    ELIF model == "systems_thinking":
        step = "系统因果分析：" + map_causal_loops(context)
    ELIF model == "antifragile":
        step = "降级恢复设计：" + design_degradation_with_recovery(context)
    ELIF model == "compliance_thinking":
        step = "合规硬约束检查：" + check_compliance_as_hard_constraint(context)
    ELIF model == "critical_thinking":
        step = "主动寻找反例：" + find_counter_evidence(decision_point)
    ELIF model == "dialectical":
        step = "对立观点综合：" + synthesize_opposing_views(context, decision_point)
    ELIF model == "tree_of_thought":
        step = "多方案并行探索：" + explore_parallel_paths(context, min_paths=2)
    ELIF model == "platform_engineering":
        step = "平台可行性验证：" + verify_platform_feasibility(context)
    ELIF model == "data_security":
        step = "数据安全边界确认：" + confirm_data_security_boundary(context)
    ELSE:
        step = apply_generic_reasoning(model, context, decision_point)

    RETURN step


# === 执行入口 ===
FUNCTION execute_core_mental_model_engine(input):
    ASSERT input.scene IN ["need_analysis", "architecture", "compliance", "quality", "degradation", "domain_adaptation", "user_interaction", "industry_adaptation", "conflict_resolution"]
    ASSERT input.context IS NOT EMPTY
    ASSERT input.decision_point IS NOT EMPTY

    # 加载上下文继承
    LOAD context_inheritance FROM shared_memory

    # 执行核心逻辑
    result = activate_mental_models(input.context, {
        "type": input.scene,
        "specific_question": input.decision_point
    })

    # 强制调用：质量门控（仅在产出方案前）
    IF result.confidence IN ["low", "medium"]:
        // 质量门控由编排器统一调用（避免递归）

    # 构建输出
    BUILD output ACCORDING TO output_schema WITH result

    RETURN output
```

## 版本

1.4.0

---
*本Skill由全域专家团构建skills体系生成，版本1.4.0，日期2026-06-17*
