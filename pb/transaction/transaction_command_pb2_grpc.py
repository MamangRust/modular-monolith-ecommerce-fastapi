# DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from pb.transaction import transaction_command_pb2 as transaction_dot_transaction__command__pb2
from pb.transaction import transaction_common_pb2 as transaction_dot_transaction__common__pb2

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
        + ' but the generated code in transaction/transaction_command_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class TransactionCommandServiceStub:
    """Missing associated documentation comment in.proto file."""

    def __init__(self, channel):
        """Constructor. Args: channel: A grpc.Channel."""
        self.Create = channel.unary_unary(
                '/pb.transaction.TransactionCommandService/Create',
                request_serializer=transaction_dot_transaction__command__pb2.CreateTransactionRequest.SerializeToString,
                response_deserializer=transaction_dot_transaction__common__pb2.ApiResponseTransaction.FromString,
                _registered_method=True)
        self.Update = channel.unary_unary(
                '/pb.transaction.TransactionCommandService/Update',
                request_serializer=transaction_dot_transaction__command__pb2.UpdateTransactionRequest.SerializeToString,
                response_deserializer=transaction_dot_transaction__common__pb2.ApiResponseTransaction.FromString,
                _registered_method=True)
        self.TrashedTransaction = channel.unary_unary(
                '/pb.transaction.TransactionCommandService/TrashedTransaction',
                request_serializer=transaction_dot_transaction__common__pb2.FindByIdTransactionRequest.SerializeToString,
                response_deserializer=transaction_dot_transaction__common__pb2.ApiResponseTransactionDeleteAt.FromString,
                _registered_method=True)
        self.RestoreTransaction = channel.unary_unary(
                '/pb.transaction.TransactionCommandService/RestoreTransaction',
                request_serializer=transaction_dot_transaction__common__pb2.FindByIdTransactionRequest.SerializeToString,
                response_deserializer=transaction_dot_transaction__common__pb2.ApiResponseTransactionDeleteAt.FromString,
                _registered_method=True)
        self.DeleteTransactionPermanent = channel.unary_unary(
                '/pb.transaction.TransactionCommandService/DeleteTransactionPermanent',
                request_serializer=transaction_dot_transaction__common__pb2.FindByIdTransactionRequest.SerializeToString,
                response_deserializer=transaction_dot_transaction__common__pb2.ApiResponseTransactionDelete.FromString,
                _registered_method=True)
        self.RestoreAllTransaction = channel.unary_unary(
                '/pb.transaction.TransactionCommandService/RestoreAllTransaction',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=transaction_dot_transaction__common__pb2.ApiResponseTransactionAll.FromString,
                _registered_method=True)
        self.DeleteTransactionByOrderPermanent = channel.unary_unary(
                '/pb.transaction.TransactionCommandService/DeleteTransactionByOrderPermanent',
                request_serializer=transaction_dot_transaction__common__pb2.FindByIdTransactionRequest.SerializeToString,
                response_deserializer=transaction_dot_transaction__common__pb2.ApiResponseTransactionDelete.FromString,
                _registered_method=True)
        self.DeleteAllTransactionPermanent = channel.unary_unary(
                '/pb.transaction.TransactionCommandService/DeleteAllTransactionPermanent',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=transaction_dot_transaction__common__pb2.ApiResponseTransactionAll.FromString,
                _registered_method=True)


class TransactionCommandServiceServicer:
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

    def TrashedTransaction(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RestoreTransaction(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteTransactionPermanent(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RestoreAllTransaction(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteTransactionByOrderPermanent(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteAllTransactionPermanent(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_TransactionCommandServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Create': grpc.unary_unary_rpc_method_handler(
                    servicer.Create,
                    request_deserializer=transaction_dot_transaction__command__pb2.CreateTransactionRequest.FromString,
                    response_serializer=transaction_dot_transaction__common__pb2.ApiResponseTransaction.SerializeToString,
            ),
            'Update': grpc.unary_unary_rpc_method_handler(
                    servicer.Update,
                    request_deserializer=transaction_dot_transaction__command__pb2.UpdateTransactionRequest.FromString,
                    response_serializer=transaction_dot_transaction__common__pb2.ApiResponseTransaction.SerializeToString,
            ),
            'TrashedTransaction': grpc.unary_unary_rpc_method_handler(
                    servicer.TrashedTransaction,
                    request_deserializer=transaction_dot_transaction__common__pb2.FindByIdTransactionRequest.FromString,
                    response_serializer=transaction_dot_transaction__common__pb2.ApiResponseTransactionDeleteAt.SerializeToString,
            ),
            'RestoreTransaction': grpc.unary_unary_rpc_method_handler(
                    servicer.RestoreTransaction,
                    request_deserializer=transaction_dot_transaction__common__pb2.FindByIdTransactionRequest.FromString,
                    response_serializer=transaction_dot_transaction__common__pb2.ApiResponseTransactionDeleteAt.SerializeToString,
            ),
            'DeleteTransactionPermanent': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteTransactionPermanent,
                    request_deserializer=transaction_dot_transaction__common__pb2.FindByIdTransactionRequest.FromString,
                    response_serializer=transaction_dot_transaction__common__pb2.ApiResponseTransactionDelete.SerializeToString,
            ),
            'RestoreAllTransaction': grpc.unary_unary_rpc_method_handler(
                    servicer.RestoreAllTransaction,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=transaction_dot_transaction__common__pb2.ApiResponseTransactionAll.SerializeToString,
            ),
            'DeleteTransactionByOrderPermanent': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteTransactionByOrderPermanent,
                    request_deserializer=transaction_dot_transaction__common__pb2.FindByIdTransactionRequest.FromString,
                    response_serializer=transaction_dot_transaction__common__pb2.ApiResponseTransactionDelete.SerializeToString,
            ),
            'DeleteAllTransactionPermanent': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteAllTransactionPermanent,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=transaction_dot_transaction__common__pb2.ApiResponseTransactionAll.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'pb.transaction.TransactionCommandService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('pb.transaction.TransactionCommandService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class TransactionCommandService:
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
            '/pb.transaction.TransactionCommandService/Create',
            transaction_dot_transaction__command__pb2.CreateTransactionRequest.SerializeToString,
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
            '/pb.transaction.TransactionCommandService/Update',
            transaction_dot_transaction__command__pb2.UpdateTransactionRequest.SerializeToString,
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
    def TrashedTransaction(request,
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
            '/pb.transaction.TransactionCommandService/TrashedTransaction',
            transaction_dot_transaction__common__pb2.FindByIdTransactionRequest.SerializeToString,
            transaction_dot_transaction__common__pb2.ApiResponseTransactionDeleteAt.FromString,
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
    def RestoreTransaction(request,
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
            '/pb.transaction.TransactionCommandService/RestoreTransaction',
            transaction_dot_transaction__common__pb2.FindByIdTransactionRequest.SerializeToString,
            transaction_dot_transaction__common__pb2.ApiResponseTransactionDeleteAt.FromString,
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
    def DeleteTransactionPermanent(request,
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
            '/pb.transaction.TransactionCommandService/DeleteTransactionPermanent',
            transaction_dot_transaction__common__pb2.FindByIdTransactionRequest.SerializeToString,
            transaction_dot_transaction__common__pb2.ApiResponseTransactionDelete.FromString,
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
    def RestoreAllTransaction(request,
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
            '/pb.transaction.TransactionCommandService/RestoreAllTransaction',
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            transaction_dot_transaction__common__pb2.ApiResponseTransactionAll.FromString,
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
    def DeleteTransactionByOrderPermanent(request,
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
            '/pb.transaction.TransactionCommandService/DeleteTransactionByOrderPermanent',
            transaction_dot_transaction__common__pb2.FindByIdTransactionRequest.SerializeToString,
            transaction_dot_transaction__common__pb2.ApiResponseTransactionDelete.FromString,
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
    def DeleteAllTransactionPermanent(request,
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
            '/pb.transaction.TransactionCommandService/DeleteAllTransactionPermanent',
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            transaction_dot_transaction__common__pb2.ApiResponseTransactionAll.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
