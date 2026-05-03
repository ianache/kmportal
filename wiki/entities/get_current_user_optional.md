---
type: function
name: get_current_user_optional
created: 2026-05-03T14:00:46Z
updated: 2026-05-03T14:00:46Z
confidence: 0.70
sources: [snapshot-20260503-134042]
related: []
tier: working
---
# get_current_user_optional

FastAPI dependency that attempts to authenticate a user using a JWT token from the Authorization header. If successful, it returns a `UserInToken` object; otherwise, it returns `None`. It also manages user synchronization with the database.

## References

- [snapshot: snapshot-20260503-134042]
