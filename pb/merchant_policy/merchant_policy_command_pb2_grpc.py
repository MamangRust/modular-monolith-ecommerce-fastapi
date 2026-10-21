# DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from pb.merchant import merchant_common_pb2 as merchant_dot_merchant__common__pb2
from pb.merchant_policy import merchant_policy_command_pb2 as merchant__policy_dot_merchant__policy__command__pb2
from pb.merchant_policy import merchant_policy_common_pb2 as merchant__policy_dot_merchant__policy__common__pb2

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
        + ' but the generated code in merchant_policy/merchant_policy_command_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class MerchantPolicyCommandServiceStub:
    """Missing associated documentation comment in.proto file."""

    def __init__(self, channel):
        """Constructor. Args: channel: A grpc.Channel."""
        self.Create = channel.unary_unary(
                '/pb.merchant_policy.MerchantPolicyCommandService/Create',
                request_serializer=merchant__policy_dot_merchant__policy__command__pb2.CreateMerchantPoliciesRequest.SerializeToString,
                response_deserializer=merchant__policy_dot_merchant__policy__common__pb2.ApiResponseMerchantPolicies.FromString,
                _registered_method=True)
        self.Update = channel.unary_unary(
                '/pb.merchant_policy.MerchantPolicyCommandService/Update',
                request_serializer=merchant__policy_dot_merchant__policy__command__pb2.UpdateMerchantPoliciesRequest.SerializeToString,
                response_deserializer=merchant__policy_dot_merchant__policy__common__pb2.ApiResponseMerchantPolicies.FromString,
                _registered_method=True)
        self.TrashedMerchantPolicies = channel.unary_unary(
                '/pb.merchant_policy.MerchantPolicyCommandService/TrashedMerchantPolicies',
                request_serializer=merchant__policy_dot_merchant__policy__common__pb2.FindByIdMerchantPoliciesRequest.SerializeToString,
                response_deserializer=merchant__policy_dot_merchant__policy__common__pb2.ApiResponseMerchantPoliciesDeleteAt.FromString,
                _registered_method=True)
        self.RestoreMerchantPolicies = channel.unary_unary(
                '/pb.merchant_policy.MerchantPolicyCommandService/RestoreMerchantPolicies',
                request_serializer=merchant__policy_dot_merchant__policy__common__pb2.FindByIdMerchantPoliciesRequest.SerializeToString,
                response_deserializer=merchant__policy_dot_merchant__policy__common__pb2.ApiResponseMerchantPoliciesDeleteAt.FromString,
                _registered_method=True)
        self.DeleteMerchantPoliciesPermanent = channel.unary_unary(
                '/pb.merchant_policy.MerchantPolicyCommandService/DeleteMerchantPoliciesPermanent',
                request_serializer=merchant__policy_dot_merchant__policy__common__pb2.FindByIdMerchantPoliciesRequest.SerializeToString,
                response_deserializer=merchant_dot_merchant__common__pb2.ApiResponseMerchantDelete.FromString,
                _registered_method=True)
        self.RestoreAllMerchantPolicies = channel.unary_unary(
                '/pb.merchant_policy.MerchantPolicyCommandService/RestoreAllMerchantPolicies',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=merchant_dot_merchant__common__pb2.ApiResponseMerchantAll.FromString,
                _registered_method=True)
        self.DeleteAllMerchantPoliciesPermanent = channel.unary_unary(
                '/pb.merchant_policy.MerchantPolicyCommandService/DeleteAllMerchantPoliciesPermanent',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=merchant_dot_merchant__common__pb2.ApiResponseMerchantAll.FromString,
                _registered_method=True)


class MerchantPolicyCommandServiceServicer:
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

    def TrashedMerchantPolicies(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RestoreMerchantPolicies(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteMerchantPoliciesPermanent(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RestoreAllMerchantPolicies(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteAllMerchantPoliciesPermanent(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_MerchantPolicyCommandServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Create': grpc.unary_unary_rpc_method_handler(
                    servicer.Create,
                    request_deserializer=merchant__policy_dot_merchant__policy__command__pb2.CreateMerchantPoliciesRequest.FromString,
                    response_serializer=merchant__policy_dot_merchant__policy__common__pb2.ApiResponseMerchantPolicies.SerializeToString,
            ),
            'Update': grpc.unary_unary_rpc_method_handler(
                    servicer.Update,
                    request_deserializer=merchant__policy_dot_merchant__policy__command__pb2.UpdateMerchantPoliciesRequest.FromString,
                    response_serializer=merchant__policy_dot_merchant__policy__common__pb2.ApiResponseMerchantPolicies.SerializeToString,
            ),
            'TrashedMerchantPolicies': grpc.unary_unary_rpc_method_handler(
                    servicer.TrashedMerchantPolicies,
                    request_deserializer=merchant__policy_dot_merchant__policy__common__pb2.FindByIdMerchantPoliciesRequest.FromString,
                    response_serializer=merchant__policy_dot_merchant__policy__common__pb2.ApiResponseMerchantPoliciesDeleteAt.SerializeToString,
            ),
            'RestoreMerchantPolicies': grpc.unary_unary_rpc_method_handler(
                    servicer.RestoreMerchantPolicies,
                    request_deserializer=merchant__policy_dot_merchant__policy__common__pb2.FindByIdMerchantPoliciesRequest.FromString,
                    response_serializer=merchant__policy_dot_merchant__policy__common__pb2.ApiResponseMerchantPoliciesDeleteAt.SerializeToString,
            ),
            'DeleteMerchantPoliciesPermanent': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteMerchantPoliciesPermanent,
                    request_deserializer=merchant__policy_dot_merchant__policy__common__pb2.FindByIdMerchantPoliciesRequest.FromString,
                    response_serializer=merchant_dot_merchant__common__pb2.ApiResponseMerchantDelete.SerializeToString,
            ),
            'RestoreAllMerchantPolicies': grpc.unary_unary_rpc_method_handler(
                    servicer.RestoreAllMerchantPolicies,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=merchant_dot_merchant__common__pb2.ApiResponseMerchantAll.SerializeToString,
            ),
            'DeleteAllMerchantPoliciesPermanent': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteAllMerchantPoliciesPermanent,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=merchant_dot_merchant__common__pb2.ApiResponseMerchantAll.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'pb.merchant_policy.MerchantPolicyCommandService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('pb.merchant_policy.MerchantPolicyCommandService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class MerchantPolicyCommandService:
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
            '/pb.merchant_policy.MerchantPolicyCommandService/Create',
            merchant__policy_dot_merchant__policy__command__pb2.CreateMerchantPoliciesRequest.SerializeToString,
            merchant__policy_dot_merchant__policy__common__pb2.ApiResponseMerchantPolicies.FromString,
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
            '/pb.merchant_policy.MerchantPolicyCommandService/Update',
            merchant__policy_dot_merchant__policy__command__pb2.UpdateMerchantPoliciesRequest.SerializeToString,
            merchant__policy_dot_merchant__policy__common__pb2.ApiResponseMerchantPolicies.FromString,
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
    def TrashedMerchantPolicies(request,
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
            '/pb.merchant_policy.MerchantPolicyCommandService/TrashedMerchantPolicies',
            merchant__policy_dot_merchant__policy__common__pb2.FindByIdMerchantPoliciesRequest.SerializeToString,
            merchant__policy_dot_merchant__policy__common__pb2.ApiResponseMerchantPoliciesDeleteAt.FromString,
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
    def RestoreMerchantPolicies(request,
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
            '/pb.merchant_policy.MerchantPolicyCommandService/RestoreMerchantPolicies',
            merchant__policy_dot_merchant__policy__common__pb2.FindByIdMerchantPoliciesRequest.SerializeToString,
            merchant__policy_dot_merchant__policy__common__pb2.ApiResponseMerchantPoliciesDeleteAt.FromString,
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
    def DeleteMerchantPoliciesPermanent(request,
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
            '/pb.merchant_policy.MerchantPolicyCommandService/DeleteMerchantPoliciesPermanent',
            merchant__policy_dot_merchant__policy__common__pb2.FindByIdMerchantPoliciesRequest.SerializeToString,
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
    def RestoreAllMerchantPolicies(request,
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
            '/pb.merchant_policy.MerchantPolicyCommandService/RestoreAllMerchantPolicies',
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
    def DeleteAllMerchantPoliciesPermanent(request,
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
            '/pb.merchant_policy.MerchantPolicyCommandService/DeleteAllMerchantPoliciesPermanent',
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
