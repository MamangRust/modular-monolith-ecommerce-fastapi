# DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from pb.role import role_common_pb2 as role_dot_role__common__pb2
from pb.user_role import user_role_pb2 as user__role_dot_user__role__pb2

GRPC_GENERATED_VERSION = '1.84.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + ' but the generated code in user_role/user_role_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class UserRoleServiceStub:
    """Missing associated documentation comment in.proto file."""

    def __init__(self, channel):
        """Constructor. Args: channel: A grpc.Channel."""
        self.FindByUserId = channel.unary_unary(
                '/pb.user_role.UserRoleService/FindByUserId',
                request_serializer=user__role_dot_user__role__pb2.FindByIdUserRoleRequest.SerializeToString,
                response_deserializer=role_dot_role__common__pb2.ApiResponsesRole.FromString,
                _registered_method=True)
        self.AssignRoleToUser = channel.unary_unary(
                '/pb.user_role.UserRoleService/AssignRoleToUser',
                request_serializer=user__role_dot_user__role__pb2.AssignRoleToUserRequest.SerializeToString,
                response_deserializer=user__role_dot_user__role__pb2.ApiResponseUserRole.FromString,
                _registered_method=True)
        self.RemoveRoleFromUser = channel.unary_unary(
                '/pb.user_role.UserRoleService/RemoveRoleFromUser',
                request_serializer=user__role_dot_user__role__pb2.RemoveRoleFromUserRequest.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                _registered_method=True)


class UserRoleServiceServicer:
    """Missing associated documentation comment in.proto file."""

    def FindByUserId(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def AssignRoleToUser(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RemoveRoleFromUser(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_UserRoleServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'FindByUserId': grpc.unary_unary_rpc_method_handler(
                    servicer.FindByUserId,
                    request_deserializer=user__role_dot_user__role__pb2.FindByIdUserRoleRequest.FromString,
                    response_serializer=role_dot_role__common__pb2.ApiResponsesRole.SerializeToString,
            ),
            'AssignRoleToUser': grpc.unary_unary_rpc_method_handler(
                    servicer.AssignRoleToUser,
                    request_deserializer=user__role_dot_user__role__pb2.AssignRoleToUserRequest.FromString,
                    response_serializer=user__role_dot_user__role__pb2.ApiResponseUserRole.SerializeToString,
            ),
            'RemoveRoleFromUser': grpc.unary_unary_rpc_method_handler(
                    servicer.RemoveRoleFromUser,
                    request_deserializer=user__role_dot_user__role__pb2.RemoveRoleFromUserRequest.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'pb.user_role.UserRoleService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('pb.user_role.UserRoleService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class UserRoleService:
    """Missing associated documentation comment in.proto file."""

    @staticmethod
    def FindByUserId(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/pb.user_role.UserRoleService/FindByUserId',
            user__role_dot_user__role__pb2.FindByIdUserRoleRequest.SerializeToString,
            role_dot_role__common__pb2.ApiResponsesRole.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def AssignRoleToUser(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/pb.user_role.UserRoleService/AssignRoleToUser',
            user__role_dot_user__role__pb2.AssignRoleToUserRequest.SerializeToString,
            user__role_dot_user__role__pb2.ApiResponseUserRole.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def RemoveRoleFromUser(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/pb.user_role.UserRoleService/RemoveRoleFromUser',
            user__role_dot_user__role__pb2.RemoveRoleFromUserRequest.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
