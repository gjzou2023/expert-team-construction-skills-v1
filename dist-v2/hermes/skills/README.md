# Hermes Agent 导入说明

## 导入步骤

1. 将此目录的 `skills/` 下所有子目录复制到 `~/.hermes/skills/`
2. 重启 Hermes Agent
3. 对话中输入"帮我建个 AI 专家团"

## 工作原理

- team-orchestrator 通过 related_skills 引导 LLM 加载子 skill
- **不再使用 skill_view 加载子 skill**（减少 context 累积）
- L0/L2/L3/L4 核心规则已内联到 team-orchestrator
- 预计 8 阶段全流程消耗 ~1,200K tokens（优化后）

## Token 优化说明

- related_skills 只列 8 个 pipeline skill（不列 L0/L2/L3/L4）
- 避免 skill_view 导致 context 无限累积
- L0/L2/L3/L4 核心规则内联节省 ~60% token

> 生成时间：2026-06-19T11:58:23.385700
