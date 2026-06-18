
# 灵活适配规则 (Flexible Rules)

> **层级**: L4 | **版本**: 1.1.0 | **ID**: `constraint-flexible-rules`
> **编排关系**: 本skill由 `team-orchestrator` 按需自动加载执行，属于全域专家团构建skills系统的内部组件，用户不应直接触发。

## 概述

默认值，用户/领域需要时调整。11条灵活规则。

## 触发条件

当检测到以下关键词或场景时自动激活：规则, 约束, 强制, 规范, 命名

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

11条灵活规则：(1)领域特定子协议按领域激活;(2)角色精简(保证第一责任人前提下合并);(3)工具可选(纯提示词始终有效);(4)人工介入密度按团队调整;(5)迭代粒度按领域调整;(6)反馈回路数量按领域激活;(7)冷启动退出条件默认可调;(8)禁用词列表长度(低≥3,高/强监管≥8);(9)平台选择灵活;(10)花名字数灵活(建议2-3字,特殊4字);(11)紧急终止模式(快速模式最小输出填充未完成阶段,4.4人工审批不可跳过)

## Few-shot 示例

### 示例 1: 角色精简+工具可选调整

**输入**:
```json
{
  "target_check": "小型团队(2人)需要A型内容传播专家团",
  "context": {
    "layer": "L4",
    "domain_type": "A",
    "team_size": 2,
    "tools_available": false
  }
}
```

**输出**:
```json
{
  "compliant": true,
  "flexibility_applied": [
    {
      "rule": "角色精简(规则2)",
      "default": "按交付物数量配置角色",
      "adjustment": "2人团队:合并选题+撰写为一个角色,发布+数据分析为另一个角色",
      "condition": "保证每项交付有第一责任人"
    },
    {
      "rule": "工具可选(规则3)",
      "default": "优先推荐MCP/API工具",
      "adjustment": "无工具可用→纯提示词方案始终有效,所有流程由用户手动执行",
      "condition": "纯提示词必须包含完整的手动操作步骤"
    }
  ]
}
```

### 示例 2: 强监管领域禁用词扩展

**输入**:
```json
{
  "target_check": "医疗科普团队(强监管领域)的禁用词列表",
  "context": {
    "layer": "L4",
    "domain_type": "A",
    "regulated": true,
    "regulation_level": "强监管"
  }
}
```

**输出**:
```json
{
  "compliant": true,
  "flexibility_applied": [
    {
      "rule": "禁用词列表长度(规则8)",
      "default": "低风险领域≥3个禁用词",
      "adjustment": "强监管医疗领域≥8个禁用词,包括:'治愈''根治''100%''绝对安全''无副作用'等",
      "condition": "每次内容生成前自动扫描禁用词,命中则拦截并建议替换"
    }
  ],
  "additional_rules": [
    "领域特定子协议(规则1):激活医疗合规子协议,要求所有医学科普附免责声明",
    "反馈回路数量(规则6):从默认1个增加到3个(内容审核→医学审校→合规终审)"
  ]
}
```

### 示例 3: 花名字数灵活+迭代粒度调整

**输入**:
```json
{
  "target_check": "古籍研究专家角色命名,领域需要4字花名体现文化内涵",
  "context": {
    "layer": "L4",
    "domain_type": "C",
    "special_name_request": true
  }
}
```

**输出**:
```json
{
  "compliant": true,
  "flexibility_applied": [
    {
      "rule": "花名字数灵活(规则10)",
      "default": "建议2-3字正常人名风格",
      "adjustment": "古籍研究领域特殊,允许4字花名如'墨韵清心'",
      "condition": "4字须体现文化内涵,非随意堆砌,仍需保持人名风格"
    },
    {
      "rule": "迭代粒度(规则5)",
      "default": "以月为迭代周期",
      "adjustment": "古籍研究内容产出慢,迭代周期调整为季度",
      "condition": "每个迭代周期至少产出3篇深度长文"
    }
  ]
}
```

## 知识库挂载点 (knowledge_base_mount_points)

- **[static]** `file://./knowledge/constraint-flexible-rules.md` — 灵活适配规则完整规则集

## 依赖关系

无前置依赖。

## 11条灵活规则展开

| 规则 | 说明 | 默认值 | 调整条件 |
| --- | --- | --- | --- |
| 领域特定子协议 | 按领域激活对应的合规/审核子协议 | 不激活子协议 | 用户选择强监管领域(医疗/金融/法律)时自动激活 |
| 角色精简 | 在保证第一责任人前提下合并相近角色 | 按交付物数量1:1配置角色 | 团队人数<交付物数量时可合并,如选题+撰写合并为内容创作者 |
| 工具可选 | MCP/API工具不可用时降级为纯提示词 | 优先推荐MCP/API工具 | 用户明确表示无工具环境或工具连接失败时切换 |
| 人工介入密度 | 人工确认节点的数量和频率可调整 | 每个阶段结束前1次确认 | 小团队/快速通道→仅关键节点确认;大团队/严格通道→每阶段2次 |
| 迭代粒度 | 按领域调整产出的迭代周期 | 以月为迭代周期 | 快节奏(社交)→周迭代;慢节奏(研究/白皮书)→季度迭代 |
| 反馈回路数量 | 按领域和监管级别激活反馈审查环节 | 1个反馈回路(用户确认) | 强监管→3个(内容审核→专业审校→合规终审);低风险→省略 |
| 冷启动退出条件 | 初始样本数量默认可调整 | 冷启动期≥5个样本 | 小团队可降至3个;强监管领域需增加到10个 |
| 禁用词列表长度 | 按风险级别调整禁用词数量 | 低风险领域≥3个禁用词 | 高风险领域≥8个;强监管领域≥8个+行业特有禁用词 |
| 平台选择灵活 | 用户可自由切换或追加目标平台 | 用户指定平台为准 | 追加平台时重新触发S5架构评估,确认兼容性 |
| 花名字数灵活 | 花名在特定领域可突破2-3字限制 | 建议2-3字正常人名风格 | 古籍/文化领域可4字(需体现文化内涵);快速通道无严格检查 |
| 紧急终止模式 | 紧急终止时用快速模式最小输出填充未完成阶段 | 不支持紧急终止 | 用户说"够了"/"直接给我"/"跳过"时激活；4.4人工审批仍不可跳过 |
| 输出深度自适应 | 根据用户角色识别自动调整输出深度和术语密度 | 标准详细度 | 探索者→简化版(术语附解释)；决策者→精简版(表格+数字)；技术负责人→完整版(含实现细节) |

## 详细执行逻辑

```text
FUNCTION execute_constraint_flexible_rules(input):
    ASSERT input matches input_schema
    ASSERT input.target_check != NULL AND LEN(input.target_check) > 0
    flexibility_applied = []
    context = input.context IF input.context != NULL ELSE {}

    // 加载11条灵活规则(每条有默认值+调整条件)
    rules = LOAD_FLEXIBLE_RULES()  // 共11条,可按领域/通道/平台调整

    // ===== 规则1: 领域特定子协议 =====
    domain = context.domain_type IF context.domain_type != NULL ELSE "A"
    IF domain IN ["A"] AND context.regulated == true:
        // 强监管领域自动激活子协议
        APPEND flexibility_applied, {
            "rule": "领域特定子协议(规则1)",
            "default": "不激活子协议",
            "adjustment": "激活" + domain + "型合规子协议,要求所有内容附免责声明",
            "condition": "用户选择强监管领域时自动激活"
        }
    ELIF domain IN ["C", "D", "F"]:
        APPEND flexibility_applied, {
            "rule": "领域特定子协议(规则1)",
            "default": "不激活子协议",
            "adjustment": "激活" + domain + "型专业审校子协议",
            "condition": "C/D/F型领域涉及专业知识,需专业审校"
        }

    // ===== 规则2: 角色精简 =====
    team_size = context.team_size IF context.team_size != NULL ELSE 999
    deliverable_count = COUNT_DELIVERABLES(input.target_check)
    IF team_size < deliverable_count:
        // 合并相近角色,保证第一责任人
        merged_roles = MERGE_ROLES_BY_DELIVERABLE(input.target_check, team_size)
        APPEND flexibility_applied, {
            "rule": "角色精简(规则2)",
            "default": "按交付物数量1:1配置角色",
            "adjustment": STRING(team_size) + "人团队:合并相近角色,每项交付保证第一责任人",
            "condition": "团队人数<交付物数量时可合并"
        }

    // ===== 规则3: 工具可选 =====
    tools_available = context.tools_available IF context.tools_available != NULL ELSE true
    IF NOT tools_available:
        APPEND flexibility_applied, {
            "rule": "工具可选(规则3)",
            "default": "优先推荐MCP/API工具",
            "adjustment": "无工具可用→纯提示词方案始终有效,所有流程由用户手动执行",
            "condition": "纯提示词必须包含完整的手动操作步骤"
        }

    // ===== 规则4: 人工介入密度 =====
    IF context.team_size != NULL AND context.team_size <= 3:
        // 小团队:仅关键节点确认
        APPEND flexibility_applied, {
            "rule": "人工介入密度(规则4)",
            "default": "每个阶段结束前1次确认",
            "adjustment": "小团队→仅关键节点确认(S3+S7)",
            "condition": "团队人数<=3时减少确认频率"
        }
    ELIF context.track == "strict":
        // 严格通道:每阶段2次确认
        APPEND flexibility_applied, {
            "rule": "人工介入密度(规则4)",
            "default": "每个阶段结束前1次确认",
            "adjustment": "严格通道→每阶段2次确认(阶段中+阶段末)",
            "condition": "strict通道需更密集的人工确认"
        }

    // ===== 规则5: 迭代粒度 =====
    IF domain == "A" AND context.channel IN ["social", "xiaohongshu"]:
        APPEND flexibility_applied, {"rule": "迭代粒度(规则5)", "adjustment": "快节奏社交→周迭代"}
    ELIF domain IN ["C"]:
        APPEND flexibility_applied, {"rule": "迭代粒度(规则5)", "adjustment": "研究/白皮书→季度迭代"}

    // ===== 规则6: 反馈回路数量 =====
    IF context.regulated == true:
        APPEND flexibility_applied, {
            "rule": "反馈回路数量(规则6)",
            "default": "1个反馈回路(用户确认)",
            "adjustment": "强监管→3个(内容审核→专业审校→合规终审)",
            "condition": "强监管领域需多层反馈审查"
        }

    // ===== 规则7: 冷启动退出条件 =====
    IF context.team_size != NULL AND context.team_size <= 3:
        APPEND flexibility_applied, {
            "rule": "冷启动退出条件(规则7)",
            "default": "冷启动期>=5个样本",
            "adjustment": "小团队可降至3个样本;强监管需增加到10个",
            "condition": "团队规模小可降低冷启动门槛"
        }

    // ===== 规则8: 禁用词列表长度 =====
    regulation_level = context.regulation_level IF context.regulation_level != NULL ELSE "低风险"
    IF regulation_level == "强监管":
        APPEND flexibility_applied, {
            "rule": "禁用词列表长度(规则8)",
            "default": "低风险领域>=3个禁用词",
            "adjustment": "强监管>=8个禁用词+行业特有禁用词(如'治愈''根治''100%')",
            "condition": "强监管领域扩展禁用词列表"
        }
    ELIF regulation_level == "高风险":
        APPEND flexibility_applied, {
            "rule": "禁用词列表长度(规则8)",
            "adjustment": "高风险>=8个禁用词",
            "condition": "高风险领域增加禁用词数量"
        }

    // ===== 规则9: 平台选择灵活 =====
    IF HAS_MULTI_PLATFORM_REQUEST(input.target_check):
        APPEND flexibility_applied, {
            "rule": "平台选择灵活(规则9)",
            "adjustment": "追加平台时重新触发S5架构评估,确认兼容性",
            "condition": "追加目标平台"
        }

    // ===== 规则10: 花名字数灵活 =====
    IF context.special_name_request == true AND domain IN ["C"]:
        APPEND flexibility_applied, {
            "rule": "花名字数灵活(规则10)",
            "default": "建议2-3字正常人名风格",
            "adjustment": "古籍/文化领域可4字(需体现文化内涵)",
            "condition": "4字须体现文化内涵,非随意堆砌"
        }

    // 汇总结果
    compliant = true  // 灵活规则不阻断,仅记录调整
    violations = []  // 灵活规则无违规概念,只有调整记录

    RETURN {"compliant": compliant, "violations": violations, "suggestions": MAP(flexibility_applied, f => f.adjustment)}
```

## 版本

1.1.0

---
*本Skill由全域专家团构建skills体系自动生成，版本1.1.0，日期2026-06-16*
