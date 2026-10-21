# DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from pb.order import order_common_pb2 as order_dot_order__common__pb2
from pb.order.stats import order_statsbymerchant_pb2 as order_dot_stats_dot_order__statsbymerchant__pb2

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
        + ' but the generated code in order/stats/order_statsbymerchant_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class OrderStatsByMerchantServiceStub:
    """Missing associated documentation comment in.proto file."""

    def __init__(self, channel):
        """Constructor. Args: channel: A grpc.Channel."""
        self.FindMonthlyTotalRevenueByMerchant = channel.unary_unary(
                '/pb.order.stats.OrderStatsByMerchantService/FindMonthlyTotalRevenueByMerchant',
                request_serializer=order_dot_stats_dot_order__statsbymerchant__pb2.FindYearMonthTotalRevenueByMerchant.SerializeToString,
                response_deserializer=order_dot_order__common__pb2.ApiResponseOrderMonthlyTotalRevenue.FromString,
                _registered_method=True)
        self.FindYearlyTotalRevenueByMerchant = channel.unary_unary(
                '/pb.order.stats.OrderStatsByMerchantService/FindYearlyTotalRevenueByMerchant',
                request_serializer=order_dot_stats_dot_order__statsbymerchant__pb2.FindYearTotalRevenueByMerchant.SerializeToString,
                response_deserializer=order_dot_order__common__pb2.ApiResponseOrderYearlyTotalRevenue.FromString,
                _registered_method=True)
        self.FindMonthlyRevenueByMerchant = channel.unary_unary(
                '/pb.order.stats.OrderStatsByMerchantService/FindMonthlyRevenueByMerchant',
                request_serializer=order_dot_stats_dot_order__statsbymerchant__pb2.FindYearOrderByMerchant.SerializeToString,
                response_deserializer=order_dot_order__common__pb2.ApiResponseOrderMonthly.FromString,
                _registered_method=True)
        self.FindYearlyRevenueByMerchant = channel.unary_unary(
                '/pb.order.stats.OrderStatsByMerchantService/FindYearlyRevenueByMerchant',
                request_serializer=order_dot_stats_dot_order__statsbymerchant__pb2.FindYearOrderByMerchant.SerializeToString,
                response_deserializer=order_dot_order__common__pb2.ApiResponseOrderYearly.FromString,
                _registered_method=True)


class OrderStatsByMerchantServiceServicer:
    """Missing associated documentation comment in.proto file."""

    def FindMonthlyTotalRevenueByMerchant(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def FindYearlyTotalRevenueByMerchant(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def FindMonthlyRevenueByMerchant(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def FindYearlyRevenueByMerchant(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_OrderStatsByMerchantServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'FindMonthlyTotalRevenueByMerchant': grpc.unary_unary_rpc_method_handler(
                    servicer.FindMonthlyTotalRevenueByMerchant,
                    request_deserializer=order_dot_stats_dot_order__statsbymerchant__pb2.FindYearMonthTotalRevenueByMerchant.FromString,
                    response_serializer=order_dot_order__common__pb2.ApiResponseOrderMonthlyTotalRevenue.SerializeToString,
            ),
            'FindYearlyTotalRevenueByMerchant': grpc.unary_unary_rpc_method_handler(
                    servicer.FindYearlyTotalRevenueByMerchant,
                    request_deserializer=order_dot_stats_dot_order__statsbymerchant__pb2.FindYearTotalRevenueByMerchant.FromString,
                    response_serializer=order_dot_order__common__pb2.ApiResponseOrderYearlyTotalRevenue.SerializeToString,
            ),
            'FindMonthlyRevenueByMerchant': grpc.unary_unary_rpc_method_handler(
                    servicer.FindMonthlyRevenueByMerchant,
                    request_deserializer=order_dot_stats_dot_order__statsbymerchant__pb2.FindYearOrderByMerchant.FromString,
                    response_serializer=order_dot_order__common__pb2.ApiResponseOrderMonthly.SerializeToString,
            ),
            'FindYearlyRevenueByMerchant': grpc.unary_unary_rpc_method_handler(
                    servicer.FindYearlyRevenueByMerchant,
                    request_deserializer=order_dot_stats_dot_order__statsbymerchant__pb2.FindYearOrderByMerchant.FromString,
                    response_serializer=order_dot_order__common__pb2.ApiResponseOrderYearly.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'pb.order.stats.OrderStatsByMerchantService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('pb.order.stats.OrderStatsByMerchantService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class OrderStatsByMerchantService:
    """Missing associated documentation comment in.proto file."""

    @staticmethod
    def FindMonthlyTotalRevenueByMerchant(request,
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
            '/pb.order.stats.OrderStatsByMerchantService/FindMonthlyTotalRevenueByMerchant',
            order_dot_stats_dot_order__statsbymerchant__pb2.FindYearMonthTotalRevenueByMerchant.SerializeToString,
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
    def FindYearlyTotalRevenueByMerchant(request,
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
            '/pb.order.stats.OrderStatsByMerchantService/FindYearlyTotalRevenueByMerchant',
            order_dot_stats_dot_order__statsbymerchant__pb2.FindYearTotalRevenueByMerchant.SerializeToString,
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
    def FindMonthlyRevenueByMerchant(request,
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
            '/pb.order.stats.OrderStatsByMerchantService/FindMonthlyRevenueByMerchant',
            order_dot_stats_dot_order__statsbymerchant__pb2.FindYearOrderByMerchant.SerializeToString,
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
    def FindYearlyRevenueByMerchant(request,
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
            '/pb.order.stats.OrderStatsByMerchantService/FindYearlyRevenueByMerchant',
            order_dot_stats_dot_order__statsbymerchant__pb2.FindYearOrderByMerchant.SerializeToString,
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
