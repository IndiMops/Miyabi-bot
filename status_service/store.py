"""
Small JSON state file: the Discord status message ID and the last heartbeat.

Writes are atomic (temporary file + os.replace), so a crash mid-write cannot
leave a half-written file that would make the service create a duplicate
status message.
"""
import json
import os
import tempfile
import time
from pathlib import Path
from typing import Any

from loguru import logger

STATE_VERSION = 1


class StateStore:
    def __init__(self, path: Path):
        self.path = Path(path)
        self._data: dict[str, Any] = {"version": STATE_VERSION, "message": None, "heartbeats": {}}
        self.last_save_ok = True

    def load(self) -> None:
        if not self.path.exists():
            logger.info(f"No status state file yet at {self.path}")
            return
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(data, dict) or data.get("version") != STATE_VERSION:
                raise ValueError("unsupported state file format")
        except (OSError, ValueError) as error:
            # Keep the broken file for inspection instead of silently overwriting it.
            backup = self.path.with_name(f"{self.path.name}.corrupt-{int(time.time())}")
            try:
                os.replace(self.path, backup)
            except OSError:
                pass
            logger.error(
                f"Could not read status state ({type(error).__name__}); moved it to {backup.name}. "
                "Set STATUS_MESSAGE_ID to reuse the existing Discord message."
            )
            return
        self._data["message"] = data.get("message") if isinstance(data.get("message"), dict) else None
        heartbeats = data.get("heartbeats")
        self._data["heartbeats"] = heartbeats if isinstance(heartbeats, dict) else {}

    def save(self) -> bool:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            fd, tmp_name = tempfile.mkstemp(dir=self.path.parent, prefix=f".{self.path.name}.")
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as file:
                    json.dump(self._data, file, indent=2)
                os.replace(tmp_name, self.path)
            except BaseException:
                if os.path.exists(tmp_name):
                    os.unlink(tmp_name)
                raise
        except OSError as error:
            if self.last_save_ok:
                logger.error(f"Could not save status state to {self.path}: {error}")
            self.last_save_ok = False
            return False
        self.last_save_ok = True
        return True

    def get_message_id(self, webhook_id: int) -> int | None:
        """Return the stored message ID, but only if it belongs to this webhook."""
        message = self._data["message"]
        if not message or message.get("webhook_id") != webhook_id:
            return None
        message_id = message.get("id")
        return message_id if isinstance(message_id, int) else None

    def set_message_id(self, webhook_id: int, message_id: int | None) -> None:
        self._data["message"] = (
            None if message_id is None else {"id": message_id, "webhook_id": webhook_id}
        )

    def get_heartbeat(self, service: str) -> dict[str, Any] | None:
        return self._data["heartbeats"].get(service)

    def set_heartbeat(self, service: str, heartbeat: dict[str, Any]) -> None:
        self._data["heartbeats"][service] = heartbeat
