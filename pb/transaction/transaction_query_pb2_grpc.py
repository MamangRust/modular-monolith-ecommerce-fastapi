# DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from pb.transaction import transaction_common_pb2 as transaction_dot_transaction__common__pb2
from pb.transaction import transaction_query_pb2 as transaction_dot_transaction__query__pb2

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
        + ' but the generated code in transaction/transaction_query_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class TransactionQueryServiceStub:
    """Missing associated documentation comment in.proto file."""

    def __init__(self, channel):
        """Constructor. Args: channel: A grpc.Channel."""
        self.FindAllTransactions = channel.unary_unary(
                '/pb.transaction.TransactionQueryService/FindAllTransactions',
                request_serializer=transaction_dot_transaction__query__pb2.FindAllTransactionRequest.SerializeToString,
                response_deserializer=transaction_dot_transaction__common__pb2.ApiResponsePaginationTransaction.FromString,
                _registered_method=True)
        self.FindByMerchant = channel.unary_unary(
                '/pb.transaction.TransactionQueryService/FindByMerchant',
                request_serializer=transaction_dot_transaction__query__pb2.FindAllTransactionByMerchantRequest.SerializeToString,
                response_deserializer=transaction_dot_transaction__common__pb2.ApiResponsePaginationTransaction.FromString,
                _registered_method=True)
        self.FindById = channel.unary_unary(
                '/pb.transaction.TransactionQueryService/FindById',
                request_serializer=transaction_dot_transaction__common__pb2.FindByIdTransactionRequest.SerializeToString,
                response_deserializer=transaction_dot_transaction__common__pb2.ApiResponseTransaction.FromString,
                _registered_method=True)
        self.FindByOrderId = channel.unary_unary(
                '/pb.transaction.TransactionQueryService/FindByOrderId',
                request_serializer=transaction_dot_transaction__query__pb2.FindByOrderIdTransactionRequest.SerializeToString,
                response_deserializer=transaction_dot_transaction__common__pb2.ApiResponseTransaction.FromString,
                _registered_method=True)
        self.FindByActive = channel.unary_unary(
                '/pb.transaction.TransactionQueryService/FindByActive',
                request_serializer=transaction_dot_transaction__query__pb2.FindAllTransactionRequest.SerializeToString,
                response_deserializer=transaction_dot_transaction__common__pb2.ApiResponsePaginationTransaction.FromString,
                _registered_method=True)
        self.FindByTrashed = channel.unary_unary(
                '/pb.transaction.TransactionQueryService/FindByTrashed',
                request_serializer=transaction_dot_transaction__query__pb2.FindAllTransactionRequest.SerializeToString,
                response_deserializer=transaction_dot_transaction__common__pb2.ApiResponsePaginationTransactionDeleteAt.FromString,
                _registered_method=True)


class TransactionQueryServiceServicer:
    """Missing associated documentation comment in.proto file."""

    def FindAllTransactions(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def FindByMerchant(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def FindById(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def FindByOrderId(self, request, context):
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


def add_TransactionQueryServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'FindAllTransactions': grpc.unary_unary_rpc_method_handler(
                    servicer.FindAllTransactions,
                    request_deserializer=transaction_dot_transaction__query__pb2.FindAllTransactionRequest.FromString,
                    response_serializer=transaction_dot_transaction__common__pb2.ApiResponsePaginationTransaction.SerializeToString,
            ),
            'FindByMerchant': grpc.unary_unary_rpc_method_handler(
                    servicer.FindByMerchant,
                    request_deserializer=transaction_dot_transaction__query__pb2.FindAllTransactionByMerchantRequest.FromString,
                    response_serializer=transaction_dot_transaction__common__pb2.ApiResponsePaginationTransaction.SerializeToString,
            ),
            'FindById': grpc.unary_unary_rpc_method_handler(
                    servicer.FindById,
                    request_deserializer=transaction_dot_transaction__common__pb2.FindByIdTransactionRequest.FromString,
                    response_serializer=transaction_dot_transaction__common__pb2.ApiResponseTransaction.SerializeToString,
            ),
            'FindByOrderId': grpc.unary_unary_rpc_method_handler(
                    servicer.FindByOrderId,
                    request_deserializer=transaction_dot_transaction__query__pb2.FindByOrderIdTransactionRequest.FromString,
                    response_serializer=transaction_dot_transaction__common__pb2.ApiResponseTransaction.SerializeToString,
            ),
            'FindByActive': grpc.unary_unary_rpc_method_handler(
                    servicer.FindByActive,
                    request_deserializer=transaction_dot_transaction__query__pb2.FindAllTransactionRequest.FromString,
                    response_serializer=transaction_dot_transaction__common__pb2.ApiResponsePaginationTransaction.SerializeToString,
            ),
            'FindByTrashed': grpc.unary_unary_rpc_method_handler(
                    servicer.FindByTrashed,
                    request_deserializer=transaction_dot_transaction__query__pb2.FindAllTransactionRequest.FromString,
                    response_serializer=transaction_dot_transaction__common__pb2.ApiResponsePaginationTransactionDeleteAt.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'pb.transaction.TransactionQueryService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('pb.transaction.TransactionQueryService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class TransactionQueryService:
    """Missing associated documentation comment in.proto file."""

    @staticmethod
    def FindAllTransactions(request,
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
            '/pb.transaction.TransactionQueryService/FindAllTransactions',
            transaction_dot_transaction__query__pb2.FindAllTransactionRequest.SerializeToString,
            transaction_dot_transaction__common__pb2.ApiResponsePaginationTransaction.FromString,
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
            '/pb.transaction.TransactionQueryService/FindByMerchant',
            transaction_dot_transaction__query__pb2.FindAllTransactionByMerchantRequest.SerializeToString,
            transaction_dot_transaction__common__pb2.ApiResponsePaginationTransaction.FromString,
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
            '/pb.transaction.TransactionQueryService/FindById',
            transaction_dot_transaction__common__pb2.FindByIdTransactionRequest.SerializeToString,
            transaction_dot_transaction__common__pb2.ApiResponseTransaction.FromString,
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
    def FindByOrderId(request,
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
            '/pb.transaction.TransactionQueryService/FindByOrderId',
            transaction_dot_transaction__query__pb2.FindByOrderIdTransactionRequest.SerializeToString,
            transaction_dot_transaction__common__pb2.ApiResponseTransaction.FromString,
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
            '/pb.transaction.TransactionQueryService/FindByActive',
            transaction_dot_transaction__query__pb2.FindAllTransactionRequest.SerializeToString,
            transaction_dot_transaction__common__pb2.ApiResponsePaginationTransaction.FromString,
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
            '/pb.transaction.TransactionQueryService/FindByTrashed',
            transaction_dot_transaction__query__pb2.FindAllTransactionRequest.SerializeToString,
            transaction_dot_transaction__common__pb2.ApiResponsePaginationTransactionDeleteAt.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
