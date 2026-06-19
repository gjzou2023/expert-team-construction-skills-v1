---
name: pipeline-s7-expert-package-generation
id: "pipeline-s7-expert-package-generation"
layer: "L1"
name_zh: "阶段七：专家包生成"
name_en: "Stage 7: Expert Package Generation"
version: "1.4.0"
description: 生成专家包概览、按目标平台格式生成配置、嵌入全局机制、生成执行计划、四步确认门。v1.4.0新增快速通道字段回填机制、展示格式弹性规则，整合确认步骤。字段追踪强制。按需条件激活L2协议和L3适配器。
agent_created: true
trigger_keywords: ["S7执行", "专家包生成", "四步确认门", "平台配置生成", "专家包导出"]
dependencies: ["core-mental-model-engine", "core-deliverable-backward-engine"]
conditional_dependencies: {
  "说明": "I-2.9修复: L2协议和L3适配器根据activation_context按需激活，不在depends_on中硬声明。activation_map定义在外部knowledge/protocol-activation-map.json。",
  "L2_protocol_activation": "按外部knowledge/protocol-activation-map.json的domain_type和compliance_activation_map条件激活",
  "L3_adapter_activation": "仅激活platform对应的单个L3适配器"
}
---

# 阶段七：专家包生成 (Stage 7: Expert Package Generation)

> **层级**: L1 | **版本**: 1.4.0 | **ID**: `pipeline-s7-expert-package-generation`
> **编排关系**: 本skill由 `team-orchestrator` 自动加载执行，用户不应直接触发。承接 `pipeline-s6-toolchain-matching` 的输出，完成后自动衔接 `pipeline-s8-platform-execution`。此阶段按激活矩阵自动激活L2协议子集和L3平台适配器。

## 概述

生成专家包概览、按目标平台格式生成配置、嵌入全局机制、生成执行计划、最终确认四步确认门。v1.3.0新增专家团组建可视化确认步骤。字段追踪强制。

## 触发条件

当检测到以下关键词或场景时自动激活：专家包, 生成, 打包, 确认, 四步确认门, 导出

## 输入规范 (input_schema)

```json
{
  "type": "object",
  "properties": {
    "s5_outputs": {
      "type": "object",
      "description": "S5架构输出(roles/sop/data_flow/feedback_loops/cold_start)"
    },
    "s6_outputs": {
      "type": "object",
      "description": "S6工具链输出(tool_matrix/integration_specs/degradation_plan)"
    },
    "platform": {
      "type": "string"
    },
    "team_type": {
      "type": "string",
      "enum": [
        "team",
        "agent"
      ]
    },
    "activation_context": {
      "type": "object",
      "description": "运行时条件激活上下文，用于按需激活L2协议和L3适配器",
      "properties": {
        "domain_type": {
          "type": "string",
          "description": "主领域类型(A-F)，用于按activation_map激活L2协议"
        },
        "secondary_domains": {
          "type": "array",
          "items": {"type": "string"},
          "description": "次领域类型列表，用于混合型场景的协议并集激活"
        },
        "market": {
          "type": "string",
          "enum": ["domestic", "overseas", "global"],
          "description": "目标市场，影响合规协议激活"
        },
        "platform": {
          "type": "string",
          "description": "目标平台，仅激活对应的单个L3适配器"
        },
        "is_regulated": {
          "type": "boolean",
          "description": "是否为强监管领域，影响合规+审批+数据安全协议激活"
        },
        "compliance_requirements": {
          "type": "object",
          "description": "合规激活映射，来自S2输出的compliance_activation_map"
        }
      }
    }
  },
  "required": [
    "s5_outputs",
    "s6_outputs",
    "platform",
    "team_type",
    "activation_context"
  ]
}
```

## 输出规范 (output_schema)

```json
{
  "type": "object",
  "properties": {
    "expert_package": {
      "type": "object"
    },
    "execution_plan": {
      "type": "object"
    },
    "final_confirmation": {
      "type": "object"
    }
  },
  "required": [
    "expert_package",
    "execution_plan",
    "final_confirmation"
  ]
}
```

## 工具声明 (tool_declarations)

本Skill无外部工具依赖，纯提示词可执行。

## 执行逻辑

(0)专家团组建可视化确认→(1)生成专家包概览(7.1)→(2)按目标平台格式生成各专家配置(7.2,调用L3平台适配层)→(3)嵌入全局机制(7.3:质量门控/信息准确性/合规/数据安全/异常处理/反馈闭环/知识沉淀/审批)→(4)生成执行计划(7.4)→(5)四步确认门(7.5):步骤0专家团确认→①内部一致性检查→②用户结构确认→③用户批准。字段追踪(§6.1#7)：引用前序阶段产出时，必须保证字段一一对应。快速通道字段回填（v1.4.0新增）：被跳过阶段字段自动回填并标注来源。确认步骤整合（v1.4.0）：步骤0与三步门合并为四步确认门，避免重复交互。

### 步骤0：专家团组建可视化确认（v1.3.0新增）

在正式生成专家包之前，展示初步推荐的专家团名单及选择理由：

1. 展示推荐名单：每位专家的角色名、职责一句话、选择理由
2. 允许用户：
   - 增加/删除特定角色（"再加一个法律顾问" / "去掉SEO专家"）
   - 调整某位专家的权重/侧重（"合规专家权重提到最高"）
   - 指定特定约束（如"必须有法规合规角色"、"不要超过5个角色"）
3. 用户确认后再启动后续生成流程

### 展示格式模板

```
初步推荐的专家团名单：

| 角色 | 职责 | 选择理由 |
|------|------|---------|
| [角色1] | [职责一句话] | [理由] |
| [角色2] | [职责一句话] | [理由] |
| ... | ... | ... |

你可以：
- 回复"确认"开始生成
- 回复"增加XXX专家"或"去掉YYY专家"调整
- 回复"合规权重优先"等调整侧重

确认后我将自动生成专家包。
```

### 展示格式弹性规则（v1.4.0新增）

- 角色数≤4：使用完整表格（角色/职责/选择理由三列）
- 角色数5-6：使用精简表格（角色/职责两列+选择理由折叠）
- 角色数≥7：使用分组展示（按"核心角色/合规角色/支撑角色"分组，每组2-3行摘要）

## Few-shot 示例

### 示例1: 正常流程 - A型内容团队专家包生成

**输入**:
```json
{
  "s5_outputs": {
    "roles": [
      {"name": "content-strategist", "one_line_duty": "选题策划+内容创作+平台适配"},
      {"name": "compliance-reviewer", "one_line_duty": "内容合规审查"}
    ],
    "sop": {"team_type": "team", "schedule": "weekly"},
    "data_flow": "选题→创作→审核→发布→数据反馈→选题(闭环)",
    "feedback_loops": ["内容效果反馈", "合规审查"],
    "cold_start": "1周内从0到首次发布"
  },
  "s6_outputs": {
    "tool_matrix": [{"role": "content-strategist", "tools": ["WebSearch", "ImageGen"]}],
    "integration_specs": {"platform": "workbuddy", "format": "JSON-config"},
    "degradation_plan": "WebSearch不可用时使用本地知识库"
  },
  "platform": "workbuddy",
  "team_type": "team",
  "activation_context": {
    "domain_type": "A",
    "secondary_domains": [],
    "channel": "standard",
    "market": "domestic",
    "platform": "workbuddy",
    "is_regulated": false,
    "compliance_requirements": {}
  }
}
```

**输出**:
```json
{
  "expert_package": {
    "overview": "ExpertTeam_小食光内容团队_v1.0.0",
    "platform_config": {
      "workbuddy": {
        "roles": ["content-strategist", "compliance-reviewer"],
        "sop_hooks": {
          "daily_standup": "auto_trigger_at_09:00",
          "weekly_review": "manual_trigger"
        },
        "global_mechanisms": {
          "quality_gate": "pre_publish_review",
          "compliance": "auto_check_content",
          "data_security": "local_only",
          "feedback_loop": "weekly_content_performance_report"
        }
      }
    }
  },
  "execution_plan": {
    "step_1": "部署 roles 配置到 WorkBuddy",
    "step_2": "配置 daily_standup 触发器",
    "step_3": "首次运行 cold_start 流程",
    "step_4": "1周后产出首篇内容"
  },
  "final_confirmation": {
    "self_check": "internal_consistency=✅, field_tracing=✅, compliance=✅",
    "user_structure_review": "请确认角色/SOP/反馈机制",
    "user_approval": "等待用户回复'批准'或'确认'"
  }
}
```

### 示例2: 异常流程 - F型客服专家包(含强合规)

**输入**:
```json
{
  "s5_outputs": {
    "roles": [
      {"name": "triage-agent", "one_line_duty": "一级分流+FAQ匹配"},
      {"name": "senior-service-agent", "one_line_duty": "复杂问题处理+升级"},
      {"name": "compliance-guardian", "one_line_duty": "所有输出合规审查"}
    ],
    "sop": {"team_type": "agent", "schedule": "always_on"},
    "data_flow": "客户问题→一级分流→FAQ匹配/复杂处理→回复生成→合规审查→发送→满意度追踪(闭环)",
    "feedback_loops": ["响应时间", "满意度", "合规命中率", "升级率"],
    "cold_start": "加载FAQ知识库+话术模板"
  },
  "s6_outputs": {
    "tool_matrix": [
      {"role": "triage-agent", "tools": ["protocol-single-question-guidance"]},
      {"role": "compliance-guardian", "tools": ["protocol-compliance-engine"]}
    ],
    "integration_specs": {"platform": "dify", "format": "Dify-workflow"},
    "degradation_plan": "所有客服回复必须经人工审核后才能发送"
  },
  "platform": "dify",
  "team_type": "agent",
  "activation_context": {
    "domain_type": "F",
    "secondary_domains": [],
    "channel": "strict",
    "market": "domestic",
    "platform": "dify",
    "is_regulated": true,
    "compliance_requirements": {
      "4.1": {"level": "warning"},
      "4.4": {"level": "mandatory"},
      "4.5": {"level": "warning"}
    }
  }
}
```

**输出**:
```json
{
  "expert_package": {
    "overview": "ExpertTeam_智能客服_v1.0.0",
    "platform_config": {
      "dify": {
        "roles": ["triage-agent", "senior-service-agent", "compliance-guardian"],
        "sop_hooks": {
          "always_on": "continuous_service"
        },
        "global_mechanisms": {
          "quality_gate": "pre_send_review_by_compliance_guardian",
          "compliance": "4.1_4.2_4.3_4.4_4.5_full",
          "data_security": "PII_masking_mandatory",
          "human_approval": "price_quote_or_dispute_requires_human",
          "feedback_loop": "real_time_satisfaction_CSAT"
        }
      }
    }
  },
  "execution_plan": {
    "step_1": "导入FAQ知识库到Dify知识库",
    "step_2": "配置Dify工作流: triage→senior→compliance",
    "step_3": "加载合规词库(禁用词≥10个)",
    "step_4": "灰度测试: 先处理10%流量"
  },
  "final_confirmation": {
    "self_check": "internal_consistency=✅, compliance_full=✅, degradation=✅",
    "user_structure_review": "请确认3角色分工/合规协议全激活/人工审批条件",
    "user_approval": "等待用户回复'批准'或'确认'"
  }
}
```

### 示例3: 快速通道 - 单人财税科普号精简专家包

**输入**:
```json
{
  "s5_outputs": {
    "roles": [
      {"name": "solo-operator", "one_line_duty": "选题+创作+发布全流程"}
    ],
    "sop": {"team_type": "agent", "schedule": "daily"},
    "data_flow": "选题→创作→发布(精简)",
    "feedback_loops": ["内容效果"],
    "cold_start": "即日启动，3天后首篇"
  },
  "s6_outputs": {
    "tool_matrix": [{"role": "solo-operator", "tools": ["纯提示词"]}],
    "integration_specs": {"platform": "workbuddy", "format": "单Agent提示词"},
    "degradation_plan": "纯提示词模式，无外部依赖"
  },
  "platform": "workbuddy",
  "team_type": "agent",
  "activation_context": {
    "domain_type": "A",
    "secondary_domains": [],
    "channel": "fast",
    "market": "domestic",
    "platform": "workbuddy",
    "is_regulated": false,
    "compliance_requirements": {
      "4.1": {"level": "warning"}
    }
  }
}
```

**输出**:
```json
{
  "expert_package": {
    "overview": "Expert_财税科普号_v1.0.0(fast)",
    "platform_config": {
      "workbuddy": {
        "single_agent_prompt": "你是一个财税科普内容创作者...",
        "global_mechanisms": {
          "quality_gate": "pre_publish_self_review",
          "compliance": "auto_check_4.1_4.3",
          "feedback_loop": "weekly_content_performance_report"
        }
      }
    }
  },
  "execution_plan": {
    "step_1": "复制提示词到WorkBuddy",
    "step_2": "测试生成一篇财税科普",
    "step_3": "调优后正式启用"
  },
  "final_confirmation": {
    "self_check": "single_role=✅, fast_channel=✅, pure_prompt=✅",
    "user_structure_review": "单人纯提示词模式，请确认",
    "user_approval": "等待用户回复'批准'或'确认'"
  }
}
```

## 知识库挂载点 (knowledge_base_mount_points)


> **⚠️ 挂载点说明**：以下 `file://` 路径为概念性挂载点（conceptual mount points），用于声明本 skill 的知识库依赖结构。它们不是物理文件路径，不需要实际加载文件。执行时请直接依据本 SKILL.md 正文中的规则定义和伪代码逻辑工作。
- **[static]** `file://./knowledge/stage-7-rules.md` — 阶段7执行规则
- **[static]** `file://./knowledge/protocol-activation-map.json` — L2协议激活映射矩阵（I-2.9新增外部化）
- **[dynamic]** `file://./knowledge/stage-7-state.json` — 阶段7运行时状态

## 依赖关系

- `core-mental-model-engine` (硬依赖)
- `core-deliverable-backward-engine` (硬依赖)
- L2协议：按`activation_context`条件激活，不在`depends_on`中硬声明
- L3适配器：仅激活`platform`对应的单个适配器，不在`depends_on`中硬声明

## 快速通道字段回填机制（v1.4.0新增）

当快速通道跳过S3(链路拆解)和S5(架构设计)时，S7的字段追踪需要回填缺失字段：

| 缺失字段 | 回填策略 | 回填来源 |
|---------|---------|---------|
| chain_decomposition(S3输出) | 自动生成简化链路图：交付物→能力→工具→输出 | S4交付物清单+核心角色定义 |
| role_definitions(S5输出) | 内联生成：每个交付物分配1个角色，能力从交付物反推 | S4交付物清单+S2领域类型默认角色集 |
| feedback_loops(S5输出) | 按领域类型使用默认反馈回路 | core-domain-classifier的领域默认反馈 |
| sop_phases(S5输出) | 使用领域默认SOP模板 | A型5阶段/B型6阶段/C型6阶段等 |
| data_flow(S5输出) | 使用线性数据流：输入→处理→输出 | S4交付物规格 |

### 回填校验
- 回填字段标注为[快速通道自动生成]
- 在三步门的格式门中增加"回填字段覆盖检查"
- 若回填覆盖率<80%，提示用户"快速通道可能遗漏关键设计，建议升级至标准通道"

## 详细执行逻辑

```text
FUNCTION execute_pipeline_s7_expert_package_generation(input):
    # ===== 阶段七：专家包生成 - 入口校验 =====
    ASSERT input.s5_outputs EXISTS
    ASSERT input.s6_outputs EXISTS
    ASSERT input.platform IS NOT EMPTY
    ASSERT input.team_type IN ["team", "agent"]
    LOAD context_inheritance FROM s5, s6

    s5_data = input.s5_outputs
    s6_data = input.s6_outputs
    # I-2.3修复：从 context_inheritance 加载全部前序阶段数据，确保字段追踪可访问
    s1_data = context_inheritance.s1_outputs
    s2_data = context_inheritance.s2_outputs
    s3_data = context_inheritance.s3_outputs
    s4_data = context_inheritance.s4_outputs
    platform = input.platform
    team_type = input.team_type
    roles = s5_data.roles
    # 改进#13修复: domain_type从activation_context获取(而非s5_data，因S5 output_schema无此字段)
    domain_type = input.activation_context.domain_type IF EXISTS ELSE "A"

    # ===== 步骤0: 专家团组建可视化确认(改进#15: 集成到主流程作为四步确认门第一步) =====
    preliminary_team = OUTPUT_PRELIMINARY_TEAM_RECOMMENDATION(roles)
    OUTPUT preliminary_team TO user
    team_confirm = WAIT_FOR_USER()
    IF team_confirm CONTAINS "增加" OR team_confirm CONTAINS "去掉" OR team_confirm CONTAINS "调整":
        roles = APPLY_TEAM_MODIFICATIONS(team_confirm, roles)
        OUTPUT_PRELIMINARY_TEAM_RECOMMENDATION(roles)
        team_confirm = WAIT_FOR_USER()
    ASSERT team_confirm IN ["确认", "批准", "继续"]

    # ===== 步骤1: 按需条件激活L2协议(改进：从全量硬依赖改为按需激活) =====
    activation_ctx = input.activation_context
    # I-2.9修复: 显式加载外部协议激活映射文件，替代概念性引用
    activation_map = LOAD("knowledge/protocol-activation-map.json")
    L2_PROTOCOLS = RESOLVE_L2_PROTOCOLS(activation_ctx, activation_map)

    # 改进#7修复: RESOLVE_L2_PROTOCOLS真实矩阵查询实现
    FUNCTION RESOLVE_L2_PROTOCOLS(activation_ctx, activation_map):
        # 构造矩阵查询key: {domain}_{channel}_{stage}
        primary_domain = activation_ctx.domain_type
        channel = activation_ctx.channel OR "standard"  # 默认standard
        stage = "S7"  # 当前阶段固定

        # 优先按primary_domain查询
        matrix_key = primary_domain + "_" + channel + "_" + stage
        IF matrix_key IN activation_map.protocol_activation_matrix:
            base_protocols = activation_map.protocol_activation_matrix[matrix_key]
        ELSE:
            base_protocols = activation_map.protocol_activation_matrix["_fallback"]

        # 混合型: 取secondary_domains对应协议的并集
        IF activation_ctx.secondary_domains EXISTS AND LENGTH(activation_ctx.secondary_domains) > 0:
            FOR sd IN activation_ctx.secondary_domains:
                sd_key = sd + "_" + channel + "_" + stage
                IF sd_key IN activation_map.protocol_activation_matrix:
                    base_protocols = base_protocols + activation_map.protocol_activation_matrix[sd_key]
            base_protocols = UNIQUE(base_protocols)  # 去重

        # 强监管场景额外激活合规协议
        IF activation_ctx.is_regulated:
            base_protocols = base_protocols + [
                "protocol-compliance-engine",
                "protocol-human-approval",
                "protocol-data-security"
            ]

        # 海外场景额外激活数据安全
        IF activation_ctx.market IN ["overseas", "global"]:
            base_protocols = base_protocols + ["protocol-data-security", "protocol-compliance-engine"]

        # 始终加载核心协议
        base_protocols = base_protocols + [
            "protocol-quality-gate",
            "protocol-confirmation-node",
            "protocol-error-handling"
        ]

        RETURN UNIQUE(base_protocols)

    protocol_bindings = {}
    FOR protocol IN L2_PROTOCOLS:
        protocol_bindings[protocol] = BIND_PROTOCOL_TO_ROLES(protocol, roles)

    # ===== 步骤2: 按platform参数条件激活L3适配器(改进：仅激活目标平台的单个适配器) =====
    L3_ADAPTERS = {
        "workbuddy": ["spawn-SendMessage", "Agent协作模式", "Markdown输出格式", "内置MCP支持"],
        "codex": ["CLI执行模式", "文件系统操作", "Git集成", "终端输出格式"],
        "hermes": ["多模态输出", "Webhook回调", "流式响应", "REST API集成"],
        "feishu": ["飞书消息卡片", "飞书文档集成", "飞书审批流", "飞书机器人API"],
        "n8n": ["工作流节点定义", "触发器配置", "数据映射", "条件分支"],
        "comfyui": ["节点图定义", "输入输出插槽", "模型加载配置", "批处理设置"],
        "coze": ["Coze工作流", "插件配置", "知识库挂载", "触发器设置"],
        "dify": ["Dify工作流", "知识库API", "对话变量", "Agent策略"]
    }
    # 仅激活用户选择的平台适配器，不再加载全部8个
    platform_adapter = L3_ADAPTERS[platform]
    adapter_config = {}
    FOR adapter_name IN platform_adapter:
        adapter_config[adapter_name] = GENERATE_ADAPTER_CONFIG(adapter_name, roles, team_type)

    # ===== 步骤3: 生成14必含章节专家包 =====
    REQUIRED_CHAPTERS = [
        "01_专家包概览",         # 包名/版本/团队类型/领域/平台
        "02_角色定义",           # 每个角色12项完整定义
        "03_协作模型",           # Team型/Agent型协作协议
        "04_SOP编排",           # 阶段定义/触发条件/数据流
        "05_数据流设计",         # 角色间数据传递Schema
        "06_反馈闭环",           # 按领域类型激活的反馈机制
        "07_质量门控",           # 产出质量验收规则
        "08_合规协议",           # 4.1-4.5合规条件激活
        "09_数据安全协议",       # 数据安全等级+流向+处理规则
        "10_异常处理",           # 8类失败模式+应对方案
        "11_知识资产沉淀",       # 知识库定义+更新机制
        "12_工具链配置",         # 工具矩阵+集成规范+降级方案
        "13_冷启动策略",         # 首次运行流程
        "14_执行计划"            # 分级启动方案
    ]
    expert_package = {}
    FOR chapter IN REQUIRED_CHAPTERS:
        chapter_content = GENERATE_CHAPTER(chapter, {
            "roles": roles,
            "domain_type": domain_type,
            "platform": platform,
            "team_type": team_type,
            "s5_data": s5_data,
            "s6_data": s6_data,
            "protocol_bindings": protocol_bindings,
            "adapter_config": adapter_config
        })
        expert_package[chapter] = chapter_content

    # ===== 步骤4: 角色定义章节特殊处理 =====
    # 按平台格式生成各专家配置
    # I-2.4修复：定义默认no-op对象，避免未激活协议访问KeyError
    # 改进#23修复: 伪函数语法统一为标准FUNCTION name(args): RETURN ...格式
    FUNCTION DEFAULT_QG_GET_FOR_ROLE(role): RETURN {"status": "auto", "check": "basic_consistency"}
    FUNCTION NOOP_COMPLIANCE_GET_FOR_ROLE(role): RETURN {"status": "inactive", "level": "none"}
    FUNCTION DEFAULT_DS_GET_FOR_ROLE(role): RETURN {"status": "local_only", "level": "basic"}
    FUNCTION DEFAULT_FL_GET_FOR_ROLE(role): RETURN {"status": "manual", "check": "basic_feedback"}
    FUNCTION DEFAULT_KS_GET_FOR_ROLE(role): RETURN {"status": "session_only", "persist": false}
    DEFAULT_QG = {"get_for_role": DEFAULT_QG_GET_FOR_ROLE}
    NOOP_COMPLIANCE = {"get_for_role": NOOP_COMPLIANCE_GET_FOR_ROLE}
    DEFAULT_DS = {"get_for_role": DEFAULT_DS_GET_FOR_ROLE}
    DEFAULT_FL = {"get_for_role": DEFAULT_FL_GET_FOR_ROLE}
    DEFAULT_KS = {"get_for_role": DEFAULT_KS_GET_FOR_ROLE}
    FOR role IN roles:
        role.platform_config = GENERATE_PLATFORM_ROLE_CONFIG(role, platform, adapter_config)
        # 嵌入全局机制到角色配置（使用安全访问，未激活协议自动降级为默认值）
        # 改进#6修复: protocol_bindings的key使用完整Skill ID
        role.global_mechanisms = {
            "quality_gate": protocol_bindings.get("protocol-quality-gate", DEFAULT_QG).get_for_role(role),
            "compliance": protocol_bindings.get("protocol-compliance-engine", NOOP_COMPLIANCE).get_for_role(role),
            "data_security": protocol_bindings.get("protocol-data-security", DEFAULT_DS).get_for_role(role),
            "feedback_loop": protocol_bindings.get("protocol-feedback-loop", DEFAULT_FL).get_for_role(role),
            "knowledge_sink": protocol_bindings.get("protocol-knowledge-persistence", DEFAULT_KS).get_for_role(role)
        }

    # ===== 步骤5: 字段追踪强制(§6.1#7) =====
    # 引用前序阶段产出时，必须保证字段一一对应
    FIELD_TRACING_MAP = {
        "s1.need_portrait": "s7.chapter_01.需求来源",
        "s2.confirmed_domain": "s7.chapter_01.领域类型",
        "s2.disambiguation_log": "s7.chapter_08.歧义消解记录",
        "s2.compliance_activation_map": "s7.chapter_08.合规激活映射",
        "s3.chain_nodes": "s7.chapter_05.数据流节点",
        "s4.deliverables": "s7.chapter_02.角色交付物",
        "s5.roles": "s7.chapter_02.角色定义",
        "s5.feedback_loops": "s7.chapter_06.反馈闭环",
        "s6.tool_matrix": "s7.chapter_12.工具链配置"
    }
    # 逐条验证字段追踪完整性
    FOR source_field IN FIELD_TRACING_MAP:
        target_field = FIELD_TRACING_MAP[source_field]
        source_value = RESOLVE_PATH(source_field, {s1: s1_data, s2: s2_data, s3: s3_data, s4: s4_data, s5: s5_data, s6: s6_data})
        target_value = RESOLVE_PATH(target_field, expert_package)
        ASSERT source_value IS_NOT_EMPTY OR target_value IS_NOT_EMPTY
        IF source_value IS_NOT_EMPTY AND target_value IS_EMPTY:
            RAISE "字段追踪断裂: " + source_field + " → " + target_field

    # ===== 步骤6: 质量门控 =====
    quality_check = CALL protocol-quality-gate(stage=7, output=expert_package)
    # 检查14章节完整性
    FOR chapter IN REQUIRED_CHAPTERS:
        ASSERT expert_package[chapter] IS_NOT_EMPTY
    # 检查角色定义完整性
    FOR role IN roles:
        ASSERT role HAS ALL_12_FIELDS
        ASSERT role.platform_config IS_NOT_EMPTY

    # ===== 步骤7: 合规检查 =====
    compliance_check = CALL protocol-compliance-engine(domain_type, expert_package)
    IF compliance_check.violations EXISTS:
        FOR violation IN compliance_check.violations:
            FIX_VIOLATION(violation, expert_package)
        # 修复后重新检查
        compliance_check = CALL protocol-compliance-engine(domain_type, expert_package)
        ASSERT compliance_check.all_passed

    # ===== 步骤8: 数据安全审查 =====
    # 改进#31修复: DATA_SECURITY_REVIEW改为CALL protocol-data-security
    security_check = CALL protocol-data-security(expert_package, s6_data)
    IF security_check.high_risk_items EXISTS:
        FOR item IN security_check.high_risk_items:
            APPLY_SECURITY_FIX(item, expert_package)
        security_check = CALL protocol-data-security(expert_package, s6_data)
    ASSERT security_check.all_passed

    # ===== 步骤9: 执行计划生成 =====
    execution_plan = {}
    execution_plan.deployment_steps = GENERATE_DEPLOYMENT_STEPS(platform, team_type, roles)
    execution_plan.verification_checklist = GENERATE_VERIFICATION_CHECKLIST(expert_package)
    execution_plan.rollback_plan = GENERATE_ROLLBACK_PLAN(platform)

    # ===== 步骤10: 最终确认三步门(7.5) =====
    # ①内部一致性检查(自检)
    self_check_result = PERFORM_INTERNAL_CONSISTENCY_CHECK(expert_package, roles, FIELD_TRACING_MAP)
    IF self_check_result.has_errors:
        FIX_INTERNAL_ERRORS(self_check_result.errors, expert_package)
        self_check_result = PERFORM_INTERNAL_CONSISTENCY_CHECK(expert_package, roles, FIELD_TRACING_MAP)
    ASSERT self_check_result.all_passed

    # ②用户结构确认(展示结构请用户确认)
    OUTPUT "专家包结构总览：" + SUMMARIZE_PACKAGE_STRUCTURE(expert_package) TO user
    structure_confirm = WAIT_FOR_USER()
    IF structure_confirm CONTAINS "修改":
        expert_package = APPLY_USER_MODIFICATIONS(structure_confirm, expert_package)

    # ③用户批准(明确说'批准'或'确认')
    OUTPUT "请回复'批准'或'确认'以完成专家包生成" TO user
    approval = WAIT_FOR_USER()
    IF approval NOT IN ["批准", "确认", "approve", "confirm"]:
        OUTPUT "请明确回复'批准'或'确认'" TO user
        approval = WAIT_FOR_USER()

    # ===== 产出输出 =====
    output = BUILD_output_according_to_output_schema({
        "expert_package": expert_package,
        "execution_plan": execution_plan,
        "final_confirmation": {
            "self_check": "✅",
            "user_structure_review": structure_confirm,
            "user_approval": approval
        }
    })
    RETURN output
```

## 下一阶段路由

> 本阶段完成后，由 `team-orchestrator` 自动衔接至 `pipeline-s8-platform-execution`（阶段八：平台执行）。
> 衔接条件：专家包已生成 + 四步确认门通过 + 平台配置已就绪。
> L2协议和L3适配器由team-orchestrator根据激活矩阵自动激活，用户无需手动选择。用户无需手动触发下一阶段。

## 版本

1.4.0

---
*本Skill由全域专家团构建skills体系生成，版本1.4.0，日期2026-06-17*
