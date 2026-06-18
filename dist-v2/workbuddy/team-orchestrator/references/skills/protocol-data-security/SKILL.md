---
name: protocol-data-security
description: 评估每个工具数据安全等级，高敏感度领域禁止敏感数据→未授权第三方，使用第三方工具必须注明数据流向。 Use when: 用户说"protocol-data-security、数据安全协议、L2数据安全"等触发词。
---

# 数据安全协议

> **层级**: L2 | **版本**: 1.1.0 | **ID**: `protocol-data-security` | **中文名**: 数据安全协议 | **英文名**: Data Security Protocol
# 数据安全协议 (Data Security Protocol)

> **层级**: L2 | **版本**: 1.0.0 | **ID**: `protocol-data-security`
> **编排关系**: 本skill由 `team-orchestrator` 按需自动加载执行，属于全域专家团构建skills系统的内部组件，用户不应直接触发。

## 概述

评估每个工具数据安全等级，高敏感度领域禁止敏感数据→未授权第三方，使用第三方工具必须注明数据流向。

## 触发条件

当检测到以下关键词或场景时自动激活：数据安全, 敏感数据, 隐私, 第三方, 数据流向

## 输入规范 (input_schema)

```json
{
  "type": "object",
  "properties": {
    "tools": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": {
            "type": "string"
          },
          "data_type": {
            "type": "string"
          },
          "third_party": {
            "type": "boolean"
          },
          "data_flow": {
            "type": "string"
          }
        }
      }
    },
    "domain_sensitivity": {
      "type": "string",
      "enum": [
        "low",
        "medium",
        "high"
      ]
    }
  },
  "required": [
    "tools",
    "domain_sensitivity"
  ]
}
```

## 输出规范 (output_schema)

```json
{
  "type": "object",
  "properties": {
    "security_assessment": {
      "type": "array",
      "items": {
        "type": "object"
      }
    },
    "restrictions": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "compliance_notes": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  },
  "required": [
    "security_assessment",
    "restrictions",
    "compliance_notes"
  ]
}
```

## 工具声明 (tool_declarations)

本Skill无外部工具依赖，纯提示词可执行。

## 执行逻辑

(1)评估每个工具数据安全等级(低/中/高)→(2)高敏感度领域禁止敏感数据→未授权第三方→(3)使用第三方工具必须注明数据流向→(4)数据安全三原则贯穿。三原则：(1)高敏感度领域禁止敏感数据发送到未授权第三方;(2)使用第三方工具必须注明数据流向;(3)每个工具评估数据安全等级。三级防护：🟢低=内容创作/知识管理→可使用任何外部工具;🟡中=客户服务/服务交付→使用前须告知;🔴高=强监管行业→禁止外发+仅本地或纯提示词。

## Few-shot 示例

### 示例 1：金融T1防护 — 高敏感度阻断第三方

**输入**:
```json
{
  "tools": [
    { "name": "财务报表分析API", "data_type": "客户财务数据", "third_party": true, "data_flow": "本地→第三方API→返回分析" },
    { "name": "本地加密存储", "data_type": "客户身份信息", "third_party": false, "data_flow": "本地处理，不外传" }
  ],
  "domain_sensitivity": "high"
}
```

**输出**:
```json
{
  "security_assessment": [
    {
      "tool": "财务报表分析API",
      "risk_level": "high",
      "data_flow_documented": true,
      "approved": false,
      "reason": "金融客户数据禁止发送到未授权第三方"
    },
    {
      "tool": "本地加密存储",
      "risk_level": "low",
      "data_flow_documented": true,
      "approved": true
    }
  ],
  "restrictions": [
    "禁止将客户财务数据发送到财务报表分析API",
    "所有客户数据仅限本地处理，使用AES-256加密"
  ],
  "compliance_notes": [
    "金融行业T1级防护：任何涉及客户PII或财务数据的第三方工具均需阻断",
    "如必须使用第三方，需先获得用户书面授权并签署数据处理协议"
  ]
}
```

### 示例 2：教育T3防护 — 中等敏感度条件放行

**输入**:
```json
{
  "tools": [
    { "name": "学情分析平台", "data_type": "学生成绩数据", "third_party": true, "data_flow": "本地→云端分析→返回报告" },
    { "name": "在线测评工具", "data_type": "学生答题数据", "third_party": true, "data_flow": "本地→测评SaaS→返回评分" }
  ],
  "domain_sensitivity": "medium"
}
```

**输出**:
```json
{
  "security_assessment": [
    {
      "tool": "学情分析平台",
      "risk_level": "medium",
      "data_flow_documented": true,
      "approved": true,
      "condition": "已脱敏处理，不含学生真实姓名和身份证号"
    },
    {
      "tool": "在线测评工具",
      "risk_level": "medium",
      "data_flow_documented": true,
      "approved": true,
      "condition": "使用匿名ID替代真实身份"
    }
  ],
  "restrictions": [
    "使用前须告知用户数据将上传第三方平台",
    "学生姓名、身份证号等PII必须在本地脱敏后传输"
  ],
  "compliance_notes": [
    "教育行业T3级防护：允许脱敏后使用第三方工具",
    "建议在最终交付文档中标注'本系统使用的第三方服务清单及数据流向'"
  ]
}
```

### 示例 3：医疗阻断 — 违规外发强行阻断

**输入**:
```json
{
  "tools": [
    { "name": "公开AI翻译服务", "data_type": "患者病历全文", "third_party": true, "data_flow": "本地→公开翻译API→返回译文" }
  ],
  "domain_sensitivity": "high"
}
```

**输出**:
```json
{
  "security_assessment": [
    {
      "tool": "公开AI翻译服务",
      "risk_level": "critical",
      "data_flow_documented": true,
      "approved": false,
      "reason": "患者病历包含受HIPAA/《个人信息保护法》保护的敏感医疗数据，禁止发送到非授权第三方"
    }
  ],
  "restrictions": [
    "🔴 阻断：患者病历禁止发送到任何公开或非授权第三方服务",
    "替代方案：使用本地部署的开源翻译模型或脱敏后仅翻译非敏感字段",
    "如需第三方翻译，必须使用签署BAA(HIPAA业务伙伴协议)的合规服务"
  ],
  "compliance_notes": [
    "医疗行业最高级防护：任何包含PHI(受保护健康信息)的数据禁止外发",
    "建议交付文档明确标注'本项目不涉及患者隐私数据处理，如需处理请使用合规HIPAA工具链'"
  ]
}
```

## 知识库挂载点 (knowledge_base_mount_points)

- **[static]** `file://data-security/three-principles` — 数据安全三原则
- **[static]** `file://data-security/protection-levels` — 三级防护等级定义

## 依赖关系

- `core-mental-model-engine`

## 详细执行逻辑

```text
FUNCTION execute_protocol_data_security(input):
    ASSERT input.tools IS NOT EMPTY
    ASSERT input.domain_sensitivity IN ["low","medium","high"]

    // === 第一步：加载数据安全三原则 ===
    LOAD file://data-security/three-principles
    LOAD file://data-security/protection-levels
    // 三原则：
    //   原则1: 高敏感度领域禁止敏感数据发送到未授权第三方
    //   原则2: 使用第三方工具必须注明数据流向
    //   原则3: 每个工具评估数据安全等级

    security_assessment = []
    restrictions = []
    compliance_notes = []

    // === 第二步：评估每个工具的数据安全等级 ===
    FOR tool IN input.tools:
        assessment = {}
        assessment.tool = tool.name

        // 评估工具数据安全等级(低/中/高)
        IF tool.data_type CONTAINS PII_OR_SENSITIVE:
            assessment.risk_level = "high"
        ELIF tool.data_type CONTAINS BUSINESS_DATA:
            assessment.risk_level = "medium"
        ELSE:
            assessment.risk_level = "low"

        // 检查数据流向是否已文档化(原则2)
        IF tool.data_flow IS NOT EMPTY:
            assessment.data_flow_documented = true
        ELSE:
            assessment.data_flow_documented = false
            APPEND restrictions WITH "工具'" + tool.name + "'未注明数据流向，须补充"

        // === 第三步：三级防护决策 ===
        IF input.domain_sensitivity == "high":
            // 🔴高=强监管行业→禁止外发+仅本地或纯提示词
            IF tool.third_party == true:
                assessment.approved = false
                assessment.reason = "高敏感度领域禁止敏感数据发送到未授权第三方(原则1)"
                APPEND restrictions WITH "🔴阻断: " + tool.data_type + "禁止发送到" + tool.name
                APPEND compliance_notes WITH "替代方案: 使用本地部署工具或脱敏后仅处理非敏感字段"
                // 高敏感用户坚持用第三方的特殊处理
                APPEND compliance_notes WITH "如必须使用第三方，需先获得用户书面授权并签署数据处理协议"
            ELSE:
                assessment.approved = true
                APPEND compliance_notes WITH "本地处理已批准，建议使用AES-256加密"

        ELIF input.domain_sensitivity == "medium":
            // 🟡中=客户服务/服务交付→使用前须告知
            IF tool.third_party == true:
                // 检查是否已脱敏
                IF tool.data_type CONTAINS PII_AND_NOT_DESENSITIZED:
                    assessment.approved = true
                    assessment.condition = "须脱敏处理后使用，不含真实姓名和身份证号"
                    APPEND restrictions WITH "使用前须告知用户数据将上传第三方平台"
                    APPEND restrictions WITH "姓名、身份证号等PII必须在本地脱敏后传输"
                ELSE:
                    assessment.approved = true
                    assessment.condition = "已脱敏处理，可安全使用"
            ELSE:
                assessment.approved = true

        ELIF input.domain_sensitivity == "low":
            // 🟢低=内容创作/知识管理→可使用任何外部工具
            assessment.approved = true
            IF tool.third_party == true:
                APPEND compliance_notes WITH "低敏感度场景，第三方工具使用已放行"

        APPEND security_assessment WITH assessment

    // === 第四步：汇总三级防护结果与合规建议 ===
    high_risk_tools = FILTER(security_assessment, a => a.risk_level == "high" AND a.approved == false)
    IF LENGTH(high_risk_tools) > 0:
        APPEND compliance_notes WITH "⚠️ 存在" + LENGTH(high_risk_tools) + "个高风险工具被阻断，必须在交付文档中标注数据安全限制"

    medium_risk_third_party = FILTER(security_assessment, a => a.third_party == true AND input.domain_sensitivity == "medium")
    IF LENGTH(medium_risk_third_party) > 0:
        APPEND compliance_notes WITH "建议在最终交付文档中标注'本系统使用的第三方服务清单及数据流向'"

    // === 第五步：最终断言与输出 ===
    ASSERT LENGTH(security_assessment) > 0
    ASSERT LENGTH(restrictions) >= 0

    CALL protocol-quality-gate before final output
    RETURN {security_assessment, restrictions, compliance_notes}
```

## 版本

1.0.0

---
*本Skill由全域专家团构建skills体系自动生成，版本1.0.0，日期2026-06-15*
