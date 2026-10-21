# DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from pb.role import role_common_pb2 as role_dot_role__common__pb2
from pb.role import role_query_pb2 as role_dot_role__query__pb2

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
        + ' but the generated code in role/role_query_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class RoleQueryServiceStub:
    """Missing associated documentation comment in.proto file."""

    def __init__(self, channel):
        """Constructor. Args: channel: A grpc.Channel."""
        self.FindAllRole = channel.unary_unary(
                '/pb.role.RoleQueryService/FindAllRole',
                request_serializer=role_dot_role__query__pb2.FindAllRoleRequest.SerializeToString,
                response_deserializer=role_dot_role__common__pb2.ApiResponsePaginationRole.FromString,
                _registered_method=True)
        self.FindByIdRole = channel.unary_unary(
                '/pb.role.RoleQueryService/FindByIdRole',
                request_serializer=role_dot_role__common__pb2.FindByIdRoleRequest.SerializeToString,
                response_deserializer=role_dot_role__common__pb2.ApiResponseRole.FromString,
                _registered_method=True)
        self.FindByNameRole = channel.unary_unary(
                '/pb.role.RoleQueryService/FindByNameRole',
                request_serializer=role_dot_role__query__pb2.FindByNameRoleRequest.SerializeToString,
                response_deserializer=role_dot_role__common__pb2.ApiResponseRole.FromString,
                _registered_method=True)
        self.FindByActive = channel.unary_unary(
                '/pb.role.RoleQueryService/FindByActive',
                request_serializer=role_dot_role__query__pb2.FindAllRoleRequest.SerializeToString,
                response_deserializer=role_dot_role__common__pb2.ApiResponsePaginationRoleDeleteAt.FromString,
                _registered_method=True)
        self.FindByTrashed = channel.unary_unary(
                '/pb.role.RoleQueryService/FindByTrashed',
                request_serializer=role_dot_role__query__pb2.FindAllRoleRequest.SerializeToString,
                response_deserializer=role_dot_role__common__pb2.ApiResponsePaginationRoleDeleteAt.FromString,
                _registered_method=True)
        self.FindByUserId = channel.unary_unary(
                '/pb.role.RoleQueryService/FindByUserId',
                request_serializer=role_dot_role__query__pb2.FindByIdUserRoleRequest.SerializeToString,
                response_deserializer=role_dot_role__common__pb2.ApiResponsesRole.FromString,
                _registered_method=True)


class RoleQueryServiceServicer:
    """Missing associated documentation comment in.proto file."""

    def FindAllRole(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def FindByIdRole(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def FindByNameRole(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def FindByActive(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def FindByTrashed(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def FindByUserId(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_RoleQueryServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'FindAllRole': grpc.unary_unary_rpc_method_handler(
                    servicer.FindAllRole,
                    request_deserializer=role_dot_role__query__pb2.FindAllRoleRequest.FromString,
                    response_serializer=role_dot_role__common__pb2.ApiResponsePaginationRole.SerializeToString,
            ),
            'FindByIdRole': grpc.unary_unary_rpc_method_handler(
                    servicer.FindByIdRole,
                    request_deserializer=role_dot_role__common__pb2.FindByIdRoleRequest.FromString,
                    response_serializer=role_dot_role__common__pb2.ApiResponseRole.SerializeToString,
            ),
            'FindByNameRole': grpc.unary_unary_rpc_method_handler(
                    servicer.FindByNameRole,
                    request_deserializer=role_dot_role__query__pb2.FindByNameRoleRequest.FromString,
                    response_serializer=role_dot_role__common__pb2.ApiResponseRole.SerializeToString,
            ),
            'FindByActive': grpc.unary_unary_rpc_method_handler(
                    servicer.FindByActive,
                    request_deserializer=role_dot_role__query__pb2.FindAllRoleRequest.FromString,
                    response_serializer=role_dot_role__common__pb2.ApiResponsePaginationRoleDeleteAt.SerializeToString,
            ),
            'FindByTrashed': grpc.unary_unary_rpc_method_handler(
                    servicer.FindByTrashed,
                    request_deserializer=role_dot_role__query__pb2.FindAllRoleRequest.FromString,
                    response_serializer=role_dot_role__common__pb2.ApiResponsePaginationRoleDeleteAt.SerializeToString,
            ),
            'FindByUserId': grpc.unary_unary_rpc_method_handler(
                    servicer.FindByUserId,
                    request_deserializer=role_dot_role__query__pb2.FindByIdUserRoleRequest.FromString,
                    response_serializer=role_dot_role__common__pb2.ApiResponsesRole.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'pb.role.RoleQueryService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('pb.role.RoleQueryService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class RoleQueryService:
    """Missing associated documentation comment in.proto file."""

    @staticmethod
    def FindAllRole(request,
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
            '/pb.role.RoleQueryService/FindAllRole',
            role_dot_role__query__pb2.FindAllRoleRequest.SerializeToString,
            role_dot_role__common__pb2.ApiResponsePaginationRole.FromString,
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
    def FindByIdRole(request,
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
            '/pb.role.RoleQueryService/FindByIdRole',
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
    def FindByNameRole(request,
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
            '/pb.role.RoleQueryService/FindByNameRole',
            role_dot_role__query__pb2.FindByNameRoleRequest.SerializeToString,
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
    def FindByActive(request,
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
            '/pb.role.RoleQueryService/FindByActive',
            role_dot_role__query__pb2.FindAllRoleRequest.SerializeToString,
            role_dot_role__common__pb2.ApiResponsePaginationRoleDeleteAt.FromString,
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
    def FindByTrashed(request,
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
            '/pb.role.RoleQueryService/FindByTrashed',
            role_dot_role__query__pb2.FindAllRoleRequest.SerializeToString,
            role_dot_role__common__pb2.ApiResponsePaginationRoleDeleteAt.FromString,
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
            '/pb.role.RoleQueryService/FindByUserId',
            role_dot_role__query__pb2.FindByIdUserRoleRequest.SerializeToString,
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
