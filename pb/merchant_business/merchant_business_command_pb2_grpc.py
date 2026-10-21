# DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from pb.merchant import merchant_common_pb2 as merchant_dot_merchant__common__pb2
from pb.merchant_business import merchant_business_command_pb2 as merchant__business_dot_merchant__business__command__pb2
from pb.merchant_business import merchant_business_common_pb2 as merchant__business_dot_merchant__business__common__pb2

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
        + ' but the generated code in merchant_business/merchant_business_command_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class MerchantBusinessCommandServiceStub:
    """Missing associated documentation comment in.proto file."""

    def __init__(self, channel):
        """Constructor. Args: channel: A grpc.Channel."""
        self.Create = channel.unary_unary(
                '/pb.merchant_business.MerchantBusinessCommandService/Create',
                request_serializer=merchant__business_dot_merchant__business__command__pb2.CreateMerchantBusinessRequest.SerializeToString,
                response_deserializer=merchant__business_dot_merchant__business__common__pb2.ApiResponseMerchantBusiness.FromString,
                _registered_method=True)
        self.Update = channel.unary_unary(
                '/pb.merchant_business.MerchantBusinessCommandService/Update',
                request_serializer=merchant__business_dot_merchant__business__command__pb2.UpdateMerchantBusinessRequest.SerializeToString,
                response_deserializer=merchant__business_dot_merchant__business__common__pb2.ApiResponseMerchantBusiness.FromString,
                _registered_method=True)
        self.TrashedMerchantBusiness = channel.unary_unary(
                '/pb.merchant_business.MerchantBusinessCommandService/TrashedMerchantBusiness',
                request_serializer=merchant__business_dot_merchant__business__common__pb2.FindByIdMerchantBusinessRequest.SerializeToString,
                response_deserializer=merchant__business_dot_merchant__business__common__pb2.ApiResponseMerchantBusinessDeleteAt.FromString,
                _registered_method=True)
        self.RestoreMerchantBusiness = channel.unary_unary(
                '/pb.merchant_business.MerchantBusinessCommandService/RestoreMerchantBusiness',
                request_serializer=merchant__business_dot_merchant__business__common__pb2.FindByIdMerchantBusinessRequest.SerializeToString,
                response_deserializer=merchant__business_dot_merchant__business__common__pb2.ApiResponseMerchantBusinessDeleteAt.FromString,
                _registered_method=True)
        self.DeleteMerchantBusinessPermanent = channel.unary_unary(
                '/pb.merchant_business.MerchantBusinessCommandService/DeleteMerchantBusinessPermanent',
                request_serializer=merchant__business_dot_merchant__business__common__pb2.FindByIdMerchantBusinessRequest.SerializeToString,
                response_deserializer=merchant_dot_merchant__common__pb2.ApiResponseMerchantDelete.FromString,
                _registered_method=True)
        self.RestoreAllMerchantBusiness = channel.unary_unary(
                '/pb.merchant_business.MerchantBusinessCommandService/RestoreAllMerchantBusiness',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=merchant_dot_merchant__common__pb2.ApiResponseMerchantAll.FromString,
                _registered_method=True)
        self.DeleteAllMerchantBusinessPermanent = channel.unary_unary(
                '/pb.merchant_business.MerchantBusinessCommandService/DeleteAllMerchantBusinessPermanent',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=merchant_dot_merchant__common__pb2.ApiResponseMerchantAll.FromString,
                _registered_method=True)


class MerchantBusinessCommandServiceServicer:
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

    def TrashedMerchantBusiness(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RestoreMerchantBusiness(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteMerchantBusinessPermanent(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RestoreAllMerchantBusiness(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteAllMerchantBusinessPermanent(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_MerchantBusinessCommandServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Create': grpc.unary_unary_rpc_method_handler(
                    servicer.Create,
                    request_deserializer=merchant__business_dot_merchant__business__command__pb2.CreateMerchantBusinessRequest.FromString,
                    response_serializer=merchant__business_dot_merchant__business__common__pb2.ApiResponseMerchantBusiness.SerializeToString,
            ),
            'Update': grpc.unary_unary_rpc_method_handler(
                    servicer.Update,
                    request_deserializer=merchant__business_dot_merchant__business__command__pb2.UpdateMerchantBusinessRequest.FromString,
                    response_serializer=merchant__business_dot_merchant__business__common__pb2.ApiResponseMerchantBusiness.SerializeToString,
            ),
            'TrashedMerchantBusiness': grpc.unary_unary_rpc_method_handler(
                    servicer.TrashedMerchantBusiness,
                    request_deserializer=merchant__business_dot_merchant__business__common__pb2.FindByIdMerchantBusinessRequest.FromString,
                    response_serializer=merchant__business_dot_merchant__business__common__pb2.ApiResponseMerchantBusinessDeleteAt.SerializeToString,
            ),
            'RestoreMerchantBusiness': grpc.unary_unary_rpc_method_handler(
                    servicer.RestoreMerchantBusiness,
                    request_deserializer=merchant__business_dot_merchant__business__common__pb2.FindByIdMerchantBusinessRequest.FromString,
                    response_serializer=merchant__business_dot_merchant__business__common__pb2.ApiResponseMerchantBusinessDeleteAt.SerializeToString,
            ),
            'DeleteMerchantBusinessPermanent': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteMerchantBusinessPermanent,
                    request_deserializer=merchant__business_dot_merchant__business__common__pb2.FindByIdMerchantBusinessRequest.FromString,
                    response_serializer=merchant_dot_merchant__common__pb2.ApiResponseMerchantDelete.SerializeToString,
            ),
            'RestoreAllMerchantBusiness': grpc.unary_unary_rpc_method_handler(
                    servicer.RestoreAllMerchantBusiness,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=merchant_dot_merchant__common__pb2.ApiResponseMerchantAll.SerializeToString,
            ),
            'DeleteAllMerchantBusinessPermanent': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteAllMerchantBusinessPermanent,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=merchant_dot_merchant__common__pb2.ApiResponseMerchantAll.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'pb.merchant_business.MerchantBusinessCommandService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('pb.merchant_business.MerchantBusinessCommandService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class MerchantBusinessCommandService:
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
            '/pb.merchant_business.MerchantBusinessCommandService/Create',
            merchant__business_dot_merchant__business__command__pb2.CreateMerchantBusinessRequest.SerializeToString,
            merchant__business_dot_merchant__business__common__pb2.ApiResponseMerchantBusiness.FromString,
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
            '/pb.merchant_business.MerchantBusinessCommandService/Update',
            merchant__business_dot_merchant__business__command__pb2.UpdateMerchantBusinessRequest.SerializeToString,
            merchant__business_dot_merchant__business__common__pb2.ApiResponseMerchantBusiness.FromString,
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
    def TrashedMerchantBusiness(request,
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
            '/pb.merchant_business.MerchantBusinessCommandService/TrashedMerchantBusiness',
            merchant__business_dot_merchant__business__common__pb2.FindByIdMerchantBusinessRequest.SerializeToString,
            merchant__business_dot_merchant__business__common__pb2.ApiResponseMerchantBusinessDeleteAt.FromString,
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
    def RestoreMerchantBusiness(request,
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
            '/pb.merchant_business.MerchantBusinessCommandService/RestoreMerchantBusiness',
            merchant__business_dot_merchant__business__common__pb2.FindByIdMerchantBusinessRequest.SerializeToString,
            merchant__business_dot_merchant__business__common__pb2.ApiResponseMerchantBusinessDeleteAt.FromString,
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
    def DeleteMerchantBusinessPermanent(request,
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
            '/pb.merchant_business.MerchantBusinessCommandService/DeleteMerchantBusinessPermanent',
            merchant__business_dot_merchant__business__common__pb2.FindByIdMerchantBusinessRequest.SerializeToString,
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
    def RestoreAllMerchantBusiness(request,
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
            '/pb.merchant_business.MerchantBusinessCommandService/RestoreAllMerchantBusiness',
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
    def DeleteAllMerchantBusinessPermanent(request,
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
            '/pb.merchant_business.MerchantBusinessCommandService/DeleteAllMerchantBusinessPermanent',
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
