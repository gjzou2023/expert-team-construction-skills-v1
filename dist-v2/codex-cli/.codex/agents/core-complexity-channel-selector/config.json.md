{
  "id": "core-complexity-channel-selector",
  "layer": "L0",
  "name_zh": "复杂度通道选择器",
  "name_en": "Complexity Channel Selector",
  "version": "1.4.0",
  "description": "基于7维度统一评估确定执行通道(快速/标准/严格)和响应模式(标准/增强/深度)，输出通道确认卡。v1.4.0将两套独立评估体系整合为统一框架。用户可升级通道但不可降级（除非明确声明理解风险）。",
  "trigger_keywords": [
    "通道选择",
    "快速通道",
    "严格通道",
    "复杂度评估",
    "跳过阶段",
    "精简流程"
  ],
  "input_schema": {
    "type": "object",
    "properties": {
      "s1_outputs": {
        "type": "object",
        "properties": {
          "domain_type": {
            "type": "string"
          },
          "deliverable_count": {
            "type": "integer"
          },
          "role_count": {
            "type": "integer"
          },
          "compliance_level": {
            "type": "string",
            "enum": [
              "none",
              "light",
              "heavy"
            ]
          },
          "automation_complexity": {
            "type": "string",
            "enum": [
              "none",
              "simple",
              "complex"
            ]
          }
        }
      }
    },
    "required": [
      "s1_outputs"
    ]
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "channel": {
        "type": "string",
        "enum": [
          "fast",
          "standard",
          "strict"
        ]
      },
      "skipped_stages": {
        "type": "array",
        "items": {
          "type": "integer"
        }
      },
      "stage_simplification": {
        "type": "object",
        "additionalProperties": {
          "type": "string"
        }
      },
      "confirmation_card": {
        "type": "string"
      }
    },
    "required": [
      "channel",
      "skipped_stages",
      "stage_simplification",
      "confirmation_card"
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
        "decision": "复杂度通道选择器已按A型内容传播场景执行",
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
      "path": "file://channel-rules/thresholds",
      "description": "三通道判定阈值与跳过规则"
    },
    {
      "type": "static",
      "path": "file://channel-rules/fast-track-simplifications",
      "description": "快速通道各阶段精简规则"
    },
    {
      "type": "dynamic",
      "path": "file://runtime/core-complexity-channel-selector/state",
      "description": "运行时状态、用户确认和阶段快照"
    },
    {
      "type": "rag",
      "path": "file://rag/core-complexity-channel-selector/references",
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
  "execution_logic": "5维度评估：知识深度(低/中/高)、监管强度(低/中/高)、错误代价(低/中/高)、更新频率(低/中/高)、数据敏感度(低/中/高)。\n通道规则：\n- 快速通道：角色数≤2,交付物≤3,无强监管,无D/F型自动化→跳过S3/S5,简化S2/S4,S7内联输出\n- 标准通道：默认,完整8阶段\n- 严格通道：强监管行业/角色≥4/涉及医疗金融法律→增加合规审查节点+人工审批+双重确认\n约束：用户可升级通道但不可降级(除非明确声明理解风险)；快速通道跳过5.9自动化触发设计，使用纯提示词降级。",
  "cascading_calls": [
    "core-mental-model-engine"
  ],
  "context_inheritance": [
    "s1_outputs"
  ],
  "shared_memory_keys": [
    "selected_channel",
    "channel_confirmation_card"
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