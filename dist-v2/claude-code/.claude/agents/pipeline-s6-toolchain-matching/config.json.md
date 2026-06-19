{
  "id": "pipeline-s6-toolchain-matching",
  "layer": "L1",
  "name_zh": "阶段六：工具链匹配",
  "name_en": "Stage 6: Toolchain Matching",
  "version": "1.1.0",
  "description": "从角色能力需求匹配工具，评估可用性，为不可用工具设计纯提示词兜底，工具数据安全评估。所有工具必须有纯提示词兜底方案。",
  "trigger_keywords": [
    "工具",
    "MCP",
    "API",
    "纯提示词",
    "兜底",
    "工具链"
  ],
  "input_schema": {
    "type": "object",
    "properties": {
      "s5_outputs": {
        "type": "object",
        "description": "S5架构设计输出(含roles/sop)"
      },
      "platform": {
        "type": "string",
        "enum": [
          "workbuddy",
          "codex",
          "hermes",
          "feishu",
          "n8n",
          "comfyui",
          "coze",
          "dify"
        ]
      }
    },
    "required": [
      "s5_outputs",
      "platform"
    ]
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "tool_matrix": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "role_id": {
              "type": "string"
            },
            "tool_name": {
              "type": "string"
            },
            "availability": {
              "type": "string",
              "enum": [
                "installed",
                "installable",
                "unavailable"
              ]
            },
            "fallback_prompt": {
              "type": "string"
            },
            "data_security_level": {
              "type": "string",
              "enum": [
                "low",
                "medium",
                "high"
              ]
            }
          }
        }
      },
      "integration_specs": {
        "type": "object"
      },
      "degradation_plan": {
        "type": "array"
      }
    },
    "required": [
      "tool_matrix",
      "integration_specs",
      "degradation_plan"
    ]
  },
  "tool_declarations": [],
  "few_shot_examples": [
    {
      "name": "正常流程(标准通道,A型内容传播,WorkBuddy)",
      "input": {
        "s5_outputs": {
          "roles": [
            {"agent_id": "content-strategist", "deliverables": ["图文笔记", "视频脚本"]},
            {"agent_id": "visual-designer", "deliverables": ["封面图", "信息图"]}
          ],
          "domain_type": "A",
          "platform": "workbuddy"
        },
        "platform": "workbuddy",
        "data_sensitivity": "低"
      },
      "output": {
        "tool_matrix": [
          {"role_id": "content-strategist", "tool_name": "WorkBuddy内置Markdown编辑", "availability": "installed", "fallback_prompt": "按模板撰写：标题+正文+CTA", "data_security_level": "low", "priority": 1},
          {"role_id": "visual-designer", "tool_name": "MCP:image-gen", "availability": "installable", "fallback_prompt": "生成提示词描述，由用户手动生成", "data_security_level": "low", "priority": 2}
        ],
        "status": "completed",
        "stage": 6,
        "next_action": "进入S7专家包生成"
      }
    },
    {
      "name": "异常场景(高敏感度+外部API数据安全拒绝)",
      "input": {
        "s5_outputs": {
          "roles": [
            {"agent_id": "financial-advisor", "deliverables": ["投资建议书"]},
            {"agent_id": "compliance-officer", "deliverables": ["合规审查意见"]}
          ],
          "domain_type": "B",
          "platform": "workbuddy",
          "regulated": true
        },
        "platform": "workbuddy",
        "data_sensitivity": "高"
      },
      "output": {
        "tool_matrix": [
          {"role_id": "financial-advisor", "tool_name": "WorkBuddy内置推理", "availability": "installed", "fallback_prompt": "基于公开数据，标注❓需核实", "data_security_level": "high", "priority": 1},
          {"role_id": "financial-advisor", "tool_name": "外部API:金融数据", "availability": "available_but_rejected", "fallback_prompt": "用户手动提供脱敏数据", "data_security_level": "high", "priority": 4, "rejection_reason": "高敏感度禁止外发"}
        ],
        "security_assessment": [{"tool": "外部API:金融数据", "risk": "🔴违反数据安全原则"}],
        "status": "completed_with_warnings",
        "stage": 6,
        "next_action": "进入S7(含数据安全协议)"
      }
    },
    {
      "name": "快速通道变体(低复杂度,纯提示词)",
      "input": {
        "s5_outputs": {
          "roles": [
            {"agent_id": "lifestyle-assistant", "deliverables": ["每日穿搭建议"]}
          ],
          "domain_type": "A",
          "platform": "workbuddy",
          "track": "快速通道"
        },
        "platform": "workbuddy",
        "data_sensitivity": "低"
      },
      "output": {
        "tool_matrix": [
          {"role_id": "lifestyle-assistant", "tool_name": "纯提示词方案", "availability": "always", "fallback_prompt": "你是一个生活方式顾问，根据场合/天气/偏好给出3套穿搭建议", "data_security_level": "low", "priority": 4}
        ],
        "status": "completed",
        "stage": 6,
        "next_action": "进入S7(快速通道简化版)"
      }
    }
  ],
  "knowledge_base_mount_points": [
    {
      "type": "static",
      "path": "file://pipeline/stage-6-rules",
      "description": "阶段6执行规则"
    },
    {
      "type": "dynamic",
      "path": "file://pipeline/stage-6-state",
      "description": "阶段6运行时状态"
    },
    {
      "type": "rag",
      "path": "file://rag/pipeline-s6-toolchain-matching/references",
      "description": "向量检索：源文档、平台规则和历史案例"
    }
  ],
  "dependencies": [
    "core-mental-model-engine"
  ],
  "execution_logic": "(1)从角色能力需求匹配工具→(2)评估工具可用性(已安装/可安装/不可用)→(3)为不可用工具设计纯提示词兜底→(4)工具数据安全评估(§5.5)→(5)调用protocol-tool-integration生成集成规范→(6)输出工具链方案。优先级：平台内置→MCP→外部API→纯提示词。纯提示词兜底强制：所有工具必须有纯提示词兜底方案。数据安全三原则：(1)高敏感度领域禁止敏感数据→第三方;(2)使用第三方必须注明数据流向;(3)每个工具评估数据安全等级。",
  "cascading_calls": [
    "core-mental-model-engine"
  ],
  "context_inheritance": [
    "s5_outputs"
  ],
  "shared_memory_keys": [
    "s6_decisions",
    "s6_snapshot"
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
    "next_stage": "pipeline-s7-expert-package-generation",
    "preconditions": [
      "所有工具均有兜底方案",
      "数据安全评估通过",
      "工具链对比矩阵已给出推荐理由"
    ],
    "blocking_rule": "高敏感数据外发风险未处理时不得进入S7。"
  }
}
