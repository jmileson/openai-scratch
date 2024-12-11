from enum import StrEnum
from typing import TypedDict, Literal, Protocol, ClassVar
from pydantic import BaseModel as _BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class BaseModel(_BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)


class Context(BaseModel):
    text: str


class Type(StrEnum):
    STR = "string"
    FLOAT = "number"
    INT = "integer"
    BOOL = "boolean"
    NONE = "null"


class Argument(TypedDict):
    type: Type
    description: str


type Property = dict[str, Argument]


class Parameters(BaseModel):
    type: Literal["object"] = "object"
    properties: Property
    required: list[str]
    additional_properties: bool = False


class Function(BaseModel):
    name: str
    description: str
    parameters: Parameters


class Tool(BaseModel):
    type: Literal["function"] = "function"
    function: Function

    def name(self) -> str:
        return self.function.name


class ToolSpec(Protocol):
    TOOL_CONFIG: Tool
