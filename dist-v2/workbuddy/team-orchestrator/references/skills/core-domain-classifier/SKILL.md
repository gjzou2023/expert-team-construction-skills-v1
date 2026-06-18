---
name: core-domain-classifier
description: 基于S1需求提取关键词，匹配六种领域类型矩阵(A/B/C/D/E/F)，如有歧义使用ToT多方案比较，输出领域确认卡。v1.4.0行业知识骨架扩展至8个高频行业 Use when: 用户说"core-domain-classifier、领域分类引擎、L0分类"等触发词。
---

# 领域分类器

> **层级**: L0 | **版本**: 1.4.0 | **ID**: `core-domain-classifier` | **中文名**: 领域分类器 | **英文名**: Domain Classifier
# 领域分类器 (Domain Classifier)

> **层级**: L0 | **版本**: 1.3.0 | **ID**: `core-domain-classifier`
> **编排关系**: 本skill由 `team-orchestrator` 按需自动加载执行，属于全域专家团构建skills系统的内部组件，用户不应直接触发。

## 概述

基于S1需求提取关键词，匹配六种领域类型矩阵(A/B/C/D/E/F)，如有歧义使用ToT多方案比较，输出领域确认卡。v1.3.0新增高频行业知识骨架预置。

## 触发条件

当检测到以下关键词或场景时自动激活：领域分类, 什么类型, A型B型, 内容传播, 服务交付, 流程自动化, 混合型

## 输入规范 (input_schema)

```json
{
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
}
```

## 输出规范 (output_schema)

```json
{
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
}
```

## 工具声明 (tool_declarations)

本Skill无外部工具依赖，纯提示词可执行。

## 执行逻辑

(1)基于S1需求提取关键词→(2)匹配六种领域类型矩阵→(3)如有歧义使用ToT多方案比较→(4)输出领域确认卡(含歧义消解过程)。
六种领域类型：A=内容传播型, B=服务交付型, C=知识管理型, D=流程自动化型, E=混合型(任意A-F组合的混合标签), F=客户服务型。
B vs F辨析：有明确"项目/订单"概念→B，持续无终点→F。
E型处理：识别包含的子类型，按并集激活子协议。改进#26修复：E型定义为任意A-F组合的混合标签，不再限定为含D/F。
歧义消解强确认：若用户选择与AI建议不一致，必须明确确认"确认选择X型,而非AI建议的Y型"。

## Few-shot 示例

### 示例 1

**输入**:
```json
{
  "s1_summary": "做小红书美食探店，每天发图文笔记",
  "keywords": [
    "小红书",
    "图文",
    "探店",
    "美食"
  ]
}
```

**输出**:
```json
{
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
```

### 示例 2

**输入**:
```json
{
  "s1_summary": "自动采集行业数据生成周报",
  "keywords": [
    "自动",
    "数据",
    "报告",
    "采集"
  ]
}
```

**输出**:
```json
{
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
```

### 示例 3：快速通道变体（B/F辨析 + 混合型E）

**输入**:
```json
{
  "s1_summary": "帮律师所做法律咨询获客，在小红书发普法内容，然后私信里做付费法律咨询",
  "keywords": [
    "法律",
    "咨询",
    "小红书",
    "获客",
    "付费",
    "私信"
  ]
}
```

**输出**:
```json
{
  "domain_type": "E",
  "domain_name": "混合型(A+B)",
  "sub_domain": "内容获客+专业服务交付",
  "compliance_activation": {
    "4.1": true,
    "4.2": ["法律咨询"],
    "4.3": true,
    "4.4": true,
    "4.5": false
  },
  "feedback_loop_types": [
    "内容效果反馈",
    "客户反馈→服务优化"
  ],
  "classification_reasoning": "用户同时包含A型(小红书内容传播获客)和B型(付费法律咨询服务交付)。A→内容合规协议+CTA策略;B→交付标准+质量验收。B/F辨析:有明确'法律咨询项目/订单'概念→B而非F(持续无终点客服)。E型处理:取A∪B子协议并集,优先处理B的强监管合规项。"
}
```

- **[static]** `file://domain-matrix/classification-rules` — 六种领域类型分类矩阵
- **[static]** `file://domain-matrix/compliance-activation-map` — 领域类型→合规协议条件激活映射

## 依赖关系

- `core-mental-model-engine`

## 六种领域类型矩阵

| 类型 | 名称 | 定义 | 典型场景 | 激活子协议 | B/F辨析规则 |
| --- | --- | --- | --- | --- | --- |
| A | 内容传播型 | 通过各平台发布内容来触达或获取目标受众。 | 自媒体获客、品牌内容营销、知识科普、短视频带货 | 内容合规协议、内容效果反馈、CTA与视觉生产 | 以内容发布为核心交付，用户消费内容而非获取服务 |
| B | 服务交付型 | 围绕项目/订单向客户交付专业成果。 | 设计接单、咨询项目、翻译服务、开发外包 | 交付标准、客户沟通、质量验收 | 有明确"项目/订单"概念，有起止时间和交付物里程碑 |
| C | 知识管理型 | 组织、整理、生成和检索知识资产。 | 企业知识库、学习笔记体系、行业研究整理 | 知识结构化、索引检索、版本更新 | 以知识组织和检索为核心，不直接面向客户交付 |
| D | 流程自动化型 | 把重复性工作流自动化执行。 | 数据采集-清洗-报告、监控告警、批量处理 | 自动化触发、异常处理、监控恢复 | 以流程编排和自动执行为核心，人机交互最小化 |
| E | 混合型 | 任意A-F中2-3个类型的组合标记(改进#26修复：不再限定含D/F)。 | 内容获客+私域服务、知识管理+内容输出 | 取所含子类型协议并集，优先处理D/F强制项 | 识别主导子类型，BF冲突时按主导类型决定 |
| F | 客户服务型 | 持续接收和响应客户问题或需求。 | 在线客服、售后支持、用户答疑、工单处理 | SLA、话术规范、满意度与响应时间反馈 | 持续无终点，无明确项目边界，以响应式交互为主 |

```text
FUNCTION classify_domain(resolved_profile):
    scores = score_against_A_to_F_matrix(resolved_profile)
    IF has_project_concept(resolved_profile):
        prefer("B")
    ELIF is_continuous_service(resolved_profile):
        prefer("F")
    IF matches_multiple_types(resolved_profile):
        candidate = "E"
        sub_types = identify_sub_types(resolved_profile)
    IF top_two_scores_close OR user_disagrees:
        PRESENT_OPTIONS_TO_USER(candidates, reasons)
        WAIT_FOR_EXPLICIT_CONFIRMATION()
    RETURN {domain_type, sub_domain, compliance_activation, feedback_loop_types}
```

## 高频行业知识骨架预置（v1.3.0新增）

针对常见行业，预置该行业的知识骨架。当识别到用户需求属于预置行业时，自动激活对应骨架，确保不遗漏关键要素。

### 触发机制

当 `domain_type` 被判定为某特定行业子类时，从以下知识骨架库中加载对应骨架，注入后续阶段（S5架构设计和S7专家包生成）。

### 预置行业骨架库

#### 金融科技（FinTech）
- 利益相关者：央行、银保监/金管局、清算机构、持牌机构、用户
- 监管框架：巴塞尔协议、反洗钱法、个人信息保护法、数据安全法
- 常见项目类型：支付、信贷、保险、资管、监管科技、数字货币/DeFi(新增)、绿色金融/ESG(新增)
- 方法论：RAROC、压力测试、蒙特卡洛模拟、A/B测试

#### 医疗健康（HealthTech）
- 利益相关者：卫健委、药监局、医院、医生、患者、药企
- 监管框架：药品管理法、医疗器械管理条例、HIPAA/GDPR（海外）
- 常见项目类型：在线问诊、健康管理、药品信息、医疗科普、AI辅助诊断(新增)、远程医疗/数字疗法(新增)
- 方法论：循证医学(EBM)、临床试验设计、FDA审批流程

#### 教育培训（EdTech）
- 利益相关者：教育部、学校、教师、学生、家长
- 监管框架：教育法、未成年人保护法、双减政策
- 常见项目类型：在线课程、智能辅导、知识测评、教务管理、AI自适应学习(新增)、职业教育/技能培训(新增)、跨国培训/多语言(新增)
- 方法论：布鲁姆分类法、间隔重复、自适应学习

#### 电商零售（E-Commerce）
- 利益相关者：平台、商家、消费者、物流、支付机构
- 监管框架：电子商务法、消费者权益保护法、广告法
- 常见项目类型：商品推荐、智能客服、库存管理、营销自动化、直播电商(新增)、跨境电商(新增)
- 方法论：RFM模型、漏斗分析、A/B测试、推荐算法评估

#### 法律合规（LegalTech）
- 利益相关者：司法机构、律所、企业法务、当事人
- 监管框架：民法典、公司法、知识产权法、GDPR
- 常见项目类型：合同审查、法律检索、合规监控、案件管理、跨境M&A(新增)、数据隐私合规(新增)
- 方法论：IRAC分析法、法条检索、判例比对

#### 自媒体运营（Content Creator）（v1.4.0新增）
- 利益相关者：平台方、广告主、粉丝/MCN、品牌方
- 监管框架：广告法、互联网信息服务管理办法、个人信息保护法、各平台社区规范
- 常见项目类型：个人IP打造、多平台内容矩阵、商业变现体系、粉丝运营
- 方法论：内容漏斗模型、A/B测试、用户增长AARRR、内容日历规划
- A型特有要素：CTA策略(温和引导)、品牌声音定义、各平台内容规格(小红书3:4/公众号2.35:1/抖音9:16)

#### 财税销售（Tax & Financial Sales）（v1.4.0新增）
- 利益相关者：税务局/金税四期、企业财务部门、审计机构、银行/支付机构
- 监管框架：税收征收管理法、会计法、反洗钱法、CRS/FATCA(跨境)
- 常见项目类型：智能财税咨询、税务筹划、报税自动化、财务合规审查
- 方法论：税基分析、转移定价、合规审计框架、风险矩阵
- B型特有要素：服务标准协议(响应时间/准确率SLA)、专业术语通俗化

#### 广告营销（Advertising & Marketing）（v1.4.0新增）
- 利益相关者：品牌方、4A/代理商、KOL/MCN、广告平台、消费者
- 监管框架：广告法、互联网广告管理暂行办法、消费者权益保护法、数据安全法
- 常见项目类型：整合营销方案、效果投放优化、品牌策略、KOL营销、社媒运营
- 方法论：AIDA漏斗、品牌定位三角、媒体组合优化、归因分析、ROI测算
- A+B型特有要素：广告法合规(禁用词≥5个)、效果归因闭环、跨平台投放策略

### 骨架激活规则

1. 仅在 `channel != "fast"` 时激活（快速通道跳过知识骨架以保持速度）
2. 激活后在 S5 架构设计的领域必设角色中增加行业特定角色
3. 激活后在 S7 专家包生成的知识资产沉淀中增加行业特定知识库类型

## 详细执行逻辑

```text
FUNCTION execute_core_domain_classifier(input):
    // ========== 输入校验与初始化 ==========
    ASSERT input.s1_summary IS NOT EMPTY, "S1需求摘要不可为空"
    ASSERT LENGTH(input.keywords) > 0, "关键词列表不可为空"
    LOAD context_inheritance FROM core-mental-model-engine
    LOAD classification_matrix FROM file://domain-matrix/classification-rules
    LOAD compliance_map FROM file://domain-matrix/compliance-activation-map

    // ========== 第1步：基于S1需求提取关键词并匹配六种领域类型矩阵 ==========
    scores = {}
    FOR type IN ["A","B","C","D","E","F"]:
        scores[type] = CALCULATE_MATCH_SCORE(input.keywords, classification_matrix[type])
        scores[type] += CALCULATE_SEMANTIC_SCORE(input.s1_summary, classification_matrix[type])

    // ========== 第2步：B vs F辨析（核心歧义消解） ==========
    IF scores["B"] > 0 AND scores["F"] > 0:
        // B与F得分均较高时，执行辨析规则
        IF HAS_PROJECT_CONCEPT(input.s1_summary):
            // 有明确"项目/订单"概念→B
            scores["B"] = scores["B"] * 1.5
            OUTPUT "B/F辨析：检测到项目/订单概念→倾向B型（服务交付型）"
        ELIF IS_CONTINUOUS_SERVICE(input.s1_summary):
            // 持续无终点→F
            scores["F"] = scores["F"] * 1.5
            OUTPUT "B/F辨析：检测到持续无终点特征→倾向F型（客户服务型）"
        ELSE:
            // 无法自动辨析，标记需用户确认
            needs_bf_disambiguation = TRUE

    // ========== 第3步：E型处理（混合型取子协议并集） ==========
    sorted_types = SORT_BY_SCORE_DESC(scores)
    top_type = sorted_types[0]
    second_type = sorted_types[1]

    IF scores[top_type] > 0 AND scores[second_type] > SCORE_THRESHOLD:
        // 多类型得分均超过阈值，判定为E型混合
        candidate_type = "E"
        sub_types = IDENTIFY_SUB_TYPES(scores, SCORE_THRESHOLD)
        ASSERT LENGTH(sub_types) >= 2, "E型必须包含至少两个子类型"
        // 取所含子类型协议并集
        merged_compliance = {}
        merged_feedback = []
        FOR sub IN sub_types:
            sub_compliance = compliance_map[sub]
            FOR key IN KEYS(sub_compliance):
                IF key NOT IN merged_compliance:
                    merged_compliance[key] = sub_compliance[key]
                ELIF sub_compliance[key] == TRUE:
                    merged_compliance[key] = TRUE  // 布尔并集：任一为真则真
            APPEND_ALL(merged_feedback, sub_compliance.feedback_loop_types)
        // 优先处理D/F强制合规项
        IF "D" IN sub_types OR "F" IN sub_types:
            merged_compliance = PRIORITIZE_MANDATORY(merged_compliance, sub_types)
    ELSE:
        candidate_type = top_type
        sub_types = [top_type]
        merged_compliance = compliance_map[top_type]
        merged_feedback = compliance_map[top_type].feedback_loop_types

    // ========== 第4步：歧义消解（ToT多方案比较） ==========
    top_score = scores[sorted_types[0]]
    second_score = scores[sorted_types[1]]
    IF IS_CLOSE(top_score, second_score, threshold=0.15) OR needs_bf_disambiguation:
        // top_two_scores_close 或 B/F无法自动辨析时，呈交用户选择
        candidates = []
        FOR i IN [0, 1]:
            APPEND(candidates, {
                type: sorted_types[i],
                score: scores[sorted_types[i]],
                reasoning: EXPLAIN_REASONING(sorted_types[i], input.keywords)
            })
        OUTPUT "⚠️ 领域分类存在歧义，请选择："
        FOR c IN candidates:
            OUTPUT "  {c.type}型 - {c.reasoning}（得分：{c.score}）"
        user_choice = WAIT_FOR_EXPLICIT_CHOICE(candidates)
        // 强确认：若用户选择与AI建议不一致，必须明确确认
        IF user_choice != candidate_type:
            OUTPUT "⚠️ 您选择了{user_choice}型，而非AI建议的{candidate_type}型，请确认：确认选择{user_choice}型，而非AI建议的{candidate_type}型"
            WAIT_FOR_EXPLICIT_CONFIRMATION()
        candidate_type = user_choice
        // 根据用户最终选择更新子类型
        IF candidate_type == "E":
            sub_types = IDENTIFY_SUB_TYPES_FROM_CHOICE(user_choice, scores)

    // ========== 第5步：生成领域确认卡 ==========
    domain_name = LOOKUP_DOMAIN_NAME(candidate_type, classification_matrix)
    IF candidate_type == "E":
        domain_name = "混合型(" + JOIN(sub_types, "+") + ")"
    sub_domain = INFER_SUB_DOMAIN(input.s1_summary, candidate_type)

    // 激活合规协议
    compliance_activation = {
        "4.1": EVALUATE_4_1(candidate_type, merged_compliance),
        "4.2": EVALUATE_4_2(candidate_type, input.keywords),
        "4.3": EVALUATE_4_3(candidate_type, merged_compliance),
        "4.4": EVALUATE_4_4(candidate_type, merged_compliance),
        "4.5": EVALUATE_4_5(candidate_type, merged_compliance)
    }

    // 反馈环路类型
    feedback_loop_types = DEDUPLICATE(merged_feedback)

    // ========== 组装输出 ==========
    output = {
        domain_type: candidate_type,
        domain_name: domain_name,
        sub_domain: sub_domain,
        compliance_activation: compliance_activation,
        feedback_loop_types: feedback_loop_types
    }
    CALL protocol-quality-gate("final_check", output)
    RETURN output

FUNCTION HAS_PROJECT_CONCEPT(summary):
    // 检测是否包含项目/订单概念
    project_patterns = ["订单", "项目", "合同", "交付", "验收", "里程碑", "工期", "报价"]
    FOR p IN project_patterns:
        IF CONTAINS(summary, p):
            RETURN TRUE
    RETURN FALSE

FUNCTION IS_CONTINUOUS_SERVICE(summary):
    // 检测是否为持续无终点服务
    continuous_patterns = ["客服", "答疑", "在线咨询", "工单", "售后", "7x24", "持续响应"]
    FOR p IN continuous_patterns:
        IF CONTAINS(summary, p):
            RETURN TRUE
    RETURN FALSE

FUNCTION IDENTIFY_SUB_TYPES(scores, threshold):
    // 识别得分超过阈值的子类型
    result = []
    FOR type IN ["A","B","C","D","F"]:
        IF scores[type] > threshold:
            APPEND(result, type)
    RETURN result

FUNCTION PRIORITIZE_MANDATORY(compliance, sub_types):
    // 优先处理D/F的强制合规项
    IF "D" IN sub_types:
        compliance["automation_safety"] = TRUE
    IF "F" IN sub_types:
        compliance["sla_required"] = TRUE
    RETURN compliance
```

## 版本

1.4.0

---
*本Skill由全域专家团构建skills体系生成，版本1.4.0，日期2026-06-17*
