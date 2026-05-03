---
type: function
name: require_reader()
created: 2026-05-03T13:49:28Z
updated: 2026-05-03T14:00:47Z
confidence: 0.80
sources: [snapshot-20260503-134042]
related: []
tier: working
---
# require_reader

FastAPI dependency that ensures the authenticated user possesses either the 'km-admin' or 'km-reader' role. Raises a 403 Forbidden exception if neither role is present.

## References

- [snapshot: snapshot-20260503-134042]
