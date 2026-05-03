---
type: concept
name: Keycloak Token Propagation Gap
created: 2026-05-03T13:55:05Z
updated: 2026-05-03T13:55:05Z
confidence: 0.70
sources: [snapshot-20260503-134042]
related: []
tier: working
---
# Keycloak Token Propagation Gap

A critical security pitfall where the BFF validates Keycloak JWTs but fails to forward them to the Core API, leading to a lack of identity context.

## References

- [snapshot: snapshot-20260503-134042]
