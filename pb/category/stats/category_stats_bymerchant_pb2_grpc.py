# DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from pb.category import category_common_pb2 as category_dot_category__common__pb2

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
        + ' but the generated code in category/stats/category_stats_bymerchant_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class CategoryStatsByMerchantServiceStub:
    """Missing associated documentation comment in.proto file."""

    def __init__(self, channel):
        """Constructor. Args: channel: A grpc.Channel."""
        self.FindMonthlyTotalPricesByMerchant = channel.unary_unary(
                '/pb.category.stats.CategoryStatsByMerchantService/FindMonthlyTotalPricesByMerchant',
                request_serializer=category_dot_category__common__pb2.FindYearMonthTotalPriceByMerchant.SerializeToString,
                response_deserializer=category_dot_category__common__pb2.ApiResponseCategoryMonthlyTotalPrice.FromString,
                _registered_method=True)
        self.FindYearlyTotalPricesByMerchant = channel.unary_unary(
                '/pb.category.stats.CategoryStatsByMerchantService/FindYearlyTotalPricesByMerchant',
                request_serializer=category_dot_category__common__pb2.FindYearTotalPriceByMerchant.SerializeToString,
                response_deserializer=category_dot_category__common__pb2.ApiResponseCategoryYearlyTotalPrice.FromString,
                _registered_method=True)
        self.FindMonthPriceByMerchant = channel.unary_unary(
                '/pb.category.stats.CategoryStatsByMerchantService/FindMonthPriceByMerchant',
                request_serializer=category_dot_category__common__pb2.FindYearCategoryByMerchant.SerializeToString,
                response_deserializer=category_dot_category__common__pb2.ApiResponseCategoryMonthPrice.FromString,
                _registered_method=True)
        self.FindYearPriceByMerchant = channel.unary_unary(
                '/pb.category.stats.CategoryStatsByMerchantService/FindYearPriceByMerchant',
                request_serializer=category_dot_category__common__pb2.FindYearCategoryByMerchant.SerializeToString,
                response_deserializer=category_dot_category__common__pb2.ApiResponseCategoryYearPrice.FromString,
                _registered_method=True)


class CategoryStatsByMerchantServiceServicer:
    """Missing associated documentation comment in.proto file."""

    def FindMonthlyTotalPricesByMerchant(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def FindYearlyTotalPricesByMerchant(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def FindMonthPriceByMerchant(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def FindYearPriceByMerchant(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_CategoryStatsByMerchantServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'FindMonthlyTotalPricesByMerchant': grpc.unary_unary_rpc_method_handler(
                    servicer.FindMonthlyTotalPricesByMerchant,
                    request_deserializer=category_dot_category__common__pb2.FindYearMonthTotalPriceByMerchant.FromString,
                    response_serializer=category_dot_category__common__pb2.ApiResponseCategoryMonthlyTotalPrice.SerializeToString,
            ),
            'FindYearlyTotalPricesByMerchant': grpc.unary_unary_rpc_method_handler(
                    servicer.FindYearlyTotalPricesByMerchant,
                    request_deserializer=category_dot_category__common__pb2.FindYearTotalPriceByMerchant.FromString,
                    response_serializer=category_dot_category__common__pb2.ApiResponseCategoryYearlyTotalPrice.SerializeToString,
            ),
            'FindMonthPriceByMerchant': grpc.unary_unary_rpc_method_handler(
                    servicer.FindMonthPriceByMerchant,
                    request_deserializer=category_dot_category__common__pb2.FindYearCategoryByMerchant.FromString,
                    response_serializer=category_dot_category__common__pb2.ApiResponseCategoryMonthPrice.SerializeToString,
            ),
            'FindYearPriceByMerchant': grpc.unary_unary_rpc_method_handler(
                    servicer.FindYearPriceByMerchant,
                    request_deserializer=category_dot_category__common__pb2.FindYearCategoryByMerchant.FromString,
                    response_serializer=category_dot_category__common__pb2.ApiResponseCategoryYearPrice.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'pb.category.stats.CategoryStatsByMerchantService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('pb.category.stats.CategoryStatsByMerchantService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class CategoryStatsByMerchantService:
    """Missing associated documentation comment in.proto file."""

    @staticmethod
    def FindMonthlyTotalPricesByMerchant(request,
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
            '/pb.category.stats.CategoryStatsByMerchantService/FindMonthlyTotalPricesByMerchant',
            category_dot_category__common__pb2.FindYearMonthTotalPriceByMerchant.SerializeToString,
            category_dot_category__common__pb2.ApiResponseCategoryMonthlyTotalPrice.FromString,
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
    def FindYearlyTotalPricesByMerchant(request,
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
            '/pb.category.stats.CategoryStatsByMerchantService/FindYearlyTotalPricesByMerchant',
            category_dot_category__common__pb2.FindYearTotalPriceByMerchant.SerializeToString,
            category_dot_category__common__pb2.ApiResponseCategoryYearlyTotalPrice.FromString,
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
    def FindMonthPriceByMerchant(request,
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
            '/pb.category.stats.CategoryStatsByMerchantService/FindMonthPriceByMerchant',
            category_dot_category__common__pb2.FindYearCategoryByMerchant.SerializeToString,
            category_dot_category__common__pb2.ApiResponseCategoryMonthPrice.FromString,
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
    def FindYearPriceByMerchant(request,
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
            '/pb.category.stats.CategoryStatsByMerchantService/FindYearPriceByMerchant',
            category_dot_category__common__pb2.FindYearCategoryByMerchant.SerializeToString,
            category_dot_category__common__pb2.ApiResponseCategoryYearPrice.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
