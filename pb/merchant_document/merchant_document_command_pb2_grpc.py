# DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from pb.merchant_document import merchant_document_command_pb2 as merchant__document_dot_merchant__document__command__pb2
from pb.merchant_document import merchant_document_common_pb2 as merchant__document_dot_merchant__document__common__pb2

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
        + ' but the generated code in merchant_document/merchant_document_command_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class MerchantDocumentCommandServiceStub:
    """Missing associated documentation comment in.proto file."""

    def __init__(self, channel):
        """Constructor. Args: channel: A grpc.Channel."""
        self.Create = channel.unary_unary(
                '/pb.merchant_document.MerchantDocumentCommandService/Create',
                request_serializer=merchant__document_dot_merchant__document__command__pb2.CreateMerchantDocumentRequest.SerializeToString,
                response_deserializer=merchant__document_dot_merchant__document__common__pb2.ApiResponseMerchantDocument.FromString,
                _registered_method=True)
        self.Update = channel.unary_unary(
                '/pb.merchant_document.MerchantDocumentCommandService/Update',
                request_serializer=merchant__document_dot_merchant__document__command__pb2.UpdateMerchantDocumentRequest.SerializeToString,
                response_deserializer=merchant__document_dot_merchant__document__common__pb2.ApiResponseMerchantDocument.FromString,
                _registered_method=True)
        self.UpdateStatus = channel.unary_unary(
                '/pb.merchant_document.MerchantDocumentCommandService/UpdateStatus',
                request_serializer=merchant__document_dot_merchant__document__command__pb2.UpdateMerchantDocumentStatusRequest.SerializeToString,
                response_deserializer=merchant__document_dot_merchant__document__common__pb2.ApiResponseMerchantDocument.FromString,
                _registered_method=True)
        self.Trashed = channel.unary_unary(
                '/pb.merchant_document.MerchantDocumentCommandService/Trashed',
                request_serializer=merchant__document_dot_merchant__document__command__pb2.TrashedMerchantDocumentRequest.SerializeToString,
                response_deserializer=merchant__document_dot_merchant__document__common__pb2.ApiResponseMerchantDocument.FromString,
                _registered_method=True)
        self.Restore = channel.unary_unary(
                '/pb.merchant_document.MerchantDocumentCommandService/Restore',
                request_serializer=merchant__document_dot_merchant__document__command__pb2.RestoreMerchantDocumentRequest.SerializeToString,
                response_deserializer=merchant__document_dot_merchant__document__common__pb2.ApiResponseMerchantDocument.FromString,
                _registered_method=True)
        self.DeletePermanent = channel.unary_unary(
                '/pb.merchant_document.MerchantDocumentCommandService/DeletePermanent',
                request_serializer=merchant__document_dot_merchant__document__command__pb2.DeleteMerchantDocumentPermanentRequest.SerializeToString,
                response_deserializer=merchant__document_dot_merchant__document__common__pb2.ApiResponseMerchantDocumentDelete.FromString,
                _registered_method=True)
        self.RestoreAll = channel.unary_unary(
                '/pb.merchant_document.MerchantDocumentCommandService/RestoreAll',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=merchant__document_dot_merchant__document__common__pb2.ApiResponseMerchantDocumentAll.FromString,
                _registered_method=True)
        self.DeleteAllPermanent = channel.unary_unary(
                '/pb.merchant_document.MerchantDocumentCommandService/DeleteAllPermanent',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=merchant__document_dot_merchant__document__common__pb2.ApiResponseMerchantDocumentAll.FromString,
                _registered_method=True)


class MerchantDocumentCommandServiceServicer:
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

    def Trashed(self, request, context):
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

    def DeleteAllPermanent(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_MerchantDocumentCommandServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Create': grpc.unary_unary_rpc_method_handler(
                    servicer.Create,
                    request_deserializer=merchant__document_dot_merchant__document__command__pb2.CreateMerchantDocumentRequest.FromString,
                    response_serializer=merchant__document_dot_merchant__document__common__pb2.ApiResponseMerchantDocument.SerializeToString,
            ),
            'Update': grpc.unary_unary_rpc_method_handler(
                    servicer.Update,
                    request_deserializer=merchant__document_dot_merchant__document__command__pb2.UpdateMerchantDocumentRequest.FromString,
                    response_serializer=merchant__document_dot_merchant__document__common__pb2.ApiResponseMerchantDocument.SerializeToString,
            ),
            'UpdateStatus': grpc.unary_unary_rpc_method_handler(
                    servicer.UpdateStatus,
                    request_deserializer=merchant__document_dot_merchant__document__command__pb2.UpdateMerchantDocumentStatusRequest.FromString,
                    response_serializer=merchant__document_dot_merchant__document__common__pb2.ApiResponseMerchantDocument.SerializeToString,
            ),
            'Trashed': grpc.unary_unary_rpc_method_handler(
                    servicer.Trashed,
                    request_deserializer=merchant__document_dot_merchant__document__command__pb2.TrashedMerchantDocumentRequest.FromString,
                    response_serializer=merchant__document_dot_merchant__document__common__pb2.ApiResponseMerchantDocument.SerializeToString,
            ),
            'Restore': grpc.unary_unary_rpc_method_handler(
                    servicer.Restore,
                    request_deserializer=merchant__document_dot_merchant__document__command__pb2.RestoreMerchantDocumentRequest.FromString,
                    response_serializer=merchant__document_dot_merchant__document__common__pb2.ApiResponseMerchantDocument.SerializeToString,
            ),
            'DeletePermanent': grpc.unary_unary_rpc_method_handler(
                    servicer.DeletePermanent,
                    request_deserializer=merchant__document_dot_merchant__document__command__pb2.DeleteMerchantDocumentPermanentRequest.FromString,
                    response_serializer=merchant__document_dot_merchant__document__common__pb2.ApiResponseMerchantDocumentDelete.SerializeToString,
            ),
            'RestoreAll': grpc.unary_unary_rpc_method_handler(
                    servicer.RestoreAll,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=merchant__document_dot_merchant__document__common__pb2.ApiResponseMerchantDocumentAll.SerializeToString,
            ),
            'DeleteAllPermanent': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteAllPermanent,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=merchant__document_dot_merchant__document__common__pb2.ApiResponseMerchantDocumentAll.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'pb.merchant_document.MerchantDocumentCommandService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('pb.merchant_document.MerchantDocumentCommandService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class MerchantDocumentCommandService:
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
            '/pb.merchant_document.MerchantDocumentCommandService/Create',
            merchant__document_dot_merchant__document__command__pb2.CreateMerchantDocumentRequest.SerializeToString,
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
            '/pb.merchant_document.MerchantDocumentCommandService/Update',
            merchant__document_dot_merchant__document__command__pb2.UpdateMerchantDocumentRequest.SerializeToString,
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
            '/pb.merchant_document.MerchantDocumentCommandService/UpdateStatus',
            merchant__document_dot_merchant__document__command__pb2.UpdateMerchantDocumentStatusRequest.SerializeToString,
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

    @staticmethod
    def Trashed(request,
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
            '/pb.merchant_document.MerchantDocumentCommandService/Trashed',
            merchant__document_dot_merchant__document__command__pb2.TrashedMerchantDocumentRequest.SerializeToString,
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
            '/pb.merchant_document.MerchantDocumentCommandService/Restore',
            merchant__document_dot_merchant__document__command__pb2.RestoreMerchantDocumentRequest.SerializeToString,
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
            '/pb.merchant_document.MerchantDocumentCommandService/DeletePermanent',
            merchant__document_dot_merchant__document__command__pb2.DeleteMerchantDocumentPermanentRequest.SerializeToString,
            merchant__document_dot_merchant__document__common__pb2.ApiResponseMerchantDocumentDelete.FromString,
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
            '/pb.merchant_document.MerchantDocumentCommandService/RestoreAll',
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            merchant__document_dot_merchant__document__common__pb2.ApiResponseMerchantDocumentAll.FromString,
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
    def DeleteAllPermanent(request,
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
            '/pb.merchant_document.MerchantDocumentCommandService/DeleteAllPermanent',
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            merchant__document_dot_merchant__document__common__pb2.ApiResponseMerchantDocumentAll.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
