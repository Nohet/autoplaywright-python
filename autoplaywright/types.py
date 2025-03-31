from typing import TypeVar
from pydantic import BaseModel

PydanticModel = TypeVar("PydanticModel", bound=BaseModel)
