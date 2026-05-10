# Goal

Improve the login page to support user information on onthologies y news

# Requirements

- Shows summarized información for (in BFF endpoint /api/v1/kb-summary):
  * active ontologies
  * knowledge domains
  * Ingested documents
  * Monthly queries

  for example:
  
  ```json
  {
    "activeOntologies": 3,
    "knowledgeDomains": 5,
    "ingestedDocuments": 100,
    "monthlyQueries": 1000
  }
  ```

- Shows "Network INTEL" showing platform status (normally ensuring all components are connected and working correctly) using BFF endpoint /api/v1/intel-status. For now only show "overall" status (HEALTHY as green dot, WARNING as yellow dot, CRITICAL as red dot).

for example:

```json
{
    "overall": "HEALTHY",
  "components": [
    {
      "name": "LLM Connector",
      "status": "healthy",
      "lastUpdate": "2022-01-01T00:00:00Z"
    },
    {
      "name": "Vector Database",
      "status": "healthy",
      "lastUpdate": "2022-01-01T00:00:00Z"
    },
    {
      "name": "Knowledge Graph",
      "status": "healthy",
      "lastUpdate": "2022-01-01T00:00:00Z"
    },
    {
      "name": "Event Bus",
      "status": "healthy",
      "lastUpdate": "2022-01-01T00:00:00Z"
    },
    {
      "name": "BFF",
      "status": "healthy",
      "lastUpdate": "2022-01-01T00:00:00Z"
    }
  ]
}
```

- Shows relevants news from the platform (in BFF endpoint /api/v1/news) from the last 30 days. Informations includes for each news:
  * Category (PLATFORM, INFR, COMPLIANCE, COMMUNITY, CONTENT) as defined in master data news categories.
  * date (show as a full date o relative from current date for example 3D AGO, 2H AGO, NEXT FRIDAY.)
  * title
  * summary (text)
  * url (link to the external news source - optional)

    For example:

```json
[
  {
    "id": "1",
    "category": "PLATFORM",
    "date"  : "2022-01-01T00:00:00Z",
    "title": "Neural Semantic Indexing v2 Live",
    "summary": "Enhanced document retrieval accuracy by 34% using multi-modal search.",
    "url": "https://www.google.com"
  },
  {
    "id": "2",
    "category": "INFRA",
    "date"  : "2022-01-01T00:00:00Z",
    "title": "Scheduled Cluster Expansion",
    "summary": "Maintenance and scaling scheduled for Friday, 22:00 UTC.",
    "url": "https://www.google.com"
  },
  {
    "id": "3",
    "category": "COMPLIANCE",
    "date"  : "2022-01-01T00:00:00Z",
    "title": "GDPR Compliance Update",
    "summary": "New guidelines for data handling and privacy regulations.",
    "url": "https://www.google.com"
  },
  {
    "id": "4",
    "category": "COMMUNITY",
    "date"  : "2022-01-01T00:00:00Z",
    "title": "Community Forum Launch",
    "summary": "Join the discussion and connect with other users.",
    "url": "https://www.google.com"
  },
  {
    "id": "5",
    "category": "CONTENT",
    "date"  : "2022-01-01T00:00:00Z",
    "title": "New Content Available",
    "summary": "Fresh insights and updates added to the knowledge base.",
    "url": "https://www.google.com"
  }
]
```

# Guard rail
- We are not chaning the design but source of information to be used to fill data
- Use the data from BFF endpoints not from the database directly
- Use mock data for now as the endpoints are not ready