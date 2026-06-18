{
  "id": "core-symbol-system",
  "layer": "L0",
  "name_zh": "符号系统",
  "name_en": "Symbol System",
  "version": "1.1.0",
  "description": "统一信息准确性、合规风险、质量等级和平台执行状态的符号，禁止跨层级混用。",
  "trigger_keywords": [
    "符号",
    "状态标记",
    "绿灯",
    "黄灯",
    "红灯",
    "格式"
  ],
  "input_schema": {
    "type": "object",
    "properties": {
      "semantic_layer": {
        "type": "string"
      },
      "status": {
        "type": "string"
      }
    },
    "required": [
      "semantic_layer",
      "status"
    ]
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "symbol": {
        "type": "string"
      },
      "meaning": {
        "type": "string"
      },
      "usage_rule": {
        "type": "string"
      }
    },
    "required": [
      "symbol",
      "meaning"
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
        "decision": "符号系统已按A型内容传播场景执行",
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
      "path": "file://doc1/core-symbol-system/rules",
      "description": "Doc1对应SK原始规则"
    },
    {
      "type": "dynamic",
      "path": "file://runtime/core-symbol-system/state",
      "description": "运行时状态"
    },
    {
      "type": "rag",
      "path": "file://rag/core-symbol-system/references",
      "description": "向量检索参考资料"
    }
  ],
  "dependencies": [],
  "mandatory_calls": [
    {
      "trigger": "every_decision_point",
      "call": "self.activate",
      "timing": "before_output"
    }
  ],
  "execution_logic": "按语义层选择符号：准确性✅/⚡/❓，合规🟢/🟡/🔴，质量⭐⭐⭐/⭐⭐/⭐，平台🟦/🟧/⬛；不同层级不得混用。",
  "cascading_calls": [],
  "context_inheritance": [
    "current_stage_outputs"
  ],
  "shared_memory_keys": [
    "core-symbol-system_state"
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
