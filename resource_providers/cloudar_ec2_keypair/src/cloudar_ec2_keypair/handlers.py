import logging
from typing import Any, MutableMapping, Optional, TYPE_CHECKING, Mapping

from botocore.exceptions import ClientError

from cloudformation_cli_python_lib import (
    Action,
    HandlerErrorCode,
    OperationStatus,
    ProgressEvent,
    Resource,
    SessionProxy,
    exceptions,
)

from .models import ResourceHandlerRequest, ResourceModel

if TYPE_CHECKING:
    import botostubs


# Use this logger to forward log messages to CloudWatch Logs.
LOG = logging.getLogger(__name__)
TYPE_NAME = "Cloudar::EC2::KeyPair"

resource = Resource(TYPE_NAME, ResourceModel)
test_entrypoint = resource.test_entrypoint


@resource.handler(Action.CREATE)
def create_handler(
    session: Optional[SessionProxy],
    request: ResourceHandlerRequest,
    callback_context: MutableMapping[str, Any],
) -> ProgressEvent:
    model = request.desiredResourceState
    progress: ProgressEvent = ProgressEvent(
        status=OperationStatus.IN_PROGRESS,
        resourceModel=model,
    )
    ec2 = session.client("ec2")  # type: botostubs.EC2

    try:
        response = ec2.import_key_pair(
            KeyName=model.KeyName, PublicKeyMaterial=model.PublicKey
        )
    except ClientError as e:
        if e.response.get("Error", {}).get("Code") == "InvalidKeyPair.Duplicate":
            raise exceptions.AlreadyExists(TYPE_NAME, model.KeyName)
        else:
            # raise the original exception
            raise

    model.Fingerprint = response["KeyFingerprint"]

    # Setting Status to success will signal to cfn that the operation is complete
    progress.resourceModel = model
    progress.status = OperationStatus.SUCCESS
    return progress


# @resource.handler(Action.UPDATE)
# We could specify an update handler, but because every property triggers an update
# we can let CloudFormation do this for us (If the resource provider does not contain
# an update handler, CloudFormation cannot update the resource during stack update
# operations, and will instead replace it).
def update_handler(
    session: Optional[SessionProxy],
    request: ResourceHandlerRequest,
    callback_context: MutableMapping[str, Any],
) -> ProgressEvent:
    # Do exactly the same as a create
    return create_handler(session, request, callback_context)


@resource.handler(Action.DELETE)
def delete_handler(
    session: Optional[SessionProxy],
    request: ResourceHandlerRequest,
    callback_context: MutableMapping[str, Any],
) -> ProgressEvent:
    model = request.desiredResourceState
    progress: ProgressEvent = ProgressEvent(
        status=OperationStatus.IN_PROGRESS,
        resourceModel=model,
    )
    ec2 = session.client("ec2")  # type: botostubs.EC2
    # DeleteKeyPair does not raise an exception if the KeyPair does not exist
    # The contract requires us to make a distinction between does not exist and
    # a successful delete, so we need to read first (the read handler will throw
    # an exception if the KeyPair does not exist).
    _ = read_handler(session, request, callback_context)
    ec2.delete_key_pair(KeyName=model.KeyName)
    progress.status = OperationStatus.SUCCESS
    return progress


@resource.handler(Action.READ)
def read_handler(
    session: Optional[SessionProxy],
    request: ResourceHandlerRequest,
    callback_context: MutableMapping[str, Any],
) -> ProgressEvent:
    model = request.desiredResourceState
    ec2 = session.client("ec2")  # type: botostubs.EC2
    try:
        keypairs = ec2.describe_key_pairs(KeyNames=[model.KeyName])["KeyPairs"]
    except ClientError as e:
        if e.response.get("Error", {}).get("Code") == "InvalidKeyPair.NotFound":
            raise exceptions.NotFound(TYPE_NAME, model.KeyName)
        else:
            # raise the original exception
            raise
    if not len(keypairs) == 1:
        raise exceptions.NotFound(TYPE_NAME, model.KeyName)

    keypair = keypairs[0]
    model.Fingerprint = keypair["KeyFingerprint"]

    return ProgressEvent(
        status=OperationStatus.SUCCESS,
        resourceModel=model,
    )


@resource.handler(Action.LIST)
def list_handler(
    session: Optional[SessionProxy],
    request: ResourceHandlerRequest,
    callback_context: MutableMapping[str, Any],
) -> ProgressEvent:
    model = request.desiredResourceState
    ec2 = session.client("ec2")  # type: botostubs.EC2
    keypairs = ec2.describe_key_pairs()["KeyPairs"]

    return ProgressEvent(
        status=OperationStatus.SUCCESS,
        resourceModels=[_create_model(x, model) for x in keypairs],
    )


def _create_model(o: Mapping, model: ResourceModel) -> ResourceModel:

    # This might be workaround for an error in the test, or actual desired
    # behaviour.
    # See https://github.com/aws-cloudformation/cloudformation-cli/issues/370
    if model.KeyName == o["KeyName"]:
        public_key = model.PublicKey
    else:
        public_key = None
    return ResourceModel(
        KeyName=o["KeyName"],
        Fingerprint=o["KeyFingerprint"],
        # There is no way to get the PublicKey from the EC2 api.
        # That's why it's defined as a writeOnlyProperty in the resource spec.
        PublicKey=public_key,
    )
