# DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from pb.order_item import order_item_command_pb2 as order__item_dot_order__item__command__pb2
from pb.order_item import order_item_common_pb2 as order__item_dot_order__item__common__pb2

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
        + ' but the generated code in order_item/order_item_command_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class OrderItemCommandServiceStub:
    """Missing associated documentation comment in.proto file."""

    def __init__(self, channel):
        """Constructor. Args: channel: A grpc.Channel."""
        self.CreateOrderItem = channel.unary_unary(
                '/pb.order_item.OrderItemCommandService/CreateOrderItem',
                request_serializer=order__item_dot_order__item__command__pb2.CreateOrderItemRecordRequest.SerializeToString,
                response_deserializer=order__item_dot_order__item__common__pb2.ApiResponseOrderItem.FromString,
                _registered_method=True)
        self.UpdateOrderItem = channel.unary_unary(
                '/pb.order_item.OrderItemCommandService/UpdateOrderItem',
                request_serializer=order__item_dot_order__item__command__pb2.UpdateOrderItemRecordRequest.SerializeToString,
                response_deserializer=order__item_dot_order__item__common__pb2.ApiResponseOrderItem.FromString,
                _registered_method=True)
        self.TrashOrderItem = channel.unary_unary(
                '/pb.order_item.OrderItemCommandService/TrashOrderItem',
                request_serializer=order__item_dot_order__item__common__pb2.FindByIdOrderItemRequest.SerializeToString,
                response_deserializer=order__item_dot_order__item__common__pb2.ApiResponseOrderItem.FromString,
                _registered_method=True)
        self.RestoreOrderItem = channel.unary_unary(
                '/pb.order_item.OrderItemCommandService/RestoreOrderItem',
                request_serializer=order__item_dot_order__item__common__pb2.FindByIdOrderItemRequest.SerializeToString,
                response_deserializer=order__item_dot_order__item__common__pb2.ApiResponseOrderItem.FromString,
                _registered_method=True)
        self.DeleteOrderItemPermanent = channel.unary_unary(
                '/pb.order_item.OrderItemCommandService/DeleteOrderItemPermanent',
                request_serializer=order__item_dot_order__item__common__pb2.FindByIdOrderItemRequest.SerializeToString,
                response_deserializer=order__item_dot_order__item__common__pb2.ApiResponseOrderItemDelete.FromString,
                _registered_method=True)
        self.RestoreAllOrdersItem = channel.unary_unary(
                '/pb.order_item.OrderItemCommandService/RestoreAllOrdersItem',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=order__item_dot_order__item__common__pb2.ApiResponseOrderItemAll.FromString,
                _registered_method=True)
        self.DeleteAllPermanentOrdersItem = channel.unary_unary(
                '/pb.order_item.OrderItemCommandService/DeleteAllPermanentOrdersItem',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=order__item_dot_order__item__common__pb2.ApiResponseOrderItemAll.FromString,
                _registered_method=True)
        self.DeleteOrderItemByOrderPermanent = channel.unary_unary(
                '/pb.order_item.OrderItemCommandService/DeleteOrderItemByOrderPermanent',
                request_serializer=order__item_dot_order__item__common__pb2.FindByIdOrderItemRequest.SerializeToString,
                response_deserializer=order__item_dot_order__item__common__pb2.ApiResponseOrderItemDelete.FromString,
                _registered_method=True)
        self.CalculateTotalPrice = channel.unary_unary(
                '/pb.order_item.OrderItemCommandService/CalculateTotalPrice',
                request_serializer=order__item_dot_order__item__command__pb2.CalculateTotalPriceRequest.SerializeToString,
                response_deserializer=order__item_dot_order__item__command__pb2.CalculateTotalPriceResponse.FromString,
                _registered_method=True)


class OrderItemCommandServiceServicer:
    """Missing associated documentation comment in.proto file."""

    def CreateOrderItem(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UpdateOrderItem(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def TrashOrderItem(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RestoreOrderItem(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteOrderItemPermanent(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RestoreAllOrdersItem(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteAllPermanentOrdersItem(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteOrderItemByOrderPermanent(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CalculateTotalPrice(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_OrderItemCommandServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'CreateOrderItem': grpc.unary_unary_rpc_method_handler(
                    servicer.CreateOrderItem,
                    request_deserializer=order__item_dot_order__item__command__pb2.CreateOrderItemRecordRequest.FromString,
                    response_serializer=order__item_dot_order__item__common__pb2.ApiResponseOrderItem.SerializeToString,
            ),
            'UpdateOrderItem': grpc.unary_unary_rpc_method_handler(
                    servicer.UpdateOrderItem,
                    request_deserializer=order__item_dot_order__item__command__pb2.UpdateOrderItemRecordRequest.FromString,
                    response_serializer=order__item_dot_order__item__common__pb2.ApiResponseOrderItem.SerializeToString,
            ),
            'TrashOrderItem': grpc.unary_unary_rpc_method_handler(
                    servicer.TrashOrderItem,
                    request_deserializer=order__item_dot_order__item__common__pb2.FindByIdOrderItemRequest.FromString,
                    response_serializer=order__item_dot_order__item__common__pb2.ApiResponseOrderItem.SerializeToString,
            ),
            'RestoreOrderItem': grpc.unary_unary_rpc_method_handler(
                    servicer.RestoreOrderItem,
                    request_deserializer=order__item_dot_order__item__common__pb2.FindByIdOrderItemRequest.FromString,
                    response_serializer=order__item_dot_order__item__common__pb2.ApiResponseOrderItem.SerializeToString,
            ),
            'DeleteOrderItemPermanent': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteOrderItemPermanent,
                    request_deserializer=order__item_dot_order__item__common__pb2.FindByIdOrderItemRequest.FromString,
                    response_serializer=order__item_dot_order__item__common__pb2.ApiResponseOrderItemDelete.SerializeToString,
            ),
            'RestoreAllOrdersItem': grpc.unary_unary_rpc_method_handler(
                    servicer.RestoreAllOrdersItem,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=order__item_dot_order__item__common__pb2.ApiResponseOrderItemAll.SerializeToString,
            ),
            'DeleteAllPermanentOrdersItem': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteAllPermanentOrdersItem,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=order__item_dot_order__item__common__pb2.ApiResponseOrderItemAll.SerializeToString,
            ),
            'DeleteOrderItemByOrderPermanent': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteOrderItemByOrderPermanent,
                    request_deserializer=order__item_dot_order__item__common__pb2.FindByIdOrderItemRequest.FromString,
                    response_serializer=order__item_dot_order__item__common__pb2.ApiResponseOrderItemDelete.SerializeToString,
            ),
            'CalculateTotalPrice': grpc.unary_unary_rpc_method_handler(
                    servicer.CalculateTotalPrice,
                    request_deserializer=order__item_dot_order__item__command__pb2.CalculateTotalPriceRequest.FromString,
                    response_serializer=order__item_dot_order__item__command__pb2.CalculateTotalPriceResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'pb.order_item.OrderItemCommandService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('pb.order_item.OrderItemCommandService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class OrderItemCommandService:
    """Missing associated documentation comment in.proto file."""

    @staticmethod
    def CreateOrderItem(request,
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
            '/pb.order_item.OrderItemCommandService/CreateOrderItem',
            order__item_dot_order__item__command__pb2.CreateOrderItemRecordRequest.SerializeToString,
            order__item_dot_order__item__common__pb2.ApiResponseOrderItem.FromString,
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
    def UpdateOrderItem(request,
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
            '/pb.order_item.OrderItemCommandService/UpdateOrderItem',
            order__item_dot_order__item__command__pb2.UpdateOrderItemRecordRequest.SerializeToString,
            order__item_dot_order__item__common__pb2.ApiResponseOrderItem.FromString,
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
    def TrashOrderItem(request,
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
            '/pb.order_item.OrderItemCommandService/TrashOrderItem',
            order__item_dot_order__item__common__pb2.FindByIdOrderItemRequest.SerializeToString,
            order__item_dot_order__item__common__pb2.ApiResponseOrderItem.FromString,
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
    def RestoreOrderItem(request,
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
            '/pb.order_item.OrderItemCommandService/RestoreOrderItem',
            order__item_dot_order__item__common__pb2.FindByIdOrderItemRequest.SerializeToString,
            order__item_dot_order__item__common__pb2.ApiResponseOrderItem.FromString,
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
    def DeleteOrderItemPermanent(request,
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
            '/pb.order_item.OrderItemCommandService/DeleteOrderItemPermanent',
            order__item_dot_order__item__common__pb2.FindByIdOrderItemRequest.SerializeToString,
            order__item_dot_order__item__common__pb2.ApiResponseOrderItemDelete.FromString,
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
    def RestoreAllOrdersItem(request,
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
            '/pb.order_item.OrderItemCommandService/RestoreAllOrdersItem',
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            order__item_dot_order__item__common__pb2.ApiResponseOrderItemAll.FromString,
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
    def DeleteAllPermanentOrdersItem(request,
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
            '/pb.order_item.OrderItemCommandService/DeleteAllPermanentOrdersItem',
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            order__item_dot_order__item__common__pb2.ApiResponseOrderItemAll.FromString,
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
    def DeleteOrderItemByOrderPermanent(request,
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
            '/pb.order_item.OrderItemCommandService/DeleteOrderItemByOrderPermanent',
            order__item_dot_order__item__common__pb2.FindByIdOrderItemRequest.SerializeToString,
            order__item_dot_order__item__common__pb2.ApiResponseOrderItemDelete.FromString,
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
    def CalculateTotalPrice(request,
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
            '/pb.order_item.OrderItemCommandService/CalculateTotalPrice',
            order__item_dot_order__item__command__pb2.CalculateTotalPriceRequest.SerializeToString,
            order__item_dot_order__item__command__pb2.CalculateTotalPriceResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
