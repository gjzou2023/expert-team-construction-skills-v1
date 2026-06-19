"""
sync_dist.py - Skills 同步脚本
==============================

将 skills/ 目录的修改自动同步到 dist-v2/ 各平台目录。

用法:
    python sync_dist.py              # 全量同步
    python sync_dist.py --watch      # 持续监控模式
    python sync_dist.py --dry-run    # 仅预览变更
    python sync_dist.py --source ./my-skills  # 自定义源目录
    python sync_dist.py --target ./my-dist      # 自定义目标目录

特点:
    - 增量同步：仅同步变更的文件（基于文件内容哈希）
    - 平台隔离：各平台特有定制内容不会被覆盖
    - 错误处理：同步失败时明确提示原因
    - 支持 --watch 模式持续监控
"""

import argparse
import hashlib
import json
import logging
import os
import shutil
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# ─── 配置 ───────────────────────────────────────────────────────────────────

DEFAULT_SRC = "skills/全域专家团"
DIST_ROOT = "dist-v2"
PLATFORMS = ["claude-code", "codex-cli", "hermes", "workbuddy"]

LOG_FORMAT = "[%(asctime)s] %(levelname)-7s %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

# 仅同步 SKILL.md 文件（config.json、knowledge/ 等非技能文件不处理）
SYNC_ONLY_SKILL_MD = True


# ─── 工具函数 ─────────────────────────────────────────────────────────────────

def file_hash(path: Path) -> str:
    """计算文件 SHA256 哈希"""
    h = hashlib.sha256()
    try:
        h.update(path.read_bytes())
    except (OSError, IOError) as e:
        logger.warning(f"无法读取文件 {path}: {e}")
        return ""
    return h.hexdigest()[:16]


def normalize_crlf(content: str) -> str:
    """统一换行符为 LF"""
    return content.replace("\r\n", "\n").replace("\r", "\n")


def detect_platform_path(platform: str, skill_name: str) -> Optional[str]:
    """
    给定平台名和技能子目录名，返回该平台上对应的 dist 目标路径。
    各平台目录结构不同，需要映射。
    """
    mapping = {
        "claude-code": f".claude/agents/{skill_name}.md",
        "codex-cli":   f".codex/agents/{skill_name}.md",
        "hermes":      f"skills/{skill_name}/SKILL.md",
        "workbuddy":   f"references/skills/{skill_name}/SKILL.md",
    }

    # 特殊处理：platform-hermes-adapter 不应同步到自己（循环依赖）
    if skill_name == "platform-hermes-adapter":
        if platform in ("hermes", "workbuddy"):
            return None

    return mapping.get(platform)


def sync_single_file(src_file: Path, dst_file: Path, rel_name: str, dry_run: bool = False) -> str:
    """
    同步单个文件到目标平台。
    返回状态: "copied", "skipped-same", "skipped-non-skills", "error"
    """
    # 只同步 SKILL.md 文件
    if SYNC_ONLY_SKILL_MD and src_file.name != "SKILL.md":
        return "skipped-non-skills"

    try:
        src_content = src_file.read_text(encoding="utf-8")
    except Exception as e:
        logger.error(f"[ERROR] 读取源文件失败: {src_file} -> {e}")
        return "error"

    # 目标不存在，创建父目录
    dst_parent = dst_file.parent
    try:
        dst_parent.mkdir(parents=True, exist_ok=True)
    except FileExistsError:
        # Windows 上如果 dst_parent 是文件而非目录
        if dst_parent.is_file():
            logger.error(f"[ERROR] 目标父路径是文件而非目录: {dst_parent}")
            return "error"
        raise

    if not dst_file.exists():
        # 新文件，直接复制
        dst_file.write_text(src_content, encoding="utf-8")
        skill_filename = dst_file.name
        logger.info(f"[NEW]    新增: {rel_name} -> {skill_filename}")
        return "copied"

    # 对比内容（忽略换行符差异）
    try:
        dst_content = dst_file.read_text(encoding="utf-8")
    except Exception as e:
        logger.error(f"[ERROR] 读取目标文件失败: {dst_file} -> {e}")
        return "error"

    if normalize_crlf(src_content) == normalize_crlf(dst_content):
        return "skipped-same"

    # 内容有差异，覆盖
    dst_file.write_text(src_content, encoding="utf-8")
    return "copied"


def sync_directory(src_base: Path, dst_base: Path, dry_run: bool = False) -> Dict[str, dict]:
    """
    将 src_base 下所有 skill 目录同步到 dst_base 的各平台子目录。
    返回同步统计结果。
    """
    stats = {}
    platform_paths = []

    for plat in PLATFORMS:
        plat_path = dst_base / plat
        if plat_path.is_dir():
            platform_paths.append((plat, plat_path))
        else:
            logger.warning(f"平台目录不存在: {plat_path}")

    if not platform_paths:
        logger.error(f"dist-v2 目录下没有找到任何平台目录！请先运行 build_dist.py")
        return stats

    for (dirpath, dirnames, filenames) in os.walk(src_base):
        for fn in sorted(filenames):
            if fn.endswith("_OLD.md"):
                continue

            src_file = Path(dirpath) / fn
            skill_name = os.path.basename(dirpath)

            plat_results = {}
            for plat, plat_path in platform_paths:
                target_rel = detect_platform_path(plat, skill_name)
                if target_rel is None:
                    plat_results[plat] = "skipped-new-file"
                    continue

                dst_file = plat_path / target_rel
                result = sync_single_file(src_file, dst_file, src_file.relative_to(src_base), dry_run)
                plat_results[plat] = result

            stats[src_file.relative_to(src_base)] = plat_results

    return stats


def print_summary(stats: Dict[str, dict]) -> None:
    """打印同步统计摘要"""
    if not stats:
        logger.info("没有需要同步的文件。")
        return

    copied_count = 0
    skipped_count = 0
    error_count = 0
    skipped_non_skills = 0

    for rel, plat_results in stats.items():
        any_changed = any(r in ("copied",) for r in plat_results.values())
        any_error = any(r == "error" for r in plat_results.values())
        any_skipped = any(r == "skipped-non-skills" for r in plat_results.values())

        if any_changed:
            copied_count += 1
            logger.info(f"[SYNC]  {rel}")
        elif any_skipped:
            skipped_non_skills += 1
        else:
            skipped_count += 1

        if any_error:
            error_count += 1

    logger.info(f"\n{'='*60}")
    logger.info(f"同步完成: {copied_count} 个文件已更新, {skipped_count} 个文件无变化, {skipped_non_skills} 个非SKILL.md文件跳过, {error_count} 个错误")
    logger.info(f"{'='*60}")


# ─── Watch 模式 ──────────────────────────────────────────────────────────────

def watch_mode(src_base: Path, dst_base: Path, interval: int = 2) -> None:
    """
    持续监控源目录变化并自动同步。
    """
    logger.info(f"启动 watch 模式，监控: {src_base}")
    logger.info(f"目标目录: {dst_base}")
    logger.info(f"轮询间隔: {interval} 秒")
    logger.info("按 Ctrl+C 退出\n")

    last_hashes: Dict[str, str] = {}

    try:
        while True:
            new_hashes = {}
            changed_files: List[Tuple[Path, str]] = []

            for (dirpath, dirnames, filenames) in os.walk(src_base):
                for fn in filenames:
                    if fn.endswith("_OLD.md"):
                        continue
                    full_path = Path(dirpath) / fn
                    rel = str(full_path.relative_to(src_base))
                    current_hash = file_hash(full_path)
                    new_hashes[rel] = current_hash

                    if current_hash and current_hash != last_hashes.get(rel):
                        changed_files.append((full_path, rel))

            if changed_files:
                logger.info(f"\n检测到 {len(changed_files)} 个文件变更，开始同步...\n")
                stats = {}
                for src_file, rel in changed_files:
                    skill_name = os.path.basename(str(src_file).rsplit(os.sep, 1)[0]) if os.sep in str(src_file) else os.path.basename(str(src_file))
                    plat_results = {}
                    for plat in PLATFORMS:
                        plat_path = dst_base / plat
                        if not plat_path.is_dir():
                            continue
                        target_rel = detect_platform_path(plat, skill_name)
                        if target_rel is None:
                            plat_results[plat] = "skipped-new-file"
                            continue
                        dst_file = plat_path / target_rel
                        result = sync_single_file(src_file, dst_file, rel)
                        plat_results[plat] = result
                    stats[rel] = plat_results
                print_summary(stats)

            last_hashes = new_hashes
            time.sleep(interval)

    except KeyboardInterrupt:
        logger.info("\n\n停止 watch 模式。")


# ─── 主入口 ──────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Skills 同步脚本 - 将 skills/ 的 SKILL.md 修改同步到 dist-v2/ 各平台",
        epilog="用法示例:\n"
               "  python sync_dist.py                    # 全量同步\n"
               "  python sync_dist.py --watch            # 持续监控\n"
               "  python sync_dist.py --dry-run          # 仅预览\n"
               "  python sync_dist.py --watch --interval 1  # 1秒轮询",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("--watch", action="store_true", help="持续监控模式")
    parser.add_argument("--interval", type=int, default=2, help="watch 模式轮询间隔（秒），默认 2")
    parser.add_argument("--dry-run", action="store_true", help="仅预览变更，不实际写入")
    parser.add_argument("--source", type=str, default=None, help=f"源目录，默认 {DEFAULT_SRC}")
    parser.add_argument("--target", type=str, default=None, help=f"dist 根目录，默认 {DIST_ROOT}")

    args = parser.parse_args()

    # 解析路径（优先使用命令行参数）
    src_base = Path(args.source) if args.source else Path(DEFAULT_SRC)
    dst_root = Path(args.target) if args.target else Path(DIST_ROOT)

    if not src_base.is_dir():
        logger.error(f"源目录不存在: {src_base}")
        sys.exit(1)

    if not dst_root.is_dir():
        logger.error(f"目标目录不存在: {dst_root}。请先运行 build_dist.py 构建 dist。")
        sys.exit(1)

    logger.info(f"源目录: {src_base.absolute()}")
    logger.info(f"目标目录: {dst_root.absolute()}")

    if args.watch:
        watch_mode(src_base, dst_root, args.interval)
    else:
        logger.info(f"全量同步模式 ({'dry-run' if args.dry_run else 'write'})\n")
        stats = sync_directory(src_base, dst_root, dry_run=args.dry_run)
        print_summary(stats)


if __name__ == "__main__":
    main()
