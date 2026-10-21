# DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from pb.user import user_command_pb2 as user_dot_user__command__pb2
from pb.user import user_common_pb2 as user_dot_user__common__pb2

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
        + ' but the generated code in user/user_command_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class UserCommandServiceStub:
    """Missing associated documentation comment in.proto file."""

    def __init__(self, channel):
        """Constructor. Args: channel: A grpc.Channel."""
        self.Create = channel.unary_unary(
                '/pb.user.UserCommandService/Create',
                request_serializer=user_dot_user__command__pb2.CreateUserRequest.SerializeToString,
                response_deserializer=user_dot_user__common__pb2.ApiResponseUser.FromString,
                _registered_method=True)
        self.Update = channel.unary_unary(
                '/pb.user.UserCommandService/Update',
                request_serializer=user_dot_user__command__pb2.UpdateUserRequest.SerializeToString,
                response_deserializer=user_dot_user__common__pb2.ApiResponseUser.FromString,
                _registered_method=True)
        self.UpdateIsVerified = channel.unary_unary(
                '/pb.user.UserCommandService/UpdateIsVerified',
                request_serializer=user_dot_user__command__pb2.UpdateUserIsVerifiedRequest.SerializeToString,
                response_deserializer=user_dot_user__common__pb2.ApiResponseUser.FromString,
                _registered_method=True)
        self.UpdatePassword = channel.unary_unary(
                '/pb.user.UserCommandService/UpdatePassword',
                request_serializer=user_dot_user__command__pb2.UpdateUserPasswordRequest.SerializeToString,
                response_deserializer=user_dot_user__common__pb2.ApiResponseUser.FromString,
                _registered_method=True)
        self.TrashedUser = channel.unary_unary(
                '/pb.user.UserCommandService/TrashedUser',
                request_serializer=user_dot_user__common__pb2.FindByIdUserRequest.SerializeToString,
                response_deserializer=user_dot_user__common__pb2.ApiResponseUserDeleteAt.FromString,
                _registered_method=True)
        self.RestoreUser = channel.unary_unary(
                '/pb.user.UserCommandService/RestoreUser',
                request_serializer=user_dot_user__common__pb2.FindByIdUserRequest.SerializeToString,
                response_deserializer=user_dot_user__common__pb2.ApiResponseUserDeleteAt.FromString,
                _registered_method=True)
        self.DeleteUserPermanent = channel.unary_unary(
                '/pb.user.UserCommandService/DeleteUserPermanent',
                request_serializer=user_dot_user__common__pb2.FindByIdUserRequest.SerializeToString,
                response_deserializer=user_dot_user__common__pb2.ApiResponseUserDelete.FromString,
                _registered_method=True)
        self.RestoreAllUser = channel.unary_unary(
                '/pb.user.UserCommandService/RestoreAllUser',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=user_dot_user__common__pb2.ApiResponseUserAll.FromString,
                _registered_method=True)
        self.DeleteAllUserPermanent = channel.unary_unary(
                '/pb.user.UserCommandService/DeleteAllUserPermanent',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=user_dot_user__common__pb2.ApiResponseUserAll.FromString,
                _registered_method=True)


class UserCommandServiceServicer:
    """Missing associated documentation comment in.proto file."""

    def Create(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Update(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UpdateIsVerified(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UpdatePassword(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def TrashedUser(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RestoreUser(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteUserPermanent(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RestoreAllUser(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteAllUserPermanent(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_UserCommandServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Create': grpc.unary_unary_rpc_method_handler(
                    servicer.Create,
                    request_deserializer=user_dot_user__command__pb2.CreateUserRequest.FromString,
                    response_serializer=user_dot_user__common__pb2.ApiResponseUser.SerializeToString,
            ),
            'Update': grpc.unary_unary_rpc_method_handler(
                    servicer.Update,
                    request_deserializer=user_dot_user__command__pb2.UpdateUserRequest.FromString,
                    response_serializer=user_dot_user__common__pb2.ApiResponseUser.SerializeToString,
            ),
            'UpdateIsVerified': grpc.unary_unary_rpc_method_handler(
                    servicer.UpdateIsVerified,
                    request_deserializer=user_dot_user__command__pb2.UpdateUserIsVerifiedRequest.FromString,
                    response_serializer=user_dot_user__common__pb2.ApiResponseUser.SerializeToString,
            ),
            'UpdatePassword': grpc.unary_unary_rpc_method_handler(
                    servicer.UpdatePassword,
                    request_deserializer=user_dot_user__command__pb2.UpdateUserPasswordRequest.FromString,
                    response_serializer=user_dot_user__common__pb2.ApiResponseUser.SerializeToString,
            ),
            'TrashedUser': grpc.unary_unary_rpc_method_handler(
                    servicer.TrashedUser,
                    request_deserializer=user_dot_user__common__pb2.FindByIdUserRequest.FromString,
                    response_serializer=user_dot_user__common__pb2.ApiResponseUserDeleteAt.SerializeToString,
            ),
            'RestoreUser': grpc.unary_unary_rpc_method_handler(
                    servicer.RestoreUser,
                    request_deserializer=user_dot_user__common__pb2.FindByIdUserRequest.FromString,
                    response_serializer=user_dot_user__common__pb2.ApiResponseUserDeleteAt.SerializeToString,
            ),
            'DeleteUserPermanent': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteUserPermanent,
                    request_deserializer=user_dot_user__common__pb2.FindByIdUserRequest.FromString,
                    response_serializer=user_dot_user__common__pb2.ApiResponseUserDelete.SerializeToString,
            ),
            'RestoreAllUser': grpc.unary_unary_rpc_method_handler(
                    servicer.RestoreAllUser,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=user_dot_user__common__pb2.ApiResponseUserAll.SerializeToString,
            ),
            'DeleteAllUserPermanent': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteAllUserPermanent,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=user_dot_user__common__pb2.ApiResponseUserAll.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'pb.user.UserCommandService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('pb.user.UserCommandService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class UserCommandService:
    """Missing associated documentation comment in.proto file."""

    @staticmethod
    def Create(request,
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
            '/pb.user.UserCommandService/Create',
            user_dot_user__command__pb2.CreateUserRequest.SerializeToString,
            user_dot_user__common__pb2.ApiResponseUser.FromString,
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
    def Update(request,
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
            '/pb.user.UserCommandService/Update',
            user_dot_user__command__pb2.UpdateUserRequest.SerializeToString,
            user_dot_user__common__pb2.ApiResponseUser.FromString,
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
    def UpdateIsVerified(request,
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
            '/pb.user.UserCommandService/UpdateIsVerified',
            user_dot_user__command__pb2.UpdateUserIsVerifiedRequest.SerializeToString,
            user_dot_user__common__pb2.ApiResponseUser.FromString,
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
    def UpdatePassword(request,
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
            '/pb.user.UserCommandService/UpdatePassword',
            user_dot_user__command__pb2.UpdateUserPasswordRequest.SerializeToString,
            user_dot_user__common__pb2.ApiResponseUser.FromString,
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
    def TrashedUser(request,
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
            '/pb.user.UserCommandService/TrashedUser',
            user_dot_user__common__pb2.FindByIdUserRequest.SerializeToString,
            user_dot_user__common__pb2.ApiResponseUserDeleteAt.FromString,
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
    def RestoreUser(request,
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
            '/pb.user.UserCommandService/RestoreUser',
            user_dot_user__common__pb2.FindByIdUserRequest.SerializeToString,
            user_dot_user__common__pb2.ApiResponseUserDeleteAt.FromString,
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
    def DeleteUserPermanent(request,
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
            '/pb.user.UserCommandService/DeleteUserPermanent',
            user_dot_user__common__pb2.FindByIdUserRequest.SerializeToString,
            user_dot_user__common__pb2.ApiResponseUserDelete.FromString,
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
    def RestoreAllUser(request,
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
            '/pb.user.UserCommandService/RestoreAllUser',
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            user_dot_user__common__pb2.ApiResponseUserAll.FromString,
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
    def DeleteAllUserPermanent(request,
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
            '/pb.user.UserCommandService/DeleteAllUserPermanent',
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            user_dot_user__common__pb2.ApiResponseUserAll.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
