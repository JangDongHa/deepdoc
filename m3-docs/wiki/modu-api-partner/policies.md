---
project: modu-api-partner
---

# modu-api-partner — Policies

<!-- updoc:begin -->

## 비즈니스 규칙

- DiscountCouponSpec processes DiscountCouponCodeResult under certain conditions for status evaluation.
- The extension is not allowed if the PartnerTicket status is not using.
- DiscountCouponSpec generates a discount coupon status based on certain conditions.
- The extension is not allowed if there are existing requests for the PartnerTicket.
- ApiKeyGuard uses AuthService to validate API keys.
- The extension is not allowed if there are ongoing extension requests for the PartnerTicket.
- JwtAuthGuard uses AuthBasicService for validating access tokens.
- The contract cannot be extended if it is not active, leading to StopSalePartnerTicketContractException.
- If the user's status is BLOCK, a BlackUserException is thrown.
- The extension is not allowed if the base time is outside the extendable period for the use end of the PartnerTicket.
- The method uses subDays to determine the start date for extending the use of the PartnerTicket.
- The method uses subBusinessDaysWithHolidays to calculate the end date for extending the use of the PartnerTicket.
- The extension is not allowed if there are ongoing stop requests for the PartnerTicket.
- partnerTicket is associated with partnerTicketContract.
- PartnerTicketRequestWithPartnerTicketRaw contains a reference to partnerTicket.
- DiscountCoupon has a status defined by DISCOUNT_COUPON_STATUS.
- If the user's status is DORMANT, a DormantUserException is thrown.
- If the user's status is UNREGISTER, an UnregisterUserException is thrown.
- If the user's status is unsupported, an UnsupportedUserStatusException is thrown.
- NiceparkInvalidApiKeyException is thrown in NiceparkController when the API key is invalid.
- If the AuthCode is null, it throws a NotFoundAuthCode exception.
- If the AuthCode's verifiedAt is null, it throws a NotVerifiedCode exception.
- If the AuthCode's phone does not match the provided phone string, it throws an UnauthorizedPhone exception.
- AuthPermissionService checks if the user has the specified PartnerPermission.
- JwtAuthGuard checks if the partner is active using PartnerSpec.
- JwtAuthGuard checks if the partner user is active using PartnerUserSpec.
- DiscountCouponSpec checks the status of a DiscountCouponUser against DISCOUNT_COUPON_USER_STATUS.
- AuthController uses AuthBasicService to validate user login requests.
- SettlementV2Module provides SettlementV2Service as a service for business logic.
- The contract cannot be purchased if it is not active, which results in NotAblePartnerTicketNewPurchaseStatusException.
- The PartnerTicketProductSpec class uses a base time for calculating business days excluding holidays.

<!-- updoc:end -->
