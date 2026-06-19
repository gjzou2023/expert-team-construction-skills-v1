{
  "_description": "平台格式模板注册表，新平台接入只需添加一个template条目",
  "workbuddy": {
    "output_format": "skill_md",
    "config_keys": ["trigger_keywords", "input_schema", "output_schema"],
    "deployment_method": "copy_to_skills_dir",
    "role_config_template": {
      "agent_format": "single_agent_prompt",
      "team_format": "team_info_with_lead_agent"
    }
  },
  "codex": {
    "output_format": "cli_config",
    "config_keys": ["command", "args", "env"],
    "deployment_method": "cli_install",
    "role_config_template": {
      "agent_format": "cli_command_chain",
      "team_format": "shell_script_orchestration"
    }
  },
  "hermes": {
    "output_format": "agent_config_json",
    "config_keys": ["webhook", "callbacks", "streaming"],
    "deployment_method": "api_import",
    "role_config_template": {
      "agent_format": "rest_api_config",
      "team_format": "multi_agent_webhook_chain"
    }
  },
  "feishu": {
    "output_format": "feishu_bot_config",
    "config_keys": ["app_id", "card_template", "approval_flow"],
    "deployment_method": "feishu_open_platform",
    "role_config_template": {
      "agent_format": "feishu_bot_config",
      "team_format": "feishu_group_bot_chain"
    }
  },
  "n8n": {
    "output_format": "workflow_json",
    "config_keys": ["nodes", "connections", "triggers"],
    "deployment_method": "n8n_import",
    "role_config_template": {
      "agent_format": "single_node_workflow",
      "team_format": "multi_node_workflow_with_branches"
    }
  },
  "comfyui": {
    "output_format": "node_graph_json",
    "config_keys": ["nodes", "links", "input_slots", "output_slots"],
    "deployment_method": "comfyui_import",
    "role_config_template": {
      "agent_format": "single_node_config",
      "team_format": "multi_node_graph"
    }
  },
  "coze": {
    "output_format": "bot_config_json",
    "config_keys": ["opening", "plugins", "workflow", "knowledge_base"],
    "deployment_method": "api_import",
    "role_config_template": {
      "agent_format": "coze_bot_config",
      "team_format": "coze_multi_bot_workflow"
    }
  },
  "dify": {
    "output_format": "dsl_json",
    "config_keys": ["workflow", "knowledge_api", "dialog_vars", "agent_strategy"],
    "deployment_method": "dify_api_import",
    "role_config_template": {
      "agent_format": "dify_agent_config",
      "team_format": "dify_multi_agent_workflow"
    }
  }
}
