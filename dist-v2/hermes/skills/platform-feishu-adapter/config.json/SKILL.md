{
  "id": "platform-feishu-adapter",
  "layer": "L3",
  "name_zh": "飞书平台适配器",
  "name_en": "Feishu Adapter",
  "version": "1.0.0",
  "description": "三种集成形态：消息型/交互型/深度集成。生成manifest.yaml+消息卡片模板+审批模板+多维表格Schema+定时触发配置。",
  "trigger_keywords": [
    "feishu",
    "feishu",
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
        "description": "manifest.yaml + 消息卡片模板 + 审批模板 + 多维表格Schema + 定时触发配置"
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
        "decision": "飞书平台适配器已按A型内容传播场景执行",
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
      "path": "file://platform/platform-feishu-adapter/format-spec",
      "description": "飞书平台适配器格式规范"
    },
    {
      "type": "dynamic",
      "path": "file://runtime/platform-feishu-adapter/state",
      "description": "运行时状态、用户确认和阶段快照"
    },
    {
      "type": "rag",
      "path": "file://rag/platform-feishu-adapter/references",
      "description": "向量检索：源文档、平台规则和历史案例"
    }
  ],
  "dependencies": [
    "core-mental-model-engine",
    "constraint-output-format"
  ],
  "execution_logic": "目标平台=飞书平台适配器时激活。输出格式：manifest.yaml + 消息卡片模板 + 审批模板 + 多维表格Schema + 定时触发配置。平台特定规则：形态确认(强制确认节点)：仅A→消息通道型;A+B或仅B→交互入口型;含C/D/E/F任一→深度集成型。",
  "cascading_calls": [
    "core-mental-model-engine"
  ],
  "context_inheritance": [
    "s5_architecture",
    "s6_toolchain",
    "s7_expert_package"
  ],
  "shared_memory_keys": [
    "platform-feishu-adapter_output"
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
    "min_compatible": "1.0.0",
    "breaking_change": "2.0.0"
  },
  "priority": 3
}
