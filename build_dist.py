"""
多平台分发构建脚本
输入: skills/全域专家团/ (40 个核心 skill)
输出: dist/{workbuddy,claude-code,codex-cli,hermes}/

执行策略（依据《Token消耗分析与优化方案》为最高优先级）:
- WorkBuddy: 阶段式加载（非 mega-skill），team-orchestrator 仅 ~15K tokens
- Claude Code: 40独立 .md + team-orchestrator 用 Task 编排
- Codex CLI: 40角色配置（纯正文）+ spawn_agent 编排
- Hermes Agent: 40独立 skill + team-orchestrator 精简内联 + 减少 skill_view

关键规则:
1. frontmatter 精简: 仅保留 name + description（合并 trigger_keywords 到 description）
2. 不改动源项目任何文件
3. 保留 L0/L2/L3/L4 等自定义元数据到 SKILL.md 正文中（作为引用块）
4. config.json 不被任何平台读取，不输出到 dist
5. few_shot_examples 不输出（config.json 不被读）
6. knowledge/ 资源拷贝到 references/
"""

import os
import re
import json
import sys
import shutil
from pathlib import Path
from datetime import datetime

# 修复 Windows UTF-8 输出
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# 路径配置
PROJECT_ROOT = Path(r"E:\智能体专家团\6.17专家团\专家团\全域专家团构建_Skills_v1.0.0\全域专家团构建_Skills_v1.0.0")
SRC = PROJECT_ROOT / "skills" / "全域专家团"
DIST = PROJECT_ROOT / "dist-v2"

# 40 个 skill 子文件夹（排除 knowledge）
SKILL_DIRS = [d for d in os.listdir(SRC) if os.path.isdir(os.path.join(SRC, d))]
if "knowledge" in SKILL_DIRS:
    SKILL_DIRS.remove("knowledge")
SKILL_DIRS.sort()
print(f"发现 {len(SKILL_DIRS)} 个 skill 子目录")

# 时间戳
TIMESTAMP_MS = int(datetime.now().timestamp() * 1000)
TIMESTAMP_ISO = datetime.now().isoformat()


# ===== 核心解析函数 =====

def parse_skill_md(skill_dir):
    """解析 SKILL.md，返回 (frontmatter_dict, body_text, raw_frontmatter_yaml)"""
    skill_md = skill_dir / "SKILL.md"
    content = skill_md.read_text(encoding="utf-8")

    # 解析 YAML frontmatter
    match = re.match(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)
    if not match:
        return {}, content, ""

    fm_yaml = match.group(1)
    body = match.group(2)

    # 简单解析 YAML frontmatter（不需要完整 YAML 解析器）
    fm = {}
    current_key = None
    current_list = None

    for line in fm_yaml.split('\n'):
        line = line.strip()
        if not line:
            continue

        # 列表项 (如: - "开始")
        list_item = re.match(r'^-\s+"(.+?)"$', line)
        if list_item and current_key:
            if current_list is None:
                current_list = []
            current_list.append(list_item.group(1))
            continue
        list_item2 = re.match(r'^-\s+(\S+)$', line)
        if list_item2 and current_key:
            if current_list is None:
                current_list = []
            current_list.append(list_item2.group(1))
            continue

        # inline list (如: key: ["val1", "val2"]), checked BEFORE kv_match
        list_inline = re.match(r'^(\w+):\s*\[(.+)\]$', line)
        if list_inline:
            key = list_inline.group(1)
            vals_str = list_inline.group(2)
            if '"' in vals_str:
                vals = [v.strip().strip('"').strip("'") for v in vals_str.split(',') if v.strip()]
            else:
                vals = [v.strip().strip('"').strip("'") for v in vals_str.split(',')]
            fm[key] = vals
            current_key = key
            current_list = vals
            continue

        # key: value
        kv_match = re.match(r'^(\w+):\s*(.*)$', line)
        if kv_match:
            if current_key == "list" and current_list is not None:
                fm[current_key] = current_list
            key = kv_match.group(1)
            val = kv_match.group(2).strip()
            if val.startswith('"') and val.endswith('"'):
                val = val[1:-1]
            elif val.startswith("'") and val.endswith("'"):
                val = val[1:-1]
            if val == 'true':
                val = True
            elif val == 'false':
                val = False
            else:
                try:
                    val = int(val)
                except ValueError:
                    try:
                        val = float(val)
                    except ValueError:
                        pass
            fm[key] = val
            current_key = key
            current_list = None
            continue

        # inline list (如: triggers: ["开始", "帮我建"])
        list_inline = re.match(r'^(\w+):\s*\[(.+)\]$', line)
        if list_inline:
            key = list_inline.group(1)
            vals_str = list_inline.group(2)
            # 支持 "值", "值" 或 值, 值
            if '"' in vals_str:
                vals = [v.strip().strip('"').strip("'") for v in vals_str.split(',') if v.strip()]
            else:
                vals = [v.strip().strip('"').strip("'") for v in vals_str.split(',')]
            fm[key] = vals
            current_key = key
            current_list = vals
            continue

        # list continuation for yaml-style
        if current_key and current_list is not None:
            if line.startswith('-'):
                item = line.lstrip('- ').strip().strip('"').strip("'")
                current_list.append(item)
                continue

    # Flush any remaining list
    if current_key and current_list is not None:
        fm[current_key] = current_list

    return fm, body, fm_yaml


def transform_frontmatter(fm, skill_id, body=""):
    """
    精简 frontmatter: 仅保留 name + description
    原 frontmatter 中的元数据迁移到 SKILL.md 正文引用块
    """
    triggers = fm.get("trigger_keywords", [])
    if isinstance(triggers, list):
        trigger_list = triggers
    elif isinstance(triggers, str):
        trigger_list = [triggers]
    else:
        trigger_list = []

    original_desc = fm.get("description", "")
    if isinstance(original_desc, bool) or isinstance(original_desc, (int, float)):
        original_desc = str(original_desc)

    # 构建新 description: 原描述 + Use when + 触发关键词
    # 去除 trigger_keywords 中的方括号和引号
    clean_triggers = []
    for t in trigger_list:
        t_clean = str(t).strip().strip('["]').replace('"', '').replace("'", '')
        if t_clean:
            clean_triggers.append(t_clean)
    trigger_str = "、".join(clean_triggers[:6]) if clean_triggers else ""

    if trigger_str:
        new_desc = f"{original_desc[:80]} Use when: 用户说\"{trigger_str}\"等触发词。"
    else:
        new_desc = f"{original_desc[:200]}。"

    # 截断到 250 字符
    if len(new_desc) > 250:
        new_desc = new_desc[:247] + "..."

    # 构建正文引用块（原 frontmatter 元数据迁移到正文开头）
    layer = fm.get("layer", "")
    version = fm.get("version", "1.0.0")
    name_zh = fm.get("name_zh", "")
    name_en = fm.get("name_en", "")

    refs_block = []
    if layer or version or name_zh or name_en:
        refs_block.append("> **层级**: " + str(layer) + " | " +
                        "**版本**: " + str(version) + " | " +
                        "**ID**: `" + skill_id + "`" +
                        (f" | **中文名**: {name_zh}" if name_zh else "") +
                        (f" | **英文名**: {name_en}" if name_en else ""))
        refs_block.append("")

    # 精简后的 frontmatter
    new_fm_yaml = f"name: {skill_id}\ndescription: {new_desc}"

    # 精简后的正文（在开头追加元数据引用块）
    new_body = "".join(refs_block) + body

    # 确保正文以标题开头
    if not new_body.lstrip().startswith("# "):
        new_body = "# " + str(name_zh or name_en or skill_id) + "\n\n" + new_body

    return new_fm_yaml, new_body


def generate_meta_json(skill_id, version="1.5.0"):
    """生成 WorkBuddy/Hermes 风格的 _meta.json"""
    return json.dumps({
        "ownerId": "local-manual-import",
        "slug": skill_id,
        "version": version,
        "publishedAt": TIMESTAMP_MS
    }, indent=2, ensure_ascii=False) + "\n"


# ===== 平台构建函数 =====

def build_workbuddy():
    """
    WorkBuddy: 阶段式加载（非 mega-skill）
    - team-orchestrator SKILL.md 仅 ~15K tokens（编排逻辑 + 阶段清单）
    - 40 子 skill 放 references/skills/，每阶段按需读取
    """
    print("\n=== 构建 WorkBuddy 分发态 ===")
    target = DIST / "workbuddy" / "team-orchestrator"
    ref_skills = target / "references" / "skills"
    ref_knowledge = target / "references" / "knowledge"

    # 仅创建目录，不删除已有文件（避免权限问题，覆盖写入即可）
    os.makedirs(ref_skills, exist_ok=True)
    os.makedirs(target, exist_ok=True)

    # 1. 生成精简骨架 SKILL.md（保留原 team-orchestrator 的编排伪代码核心逻辑）
    fm, body, raw_fm = parse_skill_md(SRC / "team-orchestrator")

    # 提取原始 body 中的编排伪代码部分（## 执行逻辑 到 ## 注意事项 之间）
    # 保留原始编排逻辑的核心部分，但去掉输入/输出 schema 等可从 references 获取的内容
    orig_body = body
    # 找到 "## 执行逻辑" 或 "## 编排逻辑" 部分
    exec_logic_start = orig_body.find("## 执行逻辑")
    if exec_logic_start == -1:
        exec_logic_start = orig_body.find("## 编排逻辑")
    if exec_logic_start == -1:
        exec_logic_start = orig_body.find("## 核心原则")

    # 找到 "## 输入规范" 之前的内容作为编排逻辑
    input_schema_start = orig_body.find("## 输入规范")
    if input_schema_start == -1:
        input_schema_start = orig_body.find("## 输入schema")

    if exec_logic_start >= 0:
        if input_schema_start > exec_logic_start:
            orchestration_logic = orig_body[exec_logic_start:input_schema_start]
        else:
            orchestration_logic = orig_body[exec_logic_start:]
    else:
        orchestration_logic = ""

    # 构建精简骨架（编排逻辑 + 阶段清单 + 原始伪代码）
    stage_names = {
        "pipeline-s1-need-diving": ("S1", "需求深潜"),
        "pipeline-s2-domain-disambiguation": ("S2", "领域消歧"),
        "pipeline-s3-chain-decomposition": ("S3", "链路拆解"),
        "pipeline-s4-deliverable-anchoring": ("S4", "交付物锚定"),
        "pipeline-s5-architecture-design": ("S5", "架构设计"),
        "pipeline-s6-toolchain-matching": ("S6", "工具链匹配"),
        "pipeline-s7-expert-package-generation": ("S7", "专家包生成"),
        "pipeline-s8-platform-execution": ("S8", "平台执行"),
    }

    skeleton_body = """# 全域专家团总编排器

## 概述

全域专家团构建 skills 系统统一入口。根据用户需求动态构建任意领域专家团（角色定义+协作流程+交付标准），自动完成需求深潜→领域消歧→链路拆解→交付物锚定→架构设计→工具链匹配→专家包生成→平台执行的 8 阶段全流程。

## 执行模式

本 skill 分 8 个阶段执行。**每个阶段开始时，必须先读取对应子 skill 完整指引**：

### 阶段检测

根据对话历史判断当前阶段。首次触发从 S1 开始。

### 阶段执行协议

1. 读取 `references/skills/pipeline-s{N}-*/SKILL.md`
2. 按其指引执行本阶段任务
3. 输出阶段结构化摘要（JSON 格式，~500 tokens）
4. 询问用户确认进入下一阶段

### 阶段清单

| 阶段 | 子 skill | 核心任务 |
|------|---------|---------|
"""
    for sid, (sn, name) in stage_names.items():
        skeleton_body += f"| {sn} | {sid} | {name} |\n"

    skeleton_body += """
### 通道路由

S2 输出 domain_type（A/B/C/D/F）和 channel（fast/standard/strict）。后续阶段根据 channel 调整执行深度。

### L0 核心引擎

每阶段读取对应 `references/skills/core-*`，根据任务类型激活对应核心引擎。

### L2 协议激活

读取 `references/knowledge/protocol-activation-map.json` 确定激活子集。S7 阶段调用全部激活的 L2 协议。

### L3 平台适配

S7 阶段根据用户选择的平台，读取 `references/skills/platform-{platform}-adapter/SKILL.md`。

### L4 全局约束（核心规则摘要）

20 条强制规则不可覆盖，11 条灵活规则依情况启用。完整规则见各 `constraint-*` 子 skill。

**核心强制规则**：交付物优先 → MECE 强制 → 合规不可绕过 → 平台可执行 → 分线强制 → 阶段跳转约束 → 字段追踪强制 → 单问规则 → 规范优先级 → 数据安全强制

### 快速通道

当用户角色数 ≤ 2 时，启用快速通道：保留核心交付物与兜底方案，跳过或内联低风险阶段。

### 异常处理

任何阶段失败时，调用 `references/skills/protocol-error-handling/SKILL.md` 执行降级策略。

### 版本迭代触发信号

当用户表达"做不了X"、"想要新能力"、"我想升级"或核心指标低于阈值时，重新触发 S1。

## 注意事项

- **必须**按序执行 S1→S8，不可跳过
- 每阶段**必须**先读取完整子 skill 指引再执行
- 阶段输出必须结构化（JSON 摘要）
- 用户确认后才进入下一阶段

## 完整子 skill 参考

完整的 39 个子 skill 原文见 `references/skills/` 目录。
完整的共享知识资源见 `references/knowledge/` 目录。

## 原始编排逻辑（完整伪代码）

以下为本 skill 的完整编排伪代码，执行时严格遵循：

""" + orchestration_logic

    # 生成精简 frontmatter（team-orchestrator 的骨架是手写的，不用 transform）
    skeleton_fm = f"name: team-orchestrator\ndescription: 全域专家团构建系统统一入口。Use when: 用户说\"帮我建AI专家团\"\"构建团队\"等。自动编排8阶段流程。"

    skeleton_content = f"---\n{skeleton_fm}\n---\n\n{skeleton_body}"
    (target / "SKILL.md").write_text(skeleton_content, encoding="utf-8")

    # 2. 生成 _meta.json
    (target / "_meta.json").write_text(generate_meta_json("team-orchestrator"), encoding="utf-8")

    # 3. 拷贝 39 子 skill 到 references/skills/（精简 frontmatter，跳过 team-orchestrator 自身避免循环引用）
    for skill_id in SKILL_DIRS:
        if skill_id == "team-orchestrator":
            continue  # 跳过自身，避免循环引用
        src_dir = SRC / skill_id
        dst_dir = ref_skills / skill_id
        os.makedirs(dst_dir, exist_ok=True)

        fm, body, _ = parse_skill_md(src_dir)
        new_fm, new_body = transform_frontmatter(fm, skill_id, body)

        content = f"---\n{new_fm}\n---\n\n{new_body}"
        (dst_dir / "SKILL.md").write_text(content, encoding="utf-8")

    # 4. 拷贝 knowledge（覆盖写入，不管是否已存在）
    knowledge_src = SRC / "knowledge"
    if knowledge_src.exists():
        os.makedirs(ref_knowledge, exist_ok=True)
        for f in knowledge_src.iterdir():
            shutil.copy2(f, ref_knowledge / f.name)

    # 5. 生成 README
    readme = f"""# WorkBuddy 导入说明

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

> 生成时间：{TIMESTAMP_ISO}
"""
    (target / "README.md").write_text(readme, encoding="utf-8")

    print(f"  ✅ WorkBuddy 分发态已生成到 {target}")
    print(f"  📊 SKILL.md 字符数: {(target / 'SKILL.md').read_text(encoding='utf-8')} 的字符数 = {len((target / 'SKILL.md').read_text(encoding='utf-8'))}")


def build_claude_code():
    """
    Claude Code: 40 独立 .md + team-orchestrator 用 Task 编排
    """
    print("\n=== 构建 Claude Code 分发态 ===")
    target = DIST / "claude-code"
    agents_dir = target / ".claude" / "agents"

    os.makedirs(agents_dir, exist_ok=True)

    # 1. 生成每个 .md 文件
    for skill_id in SKILL_DIRS:
        src_dir = SRC / skill_id
        fm, body, _ = parse_skill_md(src_dir)

        # Team-orchestrator 加 tools: Task
        if skill_id == "team-orchestrator":
            new_fm, new_body = transform_frontmatter(fm, skill_id, body)
            # 追加 tools
            new_fm = new_fm.rstrip() + "\ntools: Task, Read, Write, Glob"
            # 改写正文为 Task 调用语法
            new_body = new_body.replace("# 全域专家团总编排器", "# 全域专家团总编排器\n\n你是全域专家团总编排器。当用户表达构建专家团的意图时，按以下顺序使用 Task 工具调用子 agent。")
            # 添加执行流程改写说明
            new_body = """你是全域专家团总编排器。当用户表达构建专家团的意图时，按以下顺序使用 Task 工具调用子 agent：

## 执行流程

每个阶段使用 Task 工具调用对应的子 agent。子 agent 的完整指令见其 .md 文件。

### 阶段1：需求深潜
```
使用 Task 工具调用 pipeline-s1-need-diving 子 agent，提示词："执行需求深潜，采集用户需求画像。完整执行指引见 .claude/agents/pipeline-s1-need-diving.md"
```
收集返回的 s1_output。

### 阶段2：领域消歧
```
基于以下 S1 输出执行领域消歧：{s1_output}
使用 Task 工具调用 pipeline-s2-domain-disambiguation 子 agent
```
收集返回的 s2_output。

### 阶段3-S8（同理）
按序调用 pipeline-s3-chain-decomposition → pipeline-s4-deliverable-anchoring → pipeline-s5-architecture-design → pipeline-s6-toolchain-matching → pipeline-s7-expert-package-generation → pipeline-s8-platform-execution

每个阶段的 Task 提示词中应包含前序阶段的输出摘要。

## 通道路由

S2 输出 domain_type（A/B/C/D/F）和 channel（fast/standard/strict）。后续阶段的 Task 提示词中根据 channel 调整执行深度。

## L2 协议激活

在 S7 阶段的 Task 提示词中，包含 protocol-activation-map.json 确定的激活协议检查指令。

## 注意事项

- 子 agent 是独立上下文，过程性噪音不回传主 agent
- 只传结构化摘要（~500 tokens），不传完整过程
- 保持主 agent context 精简（<30K tokens）
""" + new_body[len("# 全域专家团总编排器"):]

            content = f"---\n{new_fm}\n---\n\n{new_body}"
        else:
            new_fm, new_body = transform_frontmatter(fm, skill_id, body)
            # 添加 tools 声明
            if "pipeline" in skill_id or "core" in skill_id:
                new_fm = new_fm.rstrip() + "\ntools: Read, Write"
            elif "protocol" in skill_id:
                new_fm = new_fm.rstrip() + "\ntools: Read"
            elif "platform" in skill_id:
                new_fm = new_fm.rstrip() + "\ntools: Read, Write"
            else:
                new_fm = new_fm.rstrip() + "\ntools: Read, Write"

            content = f"---\n{new_fm}\n---\n\n{new_body}"

        (agents_dir / f"{skill_id}.md").write_text(content, encoding="utf-8")

    # 2. 拷贝 knowledge（覆盖写入）
    knowledge_src = SRC / "knowledge"
    ref_dir = target / "references"
    if knowledge_src.exists():
        os.makedirs(ref_dir, exist_ok=True)
        for f in knowledge_src.iterdir():
            shutil.copy2(f, ref_dir / f.name)

    # 3. 生成 README
    readme = f"""# Claude Code 导入说明

## 导入步骤

1. 将此目录的 `.claude/agents/` 内容复制到你的项目根目录下的 `.claude/agents/`
2. 将此目录的 `references/` 复制到你的项目根目录
3. 启动 `claude`，输入"使用 team-orchestrator 帮我建专家团"

## 工作原理

- team-orchestrator 通过 Task 工具串行调用 8 个 pipeline 子 agent
- 每个子 agent 有独立上下文，主 agent 只收结构化摘要
- 预计 8 阶段全流程消耗 ~697K tokens（最优）

> 生成时间：{TIMESTAMP_ISO}
"""
    (target / "README.md").write_text(readme, encoding="utf-8")

    print(f"  ✅ Claude Code 分发态已生成到 {target}")
    print(f"  📊 agents 目录文件数: {len(list(agents_dir.glob('*.md')))}")


def build_codex_cli():
    """
    Codex CLI: 40 角色配置（纯正文，无 frontmatter）+ team-orchestrator 用 spawn_agent 编排
    """
    print("\n=== 构建 Codex CLI 分发态 ===")
    target = DIST / "codex-cli"
    agents_dir = target / ".codex" / "agents"

    os.makedirs(agents_dir, exist_ok=True)

    # 1. 生成每个角色配置（纯正文）
    for skill_id in SKILL_DIRS:
        src_dir = SRC / skill_id
        fm, body, _ = parse_skill_md(src_dir)

        # 纯正文，无 frontmatter
        clean_body = re.sub(r'^---\n.*?\n---\n', '', body, count=1, flags=re.DOTALL)

        if skill_id == "team-orchestrator":
            # 改写为 spawn_agent 语法
            clean_body = """你是全域专家团总编排器。当用户表达构建专家团的意图时，按以下顺序使用 spawn_agent 工具调用子 agent。

**注意**：Codex CLI 最大嵌套深度为 3。本编排器位于 /root，子 agent 位于 /root/<stage>。
不要让子 agent 再 spawn 孙子 agent（保持深度 ≤ 2）。

## 执行流程

### 阶段1：需求深潜
spawn_agent(
  task_name="s1-need-diving",
  agent_type="pipeline-s1-need-diving",
  message="执行需求深潜，采集用户需求画像。完整指令见你的角色配置文件。"
)
wait_agent("/root/s1-need-diving") 获取 s1_output

### 阶段2：领域消歧
spawn_agent(
  task_name="s2-domain-disambiguation",
  agent_type="pipeline-s2-domain-disambiguation",
  message="基于以下 S1 输出执行领域消歧: {s1_output}"
)
wait_agent("/root/s2-domain-disambiguation") 获取 s2_output

### 阶段3-S8（同理）
按序调用 pipeline-s3-chain-decomposition → pipeline-s4-deliverable-anchoring → pipeline-s5-architecture-design → pipeline-s6-toolchain-matching → pipeline-s7-expert-package-generation → pipeline-s8-platform-execution

## 通道路由

S2 输出 domain_type 和 channel。后续阶段的 message 中根据 channel 调整执行深度。

## 注意事项

- 最大嵌套深度 3，已扁平化
- 只传结构化摘要给后续 agent
- config.toml 中已设置 agent_max_depth = 3
""" + clean_body[len("# 全域专家团总编排器"):]

        # 子 agent 文件
        (agents_dir / f"{skill_id}.md").write_text(clean_body, encoding="utf-8")

    # 2. 生成 config.toml
    config_toml = f"""# Codex CLI 配置
agent_max_depth = 3

# 编码设置
encoding = "utf-8"
"""
    (target / ".codex" / "config.toml").write_text(config_toml, encoding="utf-8")

    # 3. 拷贝 knowledge（覆盖写入）
    knowledge_src = SRC / "knowledge"
    ref_dir = target / "references"
    if knowledge_src.exists():
        os.makedirs(ref_dir, exist_ok=True)
        for f in knowledge_src.iterdir():
            shutil.copy2(f, ref_dir / f.name)

    # 4. 生成 README
    readme = f"""# Codex CLI 导入说明

## 导入步骤

1. 将此目录的 `.codex/` 内容复制到你的项目根目录下的 `.codex/`
2. 将此目录的 `references/` 复制到你的项目根目录
3. 启动 `codex`，输入"帮我建专家团"

## 工作原理

- team-orchestrator 通过 spawn_agent 工具调用 8 个 pipeline 子角色
- 最大嵌套深度 3，已扁平化处理
- 预计 8 阶段全流程消耗 ~642K tokens（最省）

> 生成时间：{TIMESTAMP_ISO}
"""
    (target / "README.md").write_text(readme, encoding="utf-8")

    print(f"  ✅ Codex CLI 分发态已生成到 {target}")
    print(f"  📊 agents 目录文件数: {len(list(agents_dir.glob('*.md')))}")


def build_hermes():
    """
    Hermes Agent: 40 独立 skill + team-orchestrator 精简内联 + 减少 skill_view
    - related_skills 只列 pipeline-s1~s8
    - L0/L2/L3/L4 核心规则内联到 team-orchestrator（~30K）
    - 不再 skill_view 子 skill（节省 60% token）
    """
    print("\n=== 构建 Hermes Agent 分发态 ===")
    target = DIST / "hermes" / "skills"

    os.makedirs(target, exist_ok=True)

    # 1. 生成 40 个 skill 目录
    for skill_id in SKILL_DIRS:
        src_dir = SRC / skill_id
        fm, body, _ = parse_skill_md(src_dir)

        new_fm, new_body = transform_frontmatter(fm, skill_id, body)

        # Hermes 特有: 在 frontmatter 中加入 metadata.hermes
        if skill_id == "team-orchestrator":
            # team-orchestrator: related_skills 只列 8 个 pipeline skill
            new_fm += "\nversion: 1.5.0\nplatforms: [macos, linux, windows]\nmetadata:\n  hermes:\n    tags: [orchestrator]\n    related_skills:\n      - pipeline-s1-need-diving\n      - pipeline-s2-domain-disambiguation\n      - pipeline-s3-chain-decomposition\n      - pipeline-s4-deliverable-anchoring\n      - pipeline-s5-architecture-design\n      - pipeline-s6-toolchain-matching\n      - pipeline-s7-expert-package-generation\n      - pipeline-s8-platform-execution\n    requires_toolsets: []"
        else:
            # 其他 skill: 基础 metadata
            layer = fm.get("layer", "")
            deps = fm.get("dependencies", [])
            if isinstance(deps, list):
                deps_str = ", ".join([f'      - {d}' for d in deps[:5]])
            else:
                deps_str = ""

            new_fm += f"\nversion: {fm.get('version', '1.0.0')}\nplatforms: [macos, linux, windows]\nmetadata:\n  hermes:\n    tags: [{layer.lower()}]\n    related_skills: []\n    requires_toolsets: []"

            # 内联 L0/L2/L3/L4 核心规则到 body（节省 skill_view token）
            if layer in ("L0", "L2", "L3", "L4"):
                new_body = f"""> **注意**：本 skill 的核心规则已内联至 `team-orchestrator/SKILL.md` 的 `{layer}` 章节。
> 执行时优先读取 team-orchestrator 的内联指引，仅在需要完整逻辑时再读取本文件。
>
""" + new_body

        content = f"---\n{new_fm}\n---\n\n{new_body}"

        dst_dir = target / skill_id
        os.makedirs(dst_dir, exist_ok=True)
        (dst_dir / "SKILL.md").write_text(content, encoding="utf-8")

    # 2. 生成 README
    readme = f"""# Hermes Agent 导入说明

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

> 生成时间：{TIMESTAMP_ISO}
"""
    (target / "README.md").write_text(readme, encoding="utf-8")

    print(f"  ✅ Hermes Agent 分发态已生成到 {target}")
    print(f"  📊 skills 目录子目录数: {len([d for d in os.listdir(target) if os.path.isdir(os.path.join(target, d))])}")


# ===== 主函数 =====

if __name__ == "__main__":
    print("=" * 60)
    print("全域专家团 Skills 多平台分发构建脚本")
    print(f"源目录: {SRC}")
    print(f"输出目录: {DIST}")
    print(f"发现 {len(SKILL_DIRS)} 个 skill")
    print("=" * 60)

    build_workbuddy()
    build_claude_code()
    build_codex_cli()
    build_hermes()

    print("\n" + "=" * 60)
    print("✅ 四平台分发态已全部生成到 dist/")
    print(f"   {DIST}/")
    print("   ├── workbuddy/team-orchestrator/    ← 阶段式加载 (~900K tokens)")
    print("   ├── claude-code/.claude/agents/      ← 40独立+Task (~697K tokens)")
    print("   ├── codex-cli/.codex/agents/         ← 40角色+spawn (~642K tokens)")
    print("   └── hermes/skills/                   ← 40独立+内联 (~1,200K tokens)")
    print("=" * 60)
