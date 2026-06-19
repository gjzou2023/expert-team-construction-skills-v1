{
  "id": "pipeline-s1-need-diving",
  "layer": "L1",
  "name_zh": "阶段一：需求深潜",
  "name_en": "Stage 1: Need Diving",
  "version": "1.4.0",
  "description": "通过5-Why逐层追问(每次只问1个问题)挖掘真实需求，生成需求画像卡，初评复杂度。",
  "trigger_keywords": [
    "开始",
    "帮我建",
    "我想做",
    "专家团",
    "需求",
    "刚开始"
  ],
  "input_schema": {
    "type": "object",
    "properties": {
      "user_first_message": {
        "type": "string",
        "description": "用户首次交互消息"
      },
      "user_context": {
        "type": "object",
        "properties": {
          "experience_level": {
            "type": "string",
            "enum": [
              "novice",
              "intermediate",
              "advanced"
            ]
          },
          "team_size": {
            "type": "integer"
          }
        }
      }
    },
    "required": [
      "user_first_message",
      "user_context"
    ]
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "need_portrait": {
        "type": "object",
        "properties": {
          "core_need": {
            "type": "string"
          },
          "surface_need": {
            "type": "string"
          },
          "real_goal": {
            "type": "string"
          },
          "explicit_assumptions": {
            "type": "array",
            "items": {"type": "string"},
            "description": "基于不完整信息做出的显式假设列表（v1.3.0新增，standard/strict通道必填，fast通道可空）"
          },
          "clarification_complete": {
            "type": "boolean",
            "description": "是否已完成需求澄清（或用户选择跳过）（v1.3.0新增，v1.4.0按用户角色动态调整）"
          },
          "user_role": {
            "type": "string",
            "enum": ["decision_maker", "tech_lead", "project_manager", "explorer"],
            "description": "用户角色识别，影响后续输出风格（v1.3.0新增，v1.4.0与对偶映射表联动）"
          }
        },
        "required": ["core_need", "surface_need", "real_goal"]
      },
      "complexity_signals": {
        "type": "array",
        "items": {
          "type": "string"
        }
      },
      "initial_channel_hint": {
        "type": "string",
        "enum": [
          "fast",
          "standard",
          "strict"
        ]
      }
    },
    "required": [
      "need_portrait",
      "complexity_signals",
      "initial_channel_hint"
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
        "decision": "阶段一：需求深潜已按A型内容传播场景执行",
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
      "path": "file://pipeline/stage-1-rules",
      "description": "阶段1执行规则"
    },
    {
      "type": "dynamic",
      "path": "file://pipeline/stage-1-state",
      "description": "阶段1运行时状态"
    },
    {
      "type": "rag",
      "path": "file://rag/pipeline-s1-need-diving/references",
      "description": "向量检索：源文档、平台规则和历史案例"
    }
  ],
  "dependencies": [
    "core-mental-model-engine",
    "core-complexity-channel-selector",
    "protocol-single-question-guidance"
  ],
  "mandatory_calls": [
    {
      "trigger": "every_interaction",
      "call": "protocol-single-question-guidance.execute",
      "timing": "before_ask"
    },
    {
      "trigger": "stage_end",
      "call": "core-state-management-engine.update_snapshot",
      "timing": "after_output"
    }
  ],
  "execution_logic": "(1)开场引导(§7话术)→(2)5-Why逐层追问(每次只问1个问题,§6.1#8)→(3)需求画像生成→(4)复杂度初评(调用core-complexity-channel-selector)→(5)输出需求确认卡。单问规则：信息采集阶段每次只问1个问题;确认阶段可一次性展示汇总卡。",
  "cascading_calls": [
    "core-mental-model-engine",
    "core-complexity-channel-selector",
    "protocol-single-question-guidance"
  ],
  "context_inheritance": [],
  "shared_memory_keys": [
    "s1_decisions",
    "s1_snapshot"
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
    "next_stage": "pipeline-s2-domain-disambiguation",
    "preconditions": [
      "需求确认卡已生成",
      "用户已确认核心需求/真实目标/目标平台",
      "复杂度初评已完成"
    ],
    "blocking_rule": "未确认需求画像时不得进入S2。"
  }
}
