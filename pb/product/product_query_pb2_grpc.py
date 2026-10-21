# DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from pb.product import product_common_pb2 as product_dot_product__common__pb2
from pb.product import product_query_pb2 as product_dot_product__query__pb2

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
        + ' but the generated code in product/product_query_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class ProductQueryServiceStub:
    """Missing associated documentation comment in.proto file."""

    def __init__(self, channel):
        """Constructor. Args: channel: A grpc.Channel."""
        self.FindAll = channel.unary_unary(
                '/pb.product.ProductQueryService/FindAll',
                request_serializer=product_dot_product__query__pb2.FindAllProductRequest.SerializeToString,
                response_deserializer=product_dot_product__common__pb2.ApiResponsePaginationProduct.FromString,
                _registered_method=True)
        self.FindByMerchant = channel.unary_unary(
                '/pb.product.ProductQueryService/FindByMerchant',
                request_serializer=product_dot_product__query__pb2.FindAllProductMerchantRequest.SerializeToString,
                response_deserializer=product_dot_product__common__pb2.ApiResponsePaginationProduct.FromString,
                _registered_method=True)
        self.FindByCategory = channel.unary_unary(
                '/pb.product.ProductQueryService/FindByCategory',
                request_serializer=product_dot_product__query__pb2.FindAllProductCategoryRequest.SerializeToString,
                response_deserializer=product_dot_product__common__pb2.ApiResponsePaginationProduct.FromString,
                _registered_method=True)
        self.FindById = channel.unary_unary(
                '/pb.product.ProductQueryService/FindById',
                request_serializer=product_dot_product__common__pb2.FindByIdProductRequest.SerializeToString,
                response_deserializer=product_dot_product__common__pb2.ApiResponseProduct.FromString,
                _registered_method=True)
        self.FindByActive = channel.unary_unary(
                '/pb.product.ProductQueryService/FindByActive',
                request_serializer=product_dot_product__query__pb2.FindAllProductRequest.SerializeToString,
                response_deserializer=product_dot_product__common__pb2.ApiResponsePaginationProductDeleteAt.FromString,
                _registered_method=True)
        self.FindByTrashed = channel.unary_unary(
                '/pb.product.ProductQueryService/FindByTrashed',
                request_serializer=product_dot_product__query__pb2.FindAllProductRequest.SerializeToString,
                response_deserializer=product_dot_product__common__pb2.ApiResponsePaginationProductDeleteAt.FromString,
                _registered_method=True)


class ProductQueryServiceServicer:
    """Missing associated documentation comment in.proto file."""

    def FindAll(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def FindByMerchant(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def FindByCategory(self, request, context):
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


def add_ProductQueryServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'FindAll': grpc.unary_unary_rpc_method_handler(
                    servicer.FindAll,
                    request_deserializer=product_dot_product__query__pb2.FindAllProductRequest.FromString,
                    response_serializer=product_dot_product__common__pb2.ApiResponsePaginationProduct.SerializeToString,
            ),
            'FindByMerchant': grpc.unary_unary_rpc_method_handler(
                    servicer.FindByMerchant,
                    request_deserializer=product_dot_product__query__pb2.FindAllProductMerchantRequest.FromString,
                    response_serializer=product_dot_product__common__pb2.ApiResponsePaginationProduct.SerializeToString,
            ),
            'FindByCategory': grpc.unary_unary_rpc_method_handler(
                    servicer.FindByCategory,
                    request_deserializer=product_dot_product__query__pb2.FindAllProductCategoryRequest.FromString,
                    response_serializer=product_dot_product__common__pb2.ApiResponsePaginationProduct.SerializeToString,
            ),
            'FindById': grpc.unary_unary_rpc_method_handler(
                    servicer.FindById,
                    request_deserializer=product_dot_product__common__pb2.FindByIdProductRequest.FromString,
                    response_serializer=product_dot_product__common__pb2.ApiResponseProduct.SerializeToString,
            ),
            'FindByActive': grpc.unary_unary_rpc_method_handler(
                    servicer.FindByActive,
                    request_deserializer=product_dot_product__query__pb2.FindAllProductRequest.FromString,
                    response_serializer=product_dot_product__common__pb2.ApiResponsePaginationProductDeleteAt.SerializeToString,
            ),
            'FindByTrashed': grpc.unary_unary_rpc_method_handler(
                    servicer.FindByTrashed,
                    request_deserializer=product_dot_product__query__pb2.FindAllProductRequest.FromString,
                    response_serializer=product_dot_product__common__pb2.ApiResponsePaginationProductDeleteAt.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'pb.product.ProductQueryService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('pb.product.ProductQueryService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class ProductQueryService:
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
            '/pb.product.ProductQueryService/FindAll',
            product_dot_product__query__pb2.FindAllProductRequest.SerializeToString,
            product_dot_product__common__pb2.ApiResponsePaginationProduct.FromString,
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
    def FindByMerchant(request,
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
            '/pb.product.ProductQueryService/FindByMerchant',
            product_dot_product__query__pb2.FindAllProductMerchantRequest.SerializeToString,
            product_dot_product__common__pb2.ApiResponsePaginationProduct.FromString,
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
    def FindByCategory(request,
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
            '/pb.product.ProductQueryService/FindByCategory',
            product_dot_product__query__pb2.FindAllProductCategoryRequest.SerializeToString,
            product_dot_product__common__pb2.ApiResponsePaginationProduct.FromString,
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
            '/pb.product.ProductQueryService/FindById',
            product_dot_product__common__pb2.FindByIdProductRequest.SerializeToString,
            product_dot_product__common__pb2.ApiResponseProduct.FromString,
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
            '/pb.product.ProductQueryService/FindByActive',
            product_dot_product__query__pb2.FindAllProductRequest.SerializeToString,
            product_dot_product__common__pb2.ApiResponsePaginationProductDeleteAt.FromString,
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
            '/pb.product.ProductQueryService/FindByTrashed',
            product_dot_product__query__pb2.FindAllProductRequest.SerializeToString,
            product_dot_product__common__pb2.ApiResponsePaginationProductDeleteAt.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
