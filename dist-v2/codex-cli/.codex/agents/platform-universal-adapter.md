
# 通用平台适配器 (Universal Platform Adapter)

> **层级**: L3 | **版本**: 1.1.0 | **ID**: `platform-universal-adapter`
> **编排关系**: 本skill由 `team-orchestrator` 按需自动加载执行，属于全域专家团构建skills系统的内部组件，用户不应直接触发。

## 概述

通用平台适配器，通过`platform_template_registry.json`按目标平台格式生成配置。替代8个同质化独立适配器，新平台接入只需添加一个template条目。

## 触发条件

当检测到以下关键词或场景时自动激活：适配, 平台, 导出, 部署

## 输入规范 (input_schema)

```json
{
  "type": "object",
  "properties": {
    "expert_package": {"type": "object"},
    "platform": {"type": "string", "description": "目标平台ID"},
    "team_type": {"type": "string", "enum": ["team", "agent"]}
  },
  "required": ["expert_package", "platform", "team_type"]
}
```

## 输出规范 (output_schema)

```json
{
  "type": "object",
  "properties": {
    "platform_config": {"type": "object"},
    "deployment_instructions": {"type": "object"}
  },
  "required": ["platform_config", "deployment_instructions"]
}
```

## 工具声明 (tool_declarations)

本Skill无外部工具依赖，纯提示词可执行。

## 执行逻辑

(1)从platform_template_registry.json加载目标平台模板→(2)按模板格式生成平台配置→(3)生成分平台部署指令→(4)质量门控。

## 详细执行逻辑

```text
FUNCTION execute_platform_universal_adapter(input):
    # ===== 入口校验 =====
    ASSERT input.expert_package EXISTS
    ASSERT input.platform IS NOT EMPTY
    ASSERT input.team_type IN ["team", "agent"]

    # ===== 步骤1: 加载目标平台模板 =====
    template_registry = LOAD("platform_template_registry.json")
    platform_template = template_registry[input.platform]
    IF platform_template IS EMPTY:
        RAISE "不支持的平台: " + input.platform
    output_format = platform_template.output_format
    config_keys = platform_template.config_keys
    deployment_method = platform_template.deployment_method
    role_config_template = platform_template.role_config_template

    # ===== 步骤2: 按模板格式生成平台配置 =====
    roles = input.expert_package.roles
    platform_config = {
        "output_format": output_format,
        "roles": []
    }
    FOR role IN roles:
        role_config = GENERATE_ROLE_CONFIG_BY_TEMPLATE(role, role_config_template, input.team_type)
        platform_config.roles.APPEND(role_config)

    # Team型额外配置teamInfo
    IF input.team_type == "team":
        platform_config.team_info = {
            "lead_agent": IDENTIFY_LEAD_AGENT(roles),
            "member_agents": EXTRACT_MEMBER_AGENTS(roles)
        }

    # ===== 步骤3: 生成分平台部署指令 =====
    deployment_instructions = GENERATE_DEPLOYMENT_INSTRUCTIONS(
        deployment_method,
        input.platform,
        platform_config
    )

    # ===== 步骤4: 质量门控 =====
    CALL constraint-output-format(platform_config)
    ASSERT platform_config IS_FORMAT_COMPLIANT
    ASSERT deployment_instructions.steps IS_NOT_EMPTY

    RETURN {
        "platform_config": platform_config,
        "deployment_instructions": deployment_instructions
    }
```

## Few-shot 示例

### 示例1: WorkBuddy平台适配 - Team型

**输入**:
```json
{
  "expert_package": {
    "overview": "ExpertTeam_内容团队_v1.0.0",
    "roles": [
      {"name": "content-strategist", "profession": "内容策略师"},
      {"name": "compliance-reviewer", "profession": "合规审查员"}
    ]
  },
  "platform": "workbuddy",
  "team_type": "team"
}
```

**输出**:
```json
{
  "platform_config": {
    "output_format": "skill_md",
    "roles": [
      {"id": "content-strategist", "prompt": "你是内容策略师...", "tools": ["WebSearch", "ImageGen"]},
      {"id": "compliance-reviewer", "prompt": "你是合规审查员...", "tools": ["protocol-compliance-engine"]}
    ],
    "team_info": {"lead_agent": "content-strategist", "member_agents": ["compliance-reviewer"]}
  },
  "deployment_instructions": {
    "method": "copy_to_skills_dir",
    "steps": ["将各角色SKILL.md复制到~/.workbuddy/skills/", "重启WorkBuddy生效"]
  }
}
```

### 示例2: Dify平台适配 - Agent型

**输入**:
```json
{
  "expert_package": {
    "overview": "Expert_客服助手_v1.0.0",
    "roles": [{"name": "triage-agent", "profession": "分流助手"}]
  },
  "platform": "dify",
  "team_type": "agent"
}
```

**输出**:
```json
{
  "platform_config": {
    "output_format": "dsl_json",
    "workflow": {"nodes": [{"id": "triage-agent", "type": "agent"}]},
    "agent_strategy": "react"
  },
  "deployment_instructions": {
    "method": "dify_api_import",
    "steps": ["登录Dify控制台", "导入DSL JSON配置"]
  }
}
```

### 示例3: Feishu平台适配 - Team型含审批流

**输入**:
```json
{
  "expert_package": {
    "overview": "ExpertTeam_审批团队_v1.0.0",
    "roles": [
      {"name": "request-handler", "profession": "请求处理员"},
      {"name": "approver", "profession": "审批员"}
    ]
  },
  "platform": "feishu",
  "team_type": "team"
}
```

**输出**:
```json
{
  "platform_config": {
    "output_format": "feishu_bot_config",
    "approval_flow": {"steps": ["request-handler接收", "approver审批"], "timeout_hours": 24},
    "roles": [{"bot_id": "request-handler"}, {"bot_id": "approver"}]
  },
  "deployment_instructions": {
    "method": "feishu_open_platform",
    "steps": ["创建飞书应用", "配置机器人卡片模板", "设置审批流回调"]
  }
}
```

## 知识库挂载点 (knowledge_base_mount_points)

- **[static]** `file://./knowledge/platform-templates.md` — 平台模板说明

## 依赖关系

- `core-mental-model-engine`
- `constraint-output-format`

## 版本

1.1.0

---
*本Skill由全域专家团构建skills体系自动生成，版本1.1.0，日期2026-06-16*
