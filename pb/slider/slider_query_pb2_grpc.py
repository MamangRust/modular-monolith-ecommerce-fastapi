# DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from pb.slider import slider_common_pb2 as slider_dot_slider__common__pb2
from pb.slider import slider_query_pb2 as slider_dot_slider__query__pb2

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
        + ' but the generated code in slider/slider_query_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class SliderQueryServiceStub:
    """Missing associated documentation comment in.proto file."""

    def __init__(self, channel):
        """Constructor. Args: channel: A grpc.Channel."""
        self.FindAll = channel.unary_unary(
                '/pb.slider.SliderQueryService/FindAll',
                request_serializer=slider_dot_slider__query__pb2.FindAllSliderRequest.SerializeToString,
                response_deserializer=slider_dot_slider__common__pb2.ApiResponsePaginationSlider.FromString,
                _registered_method=True)
        self.FindById = channel.unary_unary(
                '/pb.slider.SliderQueryService/FindById',
                request_serializer=slider_dot_slider__common__pb2.FindByIdSliderRequest.SerializeToString,
                response_deserializer=slider_dot_slider__common__pb2.ApiResponseSlider.FromString,
                _registered_method=True)
        self.FindByTrashed = channel.unary_unary(
                '/pb.slider.SliderQueryService/FindByTrashed',
                request_serializer=slider_dot_slider__query__pb2.FindAllSliderRequest.SerializeToString,
                response_deserializer=slider_dot_slider__common__pb2.ApiResponsePaginationSliderDeleteAt.FromString,
                _registered_method=True)
        self.FindByActive = channel.unary_unary(
                '/pb.slider.SliderQueryService/FindByActive',
                request_serializer=slider_dot_slider__query__pb2.FindAllSliderRequest.SerializeToString,
                response_deserializer=slider_dot_slider__common__pb2.ApiResponsePaginationSliderDeleteAt.FromString,
                _registered_method=True)


class SliderQueryServiceServicer:
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


def add_SliderQueryServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'FindAll': grpc.unary_unary_rpc_method_handler(
                    servicer.FindAll,
                    request_deserializer=slider_dot_slider__query__pb2.FindAllSliderRequest.FromString,
                    response_serializer=slider_dot_slider__common__pb2.ApiResponsePaginationSlider.SerializeToString,
            ),
            'FindById': grpc.unary_unary_rpc_method_handler(
                    servicer.FindById,
                    request_deserializer=slider_dot_slider__common__pb2.FindByIdSliderRequest.FromString,
                    response_serializer=slider_dot_slider__common__pb2.ApiResponseSlider.SerializeToString,
            ),
            'FindByTrashed': grpc.unary_unary_rpc_method_handler(
                    servicer.FindByTrashed,
                    request_deserializer=slider_dot_slider__query__pb2.FindAllSliderRequest.FromString,
                    response_serializer=slider_dot_slider__common__pb2.ApiResponsePaginationSliderDeleteAt.SerializeToString,
            ),
            'FindByActive': grpc.unary_unary_rpc_method_handler(
                    servicer.FindByActive,
                    request_deserializer=slider_dot_slider__query__pb2.FindAllSliderRequest.FromString,
                    response_serializer=slider_dot_slider__common__pb2.ApiResponsePaginationSliderDeleteAt.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'pb.slider.SliderQueryService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('pb.slider.SliderQueryService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class SliderQueryService:
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
            '/pb.slider.SliderQueryService/FindAll',
            slider_dot_slider__query__pb2.FindAllSliderRequest.SerializeToString,
            slider_dot_slider__common__pb2.ApiResponsePaginationSlider.FromString,
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
            '/pb.slider.SliderQueryService/FindById',
            slider_dot_slider__common__pb2.FindByIdSliderRequest.SerializeToString,
            slider_dot_slider__common__pb2.ApiResponseSlider.FromString,
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
            '/pb.slider.SliderQueryService/FindByTrashed',
            slider_dot_slider__query__pb2.FindAllSliderRequest.SerializeToString,
            slider_dot_slider__common__pb2.ApiResponsePaginationSliderDeleteAt.FromString,
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
            '/pb.slider.SliderQueryService/FindByActive',
            slider_dot_slider__query__pb2.FindAllSliderRequest.SerializeToString,
            slider_dot_slider__common__pb2.ApiResponsePaginationSliderDeleteAt.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
