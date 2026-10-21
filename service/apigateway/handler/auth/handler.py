"""Gateway auth handler: REST <-> auth gRPC.

Transport only: build the proto request, call the auth service, convert a
gRPC failure back to its AppError, map the response, and maintain the
gateway-side response cache (login by email, refresh by token, get-me by
user id)."""

from __future__ import annotations

import grpc

from pb.auth import auth_pb2, auth_pb2_grpc
from service.apigateway.app.client import ServiceConnections
from service.apigateway.redis.auth import AuthCache
from shared.domain.response.auth import (
    ApiResponseForgotPassword,
    ApiResponseGetMe,
    ApiResponseLogin,
    ApiResponseRefreshToken,
    ApiResponseRegister,
    ApiResponseResetPassword,
    ApiResponseVerifyCode,
)
from shared.errors import parse_grpc_error
from shared.mapper.auth import (
    to_response_forgot_password,
    to_response_get_me,
    to_response_login,
    to_response_refresh_token,
    to_response_register,
    to_response_reset_password,
    to_response_verify_code,
)

RPC_TIMEOUT = 30.0


class AuthHandler:
    def __init__(
        self, connections: ServiceConnections, cache: AuthCache | None = None
    ) -> None:
        channel = connections.channel("auth")
        self._client = auth_pb2_grpc.AuthServiceStub(channel)
        self._cache = cache

    async def register(
        self,
        firstname: str,
        lastname: str,
        email: str,
        password: str,
        confirm_password: str,
    ) -> ApiResponseRegister:
        request = auth_pb2.RegisterRequest(
            firstname=firstname,
            lastname=lastname,
            email=email,
            password=password,
            confirm_password=confirm_password,
        )
        try:
            response = await self._client.RegisterUser(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_response_register(response)

    async def login(self, email: str, password: str) -> ApiResponseLogin:
        if self._cache is not None:
            cached = await self._cache.get_cached_login(email)
            if cached is not None:
                return cached

        request = auth_pb2.LoginRequest(email=email, password=password)
        try:
            response = await self._client.LoginUser(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc

        mapped = to_response_login(response)
        if self._cache is not None:
            await self._cache.set_cached_login(email, mapped)
        return mapped

    async def refresh_token(self, refresh_token: str) -> ApiResponseRefreshToken:
        if self._cache is not None:
            cached = await self._cache.get_refresh_token(refresh_token)
            if cached is not None:
                return cached

        request = auth_pb2.RefreshTokenRequest(refresh_token=refresh_token)
        try:
            response = await self._client.RefreshToken(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc

        mapped = to_response_refresh_token(response)
        if self._cache is not None:
            await self._cache.set_refresh_token(refresh_token, mapped)
        return mapped

    async def verify_code(self, code: str) -> ApiResponseVerifyCode:
        request = auth_pb2.VerifyCodeRequest(code=code)
        try:
            response = await self._client.VerifyCode(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_response_verify_code(response)

    async def forgot_password(self, email: str) -> ApiResponseForgotPassword:
        request = auth_pb2.ForgotPasswordRequest(email=email)
        try:
            response = await self._client.ForgotPassword(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_response_forgot_password(response)

    async def reset_password(
        self, reset_token: str, password: str, confirm_password: str
    ) -> ApiResponseResetPassword:
        request = auth_pb2.ResetPasswordRequest(
            reset_token=reset_token,
            password=password,
            confirm_password=confirm_password,
        )
        try:
            response = await self._client.ResetPassword(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc
        return to_response_reset_password(response)

    async def get_me(self, user_id: int) -> ApiResponseGetMe:
        if self._cache is not None:
            cached = await self._cache.get_cached_user_info(user_id)
            if cached is not None:
                return cached

        request = auth_pb2.GetMeRequest(userId=user_id)
        try:
            response = await self._client.GetMe(request, timeout=RPC_TIMEOUT)
        except grpc.aio.AioRpcError as exc:
            raise parse_grpc_error(exc) from exc

        mapped = to_response_get_me(response)
        if self._cache is not None:
            await self._cache.set_cached_user_info(user_id, mapped)
        return mapped


__all__ = ["AuthHandler"]
