{
  "id": "constraint-flexible-rules",
  "layer": "L4",
  "name_zh": "灵活适配规则",
  "name_en": "Flexible Rules",
  "version": "1.1.0",
  "description": "默认值，用户/领域需要时调整。11条灵活规则。",
  "trigger_keywords": [
    "规则",
    "约束",
    "强制",
    "规范",
    "命名"
  ],
  "input_schema": {
    "type": "object",
    "properties": {
      "target_check": {
        "type": "string",
        "description": "待检查的目标内容"
      },
      "context": {
        "type": "object",
        "description": "检查上下文"
      }
    },
    "required": [
      "target_check"
    ]
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "compliant": {
        "type": "boolean"
      },
      "violations": {
        "type": "array",
        "items": {
          "type": "object"
        }
      },
      "suggestions": {
        "type": "array",
        "items": {
          "type": "string"
        }
      }
    },
    "required": [
      "compliant",
      "violations",
      "suggestions"
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
        "decision": "灵活适配规则已按A型内容传播场景执行",
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
      "path": "file://constraints/constraint-flexible-rules",
      "description": "灵活适配规则完整规则集"
    },
    {
      "type": "dynamic",
      "path": "file://runtime/constraint-flexible-rules/state",
      "description": "运行时状态、用户确认和阶段快照"
    },
    {
      "type": "rag",
      "path": "file://rag/constraint-flexible-rules/references",
      "description": "向量检索：源文档、平台规则和历史案例"
    }
  ],
  "dependencies": [],
  "execution_logic": "10条灵活规则：(1)领域特定子协议按领域激活;(2)角色精简(保证第一责任人前提下合并);(3)工具可选(纯提示词始终有效);(4)人工介入密度按团队调整;(5)迭代粒度按领域调整;(6)反馈回路数量按领域激活;(7)冷启动退出条件默认可调;(8)禁用词列表长度(低≥3,高/强监管≥8);(9)平台选择灵活;(10)花名字数灵活(建议2-3字,特殊4字)",
  "cascading_calls": [],
  "context_inheritance": [
    "all_stage_outputs"
  ],
  "shared_memory_keys": [
    "constraint-flexible-rules_violations"
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
  "mandatory_calls": [
    {
      "callee": "protocol-quality-gate",
      "when": "阶段结束或产出方案前",
      "reason": "Doc1 CROSS_SKILL_PROTOCOL: ANY_SKILL -> SK-001"
    }
  ],
  "compatibility": {
    "min_compatible": "1.0.0",
    "breaking_change": "2.0.0"
  },
  "priority": 4
}