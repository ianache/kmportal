---
type: concept
name: separate query embedding
created: 2026-05-03T14:03:28Z
updated: 2026-05-03T14:03:28Z
confidence: 0.70
sources: [snapshot-20260503-134042]
related: []
tier: working
---
# separate query embedding

A design decision to provide a dedicated `embed_query` method in `EmbeddingPort`, acknowledging that some models can optimize embeddings differently for search queries versus documents.

## References

- [snapshot: snapshot-20260503-134042]
