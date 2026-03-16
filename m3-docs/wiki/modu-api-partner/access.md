---
project: modu-api-partner
---

# modu-api-partner — Access

<!-- updoc:begin -->

## 인증 & 접근

- PartnerTicketRequestController uses JwtAuthGuard for authentication.
- JwtAuthGuard uses AuthPermissionService to get partner user permissions.
- The SocarPassportController utilizes the ApiKeyGuard for authentication.
- AuthController uses JwtAuthGuard for protected routes like getMenu.
- The SettlementV2Controller uses the SettlementV2JwtAuthGuard for authentication on specific endpoints.
- PermissionGuard accesses the Response to check permissions.
- SettlementV2JwtAuthGuard acts on Request to retrieve the authorization header.
- PartnerCardController's create method is guarded by HasPermission with PARTNER_PERMISSION_CODE.CARD_CREATE.
- JwtAuthGuard uses AuthBasicService for validating access tokens.
- PermissionGuard uses META_DATA_KEY_PERMISSION to check user permissions.
- SettlementV2JwtAuthGuard uses SettlementV2Service to validate the access token.
- JwtAuthGuard throws NotFoundTokenException if the access token is null.
- SettlementV2JwtAuthGuard throws NotFoundTokenException if the access token is null.
- SettlementV2JwtAuthGuard modifies Response to store the user after validating the access token.
- ApiKeyGuard uses AuthService to validate API keys.
- AuthBasicService retrieves partnerUser from PartnerUserRepository to validate the refresh token.
- AuthBasicService updates refreshToken and refreshTokenExpiredAt in the PartnerUserRepository after generating a new refresh token.
- AuthController processes RefreshTokenRequestDto to issue new access tokens.
- AuthController uses Response to send HTTP responses with access tokens and partner lists.
- The AuthController has a POST endpoint for 'refresh'.
- NiceparkModule provides NICEPARK_API_KEY as a key for external API access.
- NiceparkModule provides NICEPARK_API_KEY.
- SocarPassportModule provides SOCAR_API_KEY.
- AuthService throws InvalidApiKeyException if the API key is not found and is from a Nice Park controller.
- NiceparkInvalidApiKeyException is thrown in NiceparkController when the API key is invalid.
- ApiKeyGuard throws InvalidApiKeyException when the API key is not provided and the current controller is NiceparkController.
- ApiKeyGuard throws ForbiddenApiKeyException when the API key is not provided and the current controller is not NiceparkController.
- AuthService throws ForbiddenApiKeyException if the API key is not found and is not from a Nice Park controller.
- The DiscountCouponController throws NotFoundTokenException if the API key is invalid.

<!-- updoc:end -->
