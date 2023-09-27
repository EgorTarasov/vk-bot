import abc
from typing import Type, Dict, Any


class BaseStateStorage(abc.ABC):
    @abc.abstractmethod
    def __init__(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def get_state(self, user_id: int) -> Type[Dict[str, Any]]:
        raise NotImplementedError

    @abc.abstractmethod
    def set_state(self, user_id: int, state: Dict[str, Any]) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def close(self) -> None:
        raise NotImplementedError
