# DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from pb.merchant import merchant_common_pb2 as merchant_dot_merchant__common__pb2
from pb.merchant_detail import merchant_detail_command_pb2 as merchant__detail_dot_merchant__detail__command__pb2
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
        + ' but the generated code in merchant_detail/merchant_detail_command_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class MerchantDetailCommandServiceStub:
    """Missing associated documentation comment in.proto file."""

    def __init__(self, channel):
        """Constructor. Args: channel: A grpc.Channel."""
        self.Create = channel.unary_unary(
                '/pb.merchant_detail.MerchantDetailCommandService/Create',
                request_serializer=merchant__detail_dot_merchant__detail__command__pb2.CreateMerchantDetailRequest.SerializeToString,
                response_deserializer=merchant__detail_dot_merchant__detail__common__pb2.ApiResponseMerchantDetail.FromString,
                _registered_method=True)
        self.Update = channel.unary_unary(
                '/pb.merchant_detail.MerchantDetailCommandService/Update',
                request_serializer=merchant__detail_dot_merchant__detail__command__pb2.UpdateMerchantDetailRequest.SerializeToString,
                response_deserializer=merchant__detail_dot_merchant__detail__common__pb2.ApiResponseMerchantDetail.FromString,
                _registered_method=True)
        self.TrashedMerchantDetail = channel.unary_unary(
                '/pb.merchant_detail.MerchantDetailCommandService/TrashedMerchantDetail',
                request_serializer=merchant__detail_dot_merchant__detail__common__pb2.FindByIdMerchantDetailRequest.SerializeToString,
                response_deserializer=merchant__detail_dot_merchant__detail__common__pb2.ApiResponseMerchantDetailDeleteAt.FromString,
                _registered_method=True)
        self.RestoreMerchantDetail = channel.unary_unary(
                '/pb.merchant_detail.MerchantDetailCommandService/RestoreMerchantDetail',
                request_serializer=merchant__detail_dot_merchant__detail__common__pb2.FindByIdMerchantDetailRequest.SerializeToString,
                response_deserializer=merchant__detail_dot_merchant__detail__common__pb2.ApiResponseMerchantDetailDeleteAt.FromString,
                _registered_method=True)
        self.DeleteMerchantDetailPermanent = channel.unary_unary(
                '/pb.merchant_detail.MerchantDetailCommandService/DeleteMerchantDetailPermanent',
                request_serializer=merchant__detail_dot_merchant__detail__common__pb2.FindByIdMerchantDetailRequest.SerializeToString,
                response_deserializer=merchant_dot_merchant__common__pb2.ApiResponseMerchantDelete.FromString,
                _registered_method=True)
        self.RestoreAllMerchantDetail = channel.unary_unary(
                '/pb.merchant_detail.MerchantDetailCommandService/RestoreAllMerchantDetail',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=merchant_dot_merchant__common__pb2.ApiResponseMerchantAll.FromString,
                _registered_method=True)
        self.DeleteAllMerchantDetailPermanent = channel.unary_unary(
                '/pb.merchant_detail.MerchantDetailCommandService/DeleteAllMerchantDetailPermanent',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=merchant_dot_merchant__common__pb2.ApiResponseMerchantAll.FromString,
                _registered_method=True)


class MerchantDetailCommandServiceServicer:
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

    def TrashedMerchantDetail(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RestoreMerchantDetail(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteMerchantDetailPermanent(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RestoreAllMerchantDetail(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteAllMerchantDetailPermanent(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_MerchantDetailCommandServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Create': grpc.unary_unary_rpc_method_handler(
                    servicer.Create,
                    request_deserializer=merchant__detail_dot_merchant__detail__command__pb2.CreateMerchantDetailRequest.FromString,
                    response_serializer=merchant__detail_dot_merchant__detail__common__pb2.ApiResponseMerchantDetail.SerializeToString,
            ),
            'Update': grpc.unary_unary_rpc_method_handler(
                    servicer.Update,
                    request_deserializer=merchant__detail_dot_merchant__detail__command__pb2.UpdateMerchantDetailRequest.FromString,
                    response_serializer=merchant__detail_dot_merchant__detail__common__pb2.ApiResponseMerchantDetail.SerializeToString,
            ),
            'TrashedMerchantDetail': grpc.unary_unary_rpc_method_handler(
                    servicer.TrashedMerchantDetail,
                    request_deserializer=merchant__detail_dot_merchant__detail__common__pb2.FindByIdMerchantDetailRequest.FromString,
                    response_serializer=merchant__detail_dot_merchant__detail__common__pb2.ApiResponseMerchantDetailDeleteAt.SerializeToString,
            ),
            'RestoreMerchantDetail': grpc.unary_unary_rpc_method_handler(
                    servicer.RestoreMerchantDetail,
                    request_deserializer=merchant__detail_dot_merchant__detail__common__pb2.FindByIdMerchantDetailRequest.FromString,
                    response_serializer=merchant__detail_dot_merchant__detail__common__pb2.ApiResponseMerchantDetailDeleteAt.SerializeToString,
            ),
            'DeleteMerchantDetailPermanent': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteMerchantDetailPermanent,
                    request_deserializer=merchant__detail_dot_merchant__detail__common__pb2.FindByIdMerchantDetailRequest.FromString,
                    response_serializer=merchant_dot_merchant__common__pb2.ApiResponseMerchantDelete.SerializeToString,
            ),
            'RestoreAllMerchantDetail': grpc.unary_unary_rpc_method_handler(
                    servicer.RestoreAllMerchantDetail,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=merchant_dot_merchant__common__pb2.ApiResponseMerchantAll.SerializeToString,
            ),
            'DeleteAllMerchantDetailPermanent': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteAllMerchantDetailPermanent,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=merchant_dot_merchant__common__pb2.ApiResponseMerchantAll.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'pb.merchant_detail.MerchantDetailCommandService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('pb.merchant_detail.MerchantDetailCommandService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class MerchantDetailCommandService:
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
            '/pb.merchant_detail.MerchantDetailCommandService/Create',
            merchant__detail_dot_merchant__detail__command__pb2.CreateMerchantDetailRequest.SerializeToString,
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
            '/pb.merchant_detail.MerchantDetailCommandService/Update',
            merchant__detail_dot_merchant__detail__command__pb2.UpdateMerchantDetailRequest.SerializeToString,
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
    def TrashedMerchantDetail(request,
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
            '/pb.merchant_detail.MerchantDetailCommandService/TrashedMerchantDetail',
            merchant__detail_dot_merchant__detail__common__pb2.FindByIdMerchantDetailRequest.SerializeToString,
            merchant__detail_dot_merchant__detail__common__pb2.ApiResponseMerchantDetailDeleteAt.FromString,
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
    def RestoreMerchantDetail(request,
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
            '/pb.merchant_detail.MerchantDetailCommandService/RestoreMerchantDetail',
            merchant__detail_dot_merchant__detail__common__pb2.FindByIdMerchantDetailRequest.SerializeToString,
            merchant__detail_dot_merchant__detail__common__pb2.ApiResponseMerchantDetailDeleteAt.FromString,
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
    def DeleteMerchantDetailPermanent(request,
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
            '/pb.merchant_detail.MerchantDetailCommandService/DeleteMerchantDetailPermanent',
            merchant__detail_dot_merchant__detail__common__pb2.FindByIdMerchantDetailRequest.SerializeToString,
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
    def RestoreAllMerchantDetail(request,
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
            '/pb.merchant_detail.MerchantDetailCommandService/RestoreAllMerchantDetail',
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
    def DeleteAllMerchantDetailPermanent(request,
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
            '/pb.merchant_detail.MerchantDetailCommandService/DeleteAllMerchantDetailPermanent',
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
