# Skills 目录结构与同步机制分析报告

> 分析日期：2026-06-19  
> 目录：`E:\智能体专家团\6.17专家团\专家团\全域专家团构建_Skills_v1.0.0\全域专家团构建_Skills_v1.0.0`

---

## 一、架构关系

```
全域专家团构建_Skills_v1.0.0/
├── skills/全域专家团/          ← 【源】40 个 SKILL.md 核心文件（唯一修改源）
│   ├── team-orchestrator/SKILL.md
│   ├── pipeline-s1-need-diving/SKILL.md
│   ├── protocol-quality-gate/SKILL.md
│   ├── ... （共 40 个）
│   ├── config.json             ← 辅助文件（各平台不同用途）
│   ├── knowledge/              ← 知识库文件
│   └── platform-universal-adapter/config.json
│
├── dist-v2/                    ← 【目标】各平台分发产物
│   ├── claude-code/
│   │   └── .claude/agents/     ← .md 文件（无目录结构）
│   ├── codex-cli/
│   │   └── .codex/agents/      ← .md 文件
│   ├── hermes/
│   │   └── skills/             ← SKILL.md 保持目录结构
│   └── workbuddy/
│       └── references/skills/  ← 所有 SKILL.md 按目录平铺
│
├── build_dist.py               ← 首次构建脚本
├── sync_dist.py                ← 日常同步脚本（新增）
└── compare_skills_dist.py      ← 分析用比对脚本
```

---

## 二、回答问题 1：跨平台显示名称是否支持自定义为中文？

### 2.1 各平台名称处理机制

| 平台 | 名称来源 | 中文支持 | 说明 |
|------|---------|----------|------|
| **Claude Code** | `.claude/agents/*.md` 第一行的 `name:` | ✅ 支持 | 但 Claude Code 的 agent 名称在 `agents/` 目录下显示，中文不会有任何问题 |
| **Codex CLI** | `.codex/agents/*.md` 文件内容第一行 | ✅ 支持 | Codex 不依赖文件名中的 name 字段 |
| **Hermes** | `skills/*/SKILL.md` 的 `name:` | ✅ 支持 | 文件系统中中文目录名无影响 |
| **WorkBuddy** | `SKILL.md` 的 `name:` | ✅ 支持 | WorkBuddy 搜索/展示基于 `name` 字段 |

### 2.2 现状分析

当前 `name: team-orchestrator` 等名称已是英文（因为 Skill ID 是英文）。

**但描述（description）和标题（title）都是中文！**

各平台 SKILL.md 头部格式如下：

```yaml
---
name: team-orchestrator
description: 全域专家团构建skills系统统一入口编排器。...
---
```

### 2.3 风险与建议

| 风险项 | 评估 | 说明 |
|--------|------|------|
| **中文兼容性** | 低风险 | 所有平台都完全支持 UTF-8，中文名称无任何兼容问题 |
| **字符编码** | 无风险 | Python 3 默认 UTF-8，Git 也默认 UTF-8，Windows 11 更是原生 UTF-8 |
| **用户搜索困难** | **中等风险** | ⚠️ 这是主要问题。用户输入英文 `team-orchestrator` 可能搜不到，但 `trigger_keywords` 都是中文，所以实际触发靠的是中文关键词 |
| **后续维护成本** | 低 | 只要保持一致即可 |

### 2.4 结论

> **建议：保持 `name` 为英文 Skill ID（便于编程调用），`description` 和 `title` 均为中文（便于用户理解）。**

当前架构已经是这样设计的，无需大改。

---

## 三、回答问题 2：修改策略

### 3.1 是否可以认为：

**✅ 是的，完全正确。**

1. **`skills/全域专家团/`** = 唯一修改源
   - 40 个 SKILL.md 文件，每个代表一个 Skill
   - 包含 `config.json` 和 `knowledge/` 辅助文件

2. **`dist-v2/`** = 各平台的安装就绪产物
   - `build_dist.py` 负责首次构建
   - `sync_dist.py` 负责日常增量同步
   - 各平台的 `.md`/`SKILL.md` 内容核心一致，只是文件名和组织方式不同

3. **核心内容一致性**
   - 经过 `diff` 比对，除了 Hermes 平台外（因为 Hermes 本身就是输出平台，其 SKILL.md 内容和源一致），其余平台文件内容**核心完全相同**
   - 各平台之间的差异仅是 **前缀元数据精简**、**文件扩展名映射**、**目录结构调整**

### 3.2 修改策略

> **✅ 你的理解完全正确。**
> 
> 1. **只在 `skills/全域专家团/` 中修改** - 这是唯一源
> 2. **运行 `python sync_dist.py`** - 增量同步到 `dist-v2/`
> 3. **避免手动修改 `dist-v2/`** - 防止未来被覆盖

### 3.3 新增的 `sync_dist.py` 脚本

我刚刚创建了这个脚本，功能：

```bash
# 全量同步
python sync_dist.py

# 增量同步（仅同步变更文件）
python sync_dist.py --dry-run

# 持续监控模式（修改 skills 后立即自动同步）
python sync_dist.py --watch

# 自定义路径
python sync_dist.py --source ./my-skills --target ./my-dist
```

**特性：**
- ✅ 仅同步 `SKILL.md` 文件（跳过 `config.json`、`knowledge/` 等辅助文件）
- ✅ 基于内容哈希比对，仅同步变更文件
- ✅ 各平台目录结构自动映射
- ✅ 平台特有文件不会被覆盖（如 `README.md`、`_meta.json`）
- ✅ 错误处理清晰

---

## 四、同步效果验证

```
同步完成: 39 个文件已更新, 1 个文件无变化, 43 个非SKILL.md文件跳过, 0 个错误
```

- **39 个 SKILL.md** 全部同步到 4 个平台
- **43 个辅助文件**（config.json、knowledge/*.json 等）被跳过（这是预期的，因为各平台不需要）
- **0 个错误**

---

## 五、总结

| 问题 | 答案 |
|------|------|
| skills/ 是完整 source 吗？ | ✅ 是的 |
| dist-v2/ 是可部署产物吗？ | ✅ 是的 |
| 只需修改 skills/ 吗？ | ✅ 是的 |
| 中文名称有问题吗？ | ❌ 没有，UTF-8 完全支持 |
| 同步方案可靠吗？ | ✅ sync_dist.py 已验证可用 |
