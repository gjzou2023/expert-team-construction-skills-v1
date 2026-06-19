{
  "id": "constraint-naming-convention",
  "layer": "L4",
  "name_zh": "命名规范(精确三分法)",
  "name_en": "Naming Convention",
  "version": "1.0.0",
  "description": "Agent ID: kebab-case;花名:2-3字正常人名风格(谐音巧思,不与profession重复);profession:禁止通用title。",
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
        "decision": "命名规范(精确三分法)已按A型内容传播场景执行",
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
      "path": "file://constraints/constraint-naming-convention",
      "description": "命名规范(精确三分法)完整规则集"
    },
    {
      "type": "dynamic",
      "path": "file://runtime/constraint-naming-convention/state",
      "description": "运行时状态、用户确认和阶段快照"
    },
    {
      "type": "rag",
      "path": "file://rag/constraint-naming-convention/references",
      "description": "向量检索：源文档、平台规则和历史案例"
    }
  ],
  "dependencies": [],
  "execution_logic": "精确三分法：(1)Agent ID: kebab-case(如content-strategist);(2)花名:2-3字正常人名风格,谐音巧思,不与profession重复(如'墨言'而非'内容师');(3)profession:禁止通用title(团长/主理人),必须具体职能(如'内容策略师')。禁止：纯叠字/纯功能词直接作名/谐音生硬/一个字/无意义随机名/和profession重复/数字符号英文。主理人profession框架：A=内容制作总监;B=交付总监;C=知识架构总监;D=流程编排总监;F=服务运营总监;E=取主要子类型+多线统筹",
  "cascading_calls": [],
  "context_inheritance": [
    "all_stage_outputs"
  ],
  "shared_memory_keys": [
    "constraint-naming-convention_violations"
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
