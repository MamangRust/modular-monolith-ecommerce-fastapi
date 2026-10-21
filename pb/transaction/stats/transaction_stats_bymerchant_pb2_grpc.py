# DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from pb.transaction.stats import transaction_stats_bymerchant_pb2 as transaction_dot_stats_dot_transaction__stats__bymerchant__pb2
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
        + ' but the generated code in transaction/stats/transaction_stats_bymerchant_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class TransactionStatsByMerchantServiceStub:
    """Missing associated documentation comment in.proto file."""

    def __init__(self, channel):
        """Constructor. Args: channel: A grpc.Channel."""
        self.GetMonthlyAmountSuccessByMerchant = channel.unary_unary(
                '/pb.transaction.stats.TransactionStatsByMerchantService/GetMonthlyAmountSuccessByMerchant',
                request_serializer=transaction_dot_stats_dot_transaction__stats__bymerchant__pb2.MonthAmountTransactionMerchantRequest.SerializeToString,
                response_deserializer=transaction_dot_transaction__common__pb2.ApiResponseTransactionMonthAmountSuccess.FromString,
                _registered_method=True)
        self.GetYearlyAmountSuccessByMerchant = channel.unary_unary(
                '/pb.transaction.stats.TransactionStatsByMerchantService/GetYearlyAmountSuccessByMerchant',
                request_serializer=transaction_dot_stats_dot_transaction__stats__bymerchant__pb2.YearAmountTransactionMerchantRequest.SerializeToString,
                response_deserializer=transaction_dot_transaction__common__pb2.ApiResponseTransactionYearAmountSuccess.FromString,
                _registered_method=True)
        self.GetMonthlyAmountFailedByMerchant = channel.unary_unary(
                '/pb.transaction.stats.TransactionStatsByMerchantService/GetMonthlyAmountFailedByMerchant',
                request_serializer=transaction_dot_stats_dot_transaction__stats__bymerchant__pb2.MonthAmountTransactionMerchantRequest.SerializeToString,
                response_deserializer=transaction_dot_transaction__common__pb2.ApiResponseTransactionMonthAmountFailed.FromString,
                _registered_method=True)
        self.GetYearlyAmountFailedByMerchant = channel.unary_unary(
                '/pb.transaction.stats.TransactionStatsByMerchantService/GetYearlyAmountFailedByMerchant',
                request_serializer=transaction_dot_stats_dot_transaction__stats__bymerchant__pb2.YearAmountTransactionMerchantRequest.SerializeToString,
                response_deserializer=transaction_dot_transaction__common__pb2.ApiResponseTransactionYearAmountFailed.FromString,
                _registered_method=True)
        self.GetMonthlyTransactionMethodByMerchantSuccess = channel.unary_unary(
                '/pb.transaction.stats.TransactionStatsByMerchantService/GetMonthlyTransactionMethodByMerchantSuccess',
                request_serializer=transaction_dot_stats_dot_transaction__stats__bymerchant__pb2.MonthMethodTransactionMerchantRequest.SerializeToString,
                response_deserializer=transaction_dot_transaction__common__pb2.ApiResponseTransactionMonthPaymentMethod.FromString,
                _registered_method=True)
        self.GetYearlyTransactionMethodByMerchantSuccess = channel.unary_unary(
                '/pb.transaction.stats.TransactionStatsByMerchantService/GetYearlyTransactionMethodByMerchantSuccess',
                request_serializer=transaction_dot_stats_dot_transaction__stats__bymerchant__pb2.YearMethodTransactionMerchantRequest.SerializeToString,
                response_deserializer=transaction_dot_transaction__common__pb2.ApiResponseTransactionYearPaymentmethod.FromString,
                _registered_method=True)
        self.GetMonthlyTransactionMethodByMerchantFailed = channel.unary_unary(
                '/pb.transaction.stats.TransactionStatsByMerchantService/GetMonthlyTransactionMethodByMerchantFailed',
                request_serializer=transaction_dot_stats_dot_transaction__stats__bymerchant__pb2.MonthMethodTransactionMerchantRequest.SerializeToString,
                response_deserializer=transaction_dot_transaction__common__pb2.ApiResponseTransactionMonthPaymentMethod.FromString,
                _registered_method=True)
        self.GetYearlyTransactionMethodByMerchantFailed = channel.unary_unary(
                '/pb.transaction.stats.TransactionStatsByMerchantService/GetYearlyTransactionMethodByMerchantFailed',
                request_serializer=transaction_dot_stats_dot_transaction__stats__bymerchant__pb2.YearMethodTransactionMerchantRequest.SerializeToString,
                response_deserializer=transaction_dot_transaction__common__pb2.ApiResponseTransactionYearPaymentmethod.FromString,
                _registered_method=True)


class TransactionStatsByMerchantServiceServicer:
    """Missing associated documentation comment in.proto file."""

    def GetMonthlyAmountSuccessByMerchant(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetYearlyAmountSuccessByMerchant(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetMonthlyAmountFailedByMerchant(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetYearlyAmountFailedByMerchant(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetMonthlyTransactionMethodByMerchantSuccess(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetYearlyTransactionMethodByMerchantSuccess(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetMonthlyTransactionMethodByMerchantFailed(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetYearlyTransactionMethodByMerchantFailed(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_TransactionStatsByMerchantServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'GetMonthlyAmountSuccessByMerchant': grpc.unary_unary_rpc_method_handler(
                    servicer.GetMonthlyAmountSuccessByMerchant,
                    request_deserializer=transaction_dot_stats_dot_transaction__stats__bymerchant__pb2.MonthAmountTransactionMerchantRequest.FromString,
                    response_serializer=transaction_dot_transaction__common__pb2.ApiResponseTransactionMonthAmountSuccess.SerializeToString,
            ),
            'GetYearlyAmountSuccessByMerchant': grpc.unary_unary_rpc_method_handler(
                    servicer.GetYearlyAmountSuccessByMerchant,
                    request_deserializer=transaction_dot_stats_dot_transaction__stats__bymerchant__pb2.YearAmountTransactionMerchantRequest.FromString,
                    response_serializer=transaction_dot_transaction__common__pb2.ApiResponseTransactionYearAmountSuccess.SerializeToString,
            ),
            'GetMonthlyAmountFailedByMerchant': grpc.unary_unary_rpc_method_handler(
                    servicer.GetMonthlyAmountFailedByMerchant,
                    request_deserializer=transaction_dot_stats_dot_transaction__stats__bymerchant__pb2.MonthAmountTransactionMerchantRequest.FromString,
                    response_serializer=transaction_dot_transaction__common__pb2.ApiResponseTransactionMonthAmountFailed.SerializeToString,
            ),
            'GetYearlyAmountFailedByMerchant': grpc.unary_unary_rpc_method_handler(
                    servicer.GetYearlyAmountFailedByMerchant,
                    request_deserializer=transaction_dot_stats_dot_transaction__stats__bymerchant__pb2.YearAmountTransactionMerchantRequest.FromString,
                    response_serializer=transaction_dot_transaction__common__pb2.ApiResponseTransactionYearAmountFailed.SerializeToString,
            ),
            'GetMonthlyTransactionMethodByMerchantSuccess': grpc.unary_unary_rpc_method_handler(
                    servicer.GetMonthlyTransactionMethodByMerchantSuccess,
                    request_deserializer=transaction_dot_stats_dot_transaction__stats__bymerchant__pb2.MonthMethodTransactionMerchantRequest.FromString,
                    response_serializer=transaction_dot_transaction__common__pb2.ApiResponseTransactionMonthPaymentMethod.SerializeToString,
            ),
            'GetYearlyTransactionMethodByMerchantSuccess': grpc.unary_unary_rpc_method_handler(
                    servicer.GetYearlyTransactionMethodByMerchantSuccess,
                    request_deserializer=transaction_dot_stats_dot_transaction__stats__bymerchant__pb2.YearMethodTransactionMerchantRequest.FromString,
                    response_serializer=transaction_dot_transaction__common__pb2.ApiResponseTransactionYearPaymentmethod.SerializeToString,
            ),
            'GetMonthlyTransactionMethodByMerchantFailed': grpc.unary_unary_rpc_method_handler(
                    servicer.GetMonthlyTransactionMethodByMerchantFailed,
                    request_deserializer=transaction_dot_stats_dot_transaction__stats__bymerchant__pb2.MonthMethodTransactionMerchantRequest.FromString,
                    response_serializer=transaction_dot_transaction__common__pb2.ApiResponseTransactionMonthPaymentMethod.SerializeToString,
            ),
            'GetYearlyTransactionMethodByMerchantFailed': grpc.unary_unary_rpc_method_handler(
                    servicer.GetYearlyTransactionMethodByMerchantFailed,
                    request_deserializer=transaction_dot_stats_dot_transaction__stats__bymerchant__pb2.YearMethodTransactionMerchantRequest.FromString,
                    response_serializer=transaction_dot_transaction__common__pb2.ApiResponseTransactionYearPaymentmethod.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'pb.transaction.stats.TransactionStatsByMerchantService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('pb.transaction.stats.TransactionStatsByMerchantService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class TransactionStatsByMerchantService:
    """Missing associated documentation comment in.proto file."""

    @staticmethod
    def GetMonthlyAmountSuccessByMerchant(request,
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
            '/pb.transaction.stats.TransactionStatsByMerchantService/GetMonthlyAmountSuccessByMerchant',
            transaction_dot_stats_dot_transaction__stats__bymerchant__pb2.MonthAmountTransactionMerchantRequest.SerializeToString,
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
    def GetYearlyAmountSuccessByMerchant(request,
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
            '/pb.transaction.stats.TransactionStatsByMerchantService/GetYearlyAmountSuccessByMerchant',
            transaction_dot_stats_dot_transaction__stats__bymerchant__pb2.YearAmountTransactionMerchantRequest.SerializeToString,
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
    def GetMonthlyAmountFailedByMerchant(request,
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
            '/pb.transaction.stats.TransactionStatsByMerchantService/GetMonthlyAmountFailedByMerchant',
            transaction_dot_stats_dot_transaction__stats__bymerchant__pb2.MonthAmountTransactionMerchantRequest.SerializeToString,
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
    def GetYearlyAmountFailedByMerchant(request,
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
            '/pb.transaction.stats.TransactionStatsByMerchantService/GetYearlyAmountFailedByMerchant',
            transaction_dot_stats_dot_transaction__stats__bymerchant__pb2.YearAmountTransactionMerchantRequest.SerializeToString,
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
    def GetMonthlyTransactionMethodByMerchantSuccess(request,
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
            '/pb.transaction.stats.TransactionStatsByMerchantService/GetMonthlyTransactionMethodByMerchantSuccess',
            transaction_dot_stats_dot_transaction__stats__bymerchant__pb2.MonthMethodTransactionMerchantRequest.SerializeToString,
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
    def GetYearlyTransactionMethodByMerchantSuccess(request,
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
            '/pb.transaction.stats.TransactionStatsByMerchantService/GetYearlyTransactionMethodByMerchantSuccess',
            transaction_dot_stats_dot_transaction__stats__bymerchant__pb2.YearMethodTransactionMerchantRequest.SerializeToString,
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
    def GetMonthlyTransactionMethodByMerchantFailed(request,
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
            '/pb.transaction.stats.TransactionStatsByMerchantService/GetMonthlyTransactionMethodByMerchantFailed',
            transaction_dot_stats_dot_transaction__stats__bymerchant__pb2.MonthMethodTransactionMerchantRequest.SerializeToString,
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
    def GetYearlyTransactionMethodByMerchantFailed(request,
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
            '/pb.transaction.stats.TransactionStatsByMerchantService/GetYearlyTransactionMethodByMerchantFailed',
            transaction_dot_stats_dot_transaction__stats__bymerchant__pb2.YearMethodTransactionMerchantRequest.SerializeToString,
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
