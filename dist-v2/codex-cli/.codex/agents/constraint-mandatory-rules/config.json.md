{
  "id": "constraint-mandatory-rules",
  "layer": "L4",
  "name_zh": "强制执行规则(不可覆盖)",
  "name_en": "Mandatory Rules",
  "version": "1.1.0",
  "description": "全程横贯，任何Skill执行时受此约束。21条强制规则不可覆盖。",
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
        "decision": "强制执行规则(不可覆盖)已按A型内容传播场景执行",
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
      "path": "file://constraints/constraint-mandatory-rules",
      "description": "强制执行规则(不可覆盖)完整规则集"
    },
    {
      "type": "dynamic",
      "path": "file://runtime/constraint-mandatory-rules/state",
      "description": "运行时状态、用户确认和阶段快照"
    },
    {
      "type": "rag",
      "path": "file://rag/constraint-mandatory-rules/references",
      "description": "向量检索：源文档、平台规则和历史案例"
    }
  ],
  "dependencies": [
    "protocol-confirmation-node",
    "protocol-single-question-guidance"
  ],
  "execution_logic": "20条强制规则：(1)交付物优先(先定义交付物再定义角色);(2)MECE强制(5.2三问必须通过);(3)合规不可绕过;(4)平台可执行强制;(5)分线强制(不同渠道下游分线);(6)阶段跳转约束(满足条件才能进下阶段);(7)字段追踪强制(一一对应);(8)单问规则(信息采集每次1问);(9)规范优先级(法规>平台>服务>品牌);(10)合规时效性(最新规则为准);(11)数据安全强制;(12)复杂度通道约束(可升不可降);(13)术语翻译强制(首次出现附通俗解释);(14)选项覆盖检查;(15)专家包格式合规;(16)专家命名合规(kebab-case+2-3字花名);(17)平台元数据完整(categoryId/tags3/quickPrompts3/40-50字描述);(18)Team型协作合规(≥4人Team型);(19)版本迭代触发信号(用户主动可感知事件);(20)输出可验证性(关键判断标注确定性等级和参考来源方向)",
  "cascading_calls": [
    "protocol-confirmation-node",
    "protocol-single-question-guidance"
  ],
  "context_inheritance": [
    "all_stage_outputs"
  ],
  "shared_memory_keys": [
    "constraint-mandatory-rules_violations"
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