from pathlib import Path

from sentiment.engines.contract.agent_role import RoleKey
from sentiment.engines.contract.settings import get_settings


# 获取输出目录
def get_report_dir(task_id: str, role: RoleKey) -> str:
    return str(Path(get_settings().RUNTIME_DIR / f"{task_id}" / f"{role}"))
