---
type: function
name: get_current_user()
created: 2026-05-03T13:49:28Z
updated: 2026-05-03T14:00:47Z
confidence: 0.90
sources: [snapshot-20260503-134042]
related: []
tier: working
---
# get_current_user

FastAPI dependency that enforces authentication. It depends on `get_current_user_optional` and raises a 401 Unauthorized exception if no valid user is found.

## References

- [snapshot: snapshot-20260503-134042]
