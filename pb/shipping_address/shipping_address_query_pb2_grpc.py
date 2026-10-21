# DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from pb.shipping_address import shipping_address_common_pb2 as shipping__address_dot_shipping__address__common__pb2
from pb.shipping_address import shipping_address_query_pb2 as shipping__address_dot_shipping__address__query__pb2

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
        + ' but the generated code in shipping_address/shipping_address_query_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class ShippingQueryServiceStub:
    """Missing associated documentation comment in.proto file."""

    def __init__(self, channel):
        """Constructor. Args: channel: A grpc.Channel."""
        self.FindAll = channel.unary_unary(
                '/pb.shipping_address.ShippingQueryService/FindAll',
                request_serializer=shipping__address_dot_shipping__address__query__pb2.FindAllShippingRequest.SerializeToString,
                response_deserializer=shipping__address_dot_shipping__address__common__pb2.ApiResponsePaginationShipping.FromString,
                _registered_method=True)
        self.FindById = channel.unary_unary(
                '/pb.shipping_address.ShippingQueryService/FindById',
                request_serializer=shipping__address_dot_shipping__address__common__pb2.FindByIdShippingRequest.SerializeToString,
                response_deserializer=shipping__address_dot_shipping__address__common__pb2.ApiResponseShipping.FromString,
                _registered_method=True)
        self.FindByOrder = channel.unary_unary(
                '/pb.shipping_address.ShippingQueryService/FindByOrder',
                request_serializer=shipping__address_dot_shipping__address__common__pb2.FindByIdShippingRequest.SerializeToString,
                response_deserializer=shipping__address_dot_shipping__address__common__pb2.ApiResponseShipping.FromString,
                _registered_method=True)
        self.FindByActive = channel.unary_unary(
                '/pb.shipping_address.ShippingQueryService/FindByActive',
                request_serializer=shipping__address_dot_shipping__address__query__pb2.FindAllShippingRequest.SerializeToString,
                response_deserializer=shipping__address_dot_shipping__address__common__pb2.ApiResponsePaginationShippingDeleteAt.FromString,
                _registered_method=True)
        self.FindByTrashed = channel.unary_unary(
                '/pb.shipping_address.ShippingQueryService/FindByTrashed',
                request_serializer=shipping__address_dot_shipping__address__query__pb2.FindAllShippingRequest.SerializeToString,
                response_deserializer=shipping__address_dot_shipping__address__common__pb2.ApiResponsePaginationShippingDeleteAt.FromString,
                _registered_method=True)


class ShippingQueryServiceServicer:
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

    def FindByOrder(self, request, context):
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


def add_ShippingQueryServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'FindAll': grpc.unary_unary_rpc_method_handler(
                    servicer.FindAll,
                    request_deserializer=shipping__address_dot_shipping__address__query__pb2.FindAllShippingRequest.FromString,
                    response_serializer=shipping__address_dot_shipping__address__common__pb2.ApiResponsePaginationShipping.SerializeToString,
            ),
            'FindById': grpc.unary_unary_rpc_method_handler(
                    servicer.FindById,
                    request_deserializer=shipping__address_dot_shipping__address__common__pb2.FindByIdShippingRequest.FromString,
                    response_serializer=shipping__address_dot_shipping__address__common__pb2.ApiResponseShipping.SerializeToString,
            ),
            'FindByOrder': grpc.unary_unary_rpc_method_handler(
                    servicer.FindByOrder,
                    request_deserializer=shipping__address_dot_shipping__address__common__pb2.FindByIdShippingRequest.FromString,
                    response_serializer=shipping__address_dot_shipping__address__common__pb2.ApiResponseShipping.SerializeToString,
            ),
            'FindByActive': grpc.unary_unary_rpc_method_handler(
                    servicer.FindByActive,
                    request_deserializer=shipping__address_dot_shipping__address__query__pb2.FindAllShippingRequest.FromString,
                    response_serializer=shipping__address_dot_shipping__address__common__pb2.ApiResponsePaginationShippingDeleteAt.SerializeToString,
            ),
            'FindByTrashed': grpc.unary_unary_rpc_method_handler(
                    servicer.FindByTrashed,
                    request_deserializer=shipping__address_dot_shipping__address__query__pb2.FindAllShippingRequest.FromString,
                    response_serializer=shipping__address_dot_shipping__address__common__pb2.ApiResponsePaginationShippingDeleteAt.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'pb.shipping_address.ShippingQueryService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('pb.shipping_address.ShippingQueryService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class ShippingQueryService:
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
            '/pb.shipping_address.ShippingQueryService/FindAll',
            shipping__address_dot_shipping__address__query__pb2.FindAllShippingRequest.SerializeToString,
            shipping__address_dot_shipping__address__common__pb2.ApiResponsePaginationShipping.FromString,
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
            '/pb.shipping_address.ShippingQueryService/FindById',
            shipping__address_dot_shipping__address__common__pb2.FindByIdShippingRequest.SerializeToString,
            shipping__address_dot_shipping__address__common__pb2.ApiResponseShipping.FromString,
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
    def FindByOrder(request,
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
            '/pb.shipping_address.ShippingQueryService/FindByOrder',
            shipping__address_dot_shipping__address__common__pb2.FindByIdShippingRequest.SerializeToString,
            shipping__address_dot_shipping__address__common__pb2.ApiResponseShipping.FromString,
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
            '/pb.shipping_address.ShippingQueryService/FindByActive',
            shipping__address_dot_shipping__address__query__pb2.FindAllShippingRequest.SerializeToString,
            shipping__address_dot_shipping__address__common__pb2.ApiResponsePaginationShippingDeleteAt.FromString,
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
            '/pb.shipping_address.ShippingQueryService/FindByTrashed',
            shipping__address_dot_shipping__address__query__pb2.FindAllShippingRequest.SerializeToString,
            shipping__address_dot_shipping__address__common__pb2.ApiResponsePaginationShippingDeleteAt.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
