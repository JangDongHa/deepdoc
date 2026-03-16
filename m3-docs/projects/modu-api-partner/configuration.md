---
project: modu-api-partner
---

# modu-api-partner — Configuration

<!-- updoc:begin -->

## 설정

- OnlineSalesRequestController uses APP for configuration limits in its upload methods.
- AppModule creates an instance of STSClient for AWS operations when in local environment.
- AppModule checks the current environment against NODE_ENV to determine if it is local.
- ShareTimeHistoryModule imports AuthModule in its configuration.
- FileModule provides FILE_SERVICE_OPTIONS for configuration.
- PaymentModule uses ConfigService to fetch configuration values.
- SettlementV2Service uses ConfigService for configuration management.
- OnlineSalesRequestModule imports FileModule for asynchronous root configuration.
- SettlementV2Module provides SETTLEMENT_MODULE_OPTIONS for settlement configuration.
- AppModule accesses configurations through the ConfigService to set CORS settings.

<!-- updoc:end -->
