"""
Defines a set of actions to take and how to move between them

This is probably cleaner as a real state machine, but the current steps are not that complex.
"""

from enum import Enum

from cloudformation_cli_python_lib import SessionProxy
from cloudformation_cli_python_lib.exceptions import (
    NotStabilized,
    ResourceConflict,
    NotFound,
    InternalFailure,
)

from .constants import BuildStatus, TYPE_NAME
from .models import ResourceModel, EnvironmentVariable


def create_start(session: SessionProxy, model: ResourceModel) -> "Action":
    codebuild = session.client("codebuild")

    kwargs = {"projectName": model.ProjectName}
    # Optional parameters. These are all create only, so we don't have to save them in the model.
    if model.EnvironmentVariablesOverride:
        kwargs["environmentVariablesOverride"] = [
            _environment_variable(x) for x in model.EnvironmentVariablesOverride
        ]
    if model.DebugSessionEnabled is not None:
        kwargs["debugSessionEnabled"] = model.DebugSessionEnabled

    build = codebuild.start_build(**kwargs)["build"]
    model.BuildId = build["id"]
    model.Arn = build["arn"]
    model.BuildNumber = build["buildNumber"]

    return Action.CREATE_IN_PROGRESS


def create_in_progress(session: SessionProxy, model: ResourceModel) -> "Action":
    codebuild = session.client("codebuild")

    # this build should always exist - we created it
    build = codebuild.batch_get_builds(ids=[model.BuildId])["builds"][0]
    status: BuildStatus = BuildStatus[build["buildStatus"]]

    if status == BuildStatus.SUCCEEDED:
        return Action.COMPLETE
    if status == BuildStatus.IN_PROGRESS:
        return Action.CREATE_IN_PROGRESS

    raise NotStabilized(f"The build exited with status {status.name}")


def read(session: SessionProxy, model: ResourceModel) -> "Action":
    _read_model(session, model)
    return Action.COMPLETE


def delete(session: SessionProxy, model: ResourceModel) -> "Action":
    # read first, so we can throw an error if the build does not exist
    _read_model(session, model)
    codebuild = session.client("codebuild")
    response = codebuild.batch_delete_builds(ids=[model.BuildId])
    if len(response.get("buildsNotDeleted", [])) > 0:
        raise ResourceConflict(
            f"Could not delete build. Current Status is: {response['buildsNotDeleted'][0]['statusCode']}"
        )

    return Action.DELETE_COMPLETE


def force_stop(*args, **kwargs):
    raise InternalFailure("Resource failed to stop and return a success or failure")


class FunctionWrapper:
    def __init__(self, function):
        self.function = function

    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)


class Action(Enum):
    CREATE = FunctionWrapper(create_start)
    READ = FunctionWrapper(read)
    DELETE = FunctionWrapper(delete)

    CREATE_IN_PROGRESS = FunctionWrapper(create_in_progress)

    DELETE_COMPLETE = FunctionWrapper(force_stop)
    COMPLETE = FunctionWrapper(force_stop)


def _read_model(session: SessionProxy, model: ResourceModel) -> None:
    if not model.BuildId:
        raise NotFound(TYPE_NAME, str(None))
    codebuild = session.client("codebuild")
    try:
        build = codebuild.batch_get_builds(ids=[model.BuildId])["builds"][0]
    except IndexError:
        # There where no builds found
        raise NotFound(TYPE_NAME, model.BuildId)
    # The read handler should not be called for builds that are in progress, those are still stabilizing
    # This means that we don't need to check the build state
    model.BuildId = build["id"]
    model.Arn = build["arn"]
    model.BuildNumber = build["buildNumber"]
    # SessionTarget is optional / dependent on the DebugSessionEnabled property
    model.SessionTarget = build.get("debugSession", {}).get("sessionTarget")
    # we defined EnvironmentVariablesOverride as writeOnlyProperty, because we can't tell the difference
    # between reading an override and reading en environment variable set on the project

    # model is mutable, so we don't have to return something
    return


def _environment_variable(environment_variable: EnvironmentVariable):
    # Name and Value are required by the schema
    output = {"name": environment_variable.Name, "value": environment_variable.Value}
    if environment_variable.Type:
        output["type"] = environment_variable.Type
    return output
