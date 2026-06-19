{
  "id": "pipeline-s8-platform-execution",
  "layer": "L1",
  "name_zh": "阶段八：平台执行",
  "name_en": "Stage 8: Platform Execution",
  "version": "1.1.0",
  "description": "平台注册/部署指导、验证测试(含合规测试词库+分级失效判定)、交付确认(含迭代路径说明)。",
  "trigger_keywords": [
    "部署",
    "注册",
    "上线",
    "执行",
    "验证",
    "测试"
  ],
  "input_schema": {
    "type": "object",
    "properties": {
      "s7_outputs": {
        "type": "object",
        "description": "S7专家包输出"
      },
      "platform": {
        "type": "string"
      }
    },
    "required": [
      "s7_outputs",
      "platform"
    ]
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "execution_result": {
        "type": "object"
      },
      "delivery_confirmation": {
        "type": "object"
      },
      "rollback_snapshot": {
        "type": "object"
      }
    },
    "required": [
      "execution_result",
      "delivery_confirmation",
      "rollback_snapshot"
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
        "decision": "阶段八：平台执行已按A型内容传播场景执行",
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
      "path": "file://pipeline/stage-8-rules",
      "description": "阶段8执行规则"
    },
    {
      "type": "dynamic",
      "path": "file://pipeline/stage-8-state",
      "description": "阶段8运行时状态"
    },
    {
      "type": "rag",
      "path": "file://rag/pipeline-s8-platform-execution/references",
      "description": "向量检索：源文档、平台规则和历史案例"
    }
  ],
  "dependencies": [
    "core-mental-model-engine"
  ],
  "execution_logic": "(1)平台注册/部署指导(8.1)→(2)验证测试(8.2-8.5,含合规测试词库)→(3)交付确认(8.6,含迭代路径说明)→(4)输出交付确认单。验证测试分级失效判定：完全通过→正常使用;部分失效(非核心功能)→标注+提供修复方案;核心功能失效→阻断,返回S7修复。版本迭代触发信号：用户主动可感知事件(用户说'做不了X'/'想要新能力'/'我想升级')。",
  "cascading_calls": [
    "core-mental-model-engine"
  ],
  "context_inheritance": [
    "s7_outputs"
  ],
  "shared_memory_keys": [
    "s8_decisions",
    "s8_snapshot"
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
      },
      {
        "callee": "protocol-error-handling",
        "when": "平台部署或验证失败时",
        "reason": "Doc1 CROSS_SKILL_PROTOCOL: 执行失败 -> 验证/回退"
      }
    ]
  },
  "compatibility": {
    "min_compatible": "1.1.0",
    "breaking_change": "2.0.0"
  },
  "priority": 1,
  "stage_guard": {
    "next_stage": "delivery",
    "preconditions": [
      "平台部署或导入验证已通过",
      "合规测试词库通过",
      "交付确认单包含已知限制和迭代路径"
    ],
    "blocking_rule": "核心功能失效必须返回S7修复。"
  }
}
