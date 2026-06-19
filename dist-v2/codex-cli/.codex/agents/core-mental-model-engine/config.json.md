{
  "id": "core-mental-model-engine",
  "layer": "L0",
  "name_zh": "思维框架引擎",
  "name_en": "Mental Model Engine",
  "version": "1.4.0",
  "description": "根据当前决策场景，从18个心智模型中选择匹配模型，输出结构化推理链。全程内化运行，不向用户解释模型本身，体现在提问深度、方案严谨度和输出结构中。",
  "trigger_keywords": [
    "推理",
    "决策",
    "分析",
    "判断",
    "为什么",
    "推理链",
    "思维模型"
  ],
  "input_schema": {
    "type": "object",
    "properties": {
      "scene": {
        "type": "string",
        "enum": [
          "need_analysis",
          "architecture",
          "compliance",
          "quality",
          "degradation",
          "domain_adaptation"
        ],
        "description": "决策场景类型"
      },
      "context": {
        "type": "string",
        "description": "当前对话上下文和阶段状态"
      },
      "decision_point": {
        "type": "string",
        "description": "具体决策问题描述"
      }
    },
    "required": [
      "scene",
      "context",
      "decision_point"
    ]
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "model_used": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "description": "激活的心智模型列表"
      },
      "reasoning_chain": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "description": "因为...所以...的推理路径"
      },
      "conclusion": {
        "type": "string",
        "description": "推理结论"
      },
      "confidence": {
        "type": "string",
        "enum": [
          "high",
          "medium",
          "low"
        ],
        "description": "置信度"
      }
    },
    "required": [
      "model_used",
      "reasoning_chain",
      "conclusion",
      "confidence"
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
        "decision": "思维框架引擎已按A型内容传播场景执行",
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
      "path": "file://mental-models/18-models-definitions",
      "description": "18心智模型定义与激活映射表"
    },
    {
      "type": "static",
      "path": "file://mental-models/failure-modes",
      "description": "8类失败模式预枚举"
    },
    {
      "type": "dynamic",
      "path": "file://stage-context/current-decisions",
      "description": "当前阶段决策上下文"
    },
    {
      "type": "rag",
      "path": "file://rag/core-mental-model-engine/references",
      "description": "向量检索：源文档、平台规则和历史案例"
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
  "execution_logic": "根据决策场景类型选择激活的心智模型子集：\n(1) need_analysis → 5-Why + 第一性原理\n(2) architecture → 交付物倒推 + 系统思维 + MECE + ToT + 平台工程思维\n(3) compliance → 批判思维 + 合规思维 + 辩证思维\n(4) quality → 5-Why + 批判思维 + 反向思维\n(5) degradation → 反脆弱 + 反向思维\n(6) domain_adaptation → 领域适配思维 + 产品思维\n\n18心智模型清单：\n1.交付物倒推 2.反向思维 3.系统思维 4.MECE结构化 5.CoT链式推理\n6.ToT思维树 7.产品思维 8.用户思维 9.5-Why根因分析 10.第一性原理\n11.反脆弱 12.批判思维 13.领域适配思维 14.合规思维 15.辩证思维\n16.ReAct 17.数据安全思维 18.平台工程思维\n\n核心约束：不向用户解释思维模型本身；体现在提问深度、方案严谨度、输出结构中；每个核心决策点展示推理路径(CoT)",
  "cascading_calls": [],
  "context_inheritance": [
    "previous_stage_outputs",
    "decision_snapshots"
  ],
  "shared_memory_keys": [
    "reasoning_history",
    "model_activation_log"
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
  "priority": 0,
  "trigger_conflicts": [
    {
      "keyword": "推理",
      "prefer": "pipeline-s5-architecture-design",
      "when": "用户明确处于架构设计阶段"
    }
  ]
}