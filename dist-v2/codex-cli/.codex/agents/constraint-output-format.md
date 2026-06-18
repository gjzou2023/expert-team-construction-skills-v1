
# 输出格式规范 (Output Format)

> **层级**: L4 | **版本**: 1.3.0 | **ID**: `constraint-output-format`
> **编排关系**: 本skill由 `team-orchestrator` 按需自动加载执行，属于全域专家团构建skills系统的内部组件，用户不应直接触发。

## 概述

方案文档14必含章节。v1.3.0新增标准输出结构模板与输出溯源参考指引。Markdown格式，Mermaid数据流，JSON Schema，条件激活标注。

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

方案文档14必含章节(改进#27修复：与S7的REQUIRED_CHAPTERS统一)：(1)专家包概览;(2)角色定义(各专家详细配置);(3)协作模型(Team型/Agent型协作协议);(4)SOP编排(阶段定义/触发条件/数据流);(5)数据流设计(Mermaid总图);(6)反馈闭环;(7)质量门控协议;(8)合规协议(4.1-4.5条件激活);(9)数据安全协议;(10)异常处理;(11)知识资产沉淀;(12)工具链配置(工具矩阵+集成规范+降级方案);(13)冷启动策略;(14)执行计划。格式约定：Markdown;数据流Mermaid;Schema用JSON;表格Markdown;条件激活标注'【X型激活】';技术术语首次附通俗解释

## Few-shot 示例

### 示例 1: 方案文档完整性检查

**输入**:
```json
{
  "target_check": "S7输出的专家包方案文档",
  "context": {
    "layer": "L4",
    "document_type": "方案文档"
  }
}
```

**输出**:
```json
{
  "compliant": false,
  "violations": [
    {
      "missing_chapter": "数据流总图(Mermaid)",
      "detail": "方案缺少第3章数据流总图,仅包含文字描述",
      "fix": "使用Mermaid graph TD语法绘制从S3→S5→S6→S7→S8的完整数据流"
    },
    {
      "missing_chapter": "知识资产沉淀",
      "detail": "方案缺少第10章知识资产沉淀,未说明学习成果如何结构化保存"
    }
  ],
  "chapters_present": 12,
  "chapters_required": 14,
  "suggestions": [
    "补充Mermaid数据流图",
    "在'迭代路线图+迁移指南'后增加知识资产沉淀章节"
  ]
}
```

### 示例 2: 格式规范检查

**输入**:
```json
{
  "target_check": "专家角色配置使用了纯文本描述,无JSON Schema",
  "context": {
    "layer": "L4",
    "document_type": "方案文档"
  }
}
```

**输出**:
```json
{
  "compliant": false,
  "violations": [
    {
      "rule": "格式约定",
      "detail": "Schema定义应使用JSON格式,当前为纯文本段落",
      "fix": "将各专家角色配置转为JSON Schema格式,标注必填/可选字段"
    },
    {
      "rule": "条件激活标注",
      "detail": "内容合规保障章节未标注'【X型激活】'标识",
      "fix": "在第6章开头添加'【A/B/C/D/E/F型激活】'条件激活标注"
    }
  ]
}
```

### 示例 3: 合规通过(全14章+格式正确)

**输入**:
```json
{
  "target_check": "D型数据自动化专家包最终方案",
  "context": {
    "layer": "L4",
    "domain_type": "D",
    "document_type": "方案文档"
  }
}
```

**输出**:
```json
{
  "compliant": true,
  "chapters_check": {
    "total_required": 14,
    "present": 14,
    "detail": "1专家包概览✓ 2各专家详细配置✓ 3数据流总图(Mermaid)✓ 4质量门控协议✓ 5信息准确性保障✓ 6内容合规保障(【D型激活】)✓ 7数据安全与隐私✓ 8异常处理✓ 9反馈闭环✓ 10知识资产沉淀✓ 11人类介入节点✓ 12迭代路线图+迁移指南✓ 13执行计划✓ 14架构健康检查报告✓"
  },
  "format_check": {
    "markdown": true,
    "mermaid_dataflow": true,
    "json_schema": true,
    "conditional_activation": "【D型激活】标注正确"
  }
}
```

## 知识库挂载点 (knowledge_base_mount_points)

- **[static]** `file://constraints/constraint-output-format` — 输出格式规范完整规则集

## 依赖关系

无前置依赖。

## 十四必含章节清单

改进#27修复：与S7的REQUIRED_CHAPTERS统一，消除29%重合度问题。

1. 专家包概览
2. 角色定义（各专家详细配置）
3. 协作模型（Team型/Agent型协作协议）
4. SOP编排（阶段定义/触发条件/数据流）
5. 数据流设计（Mermaid总图）
6. 反馈闭环
7. 质量门控协议
8. 合规协议（4.1-4.5条件激活）
9. 数据安全协议
10. 异常处理
11. 知识资产沉淀
12. 工具链配置（工具矩阵+集成规范+降级方案）
13. 冷启动策略
14. 执行计划

## 14必含章节与符号约定

| 序号 | 必含章节 |
| --- | --- |
| 1 | 专家包概览 |
| 2 | 角色定义（各专家详细配置） |
| 3 | 协作模型（Team型/Agent型协作协议） |
| 4 | SOP编排（阶段定义/触发条件/数据流） |
| 5 | 数据流设计（Mermaid总图） |
| 6 | 反馈闭环 |
| 7 | 质量门控协议 |
| 8 | 合规协议（4.1-4.5条件激活） |
| 9 | 数据安全协议 |
| 10 | 异常处理 |
| 11 | 知识资产沉淀 |
| 12 | 工具链配置（工具矩阵+集成规范+降级方案） |
| 13 | 冷启动策略 |
| 14 | 执行计划 |

格式约定：Markdown正文、Mermaid数据流、JSON Schema字段定义、Markdown表格；条件激活标注为【X型激活】；技术术语首次出现附通俗解释；状态符号调用`core-symbol-system`。

## 输出结构模板升级（v1.3.0新增）

在原有14必含章节基础上，增加以下标准化输出结构要求：

### 标准输出结构（嵌入各章节）

1. 🎯 **一句话结论**（30字内，核心建议）——置于专家包概览章节开头
2. 📊 **决策矩阵**（当存在多条路径时）
   | 选项 | 优势 | 风险 | 投入 | 推荐优先级 |
   |------|------|------|------|-----------|
3. 🗺️ **行动路线图**
   - **第一步**（本周可启动）：[具体动作]
   - **短期**（1-3月）：[关键里程碑]
   - **中期**（3-12月）：[阶段目标]
4. ⚠️ **关键风险与应对**——嵌入第8章异常处理
5. ❓ **待验证假设与建议咨询方向**——嵌入第5章信息准确性保障
6. 📎 **补充说明**（确定性标注汇总）——嵌入第14章架构健康检查报告

### 避免的输出模式
- ❌ 纯粹的知识科普（不产生可执行动作的信息输出）
- ❌ 没有优先级排序的并列建议
- ❌ 缺乏具体数字/时间/责任人的模糊表述
- ❌ 不给明确定性结论的"可能""也许""可以考虑"堆砌

## 输出溯源与参考指引（v1.3.0新增）

### 关键判断附带参考方向

对于方案中的关键判断，不要求精确引用（避免幻觉），但要给出参考方向：

- 对方法论建议，标注其适用条件和局限
- 对数据/参数，标注来源是"行业通用估值"还是"需实际测算"
- 对法规相关建议，标注"建议查阅：[相关标准/法规/行业报告的名称及发布机构]"

### 溯源标注格式

每条关键判断使用以下格式标注来源：

| 确定性 | 标注格式 | 示例 |
|--------|---------|------|
| 🟢 高确信 | 【行业惯例】 | "根据SAFe框架的PI Planning机制，建议..." |
| 🟡 中确信 | 【基于推理】 | "基于类似规模的SaaS产品经验，推测..." |
| 🔴 低确信 | 【需核实】 | "建议查阅：《个人信息保护法》最新修订版" |

### 限制条件

- 不要求精确引用具体条文编号（避免LLM幻觉输出错误条文）
- 对"最新政策""最新法规"类建议，必须标注"请核实最新版本"
- 对数据来源的标注区分"公开可查"和"需付费获取"

## 详细执行逻辑

```text
FUNCTION execute_constraint_output_format(input):
    ASSERT input matches input_schema
    ASSERT input.target_check != NULL AND LEN(input.target_check) > 0
    violations = []
    suggestions = []
    context = input.context IF input.context != NULL ELSE {}

    // 加载14必含章节清单(改进#27修复：与S7的REQUIRED_CHAPTERS统一)
    required_chapters = [
        "专家包概览",
        "角色定义（各专家详细配置）",
        "协作模型（Team型/Agent型协作协议）",
        "SOP编排（阶段定义/触发条件/数据流）",
        "数据流设计（Mermaid总图）",
        "反馈闭环",
        "质量门控协议",
        "合规协议（4.1-4.5条件激活）",
        "数据安全协议",
        "异常处理",
        "知识资产沉淀",
        "工具链配置（工具矩阵+集成规范+降级方案）",
        "冷启动策略",
        "执行计划"
    ]
    ASSERT LEN(required_chapters) == 14

    // 阶段1: 14必含章节完整性检查
    present_chapters = EXTRACT_CHAPTERS(input.target_check)
    missing_chapters = []
    FOR i FROM 0 TO 13:
        IF NOT CONTAINS(present_chapters, required_chapters[i]):
            APPEND missing_chapters, required_chapters[i]
            APPEND violations, {
                "missing_chapter": required_chapters[i],
                "detail": "方案缺少第" + STRING(i+1) + "章: " + required_chapters[i]
            }

    // 阶段2: 条件激活标注检查
    // 内容合规保障章节必须标注【X型激活】
    compliance_chapter = FIND_CHAPTER(input.target_check, "内容合规保障")
    IF compliance_chapter != NULL:
        domain = context.domain_type IF context.domain_type != NULL ELSE "A"
        activation_label = "【" + domain + "型激活】"
        IF NOT CONTAINS(compliance_chapter, activation_label):
            APPEND violations, {
                "rule": "条件激活标注",
                "detail": "内容合规保障章节缺少" + activation_label + "标识",
                "fix": "在章节开头添加" + activation_label + "条件激活标注"
            }
        // 其他章节的条件激活标注检查
        conditional_chapters = IDENTIFY_CONDITIONAL_CHAPTERS(input.target_check)
        FOR EACH cc IN conditional_chapters:
            IF NOT HAS_ACTIVATION_LABEL(cc.content):
                APPEND violations, {"rule": "条件激活标注", "detail": cc.name + "缺少条件激活标注"}

    // 阶段3: 格式约定校验
    // 3a: Markdown格式检查
    IF NOT IS_MARKDOWN_FORMAT(input.target_check):
        APPEND violations, {"rule": "格式约定", "detail": "方案文档应使用Markdown格式"}

    // 3b: 数据流总图必须使用Mermaid
    dataflow_chapter = FIND_CHAPTER(input.target_check, "数据流总图")
    IF dataflow_chapter != NULL:
        IF NOT CONTAINS_MERMAID(dataflow_chapter):
            APPEND violations, {
                "rule": "格式约定-Mermaid",
                "detail": "数据流总图应使用Mermaid graph TD语法绘制",
                "fix": "使用Mermaid graph TD语法绘制S3→S5→S6→S7→S8完整数据流"
            }

    // 3c: Schema定义必须使用JSON
    schema_sections = FIND_SCHEMA_SECTIONS(input.target_check)
    FOR EACH ss IN schema_sections:
        IF NOT IS_JSON_SCHEMA(ss.content):
            APPEND violations, {
                "rule": "格式约定-JSON Schema",
                "detail": ss.name + "的Schema定义应使用JSON格式",
                "fix": "将配置转为JSON Schema格式,标注必填/可选字段"
            }

    // 3d: 表格必须Markdown格式
    tables = FIND_TABLES(input.target_check)
    FOR EACH t IN tables:
        IF NOT IS_MARKDOWN_TABLE(t):
            APPEND violations, {"rule": "格式约定-表格", "detail": "表格应使用Markdown格式"}

    // 阶段4: 术语翻译检查
    jargon_list = FIND_UNTRANSLATED_JARGON(input.target_check)
    IF LEN(jargon_list) > 0:
        APPEND violations, {
            "rule": "术语翻译强制",
            "detail": "以下技术术语首次出现未附通俗解释: " + JOIN(jargon_list)
        }

    // 阶段5: 状态符号调用检查
    IF NOT USES_CORE_SYMBOL_SYSTEM(input.target_check):
        APPEND suggestions, "建议调用core-symbol-system统一状态符号"

    // 汇总结果
    compliant = (LEN(violations) == 0)
    chapters_present = LEN(present_chapters)
    chapters_required = 14

    IF compliant:
        APPEND suggestions, "14必含章节完整+格式规范校验通过"
    ELSE:
        FOR EACH v IN violations:
            IF v.fix != NULL:
                APPEND suggestions, v.fix

    RETURN {
        "compliant": compliant,
        "violations": violations,
        "suggestions": suggestions,
        "chapters_present": chapters_present,
        "chapters_required": chapters_required
    }
```

## 版本

1.3.0

---
*本Skill由全域专家团构建skills体系生成，版本1.3.0，日期2026-06-16*
