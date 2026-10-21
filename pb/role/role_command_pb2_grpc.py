# DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from pb.role import role_command_pb2 as role_dot_role__command__pb2
from pb.role import role_common_pb2 as role_dot_role__common__pb2

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
        + ' but the generated code in role/role_command_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class RoleCommandServiceStub:
    """Missing associated documentation comment in.proto file."""

    def __init__(self, channel):
        """Constructor. Args: channel: A grpc.Channel."""
        self.CreateRole = channel.unary_unary(
                '/pb.role.RoleCommandService/CreateRole',
                request_serializer=role_dot_role__command__pb2.CreateRoleRequest.SerializeToString,
                response_deserializer=role_dot_role__common__pb2.ApiResponseRole.FromString,
                _registered_method=True)
        self.UpdateRole = channel.unary_unary(
                '/pb.role.RoleCommandService/UpdateRole',
                request_serializer=role_dot_role__command__pb2.UpdateRoleRequest.SerializeToString,
                response_deserializer=role_dot_role__common__pb2.ApiResponseRole.FromString,
                _registered_method=True)
        self.TrashedRole = channel.unary_unary(
                '/pb.role.RoleCommandService/TrashedRole',
                request_serializer=role_dot_role__common__pb2.FindByIdRoleRequest.SerializeToString,
                response_deserializer=role_dot_role__common__pb2.ApiResponseRole.FromString,
                _registered_method=True)
        self.RestoreRole = channel.unary_unary(
                '/pb.role.RoleCommandService/RestoreRole',
                request_serializer=role_dot_role__common__pb2.FindByIdRoleRequest.SerializeToString,
                response_deserializer=role_dot_role__common__pb2.ApiResponseRole.FromString,
                _registered_method=True)
        self.DeleteRolePermanent = channel.unary_unary(
                '/pb.role.RoleCommandService/DeleteRolePermanent',
                request_serializer=role_dot_role__common__pb2.FindByIdRoleRequest.SerializeToString,
                response_deserializer=role_dot_role__common__pb2.ApiResponseRoleDelete.FromString,
                _registered_method=True)
        self.RestoreAllRole = channel.unary_unary(
                '/pb.role.RoleCommandService/RestoreAllRole',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=role_dot_role__common__pb2.ApiResponseRoleAll.FromString,
                _registered_method=True)
        self.DeleteAllRolePermanent = channel.unary_unary(
                '/pb.role.RoleCommandService/DeleteAllRolePermanent',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=role_dot_role__common__pb2.ApiResponseRoleAll.FromString,
                _registered_method=True)
        self.AssignRoleToUser = channel.unary_unary(
                '/pb.role.RoleCommandService/AssignRoleToUser',
                request_serializer=role_dot_role__common__pb2.AssignRoleToUserRequest.SerializeToString,
                response_deserializer=role_dot_role__common__pb2.ApiResponseUserRole.FromString,
                _registered_method=True)
        self.RemoveRoleFromUser = channel.unary_unary(
                '/pb.role.RoleCommandService/RemoveRoleFromUser',
                request_serializer=role_dot_role__common__pb2.RemoveRoleFromUserRequest.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                _registered_method=True)


class RoleCommandServiceServicer:
    """Missing associated documentation comment in.proto file."""

    def CreateRole(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UpdateRole(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def TrashedRole(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RestoreRole(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteRolePermanent(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RestoreAllRole(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteAllRolePermanent(self, request, context):
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


def add_RoleCommandServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'CreateRole': grpc.unary_unary_rpc_method_handler(
                    servicer.CreateRole,
                    request_deserializer=role_dot_role__command__pb2.CreateRoleRequest.FromString,
                    response_serializer=role_dot_role__common__pb2.ApiResponseRole.SerializeToString,
            ),
            'UpdateRole': grpc.unary_unary_rpc_method_handler(
                    servicer.UpdateRole,
                    request_deserializer=role_dot_role__command__pb2.UpdateRoleRequest.FromString,
                    response_serializer=role_dot_role__common__pb2.ApiResponseRole.SerializeToString,
            ),
            'TrashedRole': grpc.unary_unary_rpc_method_handler(
                    servicer.TrashedRole,
                    request_deserializer=role_dot_role__common__pb2.FindByIdRoleRequest.FromString,
                    response_serializer=role_dot_role__common__pb2.ApiResponseRole.SerializeToString,
            ),
            'RestoreRole': grpc.unary_unary_rpc_method_handler(
                    servicer.RestoreRole,
                    request_deserializer=role_dot_role__common__pb2.FindByIdRoleRequest.FromString,
                    response_serializer=role_dot_role__common__pb2.ApiResponseRole.SerializeToString,
            ),
            'DeleteRolePermanent': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteRolePermanent,
                    request_deserializer=role_dot_role__common__pb2.FindByIdRoleRequest.FromString,
                    response_serializer=role_dot_role__common__pb2.ApiResponseRoleDelete.SerializeToString,
            ),
            'RestoreAllRole': grpc.unary_unary_rpc_method_handler(
                    servicer.RestoreAllRole,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=role_dot_role__common__pb2.ApiResponseRoleAll.SerializeToString,
            ),
            'DeleteAllRolePermanent': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteAllRolePermanent,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=role_dot_role__common__pb2.ApiResponseRoleAll.SerializeToString,
            ),
            'AssignRoleToUser': grpc.unary_unary_rpc_method_handler(
                    servicer.AssignRoleToUser,
                    request_deserializer=role_dot_role__common__pb2.AssignRoleToUserRequest.FromString,
                    response_serializer=role_dot_role__common__pb2.ApiResponseUserRole.SerializeToString,
            ),
            'RemoveRoleFromUser': grpc.unary_unary_rpc_method_handler(
                    servicer.RemoveRoleFromUser,
                    request_deserializer=role_dot_role__common__pb2.RemoveRoleFromUserRequest.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'pb.role.RoleCommandService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('pb.role.RoleCommandService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class RoleCommandService:
    """Missing associated documentation comment in.proto file."""

    @staticmethod
    def CreateRole(request,
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
            '/pb.role.RoleCommandService/CreateRole',
            role_dot_role__command__pb2.CreateRoleRequest.SerializeToString,
            role_dot_role__common__pb2.ApiResponseRole.FromString,
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
    def UpdateRole(request,
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
            '/pb.role.RoleCommandService/UpdateRole',
            role_dot_role__command__pb2.UpdateRoleRequest.SerializeToString,
            role_dot_role__common__pb2.ApiResponseRole.FromString,
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
    def TrashedRole(request,
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
            '/pb.role.RoleCommandService/TrashedRole',
            role_dot_role__common__pb2.FindByIdRoleRequest.SerializeToString,
            role_dot_role__common__pb2.ApiResponseRole.FromString,
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
    def RestoreRole(request,
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
            '/pb.role.RoleCommandService/RestoreRole',
            role_dot_role__common__pb2.FindByIdRoleRequest.SerializeToString,
            role_dot_role__common__pb2.ApiResponseRole.FromString,
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
    def DeleteRolePermanent(request,
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
            '/pb.role.RoleCommandService/DeleteRolePermanent',
            role_dot_role__common__pb2.FindByIdRoleRequest.SerializeToString,
            role_dot_role__common__pb2.ApiResponseRoleDelete.FromString,
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
    def RestoreAllRole(request,
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
            '/pb.role.RoleCommandService/RestoreAllRole',
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            role_dot_role__common__pb2.ApiResponseRoleAll.FromString,
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
    def DeleteAllRolePermanent(request,
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
            '/pb.role.RoleCommandService/DeleteAllRolePermanent',
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            role_dot_role__common__pb2.ApiResponseRoleAll.FromString,
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
            '/pb.role.RoleCommandService/AssignRoleToUser',
            role_dot_role__common__pb2.AssignRoleToUserRequest.SerializeToString,
            role_dot_role__common__pb2.ApiResponseUserRole.FromString,
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
            '/pb.role.RoleCommandService/RemoveRoleFromUser',
            role_dot_role__common__pb2.RemoveRoleFromUserRequest.SerializeToString,
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
