
# 阶段四：交付物锚定 (Stage 4: Deliverable Anchoring)

> **层级**: L1 | **版本**: 1.0.0 | **ID**: `pipeline-s4-deliverable-anchoring`
> **编排关系**: 本skill由 `team-orchestrator` 自动加载执行，用户不应直接触发。承接 `pipeline-s3-chain-decomposition` 的输出，完成后自动衔接 `pipeline-s5-architecture-design`。

## 概述

枚举所有终端交付物，标注格式/频率/质量标准/目标受众，分配优先级和第一责任人，标注分线需求。Q9平台选择强制确认。

## 触发条件

当检测到以下关键词或场景时自动激活：交付物, 产出, 格式, 优先级, 锚定, 平台选择

## 输入规范 (input_schema)

```json
{
  "type": "object",
  "properties": {
    "s3_outputs": {
      "type": "object",
      "description": "S3链路节点输出"
    },
    "s2_outputs": {
      "type": "object",
      "description": "S2领域确认输出"
    }
  },
  "required": [
    "s3_outputs",
    "s2_outputs"
  ]
}
```

## 输出规范 (output_schema)

```json
{
  "type": "object",
  "properties": {
    "deliverables": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": {
            "type": "string"
          },
          "name": {
            "type": "string"
          },
          "format": {
            "type": "string"
          },
          "frequency": {
            "type": "string"
          },
          "quality_criteria": {
            "type": "string"
          },
          "target_audience": {
            "type": "string"
          },
          "owner_role": {
            "type": "string"
          },
          "priority": {
            "type": "string",
            "enum": [
              "core",
              "enhancement"
            ]
          },
          "channel_line": {
            "type": "string"
          }
        }
      }
    },
    "cross_channel_sharing": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  },
  "required": [
    "deliverables",
    "cross_channel_sharing"
  ]
}
```

## 工具声明 (tool_declarations)

本Skill无外部工具依赖，纯提示词可执行。

## 执行逻辑

(1)枚举所有终端交付物→(2)每个交付物标注:格式、频率、质量标准、目标受众→(3)分配优先级(core/enhancement)→(4)确定每个交付物的唯一第一责任人→(5)标注分线需求(不同渠道不同生产线,§6.1#5)→(6)输出交付物清单确认卡。Q9强制确认；'还没想好'分支：默认WorkBuddy，后续可更改。快速通道精简：交付物≤3时精简确认流程。

## Few-shot 示例

### 示例1: 正常流程 - A型内容团队交付物锚定

**输入**:
```json
{
  "s3_outputs": {
    "chain_nodes": [
      {"id": "N5", "name": "发布分发", "type": "output"}
    ]
  },
  "s2_outputs": {
    "confirmed_domain": "A",
    "domain_name": "内容传播型"
  }
}
```

**输出**:
```json
{
  "deliverables": [
    {
      "id": "D1",
      "name": "小红书图文笔记",
      "format": "JPG/PNG图片+文案",
      "frequency": "每周3篇",
      "quality_criteria": "标题吸引力>3%CTR, 图片分辨率≥1080p, 文案无违禁词",
      "target_audience": "25-35岁女性美食爱好者",
      "owner_role": "content-strategist",
      "priority": "core",
      "channel_line": "Line_1_小红书"
    },
    {
      "id": "D2",
      "name": "品牌合作提案",
      "format": "PDF文档",
      "frequency": "按需(每月2-3份)",
      "quality_criteria": "含数据报告+竞品分析+合作方案",
      "target_audience": "品牌方BD负责人",
      "owner_role": "content-strategist",
      "priority": "enhancement",
      "channel_line": "Line_2_商务"
    }
  ],
  "cross_channel_sharing": ["视觉素材库", "文案模板库"]
}
```

### 示例2: 异常流程 - B型服务交付(含分线需求)

**输入**:
```json
{
  "s3_outputs": {
    "chain_nodes": [
      {"id": "N4", "name": "方案交付", "type": "output"},
      {"id": "N5", "name": "客户确认", "type": "output"}
    ]
  },
  "s2_outputs": {
    "confirmed_domain": "B",
    "domain_name": "服务交付型",
    "project_scope": "企业官网设计"
  }
}
```

**输出**:
```json
{
  "deliverables": [
    {
      "id": "D1",
      "name": "设计稿(PC端)",
      "format": "Figma文件链接",
      "frequency": "2轮评审后定稿",
      "quality_criteria": "像素级还原, 适配1920x1080, 设计规范文档附后",
      "target_audience": "客户品牌总监",
      "owner_role": "ui-designer",
      "priority": "core",
      "channel_line": "Line_1_PC端"
    },
    {
      "id": "D2",
      "name": "设计稿(移动端)",
      "format": "Figma文件链接",
      "frequency": "与PC端同步",
      "quality_criteria": "适配375x812(iPhone), 触摸区域≥44px",
      "target_audience": "客户品牌总监",
      "owner_role": "ui-designer",
      "priority": "core",
      "channel_line": "Line_2_移动端"
    },
    {
      "id": "D3",
      "name": "设计规范文档",
      "format": "PDF",
      "frequency": "最终交付1次",
      "quality_criteria": "含色彩体系/组件库/交互说明",
      "target_audience": "客户前端开发团队",
      "owner_role": "ui-designer",
      "priority": "core",
      "channel_line": "共用(上游共享)"
    }
  ],
  "cross_channel_sharing": ["设计Token", "组件库"]
}
```

### 示例3: 快速通道 - 个人财税科普号精简交付物

**输入**:
```json
{
  "s3_outputs": {
    "chain_nodes": [
      {"id": "N3", "name": "发布", "type": "output"}
    ]
  },
  "s2_outputs": {
    "confirmed_domain": "A",
    "channel": "fast"
  }
}
```

**输出**:
```json
{
  "deliverables": [
    {
      "id": "D1",
      "name": "财税科普图文",
      "format": "文案+配图",
      "frequency": "每日1篇",
      "quality_criteria": "数据准确≥95%, 个人实操建议≥3条",
      "target_audience": "小微企业主/个人财务管理者",
      "owner_role": "solo-operator",
      "priority": "core",
      "channel_line": "Line_1_双渠道(小红书+公众号)"
    }
  ],
  "cross_channel_sharing": ["素材库共用"]
}
```

## 知识库挂载点 (knowledge_base_mount_points)

- **[static]** `file://pipeline/stage-4-rules` — 阶段4执行规则
- **[dynamic]** `file://pipeline/stage-4-state` — 阶段4运行时状态

## 依赖关系

- `core-mental-model-engine`
- `core-deliverable-backward-engine`

## 详细执行逻辑

```text
FUNCTION execute_pipeline_s4_deliverable_anchoring(input):
    # ===== 阶段四：交付物锚定 - 入口校验 =====
    ASSERT input.s3_outputs EXISTS
    ASSERT input.s2_outputs EXISTS
    LOAD context_inheritance FROM s3, s2

    s3_data = input.s3_outputs
    s2_data = input.s2_outputs
    domain_type = s2_data.confirmed_domain
    channel = s2_data.channel_hint IF EXISTS ELSE "standard"
    chain_nodes = s3_data.chain_nodes

    # ===== 快速通道精简规则 =====
    IF channel == "fast" AND LENGTH(chain_nodes) <= 3:
        CALL execute_fast_track_deliverable(domain_type, chain_nodes)
        GOTO FAST_TRACK_DELIVERABLE

    # ===== 步骤1: 枚举所有终端交付物 =====
    output_nodes = FILTER(chain_nodes, node -> node.type == "output")
    deliverable_list = []
    FOR node IN output_nodes:
        # 从链路节点推导交付物
        candidate_deliverables = CALL core-deliverable-backward-engine(node, domain_type)
        FOR candidate IN candidate_deliverables:
            deliverable = {}
            deliverable.id = "D" + (LENGTH(deliverable_list) + 1)
            deliverable.name = candidate.name
            deliverable.source_node = node.id
            APPEND deliverable TO deliverable_list

    # ===== 步骤2: 交付物规格表 - 标注格式/频率/质量标准/目标受众 =====
    FOR deliverable IN deliverable_list:
        # 格式标注
        IF domain_type == "A":
            deliverable.format = GUESS_format_content(deliverable.name)
        ELIF domain_type == "B":
            deliverable.format = GUESS_format_service(deliverable.name)
        ELIF domain_type == "C":
            deliverable.format = GUESS_format_marketing(deliverable.name)
        ELIF domain_type == "D":
            deliverable.format = GUESS_format_data(deliverable.name)
        ELIF domain_type == "F":
            deliverable.format = GUESS_format_customer_service(deliverable.name)
        ELSE:
            deliverable.format = ASK_USER("请指定" + deliverable.name + "的交付格式")

        # 频率标注
        deliverable.frequency = INFER_frequency(deliverable.name, domain_type)

        # 质量标准
        deliverable.quality_criteria = GENERATE_quality_criteria(deliverable, domain_type)

        # 目标受众
        deliverable.target_audience = s2_data.target_audience IF EXISTS ELSE INFER_audience(domain_type)

    # ===== 步骤3: 优先级分配(核心/增强) =====
    FOR deliverable IN deliverable_list:
        # 判定核心交付物：链路终节点对应的交付物为核心
        IF deliverable.source_node IS_END_OUTPUT_NODE(chain_nodes):
            deliverable.priority = "core"
        ELIF deliverable.name CONTAINS "品牌" OR deliverable.name CONTAINS "提案":
            deliverable.priority = "enhancement"
        ELIF deliverable.name CONTAINS "规范" OR deliverable.name CONTAINS "文档":
            deliverable.priority = "core"  # 支撑性文档也算核心
        ELSE:
            deliverable.priority = "enhancement"

    # ===== 步骤4: 确定每个交付物的唯一第一责任人 =====
    FOR deliverable IN deliverable_list:
        deliverable.owner_role = MAP_deliverable_to_role(deliverable, domain_type)

    # ===== 步骤5: 渠道分支判定(4条分线标准) =====
    # 分线标准: ①不同平台 ②不同受众 ③不同频率 ④不同质量流程
    channel_lines = {}
    line_counter = 1
    FOR deliverable IN deliverable_list:
        line_key = COMPUTE_channel_line_key(deliverable)
        IF line_key NOT IN channel_lines:
            channel_lines[line_key] = "Line_" + line_counter + "_" + line_key
            line_counter = line_counter + 1
        deliverable.channel_line = channel_lines[line_key]

    # ===== 步骤6: CTA策略(A型激活) =====
    IF domain_type == "A":
        FOR deliverable IN deliverable_list:
            IF deliverable.priority == "core":
                deliverable.cta_strategy = GENERATE_cta_A_type(deliverable)
                # A型CTA：引导用户互动(点赞/收藏/关注/评论)
    ELIF domain_type == "C":
        FOR deliverable IN deliverable_list:
            IF deliverable.priority == "core":
                deliverable.cta_strategy = GENERATE_cta_C_type(deliverable)
                # C型CTA：引导转化(咨询/试用/下单)

    # ===== 步骤7: 品牌声音规范(A/B/F型激活) =====
    IF domain_type IN ["A", "B", "F"]:
        brand_voice = {}
        IF domain_type == "A":
            brand_voice.tone = "亲和力+专业感"
            brand_voice.style_guide = "口语化但不失权威，善用emoji，避免学术腔"
        ELIF domain_type == "B":
            brand_voice.tone = "专业+可靠"
            brand_voice.style_guide = "结构化表达，数据支撑，避免模糊用语"
        ELIF domain_type == "F":
            brand_voice.tone = "温暖+高效"
            brand_voice.style_guide = "先共情再解决，语言简洁明确，避免机械感"
        FOR deliverable IN deliverable_list:
            deliverable.brand_voice = brand_voice

    # ===== 步骤8: 服务标准(B/F型激活) =====
    IF domain_type IN ["B", "F"]:
        service_standard = {}
        IF domain_type == "B":
            service_standard.response_time = "24小时内首次响应"
            service_standard.revision_rounds = "2轮修改"
            service_standard.quality_guarantee = "满足合同约定的验收标准"
        ELIF domain_type == "F":
            service_standard.response_time = "5分钟内首次响应"
            service_standard.resolution_target = "80%问题一次解决"
            service_standard.escalation_rule = "3轮未解决自动升级"
        FOR deliverable IN deliverable_list:
            deliverable.service_standard = service_standard

    # ===== 步骤9: 依赖图构建 =====
    cross_channel_sharing = []
    FOR d1 IN deliverable_list:
        FOR d2 IN deliverable_list:
            IF d1.id != d2.id AND HAS_SHARED_RESOURCE(d1, d2):
                shared = FIND_SHARED_RESOURCE(d1, d2)
                APPEND shared TO cross_channel_sharing
    cross_channel_sharing = UNIQUE(cross_channel_sharing)

    # ===== 步骤10: Q9平台选择强制确认 =====
    IF s2_data.platform IS_EMPTY OR s2_data.platform == "还没想好":
        platform_confirm = ASK_ONE("你计划在哪个平台使用专家团？请确认或选择")
        IF platform_confirm == "还没想好":
            platform_confirm = "workbuddy"  # 默认WorkBuddy
            OUTPUT "默认使用WorkBuddy，后续可在设置中更改" TO user
    ELSE:
        platform_confirm = s2_data.platform

    # ===== 质量门控 =====
    CALL protocol-quality-gate(stage=4, output={
        "deliverables": deliverable_list,
        "cross_channel_sharing": cross_channel_sharing
    })
    ASSERT LENGTH(deliverable_list) >= 1
    ASSERT EVERY deliverable HAS owner_role
    ASSERT EVERY deliverable HAS priority

    # ===== 产出输出 =====
    output = BUILD_output_according_to_output_schema({
        "deliverables": deliverable_list,
        "cross_channel_sharing": cross_channel_sharing
    })
    RETURN output

    # ===== 快速通道分支 =====
    FAST_TRACK_DELIVERABLE:
    fast_deliverable = {
        "id": "D1",
        "name": EXTRACT_SINGLE_DELIVERABLE(chain_nodes),
        "format": INFER_format_from_domain(domain_type),
        "frequency": "每日1篇",
        "quality_criteria": "基本质量标准",
        "target_audience": s2_data.target_audience,
        "owner_role": "solo-operator",
        "priority": "core",
        "channel_line": "Line_1_单渠道"
    }
    RETURN {
        "deliverables": [fast_deliverable],
        "cross_channel_sharing": ["素材库共用"]
    }
```

## 下一阶段路由

> 本阶段完成后，由 `team-orchestrator` 自动衔接至 `pipeline-s5-architecture-design`（阶段五：架构设计）。
> 衔接条件：交付物清单已锚定 + 优先级已分配 + Q9平台已强制确认。
> 用户无需手动触发下一阶段。

## 版本

1.0.0

---
*本Skill由全域专家团构建skills体系自动生成，版本1.0.0，日期2026-06-15*
