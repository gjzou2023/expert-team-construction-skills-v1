{
  "id": "platform-hermes-adapter",
  "layer": "L3",
  "name_zh": "Hermes Agent平台适配器",
  "name_en": "Hermes Agent Adapter",
  "version": "1.1.0",
  "description": "生成skills/{skill-name}/SKILL.md+context/{context-name}.md。持续运行+内置定时+消息监听。",
  "trigger_keywords": [
    "hermes",
    "hermes",
    "平台适配",
    "输出格式"
  ],
  "input_schema": {
    "type": "object",
    "properties": {
      "architecture": {
        "type": "object",
        "description": "S5架构输出"
      },
      "roles": {
        "type": "array",
        "description": "角色定义列表"
      },
      "sop": {
        "type": "object",
        "description": "SOP定义"
      },
      "expert_type": {
        "type": "string",
        "enum": [
          "team",
          "agent"
        ]
      },
      "track": {
        "type": "string",
        "enum": [
          "fast",
          "standard",
          "strict"
        ]
      }
    },
    "required": [
      "architecture",
      "roles",
      "expert_type"
    ]
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "output_format": {
        "type": "string",
        "description": "skills/{skill-name}/SKILL.md + context/{context-name}.md"
      },
      "platform_specific_config": {
        "type": "object"
      },
      "degradation_plan": {
        "type": "object"
      }
    },
    "required": [
      "output_format",
      "platform_specific_config"
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
        "decision": "Hermes Agent平台适配器已按A型内容传播场景执行",
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
      "path": "file://platform/platform-hermes-adapter/format-spec",
      "description": "Hermes Agent平台适配器格式规范"
    },
    {
      "type": "dynamic",
      "path": "file://runtime/platform-hermes-adapter/state",
      "description": "运行时状态、用户确认和阶段快照"
    },
    {
      "type": "rag",
      "path": "file://rag/platform-hermes-adapter/references",
      "description": "向量检索：源文档、平台规则和历史案例"
    }
  ],
  "dependencies": [
    "core-mental-model-engine",
    "constraint-output-format"
  ],
  "execution_logic": "目标平台=Hermes Agent平台适配器时激活。输出格式：skills/{skill-name}/SKILL.md + context/{context-name}.md。平台特定规则：持续运行+内置定时+消息监听;在SKILL.md中定义schedule字段和event listener。",
  "cascading_calls": [
    "core-mental-model-engine"
  ],
  "context_inheritance": [
    "s5_architecture",
    "s6_toolchain",
    "s7_expert_package"
  ],
  "shared_memory_keys": [
    "platform-hermes-adapter_output"
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
        "callee": "protocol-quality-gate",
        "when": "专家包生成完成后",
        "reason": "Doc1 CROSS_SKILL_PROTOCOL: 平台生成完成 -> SK-001"
      }
    ]
  },
  "mandatory_calls": [
    {
      "callee": "protocol-quality-gate",
      "when": "阶段结束或产出方案前",
      "reason": "Doc1 CROSS_SKILL_PROTOCOL: ANY_SKILL -> SK-001"
    },
    {
      "callee": "protocol-quality-gate",
      "when": "专家包生成完成后",
      "reason": "Doc1 CROSS_SKILL_PROTOCOL: 平台生成完成 -> SK-001"
    }
  ],
  "compatibility": {
    "min_compatible": "1.1.0",
    "breaking_change": "2.0.0"
  },
  "priority": 3
}
