---
name: constraint-naming-convention
description: Agent ID: kebab-case;花名:2-3字正常人名风格(谐音巧思,不与profession重复);profession:禁止通用title Use when: 用户说"constraint-naming-convention、命名规范约束、L4命名"等触发词。
---

# 命名规范(精确三分法)

> **层级**: L4 | **版本**: 1.0.0 | **ID**: `constraint-naming-convention` | **中文名**: 命名规范(精确三分法) | **英文名**: Naming Convention
# 命名规范(精确三分法) (Naming Convention)

> **层级**: L4 | **版本**: 1.0.0 | **ID**: `constraint-naming-convention`
> **编排关系**: 本skill由 `team-orchestrator` 按需自动加载执行，属于全域专家团构建skills系统的内部组件，用户不应直接触发。

## 概述

Agent ID: kebab-case;花名:2-3字正常人名风格(谐音巧思,不与profession重复);profession:禁止通用title。

## 触发条件

当检测到以下关键词或场景时自动激活：命名规范约束, L4命名, Agent ID规范校验

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

精确三分法：(1)Agent ID: kebab-case(如content-strategist);(2)花名:2-3字正常人名风格,谐音巧思,不与profession重复(如'墨言'而非'内容师');(3)profession:禁止通用title(团长/主理人),必须具体职能(如'内容策略师')。禁止：纯叠字/纯功能词直接作名/谐音生硬/一个字/无意义随机名/和profession重复/数字符号英文。主理人profession框架：A=内容制作总监;B=交付总监;C=知识架构总监;D=流程编排总监;F=服务运营总监;E=取主要子类型+多线统筹

## Few-shot 示例

### 示例 1: 命名三分法违规检查

**输入**:
```json
{
  "target_check": "Agent ID='内容专家1', 花名='内容师', profession='负责人'",
  "context": {
    "layer": "L4",
    "domain_type": "A"
  }
}
```

**输出**:
```json
{
  "compliant": false,
  "violations": [
    {
      "rule": "Agent ID规范",
      "detail": "'内容专家1'非法:应为kebab-case英文如content-strategist,禁止中文和数字",
      "suggestion": "content-strategist"
    },
    {
      "rule": "花名规范",
      "detail": "'内容师'是纯功能词,不符合2-3字正常人名风格(谐音巧思)",
      "suggestion": "墨言(谐音'默言')"
    },
    {
      "rule": "profession规范",
      "detail": "'负责人'是禁止的通用title,应用具体职能",
      "suggestion": "A型主理人→'内容制作总监',或非主理人→'内容策略师'"
    }
  ]
}
```

### 示例 2: 合规命名批量验证

**输入**:
```json
{
  "target_check": "团队角色列表: [{id:'chief-editor',name:'林语',profession:'总编辑'},{id:'content-writer',name:'苏砚',profession:'内容主笔'},{id:'visual-designer',name:'乔雨',profession:'视觉设计师'}]",
  "context": {
    "layer": "L4",
    "domain_type": "A"
  }
}
```

**输出**:
```json
{
  "compliant": true,
  "validation_detail": [
    {"id": "chief-editor", "name_ok": true, "reason": "林语:2字正常人名风格,kebab-case ID", "profession_ok": true, "reason": "总编辑:具体职能"},
    {"id": "content-writer", "name_ok": true, "reason": "苏砚:2字正常人名风格,有文化内涵", "profession_ok": true, "reason": "内容主笔:具体职能"},
    {"id": "visual-designer", "name_ok": true, "reason": "乔雨:2字正常人名风格", "profession_ok": true, "reason": "视觉设计师:具体职能"}
  ],
  "suggestions": []
}
```

### 示例 3: 主理人profession框架匹配

**输入**:
```json
{
  "target_check": "D型(数据+自动化)团队主理人profession='团长'",
  "context": {
    "layer": "L4",
    "domain_type": "D"
  }
}
```

**输出**:
```json
{
  "compliant": false,
  "violations": [
    {
      "rule": "profession禁止通用title",
      "detail": "'团长'是禁止的通用title",
      "domain_type": "D型数据+自动化",
      "correct_profession": "流程编排总监",
      "reason": "D型主理人profession框架: D=流程编排总监"
    }
  ],
  "suggestions": [
    "将profession改为'流程编排总监'",
    "非主理人角色的profession可用具体职能如'数据工程师'、'自动化脚本开发员'"
  ]
}
```

## 知识库挂载点 (knowledge_base_mount_points)


> **⚠️ 挂载点说明**：以下 `file://` 路径为概念性挂载点（conceptual mount points），用于声明本 skill 的知识库依赖结构。它们不是物理文件路径，不需要实际加载文件。执行时请直接依据本 SKILL.md 正文中的规则定义和伪代码逻辑工作。
- **[static]** `file://constraints/constraint-naming-convention` — 命名规范(精确三分法)完整规则集

## 依赖关系

无前置依赖。

## 详细执行逻辑

```text
FUNCTION execute_constraint_naming_convention(input):
    ASSERT input matches input_schema
    ASSERT input.target_check != NULL AND LEN(input.target_check) > 0
    violations = []
    suggestions = []
    context = input.context IF input.context != NULL ELSE {}

    // ===== 精确三分法: Agent ID / 花名 / profession =====

    // 加载禁止列表
    FORBIDDEN_PROFESSION_TITLES = ["团长", "主理人", "负责人", "管理者", "主管", "领导", "总负责", "协调人"]
    ALLOWED_HOMOPHONE_NAMES = LOAD_HOMOPHONE_DICTIONARY()  // 允许_谐音型花名
    FORBIDDEN_GENERIC_TITLES = ["总负责", "统筹", "协调", "管理"]  // 通用title禁用

    // 主理人profession框架(A-F)
    LEAD_PROFESSION_FRAMEWORK = {
        "A": "内容制作总监",
        "B": "交付总监",
        "C": "知识架构总监",
        "D": "流程编排总监",
        "E": "取主要子类型+多线统筹",  // E型需根据子类型确定
        "F": "服务运营总监"
    }

    // 提取所有角色条目
    roles = EXTRACT_ROLE_ENTRIES(input.target_check)

    FOR EACH role IN roles:
        // ===== 第一分法: Agent ID校验 =====
        agent_id = role.id
        IF agent_id == NULL OR agent_id == "":
            APPEND violations, {"rule": "Agent ID规范", "detail": "Agent ID不能为空"}
        ELIF NOT MATCH(agent_id, /^[a-z][a-z0-9-]*$/):
            // 必须kebab-case: 小写字母+数字+连字符
            APPEND violations, {
                "rule": "Agent ID规范",
                "detail": "Agent ID '" + agent_id + "' 不符合kebab-case规范,禁止中文/数字开头/下划线/大写",
                "suggestion": CONVERT_TO_KEBAB_CASE(agent_id)
            }
            APPEND suggestions, CONVERT_TO_KEBAB_CASE(agent_id)

        // 检查ID是否包含中文或数字
        IF CONTAINS_CHINESE(agent_id):
            APPEND violations, {"rule": "Agent ID禁止中文", "detail": "Agent ID禁止使用中文: " + agent_id}
        IF MATCH(agent_id, /[0-9]+$/):
            APPEND violations, {"rule": "Agent ID禁止数字后缀", "detail": "Agent ID禁止数字后缀如'expert1': " + agent_id}

        // ===== 第二分法: 花名校验 =====
        name = role.name
        IF name == NULL OR name == "":
            APPEND violations, {"rule": "花名规范", "detail": "花名不能为空"}
        ELSE:
            name_len = COUNT_CHARS(name)

            // 长度检查(建议2-3字,特殊4字)
            IF name_len == 1:
                APPEND violations, {"rule": "花名长度", "detail": "花名'" + name + "'仅1字,不符合2-3字正常人名风格"}
            ELIF name_len == 4:
                // 4字须体现文化内涵,非随意堆砌
                IF NOT IS_CULTURAL_NAME(name):
                    APPEND violations, {"rule": "花名4字规范", "detail": "4字花名'" + name + "'须体现文化内涵,非随意堆砌"}
            ELIF name_len > 4:
                APPEND violations, {"rule": "花名长度", "detail": "花名'" + name + "'超过4字,不符合规范"}

            // 禁止: 纯叠字
            IF IS_PURE_REDUPPLICATION(name):
                APPEND violations, {"rule": "花名禁止纯叠字", "detail": "'" + name + "'是纯叠字,不符合正常人名风格"}

            // 禁止: 纯功能词直接作名
            IF IS_PURE_FUNCTION_WORD(name):
                APPEND violations, {"rule": "花名禁止纯功能词", "detail": "'" + name + "'是纯功能词,不符合2-3字正常人名风格(谐音巧思)"}

            // 禁止: 谐音生硬
            IF HAS_FORCED_HOMOPHONE(name) AND NOT IN_ALLOWED_HOMOPHONE_NAMES(name):
                APPEND violations, {"rule": "花名谐音生硬", "detail": "'" + name + "'谐音生硬,不自然"}

            // 禁止: 和profession重复
            IF name == role.profession OR CONTAINS(role.profession, name):
                APPEND violations, {"rule": "花名与profession重复", "detail": "花名'" + name + "'与profession重复"}

            // 禁止: 数字/符号/英文
            IF CONTAINS_DIGIT_OR_SYMBOL_OR_ENGLISH(name):
                APPEND violations, {"rule": "花名禁止数字符号英文", "detail": "花名禁止包含数字、符号或英文"}

            // 禁止: 无意义随机名
            IF IS_RANDOM_MEANINGLESS(name):
                APPEND violations, {"rule": "花名禁止无意义随机名", "detail": "'" + name + "'无实际含义"}

        // ===== 第三分法: profession校验 =====
        profession = role.profession
        IF profession == NULL OR profession == "":
            APPEND violations, {"rule": "profession规范", "detail": "profession不能为空"}
        ELSE:
            // 禁止通用title
            FOR EACH forbidden IN FORBIDDEN_PROFESSION_TITLES:
                IF CONTAINS(profession, forbidden):
                    APPEND violations, {
                        "rule": "profession禁止通用title",
                        "detail": "profession '" + profession + "' 包含禁止的通用title '" + forbidden + "'"
                    }
                    // 根据领域推荐正确profession
                    domain = context.domain_type IF context.domain_type != NULL ELSE "A"
                    IF role.is_lead:
                        correct = LEAD_PROFESSION_FRAMEWORK[domain]
                        APPEND suggestions, domain + "型主理人→'" + correct + "'"
                    ELSE:
                        APPEND suggestions, "使用具体职能替代'" + forbidden + "'"

            // 主理人profession框架匹配
            IF role.is_lead:
                domain = context.domain_type IF context.domain_type != NULL ELSE "A"
                expected = LEAD_PROFESSION_FRAMEWORK[domain]
                IF profession != expected AND NOT CONTAINS(profession, expected):
                    APPEND violations, {
                        "rule": "主理人profession框架",
                        "detail": domain + "型主理人profession应为'" + expected + "',当前为'" + profession + "'",
                        "correct_profession": expected
                    }
                    APPEND suggestions, "将profession改为'" + expected + "'"

    // 汇总结果
    compliant = (LEN(violations) == 0)
    RETURN {"compliant": compliant, "violations": violations, "suggestions": suggestions}
```

## 版本

1.0.0

---
*本Skill由全域专家团构建skills体系自动生成，版本1.0.0，日期2026-06-15*
