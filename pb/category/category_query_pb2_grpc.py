# DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from pb.category import category_common_pb2 as category_dot_category__common__pb2
from pb.category import category_query_pb2 as category_dot_category__query__pb2

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
        + ' but the generated code in category/category_query_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class CategoryQueryServiceStub:
    """Missing associated documentation comment in.proto file."""

    def __init__(self, channel):
        """Constructor. Args: channel: A grpc.Channel."""
        self.FindMonthlyTotalPrices = channel.unary_unary(
                '/pb.category.CategoryQueryService/FindMonthlyTotalPrices',
                request_serializer=category_dot_category__common__pb2.FindYearMonthTotalPrices.SerializeToString,
                response_deserializer=category_dot_category__common__pb2.ApiResponseCategoryMonthlyTotalPrice.FromString,
                _registered_method=True)
        self.FindYearlyTotalPrices = channel.unary_unary(
                '/pb.category.CategoryQueryService/FindYearlyTotalPrices',
                request_serializer=category_dot_category__common__pb2.FindYearTotalPrices.SerializeToString,
                response_deserializer=category_dot_category__common__pb2.ApiResponseCategoryYearlyTotalPrice.FromString,
                _registered_method=True)
        self.FindMonthlyTotalPricesById = channel.unary_unary(
                '/pb.category.CategoryQueryService/FindMonthlyTotalPricesById',
                request_serializer=category_dot_category__common__pb2.FindYearMonthTotalPriceById.SerializeToString,
                response_deserializer=category_dot_category__common__pb2.ApiResponseCategoryMonthlyTotalPrice.FromString,
                _registered_method=True)
        self.FindYearlyTotalPricesById = channel.unary_unary(
                '/pb.category.CategoryQueryService/FindYearlyTotalPricesById',
                request_serializer=category_dot_category__common__pb2.FindYearTotalPriceById.SerializeToString,
                response_deserializer=category_dot_category__common__pb2.ApiResponseCategoryYearlyTotalPrice.FromString,
                _registered_method=True)
        self.FindMonthlyTotalPricesByMerchant = channel.unary_unary(
                '/pb.category.CategoryQueryService/FindMonthlyTotalPricesByMerchant',
                request_serializer=category_dot_category__common__pb2.FindYearMonthTotalPriceByMerchant.SerializeToString,
                response_deserializer=category_dot_category__common__pb2.ApiResponseCategoryMonthlyTotalPrice.FromString,
                _registered_method=True)
        self.FindYearlyTotalPricesByMerchant = channel.unary_unary(
                '/pb.category.CategoryQueryService/FindYearlyTotalPricesByMerchant',
                request_serializer=category_dot_category__common__pb2.FindYearTotalPriceByMerchant.SerializeToString,
                response_deserializer=category_dot_category__common__pb2.ApiResponseCategoryYearlyTotalPrice.FromString,
                _registered_method=True)
        self.FindMonthPrice = channel.unary_unary(
                '/pb.category.CategoryQueryService/FindMonthPrice',
                request_serializer=category_dot_category__common__pb2.FindYearCategory.SerializeToString,
                response_deserializer=category_dot_category__common__pb2.ApiResponseCategoryMonthPrice.FromString,
                _registered_method=True)
        self.FindYearPrice = channel.unary_unary(
                '/pb.category.CategoryQueryService/FindYearPrice',
                request_serializer=category_dot_category__common__pb2.FindYearCategory.SerializeToString,
                response_deserializer=category_dot_category__common__pb2.ApiResponseCategoryYearPrice.FromString,
                _registered_method=True)
        self.FindMonthPriceByMerchant = channel.unary_unary(
                '/pb.category.CategoryQueryService/FindMonthPriceByMerchant',
                request_serializer=category_dot_category__common__pb2.FindYearCategoryByMerchant.SerializeToString,
                response_deserializer=category_dot_category__common__pb2.ApiResponseCategoryMonthPrice.FromString,
                _registered_method=True)
        self.FindYearPriceByMerchant = channel.unary_unary(
                '/pb.category.CategoryQueryService/FindYearPriceByMerchant',
                request_serializer=category_dot_category__common__pb2.FindYearCategoryByMerchant.SerializeToString,
                response_deserializer=category_dot_category__common__pb2.ApiResponseCategoryYearPrice.FromString,
                _registered_method=True)
        self.FindMonthPriceById = channel.unary_unary(
                '/pb.category.CategoryQueryService/FindMonthPriceById',
                request_serializer=category_dot_category__common__pb2.FindYearCategoryById.SerializeToString,
                response_deserializer=category_dot_category__common__pb2.ApiResponseCategoryMonthPrice.FromString,
                _registered_method=True)
        self.FindYearPriceById = channel.unary_unary(
                '/pb.category.CategoryQueryService/FindYearPriceById',
                request_serializer=category_dot_category__common__pb2.FindYearCategoryById.SerializeToString,
                response_deserializer=category_dot_category__common__pb2.ApiResponseCategoryYearPrice.FromString,
                _registered_method=True)
        self.FindAll = channel.unary_unary(
                '/pb.category.CategoryQueryService/FindAll',
                request_serializer=category_dot_category__query__pb2.FindAllCategoryRequest.SerializeToString,
                response_deserializer=category_dot_category__common__pb2.ApiResponsePaginationCategory.FromString,
                _registered_method=True)
        self.FindById = channel.unary_unary(
                '/pb.category.CategoryQueryService/FindById',
                request_serializer=category_dot_category__common__pb2.FindByIdCategoryRequest.SerializeToString,
                response_deserializer=category_dot_category__common__pb2.ApiResponseCategory.FromString,
                _registered_method=True)
        self.FindByActive = channel.unary_unary(
                '/pb.category.CategoryQueryService/FindByActive',
                request_serializer=category_dot_category__query__pb2.FindAllCategoryRequest.SerializeToString,
                response_deserializer=category_dot_category__common__pb2.ApiResponsePaginationCategoryDeleteAt.FromString,
                _registered_method=True)
        self.FindByTrashed = channel.unary_unary(
                '/pb.category.CategoryQueryService/FindByTrashed',
                request_serializer=category_dot_category__query__pb2.FindAllCategoryRequest.SerializeToString,
                response_deserializer=category_dot_category__common__pb2.ApiResponsePaginationCategoryDeleteAt.FromString,
                _registered_method=True)


class CategoryQueryServiceServicer:
    """Missing associated documentation comment in.proto file."""

    def FindMonthlyTotalPrices(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def FindYearlyTotalPrices(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

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

    def FindMonthPrice(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def FindYearPrice(self, request, context):
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


def add_CategoryQueryServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'FindMonthlyTotalPrices': grpc.unary_unary_rpc_method_handler(
                    servicer.FindMonthlyTotalPrices,
                    request_deserializer=category_dot_category__common__pb2.FindYearMonthTotalPrices.FromString,
                    response_serializer=category_dot_category__common__pb2.ApiResponseCategoryMonthlyTotalPrice.SerializeToString,
            ),
            'FindYearlyTotalPrices': grpc.unary_unary_rpc_method_handler(
                    servicer.FindYearlyTotalPrices,
                    request_deserializer=category_dot_category__common__pb2.FindYearTotalPrices.FromString,
                    response_serializer=category_dot_category__common__pb2.ApiResponseCategoryYearlyTotalPrice.SerializeToString,
            ),
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
            'FindMonthPrice': grpc.unary_unary_rpc_method_handler(
                    servicer.FindMonthPrice,
                    request_deserializer=category_dot_category__common__pb2.FindYearCategory.FromString,
                    response_serializer=category_dot_category__common__pb2.ApiResponseCategoryMonthPrice.SerializeToString,
            ),
            'FindYearPrice': grpc.unary_unary_rpc_method_handler(
                    servicer.FindYearPrice,
                    request_deserializer=category_dot_category__common__pb2.FindYearCategory.FromString,
                    response_serializer=category_dot_category__common__pb2.ApiResponseCategoryYearPrice.SerializeToString,
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
            'FindAll': grpc.unary_unary_rpc_method_handler(
                    servicer.FindAll,
                    request_deserializer=category_dot_category__query__pb2.FindAllCategoryRequest.FromString,
                    response_serializer=category_dot_category__common__pb2.ApiResponsePaginationCategory.SerializeToString,
            ),
            'FindById': grpc.unary_unary_rpc_method_handler(
                    servicer.FindById,
                    request_deserializer=category_dot_category__common__pb2.FindByIdCategoryRequest.FromString,
                    response_serializer=category_dot_category__common__pb2.ApiResponseCategory.SerializeToString,
            ),
            'FindByActive': grpc.unary_unary_rpc_method_handler(
                    servicer.FindByActive,
                    request_deserializer=category_dot_category__query__pb2.FindAllCategoryRequest.FromString,
                    response_serializer=category_dot_category__common__pb2.ApiResponsePaginationCategoryDeleteAt.SerializeToString,
            ),
            'FindByTrashed': grpc.unary_unary_rpc_method_handler(
                    servicer.FindByTrashed,
                    request_deserializer=category_dot_category__query__pb2.FindAllCategoryRequest.FromString,
                    response_serializer=category_dot_category__common__pb2.ApiResponsePaginationCategoryDeleteAt.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'pb.category.CategoryQueryService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('pb.category.CategoryQueryService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class CategoryQueryService:
    """Missing associated documentation comment in.proto file."""

    @staticmethod
    def FindMonthlyTotalPrices(request,
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
            '/pb.category.CategoryQueryService/FindMonthlyTotalPrices',
            category_dot_category__common__pb2.FindYearMonthTotalPrices.SerializeToString,
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
    def FindYearlyTotalPrices(request,
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
            '/pb.category.CategoryQueryService/FindYearlyTotalPrices',
            category_dot_category__common__pb2.FindYearTotalPrices.SerializeToString,
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
            '/pb.category.CategoryQueryService/FindMonthlyTotalPricesById',
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
            '/pb.category.CategoryQueryService/FindYearlyTotalPricesById',
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
            '/pb.category.CategoryQueryService/FindMonthlyTotalPricesByMerchant',
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
            '/pb.category.CategoryQueryService/FindYearlyTotalPricesByMerchant',
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
    def FindMonthPrice(request,
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
            '/pb.category.CategoryQueryService/FindMonthPrice',
            category_dot_category__common__pb2.FindYearCategory.SerializeToString,
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
    def FindYearPrice(request,
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
            '/pb.category.CategoryQueryService/FindYearPrice',
            category_dot_category__common__pb2.FindYearCategory.SerializeToString,
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
            '/pb.category.CategoryQueryService/FindMonthPriceByMerchant',
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
            '/pb.category.CategoryQueryService/FindYearPriceByMerchant',
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
            '/pb.category.CategoryQueryService/FindMonthPriceById',
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
            '/pb.category.CategoryQueryService/FindYearPriceById',
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
            '/pb.category.CategoryQueryService/FindAll',
            category_dot_category__query__pb2.FindAllCategoryRequest.SerializeToString,
            category_dot_category__common__pb2.ApiResponsePaginationCategory.FromString,
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
            '/pb.category.CategoryQueryService/FindById',
            category_dot_category__common__pb2.FindByIdCategoryRequest.SerializeToString,
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
            '/pb.category.CategoryQueryService/FindByActive',
            category_dot_category__query__pb2.FindAllCategoryRequest.SerializeToString,
            category_dot_category__common__pb2.ApiResponsePaginationCategoryDeleteAt.FromString,
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
            '/pb.category.CategoryQueryService/FindByTrashed',
            category_dot_category__query__pb2.FindAllCategoryRequest.SerializeToString,
            category_dot_category__common__pb2.ApiResponsePaginationCategoryDeleteAt.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
