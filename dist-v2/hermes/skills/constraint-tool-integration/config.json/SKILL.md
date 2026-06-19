{
  "id": "constraint-tool-integration",
  "layer": "L4",
  "name_zh": "工具集成规范",
  "name_en": "Tool Integration Standard",
  "version": "1.0.0",
  "description": "MCP Server配置模板→健康检查机制→超时/重试策略→降级决策树→成本监控→安全校验。",
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
        "decision": "工具集成规范已按A型内容传播场景执行",
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
      "path": "file://constraints/constraint-tool-integration",
      "description": "工具集成规范完整规则集"
    },
    {
      "type": "dynamic",
      "path": "file://runtime/constraint-tool-integration/state",
      "description": "运行时状态、用户确认和阶段快照"
    },
    {
      "type": "rag",
      "path": "file://rag/constraint-tool-integration/references",
      "description": "向量检索：源文档、平台规则和历史案例"
    }
  ],
  "dependencies": [],
  "execution_logic": "工具集成三层架构：L1平台内置(零成本/最高可靠性);L2协议扩展MCP/OpenAPI(低-中成本);L3外部API(中-高成本/依赖第三方)。健康检查：每次调用前轻量ping+每日完整检查。重试：最多3次，指数退避(1s/2s/4s)。降级决策树：瞬时错误→重试;持续错误→切换降级+通知;关键错误→暂停+告警。",
  "cascading_calls": [],
  "context_inheritance": [
    "all_stage_outputs"
  ],
  "shared_memory_keys": [
    "constraint-tool-integration_violations"
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
