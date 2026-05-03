---
type: concept
name: MongoDB + PostgreSQL Dual-Write Inconsistency
created: 2026-05-03T13:55:06Z
updated: 2026-05-03T13:55:06Z
confidence: 0.70
sources: [snapshot-20260503-134042]
related: []
tier: working
---
# MongoDB + PostgreSQL Dual-Write Inconsistency

A significant pitfall where non-atomic writes to both MongoDB (for content) and PostgreSQL (for metadata) can lead to data inconsistencies and ghost records.

## References

- [snapshot: snapshot-20260503-134042]
