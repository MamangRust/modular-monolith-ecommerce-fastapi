# DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from pb.order_item import order_item_common_pb2 as order__item_dot_order__item__common__pb2
from pb.order_item import order_item_query_pb2 as order__item_dot_order__item__query__pb2

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
        + ' but the generated code in order_item/order_item_query_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class OrderItemQueryServiceStub:
    """Missing associated documentation comment in.proto file."""

    def __init__(self, channel):
        """Constructor. Args: channel: A grpc.Channel."""
        self.FindAll = channel.unary_unary(
                '/pb.order_item.OrderItemQueryService/FindAll',
                request_serializer=order__item_dot_order__item__query__pb2.FindAllOrderItemRequest.SerializeToString,
                response_deserializer=order__item_dot_order__item__common__pb2.ApiResponsePaginationOrderItem.FromString,
                _registered_method=True)
        self.FindByActive = channel.unary_unary(
                '/pb.order_item.OrderItemQueryService/FindByActive',
                request_serializer=order__item_dot_order__item__query__pb2.FindAllOrderItemRequest.SerializeToString,
                response_deserializer=order__item_dot_order__item__common__pb2.ApiResponsePaginationOrderItemDeleteAt.FromString,
                _registered_method=True)
        self.FindByTrashed = channel.unary_unary(
                '/pb.order_item.OrderItemQueryService/FindByTrashed',
                request_serializer=order__item_dot_order__item__query__pb2.FindAllOrderItemRequest.SerializeToString,
                response_deserializer=order__item_dot_order__item__common__pb2.ApiResponsePaginationOrderItemDeleteAt.FromString,
                _registered_method=True)
        self.FindOrderItemByOrder = channel.unary_unary(
                '/pb.order_item.OrderItemQueryService/FindOrderItemByOrder',
                request_serializer=order__item_dot_order__item__common__pb2.FindByIdOrderItemRequest.SerializeToString,
                response_deserializer=order__item_dot_order__item__common__pb2.ApiResponsesOrderItem.FromString,
                _registered_method=True)


class OrderItemQueryServiceServicer:
    """Missing associated documentation comment in.proto file."""

    def FindAll(self, request, context):
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

    def FindOrderItemByOrder(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_OrderItemQueryServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'FindAll': grpc.unary_unary_rpc_method_handler(
                    servicer.FindAll,
                    request_deserializer=order__item_dot_order__item__query__pb2.FindAllOrderItemRequest.FromString,
                    response_serializer=order__item_dot_order__item__common__pb2.ApiResponsePaginationOrderItem.SerializeToString,
            ),
            'FindByActive': grpc.unary_unary_rpc_method_handler(
                    servicer.FindByActive,
                    request_deserializer=order__item_dot_order__item__query__pb2.FindAllOrderItemRequest.FromString,
                    response_serializer=order__item_dot_order__item__common__pb2.ApiResponsePaginationOrderItemDeleteAt.SerializeToString,
            ),
            'FindByTrashed': grpc.unary_unary_rpc_method_handler(
                    servicer.FindByTrashed,
                    request_deserializer=order__item_dot_order__item__query__pb2.FindAllOrderItemRequest.FromString,
                    response_serializer=order__item_dot_order__item__common__pb2.ApiResponsePaginationOrderItemDeleteAt.SerializeToString,
            ),
            'FindOrderItemByOrder': grpc.unary_unary_rpc_method_handler(
                    servicer.FindOrderItemByOrder,
                    request_deserializer=order__item_dot_order__item__common__pb2.FindByIdOrderItemRequest.FromString,
                    response_serializer=order__item_dot_order__item__common__pb2.ApiResponsesOrderItem.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'pb.order_item.OrderItemQueryService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('pb.order_item.OrderItemQueryService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class OrderItemQueryService:
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
            '/pb.order_item.OrderItemQueryService/FindAll',
            order__item_dot_order__item__query__pb2.FindAllOrderItemRequest.SerializeToString,
            order__item_dot_order__item__common__pb2.ApiResponsePaginationOrderItem.FromString,
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
            '/pb.order_item.OrderItemQueryService/FindByActive',
            order__item_dot_order__item__query__pb2.FindAllOrderItemRequest.SerializeToString,
            order__item_dot_order__item__common__pb2.ApiResponsePaginationOrderItemDeleteAt.FromString,
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
            '/pb.order_item.OrderItemQueryService/FindByTrashed',
            order__item_dot_order__item__query__pb2.FindAllOrderItemRequest.SerializeToString,
            order__item_dot_order__item__common__pb2.ApiResponsePaginationOrderItemDeleteAt.FromString,
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
    def FindOrderItemByOrder(request,
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
            '/pb.order_item.OrderItemQueryService/FindOrderItemByOrder',
            order__item_dot_order__item__common__pb2.FindByIdOrderItemRequest.SerializeToString,
            order__item_dot_order__item__common__pb2.ApiResponsesOrderItem.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
