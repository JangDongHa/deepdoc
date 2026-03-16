---
project: modu-api-partner
---

# modu-api-partner — Dependencies

<!-- updoc:begin -->

## 의존성

- SettlementService depends on SettlementRepository as a constructor parameter.
- NiceparkModule provides NICEPARK_API_KEY as a key for external API access.
- AuthService class has a dependency on ApiKeyRepository as a constructor parameter.
- SettlementV2Service depends on SettlementReportRepository for accessing reports.
- SettlementV2Service depends on JwtService for token management.
- AuthModule provides AuthService for dependency injection.
- PartnerTicketContractController injects PartnerTicketContractService as a dependency.
- PartnerTicketContractController injects HolidayService as a dependency.
- SettlementReportRepository is utilized by SettlementV2Service for JWT functionalities.
- The SettlementV2Controller injects the SettlementV2Service as a dependency.

<!-- updoc:end -->
