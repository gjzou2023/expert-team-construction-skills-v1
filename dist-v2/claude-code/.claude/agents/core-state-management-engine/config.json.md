{
  "id": "core-state-management-engine",
  "layer": "L0",
  "name_zh": "状态管理引擎",
  "name_en": "State Management Engine",
  "version": "1.1.0",
  "description": "维护阶段决策快照，处理用户回退、平台更换和长对话上下文压缩。",
  "trigger_keywords": [
    "快照",
    "回退",
    "改一下",
    "换平台",
    "上下文压缩",
    "状态"
  ],
  "input_schema": {
    "type": "object",
    "properties": {
      "action": {
        "type": "string",
        "enum": [
          "update",
          "rollback",
          "platform_change",
          "compress"
        ]
      },
      "stage": {
        "type": "string"
      },
      "user_input": {
        "type": "string"
      },
      "new_platform": {
        "type": "string"
      }
    },
    "required": [
      "action",
      "stage"
    ]
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "snapshot": {
        "type": "object"
      },
      "impact_list": {
        "type": "array"
      },
      "recovery_path": {
        "type": "string"
      }
    },
    "required": [
      "snapshot"
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
        "decision": "状态管理引擎已按A型内容传播场景执行",
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
      "path": "file://doc1/core-state-management-engine/rules",
      "description": "Doc1对应SK原始规则"
    },
    {
      "type": "dynamic",
      "path": "file://runtime/core-state-management-engine/state",
      "description": "运行时状态"
    },
    {
      "type": "rag",
      "path": "file://rag/core-state-management-engine/references",
      "description": "向量检索参考资料"
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
  "execution_logic": "每阶段结束更新快照；检测回退触发词时暂停推进并输出影响清单；平台变更时保留设计并重走平台适配；对话超过40轮时压缩上下文。",
  "cascading_calls": [
    "core-mental-model-engine"
  ],
  "context_inheritance": [
    "current_stage_outputs"
  ],
  "shared_memory_keys": [
    "core-state-management-engine_state"
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
        "reason": "全局质量门控"
      },
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
