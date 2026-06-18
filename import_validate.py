#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全域专家团构建skills v1.1.0 — 导入校验脚本
验证字段完整性、结构正确性、关键依赖、few-shot质量和依赖DAG。
"""

import json
import os
import sys
from pathlib import Path

# G-1修复: 确保Windows GBK终端下也能正常输出emoji和中文
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

EXPECTED_SKILL_COUNT = 40  # v1.5.0: 新增 team-orchestrator 后从 39 改为 40

REQUIRED_FIELDS = [
    "trigger_keywords",
    "input_schema",
    "output_schema",
    "tool_declarations",
    "few_shot_examples",
    "knowledge_base_mount_points",
    "version",
    "dependencies",
]

PROTOCOL_FIELDS = [
    "cascading_calls",
    "context_inheritance",
    "shared_memory_keys",
]

REQUIRED_S5_DEPS = {
    "core-mental-model-engine",
    "core-deliverable-backward-engine",
    "protocol-quality-gate",
    "protocol-feedback-loop",
    "protocol-compliance-engine",
}

# 改进#9修复: S7从18项硬编码依赖改为2项核心依赖+条件激活校验
REQUIRED_S7_DEPS = {
    "core-mental-model-engine",
    "core-deliverable-backward-engine",
}

PLACEHOLDER_PHRASES = ["典型用户消息", "执行完成"]


def load_config(config_json, skill_id, errors):
    try:
        with open(config_json, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"[{skill_id}] config.json JSON解析失败: {e}")
    return None


def validate_few_shots(skill_id, config, warnings):
    examples = config.get("few_shot_examples", [])
    if len(examples) < 3:
        warnings.append(f"[{skill_id}] few_shot_examples少于3个")
    serialized = json.dumps(examples, ensure_ascii=False)
    if any(phrase in serialized for phrase in PLACEHOLDER_PHRASES):
        warnings.append(f"[{skill_id}] few_shot_examples疑似仍含占位示例")
    if "小红书" not in serialized and "医疗" not in serialized and "客服" not in serialized:
        warnings.append(f"[{skill_id}] few_shot_examples缺少实际业务数据")


def validate_mount_points(skill_id, config, warnings):
    mount_points = config.get("knowledge_base_mount_points", [])
    types = {item.get("type") for item in mount_points if isinstance(item, dict)}
    # G-4修复: static/dynamic为必选，rag按层级差异化要求
    for required_type in ["static", "dynamic"]:
        if required_type not in types:
            warnings.append(f"[{skill_id}] knowledge_base_mount_points缺少{required_type}类型")
    # L0/L1建议有rag，L2/L3/L4不强制
    layer = config.get("layer", "")
    if "rag" not in types and layer in ["L0", "L1"]:
        warnings.append(f"[{skill_id}] L0/L1层级建议补充rag类型挂载点")
    for item in mount_points:
        path = item.get("path", "") if isinstance(item, dict) else ""
        if path.endswith("/") or path in ["file://pipeline", "file://constraints"]:
            warnings.append(f"[{skill_id}] knowledge_base_mount_points疑似截断: {path}")


def validate_skill(skill_dir, all_skill_ids):
    errors = []
    warnings = []
    skill_id = os.path.basename(skill_dir)

    skill_md = os.path.join(skill_dir, "SKILL.md")
    if not os.path.exists(skill_md):
        errors.append(f"[{skill_id}] SKILL.md 不存在")
        return errors, warnings, None

    config_json = os.path.join(skill_dir, "config.json")
    if not os.path.exists(config_json):
        errors.append(f"[{skill_id}] config.json 不存在")
        return errors, warnings, None

    config = load_config(config_json, skill_id, errors)
    if config is None:
        return errors, warnings, None

    with open(skill_md, "r", encoding="utf-8") as f:
        skill_md_text = f.read()
    if "## 详细执行逻辑" not in skill_md_text:
        warnings.append(f"[{skill_id}] SKILL.md缺少详细执行逻辑章节")

    for field in REQUIRED_FIELDS:
        if field not in config:
            errors.append(f"[{skill_id}] 缺少必填字段: {field}")
        elif config[field] is None or config[field] == "" or config[field] == []:
            if field not in ["tool_declarations", "dependencies"]:
                warnings.append(f"[{skill_id}] 字段为空: {field}")

    for field in PROTOCOL_FIELDS:
        if field not in config:
            warnings.append(f"[{skill_id}] 缺少协议字段: {field}")

    proto = config.get("protocol")
    if not proto:
        warnings.append(f"[{skill_id}] 缺少protocol配置对象")
    else:
        for key in ["cascading_enabled", "context_inheritance_enabled", "shared_memory_enabled", "mandatory_calls"]:
            if key not in proto:
                warnings.append(f"[{skill_id}] protocol缺少字段: {key}")

    for dep in config.get("dependencies", []):
        if dep not in all_skill_ids:
            errors.append(f"[{skill_id}] 依赖的Skill不存在: {dep}")

    validate_few_shots(skill_id, config, warnings)
    validate_mount_points(skill_id, config, warnings)

    if skill_id.startswith("pipeline-") and "stage_guard" not in config:
        warnings.append(f"[{skill_id}] pipeline Skill缺少stage_guard")

    if skill_id == "pipeline-s5-architecture-design":
        missing = REQUIRED_S5_DEPS - set(config.get("dependencies", []))
        if missing:
            errors.append(f"[{skill_id}] S5关键依赖缺失: {sorted(missing)}")

    if skill_id == "pipeline-s7-expert-package-generation":
        # 改进#9修复: 仅校验2项核心依赖，条件依赖通过conditional_dependencies字段声明
        missing = REQUIRED_S7_DEPS - set(config.get("dependencies", []))
        if missing:
            errors.append(f"[{skill_id}] S7核心依赖缺失: {sorted(missing)}")
        if "conditional_dependencies" not in config:
            warnings.append(f"[{skill_id}] S7缺少conditional_dependencies声明")

    if skill_id == "platform-workbuddy-adapter" and config.get("description", "").strip().endswith("Agent I"):
        errors.append(f"[{skill_id}] description仍存在截断文本'Agent I'")

    return errors, warnings, config


def detect_cycles(graph):
    visited = set()
    visiting = set()
    cycles = []

    def dfs(node, path):
        if node in visiting:
            cycle_start = path.index(node)
            cycles.append(path[cycle_start:] + [node])
            return
        if node in visited:
            return
        visiting.add(node)
        for dep in graph.get(node, []):
            if dep in graph:
                dfs(dep, path + [dep])
        visiting.remove(node)
        visited.add(node)

    for node in graph:
        dfs(node, [node])
    return cycles


def validate_config_skill_consistency(skill_dir, all_skill_ids):
    """校验config.json与SKILL.md的一致性"""
    inconsistencies = []
    for skill_path in Path(skill_dir).rglob('SKILL.md'):
        config_path = skill_path.parent / 'config.json'
        if not config_path.exists():
            continue
        
        skill_id = skill_path.parent.name
        
        # 解析SKILL.md的frontmatter
        skill_meta = parse_frontmatter(skill_path)
        if not skill_meta:
            continue
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 版本号一致性
        if skill_meta.get('version') != config.get('version'):
            inconsistencies.append(f"版本不一致: {skill_id} (SKILL.md: {skill_meta.get('version')} vs config.json: {config.get('version')})")
        
        # 描述一致性
        skill_desc = (skill_meta.get('description', '') or '')[:30]
        config_desc = (config.get('description', '') or '')[:30]
        if skill_desc and config_desc and skill_desc != config_desc:
            inconsistencies.append(f"描述不一致: {skill_id}")
        
        # ID一致性
        if skill_meta.get('id') != config.get('id'):
            inconsistencies.append(f"ID不一致: {skill_id} (SKILL.md: {skill_meta.get('id')} vs config.json: {config.get('id')})")
    
    return inconsistencies


def parse_frontmatter(skill_md_path):
    """解析SKILL.md的YAML frontmatter（G-3修复：优先使用pyyaml，回退简易解析）"""
    try:
        with open(skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if content.startswith('---'):
            end = content.index('---', 3)
            fm_text = content[3:end].strip()
            # G-3修复：优先使用标准YAML解析器，支持列表/对象/多行字符串
            try:
                import yaml
                return yaml.safe_load(fm_text)
            except ImportError:
                # pyyaml不可用时回退到简易解析
                result = {}
                for line in fm_text.split('\n'):
                    if ':' in line and not line.startswith(' '):
                        key, _, value = line.partition(':')
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        result[key] = value
                return result
    except Exception:
        pass
    return None


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skills_dir = os.path.join(script_dir, "skills", "全域专家团")

    if not os.path.exists(skills_dir):
        print(f"❌ Skills目录不存在: {skills_dir}")
        sys.exit(1)

    skill_dirs = [
        os.path.join(skills_dir, d)
        for d in os.listdir(skills_dir)
        if os.path.isdir(os.path.join(skills_dir, d)) and d != "knowledge"
    ]
    all_skill_ids = {os.path.basename(path) for path in skill_dirs}

    print("\n📋 全域专家团构建skills 导入校验")
    print("═══════════════════════════════════════")
    print(f"Skills目录: {skills_dir}")
    print(f"发现Skill数量: {len(skill_dirs)}")
    print("═══════════════════════════════════════\n")

    all_errors = []
    all_warnings = []
    configs = {}

    if len(skill_dirs) != EXPECTED_SKILL_COUNT:
        all_errors.append(f"Skill数量应为{EXPECTED_SKILL_COUNT}，实际为{len(skill_dirs)}")

    for skill_dir in sorted(skill_dirs):
        skill_id = os.path.basename(skill_dir)
        errors, warnings, config = validate_skill(skill_dir, all_skill_ids)
        if config:
            configs[skill_id] = config
        all_errors.extend(errors)
        all_warnings.extend(warnings)
        status = "✅" if not errors else "❌"
        warn_str = f" ({len(warnings)}个警告)" if warnings else ""
        print(f"  {status} {skill_id}{warn_str}")

    graph = {skill_id: cfg.get("dependencies", []) for skill_id, cfg in configs.items()}
    cycles = detect_cycles(graph)
    for cycle in cycles:
        all_errors.append("检测到循环依赖: " + " -> ".join(cycle))

    # 改进#8修复: activation_map.json已合并到knowledge/protocol-activation-map.json
    # 文件实际位于 skills/全域专家团/knowledge/ 下，manifest.json中activation_map_file指向正确路径
    activation_map_path = os.path.join(skills_dir, "knowledge", "protocol-activation-map.json")
    if not os.path.exists(activation_map_path):
        all_errors.append("缺少文件: skills/全域专家团/knowledge/protocol-activation-map.json")
    if not os.path.exists(os.path.join(script_dir, "compatibility_matrix.json")):
        all_errors.append("缺少根目录文件: compatibility_matrix.json")

    # P3-3: config.json与SKILL.md一致性校验
    config_inconsistencies = validate_config_skill_consistency(skills_dir, all_skill_ids)
    for inc in config_inconsistencies:
        all_warnings.append(inc)

    print("\n═══════════════════════════════════════")
    print(f"校验完成：{len(skill_dirs)}个Skill")
    print(f"错误：{len(all_errors)}个")
    print(f"警告：{len(all_warnings)}个")

    if all_errors:
        print("\n❌ 错误列表：")
        for error in all_errors:
            print(f"  - {error}")

    if all_warnings:
        print("\n⚠️ 警告列表：")
        for warning in all_warnings:
            print(f"  - {warning}")

    if not all_errors:
        print("\n✅ 全部校验通过！Skills可正常导入使用。")
        sys.exit(0)

    print("\n❌ 存在阻塞性错误，请修复后重新校验。")
    sys.exit(1)


if __name__ == "__main__":
    main()
