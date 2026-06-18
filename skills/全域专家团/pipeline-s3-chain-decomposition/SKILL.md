---
name: pipeline-s3-chain-decomposition
id: "pipeline-s3-chain-decomposition"
layer: "L1"
name_zh: "阶段三：链路拆解"
name_en: "Stage 3: Chain Decomposition"
version: "1.1.0"
description: 从终端交付物倒推全链路，识别链路节点(节点ID→上下游依赖→断点标注)。S3负责'链路骨架'，不独立定义交付物内容；交付物填充由S4完成。快速通道下S3简化为3节点单链路直通(非跳过)，标准/strict通道下S3生成完整骨架节点，S4填充具体交付物。
agent_created: true
trigger_keywords: ["S3执行", "链路拆解", "链路骨架", "工作流拆解", "全链路倒推"]
dependencies: ["core-mental-model-engine", "core-deliverable-backward-engine"]
---

# 阶段三：链路拆解 (Stage 3: Chain Decomposition)

> **层级**: L1 | **版本**: 1.1.0 | **ID**: `pipeline-s3-chain-decomposition`
> **编排关系**: 本skill由 `team-orchestrator` 自动加载执行，用户不应直接触发。承接 `pipeline-s2-domain-disambiguation` 的输出，完成后自动衔接 `pipeline-s4-deliverable-anchoring`。快速通道下简化为单链路直通。

## 概述

从终端交付物倒推全链路，识别链路节点(输入→处理→输出→反馈)，标注断点与依赖。快速通道跳过，合并入S4。

## 触发条件

当检测到以下关键词或场景时自动激活：链路, 流程, 拆解, 工作流, 全链路

## 输入规范 (input_schema)

```json
{
  "type": "object",
  "properties": {
    "s2_outputs": {
      "type": "object",
      "description": "S2领域确认输出"
    },
    "deliverable_candidates": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "候选交付物，由编排器从S1需求画像和S2领域画像推导"
    },
    "channel": {
      "type": "string",
      "enum": ["fast", "standard", "strict"],
      "description": "执行通道，由编排器传递"
    },
    "s1_context": {
      "type": "object",
      "description": "S1需求画像的上下文信息（由编排器从S1输出中提取传递）",
      "properties": {
        "team_size": {"type": "integer"},
        "ai_experience": {"type": "string"},
        "target_platform": {"type": "string"}
      }
    }
  },
  "required": [
    "s2_outputs",
    "deliverable_candidates"
  ]
}
```

## 输出规范 (output_schema)

```json
{
  "type": "object",
  "properties": {
    "chain_nodes": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": {
            "type": "string"
          },
          "name": {
            "type": "string"
          },
          "type": {
            "type": "string",
            "enum": [
              "input",
              "process",
              "output",
              "feedback"
            ]
          },
          "upstream": {
            "type": "array",
            "items": {
              "type": "string"
            }
          },
          "downstream": {
            "type": "array",
            "items": {
              "type": "string"
            }
          }
        }
      }
    },
    "chain_mermaid": {
      "type": "string"
    },
    "breakpoints": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "dependencies": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  },
  "required": [
    "chain_nodes",
    "chain_mermaid",
    "breakpoints",
    "dependencies"
  ]
}
```

## 工具声明 (tool_declarations)

本Skill无外部工具依赖，纯提示词可执行。

## 执行逻辑

(1)从终端交付物倒推全链路(调用core-deliverable-backward-engine)→(2)识别链路节点(输入→处理→输出→反馈)→(3)标注断点与依赖→(4)输出链路图(Mermaid)。默认链路按领域类型：A型7步/B型6步/C型6步/D型6步/F型6步。快速通道：取3-5步精简工作流概要。

## Few-shot 示例

### 示例1: 正常流程 - A型内容链路拆解

**输入**:
```json
{
  "s2_outputs": {
    "confirmed_domain": "A",
    "domain_name": "内容传播型"
  },
  "deliverable_candidates": [
    "小红书图文笔记",
    "公众号深度文章",
    "用户互动话术"
  ]
}
```

**输出**:
```json
{
  "chain_nodes": [
    {"id": "N1", "name": "选题决策", "type": "input", "upstream": [], "downstream": ["N2"]},
    {"id": "N2", "name": "素材采集", "type": "process", "upstream": ["N1"], "downstream": ["N3"]},
    {"id": "N3", "name": "内容创作", "type": "process", "upstream": ["N2"], "downstream": ["N4"]},
    {"id": "N4", "name": "平台适配", "type": "process", "upstream": ["N3"], "downstream": ["N5"]},
    {"id": "N5", "name": "发布分发", "type": "output", "upstream": ["N4"], "downstream": ["N6"]},
    {"id": "N6", "name": "数据追踪", "type": "feedback", "upstream": ["N5"], "downstream": ["N1"]}
  ],
  "chain_mermaid": "graph LR\n  N1[选题决策] --> N2[素材采集]\n  N2 --> N3[内容创作]\n  N3 --> N4[平台适配]\n  N4 --> N5[发布分发]\n  N5 --> N6[数据追踪]\n  N6 -.->|反馈| N1",
  "breakpoints": [],
  "dependencies": ["WebSearch", "ImageGen"]
}
```

### 示例2: 异常流程 - E型混合链路拆解(含断点)

**输入**:
```json
{
  "s2_outputs": {
    "confirmed_domain": "E",
    "domain_name": "混合型(A+F)",
    "sub_domains": ["A", "F"]
  },
  "deliverable_candidates": [
    "医疗科普文章",
    "在线问诊对话",
    "患者随访记录"
  ]
}
```

**输出**:
```json
{
  "chain_nodes": [
    {"id": "N1", "name": "选题决策", "type": "input", "upstream": [], "downstream": ["N2"]},
    {"id": "N2", "name": "内容创作与合规审查", "type": "process", "upstream": ["N1"], "downstream": ["N3","N4"]},
    {"id": "N3", "name": "科普文章发布", "type": "output", "upstream": ["N2"], "downstream": ["N6"]},
    {"id": "N4", "name": "在线问诊", "type": "process", "upstream": ["N2"], "downstream": ["N5"]},
    {"id": "N5", "name": "问诊对话记录", "type": "output", "upstream": ["N4"], "downstream": ["N6"]},
    {"id": "N6", "name": "效果反馈", "type": "feedback", "upstream": ["N3","N5"], "downstream": []
    }
  ],
  "chain_mermaid": "graph LR\n  N1 --> N2\n  N2 --> N3\n  N2 --> N4\n  N4 --> N5\n  N3 --> N6\n  N5 --> N6",
  "breakpoints": ["N2→N4: 合规审查未自动化，依赖人工审核"],
  "dependencies": ["WebSearch", "protocol-compliance-engine", "protocol-human-approval"]
}
```

### 示例3: 快速通道 - 精简链路(内联S3+S4)

**输入**:
```json
{
  "s2_outputs": {
    "confirmed_domain": "A",
    "channel": "fast"
  },
  "deliverable_candidates": [
    "小红书图文笔记"
  ]
}
```

**输出**:
```json
{
  "chain_nodes": [
    {"id": "N1", "name": "选题+素材(合并)", "type": "input", "upstream": [], "downstream": ["N2"]},
    {"id": "N2", "name": "创作+适配(合并)", "type": "process", "upstream": ["N1"], "downstream": ["N3"]},
    {"id": "N3", "name": "发布", "type": "output", "upstream": ["N2"], "downstream": []}
  ],
  "chain_mermaid": "graph LR\n  N1 --> N2 --> N3",
  "breakpoints": [],
  "dependencies": ["纯提示词"]
}
```

## 知识库挂载点 (knowledge_base_mount_points)

- **[static]** `file://pipeline/stage-3-rules` — 阶段3执行规则
- **[dynamic]** `file://pipeline/stage-3-state` — 阶段3运行时状态

## 依赖关系

- `core-mental-model-engine`
- `core-deliverable-backward-engine`

## 详细执行逻辑

```text
FUNCTION execute_pipeline_s3_chain_decomposition(input):
    # ===== 阶段三：链路拆解 - 入口校验 =====
    ASSERT input.s2_outputs EXISTS
    ASSERT input.deliverable_candidates EXISTS
    LOAD context_inheritance FROM s2

    s2_data = input.s2_outputs
    # 使用domain_profile.primary_domain替代confirmed_domain（E型已改为组合标记）
    domain_type = s2_data.domain_profile.primary_domain IF EXISTS ELSE s2_data.confirmed_domain
    # channel从input获取（由编排器传递），不从s2_data读取
    channel = input.channel IF EXISTS ELSE "standard"
    deliverable_candidates = input.deliverable_candidates

    # 从s1_context获取team_size和ai_experience（S2不含这些字段，它们在S1的need_portrait._context中）
    s1_ctx = input.s1_context IF EXISTS ELSE {}
    team_size = s1_ctx.team_size IF EXISTS ELSE 3
    ai_experience = s1_ctx.ai_experience IF EXISTS ELSE "intermediate"

    # ===== 步骤1: 通道分流判断 =====
    IF channel == "fast":
        # 快速通道：取3-5步默认链路精简版，合并入S4
        CALL execute_fast_track_chain(domain_type, deliverable_candidates)
        GOTO FAST_TRACK_OUTPUT

    # ===== 步骤2: 加载默认链路模板(按领域类型) =====
    DEFAULT_CHAINS = {
        "A": ["选题决策", "素材采集", "内容创作", "平台适配", "发布分发", "数据追踪", "迭代优化"],  # 7步
        "B": ["需求分析", "方案设计", "开发实施", "质量验证", "交付确认", "复盘归档"],              # 6步
        "C": ["受众分析", "触点设计", "引流执行", "转化跟进", "数据复盘", "策略迭代"],              # 6步
        "D": ["数据采集", "指标定义", "分析建模", "洞察生成", "报告输出", "决策支持"],              # 6步
        "F": ["工单接收", "一级分流", "问题处理", "回复生成", "满意度追踪", "知识沉淀"]             # 6步
    }
    # 使用domain_profile判断混合型（E型已改为A-F的组合标记）
    IF s2_data.domain_profile EXISTS AND LENGTH(s2_data.domain_profile.secondary_domains) > 0:
        # 混合型：合并所有子类型链路，去重并标注分叉
        all_types = [s2_data.domain_profile.primary_domain] + s2_data.domain_profile.secondary_domains
        base_chain = []
        FOR t IN all_types:
            base_chain = MERGE_CHAINS(base_chain, DEFAULT_CHAINS[t])
    ELSE:
        base_chain = DEFAULT_CHAINS[domain_type]

    # ===== 步骤3: 终点倒推法 - 从交付物倒推链路 =====
    CALL core-deliverable-backward-engine
    backward_chain = CALL backward_engine_from_deliverables(deliverable_candidates)
    # 合并默认链路与倒推链路
    merged_chain = MERGE_AND_DEDUPLICATE(base_chain, backward_chain)

    # ===== 步骤4: 构建链路节点矩阵 =====
    chain_nodes = []
    FOR i FROM 0 TO LENGTH(merged_chain) - 1:
        node = {}
        node.id = "N" + (i + 1)
        node.name = merged_chain[i]

        # 节点类型判定(input/process/output/feedback)
        IF i == 0:
            node.type = "input"
        ELIF i == LENGTH(merged_chain) - 2:
            node.type = "output"
        ELIF i == LENGTH(merged_chain) - 1:
            node.type = "feedback"
        ELSE:
            node.type = "process"

        # 上下游关系
        IF i > 0:
            node.upstream = ["N" + i]
        ELSE:
            node.upstream = []
        IF i < LENGTH(merged_chain) - 1:
            node.downstream = ["N" + (i + 2)]
        ELSE:
            node.downstream = []

        APPEND node TO chain_nodes

    # ===== 步骤5: 能力盘点6维度×步骤矩阵 =====
    CAPABILITY_DIMENSIONS = ["内容能力", "技术能力", "数据能力", "运营能力", "合规能力", "交互能力"]
    capability_matrix = {}
    FOR node IN chain_nodes:
        node_capabilities = {}
        FOR dim IN CAPABILITY_DIMENSIONS:
            required_level = EVALUATE_capability_requirement(node, dim, domain_type)
            node_capabilities[dim] = required_level
        capability_matrix[node.id] = node_capabilities

    # ===== 步骤6: 瓶颈识别 =====
    breakpoints = []
    FOR node IN chain_nodes:
        # 检查能力缺口
        FOR dim IN CAPABILITY_DIMENSIONS:
            IF capability_matrix[node.id][dim] == "required" AND NOT HAS_TOOL_FOR(node, dim):
                APPEND node.id + ": " + dim + "能力缺失，依赖人工/外部工具" TO breakpoints
        # 检查跨节点依赖
        IF node.type == "process" AND LENGTH(node.downstream) > 1:
            APPEND node.id + "→" + JOIN(node.downstream, "/") + ": 存在分叉，需分线处理" TO breakpoints
        # 检查合规瓶颈
        IF node.name CONTAINS "合规" OR node.name CONTAINS "审查":
            IF domain_type IN ["B", "F"] OR (s2_data.domain_profile EXISTS AND LENGTH(s2_data.domain_profile.secondary_domains) > 0):
                APPEND node.id + ": 合规审查未自动化，依赖人工审核" TO breakpoints

    # ===== 步骤7: 外部+内部信号采集 =====
    external_signals = []
    internal_signals = []

    # 外部信号：市场趋势、竞品动态
    IF domain_type == "A":
        APPEND "内容平台算法变更" TO external_signals
        APPEND "竞品内容策略" TO external_signals
    ELIF domain_type == "C":
        APPEND "获客成本变化" TO external_signals
        APPEND "渠道政策调整" TO external_signals
    ELIF domain_type == "F":
        APPEND "客户期望响应时间" TO external_signals
    ELIF domain_type == "D":
        APPEND "数据源可用性" TO external_signals

    # 内部信号：团队能力、资源约束（使用从s1_context获取的值，而非s2_data）
    IF team_size == 1:
        APPEND "单人资源瓶颈" TO internal_signals
    IF ai_experience == "novice":
        APPEND "AI经验不足，工具链需简化" TO internal_signals
    IF LENGTH(deliverable_candidates) > 3:
        APPEND "交付物过多，需优先级排序" TO internal_signals

    # ===== 步骤8: 生成Mermaid链路图 =====
    mermaid_lines = ["graph LR"]
    FOR node IN chain_nodes:
        FOR downstream_id IN node.downstream:
            APPEND "  " + node.id + "[" + node.name + "] --> " + downstream_id TO mermaid_lines
    # 反馈回路用虚线
    IF chain_nodes[LAST].type == "feedback":
        APPEND "  " + chain_nodes[LAST].id + " -.->|反馈| " + chain_nodes[0].id TO mermaid_lines
    chain_mermaid = JOIN(mermaid_lines, "\n")

    # ===== 步骤9: 依赖关系标注 =====
    dependencies = []
    FOR node IN chain_nodes:
        IF node.name CONTAINS "搜索" OR node.name CONTAINS "采集":
            APPEND "WebSearch" TO dependencies
        IF node.name CONTAINS "图" OR node.name CONTAINS "视觉":
            APPEND "ImageGen" TO dependencies
        IF node.name CONTAINS "合规" OR node.name CONTAINS "审查":
            APPEND "protocol-compliance-engine" TO dependencies
        IF node.name CONTAINS "审批" OR node.name CONTAINS "确认":
            APPEND "protocol-human-approval" TO dependencies
    dependencies = UNIQUE(dependencies)

    # ===== 质量门控 =====
    CALL protocol-quality-gate(stage=3, output={
        "chain_nodes": chain_nodes,
        "breakpoints": breakpoints
    })
    ASSERT LENGTH(chain_nodes) >= 3
    ASSERT chain_mermaid IS NOT EMPTY

    RETURN {
        "chain_nodes": chain_nodes,
        "chain_mermaid": chain_mermaid,
        "breakpoints": breakpoints,
        "dependencies": dependencies
    }

    # ===== 快速通道分支 =====
    FAST_TRACK_OUTPUT:
    simplified_chain = TAKE_FIRST(DEFAULT_CHAINS[domain_type], 3) + [deliverable_candidates[0]]
    # 合并相邻步骤: 选题+素材合并, 创作+适配合并, 发布单独
    simplified_nodes = [
        {"id": "N1", "name": simplified_chain[0] + "+" + simplified_chain[1] + "(合并)", "type": "input", "upstream": [], "downstream": ["N2"]},
        {"id": "N2", "name": simplified_chain[2] + "+" + simplified_chain[3] + "(合并)", "type": "process", "upstream": ["N1"], "downstream": ["N3"]},
        {"id": "N3", "name": "发布", "type": "output", "upstream": ["N2"], "downstream": []}
    ]
    simplified_mermaid = "graph LR\n  N1 --> N2 --> N3"
    RETURN {
        "chain_nodes": simplified_nodes,
        "chain_mermaid": simplified_mermaid,
        "breakpoints": [],
        "dependencies": ["纯提示词"]
    }
```

## 下一阶段路由

> 本阶段完成后，由 `team-orchestrator` 自动衔接至 `pipeline-s4-deliverable-anchoring`（阶段四：交付物锚定）。
> 衔接条件：链路骨架节点已生成 + 断点已标注。
> 快速通道下S3→S4跳过确认节点，直接衔接。用户无需手动触发下一阶段。

## 版本

1.0.0

---
*本Skill由全域专家团构建skills体系自动生成，版本1.0.0，日期2026-06-15*
