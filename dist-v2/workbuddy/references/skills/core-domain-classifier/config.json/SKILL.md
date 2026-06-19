{
  "id": "core-domain-classifier",
  "layer": "L0",
  "name_zh": "领域分类器",
  "name_en": "Domain Classifier",
  "version": "1.4.0",
  "description": "基于S1需求提取关键词，匹配六种领域类型矩阵(A/B/C/D/E/F)，如有歧义使用ToT多方案比较，输出领域确认卡。",
  "trigger_keywords": [
    "领域分类",
    "什么类型",
    "A型B型",
    "内容传播",
    "服务交付",
    "流程自动化",
    "混合型"
  ],
  "input_schema": {
    "type": "object",
    "properties": {
      "s1_summary": {
        "type": "string",
        "description": "S1需求摘要"
      },
      "keywords": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "description": "关键词列表"
      }
    },
    "required": [
      "s1_summary",
      "keywords"
    ]
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "domain_type": {
        "type": "string",
        "enum": [
          "A",
          "B",
          "C",
          "D",
          "E",
          "F"
        ]
      },
      "domain_name": {
        "type": "string"
      },
      "sub_domain": {
        "type": "string"
      },
      "compliance_activation": {
        "type": "object",
        "properties": {
          "4.1": {
            "type": "boolean"
          },
          "4.2": {
            "type": "array",
            "items": {
              "type": "string"
            }
          },
          "4.3": {
            "type": "boolean"
          },
          "4.4": {
            "type": "boolean"
          },
          "4.5": {
            "type": "boolean"
          }
        }
      },
      "feedback_loop_types": {
        "type": "array",
        "items": {
          "type": "string"
        }
      }
    },
    "required": [
      "domain_type",
      "domain_name",
      "compliance_activation",
      "feedback_loop_types"
    ]
  },
  "tool_declarations": [],
  "few_shot_examples": [
    {
      "name": "正常流程(A型内容传播)",
      "input": {
        "s1_summary": "做小红书美食探店，每天发图文笔记",
        "keywords": [
          "小红书",
          "图文",
          "探店",
          "美食"
        ]
      },
      "output": {
        "domain_type": "A",
        "domain_name": "内容传播型",
        "sub_domain": "自媒体内容获客",
        "compliance_activation": {
          "4.1": true,
          "4.2": [],
          "4.3": true,
          "4.4": false,
          "4.5": false
        },
        "feedback_loop_types": [
          "内容效果反馈"
        ]
      }
    },
    {
      "name": "正常流程(D型流程自动化)",
      "input": {
        "s1_summary": "自动采集行业数据生成周报",
        "keywords": [
          "自动",
          "数据",
          "报告",
          "采集"
        ]
      },
      "output": {
        "domain_type": "D",
        "domain_name": "流程自动化型",
        "sub_domain": "数据采集报告自动化",
        "compliance_activation": {
          "4.1": false,
          "4.2": [],
          "4.3": false,
          "4.4": false,
          "4.5": false
        },
        "feedback_loop_types": [
          "执行成功率"
        ]
      }
    },
    {
      "name": "快速通道变体(E型混合:B/F辨析)",
      "input": {
        "s1_summary": "帮律师所做法律咨询获客，在小红书发普法内容，然后私信里做付费法律咨询",
        "keywords": [
          "法律",
          "咨询",
          "小红书",
          "获客",
          "付费",
          "私信"
        ]
      },
      "output": {
        "domain_type": "E",
        "domain_name": "混合型(A+B)",
        "sub_domain": "内容获客+专业服务交付",
        "compliance_activation": {
          "4.1": true,
          "4.2": [
            "法律咨询"
          ],
          "4.3": true,
          "4.4": true,
          "4.5": false
        },
        "feedback_loop_types": [
          "内容效果反馈",
          "客户反馈→服务优化"
        ],
        "classification_reasoning": "同时包含A型(内容传播获客)和B型(付费法律咨询)。B/F辨析:有明确'法律咨询项目/订单'概念→B而非F。E型处理:取A∪B子协议并集。"
      }
    }
  ],
  "knowledge_base_mount_points": [
    {
      "type": "static",
      "path": "file://domain-matrix/classification-rules",
      "description": "六种领域类型分类矩阵"
    },
    {
      "type": "static",
      "path": "file://domain-matrix/compliance-activation-map",
      "description": "领域类型→合规协议条件激活映射"
    },
    {
      "type": "dynamic",
      "path": "file://runtime/core-domain-classifier/state",
      "description": "运行时状态、用户确认和阶段快照"
    },
    {
      "type": "rag",
      "path": "file://rag/core-domain-classifier/references",
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
  "execution_logic": "(1)基于S1需求提取关键词→(2)匹配六种领域类型矩阵→(3)如有歧义使用ToT多方案比较→(4)输出领域确认卡(含歧义消解过程)。\n六种领域类型：A=内容传播型, B=服务交付型, C=知识管理型, D=流程自动化型, E=混合型(含D/F), F=客户服务型。\nB vs F辨析：有明确\"项目/订单\"概念→B，持续无终点→F。\nE型处理：识别包含的子类型，按并集激活子协议。\n歧义消解强确认：若用户选择与AI建议不一致，必须明确确认\"确认选择X型,而非AI建议的Y型\"。",
  "cascading_calls": [
    "core-mental-model-engine"
  ],
  "context_inheritance": [
    "s1_need_portrait"
  ],
  "shared_memory_keys": [
    "domain_type",
    "compliance_activation_map"
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