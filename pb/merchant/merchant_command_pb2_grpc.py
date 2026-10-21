# DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from pb.merchant import merchant_command_pb2 as merchant_dot_merchant__command__pb2
from pb.merchant import merchant_common_pb2 as merchant_dot_merchant__common__pb2

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
        + ' but the generated code in merchant/merchant_command_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class MerchantCommandServiceStub:
    """Missing associated documentation comment in.proto file."""

    def __init__(self, channel):
        """Constructor. Args: channel: A grpc.Channel."""
        self.Create = channel.unary_unary(
                '/pb.merchant.MerchantCommandService/Create',
                request_serializer=merchant_dot_merchant__command__pb2.CreateMerchantRequest.SerializeToString,
                response_deserializer=merchant_dot_merchant__common__pb2.ApiResponseMerchant.FromString,
                _registered_method=True)
        self.Update = channel.unary_unary(
                '/pb.merchant.MerchantCommandService/Update',
                request_serializer=merchant_dot_merchant__command__pb2.UpdateMerchantRequest.SerializeToString,
                response_deserializer=merchant_dot_merchant__common__pb2.ApiResponseMerchant.FromString,
                _registered_method=True)
        self.UpdateStatus = channel.unary_unary(
                '/pb.merchant.MerchantCommandService/UpdateStatus',
                request_serializer=merchant_dot_merchant__command__pb2.UpdateMerchantStatusRequest.SerializeToString,
                response_deserializer=merchant_dot_merchant__common__pb2.ApiResponseMerchant.FromString,
                _registered_method=True)
        self.TrashedMerchant = channel.unary_unary(
                '/pb.merchant.MerchantCommandService/TrashedMerchant',
                request_serializer=merchant_dot_merchant__common__pb2.FindByIdMerchantRequest.SerializeToString,
                response_deserializer=merchant_dot_merchant__common__pb2.ApiResponseMerchantDeleteAt.FromString,
                _registered_method=True)
        self.RestoreMerchant = channel.unary_unary(
                '/pb.merchant.MerchantCommandService/RestoreMerchant',
                request_serializer=merchant_dot_merchant__common__pb2.FindByIdMerchantRequest.SerializeToString,
                response_deserializer=merchant_dot_merchant__common__pb2.ApiResponseMerchant.FromString,
                _registered_method=True)
        self.DeleteMerchantPermanent = channel.unary_unary(
                '/pb.merchant.MerchantCommandService/DeleteMerchantPermanent',
                request_serializer=merchant_dot_merchant__common__pb2.FindByIdMerchantRequest.SerializeToString,
                response_deserializer=merchant_dot_merchant__common__pb2.ApiResponseMerchantDelete.FromString,
                _registered_method=True)
        self.RestoreAllMerchant = channel.unary_unary(
                '/pb.merchant.MerchantCommandService/RestoreAllMerchant',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=merchant_dot_merchant__common__pb2.ApiResponseMerchantAll.FromString,
                _registered_method=True)
        self.DeleteAllMerchantPermanent = channel.unary_unary(
                '/pb.merchant.MerchantCommandService/DeleteAllMerchantPermanent',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=merchant_dot_merchant__common__pb2.ApiResponseMerchantAll.FromString,
                _registered_method=True)


class MerchantCommandServiceServicer:
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

    def UpdateStatus(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def TrashedMerchant(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RestoreMerchant(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteMerchantPermanent(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RestoreAllMerchant(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteAllMerchantPermanent(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_MerchantCommandServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Create': grpc.unary_unary_rpc_method_handler(
                    servicer.Create,
                    request_deserializer=merchant_dot_merchant__command__pb2.CreateMerchantRequest.FromString,
                    response_serializer=merchant_dot_merchant__common__pb2.ApiResponseMerchant.SerializeToString,
            ),
            'Update': grpc.unary_unary_rpc_method_handler(
                    servicer.Update,
                    request_deserializer=merchant_dot_merchant__command__pb2.UpdateMerchantRequest.FromString,
                    response_serializer=merchant_dot_merchant__common__pb2.ApiResponseMerchant.SerializeToString,
            ),
            'UpdateStatus': grpc.unary_unary_rpc_method_handler(
                    servicer.UpdateStatus,
                    request_deserializer=merchant_dot_merchant__command__pb2.UpdateMerchantStatusRequest.FromString,
                    response_serializer=merchant_dot_merchant__common__pb2.ApiResponseMerchant.SerializeToString,
            ),
            'TrashedMerchant': grpc.unary_unary_rpc_method_handler(
                    servicer.TrashedMerchant,
                    request_deserializer=merchant_dot_merchant__common__pb2.FindByIdMerchantRequest.FromString,
                    response_serializer=merchant_dot_merchant__common__pb2.ApiResponseMerchantDeleteAt.SerializeToString,
            ),
            'RestoreMerchant': grpc.unary_unary_rpc_method_handler(
                    servicer.RestoreMerchant,
                    request_deserializer=merchant_dot_merchant__common__pb2.FindByIdMerchantRequest.FromString,
                    response_serializer=merchant_dot_merchant__common__pb2.ApiResponseMerchant.SerializeToString,
            ),
            'DeleteMerchantPermanent': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteMerchantPermanent,
                    request_deserializer=merchant_dot_merchant__common__pb2.FindByIdMerchantRequest.FromString,
                    response_serializer=merchant_dot_merchant__common__pb2.ApiResponseMerchantDelete.SerializeToString,
            ),
            'RestoreAllMerchant': grpc.unary_unary_rpc_method_handler(
                    servicer.RestoreAllMerchant,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=merchant_dot_merchant__common__pb2.ApiResponseMerchantAll.SerializeToString,
            ),
            'DeleteAllMerchantPermanent': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteAllMerchantPermanent,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=merchant_dot_merchant__common__pb2.ApiResponseMerchantAll.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'pb.merchant.MerchantCommandService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('pb.merchant.MerchantCommandService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class MerchantCommandService:
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
            '/pb.merchant.MerchantCommandService/Create',
            merchant_dot_merchant__command__pb2.CreateMerchantRequest.SerializeToString,
            merchant_dot_merchant__common__pb2.ApiResponseMerchant.FromString,
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
            '/pb.merchant.MerchantCommandService/Update',
            merchant_dot_merchant__command__pb2.UpdateMerchantRequest.SerializeToString,
            merchant_dot_merchant__common__pb2.ApiResponseMerchant.FromString,
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
    def UpdateStatus(request,
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
            '/pb.merchant.MerchantCommandService/UpdateStatus',
            merchant_dot_merchant__command__pb2.UpdateMerchantStatusRequest.SerializeToString,
            merchant_dot_merchant__common__pb2.ApiResponseMerchant.FromString,
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
    def TrashedMerchant(request,
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
            '/pb.merchant.MerchantCommandService/TrashedMerchant',
            merchant_dot_merchant__common__pb2.FindByIdMerchantRequest.SerializeToString,
            merchant_dot_merchant__common__pb2.ApiResponseMerchantDeleteAt.FromString,
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
    def RestoreMerchant(request,
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
            '/pb.merchant.MerchantCommandService/RestoreMerchant',
            merchant_dot_merchant__common__pb2.FindByIdMerchantRequest.SerializeToString,
            merchant_dot_merchant__common__pb2.ApiResponseMerchant.FromString,
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
    def DeleteMerchantPermanent(request,
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
            '/pb.merchant.MerchantCommandService/DeleteMerchantPermanent',
            merchant_dot_merchant__common__pb2.FindByIdMerchantRequest.SerializeToString,
            merchant_dot_merchant__common__pb2.ApiResponseMerchantDelete.FromString,
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
    def RestoreAllMerchant(request,
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
            '/pb.merchant.MerchantCommandService/RestoreAllMerchant',
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            merchant_dot_merchant__common__pb2.ApiResponseMerchantAll.FromString,
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
    def DeleteAllMerchantPermanent(request,
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
            '/pb.merchant.MerchantCommandService/DeleteAllMerchantPermanent',
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            merchant_dot_merchant__common__pb2.ApiResponseMerchantAll.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
