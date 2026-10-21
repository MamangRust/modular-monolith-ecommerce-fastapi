# DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from pb.shipping_address import shipping_address_command_pb2 as shipping__address_dot_shipping__address__command__pb2
from pb.shipping_address import shipping_address_common_pb2 as shipping__address_dot_shipping__address__common__pb2

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
        + ' but the generated code in shipping_address/shipping_address_command_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class ShippingCommandServiceStub:
    """Missing associated documentation comment in.proto file."""

    def __init__(self, channel):
        """Constructor. Args: channel: A grpc.Channel."""
        self.CreateShipping = channel.unary_unary(
                '/pb.shipping_address.ShippingCommandService/CreateShipping',
                request_serializer=shipping__address_dot_shipping__address__command__pb2.CreateShippingAddressRequest.SerializeToString,
                response_deserializer=shipping__address_dot_shipping__address__common__pb2.ApiResponseShipping.FromString,
                _registered_method=True)
        self.UpdateShipping = channel.unary_unary(
                '/pb.shipping_address.ShippingCommandService/UpdateShipping',
                request_serializer=shipping__address_dot_shipping__address__command__pb2.UpdateShippingAddressRequest.SerializeToString,
                response_deserializer=shipping__address_dot_shipping__address__common__pb2.ApiResponseShipping.FromString,
                _registered_method=True)
        self.TrashedShipping = channel.unary_unary(
                '/pb.shipping_address.ShippingCommandService/TrashedShipping',
                request_serializer=shipping__address_dot_shipping__address__common__pb2.FindByIdShippingRequest.SerializeToString,
                response_deserializer=shipping__address_dot_shipping__address__common__pb2.ApiResponseShippingDeleteAt.FromString,
                _registered_method=True)
        self.RestoreShipping = channel.unary_unary(
                '/pb.shipping_address.ShippingCommandService/RestoreShipping',
                request_serializer=shipping__address_dot_shipping__address__common__pb2.FindByIdShippingRequest.SerializeToString,
                response_deserializer=shipping__address_dot_shipping__address__common__pb2.ApiResponseShippingDeleteAt.FromString,
                _registered_method=True)
        self.DeleteShippingPermanent = channel.unary_unary(
                '/pb.shipping_address.ShippingCommandService/DeleteShippingPermanent',
                request_serializer=shipping__address_dot_shipping__address__common__pb2.FindByIdShippingRequest.SerializeToString,
                response_deserializer=shipping__address_dot_shipping__address__common__pb2.ApiResponseShippingDelete.FromString,
                _registered_method=True)
        self.RestoreAllShipping = channel.unary_unary(
                '/pb.shipping_address.ShippingCommandService/RestoreAllShipping',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=shipping__address_dot_shipping__address__common__pb2.ApiResponseShippingAll.FromString,
                _registered_method=True)
        self.DeleteShippingByOrderPermanent = channel.unary_unary(
                '/pb.shipping_address.ShippingCommandService/DeleteShippingByOrderPermanent',
                request_serializer=shipping__address_dot_shipping__address__common__pb2.FindByIdShippingRequest.SerializeToString,
                response_deserializer=shipping__address_dot_shipping__address__common__pb2.ApiResponseShippingDelete.FromString,
                _registered_method=True)
        self.DeleteAllShippingPermanent = channel.unary_unary(
                '/pb.shipping_address.ShippingCommandService/DeleteAllShippingPermanent',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=shipping__address_dot_shipping__address__common__pb2.ApiResponseShippingAll.FromString,
                _registered_method=True)


class ShippingCommandServiceServicer:
    """Missing associated documentation comment in.proto file."""

    def CreateShipping(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UpdateShipping(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def TrashedShipping(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RestoreShipping(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteShippingPermanent(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RestoreAllShipping(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteShippingByOrderPermanent(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteAllShippingPermanent(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ShippingCommandServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'CreateShipping': grpc.unary_unary_rpc_method_handler(
                    servicer.CreateShipping,
                    request_deserializer=shipping__address_dot_shipping__address__command__pb2.CreateShippingAddressRequest.FromString,
                    response_serializer=shipping__address_dot_shipping__address__common__pb2.ApiResponseShipping.SerializeToString,
            ),
            'UpdateShipping': grpc.unary_unary_rpc_method_handler(
                    servicer.UpdateShipping,
                    request_deserializer=shipping__address_dot_shipping__address__command__pb2.UpdateShippingAddressRequest.FromString,
                    response_serializer=shipping__address_dot_shipping__address__common__pb2.ApiResponseShipping.SerializeToString,
            ),
            'TrashedShipping': grpc.unary_unary_rpc_method_handler(
                    servicer.TrashedShipping,
                    request_deserializer=shipping__address_dot_shipping__address__common__pb2.FindByIdShippingRequest.FromString,
                    response_serializer=shipping__address_dot_shipping__address__common__pb2.ApiResponseShippingDeleteAt.SerializeToString,
            ),
            'RestoreShipping': grpc.unary_unary_rpc_method_handler(
                    servicer.RestoreShipping,
                    request_deserializer=shipping__address_dot_shipping__address__common__pb2.FindByIdShippingRequest.FromString,
                    response_serializer=shipping__address_dot_shipping__address__common__pb2.ApiResponseShippingDeleteAt.SerializeToString,
            ),
            'DeleteShippingPermanent': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteShippingPermanent,
                    request_deserializer=shipping__address_dot_shipping__address__common__pb2.FindByIdShippingRequest.FromString,
                    response_serializer=shipping__address_dot_shipping__address__common__pb2.ApiResponseShippingDelete.SerializeToString,
            ),
            'RestoreAllShipping': grpc.unary_unary_rpc_method_handler(
                    servicer.RestoreAllShipping,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=shipping__address_dot_shipping__address__common__pb2.ApiResponseShippingAll.SerializeToString,
            ),
            'DeleteShippingByOrderPermanent': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteShippingByOrderPermanent,
                    request_deserializer=shipping__address_dot_shipping__address__common__pb2.FindByIdShippingRequest.FromString,
                    response_serializer=shipping__address_dot_shipping__address__common__pb2.ApiResponseShippingDelete.SerializeToString,
            ),
            'DeleteAllShippingPermanent': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteAllShippingPermanent,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=shipping__address_dot_shipping__address__common__pb2.ApiResponseShippingAll.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'pb.shipping_address.ShippingCommandService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('pb.shipping_address.ShippingCommandService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class ShippingCommandService:
    """Missing associated documentation comment in.proto file."""

    @staticmethod
    def CreateShipping(request,
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
            '/pb.shipping_address.ShippingCommandService/CreateShipping',
            shipping__address_dot_shipping__address__command__pb2.CreateShippingAddressRequest.SerializeToString,
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
    def UpdateShipping(request,
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
            '/pb.shipping_address.ShippingCommandService/UpdateShipping',
            shipping__address_dot_shipping__address__command__pb2.UpdateShippingAddressRequest.SerializeToString,
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
    def TrashedShipping(request,
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
            '/pb.shipping_address.ShippingCommandService/TrashedShipping',
            shipping__address_dot_shipping__address__common__pb2.FindByIdShippingRequest.SerializeToString,
            shipping__address_dot_shipping__address__common__pb2.ApiResponseShippingDeleteAt.FromString,
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
    def RestoreShipping(request,
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
            '/pb.shipping_address.ShippingCommandService/RestoreShipping',
            shipping__address_dot_shipping__address__common__pb2.FindByIdShippingRequest.SerializeToString,
            shipping__address_dot_shipping__address__common__pb2.ApiResponseShippingDeleteAt.FromString,
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
    def DeleteShippingPermanent(request,
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
            '/pb.shipping_address.ShippingCommandService/DeleteShippingPermanent',
            shipping__address_dot_shipping__address__common__pb2.FindByIdShippingRequest.SerializeToString,
            shipping__address_dot_shipping__address__common__pb2.ApiResponseShippingDelete.FromString,
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
    def RestoreAllShipping(request,
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
            '/pb.shipping_address.ShippingCommandService/RestoreAllShipping',
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            shipping__address_dot_shipping__address__common__pb2.ApiResponseShippingAll.FromString,
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
    def DeleteShippingByOrderPermanent(request,
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
            '/pb.shipping_address.ShippingCommandService/DeleteShippingByOrderPermanent',
            shipping__address_dot_shipping__address__common__pb2.FindByIdShippingRequest.SerializeToString,
            shipping__address_dot_shipping__address__common__pb2.ApiResponseShippingDelete.FromString,
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
    def DeleteAllShippingPermanent(request,
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
            '/pb.shipping_address.ShippingCommandService/DeleteAllShippingPermanent',
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            shipping__address_dot_shipping__address__common__pb2.ApiResponseShippingAll.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
