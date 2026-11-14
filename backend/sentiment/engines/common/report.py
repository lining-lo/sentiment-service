from pathlib import Path
from sentiment.engines.contract.agent_role import RoleKey
from sentiment.engines.contract.settings import get_settings


def get_report_dir(task_id: str, role: RoleKey) -> str:
    return str(Path(get_settings().RUNTIME_DIR) / f"{task_id}" / f"{role}")


def save_report(
        output_dir: str | Path,
        filename: str,
        content: str
) -> Path:
    """使用明确文件名将报告内容写入指定目录"""
    path = Path(output_dir) / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path
