# DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from pb.cart import cart_command_pb2 as cart_dot_cart__command__pb2
from pb.cart import cart_common_pb2 as cart_dot_cart__common__pb2

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
        + ' but the generated code in cart/cart_command_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class CartCommandServiceStub:
    """Missing associated documentation comment in.proto file."""

    def __init__(self, channel):
        """Constructor. Args: channel: A grpc.Channel."""
        self.Create = channel.unary_unary(
                '/pb.cart.CartCommandService/Create',
                request_serializer=cart_dot_cart__command__pb2.CreateCartRequest.SerializeToString,
                response_deserializer=cart_dot_cart__common__pb2.ApiResponseCart.FromString,
                _registered_method=True)
        self.Delete = channel.unary_unary(
                '/pb.cart.CartCommandService/Delete',
                request_serializer=cart_dot_cart__command__pb2.DeleteCartRequest.SerializeToString,
                response_deserializer=cart_dot_cart__common__pb2.ApiResponseCartDelete.FromString,
                _registered_method=True)
        self.DeleteAll = channel.unary_unary(
                '/pb.cart.CartCommandService/DeleteAll',
                request_serializer=cart_dot_cart__command__pb2.DeleteAllCartRequest.SerializeToString,
                response_deserializer=cart_dot_cart__common__pb2.ApiResponseCartAll.FromString,
                _registered_method=True)


class CartCommandServiceServicer:
    """Missing associated documentation comment in.proto file."""

    def Create(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Delete(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteAll(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_CartCommandServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Create': grpc.unary_unary_rpc_method_handler(
                    servicer.Create,
                    request_deserializer=cart_dot_cart__command__pb2.CreateCartRequest.FromString,
                    response_serializer=cart_dot_cart__common__pb2.ApiResponseCart.SerializeToString,
            ),
            'Delete': grpc.unary_unary_rpc_method_handler(
                    servicer.Delete,
                    request_deserializer=cart_dot_cart__command__pb2.DeleteCartRequest.FromString,
                    response_serializer=cart_dot_cart__common__pb2.ApiResponseCartDelete.SerializeToString,
            ),
            'DeleteAll': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteAll,
                    request_deserializer=cart_dot_cart__command__pb2.DeleteAllCartRequest.FromString,
                    response_serializer=cart_dot_cart__common__pb2.ApiResponseCartAll.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'pb.cart.CartCommandService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('pb.cart.CartCommandService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class CartCommandService:
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
            '/pb.cart.CartCommandService/Create',
            cart_dot_cart__command__pb2.CreateCartRequest.SerializeToString,
            cart_dot_cart__common__pb2.ApiResponseCart.FromString,
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
    def Delete(request,
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
            '/pb.cart.CartCommandService/Delete',
            cart_dot_cart__command__pb2.DeleteCartRequest.SerializeToString,
            cart_dot_cart__common__pb2.ApiResponseCartDelete.FromString,
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
    def DeleteAll(request,
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
            '/pb.cart.CartCommandService/DeleteAll',
            cart_dot_cart__command__pb2.DeleteAllCartRequest.SerializeToString,
            cart_dot_cart__common__pb2.ApiResponseCartAll.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
