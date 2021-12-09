# DO NOT modify this file by hand, changes will be overwritten
import sys
from dataclasses import dataclass
from inspect import getmembers, isclass
from typing import (
    AbstractSet,
    Any,
    Generic,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
    Type,
    TypeVar,
)

from cloudformation_cli_python_lib.interface import (
    BaseModel,
    BaseResourceHandlerRequest,
)
from cloudformation_cli_python_lib.recast import recast_object
from cloudformation_cli_python_lib.utils import deserialize_list

T = TypeVar("T")


def set_or_none(value: Optional[Sequence[T]]) -> Optional[AbstractSet[T]]:
    if value:
        return set(value)
    return None


@dataclass
class ResourceHandlerRequest(BaseResourceHandlerRequest):
    # pylint: disable=invalid-name
    desiredResourceState: Optional["ResourceModel"]
    previousResourceState: Optional["ResourceModel"]
    typeConfiguration: Optional["TypeConfigurationModel"]


@dataclass
class ResourceModel(BaseModel):
    ProjectName: Optional[str]
    EnvironmentVariablesOverride: Optional[Sequence["_EnvironmentVariable"]]
    DebugSessionEnabled: Optional[bool]
    BuildId: Optional[str]
    Arn: Optional[str]
    BuildNumber: Optional[float]
    SessionTarget: Optional[str]

    @classmethod
    def _deserialize(
        cls: Type["_ResourceModel"],
        json_data: Optional[Mapping[str, Any]],
    ) -> Optional["_ResourceModel"]:
        if not json_data:
            return None
        dataclasses = {n: o for n, o in getmembers(sys.modules[__name__]) if isclass(o)}
        recast_object(cls, json_data, dataclasses)
        return cls(
            ProjectName=json_data.get("ProjectName"),
            EnvironmentVariablesOverride=deserialize_list(json_data.get("EnvironmentVariablesOverride"), EnvironmentVariable),
            DebugSessionEnabled=json_data.get("DebugSessionEnabled"),
            BuildId=json_data.get("BuildId"),
            Arn=json_data.get("Arn"),
            BuildNumber=json_data.get("BuildNumber"),
            SessionTarget=json_data.get("SessionTarget"),
        )


# work around possible type aliasing issues when variable has same name as a model
_ResourceModel = ResourceModel


@dataclass
class EnvironmentVariable(BaseModel):
    Value: Optional[str]
    Type: Optional[str]
    Name: Optional[str]

    @classmethod
    def _deserialize(
        cls: Type["_EnvironmentVariable"],
        json_data: Optional[Mapping[str, Any]],
    ) -> Optional["_EnvironmentVariable"]:
        if not json_data:
            return None
        return cls(
            Value=json_data.get("Value"),
            Type=json_data.get("Type"),
            Name=json_data.get("Name"),
        )


# work around possible type aliasing issues when variable has same name as a model
_EnvironmentVariable = EnvironmentVariable


@dataclass
class TypeConfigurationModel(BaseModel):

    @classmethod
    def _deserialize(
        cls: Type["_TypeConfigurationModel"],
        json_data: Optional[Mapping[str, Any]],
    ) -> Optional["_TypeConfigurationModel"]:
        if not json_data:
            return None
        return cls(
        )


# work around possible type aliasing issues when variable has same name as a model
_TypeConfigurationModel = TypeConfigurationModel


