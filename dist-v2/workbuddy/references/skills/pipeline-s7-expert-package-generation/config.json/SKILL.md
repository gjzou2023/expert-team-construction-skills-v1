{
  "id": "pipeline-s7-expert-package-generation",
  "layer": "L1",
  "name_zh": "阶段七：专家包生成",
  "name_en": "Stage 7: Expert Package Generation",
  "version": "1.4.0",
  "description": "生成专家包概览、按目标平台格式生成配置、嵌入全局机制、生成执行计划、最终确认三步门。字段追踪强制。",
  "trigger_keywords": [
    "专家包",
    "生成",
    "打包",
    "确认",
    "三步门",
    "导出"
  ],
  "input_schema": {
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
        "description": "运行时条件激活上下文，用于按需激活L2协议和L3适配器(改进#4修复)",
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
          "channel": {
            "type": "string",
            "enum": ["fast", "standard", "strict"],
            "description": "通道类型，影响协议激活矩阵查询key"
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
  },
  "output_schema": {
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
  },
  "tool_declarations": [],
  "few_shot_examples": [
    {
      "name": "正常流程",
      "input": {
        "user_input": "小红书内容团队要从选题到发布形成稳定流程",
        "context": {
          "domain_type": "A",
          "platform": "workbuddy"
        }
      },
      "output": {
        "status": "completed",
        "decision": "阶段七：专家包生成已按A型内容传播场景执行",
        "next_action": "进入下一阶段或触发质量门控"
      }
    },
    {
      "name": "边界/异常",
      "input": {
        "user_input": "我们做医疗科普，但想尽量直接承诺效果",
        "context": {
          "domain_type": "A",
          "regulated": true
        }
      },
      "output": {
        "status": "blocked_or_review",
        "risk": "强监管合规风险",
        "required_call": "protocol-compliance-engine"
      }
    },
    {
      "name": "快速通道变体",
      "input": {
        "user_input": "只有我一个人，先要一个能用的提示词版客服助手",
        "context": {
          "role_count": 1,
          "deliverable_count": 2,
          "channel": "fast"
        }
      },
      "output": {
        "status": "simplified",
        "strategy": "保留核心交付物与兜底方案，跳过或内联低风险阶段"
      }
    }
  ],
  "knowledge_base_mount_points": [
    {
      "type": "static",
      "path": "file://pipeline/stage-7-rules",
      "description": "阶段7执行规则"
    },
    {
      "type": "dynamic",
      "path": "file://pipeline/stage-7-state",
      "description": "阶段7运行时状态"
    },
    {
      "type": "rag",
      "path": "file://rag/pipeline-s7-expert-package-generation/references",
      "description": "向量检索：源文档、平台规则和历史案例"
    }
  ],
  "dependencies": [
    "core-mental-model-engine",
    "core-deliverable-backward-engine"
  ],
  "conditional_dependencies": {
    "说明": "改进#4修复: L2协议和L3适配器根据activation_context按需激活，不在dependencies中硬声明。activation_map定义在外部knowledge/protocol-activation-map.json。",
    "L2_protocol_activation": "按knowledge/protocol-activation-map.json的domain_type和compliance_activation_map条件激活",
    "L3_adapter_activation": "仅激活platform对应的单个L3适配器"
  },
  "execution_logic": "生成专家包概览后，按platform参数条件调用对应L3适配器，并嵌入全部L2协议层机制；最终执行三步门和字段追踪检查。",
  "cascading_calls": [
    "core-mental-model-engine",
    "core-deliverable-backward-engine"
  ],
  "context_inheritance": [
    "s6_outputs"
  ],
  "shared_memory_keys": [
    "s7_decisions",
    "s7_snapshot"
  ],
  "protocol": {
    "cascading_enabled": true,
    "context_inheritance_enabled": true,
    "shared_memory_enabled": true,
    "cascade_direction": "同层或下层可调用",
    "data_passing_format": "JSON-compatible",
    "immutability_rule": "上游产出一经确认，下游不得擅自修改，需通过回退协议",
    "traceability": "每个字段标注来源阶段和Skill",
    "mandatory_calls": [
      {
        "callee": "protocol-quality-gate",
        "when": "阶段结束或产出方案前",
        "reason": "Doc1 CROSS_SKILL_PROTOCOL: ANY_SKILL -> SK-001"
      },
      {
        "callee": "protocol-confirmation-node",
        "when": "阶段跳转前",
        "reason": "Doc1 CROSS_SKILL_PROTOCOL: 流程阶段跳转 -> SK-102"
      },
      {
        "callee": "protocol-quality-gate",
        "when": "专家包生成完成后",
        "reason": "Doc1 CROSS_SKILL_PROTOCOL: 平台生成完成 -> SK-001"
      }
    ]
  },
  "compatibility": {
    "min_compatible": "1.1.0",
    "breaking_change": "2.0.0"
  },
  "priority": 1,
  "stage_guard": {
    "next_stage": "pipeline-s8-platform-execution",
    "preconditions": [
      "专家包字段追踪通过",
      "全部L2协议已嵌入",
      "目标L3平台适配器已执行",
      "最终确认三步门全过"
    ],
    "blocking_rule": "没有明确批准/确认不得进入S8。"
  }
}
