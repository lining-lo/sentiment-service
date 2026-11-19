from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class DiscussionRecord:
    task_id: str
    source: str
    message_text: str
    sent_at: str
    dimension_key: str


class DiscussionBuffer:

    def __init__(self):
        """初始化讨论记录缓冲区"""
        self._discuss_records: list[DiscussionRecord] = []

    def append_message(self, data: dict[str, Any]):
        """将一条讨论消息转换并追加到缓冲区"""
        self._discuss_records.append(DiscussionRecord(
            task_id=data.get("task_id"),
            source=data.get("source"),
            message_text=data.get("content"),
            sent_at=datetime.now().strftime("%H:%M:%S"),
            dimension_key=data.get("section_key")
        ))

    def read_messages(self, task_id: str) -> dict[str, Any]:
        """读取指定任务的讨论消息"""
        return {
            "discussion_records": [
                {
                    "task_id": record.task_id,
                    "source": record.source,
                    "message_text": record.message_text,
                    "sent_at": record.sent_at,
                    "dimension_key": record.dimension_key
                }
                for record in self._discuss_records
                if record.task_id == task_id
            ]}
