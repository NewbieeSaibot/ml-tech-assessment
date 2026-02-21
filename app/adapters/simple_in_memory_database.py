from typing import Dict, Generic, TypeVar
from uuid import uuid4

from app.models.database import DBStatus, StoreStatus, LoadStatus
from app.ports.in_memory_database import InMemoryDatabase


T = TypeVar("T")


class SimpleInMemoryDatabase(InMemoryDatabase[T], Generic[T]):
    """
    A simple example just for the assessment. This can break due concurrency issues.
    A better approach would be use a Redis Adapter.
    """

    def __init__(self):
        self._storage: Dict[str, T] = {}

    def store(self, obj: T) -> StoreStatus:
        try:
            object_id = str(uuid4())
            self._storage[object_id] = obj

            return StoreStatus(
                object_id=object_id,
                status=DBStatus.SUCCESS,
            )

        except Exception as e:
            return StoreStatus(
                object_id="",
                status=DBStatus.ERROR,
                message=str(e),
            )

    def load(self, object_id: str) -> LoadStatus[T]:
        try:
            if object_id not in self._storage:
                return LoadStatus(
                    object_id=object_id,
                    status=DBStatus.NOT_FOUND,
                    data=None,
                    message="Object not found",
                )

            return LoadStatus(
                object_id=object_id,
                status=DBStatus.SUCCESS,
                data=self._storage[object_id],
            )

        except Exception as e:
            return LoadStatus(
                object_id=object_id,
                status=DBStatus.ERROR,
                data=None,
                message=str(e),
            )
