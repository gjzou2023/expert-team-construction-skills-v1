{
  "id": "pipeline-s5-architecture-design",
  "layer": "L1",
  "name_zh": "阶段五：架构设计",
  "name_en": "Stage 5: Architecture Design",
  "version": "1.3.0",
  "description": "从交付物倒推角色，MECE三问校验，设计SOP/数据流/反馈回路/冷启动策略，执行5.1-5.7自检。角色数≥4必须Team型。",
  "trigger_keywords": [
    "架构",
    "角色设计",
    "SOP",
    "团队",
    "主理人",
    "MECE"
  ],
  "input_schema": {
    "type": "object",
    "properties": {
      "s4_outputs": {
        "type": "object",
        "description": "S4交付物输出"
      },
      "domain_type": {
        "type": "string",
        "enum": [
          "A",
          "B",
          "C",
          "D",
          "E",
          "F"
        ]
      },
      "channel": {
        "type": "string",
        "enum": [
          "fast",
          "standard",
          "strict"
        ]
      }
    },
    "required": [
      "s4_outputs",
      "domain_type",
      "channel"
    ]
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "roles": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "id": {
              "type": "string"
            },
            "name": {
              "type": "string"
            },
            "profession": {
              "type": "string"
            },
            "capabilities": {
              "type": "array",
              "items": {
                "type": "string"
              }
            },
            "sop_phases": {
              "type": "array",
              "items": {
                "type": "string"
              }
            }
          }
        }
      },
      "data_flow": {
        "type": "string"
      },
      "feedback_loops": {
        "type": "array"
      },
      "cold_start_strategy": {
        "type": "object"
      },
      "sop": {
        "type": "object"
      },
      "quality_report": {
        "type": "object"
      }
    },
    "required": [
      "roles",
      "data_flow",
      "feedback_loops",
      "cold_start_strategy",
      "sop",
      "quality_report"
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
        "decision": "阶段五：架构设计已按A型内容传播场景执行",
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
      "path": "file://pipeline/stage-5-rules",
      "description": "阶段5执行规则"
    },
    {
      "type": "dynamic",
      "path": "file://pipeline/stage-5-state",
      "description": "阶段5运行时状态"
    },
    {
      "type": "rag",
      "path": "file://rag/pipeline-s5-architecture-design/references",
      "description": "向量检索：源文档、平台规则和历史案例"
    }
  ],
  "dependencies": [
    "core-mental-model-engine",
    "core-deliverable-backward-engine",
    "protocol-quality-gate",
    "protocol-feedback-loop",
    "protocol-compliance-engine"
  ],
  "execution_logic": "从交付物倒推角色，执行MECE三问，按标准/严格通道生成至少2种架构方案并用ToT比较，调用质量门控、反馈闭环和合规引擎后输出架构方案。",
  "cascading_calls": [
    "core-mental-model-engine",
    "core-deliverable-backward-engine",
    "protocol-quality-gate",
    "protocol-feedback-loop",
    "protocol-compliance-engine"
  ],
  "context_inheritance": [
    "s4_outputs"
  ],
  "shared_memory_keys": [
    "s5_decisions",
    "s5_snapshot"
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
      }
    ]
  },
  "compatibility": {
    "min_compatible": "1.0.0",
    "breaking_change": "2.0.0"
  },
  "priority": 1,
  "stage_guard": {
    "next_stage": "pipeline-s6-toolchain-matching",
    "preconditions": [
      "MECE三问通过",
      "质量守门协议通过",
      "合规层自检通过",
      "角色定义12项完整"
    ],
    "blocking_rule": "任一MECE或质量红灯项阻断输出。"
  },
  "trigger_conflicts": [
    {
      "keyword": "推理",
      "prefer": "core-mental-model-engine",
      "when": "仅需要通用推理而非架构产出"
    }
  ]
}