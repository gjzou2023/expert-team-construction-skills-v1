{
  "id": "platform-universal-adapter",
  "layer": "L3",
  "name_zh": "通用平台适配器",
  "name_en": "Universal Platform Adapter",
  "version": "1.1.0",
  "description": "通用平台适配器，通过platform_template_registry.json按目标平台格式生成配置。新平台接入只需添加一个template条目。",
  "trigger_keywords": ["适配", "平台", "导出", "部署"],
  "input_schema": {
    "type": "object",
    "properties": {
      "expert_package": {"type": "object"},
      "platform": {"type": "string", "description": "目标平台ID"},
      "team_type": {"type": "string", "enum": ["team", "agent"]}
    },
    "required": ["expert_package", "platform", "team_type"]
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "platform_config": {"type": "object"},
      "deployment_instructions": {"type": "object"}
    },
    "required": ["platform_config", "deployment_instructions"]
  },
  "tool_declarations": [],
  "few_shot_examples": [
    {
      "name": "WorkBuddy平台适配 - Team型",
      "input": {
        "expert_package": {
          "overview": "ExpertTeam_内容团队_v1.0.0",
          "roles": [
            {"name": "content-strategist", "profession": "内容策略师"},
            {"name": "compliance-reviewer", "profession": "合规审查员"}
          ]
        },
        "platform": "workbuddy",
        "team_type": "team"
      },
      "output": {
        "platform_config": {
          "output_format": "skill_md",
          "roles": [
            {"id": "content-strategist", "prompt": "你是内容策略师...", "tools": ["WebSearch", "ImageGen"]},
            {"id": "compliance-reviewer", "prompt": "你是合规审查员...", "tools": ["protocol-compliance-engine"]}
          ],
          "team_info": {
            "lead_agent": "content-strategist",
            "member_agents": ["compliance-reviewer"]
          }
        },
        "deployment_instructions": {
          "method": "copy_to_skills_dir",
          "steps": ["将各角色SKILL.md复制到~/.workbuddy/skills/", "重启WorkBuddy生效"],
          "verification": "在WorkBuddy中可见两个角色并可spawn"
        }
      }
    },
    {
      "name": "Dify平台适配 - Agent型",
      "input": {
        "expert_package": {
          "overview": "Expert_客服助手_v1.0.0",
          "roles": [{"name": "triage-agent", "profession": "分流助手"}]
        },
        "platform": "dify",
        "team_type": "agent"
      },
      "output": {
        "platform_config": {
          "output_format": "dsl_json",
          "workflow": {
            "nodes": [{"id": "triage-agent", "type": "agent", "prompt": "你是客服分流助手..."}],
            "connections": [],
            "knowledge_api": {"enabled": true, "type": "faq"}
          },
          "agent_strategy": "react"
        },
        "deployment_instructions": {
          "method": "dify_api_import",
          "steps": ["登录Dify控制台", "导入DSL JSON配置", "配置知识库API密钥"],
          "verification": "在Dify中测试对话流程"
        }
      }
    },
    {
      "name": "Feishu平台适配 - Team型含审批流",
      "input": {
        "expert_package": {
          "overview": "ExpertTeam_审批团队_v1.0.0",
          "roles": [
            {"name": "request-handler", "profession": "请求处理员"},
            {"name": "approver", "profession": "审批员"}
          ]
        },
        "platform": "feishu",
        "team_type": "team"
      },
      "output": {
        "platform_config": {
          "output_format": "feishu_bot_config",
          "app_id": "cli_${random}",
          "card_template": "approval_flow_card",
          "approval_flow": {
            "steps": ["request-handler接收", "approver审批", "返回结果"],
            "timeout_hours": 24
          },
          "roles": [
            {"bot_id": "request-handler", "webhook": "${webhook_url}"},
            {"bot_id": "approver", "webhook": "${webhook_url}"}
          ]
        },
        "deployment_instructions": {
          "method": "feishu_open_platform",
          "steps": ["创建飞书应用", "配置机器人卡片模板", "设置审批流回调", "部署到飞书群"],
          "verification": "在飞书群中@机器人测试审批流程"
        }
      }
    }
  ],
  "knowledge_base_mount_points": [
    {"type": "static", "path": "file://./knowledge/platform-templates.md", "description": "平台模板说明"},
    {"type": "static", "path": "file://./platform_template_registry.json", "description": "平台格式模板注册表"},
    {"type": "dynamic", "path": "file://./knowledge/platform-adapter-state.json", "description": "平台适配运行时状态"}
  ],
  "dependencies": ["core-mental-model-engine", "constraint-output-format"],
  "execution_logic": "(1)从platform_template_registry.json加载目标平台模板→(2)按模板格式生成平台配置→(3)生成分平台部署指令→(4)质量门控。",
  "cascading_calls": ["core-mental-model-engine", "constraint-output-format"],
  "context_inheritance": ["expert_package"],
  "shared_memory_keys": ["platform-adapter_config"],
  "protocol": {
    "cascading_enabled": true,
    "context_inheritance_enabled": true,
    "shared_memory_enabled": true,
    "cascade_direction": "同层或下层可调用",
    "data_passing_format": "JSON-compatible",
    "immutability_rule": "上游产出一经确认，下游不得擅自修改，需通过回退协议",
    "traceability": "每个字段标注来源阶段和Skill",
    "mandatory_calls": [
      {
        "callee": "constraint-output-format",
        "when": "配置生成后",
        "reason": "校验平台配置格式合规性"
      }
    ]
  },
  "compatibility": {"min_compatible": "1.1.0", "breaking_change": "2.0.0"},
  "priority": 3,
  "stage_guard": null
}
