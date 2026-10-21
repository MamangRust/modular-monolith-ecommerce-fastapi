"""Auth gRPC handler. Timestamps in Register/GetMe are formatted with `time.Time.String` shape ("2006-01-02 15:04:05.999999999 -0700 MST"), which is what the handler emits via `res.CreatedAt.Time.String`. Deviation from (recorded in the matrix): `RefreshToken` returns the *newly issued* refresh token. returns `req.RefreshToken` (the token the client just presented) while the service has already deleted it from the database, so the client would hold an invalid token; returning the new one is the evident intent."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pb.auth import auth_pb2, auth_pb2_grpc
from pkg.logger.logger import Logger
from pkg.middleware import grpc_method
from service.auth.service.interfaces import (
    IdentifyService,
    LoginService,
    PasswordResetService,
    RegistrationService,
)
from service.auth.service.service import SERVICE_NAME
from shared.domain.requests.auth import (
    AuthRequest,
    CreateResetPasswordRequest,
    RegisterRequest,
)


def go_time_string(value: datetime | None) -> str:
    """Format a datetime the way `time.Time.String` does. prints fractional seconds with trailing zeros trimmed (and no decimal point at all when they are zero), followed by the numeric offset and the zone abbreviation. Postgres `TIMESTAMP` values arrive naive and UTC, so that is the offset used here."""
    if value is None:
        return ""
    if value.microsecond:
        fraction = f"{value.microsecond:06d}".rstrip("0")
        stamp = f"{value.strftime('%Y-%m-%d %H:%M:%S')}.{fraction}"
    else:
        stamp = value.strftime("%Y-%m-%d %H:%M:%S")

    offset = value.utcoffset()
    if offset is None:
        return f"{stamp} +0000 UTC"
    total_minutes = int(offset.total_seconds() // 60)
    sign = "+" if total_minutes >= 0 else "-"
    total_minutes = abs(total_minutes)
    zone = value.tzname() or "UTC"
    return (
        f"{stamp} {sign}{total_minutes // 60:02d}{total_minutes % 60:02d} {zone}"
    )


def _fill_user(message: Any, user: Any) -> None:
    message.id = user.user_id
    message.firstname = user.firstname
    message.lastname = user.lastname
    message.email = user.email
    message.created_at = go_time_string(user.created_at)
    message.updated_at = go_time_string(user.updated_at)


class AuthHandler(auth_pb2_grpc.AuthServiceServicer):
    def __init__(
        self,
        register: RegistrationService,
        login: LoginService,
        password_reset: PasswordResetService,
        identify: IdentifyService,
        logger: Logger,
    ) -> None:
        self._register = register
        self._login = login
        self._password_reset = password_reset
        self._identify = identify
        self.logger = logger

    @grpc_method("AuthService.VerifyCode", SERVICE_NAME)
    async def VerifyCode(self, request: Any, context: Any) -> Any:
        await self._password_reset.verify_code(request.code)
        return auth_pb2.ApiResponseVerifyCode(
            status="success", message="Verification successfully"
        )

    @grpc_method("AuthService.ForgotPassword", SERVICE_NAME)
    async def ForgotPassword(self, request: Any, context: Any) -> Any:
        await self._password_reset.forgot_password(request.email)
        return auth_pb2.ApiResponseForgotPassword(
            status="success", message="ForgotPassword successful"
        )

    @grpc_method("AuthService.ResetPassword", SERVICE_NAME)
    async def ResetPassword(self, request: Any, context: Any) -> Any:
        await self._password_reset.reset_password(
            CreateResetPasswordRequest(
                reset_token=request.reset_token,
                password=request.password,
                confirm_password=request.confirm_password,
            )
        )
        return auth_pb2.ApiResponseResetPassword(
            status="success", message="Reset password successful"
        )

    @grpc_method("AuthService.LoginUser", SERVICE_NAME)
    async def LoginUser(self, request: Any, context: Any) -> Any:
        tokens = await self._login.login(
            AuthRequest(email=request.email, password=request.password)
        )
        return auth_pb2.ApiResponseLogin(
            status="success",
            message="LoginUser successfull",
            data=auth_pb2.TokenResponse(
                access_token=tokens.access_token,
                refresh_token=tokens.refresh_token,
            ),
        )

    @grpc_method("AuthService.RefreshToken", SERVICE_NAME)
    async def RefreshToken(self, request: Any, context: Any) -> Any:
        tokens = await self._identify.refresh_token(request.refresh_token)
        return auth_pb2.ApiResponseRefreshToken(
            status="success",
            message="Refresh token successful",
            data=auth_pb2.TokenResponse(
                access_token=tokens.access_token,
                refresh_token=tokens.refresh_token,
            ),
        )

    @grpc_method("AuthService.GetMe", SERVICE_NAME)
    async def GetMe(self, request: Any, context: Any) -> Any:
        user = await self._identify.get_me(int(request.userId))
        response = auth_pb2.ApiResponseGetMe(
            status="success", message="Get me successfully"
        )
        _fill_user(response.data, user)
        return response

    @grpc_method("AuthService.RegisterUser", SERVICE_NAME)
    async def RegisterUser(self, request: Any, context: Any) -> Any:
        user = await self._register.register(
            RegisterRequest(
                firstname=request.firstname,
                lastname=request.lastname,
                email=request.email,
                password=request.password,
                confirm_password=request.confirm_password,
            )
        )
        response = auth_pb2.ApiResponseRegister(
            status="success", message="RegisterUser successful"
        )
        _fill_user(response.data, user)
        return response


__all__ = ["AuthHandler", "go_time_string"]
