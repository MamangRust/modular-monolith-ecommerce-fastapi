# DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from pb.merchant_document import merchant_document_common_pb2 as merchant__document_dot_merchant__document__common__pb2
from pb.merchant_document import merchant_document_query_pb2 as merchant__document_dot_merchant__document__query__pb2

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
        + ' but the generated code in merchant_document/merchant_document_query_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class MerchantDocumentQueryServiceStub:
    """Missing associated documentation comment in.proto file."""

    def __init__(self, channel):
        """Constructor. Args: channel: A grpc.Channel."""
        self.FindAll = channel.unary_unary(
                '/pb.merchant_document.MerchantDocumentQueryService/FindAll',
                request_serializer=merchant__document_dot_merchant__document__query__pb2.FindAllMerchantDocumentsRequest.SerializeToString,
                response_deserializer=merchant__document_dot_merchant__document__common__pb2.ApiResponsePaginationMerchantDocument.FromString,
                _registered_method=True)
        self.FindAllActive = channel.unary_unary(
                '/pb.merchant_document.MerchantDocumentQueryService/FindAllActive',
                request_serializer=merchant__document_dot_merchant__document__query__pb2.FindAllMerchantDocumentsRequest.SerializeToString,
                response_deserializer=merchant__document_dot_merchant__document__common__pb2.ApiResponsePaginationMerchantDocument.FromString,
                _registered_method=True)
        self.FindAllTrashed = channel.unary_unary(
                '/pb.merchant_document.MerchantDocumentQueryService/FindAllTrashed',
                request_serializer=merchant__document_dot_merchant__document__query__pb2.FindAllMerchantDocumentsRequest.SerializeToString,
                response_deserializer=merchant__document_dot_merchant__document__common__pb2.ApiResponsePaginationMerchantDocumentAt.FromString,
                _registered_method=True)
        self.FindById = channel.unary_unary(
                '/pb.merchant_document.MerchantDocumentQueryService/FindById',
                request_serializer=merchant__document_dot_merchant__document__query__pb2.FindMerchantDocumentByIdRequest.SerializeToString,
                response_deserializer=merchant__document_dot_merchant__document__common__pb2.ApiResponseMerchantDocument.FromString,
                _registered_method=True)


class MerchantDocumentQueryServiceServicer:
    """Missing associated documentation comment in.proto file."""

    def FindAll(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def FindAllActive(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def FindAllTrashed(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def FindById(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_MerchantDocumentQueryServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'FindAll': grpc.unary_unary_rpc_method_handler(
                    servicer.FindAll,
                    request_deserializer=merchant__document_dot_merchant__document__query__pb2.FindAllMerchantDocumentsRequest.FromString,
                    response_serializer=merchant__document_dot_merchant__document__common__pb2.ApiResponsePaginationMerchantDocument.SerializeToString,
            ),
            'FindAllActive': grpc.unary_unary_rpc_method_handler(
                    servicer.FindAllActive,
                    request_deserializer=merchant__document_dot_merchant__document__query__pb2.FindAllMerchantDocumentsRequest.FromString,
                    response_serializer=merchant__document_dot_merchant__document__common__pb2.ApiResponsePaginationMerchantDocument.SerializeToString,
            ),
            'FindAllTrashed': grpc.unary_unary_rpc_method_handler(
                    servicer.FindAllTrashed,
                    request_deserializer=merchant__document_dot_merchant__document__query__pb2.FindAllMerchantDocumentsRequest.FromString,
                    response_serializer=merchant__document_dot_merchant__document__common__pb2.ApiResponsePaginationMerchantDocumentAt.SerializeToString,
            ),
            'FindById': grpc.unary_unary_rpc_method_handler(
                    servicer.FindById,
                    request_deserializer=merchant__document_dot_merchant__document__query__pb2.FindMerchantDocumentByIdRequest.FromString,
                    response_serializer=merchant__document_dot_merchant__document__common__pb2.ApiResponseMerchantDocument.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'pb.merchant_document.MerchantDocumentQueryService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('pb.merchant_document.MerchantDocumentQueryService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class MerchantDocumentQueryService:
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
            '/pb.merchant_document.MerchantDocumentQueryService/FindAll',
            merchant__document_dot_merchant__document__query__pb2.FindAllMerchantDocumentsRequest.SerializeToString,
            merchant__document_dot_merchant__document__common__pb2.ApiResponsePaginationMerchantDocument.FromString,
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
    def FindAllActive(request,
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
            '/pb.merchant_document.MerchantDocumentQueryService/FindAllActive',
            merchant__document_dot_merchant__document__query__pb2.FindAllMerchantDocumentsRequest.SerializeToString,
            merchant__document_dot_merchant__document__common__pb2.ApiResponsePaginationMerchantDocument.FromString,
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
    def FindAllTrashed(request,
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
            '/pb.merchant_document.MerchantDocumentQueryService/FindAllTrashed',
            merchant__document_dot_merchant__document__query__pb2.FindAllMerchantDocumentsRequest.SerializeToString,
            merchant__document_dot_merchant__document__common__pb2.ApiResponsePaginationMerchantDocumentAt.FromString,
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
            '/pb.merchant_document.MerchantDocumentQueryService/FindById',
            merchant__document_dot_merchant__document__query__pb2.FindMerchantDocumentByIdRequest.SerializeToString,
            merchant__document_dot_merchant__document__common__pb2.ApiResponseMerchantDocument.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
