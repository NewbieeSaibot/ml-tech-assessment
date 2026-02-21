from enum import Enum
from pydantic import BaseModel
from typing import Optional, Generic, TypeVar


T = TypeVar("T")


class DBStatus(str, Enum):
    SUCCESS = "success"
    NOT_FOUND = "not_found"
    ERROR = "error"


class StoreStatus(BaseModel):
    object_id: str
    status: DBStatus
    message: Optional[str] = None


class LoadStatus(BaseModel, Generic[T]):
    object_id: str
    status: DBStatus
    data: Optional[T] = None
    message: Optional[str] = None
