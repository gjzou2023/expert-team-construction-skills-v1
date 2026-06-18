# WorkBuddy 导入说明

## 导入步骤

1. 将 `team-orchestrator/` 整个文件夹复制到 `~/.workbuddy/skills/`
2. 重启 WorkBuddy
3. 对话中输入"帮我建个 AI 专家团"测试

## 导入后结构

```
~/.workbuddy/skills/team-orchestrator/
├── SKILL.md          ← 精简编排骨架 (~15K tokens)
├── _meta.json
└── references/
    ├── skills/       ← 40 子 skill 作为按需参考资源
    │   ├── pipeline-s1-need-diving/SKILL.md
    │   ├── ...（40个）
    │   └── platform-workbuddy-adapter/SKILL.md
    └── knowledge/    ← 共享知识资源
        ├── protocol-activation-map.json
        └── stage-routing.json
```

## 工作原理

1. 用户触发 `team-orchestrator` 后，按 S1→S8 顺序执行
2. 每阶段读取 `references/skills/pipeline-sN-*/SKILL.md` 的完整指引
3. 完成后输出结构化摘要，询问用户确认后进入下一阶段
4. 各 L0/L2/L3/L4 子 skill 按需读取

**Token 优化**：团队-orchestrator 骨架仅 ~15K tokens（vs 原 mega-skill 180K），单轮 context 控制在 ~25K tokens。

> 生成时间：2026-06-18T00:02:24.068487
