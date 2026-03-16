---
project: modu-api-partner
---

# modu-api-partner — Architecture

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

## 컨트롤러 & 엔드포인트

- The SettlementV2Controller provides a POST endpoint at '/settlement/report/auth'.
- The SettlementV2Controller provides a POST endpoint at '/settlement/report/excel'.
- The create method of DiscountCouponController is associated with the HTTP POST endpoint '/coupons'.
- The deactivate method of DiscountCouponController is associated with the HTTP POST endpoint '/coupons/:couponSeq/deactivate'.
- NiceparkController defines a success status code for the getSettlementParkinglotReport endpoint.
- The SettlementV2Controller provides a GET endpoint at '/settlement/report'.
- The POST endpoint for creating discount coupon codes is '/socar/coupon'.
- The POST endpoint for issuing discount coupons is '/socar/coupon/issue'.
- The AuthController has a POST endpoint for 'refresh'.
- The AuthController has a POST endpoint for 'logout'.

<!-- updoc:end -->
