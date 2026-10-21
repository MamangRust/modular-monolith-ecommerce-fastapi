# DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from pb.product import product_command_pb2 as product_dot_product__command__pb2
from pb.product import product_common_pb2 as product_dot_product__common__pb2

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
        + ' but the generated code in product/product_command_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class ProductCommandServiceStub:
    """Missing associated documentation comment in.proto file."""

    def __init__(self, channel):
        """Constructor. Args: channel: A grpc.Channel."""
        self.Create = channel.unary_unary(
                '/pb.product.ProductCommandService/Create',
                request_serializer=product_dot_product__command__pb2.CreateProductRequest.SerializeToString,
                response_deserializer=product_dot_product__common__pb2.ApiResponseProduct.FromString,
                _registered_method=True)
        self.Update = channel.unary_unary(
                '/pb.product.ProductCommandService/Update',
                request_serializer=product_dot_product__command__pb2.UpdateProductRequest.SerializeToString,
                response_deserializer=product_dot_product__common__pb2.ApiResponseProduct.FromString,
                _registered_method=True)
        self.UpdateProductCountStock = channel.unary_unary(
                '/pb.product.ProductCommandService/UpdateProductCountStock',
                request_serializer=product_dot_product__command__pb2.UpdateProductCountStockRequest.SerializeToString,
                response_deserializer=product_dot_product__common__pb2.ApiResponseProduct.FromString,
                _registered_method=True)
        self.AdjustProductStock = channel.unary_unary(
                '/pb.product.ProductCommandService/AdjustProductStock',
                request_serializer=product_dot_product__command__pb2.AdjustProductStockRequest.SerializeToString,
                response_deserializer=product_dot_product__common__pb2.ApiResponseProduct.FromString,
                _registered_method=True)
        self.TrashedProduct = channel.unary_unary(
                '/pb.product.ProductCommandService/TrashedProduct',
                request_serializer=product_dot_product__common__pb2.FindByIdProductRequest.SerializeToString,
                response_deserializer=product_dot_product__common__pb2.ApiResponseProductDeleteAt.FromString,
                _registered_method=True)
        self.RestoreProduct = channel.unary_unary(
                '/pb.product.ProductCommandService/RestoreProduct',
                request_serializer=product_dot_product__common__pb2.FindByIdProductRequest.SerializeToString,
                response_deserializer=product_dot_product__common__pb2.ApiResponseProductDeleteAt.FromString,
                _registered_method=True)
        self.DeleteProductPermanent = channel.unary_unary(
                '/pb.product.ProductCommandService/DeleteProductPermanent',
                request_serializer=product_dot_product__common__pb2.FindByIdProductRequest.SerializeToString,
                response_deserializer=product_dot_product__common__pb2.ApiResponseProductDelete.FromString,
                _registered_method=True)
        self.RestoreAllProduct = channel.unary_unary(
                '/pb.product.ProductCommandService/RestoreAllProduct',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=product_dot_product__common__pb2.ApiResponseProductAll.FromString,
                _registered_method=True)
        self.DeleteAllProductPermanent = channel.unary_unary(
                '/pb.product.ProductCommandService/DeleteAllProductPermanent',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=product_dot_product__common__pb2.ApiResponseProductAll.FromString,
                _registered_method=True)


class ProductCommandServiceServicer:
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

    def UpdateProductCountStock(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def AdjustProductStock(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def TrashedProduct(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RestoreProduct(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteProductPermanent(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RestoreAllProduct(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteAllProductPermanent(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ProductCommandServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Create': grpc.unary_unary_rpc_method_handler(
                    servicer.Create,
                    request_deserializer=product_dot_product__command__pb2.CreateProductRequest.FromString,
                    response_serializer=product_dot_product__common__pb2.ApiResponseProduct.SerializeToString,
            ),
            'Update': grpc.unary_unary_rpc_method_handler(
                    servicer.Update,
                    request_deserializer=product_dot_product__command__pb2.UpdateProductRequest.FromString,
                    response_serializer=product_dot_product__common__pb2.ApiResponseProduct.SerializeToString,
            ),
            'UpdateProductCountStock': grpc.unary_unary_rpc_method_handler(
                    servicer.UpdateProductCountStock,
                    request_deserializer=product_dot_product__command__pb2.UpdateProductCountStockRequest.FromString,
                    response_serializer=product_dot_product__common__pb2.ApiResponseProduct.SerializeToString,
            ),
            'AdjustProductStock': grpc.unary_unary_rpc_method_handler(
                    servicer.AdjustProductStock,
                    request_deserializer=product_dot_product__command__pb2.AdjustProductStockRequest.FromString,
                    response_serializer=product_dot_product__common__pb2.ApiResponseProduct.SerializeToString,
            ),
            'TrashedProduct': grpc.unary_unary_rpc_method_handler(
                    servicer.TrashedProduct,
                    request_deserializer=product_dot_product__common__pb2.FindByIdProductRequest.FromString,
                    response_serializer=product_dot_product__common__pb2.ApiResponseProductDeleteAt.SerializeToString,
            ),
            'RestoreProduct': grpc.unary_unary_rpc_method_handler(
                    servicer.RestoreProduct,
                    request_deserializer=product_dot_product__common__pb2.FindByIdProductRequest.FromString,
                    response_serializer=product_dot_product__common__pb2.ApiResponseProductDeleteAt.SerializeToString,
            ),
            'DeleteProductPermanent': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteProductPermanent,
                    request_deserializer=product_dot_product__common__pb2.FindByIdProductRequest.FromString,
                    response_serializer=product_dot_product__common__pb2.ApiResponseProductDelete.SerializeToString,
            ),
            'RestoreAllProduct': grpc.unary_unary_rpc_method_handler(
                    servicer.RestoreAllProduct,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=product_dot_product__common__pb2.ApiResponseProductAll.SerializeToString,
            ),
            'DeleteAllProductPermanent': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteAllProductPermanent,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=product_dot_product__common__pb2.ApiResponseProductAll.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'pb.product.ProductCommandService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('pb.product.ProductCommandService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class ProductCommandService:
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
            '/pb.product.ProductCommandService/Create',
            product_dot_product__command__pb2.CreateProductRequest.SerializeToString,
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
            '/pb.product.ProductCommandService/Update',
            product_dot_product__command__pb2.UpdateProductRequest.SerializeToString,
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
    def UpdateProductCountStock(request,
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
            '/pb.product.ProductCommandService/UpdateProductCountStock',
            product_dot_product__command__pb2.UpdateProductCountStockRequest.SerializeToString,
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
    def AdjustProductStock(request,
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
            '/pb.product.ProductCommandService/AdjustProductStock',
            product_dot_product__command__pb2.AdjustProductStockRequest.SerializeToString,
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
    def TrashedProduct(request,
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
            '/pb.product.ProductCommandService/TrashedProduct',
            product_dot_product__common__pb2.FindByIdProductRequest.SerializeToString,
            product_dot_product__common__pb2.ApiResponseProductDeleteAt.FromString,
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
    def RestoreProduct(request,
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
            '/pb.product.ProductCommandService/RestoreProduct',
            product_dot_product__common__pb2.FindByIdProductRequest.SerializeToString,
            product_dot_product__common__pb2.ApiResponseProductDeleteAt.FromString,
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
    def DeleteProductPermanent(request,
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
            '/pb.product.ProductCommandService/DeleteProductPermanent',
            product_dot_product__common__pb2.FindByIdProductRequest.SerializeToString,
            product_dot_product__common__pb2.ApiResponseProductDelete.FromString,
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
    def RestoreAllProduct(request,
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
            '/pb.product.ProductCommandService/RestoreAllProduct',
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            product_dot_product__common__pb2.ApiResponseProductAll.FromString,
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
    def DeleteAllProductPermanent(request,
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
            '/pb.product.ProductCommandService/DeleteAllProductPermanent',
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            product_dot_product__common__pb2.ApiResponseProductAll.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
