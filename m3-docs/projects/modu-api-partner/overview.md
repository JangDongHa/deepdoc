---
project: modu-api-partner
synced_from: d3b5dd2
synced_at: 2026-03-16
---

# modu-api-partner

<!-- updoc:begin -->

## 라우팅 구조

- RouterModule registers PartnerModule as a route handler.
- RouterModule registers SettlementV2Module as a route handler.
- RouterModule registers PartnerCardModule as a route handler.
- RouterModule registers PartnerTicketModule as a route handler.
- RouterModule registers ExcelModule as a route handler.
- RouterModule registers PartnerUserModule as a route handler.
- RouterModule registers PartnerPaymentModule as a route handler.
- RouterModule registers PartnerTicketContractModule as a route handler.
- RouterModule registers OnlineSalesRequestModule as a route handler.
- RouterModule registers PartnerTicketRequestModule as a route handler.
- SettlementV2Module imports CustomTypeOrmModule to utilize custom repositories.
- ExtModule imports NiceparkModule.
- SettlementV2Module imports SettlementReportRepository as a custom TypeORM repository.
- NiceparkModule imports SettlementModule.
- SettlementV2Module imports BullModule for job queue management.
- NiceparkModule imports SettlementModule for additional functionalities.
- SettlementV2Module imports SettlementV2Repository as a custom TypeORM repository.
- SettlementV2Module imports JwtModule for JSON Web Token functionality.
- SettlementV2Module exports SettlementV2Service for use in other modules.
- SettlementV2Module provides SETTLEMENT_MODULE_OPTIONS for settlement configuration.

## 데이터베이스

- DiscountCouponModule establishes a database connection for DiscountCouponRepository
- DiscountCouponModule establishes a database connection for DiscountCouponCodeRepository
- DiscountCouponModule establishes a database connection for DiscountCouponUserRepository
- CustomTypeOrmModule imports ActivityLogRepository for custom database connectivity in the auditLog connection.
- CustomTypeOrmModule imports PartnerRepository for custom database connectivity.
- CustomTypeOrmModule imports PartnerMappingRepository for custom database connectivity.
- CustomTypeOrmModule imports RoleRepository for custom database connectivity.
- CustomTypeOrmModule imports MenuRepository for custom database connectivity.
- CustomTypeOrmModule imports RoleMenuPermissionRepository for custom database connectivity.
- CustomTypeOrmModule imports PartnerUserRepository for custom database connectivity.

## 큐/백그라운드

- SettlementV2Module imports BullModule for job queue management.
- AuthController processes LoginRequestDto for user login.
- DiscountCouponSpec processes DiscountCouponCodeResult under certain conditions for status evaluation.
- AuthController processes RefreshTokenRequestDto to issue new access tokens.
- PartnerTicketModule registers a queue named BullPartner.TicketExtend through BullModule.

<!-- updoc:end -->

## Sections



- [Architecture](architecture.md)

- [Configuration](configuration.md)

- [Dependencies](dependencies.md)
