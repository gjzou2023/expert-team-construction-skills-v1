{
  "id": "core-deliverable-backward-engine",
  "layer": "L0",
  "name_zh": "交付物倒推引擎",
  "name_en": "Deliverable Backward Engine",
  "version": "1.1.0",
  "description": "从用户需求提取终端交付物→分配唯一第一责任人→反推能力→定义角色→定义工具→定义数据流。严格禁止逆向（先角色后交付物）。",
  "trigger_keywords": [
    "交付物",
    "角色设计",
    "架构设计",
    "倒推",
    "从交付物开始",
    "责任分配"
  ],
  "input_schema": {
    "type": "object",
    "properties": {
      "user_need": {
        "type": "string",
        "description": "用户需求描述"
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
        ],
        "description": "领域类型"
      },
      "deliverable_candidates": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "description": "候选交付物列表"
      }
    },
    "required": [
      "user_need",
      "domain_type"
    ]
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "deliverables": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "name": {
              "type": "string"
            },
            "format": {
              "type": "string"
            },
            "owner_role": {
              "type": "string"
            },
            "priority": {
              "type": "string",
              "enum": [
                "core",
                "enhancement"
              ]
            }
          }
        }
      },
      "role_capability_map": {
        "type": "object",
        "additionalProperties": {
          "type": "array",
          "items": {
            "type": "string"
          }
        }
      },
      "tool_requirement_map": {
        "type": "object",
        "additionalProperties": {
          "type": "array",
          "items": {
            "type": "string"
          }
        }
      },
      "data_flow": {
        "type": "string",
        "description": "Mermaid格式的数据流图"
      }
    },
    "required": [
      "deliverables",
      "role_capability_map",
      "tool_requirement_map",
      "data_flow"
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
        "decision": "交付物倒推引擎已按A型内容传播场景执行",
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
      "path": "file://domain-defaults/deliverable-templates",
      "description": "各领域默认交付物模板"
    },
    {
      "type": "static",
      "path": "file://naming-rules/role-naming",
      "description": "角色命名三分法规范"
    },
    {
      "type": "dynamic",
      "path": "file://runtime/core-deliverable-backward-engine/state",
      "description": "运行时状态、用户确认和阶段快照"
    },
    {
      "type": "rag",
      "path": "file://rag/core-deliverable-backward-engine/references",
      "description": "向量检索：源文档、平台规则和历史案例"
    }
  ],
  "dependencies": [
    "core-mental-model-engine"
  ],
  "mandatory_calls": [
    {
      "trigger": "every_decision_point",
      "call": "self.activate",
      "timing": "before_output"
    }
  ],
  "execution_logic": "执行6步倒推链：(1)从用户需求提取终端交付物→(2)每个交付物分配唯一第一责任人→(3)从交付物反推所需能力→(4)从能力定义角色→(5)从角色定义工具→(6)从工具定义数据流。\n严格禁止逆向（先角色后交付物）。\n如检测到\"先定义角色再找交付物\"的错误倾向，立即纠偏。\n分线规则：不同交付形态的渠道不得共用生产线（允许共用上游，下游必须分线）。",
  "cascading_calls": [
    "core-mental-model-engine"
  ],
  "context_inheritance": [
    "s1_need_portrait",
    "s2_domain_type"
  ],
  "shared_memory_keys": [
    "deliverable_registry",
    "role_deliverable_map"
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
      }
    ]
  },
  "compatibility": {
    "min_compatible": "1.1.0",
    "breaking_change": "2.0.0"
  },
  "priority": 0
}
