# DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from pb.order import order_common_pb2 as order_dot_order__common__pb2
from pb.order.stats import order_stats_pb2 as order_dot_stats_dot_order__stats__pb2

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
        + ' but the generated code in order/stats/order_stats_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class OrderStatsServiceStub:
    """Missing associated documentation comment in.proto file."""

    def __init__(self, channel):
        """Constructor. Args: channel: A grpc.Channel."""
        self.FindMonthlyTotalRevenue = channel.unary_unary(
                '/pb.order.stats.OrderStatsService/FindMonthlyTotalRevenue',
                request_serializer=order_dot_stats_dot_order__stats__pb2.FindYearMonthTotalRevenue.SerializeToString,
                response_deserializer=order_dot_order__common__pb2.ApiResponseOrderMonthlyTotalRevenue.FromString,
                _registered_method=True)
        self.FindYearlyTotalRevenue = channel.unary_unary(
                '/pb.order.stats.OrderStatsService/FindYearlyTotalRevenue',
                request_serializer=order_dot_stats_dot_order__stats__pb2.FindYearTotalRevenue.SerializeToString,
                response_deserializer=order_dot_order__common__pb2.ApiResponseOrderYearlyTotalRevenue.FromString,
                _registered_method=True)
        self.FindMonthlyRevenue = channel.unary_unary(
                '/pb.order.stats.OrderStatsService/FindMonthlyRevenue',
                request_serializer=order_dot_stats_dot_order__stats__pb2.FindYearOrder.SerializeToString,
                response_deserializer=order_dot_order__common__pb2.ApiResponseOrderMonthly.FromString,
                _registered_method=True)
        self.FindYearlyRevenue = channel.unary_unary(
                '/pb.order.stats.OrderStatsService/FindYearlyRevenue',
                request_serializer=order_dot_stats_dot_order__stats__pb2.FindYearOrder.SerializeToString,
                response_deserializer=order_dot_order__common__pb2.ApiResponseOrderYearly.FromString,
                _registered_method=True)


class OrderStatsServiceServicer:
    """Missing associated documentation comment in.proto file."""

    def FindMonthlyTotalRevenue(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def FindYearlyTotalRevenue(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def FindMonthlyRevenue(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def FindYearlyRevenue(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_OrderStatsServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'FindMonthlyTotalRevenue': grpc.unary_unary_rpc_method_handler(
                    servicer.FindMonthlyTotalRevenue,
                    request_deserializer=order_dot_stats_dot_order__stats__pb2.FindYearMonthTotalRevenue.FromString,
                    response_serializer=order_dot_order__common__pb2.ApiResponseOrderMonthlyTotalRevenue.SerializeToString,
            ),
            'FindYearlyTotalRevenue': grpc.unary_unary_rpc_method_handler(
                    servicer.FindYearlyTotalRevenue,
                    request_deserializer=order_dot_stats_dot_order__stats__pb2.FindYearTotalRevenue.FromString,
                    response_serializer=order_dot_order__common__pb2.ApiResponseOrderYearlyTotalRevenue.SerializeToString,
            ),
            'FindMonthlyRevenue': grpc.unary_unary_rpc_method_handler(
                    servicer.FindMonthlyRevenue,
                    request_deserializer=order_dot_stats_dot_order__stats__pb2.FindYearOrder.FromString,
                    response_serializer=order_dot_order__common__pb2.ApiResponseOrderMonthly.SerializeToString,
            ),
            'FindYearlyRevenue': grpc.unary_unary_rpc_method_handler(
                    servicer.FindYearlyRevenue,
                    request_deserializer=order_dot_stats_dot_order__stats__pb2.FindYearOrder.FromString,
                    response_serializer=order_dot_order__common__pb2.ApiResponseOrderYearly.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'pb.order.stats.OrderStatsService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('pb.order.stats.OrderStatsService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class OrderStatsService:
    """Missing associated documentation comment in.proto file."""

    @staticmethod
    def FindMonthlyTotalRevenue(request,
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
            '/pb.order.stats.OrderStatsService/FindMonthlyTotalRevenue',
            order_dot_stats_dot_order__stats__pb2.FindYearMonthTotalRevenue.SerializeToString,
            order_dot_order__common__pb2.ApiResponseOrderMonthlyTotalRevenue.FromString,
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
    def FindYearlyTotalRevenue(request,
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
            '/pb.order.stats.OrderStatsService/FindYearlyTotalRevenue',
            order_dot_stats_dot_order__stats__pb2.FindYearTotalRevenue.SerializeToString,
            order_dot_order__common__pb2.ApiResponseOrderYearlyTotalRevenue.FromString,
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
    def FindMonthlyRevenue(request,
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
            '/pb.order.stats.OrderStatsService/FindMonthlyRevenue',
            order_dot_stats_dot_order__stats__pb2.FindYearOrder.SerializeToString,
            order_dot_order__common__pb2.ApiResponseOrderMonthly.FromString,
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
    def FindYearlyRevenue(request,
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
            '/pb.order.stats.OrderStatsService/FindYearlyRevenue',
            order_dot_stats_dot_order__stats__pb2.FindYearOrder.SerializeToString,
            order_dot_order__common__pb2.ApiResponseOrderYearly.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
