from enum import Enum, auto

TYPE_NAME = "Cloudar::CodeBuild::Build"


class BuildStatus(Enum):
    SUCCEEDED = auto()
    FAILED = auto()
    FAULT = auto()
    TIMED_OUT = auto()
    IN_PROGRESS = auto()
    STOPPED = auto()
