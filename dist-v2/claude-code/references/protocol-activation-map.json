{
  "description": "L2协议激活映射矩阵 — 根据domain_type × channel × stage三维组合按需激活协议子集。I-2.9修复：外部化替代概念性引用。改进#6修复：协议名全部使用完整Skill ID。",
  "version": "1.1.0",
  "protocol_activation_matrix": {
    "A_fast_S7":    ["protocol-quality-gate", "constraint-output-format"],
    "A_standard_S7": ["protocol-quality-gate", "protocol-compliance-engine", "constraint-output-format", "constraint-naming-convention"],
    "A_strict_S7":   ["protocol-quality-gate", "protocol-compliance-engine", "protocol-data-security", "constraint-output-format", "constraint-naming-convention", "constraint-tool-integration"],
    "B_fast_S7":     ["protocol-quality-gate", "constraint-output-format"],
    "B_standard_S7": ["protocol-quality-gate", "protocol-compliance-engine", "constraint-output-format", "constraint-naming-convention", "constraint-tool-integration"],
    "B_strict_S7":   ["protocol-quality-gate", "protocol-compliance-engine", "protocol-data-security", "protocol-error-handling", "constraint-output-format", "constraint-naming-convention", "constraint-tool-integration", "protocol-human-approval"],
    "C_fast_S7":     ["protocol-quality-gate", "constraint-output-format"],
    "C_standard_S7": ["protocol-quality-gate", "protocol-compliance-engine", "constraint-output-format", "constraint-naming-convention", "constraint-tool-integration", "protocol-automation-trigger"],
    "C_strict_S7":   ["protocol-quality-gate", "protocol-compliance-engine", "protocol-data-security", "constraint-output-format", "constraint-naming-convention", "constraint-tool-integration", "protocol-human-approval"],
    "D_fast_S7":     ["protocol-quality-gate", "constraint-output-format"],
    "D_standard_S7": ["protocol-quality-gate", "constraint-output-format", "constraint-naming-convention", "protocol-automation-trigger", "constraint-tool-integration"],
    "D_strict_S7":   ["protocol-quality-gate", "protocol-compliance-engine", "protocol-data-security", "constraint-output-format", "constraint-naming-convention", "constraint-tool-integration", "protocol-human-approval"],
    "F_fast_S7":     ["protocol-quality-gate", "constraint-output-format", "constraint-naming-convention"],
    "F_standard_S7": ["protocol-quality-gate", "protocol-compliance-engine", "constraint-output-format", "constraint-naming-convention", "protocol-error-handling", "protocol-feedback-loop"],
    "F_strict_S7":   ["protocol-quality-gate", "protocol-compliance-engine", "protocol-data-security", "protocol-error-handling", "protocol-feedback-loop", "constraint-output-format", "constraint-naming-convention", "constraint-tool-integration", "protocol-human-approval", "protocol-knowledge-persistence"],
    "_fallback":      ["protocol-quality-gate", "constraint-output-format"]
  },
  "fallback_rule": "未命中key时使用_fallback最小集，混合型取所有domain_tag对应的协议并集后去重",
  "protocol_call_order": [
    "protocol-compliance-engine",
    "protocol-data-security",
    "protocol-quality-gate",
    "constraint-naming-convention",
    "constraint-output-format",
    "constraint-tool-integration",
    "protocol-error-handling",
    "protocol-feedback-loop",
    "protocol-human-approval",
    "protocol-knowledge-persistence"
  ]
}
