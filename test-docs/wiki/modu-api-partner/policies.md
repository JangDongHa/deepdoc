---
project: modu-api-partner
---

# modu-api-partner — Policies

<!-- updoc:begin -->

## 비즈니스 규칙

- If there are any progress requests, a NotAbleExtendPartnerTicketException is thrown with the message '접수된 신청이 존재합니다.'
- If the PartnerTicket status is not able to extend, a NotAbleExtendPartnerTicketException is thrown with the message '이용종료되어 연장 불가합니다.'
- If there are existing progress extend requests, a NotAbleExtendPartnerTicketException is thrown with the message '이미 연장 신청 중입니다.'
- JwtAuthGuard validates if the associated partner is active using PartnerSpec.
- If there are existing progress stop requests, a NotAbleExtendPartnerTicketException is thrown with the message '중도 취소 중인 주차권입니다.'
- If the current time is not within the extendable period, a NotAbleExtendPartnerTicketException is thrown with the message '연장 가능한 기간이 아닙니다.'
- JwtAuthGuard validates if the partner user is active using PartnerUserSpec.
- A PartnerTicket has the status PARTNER_TICKET_STATUS.USING when it is able to be extended.
- PartnerTickets may have requests of type PARTNER_TICKET_REQUEST_TYPE.STOP and PARTNER_TICKET_REQUEST_TYPE.EXTEND based on user interaction.
- JwtAuthGuard uses AuthBasicService to validate the access token.
- PartnerTicket uses subDays to calculate the start date for extendable use based on the user's end date.
- PartnerTicket uses holidays for determining the extendable period.
- PartnerTickets may have several requests with statuses including PARTNER_TICKET_REQUEST_STATUS.WAIT, PARTNER_TICKET_REQUEST_STATUS.RECEIVE, and PARTNER_TICKET_REQUEST_STATUS.SEND.
- PartnerTicket uses subBusinessDaysWithHolidays to determine the last date for extendable use while considering holidays.
- PartnerTicket uses addSeconds to calculate the new start date for the use period when extending.
- PartnerTicket checks if the base time is within the calculated interval for extendable use using isWithinInterval.
- PermissionGuard checks user permissions using Response.
- JwtAuthGuard checks permissions against PARTNER_PERMISSION_CODE.
- AuthController has an endpoint to check member using CheckMemberRequest at 'check-member'
- PermissionGuard uses Response to check if the user has permissions.

<!-- updoc:end -->
