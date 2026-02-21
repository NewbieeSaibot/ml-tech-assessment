from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from app.models.database import StoreStatus, LoadStatus


T = TypeVar("T")


class InMemoryDatabase(ABC, Generic[T]):
    @abstractmethod
    def store(self, obj: T) -> StoreStatus:
        pass

    @abstractmethod
    def load(self, object_id: str) -> LoadStatus[T]:
        pass
