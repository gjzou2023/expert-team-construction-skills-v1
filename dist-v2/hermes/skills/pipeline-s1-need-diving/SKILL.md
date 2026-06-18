---
name: pipeline-s1-need-diving
description: 通过5-Why逐层追问(每次只问1个问题)挖掘真实需求，生成需求画像卡，初评复杂度。v1.4.0将需求澄清与Q1-Q9整合为分级需求采集流程（按用户角色动态调整 Use when: 用户说"阶段一、需求深潜、5-Why、需求画像、S1执行"等触发词。
version: 1.4.0
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [l1]
    related_skills: []
    requires_toolsets: []
---

# 阶段一：需求深潜

> **层级**: L1 | **版本**: 1.4.0 | **ID**: `pipeline-s1-need-diving` | **中文名**: 阶段一：需求深潜 | **英文名**: Stage 1: Need Diving
# 阶段一：需求深潜 (Stage 1: Need Diving)

> **层级**: L1 | **版本**: 1.4.0 | **ID**: `pipeline-s1-need-diving`
> **编排关系**: 本skill由 `team-orchestrator` 自动加载执行，用户不应直接触发。完成后自动衔接 `pipeline-s2-domain-disambiguation`。

## 概述

通过5-Why逐层追问(每次只问1个问题)挖掘真实需求，生成需求画像卡，初评复杂度。v1.4.0将需求澄清与Q1-Q9整合为分级需求采集流程（按用户角色动态调整问题数量）。

## 触发条件

当检测到以下关键词或场景时自动激活：开始, 帮我建, 我想做, 专家团, 需求, 刚开始

## 输入规范 (input_schema)

```json
{
  "type": "object",
  "properties": {
    "user_first_message": {
      "type": "string",
      "description": "用户首次交互消息"
    },
    "user_context": {
      "type": "object",
      "properties": {
        "experience_level": {
          "type": "string",
          "enum": [
            "novice",
            "intermediate",
            "advanced"
          ]
        },
        "team_size": {
          "type": "integer"
        }
      }
    }
  },
  "required": [
    "user_first_message",
    "user_context"
  ]
}
```

## 输出规范 (output_schema)

```json
{
  "type": "object",
  "properties": {
    "need_portrait": {
      "type": "object",
      "properties": {
        "core_need": {
          "type": "string"
        },
        "surface_need": {
          "type": "string"
        },
        "real_goal": {
          "type": "string"
        },
        "explicit_assumptions": {
          "type": "array",
          "items": {"type": "string"},
          "description": "基于不完整信息做出的显式假设列表（v1.3.0新增，standard/strict通道必填，fast通道可空）"
        },
        "clarification_complete": {
          "type": "boolean",
          "description": "是否已完成需求澄清（或用户选择跳过）（v1.3.0新增，v1.4.0按用户角色动态调整）"
        },
        "user_role": {
          "type": "string",
          "enum": ["decision_maker", "tech_lead", "project_manager", "explorer"],
          "description": "用户角色识别，影响后续输出风格（v1.3.0新增，v1.4.0与对偶映射表联动）"
        }
      }
    },
    "complexity_signals": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "initial_channel_hint": {
      "type": "string",
      "enum": [
        "fast",
        "standard",
        "strict"
      ]
    }
  },
  "required": [
    "need_portrait",
    "complexity_signals",
    "initial_channel_hint"
  ]
}
```

## 工具声明 (tool_declarations)

本Skill无外部工具依赖，纯提示词可执行。

## 执行逻辑

(0)需求澄清前置（v1.3.0新增）→(1)开场引导(§7话术)→(2)5-Why逐层追问(每次只问1个问题,§6.1#8)→(3)需求画像生成→(4)用户角色识别（v1.3.0新增）→(5)复杂度初评(调用core-complexity-channel-selector)→(6)输出需求确认卡。单问规则：信息采集阶段每次只问1个问题;确认阶段可一次性展示汇总卡。

## 分级需求采集流程（v1.4.0升级）

### 核心探测（必问，3个问题，所有角色）
1. **目标与约束**：想达到什么结果？最关键的约束是什么？
2. **阶段与范围**：当前处于什么阶段？战略方向还是具体执行？
3. **决策语境**：这个建议将用于什么决策？谁是最终决策者？

### 深度采集（按用户角色和通道调整）

| 用户角色 | Q1-Q9精简策略 | 必答题 | 可跳过题 |
|---------|-------------|--------|---------|
| 决策者 | Q1+Q5+Q7 | 目标/标准/约束 | Q2交付物细节/Q6经验水平 |
| 技术负责人 | Q1+Q2+Q7+Q8+Q9 | 目标/交付物/约束/平台/时间 | Q5标准 |
| 项目经理 | Q1+Q2+Q5+Q7+Q9 | 目标/交付物/标准/约束/时间 | Q8平台 |
| 探索者 | Q1+Q2+Q3 | 目标/交付物/受众 | Q5-Q9全部跳过 |

### 信息去重规则
- 核心探测中已获取的信息，Q1-Q9中不再重复提问
- 已在核心探测中回答的"目标"自动填入Q1
- 核心探测第3题的答案自动推断用户角色

## 用户角色识别与适配（v1.3.0新增）

在Q6（AI经验水平）之后，增加静默用户角色推断。根据用户表述自动识别人物画像：

| 用户角色 | 识别特征 | 输出适配规则 |
|---------|---------|------------|
| 决策者/CEO | 关注ROI、战略方向、竞品对比 | 输出精简，用决策矩阵，突出取舍 |
| 技术负责人 | 关注架构、选型、技术细节、可行性 | 可深入技术细节，用架构图描述 |
| 项目经理 | 关注实施路径、资源计划、里程碑 | 给WBS分解，标注依赖关系 |
| 探索者/学习者 | 关注全景概览、概念解释、入门指引 | 先给全景地图，再逐步引导深入 |

### 适配规则优先级

1. 决策者适配：精简冗余描述，用表格和数字说话
2. 技术负责人适配：提供技术实现细节和替代方案对比
3. 项目经理适配：提供时间线、任务拆解和资源估算
4. 探索者适配：先给全景概览，术语首次出现附解释，降低信息密度

## Few-shot 示例

### 示例1: 正常流程 - 小红书美食团队

**用户**: "我想建个AI专家团帮我运营小红书美食号"

**Q1**: 🔘 内容创作与传播
**Q2**: 🔘 会做但太耗时想自动化 — "每周做3篇探店内容要花我20+小时"
**Q3**: 1轮5-Why — "因为这是我收入来源，少做一篇就少一笔"
**Q4**: 🔘 一份可直接发布的成品
**Q5**: 🔘 就我一个人
**Q6**: 🔘 建过简单的AI助手
**Q7**: 小红书图文笔记+品牌合作帖
**Q8**: 🔘 只做国内市场
**Q9**: 🔘 WorkBuddy

**需求画像卡**: 领域方向=内容创作与传播-美食探店 | 核心痛点=周均3篇内容创作太耗时 | 真实需求=自动化美食探店内容生产 | 期望成果=可直接发布的图文成品 | 团队规模=1人 | AI经验=有经验 | 目标触点=小红书图文 | 目标市场=国内 | 目标平台=WorkBuddy

### 示例2: 异常流程 - 用户全程选"不确定"

**用户**: "我也不太清楚，就是觉得AI应该能帮我做点什么"

**Q1**: "不确定..." → 小白引导话术: "没关系，从最简单的开始——你平时什么行业?"
- 用户: "我是做财务的"

**Q2**: "不知道选哪个" → 小白引导话术: "是觉得不会做？还是花太多时间？还是质量不稳定？"
- 用户: "花太多时间吧，每个月都要做报表"

**Q3**: 连续"不知道" → 小白引导话术: "换种问法——如果有个AI助手，你最希望它帮你省什么？自动收数据？自动生成报表？还是自动发给老板？"
- 用户: "自动生成报表！"

**Q4**: 🔘 一份可直接发布的成品
**Q5**: 🔘 就我一个
**Q6**: 🔘 没用过
**Q7**: "报表发给谁？" → 给老板看
**Q8**: 🔘 国内
**Q9**: "还没想好" → 推荐WorkBuddy（适合新手）

**需求画像卡**: 领域方向=数据分析-财务报表自动化 | 核心痛点=每月手工做报表耗费一整天 | 真实需求=自动生成财务报表 | 期望成果=可交付的报表成品 | 团队规模=1人 | AI经验=完全新手 | 目标触点=邮件/内部系统 | 目标市场=国内 | 目标平台=WorkBuddy

### 示例3: 快速通道 - 个人财税科普号

**用户**: "我是做个人财税科普的，想用AI自动写小红书和公众号文章"

**Q1**: 🔘 内容创作与传播
**Q2**: 🔘 会做但太耗时想自动化 — "我每周要出3篇，太累了"
**Q3**: 1轮即明确需求
**Q4**: 🔘 一份可直接发布的成品
**Q5**: 🔘 就我一个人
**Q6**: 🔘 建过简单的AI助手，想做得更专业
**Q7**: 小红书图文 + 公众号深度长文
**Q8**: 🔘 只做国内市场
**Q9**: 🔘 WorkBuddy → 确认

**需求画像卡**: 领域方向=内容创作与传播-财税科普 | 核心痛点=周均3篇产出压力 | 真实需求=自动化双渠道内容生产 | 期望成果=每天一份可发布的成品 | 复杂度信号=走快速通道(交付物单一) | 目标平台=WorkBuddy

### 示例4: 非A型场景 - 制造业设备维护知识库(C型)

**用户**: "我们工厂有200台设备，想做AI帮维护人员快速查故障维修指南"

**Q1**: 🔘 专业知识服务
**Q2**: 🔘 质量不稳定想标准化 — "老师傅经验没传承，新人查手册太慢"
**Q3**: 1轮5-Why — "因为设备停机1小时损失就上万"
**Q4**: 🔘 随时可问顾问
**Q5**: 🔘 小团队2-5人
**Q6**: 🔘 建过简单的，想接入设备数据库
**Q7**: 内部知识库+微信企业号推送
**Q8**: 🔘 只做国内市场
**Q9**: 🔘 WorkBuddy + 需要RAG挂载

**需求画像卡**: 领域方向=专业知识服务-设备维护 | 核心痛点=新人查手册慢+老师傅经验流失 | 真实需求=智能设备故障检索+维修指南生成 | 期望成果=随时可问的设备维护顾问 | 团队规模=small | AI经验=有经验 | 目标触点=内部知识库+企微 | 目标市场=国内 | 目标平台=WorkBuddy(RAG)

## 知识库挂载点 (knowledge_base_mount_points)

- **[static]** `file://./knowledge/stage-1-rules.md` — 阶段1执行规则
- **[dynamic]** `file://./knowledge/stage-1-state.json` — 阶段1运行时状态

## 依赖关系

- `core-mental-model-engine`
- `core-complexity-channel-selector`

## Q1-Q9问题序列与详细执行逻辑

```text
FUNCTION execute_need_diving():
    QUESTION_SEQUENCE = [
      Q1: 你想让专家团帮你搞定哪个领域的事？
          选项: 内容创作与传播 / 客户获取与转化 / 专业知识服务 / 数据分析与洞察 / 流程自动化 / 客户服务与支持 / 自定义
      Q2: 在这个领域里，你最头疼、最想甩给AI的是哪件事？
          选项: 从零开始不知道怎么做 / 会做但太耗时想自动化 / 质量不稳定想标准化 / 自定义
      Q3: 5-Why追问，最多3轮:
          为什么这件事对你特别重要？
          为什么现有方式解决不了？
          如果完美解决，你最先感受到的变化是什么？
      Q4: 如果专家团跑起来，你每天最希望看到什么产出？
          选项: 可直接发布成品 / 自动运行数据流水线 / 随时可问顾问 / 自动处理客户工单 / 自定义
      Q5: 你是一个人还是有团队？
          选项: 一个人 / 小团队2-5人 / 较大团队5人以上 / 自定义
      Q6: 你之前用过AI工具吗？
          选项: 完全新手 / 用过聊天工具 / 建过简单助手 / 自定义
      Q7: 目标触点/交付场景识别，先给领域例子，再判断是否需要分线。
      Q8: 目标受众主要在哪里？
          选项: 国内 / 海外 / 国内外都做 / 自定义
      Q9: 你打算在哪个AI Agent平台上使用这个专家团？
          选项: WorkBuddy / Codex CLI / Hermes Agent / Coze / Dify / 飞书 / n8n / 其他或还没想好
    ]
    FOR question IN QUESTION_SEQUENCE:
        CALL protocol-single-question-guidance(question)
        response = WAIT_FOR_USER()
        IF response is unclear:
            ask_one_clarification()
        STORE response
    IF Q9 == "还没想好":
        # 改进#10修复: 从Q1中文选项推导domain_type枚举
        DOMAIN_TYPE_MAP = {
            "内容创作与传播": "A",
            "客户获取与转化": "C",   # 按classifier定义C=知识管理(获客转化归C型，见改进#25语义统一)
            "专业知识服务": "C",     # 按classifier定义C=知识管理
            "数据分析与洞察": "D",
            "流程自动化": "D",       # 与classifier一致
            "客户服务与支持": "F",
            "自定义": "A"            # 默认A型
        }
        domain_type = DOMAIN_TYPE_MAP.get(answers.Q1, "A")
        recommendation = recommend_platform(domain_type, Q6)
        WAIT_FOR_CONFIRMATION()
    RETURN need_portrait_card
```

## 详细执行逻辑

```text
FUNCTION execute_pipeline_s1_need_diving(input):
    # ===== 阶段一：需求深潜 - 入口校验 =====
    ASSERT input.user_first_message IS NOT EMPTY
    ASSERT input.user_context EXISTS
    LOAD context_inheritance FROM upstream

    # ===== 开场引导(§7话术) =====
    CALL protocol-single-question-guidance("开场")
    greeting = GENERATE_greeting(input.user_context.experience_level)
    OUTPUT greeting TO user

    # ===== 初始化问题序列 =====
    QUESTION_SEQUENCE = [Q1, Q2, Q3, Q4, Q5, Q6, Q7, Q8, Q9]
    answers = {}
    current_q_index = 0

    # ===== Q1: 领域方向选择 =====
    CALL protocol-single-question-guidance(Q1)
    answers.Q1 = WAIT_FOR_USER()
    IF answers.Q1 == "自定义":
        answers.Q1_detail = ASK_ONE("请描述你想要的领域方向")
    IF answers.Q1 NOT IN ["内容创作与传播", "客户获取与转化", "专业知识服务", "数据分析与洞察", "流程自动化", "客户服务与支持", "自定义"]:
        answers.Q1 = ASK_ONE_CLARIFICATION("请从给定选项中选择，或选择'自定义'输入")

    # ===== Q2: 核心痛点识别 =====
    CALL protocol-single-question-guidance(Q2)
    answers.Q2 = WAIT_FOR_USER()
    IF answers.Q2 == "自定义":
        answers.Q2_detail = ASK_ONE("请描述你最头疼的事情")
    IF answers.Q2 == "从零开始不知道怎么做":
        SET novice_flag = TRUE

    # ===== Q3: 5-Why追问(最多3轮) =====
    # 改进#14修复: 添加skip检查，与用户角色表"必答题"列对齐(决策者必答Q1+Q5+Q7不含Q3，可跳过)
    IF "Q3" NOT IN skip_set:
        CALL protocol-single-question-guidance(Q3)
        max_rounds = 3
        why_round = 0
        real_need = answers.Q2
        FOR why_round FROM 1 TO max_rounds:
            IF why_round == 1:
                follow_up = "为什么这件事对你特别重要？"
            ELIF why_round == 2:
                follow_up = "为什么现有方式解决不了？"
            ELIF why_round == 3:
                follow_up = "如果完美解决，你最先感受到的变化是什么？"
            OUTPUT follow_up TO user
            response = WAIT_FOR_USER()
            IF response IS clear_and_specific:
                real_need = EXTRACT_core_need(response)
                BREAK  # 提前获得真实需求，结束追问
            ELIF response IN ["不确定", "不知道", "没想过"]:
                IF why_round < max_rounds:
                    CONTINUE  # 继续追问
                ELSE:
                    real_need = answers.Q2  # 追问失败，使用Q2表层需求
        answers.Q3 = real_need
    ELSE:
        # 角色跳过Q3，直接使用Q2作为core_need
        answers.Q3 = answers.Q2

    # ===== I-2.8改进: 核心探测完成后推断用户角色，动态调整后续问题 =====
    user_role = INFER_USER_ROLE(answers, input.user_context)
    # 按用户角色确定可跳过的问题
    SKIP_MAP = {
        "decision_maker": ["Q2", "Q6"],            # 不关心交付物细节和经验水平
        "tech_lead": ["Q5"],                        # 团队规模可能不相关
        "project_manager": ["Q8"],                  # 平台不相关
        "explorer": ["Q5", "Q6", "Q7", "Q8", "Q9"] # 快速获取核心信息
    }
    skip_set = SKIP_MAP.get(user_role, [])
    OUTPUT "[内部] 用户角色推断: " + user_role + ", 跳过问题: " + JOIN(skip_set) TO log

    # ===== Q4: 期望成果形态 =====
    IF "Q4" NOT IN skip_set:
        CALL protocol-single-question-guidance(Q4)
        answers.Q4 = WAIT_FOR_USER()
        IF answers.Q4 == "可直接发布成品":
            SET deliverable_type = "成品型"
        ELIF answers.Q4 == "自动运行数据流水线":
            SET deliverable_type = "流水线型"
        ELIF answers.Q4 == "随时可问顾问":
            SET deliverable_type = "顾问型"
        ELIF answers.Q4 == "自动处理客户工单":
            SET deliverable_type = "工单型"
        ELSE:
            answers.Q4_detail = ASK_ONE("请描述你期望的产出形态")
    ELSE:
        # 角色跳过，使用默认值
        answers.Q4 = "自动运行数据流水线" IF user_role == "tech_lead" ELSE "可直接发布成品"
        SET deliverable_type = "default"

    # ===== Q5: 团队规模 =====
    IF "Q5" NOT IN skip_set:
        CALL protocol-single-question-guidance(Q5)
        answers.Q5 = WAIT_FOR_USER()
        IF answers.Q5 == "一个人":
            SET team_size = 1
            SET solo_flag = TRUE
        ELIF answers.Q5 == "小团队2-5人":
            SET team_size = 3  # 改进#34修复: 统一为integer，取中值
            SET solo_flag = FALSE
        ELIF answers.Q5 == "较大团队5人以上":
            SET team_size = 6  # 改进#34修复: 统一为integer，取中值
            SET solo_flag = FALSE
        ELSE:
            answers.Q5_detail = ASK_ONE("请说明你的团队情况")
    ELSE:
        # 角色跳过，使用默认值
        answers.Q5 = "小团队2-5人"
        SET team_size = 3  # 改进#34修复: 统一为integer
        SET solo_flag = FALSE

    # ===== Q6: AI经验水平 =====
    IF "Q6" NOT IN skip_set:
        CALL protocol-single-question-guidance(Q6)
        answers.Q6 = WAIT_FOR_USER()
        IF answers.Q6 == "完全新手":
            SET ai_experience = "novice"
        ELIF answers.Q6 == "用过聊天工具":
            SET ai_experience = "intermediate_basic"
        ELIF answers.Q6 == "建过简单助手":
            SET ai_experience = "intermediate_advanced"
        ELSE:
            SET ai_experience = "advanced"
    ELSE:
        # 角色跳过，使用默认值
        answers.Q6 = "建过简单助手"
        SET ai_experience = "intermediate_advanced"

    # ===== Q7: 目标触点/交付场景识别 =====
    IF "Q7" NOT IN skip_set:
        CALL protocol-single-question-guidance(Q7)
        # 先根据Q1领域给出示例
        domain_examples = GET_domain_touchpoint_examples(answers.Q1)
        OUTPUT "你的领域常见触点示例：" + domain_examples TO user
        answers.Q7 = WAIT_FOR_USER()
        # 判断是否需要分线(多平台/多格式)
        touchpoint_list = PARSE_touchpoints(answers.Q7)
        IF LENGTH(touchpoint_list) > 1:
            SET multi_channel_flag = TRUE
        ELSE:
            SET multi_channel_flag = FALSE
    ELSE:
        # 角色跳过，使用默认值
        answers.Q7 = "线上发布"
        SET multi_channel_flag = FALSE

    # ===== Q8: 目标市场 =====
    IF "Q8" NOT IN skip_set:
        CALL protocol-single-question-guidance(Q8)
        answers.Q8 = WAIT_FOR_USER()
        IF answers.Q8 == "国内":
            SET market = "domestic"
        ELIF answers.Q8 == "海外":
            SET market = "overseas"
        ELIF answers.Q8 == "国内外都做":
            SET market = "global"
        ELSE:
            SET market = "domestic"  # 默认国内
    ELSE:
        # 角色跳过，使用默认值
        answers.Q8 = "国内"
        SET market = "domestic"

    # ===== Q9: 目标平台选择(特殊处理) =====
    IF "Q9" NOT IN skip_set:
        CALL protocol-single-question-guidance(Q9)
        answers.Q9 = WAIT_FOR_USER()
        IF answers.Q9 == "还没想好":
            # 调用平台推荐函数
            recommendation = CALL recommend_platform(answers.Q1, ai_experience, team_size)
            OUTPUT "根据你的情况，推荐使用" + recommendation.name + "，原因：" + recommendation.reason TO user
            confirmed = WAIT_FOR_CONFIRMATION()
            IF confirmed:
                answers.Q9 = recommendation.id
            ELSE:
                answers.Q9 = "workbuddy"  # 默认WorkBuddy
        ELIF answers.Q9 == "其他":
            answers.Q9_detail = ASK_ONE("请输入你想使用的平台名称")
    ELSE:
        # 角色跳过，使用默认值
        CALL recommend_platform(answers.Q1, ai_experience, team_size)
        answers.Q9 = "workbuddy"  # 默认WorkBuddy

    # ===== 生成需求画像卡 =====
    # 改进#5修复: 字段名使用英文键与output_schema对齐
    need_portrait_card = {
        "core_need": answers.Q3,            # 真实需求 → core_need
        "surface_need": answers.Q2,         # 核心痛点 → surface_need
        "real_goal": EXTRACT_REAL_GOAL(answers.Q3),
        "explicit_assumptions": EXTRACT_ASSUMPTIONS(answers),
        "clarification_complete": TRUE,
        "user_role": user_role
    }
    # 辅助上下文字段(向后兼容下游Skill可能引用的中文键)
    need_portrait_card._context = {
        "领域方向": answers.Q1,
        "期望成果": answers.Q4,
        "团队规模": team_size,
        "AI经验": answers.Q6,
        "目标触点": answers.Q7,
        "目标市场": answers.Q8,
        "目标平台": answers.Q9
    }

    # ===== 复杂度初评(调用core-complexity-channel-selector) =====
    complexity_signals = []
    IF team_size == 1 AND multi_channel_flag == FALSE AND ai_experience IN ["intermediate_advanced", "advanced"]:
        APPEND "fast_channel_candidate" TO complexity_signals
    ELIF multi_channel_flag == TRUE OR answers.Q1 IN ["客户获取与转化", "专业知识服务"]:
        APPEND "standard_channel_candidate" TO complexity_signals
    IF answers.Q1 IN ["专业知识服务"] AND market == "global":
        APPEND "strict_channel_candidate" TO complexity_signals

    channel_hint = CALL core-complexity-channel-selector(complexity_signals, need_portrait_card)

    # ===== 输出需求确认卡(确认阶段可一次性展示汇总) =====
    OUTPUT need_portrait_card TO user
    OUTPUT "通道建议：" + channel_hint TO user
    final_confirm = WAIT_FOR_CONFIRMATION()

    # ===== 质量门控 =====
    CALL protocol-quality-gate(stage=1, output=need_portrait_card)
    ASSERT need_portrait_card HAS ALL_REQUIRED_FIELDS
    ASSERT channel_hint IN ["fast", "standard", "strict"]

    # ===== 产出输出 =====
    output = BUILD_output_according_to_output_schema({
        "need_portrait": need_portrait_card,
        "complexity_signals": complexity_signals,
        "initial_channel_hint": channel_hint
    })
    RETURN output

// I-2.8新增: 核心探测完成后推断用户角色
FUNCTION INFER_USER_ROLE(answers, user_context):
    // 根据前三问的回答风格和已有上下文推断角色
    IF user_context.experience_level IN ["advanced", "intermediate"] AND answers.Q2 IN ["会做但太耗时想自动化", "质量不稳定想标准化"]:
        IF answers.Q1 IN ["客户获取与转化", "流程自动化"]:
            RETURN "decision_maker"
        ELIF answers.Q1 IN ["数据分析与洞察"]:
            RETURN "tech_lead"
        ELSE:
            RETURN "project_manager"
    IF user_context.experience_level == "novice" OR answers.Q2 == "从零开始不知道怎么做":
        RETURN "explorer"
    RETURN "project_manager"  // 默认角色
```

## 版本

1.4.0

## 下一阶段路由

> 本阶段完成后，由 `team-orchestrator` 自动衔接至 `pipeline-s2-domain-disambiguation`（阶段二：领域分类与消歧）。
> 衔接条件：需求画像卡已生成 + 用户已确认核心需求 + 复杂度初评已完成。
> 用户无需手动触发下一阶段。

---
*本Skill由全域专家团构建skills体系生成，版本1.4.0，日期2026-06-17*
