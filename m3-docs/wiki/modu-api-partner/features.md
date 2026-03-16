---
project: modu-api-partner
---

# modu-api-partner — Features

<!-- updoc:begin -->

## 기능

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

## 백그라운드 처리

- SettlementV2Module imports BullModule for job queue management.
- AuthController processes LoginRequestDto for user login.
- DiscountCouponSpec processes DiscountCouponCodeResult under certain conditions for status evaluation.
- AuthController processes RefreshTokenRequestDto to issue new access tokens.
- PartnerTicketModule registers a queue named BullPartner.TicketExtend through BullModule.

<!-- updoc:end -->
