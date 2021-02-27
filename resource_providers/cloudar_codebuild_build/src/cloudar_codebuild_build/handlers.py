import logging
from typing import Any, MutableMapping, Optional

from cloudformation_cli_python_lib import (
    Action,
    OperationStatus,
    ProgressEvent,
    Resource,
    SessionProxy,
)
from cloudformation_cli_python_lib.exceptions import (
    InternalFailure,
    NotFound,
    ServiceLimitExceeded,
    InvalidRequest,
)

from .actions import Action as HandlerAction
from .constants import TYPE_NAME
from .models import ResourceHandlerRequest, ResourceModel

# Use this logger to forward log messages to CloudWatch Logs.
LOG = logging.getLogger(__name__)

resource = Resource(TYPE_NAME, ResourceModel)
test_entrypoint = resource.test_entrypoint


@resource.handler(Action.CREATE)
def create_handler(
    session: Optional[SessionProxy],
    request: ResourceHandlerRequest,
    callback_context: MutableMapping[str, Any],
) -> ProgressEvent:
    # We have to do some extra error checking because the python plugin doesn't
    # see https://github.com/aws-cloudformation/cloudformation-cli/issues/683
    if not callback_context:
        # Check all readOnly properties to verify that they're empty. We only
        # do this on the initial Create request
        if request.desiredResourceState.BuildId:
            raise InvalidRequest("BuildId is a readOnlyProperty")
        if request.desiredResourceState.Arn:
            raise InvalidRequest("Arn is a readOnlyProperty")
        if request.desiredResourceState.BuildNumber:
            raise InvalidRequest("BuildNumber is a readOnlyProperty")
    return _action_handler(session, request, callback_context, HandlerAction.CREATE)


@resource.handler(Action.DELETE)
def delete_handler(
    session: Optional[SessionProxy],
    request: ResourceHandlerRequest,
    callback_context: MutableMapping[str, Any],
) -> ProgressEvent:
    return _action_handler(session, request, callback_context, HandlerAction.DELETE)


@resource.handler(Action.READ)
def read_handler(
    session: Optional[SessionProxy],
    request: ResourceHandlerRequest,
    callback_context: MutableMapping[str, Any],
) -> ProgressEvent:
    return _action_handler(session, request, callback_context, HandlerAction.READ)


def _action_handler(
    session: Optional[SessionProxy],
    request: ResourceHandlerRequest,
    callback_context: MutableMapping[str, Any],
    start_action: HandlerAction,
) -> ProgressEvent:
    model = request.desiredResourceState
    if session is None:
        raise InternalFailure("No AWS credentials found: no session set")

    # Get next action
    next_action: HandlerAction = HandlerAction[callback_context.get("next_action", start_action.name)]

    # Some exceptions are always handled the same, so we can catch them here instead of in the actions
    codebuild_exceptions = session.client("codebuild").exceptions
    try:
        # execute the action
        next_action = next_action.value(session, model)
    except codebuild_exceptions.ResourceNotFoundException as e:
        raise NotFound(TYPE_NAME, model.BuildId) from e
    except codebuild_exceptions.AccountLimitExceededException as e:
        raise ServiceLimitExceeded() from e
    except codebuild_exceptions.InvalidInputException as e:
        raise InvalidRequest() from e

    # EnvironmentVariablesOverride is part of the desiredResourceState, but we consider it a write only property
    # (because it's not possible to always read it correctly). We can't return write only properties. according to the
    # contract. Once we executed all our actions we can delete it.
    model.EnvironmentVariablesOverride = None

    # Handle cases where there is no next action to take
    if next_action is HandlerAction.DELETE_COMPLETE:
        # Delete handler cannot return a Model
        return ProgressEvent(status=OperationStatus.SUCCESS, resourceModel=None)
    if next_action is HandlerAction.COMPLETE:
        # No callback context is needed
        return ProgressEvent(status=OperationStatus.SUCCESS, resourceModel=model)

    return ProgressEvent(
        status=OperationStatus.IN_PROGRESS,
        resourceModel=model,
        callbackContext={"next_action": next_action.name},
        # CodeBuild isn't the fastest service, we can wait at least 30 seconds before looking at the build status again
        callbackDelaySeconds=30,
    )


# We don't have these handlers:
# Update: Every update is a replacement, so only the read handler is needed
# List: It currently does not make sense to add this complexity, as there is no use case for it yet
