---
type: function
name: embed_query
created: 2026-05-04T03:25:50Z
updated: 2026-05-04T03:25:50Z
confidence: 0.70
sources: [06f748994444acb493a188587ba10a43771931c2]
related: []
tier: working
---
# embed_query

A new method in `OllamaAdapter` designed to generate an embedding optimized for search queries. It calls the general `embed` method with the input text wrapped in a list and returns the full `List[List[float]]` result, despite its type hint `List[float]`.

## References

- [06f74899](../summaries/06f74899.md)
