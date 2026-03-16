---
project: modu-api-partner
synced_from: d3b5dd2
synced_at: 2026-03-16
---

# modu-api-partner

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

*No data found for 데이터베이스.*

*No data found for 큐/백그라운드.*

<!-- updoc:end -->

## Sections



- [Architecture](architecture.md)

- [Configuration](configuration.md)

- [Dependencies](dependencies.md)
