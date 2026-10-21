# DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from pb.review import review_command_pb2 as review_dot_review__command__pb2
from pb.review import review_common_pb2 as review_dot_review__common__pb2

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
        + ' but the generated code in review/review_command_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class ReviewCommandServiceStub:
    """Missing associated documentation comment in.proto file."""

    def __init__(self, channel):
        """Constructor. Args: channel: A grpc.Channel."""
        self.Create = channel.unary_unary(
                '/pb.review.ReviewCommandService/Create',
                request_serializer=review_dot_review__command__pb2.CreateReviewRequest.SerializeToString,
                response_deserializer=review_dot_review__common__pb2.ApiResponseReview.FromString,
                _registered_method=True)
        self.Update = channel.unary_unary(
                '/pb.review.ReviewCommandService/Update',
                request_serializer=review_dot_review__command__pb2.UpdateReviewRequest.SerializeToString,
                response_deserializer=review_dot_review__common__pb2.ApiResponseReview.FromString,
                _registered_method=True)
        self.TrashedReview = channel.unary_unary(
                '/pb.review.ReviewCommandService/TrashedReview',
                request_serializer=review_dot_review__common__pb2.FindByIdReviewRequest.SerializeToString,
                response_deserializer=review_dot_review__common__pb2.ApiResponseReviewDeleteAt.FromString,
                _registered_method=True)
        self.RestoreReview = channel.unary_unary(
                '/pb.review.ReviewCommandService/RestoreReview',
                request_serializer=review_dot_review__common__pb2.FindByIdReviewRequest.SerializeToString,
                response_deserializer=review_dot_review__common__pb2.ApiResponseReviewDeleteAt.FromString,
                _registered_method=True)
        self.DeleteReviewPermanent = channel.unary_unary(
                '/pb.review.ReviewCommandService/DeleteReviewPermanent',
                request_serializer=review_dot_review__common__pb2.FindByIdReviewRequest.SerializeToString,
                response_deserializer=review_dot_review__common__pb2.ApiResponseReviewDelete.FromString,
                _registered_method=True)
        self.RestoreAllReview = channel.unary_unary(
                '/pb.review.ReviewCommandService/RestoreAllReview',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=review_dot_review__common__pb2.ApiResponseReviewAll.FromString,
                _registered_method=True)
        self.DeleteAllReviewPermanent = channel.unary_unary(
                '/pb.review.ReviewCommandService/DeleteAllReviewPermanent',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=review_dot_review__common__pb2.ApiResponseReviewAll.FromString,
                _registered_method=True)


class ReviewCommandServiceServicer:
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

    def TrashedReview(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RestoreReview(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteReviewPermanent(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RestoreAllReview(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteAllReviewPermanent(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ReviewCommandServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Create': grpc.unary_unary_rpc_method_handler(
                    servicer.Create,
                    request_deserializer=review_dot_review__command__pb2.CreateReviewRequest.FromString,
                    response_serializer=review_dot_review__common__pb2.ApiResponseReview.SerializeToString,
            ),
            'Update': grpc.unary_unary_rpc_method_handler(
                    servicer.Update,
                    request_deserializer=review_dot_review__command__pb2.UpdateReviewRequest.FromString,
                    response_serializer=review_dot_review__common__pb2.ApiResponseReview.SerializeToString,
            ),
            'TrashedReview': grpc.unary_unary_rpc_method_handler(
                    servicer.TrashedReview,
                    request_deserializer=review_dot_review__common__pb2.FindByIdReviewRequest.FromString,
                    response_serializer=review_dot_review__common__pb2.ApiResponseReviewDeleteAt.SerializeToString,
            ),
            'RestoreReview': grpc.unary_unary_rpc_method_handler(
                    servicer.RestoreReview,
                    request_deserializer=review_dot_review__common__pb2.FindByIdReviewRequest.FromString,
                    response_serializer=review_dot_review__common__pb2.ApiResponseReviewDeleteAt.SerializeToString,
            ),
            'DeleteReviewPermanent': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteReviewPermanent,
                    request_deserializer=review_dot_review__common__pb2.FindByIdReviewRequest.FromString,
                    response_serializer=review_dot_review__common__pb2.ApiResponseReviewDelete.SerializeToString,
            ),
            'RestoreAllReview': grpc.unary_unary_rpc_method_handler(
                    servicer.RestoreAllReview,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=review_dot_review__common__pb2.ApiResponseReviewAll.SerializeToString,
            ),
            'DeleteAllReviewPermanent': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteAllReviewPermanent,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=review_dot_review__common__pb2.ApiResponseReviewAll.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'pb.review.ReviewCommandService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('pb.review.ReviewCommandService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class ReviewCommandService:
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
            '/pb.review.ReviewCommandService/Create',
            review_dot_review__command__pb2.CreateReviewRequest.SerializeToString,
            review_dot_review__common__pb2.ApiResponseReview.FromString,
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
            '/pb.review.ReviewCommandService/Update',
            review_dot_review__command__pb2.UpdateReviewRequest.SerializeToString,
            review_dot_review__common__pb2.ApiResponseReview.FromString,
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
    def TrashedReview(request,
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
            '/pb.review.ReviewCommandService/TrashedReview',
            review_dot_review__common__pb2.FindByIdReviewRequest.SerializeToString,
            review_dot_review__common__pb2.ApiResponseReviewDeleteAt.FromString,
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
    def RestoreReview(request,
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
            '/pb.review.ReviewCommandService/RestoreReview',
            review_dot_review__common__pb2.FindByIdReviewRequest.SerializeToString,
            review_dot_review__common__pb2.ApiResponseReviewDeleteAt.FromString,
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
    def DeleteReviewPermanent(request,
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
            '/pb.review.ReviewCommandService/DeleteReviewPermanent',
            review_dot_review__common__pb2.FindByIdReviewRequest.SerializeToString,
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
    def RestoreAllReview(request,
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
            '/pb.review.ReviewCommandService/RestoreAllReview',
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
    def DeleteAllReviewPermanent(request,
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
            '/pb.review.ReviewCommandService/DeleteAllReviewPermanent',
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
