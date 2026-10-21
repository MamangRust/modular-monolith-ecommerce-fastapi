# DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from pb.order import order_command_pb2 as order_dot_order__command__pb2
from pb.order import order_common_pb2 as order_dot_order__common__pb2

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
        + ' but the generated code in order/order_command_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class OrderCommandServiceStub:
    """Missing associated documentation comment in.proto file."""

    def __init__(self, channel):
        """Constructor. Args: channel: A grpc.Channel."""
        self.Create = channel.unary_unary(
                '/pb.order.OrderCommandService/Create',
                request_serializer=order_dot_order__command__pb2.CreateOrderRequest.SerializeToString,
                response_deserializer=order_dot_order__common__pb2.ApiResponseOrder.FromString,
                _registered_method=True)
        self.Update = channel.unary_unary(
                '/pb.order.OrderCommandService/Update',
                request_serializer=order_dot_order__command__pb2.UpdateOrderRequest.SerializeToString,
                response_deserializer=order_dot_order__common__pb2.ApiResponseOrder.FromString,
                _registered_method=True)
        self.TrashedOrder = channel.unary_unary(
                '/pb.order.OrderCommandService/TrashedOrder',
                request_serializer=order_dot_order__common__pb2.FindByIdOrderRequest.SerializeToString,
                response_deserializer=order_dot_order__common__pb2.ApiResponseOrderDeleteAt.FromString,
                _registered_method=True)
        self.RestoreOrder = channel.unary_unary(
                '/pb.order.OrderCommandService/RestoreOrder',
                request_serializer=order_dot_order__common__pb2.FindByIdOrderRequest.SerializeToString,
                response_deserializer=order_dot_order__common__pb2.ApiResponseOrderDeleteAt.FromString,
                _registered_method=True)
        self.DeleteOrderPermanent = channel.unary_unary(
                '/pb.order.OrderCommandService/DeleteOrderPermanent',
                request_serializer=order_dot_order__common__pb2.FindByIdOrderRequest.SerializeToString,
                response_deserializer=order_dot_order__common__pb2.ApiResponseOrderDelete.FromString,
                _registered_method=True)
        self.RestoreAllOrder = channel.unary_unary(
                '/pb.order.OrderCommandService/RestoreAllOrder',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=order_dot_order__common__pb2.ApiResponseOrderAll.FromString,
                _registered_method=True)
        self.DeleteAllOrderPermanent = channel.unary_unary(
                '/pb.order.OrderCommandService/DeleteAllOrderPermanent',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=order_dot_order__common__pb2.ApiResponseOrderAll.FromString,
                _registered_method=True)


class OrderCommandServiceServicer:
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

    def TrashedOrder(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RestoreOrder(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteOrderPermanent(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RestoreAllOrder(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteAllOrderPermanent(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_OrderCommandServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Create': grpc.unary_unary_rpc_method_handler(
                    servicer.Create,
                    request_deserializer=order_dot_order__command__pb2.CreateOrderRequest.FromString,
                    response_serializer=order_dot_order__common__pb2.ApiResponseOrder.SerializeToString,
            ),
            'Update': grpc.unary_unary_rpc_method_handler(
                    servicer.Update,
                    request_deserializer=order_dot_order__command__pb2.UpdateOrderRequest.FromString,
                    response_serializer=order_dot_order__common__pb2.ApiResponseOrder.SerializeToString,
            ),
            'TrashedOrder': grpc.unary_unary_rpc_method_handler(
                    servicer.TrashedOrder,
                    request_deserializer=order_dot_order__common__pb2.FindByIdOrderRequest.FromString,
                    response_serializer=order_dot_order__common__pb2.ApiResponseOrderDeleteAt.SerializeToString,
            ),
            'RestoreOrder': grpc.unary_unary_rpc_method_handler(
                    servicer.RestoreOrder,
                    request_deserializer=order_dot_order__common__pb2.FindByIdOrderRequest.FromString,
                    response_serializer=order_dot_order__common__pb2.ApiResponseOrderDeleteAt.SerializeToString,
            ),
            'DeleteOrderPermanent': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteOrderPermanent,
                    request_deserializer=order_dot_order__common__pb2.FindByIdOrderRequest.FromString,
                    response_serializer=order_dot_order__common__pb2.ApiResponseOrderDelete.SerializeToString,
            ),
            'RestoreAllOrder': grpc.unary_unary_rpc_method_handler(
                    servicer.RestoreAllOrder,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=order_dot_order__common__pb2.ApiResponseOrderAll.SerializeToString,
            ),
            'DeleteAllOrderPermanent': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteAllOrderPermanent,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=order_dot_order__common__pb2.ApiResponseOrderAll.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'pb.order.OrderCommandService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('pb.order.OrderCommandService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class OrderCommandService:
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
            '/pb.order.OrderCommandService/Create',
            order_dot_order__command__pb2.CreateOrderRequest.SerializeToString,
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
            '/pb.order.OrderCommandService/Update',
            order_dot_order__command__pb2.UpdateOrderRequest.SerializeToString,
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
    def TrashedOrder(request,
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
            '/pb.order.OrderCommandService/TrashedOrder',
            order_dot_order__common__pb2.FindByIdOrderRequest.SerializeToString,
            order_dot_order__common__pb2.ApiResponseOrderDeleteAt.FromString,
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
    def RestoreOrder(request,
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
            '/pb.order.OrderCommandService/RestoreOrder',
            order_dot_order__common__pb2.FindByIdOrderRequest.SerializeToString,
            order_dot_order__common__pb2.ApiResponseOrderDeleteAt.FromString,
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
    def DeleteOrderPermanent(request,
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
            '/pb.order.OrderCommandService/DeleteOrderPermanent',
            order_dot_order__common__pb2.FindByIdOrderRequest.SerializeToString,
            order_dot_order__common__pb2.ApiResponseOrderDelete.FromString,
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
    def RestoreAllOrder(request,
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
            '/pb.order.OrderCommandService/RestoreAllOrder',
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            order_dot_order__common__pb2.ApiResponseOrderAll.FromString,
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
    def DeleteAllOrderPermanent(request,
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
            '/pb.order.OrderCommandService/DeleteAllOrderPermanent',
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            order_dot_order__common__pb2.ApiResponseOrderAll.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
