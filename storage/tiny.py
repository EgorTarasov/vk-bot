from typing import Any, Dict, Type
from tinydb import TinyDB, Query, operations

from .base import BaseStateStorage
import typing


class TinyStateStorage(BaseStateStorage):
    def __init__(self, db_path: str = "db.json"):
        self.db = TinyDB(db_path)
        self.User = Query()

    def get_state(self, user_id: int) -> dict[str, typing.Any]:
        state = self.db.search(self.User.id == user_id)
        if state:
            return state[0]
        else:
            self.db.insert({"id": user_id, "name": "menu"})
            return {"name": "menu"}

    def set_state(self, user_id: int, state: Dict[str, Any]) -> None:
        state["id"] = user_id
        self.db.update(state, self.User.id == user_id)

    def close(self) -> None:
        self.db.close()
