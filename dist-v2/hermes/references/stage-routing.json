{
  "description": "阶段路由配置 — 定义S1→S8的阶段衔接规则、前置条件、快速通道简化策略",
  "version": "1.0.0",
  "stages": [
    {
      "id": "S1",
      "skill_id": "pipeline-s1-need-diving",
      "name": "需求深潜",
      "next_stage": "S2",
      "preconditions": [],
      "quality_gate_required": true,
      "confirmation_required": true,
      "fast_channel_simplification": null
    },
    {
      "id": "S2",
      "skill_id": "pipeline-s2-domain-disambiguation",
      "name": "领域分类与消歧",
      "next_stage": "S3",
      "preconditions": ["需求画像卡已生成", "用户已确认核心需求", "复杂度初评已完成"],
      "quality_gate_required": true,
      "confirmation_required": true,
      "fast_channel_simplification": null
    },
    {
      "id": "S3",
      "skill_id": "pipeline-s3-chain-decomposition",
      "name": "链路拆解",
      "next_stage": "S4",
      "preconditions": ["领域确认卡已生成", "domain_type已确定"],
      "quality_gate_required": true,
      "confirmation_required": false,
      "fast_channel_simplification": {
        "mode": "simplify",
        "strategy": "单链路直通，不拆子链路",
        "minimal_output": {
          "chain_list": [{"name": "main_chain", "steps": ["input -> process -> output"]}]
        }
      }
    },
    {
      "id": "S4",
      "skill_id": "pipeline-s4-deliverable-anchoring",
      "name": "交付物锚定",
      "next_stage": "S5",
      "preconditions": ["链路骨架节点已生成"],
      "quality_gate_required": true,
      "confirmation_required": true,
      "fast_channel_simplification": null
    },
    {
      "id": "S5",
      "skill_id": "pipeline-s5-architecture-design",
      "name": "架构设计",
      "next_stage": "S6",
      "preconditions": ["交付物清单已锚定", "优先级已分配", "Q9平台已强制确认"],
      "quality_gate_required": true,
      "confirmation_required": true,
      "fast_channel_simplification": {
        "mode": "simplify",
        "strategy": "单人角色，不设计SOP和反馈回路",
        "minimal_output": {
          "roles": [{"name": "主理人", "covers": "全链路"}],
          "sop": "skip",
          "feedback_loops": []
        }
      }
    },
    {
      "id": "S6",
      "skill_id": "pipeline-s6-toolchain-matching",
      "name": "工具链匹配",
      "next_stage": "S7",
      "preconditions": ["角色清单已生成", "MECE校验通过"],
      "quality_gate_required": true,
      "confirmation_required": true,
      "fast_channel_simplification": null
    },
    {
      "id": "S7",
      "skill_id": "pipeline-s7-expert-package-generation",
      "name": "专家包生成",
      "next_stage": "S8",
      "preconditions": ["工具链已匹配", "每个工具均有纯提示词兜底方案"],
      "quality_gate_required": true,
      "confirmation_required": true,
      "fast_channel_simplification": {
        "mode": "simplify",
        "strategy": "仅激活quality-gate + output-format，跳过其他L2协议",
        "minimal_protocols": ["protocol-quality-gate", "constraint-output-format"]
      }
    },
    {
      "id": "S8",
      "skill_id": "pipeline-s8-platform-execution",
      "name": "平台执行",
      "next_stage": null,
      "preconditions": ["专家包已生成", "四步确认门通过"],
      "quality_gate_required": true,
      "confirmation_required": false,
      "fast_channel_simplification": null
    }
  ],
  "channel_resolution": {
    "description": "通道路由判定规则 — 根据S1初评和S2领域分类的联合结果确定最终通道",
    "rules": [
      {"condition": "is_regulated == true", "channel": "strict", "reason": "强监管领域强制strict"},
      {"condition": "initial_hint == 'fast' AND complexity == 'low'", "channel": "fast"},
      {"condition": "initial_hint == 'strict' OR complexity == 'high'", "channel": "strict"},
      {"condition": "default", "channel": "standard"}
    ],
    "upgrade_allowed": true,
    "downgrade_allowed": false,
    "downgrade_exception": "用户明确声明理解风险时可降级"
  },
  "l2_activation_source": "knowledge/protocol-activation-map.json",
  "l3_activation_rule": "仅激活目标平台对应的单个L3适配器",
  "l0_l4_activation_rule": "全程自动激活，无需条件判断"
}
