# DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from pb.merchant import merchant_query_pb2 as merchant_dot_merchant__query__pb2
from pb.merchant_detail import merchant_detail_common_pb2 as merchant__detail_dot_merchant__detail__common__pb2

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
        + ' but the generated code in merchant_detail/merchant_detail_query_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class MerchantDetailQueryServiceStub:
    """Missing associated documentation comment in.proto file."""

    def __init__(self, channel):
        """Constructor. Args: channel: A grpc.Channel."""
        self.FindAll = channel.unary_unary(
                '/pb.merchant_detail.MerchantDetailQueryService/FindAll',
                request_serializer=merchant_dot_merchant__query__pb2.FindAllMerchantRequest.SerializeToString,
                response_deserializer=merchant__detail_dot_merchant__detail__common__pb2.ApiResponsePaginationMerchantDetail.FromString,
                _registered_method=True)
        self.FindById = channel.unary_unary(
                '/pb.merchant_detail.MerchantDetailQueryService/FindById',
                request_serializer=merchant__detail_dot_merchant__detail__common__pb2.FindByIdMerchantDetailRequest.SerializeToString,
                response_deserializer=merchant__detail_dot_merchant__detail__common__pb2.ApiResponseMerchantDetail.FromString,
                _registered_method=True)
        self.FindByActive = channel.unary_unary(
                '/pb.merchant_detail.MerchantDetailQueryService/FindByActive',
                request_serializer=merchant_dot_merchant__query__pb2.FindAllMerchantRequest.SerializeToString,
                response_deserializer=merchant__detail_dot_merchant__detail__common__pb2.ApiResponsePaginationMerchantDetailDeleteAt.FromString,
                _registered_method=True)
        self.FindByTrashed = channel.unary_unary(
                '/pb.merchant_detail.MerchantDetailQueryService/FindByTrashed',
                request_serializer=merchant_dot_merchant__query__pb2.FindAllMerchantRequest.SerializeToString,
                response_deserializer=merchant__detail_dot_merchant__detail__common__pb2.ApiResponsePaginationMerchantDetailDeleteAt.FromString,
                _registered_method=True)


class MerchantDetailQueryServiceServicer:
    """Missing associated documentation comment in.proto file."""

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


def add_MerchantDetailQueryServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'FindAll': grpc.unary_unary_rpc_method_handler(
                    servicer.FindAll,
                    request_deserializer=merchant_dot_merchant__query__pb2.FindAllMerchantRequest.FromString,
                    response_serializer=merchant__detail_dot_merchant__detail__common__pb2.ApiResponsePaginationMerchantDetail.SerializeToString,
            ),
            'FindById': grpc.unary_unary_rpc_method_handler(
                    servicer.FindById,
                    request_deserializer=merchant__detail_dot_merchant__detail__common__pb2.FindByIdMerchantDetailRequest.FromString,
                    response_serializer=merchant__detail_dot_merchant__detail__common__pb2.ApiResponseMerchantDetail.SerializeToString,
            ),
            'FindByActive': grpc.unary_unary_rpc_method_handler(
                    servicer.FindByActive,
                    request_deserializer=merchant_dot_merchant__query__pb2.FindAllMerchantRequest.FromString,
                    response_serializer=merchant__detail_dot_merchant__detail__common__pb2.ApiResponsePaginationMerchantDetailDeleteAt.SerializeToString,
            ),
            'FindByTrashed': grpc.unary_unary_rpc_method_handler(
                    servicer.FindByTrashed,
                    request_deserializer=merchant_dot_merchant__query__pb2.FindAllMerchantRequest.FromString,
                    response_serializer=merchant__detail_dot_merchant__detail__common__pb2.ApiResponsePaginationMerchantDetailDeleteAt.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'pb.merchant_detail.MerchantDetailQueryService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('pb.merchant_detail.MerchantDetailQueryService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class MerchantDetailQueryService:
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
            '/pb.merchant_detail.MerchantDetailQueryService/FindAll',
            merchant_dot_merchant__query__pb2.FindAllMerchantRequest.SerializeToString,
            merchant__detail_dot_merchant__detail__common__pb2.ApiResponsePaginationMerchantDetail.FromString,
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
            '/pb.merchant_detail.MerchantDetailQueryService/FindById',
            merchant__detail_dot_merchant__detail__common__pb2.FindByIdMerchantDetailRequest.SerializeToString,
            merchant__detail_dot_merchant__detail__common__pb2.ApiResponseMerchantDetail.FromString,
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
            '/pb.merchant_detail.MerchantDetailQueryService/FindByActive',
            merchant_dot_merchant__query__pb2.FindAllMerchantRequest.SerializeToString,
            merchant__detail_dot_merchant__detail__common__pb2.ApiResponsePaginationMerchantDetailDeleteAt.FromString,
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
            '/pb.merchant_detail.MerchantDetailQueryService/FindByTrashed',
            merchant_dot_merchant__query__pb2.FindAllMerchantRequest.SerializeToString,
            merchant__detail_dot_merchant__detail__common__pb2.ApiResponsePaginationMerchantDetailDeleteAt.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
