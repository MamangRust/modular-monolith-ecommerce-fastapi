# DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from pb.review import review_common_pb2 as review_dot_review__common__pb2
from pb.review_detail import review_detail_command_pb2 as review__detail_dot_review__detail__command__pb2
from pb.review_detail import review_detail_common_pb2 as review__detail_dot_review__detail__common__pb2

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
        + ' but the generated code in review_detail/review_detail_command_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class ReviewDetailCommandServiceStub:
    """Missing associated documentation comment in.proto file."""

    def __init__(self, channel):
        """Constructor. Args: channel: A grpc.Channel."""
        self.Create = channel.unary_unary(
                '/pb.review_detail.ReviewDetailCommandService/Create',
                request_serializer=review__detail_dot_review__detail__command__pb2.CreateReviewDetailRequest.SerializeToString,
                response_deserializer=review__detail_dot_review__detail__common__pb2.ApiResponseReviewDetail.FromString,
                _registered_method=True)
        self.Update = channel.unary_unary(
                '/pb.review_detail.ReviewDetailCommandService/Update',
                request_serializer=review__detail_dot_review__detail__command__pb2.UpdateReviewDetailRequest.SerializeToString,
                response_deserializer=review__detail_dot_review__detail__common__pb2.ApiResponseReviewDetail.FromString,
                _registered_method=True)
        self.TrashedReviewDetail = channel.unary_unary(
                '/pb.review_detail.ReviewDetailCommandService/TrashedReviewDetail',
                request_serializer=review__detail_dot_review__detail__common__pb2.FindByIdReviewDetailRequest.SerializeToString,
                response_deserializer=review__detail_dot_review__detail__common__pb2.ApiResponseReviewDetailDeleteAt.FromString,
                _registered_method=True)
        self.RestoreReviewDetail = channel.unary_unary(
                '/pb.review_detail.ReviewDetailCommandService/RestoreReviewDetail',
                request_serializer=review__detail_dot_review__detail__common__pb2.FindByIdReviewDetailRequest.SerializeToString,
                response_deserializer=review__detail_dot_review__detail__common__pb2.ApiResponseReviewDetailDeleteAt.FromString,
                _registered_method=True)
        self.DeleteReviewDetailPermanent = channel.unary_unary(
                '/pb.review_detail.ReviewDetailCommandService/DeleteReviewDetailPermanent',
                request_serializer=review__detail_dot_review__detail__common__pb2.FindByIdReviewDetailRequest.SerializeToString,
                response_deserializer=review_dot_review__common__pb2.ApiResponseReviewDelete.FromString,
                _registered_method=True)
        self.RestoreAllReviewDetail = channel.unary_unary(
                '/pb.review_detail.ReviewDetailCommandService/RestoreAllReviewDetail',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=review_dot_review__common__pb2.ApiResponseReviewAll.FromString,
                _registered_method=True)
        self.DeleteAllReviewDetailPermanent = channel.unary_unary(
                '/pb.review_detail.ReviewDetailCommandService/DeleteAllReviewDetailPermanent',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=review_dot_review__common__pb2.ApiResponseReviewAll.FromString,
                _registered_method=True)


class ReviewDetailCommandServiceServicer:
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

    def TrashedReviewDetail(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RestoreReviewDetail(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteReviewDetailPermanent(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RestoreAllReviewDetail(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteAllReviewDetailPermanent(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ReviewDetailCommandServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Create': grpc.unary_unary_rpc_method_handler(
                    servicer.Create,
                    request_deserializer=review__detail_dot_review__detail__command__pb2.CreateReviewDetailRequest.FromString,
                    response_serializer=review__detail_dot_review__detail__common__pb2.ApiResponseReviewDetail.SerializeToString,
            ),
            'Update': grpc.unary_unary_rpc_method_handler(
                    servicer.Update,
                    request_deserializer=review__detail_dot_review__detail__command__pb2.UpdateReviewDetailRequest.FromString,
                    response_serializer=review__detail_dot_review__detail__common__pb2.ApiResponseReviewDetail.SerializeToString,
            ),
            'TrashedReviewDetail': grpc.unary_unary_rpc_method_handler(
                    servicer.TrashedReviewDetail,
                    request_deserializer=review__detail_dot_review__detail__common__pb2.FindByIdReviewDetailRequest.FromString,
                    response_serializer=review__detail_dot_review__detail__common__pb2.ApiResponseReviewDetailDeleteAt.SerializeToString,
            ),
            'RestoreReviewDetail': grpc.unary_unary_rpc_method_handler(
                    servicer.RestoreReviewDetail,
                    request_deserializer=review__detail_dot_review__detail__common__pb2.FindByIdReviewDetailRequest.FromString,
                    response_serializer=review__detail_dot_review__detail__common__pb2.ApiResponseReviewDetailDeleteAt.SerializeToString,
            ),
            'DeleteReviewDetailPermanent': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteReviewDetailPermanent,
                    request_deserializer=review__detail_dot_review__detail__common__pb2.FindByIdReviewDetailRequest.FromString,
                    response_serializer=review_dot_review__common__pb2.ApiResponseReviewDelete.SerializeToString,
            ),
            'RestoreAllReviewDetail': grpc.unary_unary_rpc_method_handler(
                    servicer.RestoreAllReviewDetail,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=review_dot_review__common__pb2.ApiResponseReviewAll.SerializeToString,
            ),
            'DeleteAllReviewDetailPermanent': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteAllReviewDetailPermanent,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=review_dot_review__common__pb2.ApiResponseReviewAll.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'pb.review_detail.ReviewDetailCommandService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('pb.review_detail.ReviewDetailCommandService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class ReviewDetailCommandService:
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
            '/pb.review_detail.ReviewDetailCommandService/Create',
            review__detail_dot_review__detail__command__pb2.CreateReviewDetailRequest.SerializeToString,
            review__detail_dot_review__detail__common__pb2.ApiResponseReviewDetail.FromString,
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
            '/pb.review_detail.ReviewDetailCommandService/Update',
            review__detail_dot_review__detail__command__pb2.UpdateReviewDetailRequest.SerializeToString,
            review__detail_dot_review__detail__common__pb2.ApiResponseReviewDetail.FromString,
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
    def TrashedReviewDetail(request,
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
            '/pb.review_detail.ReviewDetailCommandService/TrashedReviewDetail',
            review__detail_dot_review__detail__common__pb2.FindByIdReviewDetailRequest.SerializeToString,
            review__detail_dot_review__detail__common__pb2.ApiResponseReviewDetailDeleteAt.FromString,
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
    def RestoreReviewDetail(request,
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
            '/pb.review_detail.ReviewDetailCommandService/RestoreReviewDetail',
            review__detail_dot_review__detail__common__pb2.FindByIdReviewDetailRequest.SerializeToString,
            review__detail_dot_review__detail__common__pb2.ApiResponseReviewDetailDeleteAt.FromString,
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
    def DeleteReviewDetailPermanent(request,
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
            '/pb.review_detail.ReviewDetailCommandService/DeleteReviewDetailPermanent',
            review__detail_dot_review__detail__common__pb2.FindByIdReviewDetailRequest.SerializeToString,
            review_dot_review__common__pb2.ApiResponseReviewDelete.FromString,
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
    def RestoreAllReviewDetail(request,
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
            '/pb.review_detail.ReviewDetailCommandService/RestoreAllReviewDetail',
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            review_dot_review__common__pb2.ApiResponseReviewAll.FromString,
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
    def DeleteAllReviewDetailPermanent(request,
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
            '/pb.review_detail.ReviewDetailCommandService/DeleteAllReviewDetailPermanent',
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            review_dot_review__common__pb2.ApiResponseReviewAll.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
