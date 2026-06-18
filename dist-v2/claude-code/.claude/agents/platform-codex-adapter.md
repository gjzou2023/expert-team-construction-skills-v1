---
name: platform-codex-adapter
description: 生成.codex/agents/*.toml+AGENTS.md+.codex/config.toml。description必须英文,developer_in Use when: 用户说"platform-codex-adapter、Codex适配器、L3-Codex"等触发词。
tools: Read, Write
---

# Codex CLI平台适配器

> **层级**: L3 | **版本**: 1.1.0 | **ID**: `platform-codex-adapter` | **中文名**: Codex CLI平台适配器 | **英文名**: Codex CLI Adapter
# Codex CLI平台适配器 (Codex CLI Adapter)

> **层级**: L3 | **版本**: 1.0.0 | **ID**: `platform-codex-adapter`
> **编排关系**: 本skill由 `team-orchestrator` 按需自动加载执行，属于全域专家团构建skills系统的内部组件，用户不应直接触发。

## 概述

生成.codex/agents/*.toml+AGENTS.md+.codex/config.toml。description必须英文,developer_instructions≥200字符,model禁止占位符,sandbox_mode必须明确。

## 触发条件

当检测到以下关键词或场景时自动激活：codex, codex, 平台适配, 输出格式

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
      "description": ".codex/agents/*.toml + AGENTS.md + .codex/config.toml"
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

目标平台=Codex CLI平台适配器时激活。输出格式：.codex/agents/*.toml + AGENTS.md + .codex/config.toml。平台特定规则：无内置调度能力,需外部crontab;输出shell脚本+crontab配置,用户需自行部署。快速通道TOML规则(简化版)。

## Few-shot 示例

### 示例 1: Team型Codex代理生成

**输入**:
```json
{
  "architecture": {
    "domain_type": "A",
    "platform": "codex"
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
  "output_format": ".codex/agents/*.toml + AGENTS.md + .codex/config.toml",
  "platform_specific_config": {
    "scheduling": "无内置调度,输出shell脚本+crontab配置供用户自行部署",
    "agent_configs": [
      ".codex/agents/chief-editor.toml: description='Chief editor role for editorial planning', developer_instructions≥200字符, model='claude-sonnet-4-20250514', sandbox_mode='workspace-write'",
      ".codex/agents/content-writer.toml: description='Content writer for article drafting', developer_instructions≥200字符, model='claude-sonnet-4-20250514', sandbox_mode='workspace-write'",
      ".codex/agents/visual-designer.toml: description='Visual designer for image creation', developer_instructions≥200字符, model='claude-sonnet-4-20250514', sandbox_mode='workspace-write'"
    ],
    "AGENTS.md": "团队编排规范与成员职责定义",
    "config.toml": "sandbox_mode='workspace-write', model无占位符"
  }
}
```

### 示例 2: 强监管领域合规拦截

**输入**:
```json
{
  "architecture": {
    "domain_type": "A",
    "platform": "codex",
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
  "blocked_reason": "医疗领域触发生命健康强监管规则",
  "required_call": "protocol-compliance-engine",
  "next_action": "审查通过后生成.codex/agents/medical-advisor.toml,description不含疗效承诺"
}
```

### 示例 3: 快速通道单Agent

**输入**:
```json
{
  "architecture": {
    "domain_type": "A",
    "platform": "codex",
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
  "output_format": ".codex/agents/social-assistant.toml + AGENTS.md",
  "generated_files": [
    ".codex/agents/social-assistant.toml: 简化TOML规则,sandbox_mode='workspace-write', developer_instructions≥200字符",
    "AGENTS.md: 单Agent模式,无团队编排内容"
  ],
  "degradation_plan": {
    "strategy": "跳过config.toml可选配置,保留核心代理文件"
  }
}
```

## 知识库挂载点 (knowledge_base_mount_points)

- **[static]** `file://platform/platform-codex-adapter/format-spec` — Codex CLI平台适配器格式规范

## 依赖关系

- `pipeline-s7-expert-package-generation`

## 详细执行逻辑

```text
FUNCTION execute_platform_codex_adapter(input):
    ASSERT input matches input_schema
    ASSERT input.architecture != NULL
    ASSERT input.roles != NULL AND LEN(input.roles) >= 1

    // 阶段1: 合规前置检查
    CALL protocol_compliance_engine(input.architecture.domain_type, input.track)
    IF compliance_result.status == "blocked":
        RETURN {"status": "blocked_or_review", "required_call": "protocol-compliance-engine"}

    // 阶段2: 初始化Codex配置结构
    codex_dir = ".codex/"
    agents_dir = codex_dir + "agents/"
    config_path = codex_dir + "config.toml"
    agents_md_path = "AGENTS.md"

    // 阶段3: 生成.codex/config.toml(全局配置)
    config_toml = {
        "sandbox_mode": "workspace-write",  // 必须明确,禁止占位符
        "model": SELECT_MODEL(input.track),  // 禁止占位符,必须指定具体模型
        "developer_instructions_min_length": 200
    }
    ASSERT config_toml.model != "placeholder"
    ASSERT config_toml.sandbox_mode IN ["workspace-write", "workspace-read", "full-access"]

    // 阶段4: 为每个角色生成TOML代理文件
    agent_toml_files = []
    FOR EACH role IN input.roles:
        agent_id = GENERATE_kebab_case(role.profession)
        ASSERT MATCH(agent_id, /^[a-z][a-z0-9-]*$/)

        // description必须英文
        description_en = TRANSLATE_TO_ENGLISH(role.profession + " role for " + input.architecture.domain_label)
        ASSERT MATCH(description_en, /^[A-Z]/)  // 英文首字母大写
        ASSERT NOT CONTAINS_CHINESE(description_en)

        // developer_instructions必须≥200字符
        dev_instructions = BUILD_DEVELOPER_INSTRUCTIONS(role, input.sop, input.architecture)
        ASSERT LEN(dev_instructions) >= 200

        // 构建TOML文件内容
        toml_content = BUILD_TOML({
            "id": agent_id,
            "description": description_en,
            "developer_instructions": dev_instructions,
            "model": config_toml.model,
            "sandbox_mode": config_toml.sandbox_mode
        })

        file_path = agents_dir + agent_id + ".toml"
        APPEND agent_toml_files, {"path": file_path, "content": toml_content}

    // 阶段5: 父子会话模型编排
    IF input.expert_type == "team":
        // 识别主理人作为父会话
        lead_agent = IDENTIFY_LEAD_AGENT(input.roles)
        parent_session_config = {
            "parent_agent": lead_agent.id,
            "child_agents": MAP(FILTER(input.roles, r => r.id != lead_agent.id), r => r.id),
            "communication_model": "parent-child",
            "description": "主理人作为父会话,成员Agent作为子会话,纯CLI交互"
        }
        // 在AGENTS.md中定义父子会话编排规范
        agents_md = BUILD_AGENTS_MD_TEAM(parent_session_config, input.roles)
    ELIF input.expert_type == "agent":
        // 单Agent模式,无团队编排
        agents_md = BUILD_AGENTS_MD_SINGLE(input.roles[0])
        // 快速通道:跳过config.toml可选配置
        IF input.track == "fast":
            REMOVE config_toml_from_output()

    // 阶段6: 外部调度配置
    IF input.sop.has_schedule_trigger:
        // Codex无内置调度,输出shell脚本+crontab配置
        cron_schedule = EXTRACT_CRON(input.sop.schedule)
        shell_script = BUILD_CRON_SCRIPT(cron_schedule, agent_toml_files[0].path)
        APPEND output_files, {"path": "scripts/schedule.sh", "content": shell_script}
        APPEND output_files, {"path": "scripts/crontab.conf", "content": cron_schedule + " " + shell_script_path}

    // 阶段7: 降级策略
    degradation_plan = {
        "fast": "跳过config.toml可选配置,保留核心代理文件",
        "no_cron": "省略shell脚本,用户须手动触发"
    }

    // 阶段8: 质量门控
    CALL protocol_quality_gate(agent_toml_files, config_toml, agents_md)
    IF quality_gate_result.violations:
        FIX_VIOLATIONS(quality_gate_result.violations)

    output = {
        "output_format": ".codex/agents/*.toml + AGENTS.md + .codex/config.toml",
        "platform_specific_config": {
            "scheduling": "无内置调度,输出shell脚本+crontab配置供用户自行部署",
            "agent_configs": agent_toml_files,
            "AGENTS.md": agents_md,
            "config.toml": config_toml
        },
        "degradation_plan": degradation_plan
    }
    RETURN output
```

## 版本

1.0.0

---
*本Skill由全域专家团构建skills体系自动生成，版本1.0.0，日期2026-06-15*
