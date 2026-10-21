# DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from pb.category import category_command_pb2 as category_dot_category__command__pb2
from pb.category import category_common_pb2 as category_dot_category__common__pb2
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2

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
        + ' but the generated code in category/category_command_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class CategoryCommandServiceStub:
    """Missing associated documentation comment in.proto file."""

    def __init__(self, channel):
        """Constructor. Args: channel: A grpc.Channel."""
        self.Create = channel.unary_unary(
                '/pb.category.CategoryCommandService/Create',
                request_serializer=category_dot_category__command__pb2.CreateCategoryRequest.SerializeToString,
                response_deserializer=category_dot_category__common__pb2.ApiResponseCategory.FromString,
                _registered_method=True)
        self.Update = channel.unary_unary(
                '/pb.category.CategoryCommandService/Update',
                request_serializer=category_dot_category__command__pb2.UpdateCategoryRequest.SerializeToString,
                response_deserializer=category_dot_category__common__pb2.ApiResponseCategory.FromString,
                _registered_method=True)
        self.TrashedCategory = channel.unary_unary(
                '/pb.category.CategoryCommandService/TrashedCategory',
                request_serializer=category_dot_category__common__pb2.FindByIdCategoryRequest.SerializeToString,
                response_deserializer=category_dot_category__common__pb2.ApiResponseCategoryDeleteAt.FromString,
                _registered_method=True)
        self.RestoreCategory = channel.unary_unary(
                '/pb.category.CategoryCommandService/RestoreCategory',
                request_serializer=category_dot_category__common__pb2.FindByIdCategoryRequest.SerializeToString,
                response_deserializer=category_dot_category__common__pb2.ApiResponseCategoryDeleteAt.FromString,
                _registered_method=True)
        self.DeleteCategoryPermanent = channel.unary_unary(
                '/pb.category.CategoryCommandService/DeleteCategoryPermanent',
                request_serializer=category_dot_category__common__pb2.FindByIdCategoryRequest.SerializeToString,
                response_deserializer=category_dot_category__common__pb2.ApiResponseCategoryDelete.FromString,
                _registered_method=True)
        self.RestoreAllCategory = channel.unary_unary(
                '/pb.category.CategoryCommandService/RestoreAllCategory',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=category_dot_category__common__pb2.ApiResponseCategoryAll.FromString,
                _registered_method=True)
        self.DeleteAllCategoryPermanent = channel.unary_unary(
                '/pb.category.CategoryCommandService/DeleteAllCategoryPermanent',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=category_dot_category__common__pb2.ApiResponseCategoryAll.FromString,
                _registered_method=True)


class CategoryCommandServiceServicer:
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

    def TrashedCategory(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RestoreCategory(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteCategoryPermanent(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RestoreAllCategory(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteAllCategoryPermanent(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_CategoryCommandServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Create': grpc.unary_unary_rpc_method_handler(
                    servicer.Create,
                    request_deserializer=category_dot_category__command__pb2.CreateCategoryRequest.FromString,
                    response_serializer=category_dot_category__common__pb2.ApiResponseCategory.SerializeToString,
            ),
            'Update': grpc.unary_unary_rpc_method_handler(
                    servicer.Update,
                    request_deserializer=category_dot_category__command__pb2.UpdateCategoryRequest.FromString,
                    response_serializer=category_dot_category__common__pb2.ApiResponseCategory.SerializeToString,
            ),
            'TrashedCategory': grpc.unary_unary_rpc_method_handler(
                    servicer.TrashedCategory,
                    request_deserializer=category_dot_category__common__pb2.FindByIdCategoryRequest.FromString,
                    response_serializer=category_dot_category__common__pb2.ApiResponseCategoryDeleteAt.SerializeToString,
            ),
            'RestoreCategory': grpc.unary_unary_rpc_method_handler(
                    servicer.RestoreCategory,
                    request_deserializer=category_dot_category__common__pb2.FindByIdCategoryRequest.FromString,
                    response_serializer=category_dot_category__common__pb2.ApiResponseCategoryDeleteAt.SerializeToString,
            ),
            'DeleteCategoryPermanent': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteCategoryPermanent,
                    request_deserializer=category_dot_category__common__pb2.FindByIdCategoryRequest.FromString,
                    response_serializer=category_dot_category__common__pb2.ApiResponseCategoryDelete.SerializeToString,
            ),
            'RestoreAllCategory': grpc.unary_unary_rpc_method_handler(
                    servicer.RestoreAllCategory,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=category_dot_category__common__pb2.ApiResponseCategoryAll.SerializeToString,
            ),
            'DeleteAllCategoryPermanent': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteAllCategoryPermanent,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=category_dot_category__common__pb2.ApiResponseCategoryAll.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'pb.category.CategoryCommandService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('pb.category.CategoryCommandService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class CategoryCommandService:
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
            '/pb.category.CategoryCommandService/Create',
            category_dot_category__command__pb2.CreateCategoryRequest.SerializeToString,
            category_dot_category__common__pb2.ApiResponseCategory.FromString,
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
            '/pb.category.CategoryCommandService/Update',
            category_dot_category__command__pb2.UpdateCategoryRequest.SerializeToString,
            category_dot_category__common__pb2.ApiResponseCategory.FromString,
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
    def TrashedCategory(request,
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
            '/pb.category.CategoryCommandService/TrashedCategory',
            category_dot_category__common__pb2.FindByIdCategoryRequest.SerializeToString,
            category_dot_category__common__pb2.ApiResponseCategoryDeleteAt.FromString,
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
    def RestoreCategory(request,
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
            '/pb.category.CategoryCommandService/RestoreCategory',
            category_dot_category__common__pb2.FindByIdCategoryRequest.SerializeToString,
            category_dot_category__common__pb2.ApiResponseCategoryDeleteAt.FromString,
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
    def DeleteCategoryPermanent(request,
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
            '/pb.category.CategoryCommandService/DeleteCategoryPermanent',
            category_dot_category__common__pb2.FindByIdCategoryRequest.SerializeToString,
            category_dot_category__common__pb2.ApiResponseCategoryDelete.FromString,
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
    def RestoreAllCategory(request,
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
            '/pb.category.CategoryCommandService/RestoreAllCategory',
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            category_dot_category__common__pb2.ApiResponseCategoryAll.FromString,
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
    def DeleteAllCategoryPermanent(request,
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
            '/pb.category.CategoryCommandService/DeleteAllCategoryPermanent',
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            category_dot_category__common__pb2.ApiResponseCategoryAll.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
