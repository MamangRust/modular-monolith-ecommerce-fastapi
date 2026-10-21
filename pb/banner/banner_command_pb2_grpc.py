# DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from pb.banner import banner_command_pb2 as banner_dot_banner__command__pb2
from pb.banner import banner_common_pb2 as banner_dot_banner__common__pb2
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2

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
        + ' but the generated code in banner/banner_command_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class BannerCommandServiceStub:
    """Missing associated documentation comment in.proto file."""

    def __init__(self, channel):
        """Constructor. Args: channel: A grpc.Channel."""
        self.Create = channel.unary_unary(
                '/pb.banner.BannerCommandService/Create',
                request_serializer=banner_dot_banner__command__pb2.CreateBannerRequest.SerializeToString,
                response_deserializer=banner_dot_banner__common__pb2.ApiResponseBanner.FromString,
                _registered_method=True)
        self.Update = channel.unary_unary(
                '/pb.banner.BannerCommandService/Update',
                request_serializer=banner_dot_banner__command__pb2.UpdateBannerRequest.SerializeToString,
                response_deserializer=banner_dot_banner__common__pb2.ApiResponseBanner.FromString,
                _registered_method=True)
        self.Trash = channel.unary_unary(
                '/pb.banner.BannerCommandService/Trash',
                request_serializer=banner_dot_banner__common__pb2.FindByIdBannerRequest.SerializeToString,
                response_deserializer=banner_dot_banner__common__pb2.ApiResponseBannerDeleteAt.FromString,
                _registered_method=True)
        self.Restore = channel.unary_unary(
                '/pb.banner.BannerCommandService/Restore',
                request_serializer=banner_dot_banner__common__pb2.FindByIdBannerRequest.SerializeToString,
                response_deserializer=banner_dot_banner__common__pb2.ApiResponseBannerDeleteAt.FromString,
                _registered_method=True)
        self.DeletePermanent = channel.unary_unary(
                '/pb.banner.BannerCommandService/DeletePermanent',
                request_serializer=banner_dot_banner__common__pb2.FindByIdBannerRequest.SerializeToString,
                response_deserializer=banner_dot_banner__common__pb2.ApiResponseBannerDelete.FromString,
                _registered_method=True)
        self.RestoreAll = channel.unary_unary(
                '/pb.banner.BannerCommandService/RestoreAll',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=banner_dot_banner__common__pb2.ApiResponseBannerAll.FromString,
                _registered_method=True)
        self.DeleteAll = channel.unary_unary(
                '/pb.banner.BannerCommandService/DeleteAll',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=banner_dot_banner__common__pb2.ApiResponseBannerAll.FromString,
                _registered_method=True)


class BannerCommandServiceServicer:
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

    def Trash(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Restore(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeletePermanent(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RestoreAll(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteAll(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_BannerCommandServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Create': grpc.unary_unary_rpc_method_handler(
                    servicer.Create,
                    request_deserializer=banner_dot_banner__command__pb2.CreateBannerRequest.FromString,
                    response_serializer=banner_dot_banner__common__pb2.ApiResponseBanner.SerializeToString,
            ),
            'Update': grpc.unary_unary_rpc_method_handler(
                    servicer.Update,
                    request_deserializer=banner_dot_banner__command__pb2.UpdateBannerRequest.FromString,
                    response_serializer=banner_dot_banner__common__pb2.ApiResponseBanner.SerializeToString,
            ),
            'Trash': grpc.unary_unary_rpc_method_handler(
                    servicer.Trash,
                    request_deserializer=banner_dot_banner__common__pb2.FindByIdBannerRequest.FromString,
                    response_serializer=banner_dot_banner__common__pb2.ApiResponseBannerDeleteAt.SerializeToString,
            ),
            'Restore': grpc.unary_unary_rpc_method_handler(
                    servicer.Restore,
                    request_deserializer=banner_dot_banner__common__pb2.FindByIdBannerRequest.FromString,
                    response_serializer=banner_dot_banner__common__pb2.ApiResponseBannerDeleteAt.SerializeToString,
            ),
            'DeletePermanent': grpc.unary_unary_rpc_method_handler(
                    servicer.DeletePermanent,
                    request_deserializer=banner_dot_banner__common__pb2.FindByIdBannerRequest.FromString,
                    response_serializer=banner_dot_banner__common__pb2.ApiResponseBannerDelete.SerializeToString,
            ),
            'RestoreAll': grpc.unary_unary_rpc_method_handler(
                    servicer.RestoreAll,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=banner_dot_banner__common__pb2.ApiResponseBannerAll.SerializeToString,
            ),
            'DeleteAll': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteAll,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=banner_dot_banner__common__pb2.ApiResponseBannerAll.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'pb.banner.BannerCommandService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('pb.banner.BannerCommandService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class BannerCommandService:
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
            '/pb.banner.BannerCommandService/Create',
            banner_dot_banner__command__pb2.CreateBannerRequest.SerializeToString,
            banner_dot_banner__common__pb2.ApiResponseBanner.FromString,
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
            '/pb.banner.BannerCommandService/Update',
            banner_dot_banner__command__pb2.UpdateBannerRequest.SerializeToString,
            banner_dot_banner__common__pb2.ApiResponseBanner.FromString,
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
    def Trash(request,
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
            '/pb.banner.BannerCommandService/Trash',
            banner_dot_banner__common__pb2.FindByIdBannerRequest.SerializeToString,
            banner_dot_banner__common__pb2.ApiResponseBannerDeleteAt.FromString,
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
    def Restore(request,
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
            '/pb.banner.BannerCommandService/Restore',
            banner_dot_banner__common__pb2.FindByIdBannerRequest.SerializeToString,
            banner_dot_banner__common__pb2.ApiResponseBannerDeleteAt.FromString,
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
    def DeletePermanent(request,
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
            '/pb.banner.BannerCommandService/DeletePermanent',
            banner_dot_banner__common__pb2.FindByIdBannerRequest.SerializeToString,
            banner_dot_banner__common__pb2.ApiResponseBannerDelete.FromString,
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
    def RestoreAll(request,
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
            '/pb.banner.BannerCommandService/RestoreAll',
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            banner_dot_banner__common__pb2.ApiResponseBannerAll.FromString,
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
    def DeleteAll(request,
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
            '/pb.banner.BannerCommandService/DeleteAll',
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            banner_dot_banner__common__pb2.ApiResponseBannerAll.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
