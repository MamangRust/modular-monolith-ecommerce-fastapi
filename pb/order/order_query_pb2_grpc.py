# DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from pb.order import order_common_pb2 as order_dot_order__common__pb2
from pb.order import order_query_pb2 as order_dot_order__query__pb2

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
        + ' but the generated code in order/order_query_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class OrderQueryServiceStub:
    """Missing associated documentation comment in.proto file."""

    def __init__(self, channel):
        """Constructor. Args: channel: A grpc.Channel."""
        self.FindAll = channel.unary_unary(
                '/pb.order.OrderQueryService/FindAll',
                request_serializer=order_dot_order__query__pb2.FindAllOrderRequest.SerializeToString,
                response_deserializer=order_dot_order__common__pb2.ApiResponsePaginationOrder.FromString,
                _registered_method=True)
        self.FindById = channel.unary_unary(
                '/pb.order.OrderQueryService/FindById',
                request_serializer=order_dot_order__common__pb2.FindByIdOrderRequest.SerializeToString,
                response_deserializer=order_dot_order__common__pb2.ApiResponseOrder.FromString,
                _registered_method=True)
        self.FindByActive = channel.unary_unary(
                '/pb.order.OrderQueryService/FindByActive',
                request_serializer=order_dot_order__query__pb2.FindAllOrderRequest.SerializeToString,
                response_deserializer=order_dot_order__common__pb2.ApiResponsePaginationOrderDeleteAt.FromString,
                _registered_method=True)
        self.FindByTrashed = channel.unary_unary(
                '/pb.order.OrderQueryService/FindByTrashed',
                request_serializer=order_dot_order__query__pb2.FindAllOrderRequest.SerializeToString,
                response_deserializer=order_dot_order__common__pb2.ApiResponsePaginationOrderDeleteAt.FromString,
                _registered_method=True)


class OrderQueryServiceServicer:
    """Missing associated documentation comment in.proto file."""

    def FindAll(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def FindById(self, request, context):
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


def add_OrderQueryServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'FindAll': grpc.unary_unary_rpc_method_handler(
                    servicer.FindAll,
                    request_deserializer=order_dot_order__query__pb2.FindAllOrderRequest.FromString,
                    response_serializer=order_dot_order__common__pb2.ApiResponsePaginationOrder.SerializeToString,
            ),
            'FindById': grpc.unary_unary_rpc_method_handler(
                    servicer.FindById,
                    request_deserializer=order_dot_order__common__pb2.FindByIdOrderRequest.FromString,
                    response_serializer=order_dot_order__common__pb2.ApiResponseOrder.SerializeToString,
            ),
            'FindByActive': grpc.unary_unary_rpc_method_handler(
                    servicer.FindByActive,
                    request_deserializer=order_dot_order__query__pb2.FindAllOrderRequest.FromString,
                    response_serializer=order_dot_order__common__pb2.ApiResponsePaginationOrderDeleteAt.SerializeToString,
            ),
            'FindByTrashed': grpc.unary_unary_rpc_method_handler(
                    servicer.FindByTrashed,
                    request_deserializer=order_dot_order__query__pb2.FindAllOrderRequest.FromString,
                    response_serializer=order_dot_order__common__pb2.ApiResponsePaginationOrderDeleteAt.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'pb.order.OrderQueryService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('pb.order.OrderQueryService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class OrderQueryService:
    """Missing associated documentation comment in.proto file."""

    @staticmethod
    def FindAll(request,
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
            '/pb.order.OrderQueryService/FindAll',
            order_dot_order__query__pb2.FindAllOrderRequest.SerializeToString,
            order_dot_order__common__pb2.ApiResponsePaginationOrder.FromString,
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
    def FindById(request,
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
            '/pb.order.OrderQueryService/FindById',
            order_dot_order__common__pb2.FindByIdOrderRequest.SerializeToString,
            order_dot_order__common__pb2.ApiResponseOrder.FromString,
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
            '/pb.order.OrderQueryService/FindByActive',
            order_dot_order__query__pb2.FindAllOrderRequest.SerializeToString,
            order_dot_order__common__pb2.ApiResponsePaginationOrderDeleteAt.FromString,
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
            '/pb.order.OrderQueryService/FindByTrashed',
            order_dot_order__query__pb2.FindAllOrderRequest.SerializeToString,
            order_dot_order__common__pb2.ApiResponsePaginationOrderDeleteAt.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
