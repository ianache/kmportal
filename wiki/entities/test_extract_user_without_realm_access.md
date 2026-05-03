---
type: function
name: test_extract_user_without_realm_access
created: 2026-05-03T14:07:27Z
updated: 2026-05-03T14:07:27Z
confidence: 0.70
sources: [snapshot-20260503-134042]
related: []
tier: working
---
# test_extract_user_without_realm_access

Tests that `extract_user_from_token` gracefully handles payloads missing the `realm_access` field, resulting in an empty roles list.

## References

- [snapshot: snapshot-20260503-134042]
