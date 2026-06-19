---
name: platform-hermes-adapter
description: 生成skills/{skill-name}/SKILL.md+context/{context-name}.md。持续运行+内置定时+消息监听 Use when: 用户说"platform-hermes-adapter、Hermes适配器、L3-Hermes"等触发词。
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
# Hermes Agent平台适配器

> **层级**: L3 | **版本**: 1.1.0 | **ID**: `platform-hermes-adapter` | **中文名**: Hermes Agent平台适配器 | **英文名**: Hermes Agent Adapter
# Hermes Agent平台适配器 (Hermes Agent Adapter)

> **层级**: L3 | **版本**: 1.1.0 | **ID**: `platform-hermes-adapter`
> **编排关系**: 本skill由 `team-orchestrator` 按需自动加载执行，属于全域专家团构建skills系统的内部组件，用户不应直接触发。

## 概述

生成skills/{skill-name}/SKILL.md+context/{context-name}.md。持续运行+内置定时+消息监听。

## 触发条件

当检测到以下关键词或场景时自动激活：hermes, hermes, 平台适配, 输出格式

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
      "description": "skills/{skill-name}/SKILL.md + context/{context-name}.md"
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

目标平台=Hermes Agent平台适配器时激活。输出格式：skills/{skill-name}/SKILL.md + context/{context-name}.md。平台特定规则：持续运行+内置定时+消息监听;在SKILL.md中定义schedule字段和event listener。

## Few-shot 示例

### 示例 1: 持续运行技能生成

**输入**:
```json
{
  "architecture": {
    "domain_type": "B",
    "platform": "hermes"
  },
  "roles": [
    {"id": "monitor-agent", "name": "守一", "profession": "系统监控员"},
    {"id": "alert-handler", "name": "应辰", "profession": "告警处理员"}
  ],
  "expert_type": "team",
  "track": "standard"
}
```

**输出**:
```json
{
  "output_format": "skills/{skill-name}/SKILL.md + context/{context-name}.md",
  "platform_specific_config": {
    "skills/monitor-system/SKILL.md": "schedule字段定义定时巡检,event listener监听系统事件,持续运行模式",
    "skills/alert-handling/SKILL.md": "schedule字段定义告警响应间隔,内置消息监听触发处理流程",
    "context/system-state.md": "维护运行时状态上下文,跨技能共享"
  }
}
```

### 示例 2: 强监管领域合规拦截

**输入**:
```json
{
  "architecture": {
    "domain_type": "A",
    "platform": "hermes",
    "regulated": true
  },
  "roles": [
    {"id": "medical-reviewer", "name": "陈济", "profession": "医学审查员"}
  ],
  "expert_type": "agent",
  "track": "strict"
}
```

**输出**:
```json
{
  "status": "blocked_or_review",
  "blocked_reason": "医疗领域触发合规审查，Schedule触发前须经人工确认",
  "required_call": "protocol-compliance-engine",
  "next_action": "在SKILL.md中标注schedule触发需合规引擎预检查"
}
```

### 示例 3: 快速通道单技能

**输入**:
```json
{
  "architecture": {
    "domain_type": "A",
    "platform": "hermes",
    "role_count": 1
  },
  "roles": [
    {"id": "daily-digest", "name": "简闻", "profession": "日报生成员"}
  ],
  "expert_type": "agent",
  "track": "fast"
}
```

**输出**:
```json
{
  "status": "simplified",
  "output_format": "skills/daily-digest/SKILL.md",
  "generated_files": [
    "skills/daily-digest/SKILL.md: schedule=每工作日08:00触发, event listener=无,单技能持续运行模式"
  ],
  "degradation_plan": {
    "strategy": "省略context共享文件,保留核心SKILL.md定义"
  }
}
```

## 知识库挂载点 (knowledge_base_mount_points)


> **⚠️ 挂载点说明**：以下 `file://` 路径为概念性挂载点（conceptual mount points），用于声明本 skill 的知识库依赖结构。它们不是物理文件路径，不需要实际加载文件。执行时请直接依据本 SKILL.md 正文中的规则定义和伪代码逻辑工作。
- **[static]** `file://platform/platform-hermes-adapter/format-spec` — Hermes Agent平台适配器格式规范

## 依赖关系

- `pipeline-s7-expert-package-generation`

## 详细执行逻辑

```text
FUNCTION execute_platform_hermes_adapter(input):
    ASSERT input matches input_schema
    ASSERT input.architecture != NULL
    ASSERT input.roles != NULL AND LEN(input.roles) >= 1

    // 阶段1: 合规前置检查
    CALL protocol_compliance_engine(input.architecture.domain_type, input.track)
    IF compliance_result.status == "blocked":
        RETURN {"status": "blocked_or_review", "required_call": "protocol-compliance-engine"}

    // 阶段2: 初始化Hermes目录结构
    skills_dir = "skills/"
    context_dir = "context/"
    skill_names = []

    // 阶段3: 为每个角色生成SKILL.md
    FOR EACH role IN input.roles:
        skill_name = GENERATE_kebab_case(role.profession)
        ASSERT MATCH(skill_name, /^[a-z][a-z0-9-]*$/)
        APPEND skill_names, skill_name

        // 构建SKILL.md核心内容
        skill_md_content = ""

        // 3a: 定义触发条件(trigger_keywords)
        trigger_keywords = EXTRACT_TRIGGER_KEYWORDS(role.profession, input.architecture)
        APPEND skill_md_content, "## 触发条件\n" + JOIN(trigger_keywords, ", ")

        // 3b: 定义schedule字段(持续运行+内置定时)
        IF input.sop.has_schedule_trigger:
            schedule_config = {
                "type": "cron",
                "expression": EXTRACT_CRON(input.sop.schedule),
                "description": "Hermes内置定时触发,持续运行模式"
            }
            APPEND skill_md_content, "## Schedule\n" + SERIALIZE_YAML(schedule_config)

            // 合规场景:Schedule触发前须人工确认
            IF compliance_result.status == "review_required":
                APPEND skill_md_content, "## 合规预检查\nschedule触发需合规引擎预检查"

        // 3c: 定义event listener(消息监听)
        IF role.requires_event_listener OR input.architecture.has_external_events:
            event_config = {
                "type": "message_listener",
                "topics": IDENTIFY_EVENT_TOPICS(input.architecture, role),
                "handler": skill_name + "_event_handler"
            }
            APPEND skill_md_content, "## Event Listener\n" + SERIALIZE_YAML(event_config)

        // 3d: spawn隔离子Agent逻辑(开源自主Agent架构)
        IF input.expert_type == "team" AND role.is_lead:
            spawn_config = {
                "isolation": "spawn",
                "child_skills": MAP(FILTER(input.roles, r => r.id != role.id), r => GENERATE_kebab_case(r.profession)),
                "communication": "inter-skill-message-passing",
                "description": "主理人通过spawn隔离子Agent,跨技能消息传递"
            }
            APPEND skill_md_content, "## Spawn Configuration\n" + SERIALIZE_YAML(spawn_config)

        // 3e: 构建完整SKILL.md
        skill_md = BUILD_SKILL_MD(skill_name, role, skill_md_content, input.architecture)
        WRITE_FILE(skills_dir + skill_name + "/SKILL.md", skill_md)

    // 阶段4: 生成context共享文件(跨技能共享运行时状态)
    IF input.expert_type == "team":
        // 多技能需要共享上下文
        context_name = GENERATE_CONTEXT_NAME(input.architecture)
        context_content = {
            "shared_state": {},
            "skill_communication_log": [],
            "last_updated": CURRENT_TIMESTAMP()
        }
        context_md = BUILD_CONTEXT_MD(context_name, context_content, skill_names)
        WRITE_FILE(context_dir + context_name + ".md", context_md)

    // 阶段5: 快速通道降级
    IF input.track == "fast":
        // 省略context共享文件,保留核心SKILL.md定义
        // 省略event listener配置,仅保留schedule
        REMOVE_FROM_OUTPUT(context_dir)

    // 阶段6: 质量门控
    CALL protocol_quality_gate(skill_names, skill_md_files)
    IF quality_gate_result.violations:
        FIX_VIOLATIONS(quality_gate_result.violations)

    output = {
        "output_format": "skills/{skill-name}/SKILL.md + context/{context-name}.md",
        "platform_specific_config": {
            "continuous_run": true,
            "builtin_schedule": true,
            "message_listener": true,
            "spawn_isolation": input.expert_type == "team"
        },
        "degradation_plan": {"fast": "省略context共享文件,保留核心SKILL.md定义"}
    }
    RETURN output
```

## 版本

1.0.0

---
*本Skill由全域专家团构建skills体系自动生成，版本1.0.0，日期2026-06-15*
