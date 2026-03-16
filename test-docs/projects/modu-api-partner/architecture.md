---
project: modu-api-partner
---

# modu-api-partner — Architecture

<!-- updoc:begin -->

## 라우팅 구조

- RouterModule registers ShareTimeHistoryModule as a route handler.
- ExtModule imports RouterModule.
- RouterModule registers NiceparkModule as a route handler.
- RouterModule registers SocarPassportModule as a route handler.
- SettlementV2Module exports SettlementV2Service.
- ExtModule imports NiceparkModule.
- SettlementV2Module exports SettlementV2Service.
- NiceparkModule imports SettlementModule.
- ExtModule imports ShareTimeHistoryModule.
- ExtModule imports SocarPassportModule.
- ExtModule imports RouterModule.
- ShareTimeHistoryModule imports AuthModule for authentication.
- SocarPassportModule imports AuthModule for authentication.
- SocarPassportModule imports DiscountCouponRepository for custom usage.
- SocarPassportModule imports DiscountCouponCodeRepository for custom usage.

## 컨트롤러 & 엔드포인트

- AuthController has an endpoint to login using LoginRequest at 'login'
- AuthController has an endpoint to logout using Request at 'logout'
- NiceparkModule includes NiceparkController as a controller.
- ShareTimeHistoryModule includes ShareTimeHistoryController as a controller.
- SocarPassportModule includes SocarPassportController as a controller.
- AuthController has an endpoint to check member using CheckMemberRequest at 'check-member'
- AuthController has an endpoint to verify code using VerifyCodeRequest at 'verify-code'
- AuthController has an endpoint to set password using SetPasswordRequest at 'set-password'
- AuthController has an endpoint to reset password using ResetPasswordRequest at 'reset-password'
- AuthController has an endpoint to send verification code using SendVerificationCodeRequest at 'send-verification-code'

<!-- updoc:end -->
