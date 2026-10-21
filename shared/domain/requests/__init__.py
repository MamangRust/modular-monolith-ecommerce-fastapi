"""
Request DTO aggregator (regenerated for the ecommerce port).
"""

from shared.domain.requests.auth import (
    AuthRequest,
    CreateRefreshToken,
    CreateResetPasswordRequest,
    CreateResetTokenRequest,
    CreateUserRoleRequest,
    ForgotPasswordRequest,
    JWTToken,
    RefreshTokenRequest,
    RegisterRequest,
    RemoveUserRoleRequest,
    ResetPasswordRequest,
    UpdateRefreshToken,
    VerifyCodeRequest,
)
from shared.domain.requests.banner import (
    CreateBannerRequest,
    FindAllBanner,
    UpdateBannerRequest,
)
from shared.domain.requests.category import (
    CreateCategoryRequest,
    FindAllCategory,
    MonthPriceId,
    MonthPriceMerchant,
    MonthTotalPrice,
    MonthTotalPriceCategory,
    MonthTotalPriceMerchant,
    UpdateCategoryRequest,
    YearPriceId,
    YearPriceMerchant,
    YearTotalPriceCategory,
    YearTotalPriceMerchant,
)
from shared.domain.requests.order_item import (
    CreateOrderItemRecordRequest,
    FindAllOrderItems,
    UpdateOrderItemRecordRequest,
)
from shared.domain.requests.role import CreateRoleRequest, FindAllRoles, RoleRequestPayload, UpdateRoleRequest
from shared.domain.requests.shipping_address import (
    CreateShippingAddressRequest,
    FindAllShippingAddress,
    UpdateShippingAddressRequest,
)
from shared.domain.requests.slider import (
    CreateSliderRequest,
    FindAllSlider,
    UpdateSliderRequest,
)
from shared.domain.requests.user import CreateUserRequest, FindAllUsers, UpdateUserRequest

__all__ = [
    "AuthRequest",
    "CreateRefreshToken",
    "CreateResetPasswordRequest",
    "CreateResetTokenRequest",
    "CreateUserRoleRequest",
    "ForgotPasswordRequest",
    "JWTToken",
    "RefreshTokenRequest",
    "RegisterRequest",
    "RemoveUserRoleRequest",
    "ResetPasswordRequest",
    "UpdateRefreshToken",
    "VerifyCodeRequest",
    "CreateBannerRequest",
    "FindAllBanner",
    "UpdateBannerRequest",
    "CreateCategoryRequest",
    "FindAllCategory",
    "MonthPriceId",
    "MonthPriceMerchant",
    "MonthTotalPrice",
    "MonthTotalPriceCategory",
    "MonthTotalPriceMerchant",
    "UpdateCategoryRequest",
    "YearPriceId",
    "YearPriceMerchant",
    "YearTotalPriceCategory",
    "YearTotalPriceMerchant",
    "CreateRoleRequest",
    "FindAllRoles",
    "RoleRequestPayload",
    "UpdateRoleRequest",
    "CreateUserRequest",
    "FindAllUsers",
    "UpdateUserRequest",
    "CreateOrderItemRecordRequest",
    "FindAllOrderItems",
    "UpdateOrderItemRecordRequest",
    "CreateShippingAddressRequest",
    "FindAllShippingAddress",
    "UpdateShippingAddressRequest",
    "CreateSliderRequest",
    "FindAllSlider",
    "UpdateSliderRequest",
]
