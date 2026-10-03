# Requirements vs. Implementation — Order Management

Sources checked: docs/requirements.md, src/auth/permissions.ts, src/orders/cancel.ts (repository/file tools, read-only). Database, API, and project-tracker tools were not connected for this check — nothing below relies on them.

## FR-010 — Only Admins can delete an order
Evidence: src/auth/permissions.ts
Evidence type: CODE_OBSERVED
Status: Conflict
Confidence: High

CONFLICT-001
Documented: Admin-only deletion
Observed: `canDeleteOrder()` returns true for both "admin" and "manager" roles
Status: Requires business decision

## FR-011 — Orders can be cancelled by the customer within 24 hours of placement
Evidence: src/orders/cancel.ts
Evidence type: CODE_OBSERVED
Status: Partially implemented
Confidence: Medium

The 24-hour window is implemented (`hoursSincePlaced <= 24`). The documentation doesn't mention the additional condition observed in code — cancellation is also blocked once `order.status === "shipped"`, even inside the 24-hour window. That's either an undocumented business rule or a bug; confirm which.

## Undocumented functionality

FR-CANDIDATE-001 — Password reset request
Evidence: src/orders/cancel.ts (resetPasswordRequest function)
Evidence type: CODE_OBSERVED
Status: Observed in implementation but not documented anywhere in docs/requirements.md.
Action: Confirm whether this should become an official requirement — and note it's oddly located in the orders/cancel module rather than an auth module, which may be worth flagging to the team separately.

## What wasn't checked
No database schema, API spec, or issue tracker was connected this session, so order data persistence and any ticket history around these rules couldn't be verified. The findings above rest only on the two source files and the one requirements doc read.
