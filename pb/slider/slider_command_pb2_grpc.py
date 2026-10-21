# DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from pb.slider import slider_command_pb2 as slider_dot_slider__command__pb2
from pb.slider import slider_common_pb2 as slider_dot_slider__common__pb2

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
        + ' but the generated code in slider/slider_command_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class SliderCommandServiceStub:
    """Missing associated documentation comment in.proto file."""

    def __init__(self, channel):
        """Constructor. Args: channel: A grpc.Channel."""
        self.Create = channel.unary_unary(
                '/pb.slider.SliderCommandService/Create',
                request_serializer=slider_dot_slider__command__pb2.CreateSliderRequest.SerializeToString,
                response_deserializer=slider_dot_slider__common__pb2.ApiResponseSlider.FromString,
                _registered_method=True)
        self.Update = channel.unary_unary(
                '/pb.slider.SliderCommandService/Update',
                request_serializer=slider_dot_slider__command__pb2.UpdateSliderRequest.SerializeToString,
                response_deserializer=slider_dot_slider__common__pb2.ApiResponseSlider.FromString,
                _registered_method=True)
        self.TrashedSlider = channel.unary_unary(
                '/pb.slider.SliderCommandService/TrashedSlider',
                request_serializer=slider_dot_slider__common__pb2.FindByIdSliderRequest.SerializeToString,
                response_deserializer=slider_dot_slider__common__pb2.ApiResponseSliderDeleteAt.FromString,
                _registered_method=True)
        self.RestoreSlider = channel.unary_unary(
                '/pb.slider.SliderCommandService/RestoreSlider',
                request_serializer=slider_dot_slider__common__pb2.FindByIdSliderRequest.SerializeToString,
                response_deserializer=slider_dot_slider__common__pb2.ApiResponseSliderDeleteAt.FromString,
                _registered_method=True)
        self.DeleteSliderPermanent = channel.unary_unary(
                '/pb.slider.SliderCommandService/DeleteSliderPermanent',
                request_serializer=slider_dot_slider__common__pb2.FindByIdSliderRequest.SerializeToString,
                response_deserializer=slider_dot_slider__common__pb2.ApiResponseSliderDelete.FromString,
                _registered_method=True)
        self.RestoreAllSlider = channel.unary_unary(
                '/pb.slider.SliderCommandService/RestoreAllSlider',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=slider_dot_slider__common__pb2.ApiResponseSliderAll.FromString,
                _registered_method=True)
        self.DeleteAllSliderPermanent = channel.unary_unary(
                '/pb.slider.SliderCommandService/DeleteAllSliderPermanent',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=slider_dot_slider__common__pb2.ApiResponseSliderAll.FromString,
                _registered_method=True)


class SliderCommandServiceServicer:
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

    def TrashedSlider(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RestoreSlider(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteSliderPermanent(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RestoreAllSlider(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteAllSliderPermanent(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_SliderCommandServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Create': grpc.unary_unary_rpc_method_handler(
                    servicer.Create,
                    request_deserializer=slider_dot_slider__command__pb2.CreateSliderRequest.FromString,
                    response_serializer=slider_dot_slider__common__pb2.ApiResponseSlider.SerializeToString,
            ),
            'Update': grpc.unary_unary_rpc_method_handler(
                    servicer.Update,
                    request_deserializer=slider_dot_slider__command__pb2.UpdateSliderRequest.FromString,
                    response_serializer=slider_dot_slider__common__pb2.ApiResponseSlider.SerializeToString,
            ),
            'TrashedSlider': grpc.unary_unary_rpc_method_handler(
                    servicer.TrashedSlider,
                    request_deserializer=slider_dot_slider__common__pb2.FindByIdSliderRequest.FromString,
                    response_serializer=slider_dot_slider__common__pb2.ApiResponseSliderDeleteAt.SerializeToString,
            ),
            'RestoreSlider': grpc.unary_unary_rpc_method_handler(
                    servicer.RestoreSlider,
                    request_deserializer=slider_dot_slider__common__pb2.FindByIdSliderRequest.FromString,
                    response_serializer=slider_dot_slider__common__pb2.ApiResponseSliderDeleteAt.SerializeToString,
            ),
            'DeleteSliderPermanent': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteSliderPermanent,
                    request_deserializer=slider_dot_slider__common__pb2.FindByIdSliderRequest.FromString,
                    response_serializer=slider_dot_slider__common__pb2.ApiResponseSliderDelete.SerializeToString,
            ),
            'RestoreAllSlider': grpc.unary_unary_rpc_method_handler(
                    servicer.RestoreAllSlider,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=slider_dot_slider__common__pb2.ApiResponseSliderAll.SerializeToString,
            ),
            'DeleteAllSliderPermanent': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteAllSliderPermanent,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=slider_dot_slider__common__pb2.ApiResponseSliderAll.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'pb.slider.SliderCommandService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('pb.slider.SliderCommandService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class SliderCommandService:
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
            '/pb.slider.SliderCommandService/Create',
            slider_dot_slider__command__pb2.CreateSliderRequest.SerializeToString,
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
            '/pb.slider.SliderCommandService/Update',
            slider_dot_slider__command__pb2.UpdateSliderRequest.SerializeToString,
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
    def TrashedSlider(request,
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
            '/pb.slider.SliderCommandService/TrashedSlider',
            slider_dot_slider__common__pb2.FindByIdSliderRequest.SerializeToString,
            slider_dot_slider__common__pb2.ApiResponseSliderDeleteAt.FromString,
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
    def RestoreSlider(request,
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
            '/pb.slider.SliderCommandService/RestoreSlider',
            slider_dot_slider__common__pb2.FindByIdSliderRequest.SerializeToString,
            slider_dot_slider__common__pb2.ApiResponseSliderDeleteAt.FromString,
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
    def DeleteSliderPermanent(request,
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
            '/pb.slider.SliderCommandService/DeleteSliderPermanent',
            slider_dot_slider__common__pb2.FindByIdSliderRequest.SerializeToString,
            slider_dot_slider__common__pb2.ApiResponseSliderDelete.FromString,
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
    def RestoreAllSlider(request,
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
            '/pb.slider.SliderCommandService/RestoreAllSlider',
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            slider_dot_slider__common__pb2.ApiResponseSliderAll.FromString,
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
    def DeleteAllSliderPermanent(request,
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
            '/pb.slider.SliderCommandService/DeleteAllSliderPermanent',
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            slider_dot_slider__common__pb2.ApiResponseSliderAll.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
