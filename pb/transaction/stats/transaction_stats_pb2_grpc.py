# DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from pb.transaction.stats import transaction_stats_pb2 as transaction_dot_stats_dot_transaction__stats__pb2
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
        + ' but the generated code in transaction/stats/transaction_stats_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class TransactionStatsServiceStub:
    """Missing associated documentation comment in.proto file."""

    def __init__(self, channel):
        """Constructor. Args: channel: A grpc.Channel."""
        self.GetMonthlyAmountSuccess = channel.unary_unary(
                '/pb.transaction.stats.TransactionStatsService/GetMonthlyAmountSuccess',
                request_serializer=transaction_dot_stats_dot_transaction__stats__pb2.MonthAmountTransactionRequest.SerializeToString,
                response_deserializer=transaction_dot_transaction__common__pb2.ApiResponseTransactionMonthAmountSuccess.FromString,
                _registered_method=True)
        self.GetYearlyAmountSuccess = channel.unary_unary(
                '/pb.transaction.stats.TransactionStatsService/GetYearlyAmountSuccess',
                request_serializer=transaction_dot_stats_dot_transaction__stats__pb2.YearAmountTransactionRequest.SerializeToString,
                response_deserializer=transaction_dot_transaction__common__pb2.ApiResponseTransactionYearAmountSuccess.FromString,
                _registered_method=True)
        self.GetMonthlyAmountFailed = channel.unary_unary(
                '/pb.transaction.stats.TransactionStatsService/GetMonthlyAmountFailed',
                request_serializer=transaction_dot_stats_dot_transaction__stats__pb2.MonthAmountTransactionRequest.SerializeToString,
                response_deserializer=transaction_dot_transaction__common__pb2.ApiResponseTransactionMonthAmountFailed.FromString,
                _registered_method=True)
        self.GetYearlyAmountFailed = channel.unary_unary(
                '/pb.transaction.stats.TransactionStatsService/GetYearlyAmountFailed',
                request_serializer=transaction_dot_stats_dot_transaction__stats__pb2.YearAmountTransactionRequest.SerializeToString,
                response_deserializer=transaction_dot_transaction__common__pb2.ApiResponseTransactionYearAmountFailed.FromString,
                _registered_method=True)
        self.GetMonthlyTransactionMethodSuccess = channel.unary_unary(
                '/pb.transaction.stats.TransactionStatsService/GetMonthlyTransactionMethodSuccess',
                request_serializer=transaction_dot_stats_dot_transaction__stats__pb2.MonthMethodTransactionRequest.SerializeToString,
                response_deserializer=transaction_dot_transaction__common__pb2.ApiResponseTransactionMonthPaymentMethod.FromString,
                _registered_method=True)
        self.GetYearlyTransactionMethodSuccess = channel.unary_unary(
                '/pb.transaction.stats.TransactionStatsService/GetYearlyTransactionMethodSuccess',
                request_serializer=transaction_dot_stats_dot_transaction__stats__pb2.YearMethodTransactionRequest.SerializeToString,
                response_deserializer=transaction_dot_transaction__common__pb2.ApiResponseTransactionYearPaymentmethod.FromString,
                _registered_method=True)
        self.GetMonthlyTransactionMethodFailed = channel.unary_unary(
                '/pb.transaction.stats.TransactionStatsService/GetMonthlyTransactionMethodFailed',
                request_serializer=transaction_dot_stats_dot_transaction__stats__pb2.MonthMethodTransactionRequest.SerializeToString,
                response_deserializer=transaction_dot_transaction__common__pb2.ApiResponseTransactionMonthPaymentMethod.FromString,
                _registered_method=True)
        self.GetYearlyTransactionMethodFailed = channel.unary_unary(
                '/pb.transaction.stats.TransactionStatsService/GetYearlyTransactionMethodFailed',
                request_serializer=transaction_dot_stats_dot_transaction__stats__pb2.YearMethodTransactionRequest.SerializeToString,
                response_deserializer=transaction_dot_transaction__common__pb2.ApiResponseTransactionYearPaymentmethod.FromString,
                _registered_method=True)


class TransactionStatsServiceServicer:
    """Missing associated documentation comment in.proto file."""

    def GetMonthlyAmountSuccess(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetYearlyAmountSuccess(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetMonthlyAmountFailed(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetYearlyAmountFailed(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetMonthlyTransactionMethodSuccess(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetYearlyTransactionMethodSuccess(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetMonthlyTransactionMethodFailed(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetYearlyTransactionMethodFailed(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_TransactionStatsServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'GetMonthlyAmountSuccess': grpc.unary_unary_rpc_method_handler(
                    servicer.GetMonthlyAmountSuccess,
                    request_deserializer=transaction_dot_stats_dot_transaction__stats__pb2.MonthAmountTransactionRequest.FromString,
                    response_serializer=transaction_dot_transaction__common__pb2.ApiResponseTransactionMonthAmountSuccess.SerializeToString,
            ),
            'GetYearlyAmountSuccess': grpc.unary_unary_rpc_method_handler(
                    servicer.GetYearlyAmountSuccess,
                    request_deserializer=transaction_dot_stats_dot_transaction__stats__pb2.YearAmountTransactionRequest.FromString,
                    response_serializer=transaction_dot_transaction__common__pb2.ApiResponseTransactionYearAmountSuccess.SerializeToString,
            ),
            'GetMonthlyAmountFailed': grpc.unary_unary_rpc_method_handler(
                    servicer.GetMonthlyAmountFailed,
                    request_deserializer=transaction_dot_stats_dot_transaction__stats__pb2.MonthAmountTransactionRequest.FromString,
                    response_serializer=transaction_dot_transaction__common__pb2.ApiResponseTransactionMonthAmountFailed.SerializeToString,
            ),
            'GetYearlyAmountFailed': grpc.unary_unary_rpc_method_handler(
                    servicer.GetYearlyAmountFailed,
                    request_deserializer=transaction_dot_stats_dot_transaction__stats__pb2.YearAmountTransactionRequest.FromString,
                    response_serializer=transaction_dot_transaction__common__pb2.ApiResponseTransactionYearAmountFailed.SerializeToString,
            ),
            'GetMonthlyTransactionMethodSuccess': grpc.unary_unary_rpc_method_handler(
                    servicer.GetMonthlyTransactionMethodSuccess,
                    request_deserializer=transaction_dot_stats_dot_transaction__stats__pb2.MonthMethodTransactionRequest.FromString,
                    response_serializer=transaction_dot_transaction__common__pb2.ApiResponseTransactionMonthPaymentMethod.SerializeToString,
            ),
            'GetYearlyTransactionMethodSuccess': grpc.unary_unary_rpc_method_handler(
                    servicer.GetYearlyTransactionMethodSuccess,
                    request_deserializer=transaction_dot_stats_dot_transaction__stats__pb2.YearMethodTransactionRequest.FromString,
                    response_serializer=transaction_dot_transaction__common__pb2.ApiResponseTransactionYearPaymentmethod.SerializeToString,
            ),
            'GetMonthlyTransactionMethodFailed': grpc.unary_unary_rpc_method_handler(
                    servicer.GetMonthlyTransactionMethodFailed,
                    request_deserializer=transaction_dot_stats_dot_transaction__stats__pb2.MonthMethodTransactionRequest.FromString,
                    response_serializer=transaction_dot_transaction__common__pb2.ApiResponseTransactionMonthPaymentMethod.SerializeToString,
            ),
            'GetYearlyTransactionMethodFailed': grpc.unary_unary_rpc_method_handler(
                    servicer.GetYearlyTransactionMethodFailed,
                    request_deserializer=transaction_dot_stats_dot_transaction__stats__pb2.YearMethodTransactionRequest.FromString,
                    response_serializer=transaction_dot_transaction__common__pb2.ApiResponseTransactionYearPaymentmethod.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'pb.transaction.stats.TransactionStatsService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('pb.transaction.stats.TransactionStatsService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class TransactionStatsService:
    """Missing associated documentation comment in.proto file."""

    @staticmethod
    def GetMonthlyAmountSuccess(request,
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
            '/pb.transaction.stats.TransactionStatsService/GetMonthlyAmountSuccess',
            transaction_dot_stats_dot_transaction__stats__pb2.MonthAmountTransactionRequest.SerializeToString,
            transaction_dot_transaction__common__pb2.ApiResponseTransactionMonthAmountSuccess.FromString,
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
    def GetYearlyAmountSuccess(request,
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
            '/pb.transaction.stats.TransactionStatsService/GetYearlyAmountSuccess',
            transaction_dot_stats_dot_transaction__stats__pb2.YearAmountTransactionRequest.SerializeToString,
            transaction_dot_transaction__common__pb2.ApiResponseTransactionYearAmountSuccess.FromString,
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
    def GetMonthlyAmountFailed(request,
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
            '/pb.transaction.stats.TransactionStatsService/GetMonthlyAmountFailed',
            transaction_dot_stats_dot_transaction__stats__pb2.MonthAmountTransactionRequest.SerializeToString,
            transaction_dot_transaction__common__pb2.ApiResponseTransactionMonthAmountFailed.FromString,
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
    def GetYearlyAmountFailed(request,
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
            '/pb.transaction.stats.TransactionStatsService/GetYearlyAmountFailed',
            transaction_dot_stats_dot_transaction__stats__pb2.YearAmountTransactionRequest.SerializeToString,
            transaction_dot_transaction__common__pb2.ApiResponseTransactionYearAmountFailed.FromString,
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
    def GetMonthlyTransactionMethodSuccess(request,
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
            '/pb.transaction.stats.TransactionStatsService/GetMonthlyTransactionMethodSuccess',
            transaction_dot_stats_dot_transaction__stats__pb2.MonthMethodTransactionRequest.SerializeToString,
            transaction_dot_transaction__common__pb2.ApiResponseTransactionMonthPaymentMethod.FromString,
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
    def GetYearlyTransactionMethodSuccess(request,
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
            '/pb.transaction.stats.TransactionStatsService/GetYearlyTransactionMethodSuccess',
            transaction_dot_stats_dot_transaction__stats__pb2.YearMethodTransactionRequest.SerializeToString,
            transaction_dot_transaction__common__pb2.ApiResponseTransactionYearPaymentmethod.FromString,
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
    def GetMonthlyTransactionMethodFailed(request,
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
            '/pb.transaction.stats.TransactionStatsService/GetMonthlyTransactionMethodFailed',
            transaction_dot_stats_dot_transaction__stats__pb2.MonthMethodTransactionRequest.SerializeToString,
            transaction_dot_transaction__common__pb2.ApiResponseTransactionMonthPaymentMethod.FromString,
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
    def GetYearlyTransactionMethodFailed(request,
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
            '/pb.transaction.stats.TransactionStatsService/GetYearlyTransactionMethodFailed',
            transaction_dot_stats_dot_transaction__stats__pb2.YearMethodTransactionRequest.SerializeToString,
            transaction_dot_transaction__common__pb2.ApiResponseTransactionYearPaymentmethod.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
