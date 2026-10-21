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
        + ' but the generated code in category/stats/category_stats_byid_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class CategoryStatsByIdServiceStub:
    """Missing associated documentation comment in.proto file."""

    def __init__(self, channel):
        """Constructor. Args: channel: A grpc.Channel."""
        self.FindMonthlyTotalPricesById = channel.unary_unary(
                '/pb.category.stats.CategoryStatsByIdService/FindMonthlyTotalPricesById',
                request_serializer=category_dot_category__common__pb2.FindYearMonthTotalPriceById.SerializeToString,
                response_deserializer=category_dot_category__common__pb2.ApiResponseCategoryMonthlyTotalPrice.FromString,
                _registered_method=True)
        self.FindYearlyTotalPricesById = channel.unary_unary(
                '/pb.category.stats.CategoryStatsByIdService/FindYearlyTotalPricesById',
                request_serializer=category_dot_category__common__pb2.FindYearTotalPriceById.SerializeToString,
                response_deserializer=category_dot_category__common__pb2.ApiResponseCategoryYearlyTotalPrice.FromString,
                _registered_method=True)
        self.FindMonthPriceById = channel.unary_unary(
                '/pb.category.stats.CategoryStatsByIdService/FindMonthPriceById',
                request_serializer=category_dot_category__common__pb2.FindYearCategoryById.SerializeToString,
                response_deserializer=category_dot_category__common__pb2.ApiResponseCategoryMonthPrice.FromString,
                _registered_method=True)
        self.FindYearPriceById = channel.unary_unary(
                '/pb.category.stats.CategoryStatsByIdService/FindYearPriceById',
                request_serializer=category_dot_category__common__pb2.FindYearCategoryById.SerializeToString,
                response_deserializer=category_dot_category__common__pb2.ApiResponseCategoryYearPrice.FromString,
                _registered_method=True)


class CategoryStatsByIdServiceServicer:
    """Missing associated documentation comment in.proto file."""

    def FindMonthlyTotalPricesById(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def FindYearlyTotalPricesById(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def FindMonthPriceById(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def FindYearPriceById(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_CategoryStatsByIdServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'FindMonthlyTotalPricesById': grpc.unary_unary_rpc_method_handler(
                    servicer.FindMonthlyTotalPricesById,
                    request_deserializer=category_dot_category__common__pb2.FindYearMonthTotalPriceById.FromString,
                    response_serializer=category_dot_category__common__pb2.ApiResponseCategoryMonthlyTotalPrice.SerializeToString,
            ),
            'FindYearlyTotalPricesById': grpc.unary_unary_rpc_method_handler(
                    servicer.FindYearlyTotalPricesById,
                    request_deserializer=category_dot_category__common__pb2.FindYearTotalPriceById.FromString,
                    response_serializer=category_dot_category__common__pb2.ApiResponseCategoryYearlyTotalPrice.SerializeToString,
            ),
            'FindMonthPriceById': grpc.unary_unary_rpc_method_handler(
                    servicer.FindMonthPriceById,
                    request_deserializer=category_dot_category__common__pb2.FindYearCategoryById.FromString,
                    response_serializer=category_dot_category__common__pb2.ApiResponseCategoryMonthPrice.SerializeToString,
            ),
            'FindYearPriceById': grpc.unary_unary_rpc_method_handler(
                    servicer.FindYearPriceById,
                    request_deserializer=category_dot_category__common__pb2.FindYearCategoryById.FromString,
                    response_serializer=category_dot_category__common__pb2.ApiResponseCategoryYearPrice.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'pb.category.stats.CategoryStatsByIdService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('pb.category.stats.CategoryStatsByIdService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class CategoryStatsByIdService:
    """Missing associated documentation comment in.proto file."""

    @staticmethod
    def FindMonthlyTotalPricesById(request,
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
            '/pb.category.stats.CategoryStatsByIdService/FindMonthlyTotalPricesById',
            category_dot_category__common__pb2.FindYearMonthTotalPriceById.SerializeToString,
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
    def FindYearlyTotalPricesById(request,
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
            '/pb.category.stats.CategoryStatsByIdService/FindYearlyTotalPricesById',
            category_dot_category__common__pb2.FindYearTotalPriceById.SerializeToString,
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
    def FindMonthPriceById(request,
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
            '/pb.category.stats.CategoryStatsByIdService/FindMonthPriceById',
            category_dot_category__common__pb2.FindYearCategoryById.SerializeToString,
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
    def FindYearPriceById(request,
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
            '/pb.category.stats.CategoryStatsByIdService/FindYearPriceById',
            category_dot_category__common__pb2.FindYearCategoryById.SerializeToString,
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
