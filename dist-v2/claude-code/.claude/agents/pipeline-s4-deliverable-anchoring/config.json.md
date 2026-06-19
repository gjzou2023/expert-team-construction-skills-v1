{
  "id": "pipeline-s4-deliverable-anchoring",
  "layer": "L1",
  "name_zh": "阶段四：交付物锚定",
  "name_en": "Stage 4: Deliverable Anchoring",
  "version": "1.1.0",
  "description": "I-2.6改进: 在S3链路骨架基础上，填充每个节点的具体交付物（格式/频率/质量标准/目标受众），分配优先级和第一责任人，标注分线需求。S4负责'交付物填充'，不独立定义链路依赖；链路骨架由S3完成。标准/strict通道下承接S3骨架节点，仅填充内容，消除重复推理。Q9平台选择强制确认。",
  "trigger_keywords": [
    "交付物",
    "产出",
    "格式",
    "优先级",
    "锚定",
    "平台选择"
  ],
  "input_schema": {
    "type": "object",
    "properties": {
      "s3_outputs": {
        "type": "object",
        "description": "S3链路节点输出"
      },
      "s2_outputs": {
        "type": "object",
        "description": "S2领域确认输出"
      }
    },
    "required": [
      "s3_outputs",
      "s2_outputs"
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
            "id": {
              "type": "string"
            },
            "name": {
              "type": "string"
            },
            "format": {
              "type": "string"
            },
            "frequency": {
              "type": "string"
            },
            "quality_criteria": {
              "type": "string"
            },
            "target_audience": {
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
            },
            "channel_line": {
              "type": "string"
            }
          }
        }
      },
      "cross_channel_sharing": {
        "type": "array",
        "items": {
          "type": "string"
        }
      }
    },
    "required": [
      "deliverables",
      "cross_channel_sharing"
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
        "decision": "阶段四：交付物锚定已按A型内容传播场景执行",
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
      "path": "file://pipeline/stage-4-rules",
      "description": "阶段4执行规则"
    },
    {
      "type": "dynamic",
      "path": "file://pipeline/stage-4-state",
      "description": "阶段4运行时状态"
    },
    {
      "type": "rag",
      "path": "file://rag/pipeline-s4-deliverable-anchoring/references",
      "description": "向量检索：源文档、平台规则和历史案例"
    }
  ],
  "dependencies": [
    "core-mental-model-engine",
    "core-deliverable-backward-engine"
  ],
  "execution_logic": "(1)枚举所有终端交付物→(2)每个交付物标注:格式、频率、质量标准、目标受众→(3)分配优先级(core/enhancement)→(4)确定每个交付物的唯一第一责任人→(5)标注分线需求(不同渠道不同生产线,§6.1#5)→(6)输出交付物清单确认卡。Q9强制确认；'还没想好'分支：默认WorkBuddy，后续可更改。快速通道精简：交付物≤3时精简确认流程。",
  "cascading_calls": [
    "core-mental-model-engine"
  ],
  "context_inheritance": [
    "s3_outputs"
  ],
  "shared_memory_keys": [
    "s4_decisions",
    "s4_snapshot"
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
    "min_compatible": "1.1.0",
    "breaking_change": "2.0.0"
  },
  "priority": 1,
  "stage_guard": {
    "next_stage": "pipeline-s5-architecture-design",
    "preconditions": [
      "交付物清单已确认",
      "每个交付物有格式/频率/质量标准/受众",
      "每个交付物有唯一第一责任人"
    ],
    "blocking_rule": "没有第一责任人的交付物不得进入架构设计。"
  }
}
