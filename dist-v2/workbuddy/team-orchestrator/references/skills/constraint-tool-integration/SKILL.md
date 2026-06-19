---
name: constraint-tool-integration
description: MCP Server配置模板→健康检查机制→超时/重试策略→降级决策树→成本监控→安全校验。 Use when: 用户说"constraint-tool-integration、工具集成约束、L4工具"等触发词。
---

# 工具集成规范

> **层级**: L4 | **版本**: 1.0.0 | **ID**: `constraint-tool-integration` | **中文名**: 工具集成规范 | **英文名**: Tool Integration Standard
# 工具集成规范 (Tool Integration Standard)

> **层级**: L4 | **版本**: 1.0.0 | **ID**: `constraint-tool-integration`
> **编排关系**: 本skill由 `team-orchestrator` 按需自动加载执行，属于全域专家团构建skills系统的内部组件，用户不应直接触发。

## 概述

MCP Server配置模板→健康检查机制→超时/重试策略→降级决策树→成本监控→安全校验。

## 触发条件

当检测到以下关键词或场景时自动激活：工具集成约束, L4工具, MCP配置降级决策树

## 输入规范 (input_schema)

```json
{
  "type": "object",
  "properties": {
    "target_check": {
      "type": "string",
      "description": "待检查的目标内容"
    },
    "context": {
      "type": "object",
      "description": "检查上下文"
    }
  },
  "required": [
    "target_check"
  ]
}
```

## 输出规范 (output_schema)

```json
{
  "type": "object",
  "properties": {
    "compliant": {
      "type": "boolean"
    },
    "violations": {
      "type": "array",
      "items": {
        "type": "object"
      }
    },
    "suggestions": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  },
  "required": [
    "compliant",
    "violations",
    "suggestions"
  ]
}
```

## 工具声明 (tool_declarations)

本Skill无外部工具依赖，纯提示词可执行。

## 执行逻辑

工具集成三层架构：L1平台内置(零成本/最高可靠性);L2协议扩展MCP/OpenAPI(低-中成本);L3外部API(中-高成本/依赖第三方)。健康检查：每次调用前轻量ping+每日完整检查。重试：最多3次，指数退避(1s/2s/4s)。降级决策树：瞬时错误→重试;持续错误→切换降级+通知;关键错误→暂停+告警。

## Few-shot 示例

### 示例 1: MCP Server健康检查通过

**输入**:
```json
{
  "target_check": "ComfyUI MCP Server连接配置",
  "context": {
    "layer": "L4",
    "tool_tier": "L2协议扩展",
    "check_type": "health"
  }
}
```

**输出**:
```json
{
  "compliant": true,
  "health_check": {
    "ping_result": "ok",
    "latency_ms": 45,
    "retry_remaining": 3,
    "next_full_check": "24h后"
  },
  "integration_config": {
    "tier": "L2 MCP",
    "retry_strategy": "指数退避1s/2s/4s,最多3次",
    "degradation_plan": "MCP不可用时→手动+参数快照降级方案"
  }
}
```

### 示例 2: 工具持续故障→降级决策

**输入**:
```json
{
  "target_check": "飞书API连续3次调用失败(500错误)",
  "context": {
    "layer": "L4",
    "tool_tier": "L3外部API",
    "error_type": "persistent"
  }
}
```

**输出**:
```json
{
  "compliant": true,
  "health_check": {
    "status": "unavailable",
    "consecutive_failures": 3,
    "retry_exhausted": true
  },
  "degradation_decision": {
    "action": "切换降级+通知",
    "degraded_to": "纯提示词方案(用户手动推送)",
    "notification": "飞书API不可用,已自动切换为手动推送模式,恢复后自动切回"
  },
  "recovery_plan": "每5分钟轻量ping检查,恢复后自动回切"
}
```

### 示例 3: 关键错误→暂停+告警

**输入**:
```json
{
  "target_check": "数据安全校验发现客户手机号未经脱敏直接传给第三方API",
  "context": {
    "layer": "L4",
    "error_type": "critical",
    "security_level": "PII"
  }
}
```

**输出**:
```json
{
  "compliant": false,
  "violations": [
    {
      "rule": "数据安全强制+安全校验",
      "detail": "客户手机号(PII)未经脱敏直接传给第三方API",
      "consequence": "违反数据安全法规,可能造成隐私泄露"
    }
  ],
  "action": "暂停+告警",
  "required_fix": "在API调用前增加脱敏层(mask_phone字段),或走L1平台内置工具",
  "escalation": "通知安全负责人,待修复后人工确认放行"
}
```

## 知识库挂载点 (knowledge_base_mount_points)


> **⚠️ 挂载点说明**：以下 `file://` 路径为概念性挂载点（conceptual mount points），用于声明本 skill 的知识库依赖结构。它们不是物理文件路径，不需要实际加载文件。执行时请直接依据本 SKILL.md 正文中的规则定义和伪代码逻辑工作。
- **[static]** `file://constraints/constraint-tool-integration` — 工具集成规范完整规则集

## 依赖关系

无前置依赖。

## 详细执行逻辑

```text
FUNCTION execute_constraint_tool_integration(input):
    ASSERT input matches input_schema
    ASSERT input.target_check != NULL AND LEN(input.target_check) > 0
    violations = []
    suggestions = []
    context = input.context IF input.context != NULL ELSE {}

    // ===== 阶段1: 4级优先级评估 =====
    // 优先级: L1平台内置(零成本/最高可靠性) > L2协议扩展MCP/OpenAPI(低-中成本) > L3外部API(中-高成本) > 纯提示词兜底(强制)
    tool_tier = IDENTIFY_TOOL_TIER(input.target_check)
    IF context.tool_tier != NULL:
        tool_tier = context.tool_tier

    priority_score = CALCULATE_PRIORITY(tool_tier)
    // L1=100, L2=60, L3=30, 纯提示词=0(但始终有效)

    // ===== 阶段2: 纯提示词兜底强制 =====
    // 无论选择哪个优先级的工具,都必须提供纯提示词兜底方案
    IF NOT HAS_PROMPT_FALLBACK(input.target_check):
        APPEND violations, {
            "rule": "纯提示词兜底强制",
            "detail": "所有工具集成必须提供纯提示词兜底方案",
            "consequence": "工具不可用时流程完全中断"
        }
        APPEND suggestions, "为每个工具依赖添加纯提示词替代步骤"

    // ===== 阶段3: 健康检查机制 =====
    health_config = EXTRACT_HEALTH_CONFIG(input.target_check)
    IF health_config == NULL:
        APPEND violations, {
            "rule": "健康检查",
            "detail": "缺少工具健康检查配置",
            "fix": "配置每次调用前轻量ping+每日完整检查"
        }
    ELSE:
        // 3a: 轻量ping检查(每次调用前)
        IF NOT health_config.has_ping_check:
            APPEND suggestions, "添加每次调用前轻量ping检查"
        // 3b: 完整检查(每日)
        IF NOT health_config.has_daily_check:
            APPEND suggestions, "添加每日完整健康检查"

    // ===== 阶段4: 超时/重试策略 =====
    retry_config = EXTRACT_RETRY_CONFIG(input.target_check)
    IF retry_config == NULL:
        // 默认重试策略:最多3次,指数退避(1s/2s/4s)
        retry_config = {"max_retries": 3, "backoff": [1, 2, 4], "strategy": "exponential"}
        APPEND suggestions, "使用默认重试策略:最多3次,指数退避1s/2s/4s"
    ELSE:
        IF retry_config.max_retries > 3:
            APPEND suggestions, "重试次数建议不超过3次,避免雪崩"
        IF NOT retry_config.has_exponential_backoff:
            APPEND suggestions, "建议使用指数退避策略"

    // ===== 阶段5: 降级决策树 =====
    degradation_tree = BUILD_DEGRADATION_TREE(input.target_check)
    // 5a: 瞬时错误→重试
    IF context.error_type == "transient":
        action = "retry"
        retry_count = 0
        WHILE retry_count < retry_config.max_retries:
            result = RETRY_OPERATION()
            IF result.success:
                BREAK
            WAIT(retry_config.backoff[retry_count])
            retry_count = retry_count + 1

    // 5b: 持续错误→切换降级+通知
    IF context.error_type == "persistent":
        APPEND suggestions, "持续错误→切换降级方案+通知用户"
        degraded_to = SELECT_DEGRADATION_TARGET(tool_tier)
        // L3→L2→L1→纯提示词
        APPEND suggestions, "降级到: " + degraded_to + ",恢复后自动切回"

    // 5c: 关键错误→暂停+告警
    IF context.error_type == "critical":
        APPEND violations, {
            "rule": "关键错误处理",
            "detail": "关键错误须暂停操作+告警通知",
            "consequence": "继续执行可能导致数据损坏或安全风险"
        }
        APPEND suggestions, "暂停操作,通知安全负责人,待修复后人工确认放行"

    // ===== 阶段6: 成本监控 =====
    cost_config = EXTRACT_COST_CONFIG(input.target_check)
    IF cost_config != NULL:
        IF cost_config.estimated_cost > cost_config.budget_limit:
            APPEND suggestions, "预估成本超限,建议降级到更低优先级工具"
        IF NOT cost_config.has_cost_tracking:
            APPEND suggestions, "添加成本跟踪配置,监控API调用量和费用"

    // ===== 阶段7: 数据安全审查集成 =====
    IF context.security_level == "PII" OR HAS_PII_DATA(input.target_check):
        // 敏感数据必须脱敏后才能传给第三方API
        IF NOT HAS_DATA_MASKING(input.target_check):
            APPEND violations, {
                "rule": "数据安全强制+安全校验",
                "detail": "敏感数据(PII)未经脱敏直接传给第三方API",
                "consequence": "违反数据安全法规,可能造成隐私泄露"
            }
            APPEND suggestions, "在API调用前增加脱敏层,或走L1平台内置工具"

    IF context.security_level == "financial" OR context.security_level == "medical":
        IF NOT HAS_ENCRYPTION(input.target_check):
            APPEND violations, {
                "rule": "数据安全-加密",
                "detail": "金融/医疗数据传输必须加密",
                "consequence": "明文传输违反行业合规要求"
            }

    // 汇总结果
    compliant = (LEN(violations) == 0)
    RETURN {"compliant": compliant, "violations": violations, "suggestions": suggestions}
```

## 版本

1.0.0

---
*本Skill由全域专家团构建skills体系自动生成，版本1.0.0，日期2026-06-15*
