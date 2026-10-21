# DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from pb.review import review_query_pb2 as review_dot_review__query__pb2
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
        + ' but the generated code in review_detail/review_detail_query_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class ReviewDetailQueryServiceStub:
    """Missing associated documentation comment in.proto file."""

    def __init__(self, channel):
        """Constructor. Args: channel: A grpc.Channel."""
        self.FindAll = channel.unary_unary(
                '/pb.review_detail.ReviewDetailQueryService/FindAll',
                request_serializer=review_dot_review__query__pb2.FindAllReviewRequest.SerializeToString,
                response_deserializer=review__detail_dot_review__detail__common__pb2.ApiResponsePaginationReviewDetails.FromString,
                _registered_method=True)
        self.FindById = channel.unary_unary(
                '/pb.review_detail.ReviewDetailQueryService/FindById',
                request_serializer=review__detail_dot_review__detail__common__pb2.FindByIdReviewDetailRequest.SerializeToString,
                response_deserializer=review__detail_dot_review__detail__common__pb2.ApiResponseReviewDetail.FromString,
                _registered_method=True)
        self.FindByActive = channel.unary_unary(
                '/pb.review_detail.ReviewDetailQueryService/FindByActive',
                request_serializer=review_dot_review__query__pb2.FindAllReviewRequest.SerializeToString,
                response_deserializer=review__detail_dot_review__detail__common__pb2.ApiResponsePaginationReviewDetailsDeleteAt.FromString,
                _registered_method=True)
        self.FindByTrashed = channel.unary_unary(
                '/pb.review_detail.ReviewDetailQueryService/FindByTrashed',
                request_serializer=review_dot_review__query__pb2.FindAllReviewRequest.SerializeToString,
                response_deserializer=review__detail_dot_review__detail__common__pb2.ApiResponsePaginationReviewDetailsDeleteAt.FromString,
                _registered_method=True)


class ReviewDetailQueryServiceServicer:
    """Missing associated documentation comment in.proto file."""

    def FindAll(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def FindById(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def FindByActive(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def FindByTrashed(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ReviewDetailQueryServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'FindAll': grpc.unary_unary_rpc_method_handler(
                    servicer.FindAll,
                    request_deserializer=review_dot_review__query__pb2.FindAllReviewRequest.FromString,
                    response_serializer=review__detail_dot_review__detail__common__pb2.ApiResponsePaginationReviewDetails.SerializeToString,
            ),
            'FindById': grpc.unary_unary_rpc_method_handler(
                    servicer.FindById,
                    request_deserializer=review__detail_dot_review__detail__common__pb2.FindByIdReviewDetailRequest.FromString,
                    response_serializer=review__detail_dot_review__detail__common__pb2.ApiResponseReviewDetail.SerializeToString,
            ),
            'FindByActive': grpc.unary_unary_rpc_method_handler(
                    servicer.FindByActive,
                    request_deserializer=review_dot_review__query__pb2.FindAllReviewRequest.FromString,
                    response_serializer=review__detail_dot_review__detail__common__pb2.ApiResponsePaginationReviewDetailsDeleteAt.SerializeToString,
            ),
            'FindByTrashed': grpc.unary_unary_rpc_method_handler(
                    servicer.FindByTrashed,
                    request_deserializer=review_dot_review__query__pb2.FindAllReviewRequest.FromString,
                    response_serializer=review__detail_dot_review__detail__common__pb2.ApiResponsePaginationReviewDetailsDeleteAt.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'pb.review_detail.ReviewDetailQueryService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('pb.review_detail.ReviewDetailQueryService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class ReviewDetailQueryService:
    """Missing associated documentation comment in.proto file."""

    @staticmethod
    def FindAll(request,
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
            '/pb.review_detail.ReviewDetailQueryService/FindAll',
            review_dot_review__query__pb2.FindAllReviewRequest.SerializeToString,
            review__detail_dot_review__detail__common__pb2.ApiResponsePaginationReviewDetails.FromString,
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
    def FindById(request,
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
            '/pb.review_detail.ReviewDetailQueryService/FindById',
            review__detail_dot_review__detail__common__pb2.FindByIdReviewDetailRequest.SerializeToString,
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
    def FindByActive(request,
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
            '/pb.review_detail.ReviewDetailQueryService/FindByActive',
            review_dot_review__query__pb2.FindAllReviewRequest.SerializeToString,
            review__detail_dot_review__detail__common__pb2.ApiResponsePaginationReviewDetailsDeleteAt.FromString,
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
    def FindByTrashed(request,
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
            '/pb.review_detail.ReviewDetailQueryService/FindByTrashed',
            review_dot_review__query__pb2.FindAllReviewRequest.SerializeToString,
            review__detail_dot_review__detail__common__pb2.ApiResponsePaginationReviewDetailsDeleteAt.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
