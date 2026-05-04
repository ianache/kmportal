---
type: summary
name: c9afdce3
sha: c9afdce35cfe3129d23567c6bab2322d15e267bc
created: 2026-05-04T01:11:01Z
updated: 2026-05-04T01:11:01Z
confidence: 1.00
sources: [c9afdce35cfe3129d23567c6bab2322d15e267bc]
tier: episodic
---
# Commit c9afdce3

        **fix(api): add model field to Gemini batch embedding requests and fix database connection string

- Fix Gemini adapter to include 'model' field in each request of batchEmbedContents
  This resolves the 'model is not specified' error from Gemini API
- Update .env DATABASE_URL to use 'postgres' hostname for Docker compatibility**

        This commit updates the Gemini adapter to explicitly include the 'model' field in batch embedding requests, which resolves a 'model is not specified' error from the Gemini API, and also updates the DATABASE_URL in the .env file for Docker compatibility.

        ## Changed Files
        - `api/src/adapters/embedding/gemini.py`

        ## Entities
        - **GeminiAdapter** (class): An adapter class that implements the EmbeddingPort interface, using Google's Gemini API for generating text embeddings.
- **_embed_batch** (function): A private method within GeminiAdapter responsible for constructing and sending a batch of embedding requests to the Gemini API.
- **api/src/adapters/embedding/gemini.py** (module): The Python module containing the implementation of the GeminiAdapter.
- **Gemini API batch embedding request payload** (concept): The JSON structure sent to the Gemini API's `batchEmbedContents` endpoint, which contains individual embedding requests.

        ## Stats
        - Author: ianache <ianache@crossnet.ws>
        - Timestamp: 2026-05-03T20:10:20-05:00
        - Files changed: 1
