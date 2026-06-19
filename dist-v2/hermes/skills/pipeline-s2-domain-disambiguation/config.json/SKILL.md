{
  "id": "pipeline-s2-domain-disambiguation",
  "layer": "L1",
  "name_zh": "阶段二：领域分类与消歧",
  "name_en": "Stage 2: Domain Disambiguation",
  "version": "1.1.0",
  "description": "调用core-domain-classifier，4维度逐个消解歧义(领域本体/目标用户/交付形式/交付渠道)，输出领域确认卡。歧义消解强确认。",
  "trigger_keywords": [
    "领域确认",
    "分类",
    "什么型",
    "A型",
    "B型",
    "歧义"
  ],
  "input_schema": {
    "type": "object",
    "properties": {
      "s1_outputs": {
        "type": "object",
        "description": "S1需求画像输出"
      },
      "domain_suggestion": {
        "type": "object",
        "description": "core-domain-classifier输出"
      }
    },
    "required": [
      "s1_outputs",
      "domain_suggestion"
    ]
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "domain_profile": {
        "type": "object",
        "description": "领域画像(替代原confirmed_domain单一枚举，支持多标签组合+时序演化)",
        "properties": {
          "primary_domain": {
            "type": "string",
            "enum": ["A", "B", "C", "D", "F"],
            "description": "主领域类型(不再有E型，E型改为A-F的组合标记)"
          },
          "secondary_domains": {
            "type": "array",
            "items": {
              "type": "string",
              "enum": ["A", "B", "C", "D", "F"]
            },
            "description": "次领域类型(可选0-2个标签，与primary_domain不可重复)"
          },
          "domain_evolution": {
            "type": "object",
            "description": "领域时序演化规划(可选，仅当业务有明显阶段变化时填写)",
            "properties": {
              "phase_1_cold_start": {"type": "string", "description": "冷启动期领域标签，如'A'"},
              "phase_2_growth": {"type": "string", "description": "成长期领域标签，如'A+C'"},
              "phase_3_mature": {"type": "string", "description": "成熟期领域标签，如'A+C+F'"}
            }
          }
        },
        "required": ["primary_domain"]
      },
      "confirmed_domain": {
        "type": "string",
        "enum": ["A", "B", "C", "D", "E", "F"],
        "description": "[向后兼容] 原单一领域类型，当secondary_domains为空时等于primary_domain；当secondary_domains非空时为'E'。下游Skill应优先使用domain_profile。"
      },
      "disambiguation_log": {
        "type": "array",
        "items": {
          "type": "string"
        }
      },
      "compliance_activation_map": {
        "type": "object",
        "properties": {
          "4.1": {
            "type": "object",
            "properties": {
              "level": {"type": "string", "enum": ["none", "warning", "mandatory"]},
              "sensitive_categories": {"type": "array", "items": {"type": "string"}}
            }
          },
          "4.2": {
            "type": "object",
            "properties": {
              "level": {"type": "string", "enum": ["none", "warning", "mandatory"]},
              "sensitive_words": {"type": "object", "description": "按领域的敏感词注册表"}
            }
          },
          "4.3": {
            "type": "object",
            "properties": {
              "level": {"type": "string", "enum": ["none", "warning", "mandatory"]},
              "regulations": {"type": "array", "items": {"type": "string"}, "description": "适用法规列表如GDPR/PIPL/CCPA"},
              "data_residency": {"type": "string", "enum": ["CN", "EU", "US", "multi_region"]}
            }
          },
          "4.4": {
            "type": "object",
            "properties": {
              "level": {"type": "string", "enum": ["none", "warning", "mandatory"]},
              "trigger_conditions": {"type": "array", "items": {"type": "string"}}
            }
          },
          "4.5": {
            "type": "object",
            "properties": {
              "level": {"type": "string", "enum": ["none", "warning", "mandatory"]},
              "data_categories": {"type": "array", "items": {"type": "string"}}
            }
          }
        }
      },
      "feedback_loops_required": {
        "type": "array",
        "items": {
          "type": "string"
        }
      }
    },
    "required": [
      "domain_profile",
      "confirmed_domain",
      "disambiguation_log",
      "compliance_activation_map",
      "feedback_loops_required"
    ]
  },
  "tool_declarations": [],
  "few_shot_examples": [
    {
      "name": "正常流程 - 小红书美食团队(A型)",
      "input": {
        "s1_outputs": {
          "core_need": "自动化美食探店内容生产",
          "keywords": ["小红书", "图文", "探店", "美食"],
          "team_size": 1
        },
        "domain_suggestion": {
          "domain_type": "A",
          "domain_name": "内容传播型",
          "confidence": "high"
        }
      },
      "output": {
        "domain_profile": {
          "primary_domain": "A",
          "secondary_domains": []
        },
        "confirmed_domain": "A",
        "disambiguation_log": [
          "领域本体: 内容创作与传播-美食探店 → 确认",
          "目标用户: 小红书年轻女性用户 → 确认",
          "交付形式: 图文笔记+品牌合作帖 → 确认",
          "交付渠道: 小红书发现页 → 确认"
        ],
        "compliance_activation_map": {
          "4.1": {"level": "warning", "sensitive_categories": ["食品安全广告", "探店类内容"]},
          "4.2": {"level": "none", "sensitive_words": {}},
          "4.3": {"level": "none", "regulations": [], "data_residency": "CN"},
          "4.4": {"level": "none", "trigger_conditions": []},
          "4.5": {"level": "none", "data_categories": []}
        },
        "feedback_loops_required": ["内容效果反馈", "用户互动数据"]
      }
    },
    {
      "name": "异常流程 - 医疗科普+客服(A/F混合)",
      "input": {
        "s1_outputs": {
          "core_need": "医疗健康科普+在线问诊",
          "keywords": ["医疗", "科普", "在线问诊", "健康"],
          "team_size": 3
        },
        "domain_suggestion": {
          "domain_type": "E",
          "domain_name": "混合型(A+F)",
          "confidence": "medium",
          "ambiguity": "同时涉及内容传播和客户服务"
        }
      },
      "output": {
        "domain_profile": {
          "primary_domain": "A",
          "secondary_domains": ["F"]
        },
        "confirmed_domain": "E",
        "disambiguation_log": [
          "领域本体: 医疗科普(A) + 在线问诊(F) → 确认混合型E",
          "目标用户: 患者及家属 → 确认",
          "交付形式: 科普文章+问诊对话 → 确认",
          "交付渠道: 公众号+小程序 → 确认"
        ],
        "compliance_activation_map": {
          "4.1": {"level": "warning", "sensitive_categories": ["医疗广告", "诊疗建议", "药品信息"]},
          "4.2": {"level": "warning", "sensitive_words": {"医疗": ["处方", "治愈率", "疗效保证", "根治", "无副作用"]}},
          "4.3": {"level": "mandatory", "regulations": ["广告法", "药品管理法"], "data_residency": "CN"},
          "4.4": {"level": "mandatory", "trigger_conditions": ["涉及诊疗建议", "药品信息发布"]},
          "4.5": {"level": "warning", "data_categories": ["用户健康数据", "问诊记录"]}
        },
        "feedback_loops_required": ["内容合规审查", "问诊质量监控", "用户满意度"]
      }
    },
    {
      "name": "快速通道 - 个人财税科普号(A型直接确认)",
      "input": {
        "s1_outputs": {
          "core_need": "财税科普内容自动化生产",
          "keywords": ["财税", "科普", "小红书", "公众号"],
          "team_size": 1
        },
        "domain_suggestion": {
          "domain_type": "A",
          "domain_name": "内容传播型",
          "confidence": "high"
        }
      },
      "output": {
        "domain_profile": {
          "primary_domain": "A",
          "secondary_domains": []
        },
        "confirmed_domain": "A",
        "disambiguation_log": [
          "领域本体: 内容创作与传播-财税科普 → 无歧义",
          "目标用户: 小微企业主/财务人员 → 确认",
          "交付形式: 小红书图文+公众号长文 → 确认",
          "交付渠道: 小红书+微信公众号 → 确认"
        ],
        "compliance_activation_map": {
          "4.1": {"level": "warning", "sensitive_categories": ["财税建议", "投资建议"]},
          "4.2": {"level": "warning", "sensitive_words": {"金融": ["保本", "稳赚", "内部消息", "代客理财", "100%收益"]}},
          "4.3": {"level": "warning", "regulations": ["广告法"], "data_residency": "CN"},
          "4.4": {"level": "none", "trigger_conditions": []},
          "4.5": {"level": "none", "data_categories": []}
        },
        "feedback_loops_required": ["内容效果反馈"]
      }
    }
  ],
  "knowledge_base_mount_points": [
    {
      "type": "static",
      "path": "file://pipeline/stage-2-rules",
      "description": "阶段2执行规则"
    },
    {
      "type": "dynamic",
      "path": "file://pipeline/stage-2-state",
      "description": "阶段2运行时状态"
    },
    {
      "type": "rag",
      "path": "file://rag/pipeline-s2-domain-disambiguation/references",
      "description": "向量检索：源文档、平台规则和历史案例"
    }
  ],
  "dependencies": [
    "core-mental-model-engine",
    "core-domain-classifier",
    "core-complexity-channel-selector",
    "protocol-single-question-guidance",
    "protocol-confirmation-node",
    "protocol-quality-gate"
  ],
  "mandatory_calls": [
    {
      "trigger": "every_interaction",
      "call": "core-domain-classifier.execute",
      "timing": "before_ask"
    },
    {
      "trigger": "stage_end",
      "call": "core-state-management-engine.update_snapshot",
      "timing": "after_output"
    }
  ],
  "execution_logic": "(1)调用core-domain-classifier→(2)输出领域确认卡(含6种类型选项)→(3)如用户选择与AI建议不同,记录偏差→(4)歧义消解强确认(若用户选择与AI建议不一致，必须明确确认'确认选择X型,而非AI建议的Y型')→(5)确定合规激活条件→(6)调用core-complexity-channel-selector确定通道。",
  "cascading_calls": [
    "core-domain-classifier",
    "protocol-confirmation-node"
  ],
  "context_inheritance": [
    "s1_outputs"
  ],
  "shared_memory_keys": [
    "s2_decisions",
    "s2_snapshot"
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
  "priority": 2,
  "stage_guard": {
    "next_stage": "pipeline-s3-chain-decomposition",
    "preconditions": [
      "领域类型A-F已确认",
      "歧义消解4维度无未决项",
      "合规激活条件已记录"
    ],
    "blocking_rule": "用户选择与AI建议不一致时必须强确认。"
  }
}
