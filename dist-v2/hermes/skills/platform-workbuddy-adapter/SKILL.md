---
name: platform-workbuddy-adapter
description: 生成.workbuddy-plugin/plugin.json+agents/*.md+avatars+settings.json(Team型)。Agent I Use when: 用户说"platform-workbuddy-adapter、WorkBuddy适配器、L3-WB"等触发词。
version: 1.1.0
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [l3]
    related_skills: []
    requires_toolsets: []
---

> **注意**：本 skill 的核心规则已内联至 `team-orchestrator/SKILL.md` 的 `L3` 章节。
> 执行时优先读取 team-orchestrator 的内联指引，仅在需要完整逻辑时再读取本文件。
>
# WorkBuddy平台适配器

> **层级**: L3 | **版本**: 1.1.0 | **ID**: `platform-workbuddy-adapter` | **中文名**: WorkBuddy平台适配器 | **英文名**: WorkBuddy Adapter
# WorkBuddy平台适配器 (WorkBuddy Adapter)

> **层级**: L3 | **版本**: 1.1.0 | **ID**: `platform-workbuddy-adapter`
> **编排关系**: 本skill由 `team-orchestrator` 按需自动加载执行，属于全域专家团构建skills系统的内部组件，用户不应直接触发。

## 概述

生成.workbuddy-plugin/plugin.json+agents/*.MD+avatars+settings.json(Team型)。Agent ID kebab-case,花名2-3字,categoryId标准列表,tags 3个,quickPrompts 3个,displayDescription中文40-50字。

## 触发条件

当检测到以下关键词或场景时自动激活：workbuddy, workbuddy, 平台适配, 输出格式

## 输入规范 (input_schema)

```json
{
  "type": "object",
  "properties": {
    "architecture": {
      "type": "object",
      "description": "S5架构输出"
    },
    "roles": {
      "type": "array",
      "description": "角色定义列表"
    },
    "sop": {
      "type": "object",
      "description": "SOP定义"
    },
    "expert_type": {
      "type": "string",
      "enum": [
        "team",
        "agent"
      ]
    },
    "track": {
      "type": "string",
      "enum": [
        "fast",
        "standard",
        "strict"
      ]
    }
  },
  "required": [
    "architecture",
    "roles",
    "expert_type"
  ]
}
```

## 输出规范 (output_schema)

```json
{
  "type": "object",
  "properties": {
    "output_format": {
      "type": "string",
      "description": "plugin.json + agents/*.md + avatars/*.png + settings.json(Team型) + references/(可选) + skills/(可选)"
    },
    "platform_specific_config": {
      "type": "object"
    },
    "degradation_plan": {
      "type": "object"
    }
  },
  "required": [
    "output_format",
    "platform_specific_config"
  ]
}
```

## 工具声明 (tool_declarations)

本Skill无外部工具依赖，纯提示词可执行。

## 执行逻辑

目标平台=WorkBuddy平台适配器时激活。输出格式：plugin.json + agents/*.md + avatars/*.png + settings.json(Team型) + references/(可选) + skills/(可选)。平台特定规则：Team型:settings.json中teamInfo.leadAgent+memberAgents;主理人用spawn+SendMessage编排;所有跨成员信息流经主理人中转。Automation:§5.9定时触发使用WorkBuddy Automation功能。

## Few-shot 示例

### 示例 1: Team型专家团生成

**输入**:
```json
{
  "architecture": {
    "domain_type": "A",
    "platform": "workbuddy"
  },
  "roles": [
    {"id": "chief-editor", "name": "林语", "profession": "总编辑"},
    {"id": "content-writer", "name": "苏砚", "profession": "内容主笔"},
    {"id": "visual-designer", "name": "乔雨", "profession": "视觉设计师"}
  ],
  "expert_type": "team",
  "track": "standard"
}
```

**输出**:
```json
{
  "output_format": "plugin.json + agents/*.md + avatars/*.png + settings.json(Team型)",
  "platform_specific_config": {
    "teamInfo": {
      "leadAgent": "chief-editor",
      "memberAgents": ["content-writer", "visual-designer"],
      "orchestration": "leadAgent使用spawn+SendMessage编排，跨成员信息流经leadAgent中转"
    }
  },
  "generated_files": [
    "plugin.json: id=content-team, categoryId=content-creation, tags=[内容创作,content,团队协作,team,编辑工作流,editorial]",
    "agents/chief-editor.md: displayDescription='负责选题策划和内容质量把控的总编辑角色'",
    "settings.json: type=team, automation=WorkBuddy Automation功能实现§5.9定时触发"
  ]
}
```

### 示例 2: 强监管领域合规拦截

**输入**:
```json
{
  "architecture": {
    "domain_type": "A",
    "platform": "workbuddy",
    "regulated": true
  },
  "roles": [
    {"id": "medical-advisor", "name": "陈济", "profession": "医学顾问"}
  ],
  "expert_type": "agent",
  "track": "strict"
}
```

**输出**:
```json
{
  "status": "blocked_or_review",
  "blocked_reason": "医疗领域触发生命健康强监管规则，须经protocol-compliance-engine审查",
  "required_call": "protocol-compliance-engine",
  "next_action": "人工审查医疗声明合规性，确认无直接承诺疗效/安全性表述后放行"
}
```

### 示例 3: 快速通道单Agent生成

**输入**:
```json
{
  "architecture": {
    "domain_type": "A",
    "platform": "workbuddy",
    "role_count": 1
  },
  "roles": [
    {"id": "social-assistant", "name": "安之", "profession": "社交媒体助理"}
  ],
  "expert_type": "agent",
  "track": "fast"
}
```

**输出**:
```json
{
  "status": "simplified",
  "output_format": "plugin.json + agents/*.md + avatars/*.png",
  "generated_files": [
    "plugin.json: id=social-assistant, categoryId=social-media, tags=[社交媒体,social,内容助理,assistant,效率工具,productivity]",
    "settings.json: type=agent (Team型配置项省略,无memberAgents)",
    "agents/social-assistant.md: quickPrompts[0]=defaultInitPrompt='帮我批量生成本周社交媒体文案'"
  ],
  "degradation_plan": {
    "strategy": "保留核心交付物，跳过references/skills可选目录"
  }
}
```

## 知识库挂载点 (knowledge_base_mount_points)

- **[static]** `file://platform/platform-workbuddy-adapter/format-spec` — WorkBuddy平台适配器格式规范

## 依赖关系

- `pipeline-s7-expert-package-generation`

## WorkBuddy描述修复与命名约束

生成`.workbuddy-plugin/plugin.json`、`agents/*.md`、`avatars/*.png`、`settings.json`和可选`references/`、`skills/`。Agent ID必须使用kebab-case；花名使用2-3字正常人名风格，特殊情况可4字；主理人profession禁止使用团长、主理人、负责人等通用title；tags恰好3个，quickPrompts恰好3个，displayDescription为中文40-50字。

## 详细执行逻辑

```text
FUNCTION execute_platform_workbuddy_adapter(input):
    ASSERT input matches input_schema
    ASSERT input.architecture != NULL
    ASSERT input.roles != NULL AND LEN(input.roles) >= 1
    ASSERT input.expert_type IN ["team", "agent"]

    // 阶段1: 合规前置检查
    CALL protocol_compliance_engine(input.architecture.domain_type, input.track)
    IF compliance_result.status == "blocked":
        RETURN {"status": "blocked_or_review", "required_call": "protocol-compliance-engine"}

    // 阶段2: 构建plugin.json核心结构
    plugin_id = GENERATE_kebab_case(input.architecture.domain_label)
    ASSERT MATCH(plugin_id, /^[a-z][a-z0-9-]*$/)
    category_id = SELECT_FROM_STANDARD_LIST(input.architecture.domain_type)
    ASSERT category_id IN VALID_CATEGORY_IDS

    // 阶段3: 生成tags(恰好3个,中英文)
    tags = []
    FOR i FROM 1 TO 3:
        tag_zh = SELECT_RELEVANT_TAG(input.roles, input.architecture, i, "zh")
        tag_en = SELECT_RELEVANT_TAG(input.roles, input.architecture, i, "en")
        APPEND tags, {"zh": tag_zh, "en": tag_en}
    ASSERT LEN(tags) == 3

    // 阶段4: 为每个角色生成Agent配置
    agents_config = []
    FOR EACH role IN input.roles:
        agent_id = GENERATE_kebab_case(role.profession)
        ASSERT MATCH(agent_id, /^[a-z][a-z0-9-]*$/)

        // 花名校验: 2-3字正常人名风格
        IF LEN(role.name) < 2 OR LEN(role.name) > 3:
            IF NOT (LEN(role.name) == 4 AND role.special_name_justified):
                LOG_WARNING("花名'" + role.name + "'不符合2-3字规范")

        // displayDescription校验: 中文40-50字
        desc = GENERATE_display_description(role, input.architecture)
        desc_len = COUNT_CHINESE_CHARS(desc)
        ASSERT desc_len >= 40 AND desc_len <= 50

        // quickPrompts生成(恰好3个,中英文,第一条=defaultInitPrompt)
        quick_prompts = []
        default_prompt = GENERATE_default_init_prompt(role)
        APPEND quick_prompts, {"zh": default_prompt.zh, "en": default_prompt.en}
        FOR j FROM 2 TO 3:
            prompt = GENERATE_quick_prompt(role, j)
            APPEND quick_prompts, {"zh": prompt.zh, "en": prompt.en}
        ASSERT LEN(quick_prompts) == 3

        // 生成agents/{agent_id}.md
        agent_md = BUILD_AGENT_MARKDOWN(agent_id, role.name, role.profession, desc, quick_prompts)
        APPEND agents_config, agent_md

    // 阶段5: Team型配置
    IF input.expert_type == "team":
        ASSERT LEN(input.roles) >= 4
        lead_agent = IDENTIFY_LEAD_AGENT(input.roles)
        member_agents = FILTER(input.roles, lambda r: r.id != lead_agent.id)

        team_info = {
            "leadAgent": lead_agent.id,
            "memberAgents": MAP(member_agents, lambda r: r.id),
            "orchestration": "leadAgent使用spawn+SendMessage编排,跨成员信息流经leadAgent中转"
        }
        ASSERT team_info.leadAgent != NULL
        ASSERT LEN(team_info.memberAgents) >= 1

    // 阶段6: settings.json构建
    settings = {
        "type": input.expert_type,
        "agents": MAP(agents_config, lambda a: a.id)
    }
    IF input.expert_type == "team":
        settings.teamInfo = team_info

    // 阶段7: §5.9定时触发配置(Automation)
    IF input.sop.has_schedule_trigger:
        automation_config = BUILD_AUTOMATION_CONFIG(input.sop.schedule)
        settings.automation = automation_config
        // 使用WorkBuddy Automation功能实现定时触发

    // 阶段8: 快速通道降级处理
    IF input.track == "fast":
        // 保留核心交付物,跳过references/skills可选目录
        output_files = ["plugin.json", "agents/*.md", "avatars/*.png", "settings.json"]
    ELIF input.track == "standard":
        output_files = ["plugin.json", "agents/*.md", "avatars/*.png", "settings.json", "references/"]
    ELSE:
        output_files = ["plugin.json", "agents/*.md", "avatars/*.png", "settings.json", "references/", "skills/"]

    // 阶段9: 质量门控
    CALL protocol_quality_gate(agents_config, plugin_id, tags, settings)
    IF quality_gate_result.violations:
        FIX_VIOLATIONS(quality_gate_result.violations)

    output = {
        "output_format": JOIN(output_files, " + "),
        "platform_specific_config": {"teamInfo": team_info IF input.expert_type == "team" ELSE NULL},
        "generated_files": output_files
    }
    RETURN output
```

## 版本

1.0.0

---
*本Skill由全域专家团构建skills体系自动生成，版本1.1.0，日期2026-06-16*
