{
  "id": "constraint-output-format",
  "layer": "L4",
  "name_zh": "输出格式规范",
  "name_en": "Output Format",
  "version": "1.3.0",
  "description": "方案文档14必含章节。v1.3.0新增标准输出结构模板与输出溯源参考指引。Markdown格式，Mermaid数据流，JSON Schema，条件激活标注。",
  "trigger_keywords": [
    "规则",
    "约束",
    "强制",
    "规范",
    "命名"
  ],
  "input_schema": {
    "type": "object",
    "properties": {
      "target_check": {
        "type": "string",
        "description": "待检查的目标内容"
      },
      "context": {
        "type": "object",
        "description": "检查上下文"
      }
    },
    "required": [
      "target_check"
    ]
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "compliant": {
        "type": "boolean"
      },
      "violations": {
        "type": "array",
        "items": {
          "type": "object"
        }
      },
      "suggestions": {
        "type": "array",
        "items": {
          "type": "string"
        }
      }
    },
    "required": [
      "compliant",
      "violations",
      "suggestions"
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
        "decision": "输出格式规范已按A型内容传播场景执行",
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
      "path": "file://constraints/constraint-output-format",
      "description": "输出格式规范完整规则集"
    },
    {
      "type": "dynamic",
      "path": "file://runtime/constraint-output-format/state",
      "description": "运行时状态、用户确认和阶段快照"
    },
    {
      "type": "rag",
      "path": "file://rag/constraint-output-format/references",
      "description": "向量检索：源文档、平台规则和历史案例"
    }
  ],
  "dependencies": [
    "core-symbol-system"
  ],
  "execution_logic": "方案文档14必含章节：(1)专家包概览;(2)各专家详细配置;(3)数据流总图(Mermaid);(4)质量门控协议;(5)信息准确性保障;(6)内容合规保障(条件激活);(7)数据安全与隐私;(8)异常处理;(9)反馈闭环;(10)知识资产沉淀;(11)人类介入节点;(12)迭代路线图+迁移指南;(13)执行计划;(14)架构健康检查报告。格式约定：Markdown;数据流Mermaid;Schema用JSON;表格Markdown;条件激活标注'【X型激活】';技术术语首次附通俗解释",
  "cascading_calls": [
    "core-symbol-system"
  ],
  "context_inheritance": [
    "all_stage_outputs"
  ],
  "shared_memory_keys": [
    "constraint-output-format_violations"
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
  "mandatory_calls": [
    {
      "callee": "protocol-quality-gate",
      "when": "阶段结束或产出方案前",
      "reason": "Doc1 CROSS_SKILL_PROTOCOL: ANY_SKILL -> SK-001"
    }
  ],
  "compatibility": {
    "min_compatible": "1.0.0",
    "breaking_change": "2.0.0"
  },
  "priority": 4
}