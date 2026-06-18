
# ComfyUI多模态生成适配器 (ComfyUI Adapter)

> **层级**: L3 | **版本**: 1.0.0 | **ID**: `platform-comfyui-adapter`
> **编排关系**: 本skill由 `team-orchestrator` 按需自动加载执行，属于全域专家团构建skills系统的内部组件，用户不应直接触发。

## 概述

视觉生产引擎：预设映射+SOP扩展(6步)。三档降级：ComfyUI可用→完整自动化;不可用→手动+参数快照;无任何工具→纯描述+占位。

## 触发条件

当检测到以下关键词或场景时自动激活：comfyui, comfyui, 平台适配, 输出格式

## 输入规范 (input_schema)

```json
{
  "type": "object",
  "properties": {
    "architecture": {
      "type": "object",
      "description": "S5架构输出"
    },
    "roles": {
      "type": "array",
      "description": "角色定义列表"
    },
    "sop": {
      "type": "object",
      "description": "SOP定义"
    },
    "expert_type": {
      "type": "string",
      "enum": [
        "team",
        "agent"
      ]
    },
    "track": {
      "type": "string",
      "enum": [
        "fast",
        "standard",
        "strict"
      ]
    }
  },
  "required": [
    "architecture",
    "roles",
    "expert_type"
  ]
}
```

## 输出规范 (output_schema)

```json
{
  "type": "object",
  "properties": {
    "output_format": {
      "type": "string",
      "description": "预设映射配置 + 接口Schema + 视觉角色SOP扩展 + 降级方案"
    },
    "platform_specific_config": {
      "type": "object"
    },
    "degradation_plan": {
      "type": "object"
    }
  },
  "required": [
    "output_format",
    "platform_specific_config"
  ]
}
```

## 工具声明 (tool_declarations)

本Skill无外部工具依赖，纯提示词可执行。

## 执行逻辑

目标平台=ComfyUI多模态生成适配器时激活。输出格式：预设映射配置 + 接口Schema + 视觉角色SOP扩展 + 降级方案。平台特定规则：交付物→预设映射(小红书封面3x4/公众号封面235x1等)。参数快照必须保存：模型版本+种子值+提示词+参数。

## Few-shot 示例

### 示例 1: 多角色视觉团队(完整自动化)

**输入**:
```json
{
  "architecture": {
    "domain_type": "E",
    "platform": "comfyui",
    "comfyui_available": true
  },
  "roles": [
    {"id": "visual-director", "name": "乔雨", "profession": "视觉总监"},
    {"id": "cover-designer", "name": "清墨", "profession": "封面设计师"},
    {"id": "illustrator", "name": "丹青", "profession": "插画师"}
  ],
  "expert_type": "team",
  "track": "standard"
}
```

**输出**:
```json
{
  "output_format": "预设映射配置 + 接口Schema + 视觉角色SOP扩展 + 降级方案",
  "platform_specific_config": {
    "degradation_level": "完整自动化",
    "precondition": "ComfyUI可用→完整自动化链路",
    "preset_mappings": {
      "cover-designer": "小红书封面→1080x1440,公众号封面→900x383",
      "illustrator": "文章配图→1200x800,社交媒体→1080x1080"
    },
    "sop_extension": "6步视觉生产流程:需求拆解→预设匹配→风格定义→生成→质检→输出",
    "parameter_snapshot": "保存模型版本/种子值/提示词/所有参数"
  }
}
```

### 示例 2: ComfyUI不可用降级

**输入**:
```json
{
  "architecture": {
    "domain_type": "E",
    "platform": "comfyui",
    "comfyui_available": false
  },
  "roles": [
    {"id": "cover-designer", "name": "清墨", "profession": "封面设计师"}
  ],
  "expert_type": "agent",
  "track": "standard"
}
```

**输出**:
```json
{
  "status": "degraded",
  "degradation_level": "手动+参数快照",
  "output_format": "预设映射配置 + 手动生成指南 + 参数快照模板",
  "detail": "ComfyUI不可用→输出完整参数快照(模型/种子/提示词/尺寸)，用户可手动在ComfyUI中执行"
}
```

### 示例 3: 无任何视觉工具(纯描述)

**输入**:
```json
{
  "architecture": {
    "domain_type": "E",
    "platform": "comfyui",
    "no_visual_tools": true
  },
  "roles": [
    {"id": "visual-assistant", "name": "安之", "profession": "视觉助理"}
  ],
  "expert_type": "agent",
  "track": "fast"
}
```

**输出**:
```json
{
  "status": "fully_degraded",
  "degradation_level": "纯描述+占位",
  "output_format": "视觉需求描述文档 + 占位图说明",
  "generated_files": [
    "visual_brief.md: 详细描述每个视觉产出物的风格/颜色/构图要求",
    "placeholder_guide.md: 每张图标注尺寸/用途/推荐工具和参数"
  ],
  "degradation_plan": {
    "strategy": "输出详细视觉需求描述供设计师参考,附ComfyUI工作流伪代码"
  }
}
```

## 知识库挂载点 (knowledge_base_mount_points)

- **[static]** `file://platform/platform-comfyui-adapter/format-spec` — ComfyUI多模态生成适配器格式规范

## 依赖关系

- `pipeline-s7-expert-package-generation`

## 详细执行逻辑

```text
FUNCTION execute_platform_comfyui_adapter(input):
    ASSERT input matches input_schema
    ASSERT input.architecture != NULL
    ASSERT input.roles != NULL AND LEN(input.roles) >= 1

    // 阶段1: 合规前置检查
    CALL protocol_compliance_engine(input.architecture.domain_type, input.track)
    IF compliance_result.status == "blocked":
        RETURN {"status": "blocked_or_review", "required_call": "protocol-compliance-engine"}

    // 阶段2: ComfyUI可用性检查→三档降级
    comfyui_available = CHECK_COMFYUI_INSTANCE(input.architecture)
    any_visual_tools = CHECK_ANY_VISUAL_TOOLS(input.architecture)

    IF comfyui_available:
        degradation_level = "full_automation"  // 完整自动化
    ELIF NOT comfyui_available AND any_visual_tools:
        degradation_level = "manual_with_snapshot"  // 手动+参数快照
    ELSE:
        degradation_level = "pure_description"  // 纯描述+占位

    // 阶段3: 预设映射(交付物尺寸映射)
    preset_mappings = {}
    FOR EACH role IN input.roles:
        IF role.is_visual_role:
            presets = []
            // 小红书封面3x4→1080x1440
            IF CONTAINS(role.channels, "xiaohongshu"):
                APPEND presets, {"name": "小红书封面", "width": 1080, "height": 1440, "ratio": "3:4"}
            // 公众号封面2.35:1→900x383
            IF CONTAINS(role.channels, "wechat_article"):
                APPEND presets, {"name": "公众号封面", "width": 900, "height": 383, "ratio": "2.35:1"}
            // 文章配图→1200x800
            IF CONTAINS(role.channels, "article_illustration"):
                APPEND presets, {"name": "文章配图", "width": 1200, "height": 800, "ratio": "3:2"}
            // 社交媒体→1080x1080
            IF CONTAINS(role.channels, "social_square"):
                APPEND presets, {"name": "社交媒体", "width": 1080, "height": 1080, "ratio": "1:1"}
            preset_mappings[role.id] = presets

    // 阶段4: SOP扩展(6步视觉生产流程)
    visual_sop_steps = [
        "需求拆解:分析视觉产出物清单和规格要求",
        "预设匹配:根据渠道选择对应尺寸预设",
        "风格定义:确定色彩/构图/字体风格参数",
        "生成:执行ComfyUI工作流生成视觉资产",
        "质检:校验尺寸/风格一致性/品牌合规",
        "输出:交付最终视觉文件+参数快照"
    ]

    // 阶段5: 参数快照构建(必须保存)
    parameter_snapshots = []
    FOR EACH role IN input.roles:
        IF role.is_visual_role:
            snapshot = {
                "role_id": role.id,
                "model_version": SELECT_MODEL_VERSION(role.profession),
                "seed_value": GENERATE_SEED(),
                "prompt": BUILD_VISUAL_PROMPT(role, input.architecture),
                "parameters": {
                    "width": preset_mappings[role.id][0].width,
                    "height": preset_mappings[role.id][0].height,
                    "cfg_scale": 7.5,
                    "steps": 30,
                    "sampler": "euler_ancestral"
                }
            }
            APPEND parameter_snapshots, snapshot

    // 阶段6: 风格一致性校验
    IF LEN(input.roles) > 1:
        // 多角色需确保风格一致性
        style_consistency = CHECK_STYLE_CONSISTENCY(parameter_snapshots)
        IF NOT style_consistency.consistent:
            RECONCILE_STYLES(parameter_snapshots, style_consistency.conflicts)

    // 阶段7: 按降级级别生成输出
    IF degradation_level == "full_automation":
        // ComfyUI工作流JSON(完整自动化链路)
        comfyui_workflow = BUILD_COMFYUI_WORKFLOW_JSON(preset_mappings, parameter_snapshots)
        output_files = [{"path": "comfyui_workflow.json", "content": comfyui_workflow}]
    ELIF degradation_level == "manual_with_snapshot":
        // 手动生成指南+参数快照模板
        manual_guide = BUILD_MANUAL_GUIDE(preset_mappings, parameter_snapshots)
        snapshot_template = BUILD_SNAPSHOT_TEMPLATE(parameter_snapshots)
        output_files = [
            {"path": "manual_generation_guide.md", "content": manual_guide},
            {"path": "parameter_snapshot_template.json", "content": snapshot_template}
        ]
    ELSE:
        // 纯描述+占位
        visual_brief = BUILD_VISUAL_BRIEF(input.roles, preset_mappings)
        placeholder_guide = BUILD_PLACEHOLDER_GUIDE(preset_mappings, parameter_snapshots)
        output_files = [
            {"path": "visual_brief.md", "content": visual_brief},
            {"path": "placeholder_guide.md", "content": placeholder_guide}
        ]

    // 阶段8: 质量门控
    CALL protocol_quality_gate(output_files, preset_mappings, parameter_snapshots)
    IF quality_gate_result.violations:
        FIX_VIOLATIONS(quality_gate_result.violations)

    output = {
        "output_format": "预设映射配置 + " +
            (degradation_level == "full_automation" ? "ComfyUI工作流JSON" :
             degradation_level == "manual_with_snapshot" ? "手动生成指南+参数快照" :
             "视觉需求描述+占位图说明"),
        "platform_specific_config": {
            "degradation_level": degradation_level,
            "preset_mappings": preset_mappings,
            "parameter_snapshots": parameter_snapshots,
            "sop_extension": visual_sop_steps
        }
    }
    RETURN output
```

## 版本

1.0.0

---
*本Skill由全域专家团构建skills体系自动生成，版本1.0.0，日期2026-06-15*
