---
name: pipeline-s2-domain-disambiguation
id: "pipeline-s2-domain-disambiguation"
layer: "L1"
name_zh: "阶段二：领域分类与消歧"
name_en: "Stage 2: Domain Disambiguation"
version: "1.1.0"
description: 调用core-domain-classifier，4维度逐个消解歧义(领域本体/目标用户/交付形式/交付渠道)，输出领域确认卡(支持多标签组合+时序演化)。歧义消解强确认。
agent_created: true
trigger_keywords: ["S2执行", "领域确认", "分类消歧", "标签组合", "领域画像"]
dependencies: ["core-mental-model-engine", "core-domain-classifier", "core-complexity-channel-selector", "protocol-single-question-guidance", "protocol-confirmation-node", "protocol-quality-gate"]
---

# 阶段二：领域分类与消歧 (Stage 2: Domain Disambiguation)

> **层级**: L1 | **版本**: 1.1.0 | **ID**: `pipeline-s2-domain-disambiguation`
> **编排关系**: 本skill由 `team-orchestrator` 自动加载执行，用户不应直接触发。承接 `pipeline-s1-need-diving` 的输出，完成后自动衔接 `pipeline-s3-chain-decomposition`。

## 概述

调用core-domain-classifier，4维度逐个消解歧义(领域本体/目标用户/交付形式/交付渠道)，输出领域确认卡。歧义消解强确认。

## 触发条件

当检测到以下关键词或场景时自动激活：领域确认, 分类, 什么型, A型, B型, 歧义

## 输入规范 (input_schema)

```json
{
  "type": "object",
  "properties": {
    "s1_outputs": {
      "type": "object",
      "description": "S1需求画像输出"
    },
    "domain_suggestion": {
      "type": "object",
      "description": "可选：外部预生成的领域建议。为空时S2内部调用core-domain-classifier生成"
    }
  },
  "required": [
    "s1_outputs"
  ]
}
```

## 输出规范 (output_schema)

```json
{
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
            "phase_1_cold_start": {
              "type": "string",
              "description": "冷启动期领域标签，如'A'"
            },
            "phase_2_growth": {
              "type": "string",
              "description": "成长期领域标签，如'A+C'"
            },
            "phase_3_mature": {
              "type": "string",
              "description": "成熟期领域标签，如'A+C+F'"
            }
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
}
```

## 工具声明 (tool_declarations)

本Skill无外部工具依赖，纯提示词可执行。

## 执行逻辑

(1)调用core-domain-classifier→(2)输出领域确认卡(支持1-3个标签组合，取消E型独立类型，改为A-F的组合标记)→(3)如用户选择与AI建议不同,记录偏差→(4)歧义消解强确认(若用户选择与AI建议不一致，必须明确确认'确认选择X型,而非AI建议的Y型')→(5)确定合规激活条件(分级+领域专属)→(6)可选：领域时序演化规划(冷启动/成长/成熟期标签)→(7)调用core-complexity-channel-selector确定通道。

## Few-shot 示例

### 示例1: 正常流程 - 小红书美食团队(A型)

**输入**:
```json
{
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
}
```

**输出**:
```json
{
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
```

### 示例2: 异常流程 - 医疗科普+客服(B/F歧义)

**输入**:
```json
{
  "s1_outputs": {
    "core_need": "医疗健康科普+在线问诊",
    "keywords": ["医疗", "科普", "在线问诊", "健康"],
    "team_size": 3
  },
  "domain_suggestion": {
    "domain_type": "A",  # E型已改为组合标记，主类型为A，次类型含F
    "domain_name": "混合型(A+F)",
    "confidence": "medium",
    "ambiguity": "同时涉及内容传播和客户服务，建议按E型处理"
  }
}
```

**输出**:
```json
{
  "domain_profile": {
    "primary_domain": "A",
    "secondary_domains": ["F"]
  },
  "confirmed_domain": "E",
  "disambiguation_log": [
    "领域本体: 医疗科普(内容传播A) + 在线问诊(客户服务F) → 确认混合型E",
    "目标用户: 患者及家属 → 确认",
    "交付形式: 科普文章+问诊对话 → 确认",
    "交付渠道: 公众号+小程序→ 确认",
    "BF辨析: 同时存在内容发布和持续客户交互，非单纯项目交付B，非纯客服F"
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
```

### 示例3: 快速通道 - 个人财税科普号(A型直接确认)

**输入**:
```json
{
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
}
```

**输出**:
```json
{
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
```

## 知识库挂载点 (knowledge_base_mount_points)


> **⚠️ 挂载点说明**：以下 `file://` 路径为概念性挂载点（conceptual mount points），用于声明本 skill 的知识库依赖结构。它们不是物理文件路径，不需要实际加载文件。执行时请直接依据本 SKILL.md 正文中的规则定义和伪代码逻辑工作。
- **[static]** `file://./knowledge/stage-2-rules.md` — 阶段2执行规则
- **[dynamic]** `file://./knowledge/stage-2-state.json` — 阶段2运行时状态

## 依赖关系

- `core-mental-model-engine`
- `core-domain-classifier`

## 四维歧义消解模板

| 维度 | 正例模板 | 反例模板 | 触发条件 |
| --- | --- | --- | --- |
| 领域本体 | 具体做什么事？→ "帮中小企业老板提供代账服务的获客" | 不是含糊表述 → 不是'财税'，而是明确行业/场景 | (1)领域描述过于宽泛(如"做AI"、"搞内容") (2)领域描述同时涉及多个类型(A~F有重叠) (3)B/F难以区分(同时涉及"项目"和"持续服务") (4)用户对领域的理解与行业定义有偏差 |
| 目标用户 | 服务/触达谁？→ "武汉年营收500万以下的小企业老板" | 不是泛泛之词 → 不是'所有人'，而是有明确画像的群体 | (1)用户描述为"所有人"、"大众"等泛化表述 (2)用户同时提供多个差异明显的目标群体 (3)目标用户画像与领域类型不匹配 (4)用户对受众的认知与交付形式矛盾 |
| 交付形式 | 产出什么形态的东西？→ "小红书避坑图文+公众号深度攻略+微信私聊话术" | 不是笼统形式 → 不是'内容'，而是具体的格式/渠道/频次 | (1)交付物形态不清(只说"做个系统"、"出内容") (2)不同交付形式需要不同渠道(需要分线) (3)用户期望的交付形式与目标平台能力不符 (4)交付形式在B/F间模糊("工单系统"vs"客服系统") |
| 交付渠道 | 通过什么触达？→ "小红书发现页+公众号推送到微信" | 不是模糊渠道 → 不是'线上'，而是具体的平台/场景/接口 | (1)渠道描述过于宽泛("线上"、"社交媒体") (2)目标渠道与交付形式冲突(图文内容用API交付) (3)涉及多平台需要分线(不同平台格式要求不同) (4)渠道选择影响合规策略(医疗类禁止某些渠道投放) |

```text
FUNCTION resolve_ambiguity(user_input):
    IF no broad_term AND no compound_domain AND no ambiguity AND not regulated:
        RETURN user_input
    FOR dimension IN [领域本体, 目标用户, 交付形式, 交付渠道]:
        ask_one_question(dimension)
        response = WAIT_FOR_USER()
        IF response IN ["都行", "随便", "不确定"]:
            ask_clarification_once(dimension)
        STORE resolved_value
    IF user_choice != ai_suggestion:
        CALL protocol-confirmation-node.strong_confirm("stage_2_ambiguity")
    RETURN resolved_domain_profile
```

## 详细执行逻辑

```text
FUNCTION execute_pipeline_s2_domain_disambiguation(input):
    # ===== 阶段二：领域分类与消歧 - 入口校验 =====
    ASSERT input.s1_outputs EXISTS
    ASSERT input.domain_suggestion EXISTS
    LOAD context_inheritance FROM s1

    s1_data = input.s1_outputs
    domain_suggestion = input.domain_suggestion

    # ===== 步骤1: 调用core-domain-classifier获取领域建议 =====
    classification_result = CALL core-domain-classifier(s1_data)
    suggested_domain = classification_result.domain_type
    suggested_name = classification_result.domain_name
    confidence = classification_result.confidence

    # ===== 步骤2: 宽泛词检测 =====
    BROAD_TERMS = ["做自媒体", "搞电商", "搞财税", "做AI", "搞内容", "做互联网", "搞技术"]
    user_keywords = EXTRACT_keywords(s1_data)
    broad_term_detected = FALSE
    FOR term IN BROAD_TERMS:
        IF term IN user_keywords:
            broad_term_detected = TRUE
            BREAK

    # ===== 步骤3: 四维度歧义消解 =====
    dimensions = ["领域本体", "目标用户", "交付形式", "交付渠道"]
    disambiguation_log = []
    resolved_values = {}

    FOR dimension IN dimensions:
        # 检查该维度是否需要消解
        needs_disambiguation = FALSE

        IF dimension == "领域本体":
            IF broad_term_detected:
                needs_disambiguation = TRUE
            IF classification_result.domain_overlap EXISTS:
                needs_disambiguation = TRUE
            IF confidence == "low" OR confidence == "medium":
                needs_disambiguation = TRUE

        ELIF dimension == "目标用户":
            IF s1_data.target_audience IN ["所有人", "大众", "不确定", ""]:
                needs_disambiguation = TRUE
            IF s1_data.target_audience_count > 1:
                needs_disambiguation = TRUE
            IF s1_data.target_audience NOT MATCHES domain_type:
                needs_disambiguation = TRUE

        ELIF dimension == "交付形式":
            IF s1_data.deliverable_form IN ["做个系统", "出内容", ""]:
                needs_disambiguation = TRUE
            IF multi_format_detected(s1_data):
                needs_disambiguation = TRUE
            IF s1_data.deliverable_form NOT MATCHES platform_capability:
                needs_disambiguation = TRUE

        ELIF dimension == "交付渠道":
            IF s1_data.channel IN ["线上", "社交媒体", ""]:
                needs_disambiguation = TRUE
            IF s1_data.channel NOT MATCHES deliverable_form:
                needs_disambiguation = TRUE
            IF multi_platform_detected(s1_data):
                needs_disambiguation = TRUE

        # 执行消解提问
        IF needs_disambiguation:
            CALL protocol-single-question-guidance(dimension)
            question_text = GENERATE_disambiguation_question(dimension, s1_data)
            OUTPUT question_text TO user
            response = WAIT_FOR_USER()
            IF response IN ["都行", "随便", "不确定"]:
                # 仅追问一次，不反复纠缠
                clarification = ASK_ONE_CLARIFICATION(dimension)
                response = WAIT_FOR_USER()
                IF response IN ["都行", "随便", "不确定"]:
                    response = GET_default_value(dimension, suggested_domain)
            resolved_values[dimension] = response
            APPEND dimension + ": " + response + " → 消解完成" TO disambiguation_log
        ELSE:
            resolved_values[dimension] = GET_current_value(dimension, s1_data)
            APPEND dimension + ": " + resolved_values[dimension] + " → 无歧义" TO disambiguation_log

    # ===== 步骤4: 用户选择与AI建议偏差处理(歧义消解强确认) =====
    # 改进：支持多标签组合，E型不再是独立类型
    user_choice = ASK_USER_TO_CONFIRM_DOMAIN(suggested_domain, suggested_name)
    IF user_choice != suggested_domain:
        # 强确认：必须明确确认选择偏差
        CALL protocol-confirmation-node.strong_confirm("stage_2_ambiguity")
        confirmation = ASK_ONE("你选择了" + user_choice + "型，而非AI建议的" + suggested_domain + "型，确认吗？")
        IF confirmation == "确认":
            primary_domain = user_choice
            APPEND "用户选择偏差: 用户选" + user_choice + "，AI建议" + suggested_domain + " → 用户确认" TO disambiguation_log
        ELSE:
            primary_domain = suggested_domain
            APPEND "用户选择偏差后撤回: 采用AI建议" + suggested_domain TO disambiguation_log
    ELSE:
        primary_domain = suggested_domain

    # 询问是否有多领域标签(改进：从6选1改为1-3标签组合)
    secondary_domains = []
    multi_domain_hint = ASK_ONE("除了" + primary_domain + "型，你的业务是否还涉及其他领域？(可选0-2个)")
    IF multi_domain_hint NOT IN ["没有", "不确定", "就这个"]:
        secondary_domains = PARSE_SECONDARY_DOMAINS(multi_domain_hint)
        APPEND "多标签组合: " + primary_domain + "+" + JOIN(secondary_domains) + " → 确认" TO disambiguation_log

    # 构建domain_profile(改进：替代原confirmed_domain单一枚举)
    domain_profile = {
        "primary_domain": primary_domain,
        "secondary_domains": secondary_domains
    }

    # 向后兼容：构建confirmed_domain
    IF LENGTH(secondary_domains) > 0:
        confirmed_domain = "E"  # 混合场景向后兼容为E型
    ELSE:
        confirmed_domain = primary_domain

    # 可选：领域时序演化规划(改进：仅当业务有明显阶段变化时询问)
    has_evolution = ASK_ONE("你的业务在不同阶段(如冷启动期/成长期/成熟期)是否涉及不同领域？")
    IF has_evolution IN ["是", "对", "有的"]:
        domain_profile.domain_evolution = {
            "phase_1_cold_start": ASK_ONE("冷启动期主要是哪个领域？"),
            "phase_2_growth": ASK_ONE("成长期增加了哪些领域？"),
            "phase_3_mature": ASK_ONE("成熟期涉及哪些领域？")
        }
        APPEND "领域时序演化: " + JSON(domain_profile.domain_evolution) + " → 记录" TO disambiguation_log

    # ===== 步骤5: 确定合规激活条件(改进：从布尔改为分级+领域专属) =====
    compliance_activation_map = {
        "4.1": {"level": "none", "sensitive_categories": []},
        "4.2": {"level": "none", "sensitive_words": {}},
        "4.3": {"level": "none", "regulations": [], "data_residency": "CN"},
        "4.4": {"level": "none", "trigger_conditions": []},
        "4.5": {"level": "none", "data_categories": []}
    }

    # 按领域类型标签组合激活合规条件
    all_domain_tags = [primary_domain] + secondary_domains

    # 4.1内容合规
    IF "A" IN all_domain_tags OR "F" IN all_domain_tags:
        compliance_activation_map["4.1"]["level"] = "warning"
        compliance_activation_map["4.1"]["sensitive_categories"] = GET_sensitive_categories(resolved_values["领域本体"])

    # 4.2敏感词库(改进：按领域填充专属词表)
    IF "A" IN all_domain_tags:
        compliance_activation_map["4.2"]["level"] = "warning"
    domain_keyword = EXTRACT_DOMAIN_KEYWORD(resolved_values["领域本体"])
    compliance_activation_map["4.2"]["sensitive_words"] = GET_DOMAIN_SENSITIVE_WORDS(domain_keyword)
    # 领域专属敏感词注册表
    # medical: ["处方", "治愈率", "疗效保证", "根治", "无副作用"]
    # finance: ["保本", "稳赚", "内部消息", "代客理财", "100%收益"]
    # education: ["包过", "100%升学", "名校保录", "保分"]

    # 4.3数据合规(改进：增加法规列表和数据驻留地)
    IF "B" IN all_domain_tags OR "D" IN all_domain_tags:
        compliance_activation_map["4.3"]["level"] = "warning"
    IF resolved_values["目标市场"] IN ["海外", "global"]:
        compliance_activation_map["4.3"]["level"] = "mandatory"
        IF resolved_values["目标市场"] == "EU" OR CONTAINS_EU_AUDIENCE:
            compliance_activation_map["4.3"]["regulations"] = ["GDPR"]
            compliance_activation_map["4.3"]["data_residency"] = "EU"
        ELIF resolved_values["目标市场"] == "overseas":
            compliance_activation_map["4.3"]["regulations"] = ["PIPL"]
            compliance_activation_map["4.3"]["data_residency"] = "multi_region"

    # 4.4人工审批(改进：增加触发条件)
    IF "F" IN all_domain_tags OR "C" IN all_domain_tags:
        compliance_activation_map["4.4"]["level"] = "warning"
        compliance_activation_map["4.4"]["trigger_conditions"] = ["涉及专业建议", "客户投诉升级"]
    IF compliance_activation_map["4.3"]["level"] == "mandatory":
        compliance_activation_map["4.4"]["level"] = "mandatory"
        compliance_activation_map["4.4"]["trigger_conditions"].extend(["跨境数据传输", "敏感数据处理"])

    # 4.5隐私保护
    IF "F" IN all_domain_tags:
        compliance_activation_map["4.5"]["level"] = "warning"
        compliance_activation_map["4.5"]["data_categories"] = ["用户对话记录", "联系方式"]
    IF compliance_activation_map["4.3"]["level"] == "mandatory":
        compliance_activation_map["4.5"]["level"] = "mandatory"
        compliance_activation_map["4.5"]["data_categories"].extend(["跨境个人数据", "生物识别信息"])

    # ===== 步骤6: 通道确认三步流程 =====
    # 三步: ①初评(来自S1) → ②领域确认后修正 → ③最终确认
    initial_channel = s1_data.initial_channel_hint
    IF confirmed_domain IN ["C", "D"] AND compliance_activation_map["4.4"]["level"] IN ["warning", "mandatory"]:
        revised_channel = "strict"
    ELIF LENGTH(secondary_domains) > 0:
        # 改进（I-2.5）：混合型通道判定改为基于合规级联合评估，不再强制strict
        # 改进#24修复: MAX_COMPLIANCE_LEVEL函数定义
        combined_compliance = MAX_COMPLIANCE_LEVEL(all_domain_tags)
        IF combined_compliance == "mandatory":
            revised_channel = "strict"
        ELIF combined_compliance == "warning":
            revised_channel = "standard"
        ELSE:
            revised_channel = "fast"
    ELIF broad_term_detected == FALSE AND confidence == "high":
        revised_channel = "fast"
    ELSE:
        revised_channel = initial_channel

    # 改进#24修复: MAX_COMPLIANCE_LEVEL函数定义
    FUNCTION MAX_COMPLIANCE_LEVEL(domain_tags):
        # 从domain_tags推导最高合规级别
        levels = []
        FOR tag IN domain_tags:
            level = GET_DOMAIN_COMPLIANCE_LEVEL(tag)
            levels.APPEND(level)
        # 优先级: mandatory > warning > none
        IF "mandatory" IN levels:
            RETURN "mandatory"
        ELIF "warning" IN levels:
            RETURN "warning"
        ELSE:
            RETURN "none"

    FUNCTION GET_DOMAIN_COMPLIANCE_LEVEL(domain_tag):
        # 按领域类型返回默认合规级别
        # F型(客服)和强监管场景默认warning
        IF domain_tag == "F":
            RETURN "warning"
        # B/D型(服务交付/流程自动化)涉及数据处理默认warning
        IF domain_tag IN ["B", "D"]:
            RETURN "warning"
        # A/C型默认none(除非S2已检测到强监管)
        RETURN "none"

    channel_hint = CALL core-complexity-channel-selector(revised_channel, confirmed_domain, compliance_activation_map)

    # ===== 步骤7: 确定反馈回路需求（E型已改为组合标记，通过domain_profile判断混合型） =====
    feedback_loops_required = []
    has_secondary = domain_profile EXISTS AND LENGTH(domain_profile.secondary_domains) > 0
    secondary_contains_a = has_secondary AND "A" IN domain_profile.secondary_domains
    secondary_contains_f = has_secondary AND "F" IN domain_profile.secondary_domains
    IF confirmed_domain == "A" OR secondary_contains_a:
        APPEND "内容效果反馈" TO feedback_loops_required
    IF confirmed_domain == "F" OR secondary_contains_f:
        APPEND "满意度追踪" TO feedback_loops_required
    IF confirmed_domain == "B":
        APPEND "项目进度反馈" TO feedback_loops_required
    IF confirmed_domain == "D":
        APPEND "分析准确度反馈" TO feedback_loops_required
    IF confirmed_domain == "C":
        APPEND "获客转化反馈" TO feedback_loops_required

    # ===== 质量门控 =====
    CALL protocol-quality-gate(stage=2, output={
        "domain_profile": domain_profile,
        "confirmed_domain": confirmed_domain,
        "disambiguation_log": disambiguation_log
    })
    ASSERT primary_domain IN ["A", "B", "C", "D", "F"]
    ASSERT LENGTH(disambiguation_log) >= 4  # 四维度都必须有记录

    # ===== 产出输出 =====
    output = BUILD_output_according_to_output_schema({
        "domain_profile": domain_profile,
        "confirmed_domain": confirmed_domain,
        "disambiguation_log": disambiguation_log,
        "compliance_activation_map": compliance_activation_map,
        "feedback_loops_required": feedback_loops_required
    })
    RETURN output
```

## 下一阶段路由

> 本阶段完成后，由 `team-orchestrator` 自动衔接至 `pipeline-s3-chain-decomposition`（阶段三：链路拆解）。
> 衔接条件：领域确认卡已生成 + domain_type已确定 + 用户已强确认。
> 用户无需手动触发下一阶段。

## 版本

1.1.0

---
*本Skill由全域专家团构建skills体系自动生成，版本1.1.0，日期2026-06-16*
