---
project: modu-api-partner
---

# modu-api-partner — Access

<!-- updoc:begin -->

## 인증 & 접근

- JwtAuthGuard uses AuthPermissionService to get user permissions.
- ShareTimeHistoryModule imports AuthModule for authentication.
- JwtAuthGuard uses Reflector to get metadata about permissions.
- JwtAuthGuard checks permissions against PARTNER_PERMISSION_CODE.
- SocarPassportModule imports AuthModule for authentication.
- PermissionGuard checks user permissions using Response.
- PermissionGuard uses Response to check if the user has permissions.
- JwtAuthGuard uses AuthBasicService to validate the access token.
- PermissionGuard uses Reflector to get permission metadata.
- JwtAuthGuard throws NotFoundTokenException if the access token is not found.
- JwtAuthGuard validates if the partner user is active using PartnerUserSpec.
- JwtAuthGuard validates if the associated partner is active using PartnerSpec.
- JwtAuthGuard throws NotActivatedPartnerException if the partner is not activated.

<!-- updoc:end -->
