
# 强制执行规则(不可覆盖) (Mandatory Rules)

> **层级**: L4 | **版本**: 1.1.0 | **ID**: `constraint-mandatory-rules`
> **编排关系**: 本skill由 `team-orchestrator` 按需自动加载执行，属于全域专家团构建skills系统的内部组件，用户不应直接触发。

## 概述

全程横贯，任何Skill执行时受此约束。21条强制规则不可覆盖。

## 触发条件

当检测到以下关键词或场景时自动激活：规则, 约束, 强制, 规范, 命名

## 输入规范 (input_schema)

```json
{
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
}
```

## 输出规范 (output_schema)

```json
{
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
}
```

## 工具声明 (tool_declarations)

本Skill无外部工具依赖，纯提示词可执行。

## 执行逻辑

20条强制规则：(1)交付物优先(先定义交付物再定义角色);(2)MECE强制(5.2三问必须通过);(3)合规不可绕过;(4)平台可执行强制;(5)分线强制(不同渠道下游分线);(6)阶段跳转约束(满足条件才能进下阶段);(7)字段追踪强制(一一对应);(8)单问规则(信息采集每次1问);(9)规范优先级(法规>平台>服务>品牌);(10)合规时效性(最新规则为准);(11)数据安全强制;(12)复杂度通道约束(可升不可降);(13)术语翻译强制(首次出现附通俗解释);(14)选项覆盖检查;(15)专家包格式合规;(16)专家命名合规(kebab-case+2-3字花名);(17)平台元数据完整(categoryId/tags3/quickPrompts3/40-50字描述);(18)Team型协作合规(≥4人Team型);(19)版本迭代触发信号(用户主动可感知事件);(20)紧急终止合规(4.4人工审批不可跳过);(21)输出可验证性(关键判断标注确定性等级🟢/🟡/🔴)。改进#33修复：实际21条，已同步description和章节标题。

## Few-shot 示例

### 示例 1: 命名合规检查(不通过)

**输入**:
```json
{
  "target_check": "Agent ID='内容专家1', 花名='内容师', profession='负责人'",
  "context": {
    "layer": "L4",
    "pipeline_stage": "S3"
  }
}
```

**输出**:
```json
{
  "compliant": false,
  "violations": [
    {
      "rule": "规则16专家命名合规",
      "detail": "Agent ID应kebab-case如content-expert，非中文+数字",
      "consequence": "平台无法识别该ID，导入失败"
    },
    {
      "rule": "规则16花名规范",
      "detail": "花名'内容师'是纯功能词，不符合2-3字正常人名风格",
      "consequence": "用户无法与角色建立自然交互关系"
    },
    {
      "rule": "规则16profession禁止通用title",
      "detail": "profession='负责人'是通用title，应使用具体职能如'内容策略师'",
      "consequence": "主理人角色模糊，协作调度失效"
    }
  ],
  "suggestions": [
    "Agent ID: content-strategist",
    "花名: 墨言(谐音'默言')",
    "profession: 内容策略师"
  ]
}
```

### 示例 2: Team型协作合规触发

**输入**:
```json
{
  "target_check": "专家包配置: 6个角色, expert_type=agent, 无teamInfo",
  "context": {
    "layer": "L4",
    "pipeline_stage": "S7"
  }
}
```

**输出**:
```json
{
  "compliant": false,
  "violations": [
    {
      "rule": "规则18Team型协作合规",
      "detail": "角色数>=4(实际6个)必须设为Team型并配置teamInfo.leadAgent+memberAgents",
      "consequence": "6个角色无法调度协作，产出混乱或重复"
    }
  ],
  "suggestions": [
    "将expert_type改为team",
    "设置teamInfo: leadAgent=chief-editor, memberAgents=[...]",
    "为主理人chief-editor定义spawn+SendMessage编排SOP"
  ]
}
```

### 示例 3: MECE三问检查

**输入**:
```json
{
  "target_check": "两个角色: content-writer负责小红书文案, editor负责公众号文案",
  "context": {
    "layer": "L4",
    "pipeline_stage": "S3",
    "domain_type": "A"
  }
}
```

**输出**:
```json
{
  "compliant": false,
  "violations": [
    {
      "rule": "规则2MECE强制",
      "detail": "独立性失败:小红书和公众号分为两个角色但内容撰写职责重叠,最终文案无人对质量总负责",
      "consequence": "双渠道内容质量无统一标准,品牌调性分裂"
    }
  ],
  "suggestions": [
    "合并为content-writer统一负责所有渠道文案",
    "或保持分角色但增设chief-editor作为内容质量第一责任人",
    "MECE三问验证:覆盖性✓ 独立性✗ 责任唯一性✗"
  ]
}
```

## 知识库挂载点 (knowledge_base_mount_points)

- **[static]** `file://./knowledge/constraint-mandatory-rules.md` — 强制执行规则(不可覆盖)完整规则集

## 依赖关系

无前置依赖。

## 21条强制规则展开

| 规则 | 说明 | 违规后果 | 反例 |
| --- | --- | --- | --- |
| 交付物优先 | 先定义交付物再定义角色。 | 会导致角色空转、职责无法验收。 | 先创建'内容策划师'再反推要产出什么。 |
| MECE强制 | 覆盖性、独立性、责任唯一性三问必须通过。 | 职责遗漏或重叠会让专家团无法稳定协作。 | 两个角色都负责最终文案但没有第一责任人。 |
| 合规不可绕过 | 强监管和内容发布场景必须执行合规审查。 | 可能生成违规内容或无法上线。 | 医疗建议直接发布，不加风险提示。 |
| 平台可执行强制 | 交付必须能在目标平台可见、可导入、可运行。 | 方案会停留在文档层面。 | 只写团队设想，不给WorkBuddy或Codex文件结构。 |
| 分线强制 | 不同渠道下游生产线必须分线。 | 渠道规格冲突会污染输出。 | 小红书图文和公众号长文共用同一末端模板。 |
| 阶段跳转约束 | 满足当前阶段守卫条件才能进入下一阶段。 | 上游未确认会放大下游返工。 | 没确认领域类型就开始设计角色。 |
| 字段追踪强制 | 引用前序产出必须字段一一对应。 | 会出现大意引用和虚构字段。 | S7引用不存在的工具配置。 |
| 单问规则 | 信息采集阶段每次只问一个问题。 | 用户负担过重，答案混杂。 | 一轮同时问领域、预算、平台、团队。 |
| 规范优先级 | 法规>平台>服务>品牌。 | 低优先级偏好会覆盖硬性规则。 | 为了品牌话术违反平台禁词。 |
| 合规时效性 | 以最新规则为准，必要时要求外部核验。 | 旧规则可能导致误判。 | 沿用过期平台导流规则。 |
| 数据安全强制 | 敏感数据最小化暴露并标注流向。 | 可能造成隐私泄露。 | 客户手机号直接发给第三方API。 |
| 复杂度通道约束 | 用户可升级通道，不可无风险说明降级。 | 复杂需求被过度简化。 | 金融服务需求强行走快速通道。 |
| 术语翻译强制 | 技术术语首次出现附通俗解释。 | 非技术用户无法确认。 | 只写MCP、Webhook、不解释含义。 |
| 选项覆盖检查 | 选项必须覆盖常见业务场景并提供自定义。 | 用户被迫误选。 | 平台选项没有'还没想好'。 |
| 专家包格式合规 | S7输出必须满足目标平台导入格式。 | 导入失败。 | Dify配置里混入WorkBuddy字段。 |
| 专家命名合规 | Agent ID kebab-case，花名2-3字正常人名。 | 平台识别或用户理解失败。 | agent id写成'内容专家1'。 |
| 平台元数据完整 | categoryId/tags3/quickPrompts3/40-50字描述必须完整。 | 平台展示和注册失败。 | tags只有1个或描述太短。 |
| Team型协作合规 | 角色数>=4必须Team型并有主理人SOP。 | 多角色无法调度。 | 6个角色仍做成单Agent分支。 |
| 版本迭代触发信号 | 只在用户主动可感知事件触发V2规划。 | 日常交互被升级提示打断。 | 每轮都提醒用户升级。 |
| 紧急终止合规 | 紧急终止模式下4.4人工审批仍不可跳过(合规红线)。 | 可能导致未经审核的合规风险内容输出。 | 紧急终止时跳过所有人工审批节点。 |
| 输出可验证性 | 关键判断必须标注确定性等级(🟢/🟡/🔴)和参考来源方向。 | 用户无法判断建议可信度。 | 金融建议无任何风险等级标注。 |

## 详细执行逻辑

```text
FUNCTION execute_constraint_mandatory_rules(input):
    ASSERT input matches input_schema
    ASSERT input.target_check != NULL AND LEN(input.target_check) > 0
    violations = []
    suggestions = []

    // 加载21条强制规则引擎(改进#33修复：实际21条)
    rules = LOAD_MANDATORY_RULES()  // 共21条,不可覆盖
    context = input.context IF input.context != NULL ELSE {}

    // ===== 规则1: 交付物优先 =====
    IF NOT HAS_DELIVERABLES_DEFINED_BEFORE_ROLES(input.target_check):
        APPEND violations, {
            "rule": "规则1交付物优先",
            "detail": "先定义交付物再定义角色,当前角色无对应交付物",
            "consequence": "角色空转,职责无法验收"
        }
        APPEND suggestions, "先列出所有交付物,再为每个交付物分配第一责任人"

    // ===== 规则2: MECE强制(三问必须通过) =====
    mece_result = CHECK_MECE(input.target_check)
    IF NOT mece_result.coverage:
        APPEND violations, {"rule": "规则2MECE覆盖性", "detail": "存在未覆盖的交付物"}
    IF NOT mece_result.independence:
        APPEND violations, {"rule": "规则2MECE独立性", "detail": "角色职责重叠,无第一责任人"}
    IF NOT mece_result.accountability:
        APPEND violations, {"rule": "规则2MECE责任唯一性", "detail": "多个角色对同一交付物负责但无主责人"}

    // ===== 规则3: 合规不可绕过 =====
    IF context.regulated == true OR DETECT_REGULATED_DOMAIN(input.target_check):
        IF NOT HAS_COMPLIANCE_CHECK(input.target_check):
            APPEND violations, {
                "rule": "规则3合规不可绕过",
                "detail": "强监管领域必须执行合规审查,当前未设置合规节点",
                "consequence": "可能生成违规内容或无法上线"
            }
            APPEND suggestions, "在内容发布前添加protocol-compliance-engine审查节点"

    // ===== 规则4: 平台可执行强制 =====
    IF NOT IS_PLATFORM_EXECUTABLE(input.target_check):
        APPEND violations, {
            "rule": "规则4平台可执行强制",
            "detail": "交付物无法在目标平台导入或运行",
            "consequence": "方案停留在文档层面"
        }

    // ===== 规则5: 分线强制 =====
    IF HAS_MULTI_CHANNEL(input.target_check):
        IF NOT HAS_CHANNEL_BRANCHING(input.target_check):
            APPEND violations, {"rule": "规则5分线强制", "detail": "不同渠道下游必须分线,当前共用模板"}

    // ===== 规则6: 阶段跳转约束 =====
    IF context.pipeline_stage != NULL:
        IF NOT STAGE_GUARD_PASSED(context.pipeline_stage, input.target_check):
            APPEND violations, {
                "rule": "规则6阶段跳转约束",
                "detail": "当前阶段守卫条件未满足,不能进入下一阶段"
            }

    // ===== 规则7: 字段追踪强制 =====
    IF HAS_FIELD_REFERENCES(input.target_check):
        orphan_fields = FIND_ORPHAN_FIELDS(input.target_check)
        IF LEN(orphan_fields) > 0:
            APPEND violations, {"rule": "规则7字段追踪", "detail": "引用了不存在的前序字段: " + JOIN(orphan_fields)}

    // ===== 受控修改通道(改进12: 不可变→受控可变) =====
    // 下游确实不能擅自修改上游产出，但可通过protocol-confirmation-node的strong_confirm发起修改请求
    // 修改请求必须包含: 修改原因 + 影响范围 + 回退方案
    // 修改被批准后，SME创建新的决策快照，原快照标记为superseded但保留历史
    IF HAS_MODIFICATION_REQUEST(input.target_check):
        mod_request = PARSE_MODIFICATION_REQUEST(input.target_check)
        IF mod_request HAS ["reason", "impact_scope", "rollback_plan"]:
            CALL protocol-confirmation-node.strong_confirm("controlled_modification")
            IF modification_approved:
                CALL core-state-management-engine("update", mod_request)
                // 原快照标记为superseded，新快照创建
                APPEND suggestions, "受控修改已批准，原决策快照标记为superseded"
            ELSE:
                APPEND suggestions, "修改请求未通过确认，保持原产出不变"
        ELSE:
            APPEND violations, {"rule": "受控修改请求不完整", "detail": "修改请求须包含reason+impact_scope+rollback_plan"}

    // ===== 规则8: 单问规则 =====
    IF COUNT_QUESTIONS_PER_TURN(input.target_check) > 1:
        APPEND violations, {"rule": "规则8单问规则", "detail": "信息采集阶段每次只问一个问题"}

    // ===== 规则9: 规范优先级 =====
    IF HAS_PRIORITY_CONFLICT(input.target_check):
        APPEND violations, {"rule": "规则9规范优先级", "detail": "法规>平台>服务>品牌,当前低优先级覆盖高优先级"}

    // ===== 规则10: 合规时效性 =====
    IF HAS_STALE_RULES(input.target_check):
        APPEND violations, {"rule": "规则10合规时效性", "detail": "引用了过期的规则,以最新规则为准"}

    // ===== 规则11: 数据安全强制 =====
    pii_exposure = SCAN_PII_EXPOSURE(input.target_check)
    IF LEN(pii_exposure) > 0:
        APPEND violations, {
            "rule": "规则11数据安全强制",
            "detail": "敏感数据暴露: " + JOIN(pii_exposure),
            "consequence": "可能造成隐私泄露"
        }

    // ===== 规则12: 复杂度通道约束 =====
    IF HAS_UNSAFE_DOWNGRADE(input.target_check, context):
        APPEND violations, {"rule": "规则12复杂度通道约束", "detail": "复杂需求不可无风险说明降级"}

    // ===== 规则13: 术语翻译强制 =====
    jargon_list = FIND_UNTRANSLATED_JARGON(input.target_check)
    IF LEN(jargon_list) > 0:
        APPEND violations, {"rule": "规则13术语翻译", "detail": "以下术语未附通俗解释: " + JOIN(jargon_list)}

    // ===== 规则14: 选项覆盖检查 =====
    IF NOT HAS_COMPLETE_OPTIONS(input.target_check):
        APPEND violations, {"rule": "规则14选项覆盖", "detail": "选项未覆盖常见业务场景或缺少自定义选项"}

    // ===== 规则15: 专家包格式合规 =====
    IF NOT PACKAGE_FORMAT_COMPLIANT(input.target_check):
        APPEND violations, {"rule": "规则15专家包格式", "detail": "S7输出格式不满足目标平台导入要求"}

    // ===== 规则16: 专家命名合规 =====
    naming_violations = CHECK_NAMING_CONVENTION(input.target_check)
    FOR EACH nv IN naming_violations:
        APPEND violations, nv

    // ===== 规则17: 平台元数据完整 =====
    IF NOT METADATA_COMPLETE(input.target_check):
        APPEND violations, {
            "rule": "规则17平台元数据",
            "detail": "categoryId/tags3/quickPrompts3/40-50字描述不完整"
        }

    // ===== 规则18: Team型协作合规 =====
    role_count = COUNT_ROLES(input.target_check)
    IF role_count >= 4 AND NOT IS_TEAM_TYPE(input.target_check):
        APPEND violations, {
            "rule": "规则18Team型协作",
            "detail": "角色数>=4(" + role_count + ")必须设为Team型并配置teamInfo"
        }

    // ===== 规则19: 版本迭代触发信号 =====
    IF HAS_UNSOLICITED_UPGRADE(input.target_check):
        APPEND violations, {"rule": "规则19版本迭代信号", "detail": "仅在用户主动可感知事件触发V2规划"}

    // ===== 规则20: 紧急终止合规 =====
    IF context.early_termination == true:
        IF compliance_activation_map["4.4"]["level"] == "mandatory":
            APPEND violations, {
                "rule": "规则20紧急终止合规",
                "detail": "紧急终止模式下4.4人工审批仍不可跳过(合规红线)",
                "consequence": "可能导致未经审核的合规风险内容输出"
            }
            APPEND suggestions, "紧急终止模式下仍须完成4.4人工审批后才能输出"

    // 汇总结果
    compliant = (LEN(violations) == 0)
    IF compliant:
        APPEND suggestions, "全部21条强制规则校验通过"
    ELSE:
        // 违规则阻断
        FOR EACH v IN violations:
            APPEND suggestions, GENERATE_FIX_SUGGESTION(v.rule)

    RETURN {"compliant": compliant, "violations": violations, "suggestions": suggestions}
```

## 版本

1.1.0

---
*本Skill由全域专家团构建skills体系自动生成，版本1.1.0，日期2026-06-16*
