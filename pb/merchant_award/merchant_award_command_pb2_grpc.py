# DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from pb.merchant import merchant_common_pb2 as merchant_dot_merchant__common__pb2
from pb.merchant_award import merchant_award_command_pb2 as merchant__award_dot_merchant__award__command__pb2
from pb.merchant_award import merchant_award_common_pb2 as merchant__award_dot_merchant__award__common__pb2

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
        + ' but the generated code in merchant_award/merchant_award_command_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class MerchantAwardCommandServiceStub:
    """Missing associated documentation comment in.proto file."""

    def __init__(self, channel):
        """Constructor. Args: channel: A grpc.Channel."""
        self.Create = channel.unary_unary(
                '/pb.merchant_award.MerchantAwardCommandService/Create',
                request_serializer=merchant__award_dot_merchant__award__command__pb2.CreateMerchantAwardRequest.SerializeToString,
                response_deserializer=merchant__award_dot_merchant__award__common__pb2.ApiResponseMerchantAward.FromString,
                _registered_method=True)
        self.Update = channel.unary_unary(
                '/pb.merchant_award.MerchantAwardCommandService/Update',
                request_serializer=merchant__award_dot_merchant__award__command__pb2.UpdateMerchantAwardRequest.SerializeToString,
                response_deserializer=merchant__award_dot_merchant__award__common__pb2.ApiResponseMerchantAward.FromString,
                _registered_method=True)
        self.TrashedMerchantAward = channel.unary_unary(
                '/pb.merchant_award.MerchantAwardCommandService/TrashedMerchantAward',
                request_serializer=merchant__award_dot_merchant__award__common__pb2.FindByIdMerchantAwardRequest.SerializeToString,
                response_deserializer=merchant__award_dot_merchant__award__common__pb2.ApiResponseMerchantAwardDeleteAt.FromString,
                _registered_method=True)
        self.RestoreMerchantAward = channel.unary_unary(
                '/pb.merchant_award.MerchantAwardCommandService/RestoreMerchantAward',
                request_serializer=merchant__award_dot_merchant__award__common__pb2.FindByIdMerchantAwardRequest.SerializeToString,
                response_deserializer=merchant__award_dot_merchant__award__common__pb2.ApiResponseMerchantAwardDeleteAt.FromString,
                _registered_method=True)
        self.DeleteMerchantAwardPermanent = channel.unary_unary(
                '/pb.merchant_award.MerchantAwardCommandService/DeleteMerchantAwardPermanent',
                request_serializer=merchant__award_dot_merchant__award__common__pb2.FindByIdMerchantAwardRequest.SerializeToString,
                response_deserializer=merchant_dot_merchant__common__pb2.ApiResponseMerchantDelete.FromString,
                _registered_method=True)
        self.RestoreAllMerchantAward = channel.unary_unary(
                '/pb.merchant_award.MerchantAwardCommandService/RestoreAllMerchantAward',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=merchant_dot_merchant__common__pb2.ApiResponseMerchantAll.FromString,
                _registered_method=True)
        self.DeleteAllMerchantAwardPermanent = channel.unary_unary(
                '/pb.merchant_award.MerchantAwardCommandService/DeleteAllMerchantAwardPermanent',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=merchant_dot_merchant__common__pb2.ApiResponseMerchantAll.FromString,
                _registered_method=True)


class MerchantAwardCommandServiceServicer:
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

    def TrashedMerchantAward(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RestoreMerchantAward(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteMerchantAwardPermanent(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RestoreAllMerchantAward(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteAllMerchantAwardPermanent(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_MerchantAwardCommandServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Create': grpc.unary_unary_rpc_method_handler(
                    servicer.Create,
                    request_deserializer=merchant__award_dot_merchant__award__command__pb2.CreateMerchantAwardRequest.FromString,
                    response_serializer=merchant__award_dot_merchant__award__common__pb2.ApiResponseMerchantAward.SerializeToString,
            ),
            'Update': grpc.unary_unary_rpc_method_handler(
                    servicer.Update,
                    request_deserializer=merchant__award_dot_merchant__award__command__pb2.UpdateMerchantAwardRequest.FromString,
                    response_serializer=merchant__award_dot_merchant__award__common__pb2.ApiResponseMerchantAward.SerializeToString,
            ),
            'TrashedMerchantAward': grpc.unary_unary_rpc_method_handler(
                    servicer.TrashedMerchantAward,
                    request_deserializer=merchant__award_dot_merchant__award__common__pb2.FindByIdMerchantAwardRequest.FromString,
                    response_serializer=merchant__award_dot_merchant__award__common__pb2.ApiResponseMerchantAwardDeleteAt.SerializeToString,
            ),
            'RestoreMerchantAward': grpc.unary_unary_rpc_method_handler(
                    servicer.RestoreMerchantAward,
                    request_deserializer=merchant__award_dot_merchant__award__common__pb2.FindByIdMerchantAwardRequest.FromString,
                    response_serializer=merchant__award_dot_merchant__award__common__pb2.ApiResponseMerchantAwardDeleteAt.SerializeToString,
            ),
            'DeleteMerchantAwardPermanent': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteMerchantAwardPermanent,
                    request_deserializer=merchant__award_dot_merchant__award__common__pb2.FindByIdMerchantAwardRequest.FromString,
                    response_serializer=merchant_dot_merchant__common__pb2.ApiResponseMerchantDelete.SerializeToString,
            ),
            'RestoreAllMerchantAward': grpc.unary_unary_rpc_method_handler(
                    servicer.RestoreAllMerchantAward,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=merchant_dot_merchant__common__pb2.ApiResponseMerchantAll.SerializeToString,
            ),
            'DeleteAllMerchantAwardPermanent': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteAllMerchantAwardPermanent,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=merchant_dot_merchant__common__pb2.ApiResponseMerchantAll.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'pb.merchant_award.MerchantAwardCommandService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('pb.merchant_award.MerchantAwardCommandService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class MerchantAwardCommandService:
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
            '/pb.merchant_award.MerchantAwardCommandService/Create',
            merchant__award_dot_merchant__award__command__pb2.CreateMerchantAwardRequest.SerializeToString,
            merchant__award_dot_merchant__award__common__pb2.ApiResponseMerchantAward.FromString,
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
            '/pb.merchant_award.MerchantAwardCommandService/Update',
            merchant__award_dot_merchant__award__command__pb2.UpdateMerchantAwardRequest.SerializeToString,
            merchant__award_dot_merchant__award__common__pb2.ApiResponseMerchantAward.FromString,
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
    def TrashedMerchantAward(request,
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
            '/pb.merchant_award.MerchantAwardCommandService/TrashedMerchantAward',
            merchant__award_dot_merchant__award__common__pb2.FindByIdMerchantAwardRequest.SerializeToString,
            merchant__award_dot_merchant__award__common__pb2.ApiResponseMerchantAwardDeleteAt.FromString,
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
    def RestoreMerchantAward(request,
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
            '/pb.merchant_award.MerchantAwardCommandService/RestoreMerchantAward',
            merchant__award_dot_merchant__award__common__pb2.FindByIdMerchantAwardRequest.SerializeToString,
            merchant__award_dot_merchant__award__common__pb2.ApiResponseMerchantAwardDeleteAt.FromString,
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
    def DeleteMerchantAwardPermanent(request,
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
            '/pb.merchant_award.MerchantAwardCommandService/DeleteMerchantAwardPermanent',
            merchant__award_dot_merchant__award__common__pb2.FindByIdMerchantAwardRequest.SerializeToString,
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
    def RestoreAllMerchantAward(request,
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
            '/pb.merchant_award.MerchantAwardCommandService/RestoreAllMerchantAward',
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
    def DeleteAllMerchantAwardPermanent(request,
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
            '/pb.merchant_award.MerchantAwardCommandService/DeleteAllMerchantAwardPermanent',
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
