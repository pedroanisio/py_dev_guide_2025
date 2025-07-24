from dataclasses import dataclass
from enum import Enum

class ModelType(Enum):
    SETTINGS = "Settings"

@dataclass
class PydanticModel:
    name: str
    model_type: ModelType
    description: str
    code: str

models = [
    PydanticModel(
        name="Settings",
        model_type=ModelType.SETTINGS,
        description="Application settings with environment variable loading",
        code="""
import os
# ...
"""
    )
] 