{
  "id": "pipeline-s3-chain-decomposition",
  "layer": "L1",
  "name_zh": "阶段三：链路拆解",
  "name_en": "Stage 3: Chain Decomposition",
  "version": "1.1.0",
  "description": "I-2.6改进: 从终端交付物倒推全链路，识别链路节点(节点ID→上下游依赖→断点标注)。S3负责'链路骨架'，不独立定义交付物内容；交付物填充由S4完成。快速通道跳过，合并入S4。标准/strict通道下S3仅生成骨架节点，S4填充具体交付物，消除40%重复推理。",
  "trigger_keywords": [
    "链路",
    "流程",
    "拆解",
    "工作流",
    "全链路"
  ],
  "input_schema": {
    "type": "object",
    "properties": {
      "s2_outputs": {
        "type": "object",
        "description": "S2领域确认输出"
      },
      "deliverable_candidates": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "description": "候选交付物"
      }
    },
    "required": [
      "s2_outputs",
      "deliverable_candidates"
    ]
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "chain_nodes": {
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
            "type": {
              "type": "string",
              "enum": [
                "input",
                "process",
                "output",
                "feedback"
              ]
            },
            "upstream": {
              "type": "array",
              "items": {
                "type": "string"
              }
            },
            "downstream": {
              "type": "array",
              "items": {
                "type": "string"
              }
            }
          }
        }
      },
      "chain_mermaid": {
        "type": "string"
      },
      "breakpoints": {
        "type": "array",
        "items": {
          "type": "string"
        }
      },
      "dependencies": {
        "type": "array",
        "items": {
          "type": "string"
        }
      }
    },
    "required": [
      "chain_nodes",
      "chain_mermaid",
      "breakpoints",
      "dependencies"
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
        "decision": "阶段三：链路拆解已按A型内容传播场景执行",
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
      "path": "file://pipeline/stage-3-rules",
      "description": "阶段3执行规则"
    },
    {
      "type": "dynamic",
      "path": "file://pipeline/stage-3-state",
      "description": "阶段3运行时状态"
    },
    {
      "type": "rag",
      "path": "file://rag/pipeline-s3-chain-decomposition/references",
      "description": "向量检索：源文档、平台规则和历史案例"
    }
  ],
  "dependencies": [
    "core-mental-model-engine",
    "core-deliverable-backward-engine"
  ],
  "mandatory_calls": [
    {
      "trigger": "every_interaction",
      "call": "core-deliverable-backward-engine.execute",
      "timing": "before_ask"
    },
    {
      "trigger": "stage_end",
      "call": "core-state-management-engine.update_snapshot",
      "timing": "after_output"
    }
  ],
  "execution_logic": "(1)从终端交付物倒推全链路(调用core-deliverable-backward-engine)→(2)识别链路节点(输入→处理→输出→反馈)→(3)标注断点与依赖→(4)输出链路图(Mermaid)。默认链路按领域类型：A型7步/B型6步/C型6步/D型6步/F型6步。快速通道：取3-5步精简工作流概要。",
  "cascading_calls": [
    "core-mental-model-engine"
  ],
  "context_inheritance": [
    "s2_outputs"
  ],
  "shared_memory_keys": [
    "s3_decisions",
    "s3_snapshot"
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
  "priority": 3,
  "stage_guard": {
    "next_stage": "pipeline-s4-deliverable-anchoring",
    "preconditions": [
      "链路节点已覆盖输入/处理/输出/反馈",
      "断点已修复或标注",
      "Mermaid链路图已生成"
    ],
    "blocking_rule": "存在未处理断点时不得进入S4。"
  }
}
