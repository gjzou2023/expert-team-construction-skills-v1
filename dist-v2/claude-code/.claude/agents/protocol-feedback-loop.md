---
name: protocol-feedback-loop
id: "protocol-feedback-loop"
layer: "L2"
name_zh: "反馈闭环协议"
name_en: "Feedback Loop Protocol"
version: "1.3.0"
description: 按领域类型确定必建反馈回路类型，为每条回路定义信号源/处理动作/频率/冷启动策略。v1.3.0新增多轮深化引导与反馈收集闭环。与5.9调度监控指标关联。
agent_created: true
trigger_keywords: ["protocol-feedback-loop", "反馈回路协议", "L2反馈"]
dependencies: ["core-mental-model-engine"]
---

# 反馈闭环协议 (Feedback Loop Protocol)

> **层级**: L2 | **版本**: 1.3.0 | **ID**: `protocol-feedback-loop`
> **编排关系**: 本skill由 `team-orchestrator` 按需自动加载执行，属于全域专家团构建skills系统的内部组件，用户不应直接触发。

## 概述

按领域类型确定必建反馈回路类型，为每条回路定义信号源/处理动作/频率/冷启动策略。v1.3.0新增多轮深化引导与反馈收集闭环。与5.9调度监控指标关联。

## 触发条件

当检测到以下关键词或场景时自动激活：反馈, 闭环, 冷启动, 监控, 信号

## 输入规范 (input_schema)

```json
{
  "type": "object",
  "properties": {
    "domain_type": {
      "type": "string",
      "enum": [
        "A",
        "B",
        "C",
        "D",
        "E",
        "F"
      ]
    },
    "automation_enabled": {
      "type": "boolean"
    }
  },
  "required": [
    "domain_type"
  ]
}
```

## 输出规范 (output_schema)

```json
{
  "type": "object",
  "properties": {
    "loops": {
      "type": "array",
      "items": {
        "type": "object"
      }
    },
    "monitoring_metrics": {
      "type": "array",
      "items": {
        "type": "object"
      }
    }
  },
  "required": [
    "loops",
    "monitoring_metrics"
  ]
}
```

## 工具声明 (tool_declarations)

本Skill无外部工具依赖，纯提示词可执行。

## 执行逻辑

(1)按领域类型确定必建反馈回路类型→(2)为每条回路定义:信号源(外部+内部)、处理动作、频率→(3)定义冷启动策略(默认值+退出条件)→(4)定义信号质量筛选规则→(5)与5.9调度监控指标关联。按领域必建回路：A型:内容效果反馈;B型:客户满意度+转化率;C型:知识使用率;D型:执行成功率;F型:客户满意度+响应时间;E型:按包含子类型激活。调度监控指标(5.9.6)：执行成功率(≥90%健康,<70%告警);平均执行时长;调度偏移量(≤30秒);连续失败计数(≥3暂停);依赖阻塞率(≤5%)。

## 多轮深化引导机制（v1.3.0新增）

### 首轮输出末尾增加深化引导

首轮输出完成后，在末尾附深化引导：

```
以上为整体框架级建议。如需深入，可选择以下方向继续：

A. 深入[技术架构]细节
B. 深入[商业模式/投融资]细节
C. 深入[合规/法律]细节
D. 针对[具体环节]制定详细执行计划
E. 对方案进行压力测试/风险推演
```

### 后续轮次自动继承上下文

- 保持专家团角色一致性（同一批专家角色在后续轮次中保持）
- 在新一轮深入时，调整对应专家发言权重（当前深入方向的专家权重提升）
- 允许用户动态增减专家角色（"去掉XX专家，增加YY专家"）

### 深化轮次管理

- 每轮输出标注为"第N轮"以保持上下文追溯
- 在状态管理引擎中维护对话轮次计数器
- 当同一话题轮次≥3时，自动提示用户是否考虑进入深度模式

### 与反馈闭环的关系

多轮深化引导利用反馈闭环协议中的用户反馈信号，识别用户对哪些方向关注度最高（通过用户的深化选择），形成正向反馈循环。

## 反馈收集闭环（v1.3.0新增）

### 输出结束后反馈收集

在每次专家团建议输出完成后，追加以下反馈收集：

```
本次专家团建议是否对您有帮助？

- 哪些专家的建议最有价值？
- 是否有您期望但未被覆盖的视角？
- 建议的深度是否满足您的需要？

您的反馈将帮助我在后续对话中更好地服务您。
```

### 反馈信号采集规则

| 反馈信号 | 采集方式 | 后续动作 |
|---------|---------|---------|
| 用户指定某专家"最有价值" | 自然语言解析 | 后续同类需求中提升该专家权重 |
| 用户指出"缺少XX视角" | 自然语言解析 | 下次同类需求自动增加对应角色 |
| 用户要求"更深入" | 自然语言解析 | 触发多轮深化引导 |
| 用户表示"太复杂" | 自然语言解析 | 降档至更简化的输出模式 |
| 无反馈 | 默认无变化 | 维持当前配置 |

### 反馈历史存储

- 反馈信号存入 `protocol-knowledge-persistence` 协议的知识资产中
- 同一领域的多次反馈形成领域偏好画像
- 在用户下次发起同类需求时，S1需求深潜阶段自动加载偏好画像

## 调度监控指标

| 指标 | 健康线 | 告警线 | 处理动作 |
| --- | --- | --- | --- |
| 执行成功率 | ≥90% | <70%告警 | 复查失败策略+暂停连续失败任务 |
| 平均执行时长 | 不高于预估1.2倍 | 超过预估1.5倍告警 | 调整超时阈值或触发降级 |
| 调度偏移量 | ≤30秒 | 偏移>30秒告警 | 检查平台调度能力+校准cron |
| 连续失败计数 | <3次 | ≥3次暂停任务 | 升级人工审批+排查根因 |
| 依赖阻塞率 | ≤5% | >5%告警 | 检查DAG前置任务+解锁阻塞链路 |

## Few-shot 示例

### 示例 1：正常流程 — A型内容传播反馈回路

**输入**:
```json
{
  "domain_type": "A",
  "automation_enabled": true
}
```

**输出**:
```json
{
  "loops": [
    {
      "type": "内容效果反馈",
      "signal_sources": { "external": ["互动量", "转化率"], "internal": ["选题命中率"] },
      "action": "更新选题库+优化提示词",
      "frequency": "每日",
      "cold_start": { "default_values": "前7天使用行业均值", "exit_conditions": "连续3天数据采集成功率>80%" }
    }
  ],
  "monitoring_metrics": [
    { "name": "执行成功率", "healthy_threshold": "≥90%", "alert_threshold": "<70%" },
    { "name": "平均执行时长", "healthy_threshold": "≤预估1.2倍", "alert_threshold": ">预估1.5倍" },
    { "name": "调度偏移量", "healthy_threshold": "≤30秒", "alert_threshold": ">30秒" }
  ]
}
```

### 示例 2：异常流程 — 冷启动数据不足触发保守策略

**输入**:
```json
{
  "domain_type": "B",
  "automation_enabled": false,
  "cold_start": true
}
```

**输出**:
```json
{
  "loops": [
    {
      "type": "客户满意度反馈",
      "signal_sources": { "external": ["NPS评分"], "internal": ["工单解决率"] },
      "action": "预设NPS基准值=50+人工标注前100条",
      "frequency": "每周",
      "cold_start": { "default_values": "NPS基准50分, 转化率基准3%", "exit_conditions": "累计100条有效反馈后切换自动计算" }
    }
  ],
  "monitoring_metrics": [
    { "name": "执行成功率", "healthy_threshold": "≥90%", "alert_threshold": "<70%", "status": "cold_start_warning" },
    { "name": "连续失败计数", "healthy_threshold": "<3次", "alert_threshold": "≥3次暂停", "status": "healthy" }
  ]
}
```

### 示例 3：快速通道 — 单人场景简化反馈回路

**输入**:
```json
{
  "domain_type": "A",
  "automation_enabled": false,
  "channel": "fast"
}
```

**输出**:
```json
{
  "loops": [
    {
      "type": "内容效果反馈(简化)",
      "signal_sources": { "external": ["用户直接反馈"], "internal": [] },
      "action": "每完成10条内容手工复盘",
      "frequency": "按需",
      "cold_start": { "default_values": "首次使用预设模板", "exit_conditions": "积累20条以上内容后切换" },
      "note": "快速通道：仅保留核心反馈回路，跳过自动化监控"
    }
  ],
  "monitoring_metrics": [
    { "name": "执行成功率", "healthy_threshold": "≥90%", "alert_threshold": "<70%", "note": "快速通道仅做基本健康检查" }
  ]
}
```

## 知识库挂载点 (knowledge_base_mount_points)


> **⚠️ 挂载点说明**：以下 `file://` 路径为概念性挂载点（conceptual mount points），用于声明本 skill 的知识库依赖结构。它们不是物理文件路径，不需要实际加载文件。执行时请直接依据本 SKILL.md 正文中的规则定义和伪代码逻辑工作。
- **[static]** `file://feedback-loops/domain-required-loops` — 按领域类型必建反馈回路映射

## 依赖关系

- `core-mental-model-engine`

## 详细执行逻辑

```text
FUNCTION execute_protocol_feedback_loop(input):
    ASSERT input.domain_type IN ["A","B","C","D","F"]  # E型已改为A-F组合标记

    // === 第一步：按领域类型确定必建反馈回路 ===
    // 按领域类型必建反馈回路映射已在本SKILL.md正文中定义，无需外部加载
    loops = []
    domain_required = GET_REQUIRED_LOOPS(input.domain_type)

    // 各领域必建回路数量：
    // A型: 3条(内容效果+选题命中率+内容质量)
    // B型: 2条(客户满意度+转化率)
    // C型: 2条(知识使用率+知识更新率)
    // D型: 2条(执行成功率+数据质量)
    // F型: 2条(客户满意度+响应时间)
    // E型: 取包含子类型的并集

    // 使用domain_profile判断混合型（E型已改为A-F的组合标记，不再是独立类型）
    IF input.domain_profile EXISTS AND LENGTH(input.domain_profile.secondary_domains) > 0:
        // 混合型场景：取包含子类型的并集
        all_types = [input.domain_profile.primary_domain] + input.domain_profile.secondary_domains
        FOR sub IN all_types:
            sub_required = GET_REQUIRED_LOOPS(sub)
            FOR req IN sub_required:
                IF req NOT IN domain_required:
                    APPEND domain_required WITH req

    // === 第二步：为每条回路定义信号源/处理动作/频率 ===
    FOR required_loop IN domain_required:
        loop_config = {}
        loop_config.type = required_loop.name

        // 定义信号源(外部+内部)
        IF required_loop == "内容效果反馈":
            loop_config.signal_sources = {external: ["互动量","转化率"], internal: ["选题命中率"]}
            loop_config.action = "更新选题库+优化提示词"
            loop_config.frequency = "每日"
        ELIF required_loop == "客户满意度":
            loop_config.signal_sources = {external: ["NPS评分"], internal: ["工单解决率"]}
            loop_config.action = "预设NPS基准值+人工标注前100条"
            loop_config.frequency = "每周"
        ELIF required_loop == "知识使用率":
            loop_config.signal_sources = {external: ["检索量"], internal: ["命中率"]}
            loop_config.action = "更新知识库索引+优化检索提示词"
            loop_config.frequency = "每周"
        ELIF required_loop == "执行成功率":
            loop_config.signal_sources = {external: ["任务完成率"], internal: ["调度成功率"]}
            loop_config.action = "复查失败策略+优化执行链路"
            loop_config.frequency = "每日"
        ELIF required_loop == "响应时间":
            loop_config.signal_sources = {external: ["平均响应时长"], internal: ["调度延迟"]}
            loop_config.action = "调整超时阈值+优化调度优先级"
            loop_config.frequency = "每日"
        ELIF required_loop == "转化率":
            loop_config.signal_sources = {external: ["转化漏斗数据"], internal: ["CTA点击率"]}
            loop_config.action = "优化CTA措辞+调整转化路径"
            loop_config.frequency = "每周"

        // === 第三步：定义冷启动策略(默认值+退出条件) ===
        loop_config.cold_start = {}
        IF input.cold_start == true OR IS_NEW_DEPLOYMENT():
            IF required_loop == "内容效果反馈":
                loop_config.cold_start.default_values = "前7天使用行业均值"
                loop_config.cold_start.exit_conditions = "连续3天数据采集成功率>80%"
            ELIF required_loop == "客户满意度":
                loop_config.cold_start.default_values = "NPS基准50分, 转化率基准3%"
                loop_config.cold_start.exit_conditions = "累计100条有效反馈后切换自动计算"
            ELIF required_loop == "执行成功率":
                loop_config.cold_start.default_values = "前30天使用预设成功率90%"
                loop_config.cold_start.exit_conditions = "连续7天实际数据采集成功率>85%"
            ELSE:
                loop_config.cold_start.default_values = "行业通用基准值"
                loop_config.cold_start.exit_conditions = "累计50条有效信号后切换自动计算"

        APPEND loops WITH loop_config

    // === 第四步：信号质量筛选规则 ===
    FOR loop IN loops:
        loop.quality_filter = {}
        loop.quality_filter.min_sample_size = 10  // 最低样本量
        loop.quality_filter.outlier_threshold = "3σ"  // 异常值阈值
        loop.quality_filter.signal_confidence = 0.8  // 信号置信度下限
        // 筛选规则：样本不足→使用冷启动默认值；异常值→标记不参与计算

    // === 第五步：5项调度监控指标(§5.9.6关联) ===
    monitoring_metrics = [
        {name: "执行成功率", healthy_threshold: "≥90%", alert_threshold: "<70%告警",
         action: "复查失败策略+暂停连续失败任务"},
        {name: "平均执行时长", healthy_threshold: "≤预估1.2倍", alert_threshold: ">预估1.5倍告警",
         action: "调整超时阈值或触发降级"},
        {name: "调度偏移量", healthy_threshold: "≤30秒", alert_threshold: "偏移>30秒告警",
         action: "检查平台调度能力+校准cron"},
        {name: "连续失败计数", healthy_threshold: "<3次", alert_threshold: "≥3次暂停任务",
         action: "升级人工审批+排查根因"},
        {name: "依赖阻塞率", healthy_threshold: "≤5%", alert_threshold: ">5%告警",
         action: "检查DAG前置任务+解锁阻塞链路"}
    ]

    // 快速通道简化处理
    IF input.channel == "fast":
        loops = [loops[0]]  // 仅保留核心反馈回路
        monitoring_metrics = [monitoring_metrics[0]]  // 仅保留基本健康检查
        APPEND loops[0] WITH {note: "快速通道：仅保留核心反馈回路，跳过自动化监控"}

    // === 第六步：最终断言与输出 ===
    ASSERT LENGTH(loops) > 0
    ASSERT LENGTH(monitoring_metrics) > 0

    // 质量门控由编排器在阶段结束后统一调用，skill内部不再自调用quality-gate（避免递归）
    RETURN {loops, monitoring_metrics}
```

## 版本

1.3.0

---
*本Skill由全域专家团构建skills体系生成，版本1.3.0，日期2026-06-16*
