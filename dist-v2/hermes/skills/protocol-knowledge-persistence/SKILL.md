---
name: protocol-knowledge-persistence
description: 设计决策沉淀到§5.5，执行细节沉淀到§7.3，多模态资产管理(参数快照)。版本迁移指南。 Use when: 用户说"protocol-knowledge-persistence、知识沉淀协议、L2沉淀"等触发词。
version: 1.1.0
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [l2]
    related_skills: []
    requires_toolsets: []
---

> **注意**：本 skill 的核心规则已内联至 `team-orchestrator/SKILL.md` 的 `L2` 章节。
> 执行时优先读取 team-orchestrator 的内联指引，仅在需要完整逻辑时再读取本文件。
>
# 知识资产沉淀协议

> **层级**: L2 | **版本**: 1.1.0 | **ID**: `protocol-knowledge-persistence` | **中文名**: 知识资产沉淀协议 | **英文名**: Knowledge Persistence Protocol
# 知识资产沉淀协议 (Knowledge Persistence Protocol)

> **层级**: L2 | **版本**: 1.0.0 | **ID**: `protocol-knowledge-persistence`
> **编排关系**: 本skill由 `team-orchestrator` 按需自动加载执行，属于全域专家团构建skills系统的内部组件，用户不应直接触发。

## 概述

设计决策沉淀到§5.5，执行细节沉淀到§7.3，多模态资产管理(参数快照)。版本迁移指南。

## 触发条件

当检测到以下关键词或场景时自动激活：知识沉淀, 保存, 版本, 参数快照, 多模态资产

## 输入规范 (input_schema)

```json
{
  "type": "object",
  "properties": {
    "decision_type": {
      "type": "string",
      "enum": [
        "design",
        "execution",
        "parameter_change"
      ]
    },
    "content": {
      "type": "object"
    },
    "metadata": {
      "type": "object",
      "properties": {
        "stage": {
          "type": "string"
        },
        "role": {
          "type": "string"
        },
        "timestamp": {
          "type": "string"
        }
      }
    }
  },
  "required": [
    "decision_type",
    "content",
    "metadata"
  ]
}
```

## 输出规范 (output_schema)

```json
{
  "type": "object",
  "properties": {
    "persisted": {
      "type": "boolean"
    },
    "storage_location": {
      "type": "string",
      "enum": [
        "section_5.5",
        "section_7.3"
      ]
    },
    "asset_type": {
      "type": "string",
      "enum": [
        "text",
        "config",
        "parameter_snapshot",
        "multimodal"
      ]
    },
    "version": {
      "type": "string"
    }
  },
  "required": [
    "persisted",
    "storage_location",
    "asset_type",
    "version"
  ]
}
```

## 工具声明 (tool_declarations)

本Skill无外部工具依赖，纯提示词可执行。

## 执行逻辑

(1)设计决策沉淀到§5.5:架构决策、角色定义、SOP设计依据→(2)执行细节沉淀到§7.3:工具配置、提示词、数据映射→(3)多模态资产管理:参数快照(生成参数+模型版本+种子值+提示词)→(4)版本迁移指南。多模态资产(5.5修订)：AI生成的图片/视频/音频:必须保存生成参数(模型版本+种子值+提示词+参数),而非仅保存产出文件。

## Few-shot 示例

### 示例 1：正常流程 — 设计决策沉淀到§5.5

**输入**:
```json
{
  "decision_type": "design",
  "content": {
    "title": "内容创作团队角色拆分决策",
    "rationale": "经MECE分析，原'全栈创作者'角色覆盖选题、文案、视觉三个职责，独立性不足",
    "decision": "拆分为内容策略师(选题+日历)、文案师(文案+标题)、视觉设计师(配图+封面)",
    "alternatives_considered": ["保持单一角色(已否决:独立性不足)", "拆分为5个角色(已否决:超出快速通道能力)"]
  },
  "metadata": {
    "stage": "5",
    "role": "架构师",
    "timestamp": "2026-06-15T10:00:00Z"
  }
}
```

**输出**:
```json
{
  "persisted": true,
  "storage_location": "section_5.5",
  "asset_type": "text",
  "version": "1.0.0"
}
```

### 示例 2：异常流程 — 多模态资产参数快照完整保存

**输入**:
```json
{
  "decision_type": "parameter_change",
  "content": {
    "asset_type": "image",
    "model": "comfyui",
    "model_version": "SDXL-1.0",
    "seed": 42,
    "prompt": "美食封面图,暖色调,俯拍角度,自然光",
    "negative_prompt": "文字,水印,低画质",
    "parameters": { "steps": 30, "cfg_scale": 7.5, "sampler": "DPM++ 2M Karras", "width": 1024, "height": 1024 },
    "post_processing": "Lightroom调色预设v3"
  },
  "metadata": {
    "stage": "6",
    "role": "visual-designer",
    "timestamp": "2026-06-15T10:00:00Z"
  }
}
```

**输出**:
```json
{
  "persisted": true,
  "storage_location": "section_7.3",
  "asset_type": "parameter_snapshot",
  "version": "1.0.0",
  "warning": "注意：仅保存参数快照而非仅保存产出文件。如需复现，使用相同模型版本+种子+提示词即可。"
}
```

### 示例 3：快速通道 — 执行细节最小沉淀

**输入**:
```json
{
  "decision_type": "execution",
  "content": {
    "type": "快速通道单人配置",
    "tools_used": ["WebSearch(静态清单兜底)"],
    "prompt_version": "v1.0-fast"
  },
  "metadata": {
    "stage": "7",
    "role": "主理人",
    "timestamp": "2026-06-15T10:00:00Z"
  },
  "channel": "fast"
}
```

**输出**:
```json
{
  "persisted": true,
  "storage_location": "section_7.3",
  "asset_type": "config",
  "version": "1.0.0-fast",
  "note": "快速通道：仅保存核心配置和关键提示词版本，详细设计决策待后续补充到§5.5"
}
```

## 知识库挂载点 (knowledge_base_mount_points)

- **[static]** `file://knowledge-persistence/multimodal-template` — 多模态资产参数快照模板

## 依赖关系

- `core-mental-model-engine`

## 详细执行逻辑

```text
FUNCTION execute_protocol_knowledge_persistence(input):
    ASSERT input.decision_type IN ["design","execution","parameter_change"]
    ASSERT input.content IS NOT EMPTY
    ASSERT input.metadata.stage IS NOT EMPTY
    ASSERT input.metadata.role IS NOT EMPTY
    ASSERT input.metadata.timestamp IS NOT EMPTY

    // === 第一步：文本资产设计决策沉淀到§5.5 ===
    IF input.decision_type == "design":
        storage_location = "section_5.5"
        asset_type = "text"
        // 设计决策包含：架构决策、角色定义、SOP设计依据
        design_record = {}
        design_record.title = input.content.title
        design_record.rationale = input.content.rationale
        design_record.decision = input.content.decision
        design_record.alternatives_considered = input.content.alternatives_considered
        design_record.stage = input.metadata.stage
        design_record.role = input.metadata.role
        design_record.timestamp = input.metadata.timestamp

        // 检查是否为快速通道最小沉淀
        IF input.channel == "fast":
            design_record.note = "快速通道：仅保存核心配置和关键提示词版本，详细设计决策待后续补充到§5.5"
            asset_type = "config"

        persisted = WRITE_TO_SECTION(storage_location, design_record)
        version = GENERATE_VERSION(input.metadata.stage)

    // === 第二步：执行细节沉淀到§7.3 ===
    ELIF input.decision_type == "execution":
        storage_location = "section_7.3"
        asset_type = "config"
        // 执行细节包含：工具配置、提示词、数据映射
        execution_record = {}
        execution_record.tools_used = input.content.tools_used
        execution_record.prompt_version = input.content.prompt_version
        execution_record.data_mapping = input.content.data_mapping
        execution_record.stage = input.metadata.stage
        execution_record.role = input.metadata.role
        execution_record.timestamp = input.metadata.timestamp

        persisted = WRITE_TO_SECTION(storage_location, execution_record)
        version = GENERATE_VERSION(input.metadata.stage)

    // === 第三步：多模态资产管理(参数快照) ===
    ELIF input.decision_type == "parameter_change":
        storage_location = "section_7.3"
        asset_type = "parameter_snapshot"

        // 参数快照必须包含完整生成参数
        snapshot = {}
        snapshot.asset_type = input.content.asset_type  // image/video/audio
        snapshot.model = input.content.model
        snapshot.model_version = input.content.model_version
        snapshot.seed = input.content.seed
        snapshot.prompt = input.content.prompt
        snapshot.negative_prompt = input.content.negative_prompt
        snapshot.parameters = input.content.parameters  // steps, cfg_scale, sampler, width, height等
        snapshot.post_processing = input.content.post_processing
        snapshot.stage = input.metadata.stage
        snapshot.role = input.metadata.role
        snapshot.timestamp = input.metadata.timestamp

        // 验证参数快照完整性
        ASSERT snapshot.model_version IS NOT EMPTY
        ASSERT snapshot.seed IS NOT NULL
        ASSERT snapshot.prompt IS NOT EMPTY
        ASSERT snapshot.parameters IS NOT EMPTY

        // 存储参数快照(而非仅保存产出文件)
        persisted = WRITE_TO_SECTION(storage_location, snapshot)

        // 索引管理：为多模态资产建立索引
        index_entry = {}
        index_entry.asset_id = COMPUTE_HASH(snapshot)
        index_entry.tags = EXTRACT_TAGS(snapshot.prompt)
        index_entry.generation_model = snapshot.model_version
        index_entry.reproducible = true  // 有完整参数即可复现
        CALL UPDATE_MULTIMODAL_INDEX(index_entry)

        version = GENERATE_VERSION(input.metadata.stage)
        WARN "注意：仅保存参数快照而非仅保存产出文件。如需复现，使用相同模型版本+种子+提示词即可。"

    // === 第四步：多模态资产全生命周期管理 ===
    // 存储：参数快照存入§7.3，设计决策存入§5.5
    // 索引：建立资产索引表(模型版本+种子+标签)
    // 更新：版本变更时标记旧版本为deprecated
    // 失效：模型版本下线时标记不可复现
    // 复用：通过索引表检索可复用资产
    // 命名：{项目ID}_{资产类型}_{版本号}_{时间戳}
    // 生命周期：active → deprecated → archived

    IF persisted:
        // 更新版本迁移指南
        IF EXISTS_PREVIOUS_VERSION(version):
            migration_guide = GENERATE_MIGRATION_GUIDE(previous_version, version)
            APPEND_TO_SECTION("section_7.3", migration_guide)
            MARK_PREVIOUS_AS("deprecated")

    // === 第五步：最终断言与输出 ===
    ASSERT persisted == true OR persisted == false
    ASSERT storage_location IN ["section_5.5","section_7.3"]
    ASSERT asset_type IN ["text","config","parameter_snapshot","multimodal"]
    ASSERT version IS NOT EMPTY

    CALL protocol-quality-gate before final output
    RETURN {persisted, storage_location, asset_type, version}
```

## 版本

1.0.0

---
*本Skill由全域专家团构建skills体系自动生成，版本1.0.0，日期2026-06-15*
