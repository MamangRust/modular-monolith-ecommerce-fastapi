# DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from pb.review import review_common_pb2 as review_dot_review__common__pb2
from pb.review import review_query_pb2 as review_dot_review__query__pb2

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
        + ' but the generated code in review/review_query_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class ReviewQueryServiceStub:
    """Missing associated documentation comment in.proto file."""

    def __init__(self, channel):
        """Constructor. Args: channel: A grpc.Channel."""
        self.FindAll = channel.unary_unary(
                '/pb.review.ReviewQueryService/FindAll',
                request_serializer=review_dot_review__query__pb2.FindAllReviewRequest.SerializeToString,
                response_deserializer=review_dot_review__common__pb2.ApiResponsePaginationReview.FromString,
                _registered_method=True)
        self.FindByProduct = channel.unary_unary(
                '/pb.review.ReviewQueryService/FindByProduct',
                request_serializer=review_dot_review__query__pb2.FindAllReviewProductRequest.SerializeToString,
                response_deserializer=review_dot_review__common__pb2.ApiResponsePaginationReviewDetail.FromString,
                _registered_method=True)
        self.FindByMerchant = channel.unary_unary(
                '/pb.review.ReviewQueryService/FindByMerchant',
                request_serializer=review_dot_review__query__pb2.FindAllReviewMerchantRequest.SerializeToString,
                response_deserializer=review_dot_review__common__pb2.ApiResponsePaginationReviewDetail.FromString,
                _registered_method=True)
        self.FindByTrashed = channel.unary_unary(
                '/pb.review.ReviewQueryService/FindByTrashed',
                request_serializer=review_dot_review__query__pb2.FindAllReviewRequest.SerializeToString,
                response_deserializer=review_dot_review__common__pb2.ApiResponsePaginationReviewDeleteAt.FromString,
                _registered_method=True)
        self.FindByActive = channel.unary_unary(
                '/pb.review.ReviewQueryService/FindByActive',
                request_serializer=review_dot_review__query__pb2.FindAllReviewRequest.SerializeToString,
                response_deserializer=review_dot_review__common__pb2.ApiResponsePaginationReviewDeleteAt.FromString,
                _registered_method=True)


class ReviewQueryServiceServicer:
    """Missing associated documentation comment in.proto file."""

    def FindAll(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def FindByProduct(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def FindByMerchant(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def FindByTrashed(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def FindByActive(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ReviewQueryServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'FindAll': grpc.unary_unary_rpc_method_handler(
                    servicer.FindAll,
                    request_deserializer=review_dot_review__query__pb2.FindAllReviewRequest.FromString,
                    response_serializer=review_dot_review__common__pb2.ApiResponsePaginationReview.SerializeToString,
            ),
            'FindByProduct': grpc.unary_unary_rpc_method_handler(
                    servicer.FindByProduct,
                    request_deserializer=review_dot_review__query__pb2.FindAllReviewProductRequest.FromString,
                    response_serializer=review_dot_review__common__pb2.ApiResponsePaginationReviewDetail.SerializeToString,
            ),
            'FindByMerchant': grpc.unary_unary_rpc_method_handler(
                    servicer.FindByMerchant,
                    request_deserializer=review_dot_review__query__pb2.FindAllReviewMerchantRequest.FromString,
                    response_serializer=review_dot_review__common__pb2.ApiResponsePaginationReviewDetail.SerializeToString,
            ),
            'FindByTrashed': grpc.unary_unary_rpc_method_handler(
                    servicer.FindByTrashed,
                    request_deserializer=review_dot_review__query__pb2.FindAllReviewRequest.FromString,
                    response_serializer=review_dot_review__common__pb2.ApiResponsePaginationReviewDeleteAt.SerializeToString,
            ),
            'FindByActive': grpc.unary_unary_rpc_method_handler(
                    servicer.FindByActive,
                    request_deserializer=review_dot_review__query__pb2.FindAllReviewRequest.FromString,
                    response_serializer=review_dot_review__common__pb2.ApiResponsePaginationReviewDeleteAt.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'pb.review.ReviewQueryService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('pb.review.ReviewQueryService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class ReviewQueryService:
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
            '/pb.review.ReviewQueryService/FindAll',
            review_dot_review__query__pb2.FindAllReviewRequest.SerializeToString,
            review_dot_review__common__pb2.ApiResponsePaginationReview.FromString,
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
    def FindByProduct(request,
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
            '/pb.review.ReviewQueryService/FindByProduct',
            review_dot_review__query__pb2.FindAllReviewProductRequest.SerializeToString,
            review_dot_review__common__pb2.ApiResponsePaginationReviewDetail.FromString,
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
    def FindByMerchant(request,
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
            '/pb.review.ReviewQueryService/FindByMerchant',
            review_dot_review__query__pb2.FindAllReviewMerchantRequest.SerializeToString,
            review_dot_review__common__pb2.ApiResponsePaginationReviewDetail.FromString,
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
            '/pb.review.ReviewQueryService/FindByTrashed',
            review_dot_review__query__pb2.FindAllReviewRequest.SerializeToString,
            review_dot_review__common__pb2.ApiResponsePaginationReviewDeleteAt.FromString,
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
            '/pb.review.ReviewQueryService/FindByActive',
            review_dot_review__query__pb2.FindAllReviewRequest.SerializeToString,
            review_dot_review__common__pb2.ApiResponsePaginationReviewDeleteAt.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
