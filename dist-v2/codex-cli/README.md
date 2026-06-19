# Codex CLI 导入说明

## 导入步骤

1. 将此目录的 `.codex/` 内容复制到你的项目根目录下的 `.codex/`
2. 将此目录的 `references/` 复制到你的项目根目录
3. 启动 `codex`，输入"帮我建专家团"

## 工作原理

- team-orchestrator 通过 spawn_agent 工具调用 8 个 pipeline 子角色
- 最大嵌套深度 3，已扁平化处理
- 预计 8 阶段全流程消耗 ~642K tokens（最省）

> 生成时间：2026-06-19T11:58:23.385700
