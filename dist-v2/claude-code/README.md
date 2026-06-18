# Claude Code 导入说明

## 导入步骤

1. 将此目录的 `.claude/agents/` 内容复制到你的项目根目录下的 `.claude/agents/`
2. 将此目录的 `references/` 复制到你的项目根目录
3. 启动 `claude`，输入"使用 team-orchestrator 帮我建专家团"

## 工作原理

- team-orchestrator 通过 Task 工具串行调用 8 个 pipeline 子 agent
- 每个子 agent 有独立上下文，主 agent 只收结构化摘要
- 预计 8 阶段全流程消耗 ~697K tokens（最优）

> 生成时间：2026-06-18T00:02:24.068487
