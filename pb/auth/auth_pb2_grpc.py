# DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from pb.auth import auth_pb2 as auth_dot_auth__pb2

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
        + ' but the generated code in auth/auth_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class AuthServiceStub:
    """Missing associated documentation comment in.proto file."""

    def __init__(self, channel):
        """Constructor. Args: channel: A grpc.Channel."""
        self.VerifyCode = channel.unary_unary(
                '/pb.AuthService/VerifyCode',
                request_serializer=auth_dot_auth__pb2.VerifyCodeRequest.SerializeToString,
                response_deserializer=auth_dot_auth__pb2.ApiResponseVerifyCode.FromString,
                _registered_method=True)
        self.ForgotPassword = channel.unary_unary(
                '/pb.AuthService/ForgotPassword',
                request_serializer=auth_dot_auth__pb2.ForgotPasswordRequest.SerializeToString,
                response_deserializer=auth_dot_auth__pb2.ApiResponseForgotPassword.FromString,
                _registered_method=True)
        self.ResetPassword = channel.unary_unary(
                '/pb.AuthService/ResetPassword',
                request_serializer=auth_dot_auth__pb2.ResetPasswordRequest.SerializeToString,
                response_deserializer=auth_dot_auth__pb2.ApiResponseResetPassword.FromString,
                _registered_method=True)
        self.RegisterUser = channel.unary_unary(
                '/pb.AuthService/RegisterUser',
                request_serializer=auth_dot_auth__pb2.RegisterRequest.SerializeToString,
                response_deserializer=auth_dot_auth__pb2.ApiResponseRegister.FromString,
                _registered_method=True)
        self.LoginUser = channel.unary_unary(
                '/pb.AuthService/LoginUser',
                request_serializer=auth_dot_auth__pb2.LoginRequest.SerializeToString,
                response_deserializer=auth_dot_auth__pb2.ApiResponseLogin.FromString,
                _registered_method=True)
        self.RefreshToken = channel.unary_unary(
                '/pb.AuthService/RefreshToken',
                request_serializer=auth_dot_auth__pb2.RefreshTokenRequest.SerializeToString,
                response_deserializer=auth_dot_auth__pb2.ApiResponseRefreshToken.FromString,
                _registered_method=True)
        self.GetMe = channel.unary_unary(
                '/pb.AuthService/GetMe',
                request_serializer=auth_dot_auth__pb2.GetMeRequest.SerializeToString,
                response_deserializer=auth_dot_auth__pb2.ApiResponseGetMe.FromString,
                _registered_method=True)


class AuthServiceServicer:
    """Missing associated documentation comment in.proto file."""

    def VerifyCode(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ForgotPassword(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ResetPassword(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RegisterUser(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def LoginUser(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RefreshToken(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetMe(self, request, context):
        """Missing associated documentation comment in.proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_AuthServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'VerifyCode': grpc.unary_unary_rpc_method_handler(
                    servicer.VerifyCode,
                    request_deserializer=auth_dot_auth__pb2.VerifyCodeRequest.FromString,
                    response_serializer=auth_dot_auth__pb2.ApiResponseVerifyCode.SerializeToString,
            ),
            'ForgotPassword': grpc.unary_unary_rpc_method_handler(
                    servicer.ForgotPassword,
                    request_deserializer=auth_dot_auth__pb2.ForgotPasswordRequest.FromString,
                    response_serializer=auth_dot_auth__pb2.ApiResponseForgotPassword.SerializeToString,
            ),
            'ResetPassword': grpc.unary_unary_rpc_method_handler(
                    servicer.ResetPassword,
                    request_deserializer=auth_dot_auth__pb2.ResetPasswordRequest.FromString,
                    response_serializer=auth_dot_auth__pb2.ApiResponseResetPassword.SerializeToString,
            ),
            'RegisterUser': grpc.unary_unary_rpc_method_handler(
                    servicer.RegisterUser,
                    request_deserializer=auth_dot_auth__pb2.RegisterRequest.FromString,
                    response_serializer=auth_dot_auth__pb2.ApiResponseRegister.SerializeToString,
            ),
            'LoginUser': grpc.unary_unary_rpc_method_handler(
                    servicer.LoginUser,
                    request_deserializer=auth_dot_auth__pb2.LoginRequest.FromString,
                    response_serializer=auth_dot_auth__pb2.ApiResponseLogin.SerializeToString,
            ),
            'RefreshToken': grpc.unary_unary_rpc_method_handler(
                    servicer.RefreshToken,
                    request_deserializer=auth_dot_auth__pb2.RefreshTokenRequest.FromString,
                    response_serializer=auth_dot_auth__pb2.ApiResponseRefreshToken.SerializeToString,
            ),
            'GetMe': grpc.unary_unary_rpc_method_handler(
                    servicer.GetMe,
                    request_deserializer=auth_dot_auth__pb2.GetMeRequest.FromString,
                    response_serializer=auth_dot_auth__pb2.ApiResponseGetMe.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'pb.AuthService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('pb.AuthService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class AuthService:
    """Missing associated documentation comment in.proto file."""

    @staticmethod
    def VerifyCode(request,
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
            '/pb.AuthService/VerifyCode',
            auth_dot_auth__pb2.VerifyCodeRequest.SerializeToString,
            auth_dot_auth__pb2.ApiResponseVerifyCode.FromString,
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
    def ForgotPassword(request,
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
            '/pb.AuthService/ForgotPassword',
            auth_dot_auth__pb2.ForgotPasswordRequest.SerializeToString,
            auth_dot_auth__pb2.ApiResponseForgotPassword.FromString,
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
    def ResetPassword(request,
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
            '/pb.AuthService/ResetPassword',
            auth_dot_auth__pb2.ResetPasswordRequest.SerializeToString,
            auth_dot_auth__pb2.ApiResponseResetPassword.FromString,
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
    def RegisterUser(request,
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
            '/pb.AuthService/RegisterUser',
            auth_dot_auth__pb2.RegisterRequest.SerializeToString,
            auth_dot_auth__pb2.ApiResponseRegister.FromString,
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
    def LoginUser(request,
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
            '/pb.AuthService/LoginUser',
            auth_dot_auth__pb2.LoginRequest.SerializeToString,
            auth_dot_auth__pb2.ApiResponseLogin.FromString,
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
    def RefreshToken(request,
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
            '/pb.AuthService/RefreshToken',
            auth_dot_auth__pb2.RefreshTokenRequest.SerializeToString,
            auth_dot_auth__pb2.ApiResponseRefreshToken.FromString,
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
    def GetMe(request,
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
            '/pb.AuthService/GetMe',
            auth_dot_auth__pb2.GetMeRequest.SerializeToString,
            auth_dot_auth__pb2.ApiResponseGetMe.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
