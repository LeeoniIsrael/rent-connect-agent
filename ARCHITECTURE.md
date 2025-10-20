# RentConnect-C3AN System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    React Native Mobile App                          │
│                     (iOS/Android via Expo)                          │
└────────────────────────────┬────────────────────────────────────────┘
                             │ REST API / GraphQL
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   Backend Services Layer                             │
│                  (Vercel / Google Cloud Functions)                   │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              Orchestration Agent (Main Controller)            │  │
│  │  • Workflow Management                                        │  │
│  │  • Agent Coordination                                         │  │
│  │  • Human-in-the-loop Review                                   │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                             │                                        │
│         ┌───────────────────┼───────────────────┐                   │
│         ▼                   ▼                   ▼                   │
│  ┌──────────┐      ┌──────────────┐     ┌──────────────┐          │
│  │ Ingestion│      │   Analysis   │     │   Decision   │          │
│  │  Agents  │      │    Agents    │     │    Agents    │          │
│  └──────────┘      └──────────────┘     └──────────────┘          │
│       │                    │                     │                  │
│       ├─ Data Ingestion    ├─ Listing Analysis   ├─ Ranking        │
│       └─ Survey Ingestion  ├─ Image Analysis     ├─ Matching       │
│                            └─ Risk Detection     ├─ Route Planning  │
│                                                  └─ Compliance      │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │           Knowledge Graph Agent (Symbolic Layer)             │  │
│  │  • Fair Housing Act Rules                                     │  │
│  │  • Campus Zones & Buildings                                   │  │
│  │  • Transit Network (GTFS)                                     │  │
│  │  • Lease Term Taxonomies                                      │  │
│  │  • Safety Event Data                                          │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │      Explanation & Feedback Agents (Trust Layer)             │  │
│  │  • Decision Explanations                                      │  │
│  │  • Attribution & Traceability                                 │  │
│  │  • User Feedback Processing                                   │  │
│  │  • Continuous Learning                                        │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Firebase   │    │  External    │    │   ML Models  │
│ Auth + Store │    │   Data APIs  │    │  (Compact)   │
└──────────────┘    └──────────────┘    └──────────────┘
  • User Auth         • Zillow ZORI       • Scam Detection
  • Listings DB       • Redfin Data       • Feature Extract
  • User Profiles     • Columbia GIS      • Price Anomaly
  • Matches           • COMET GTFS        • Image Analysis
                      • HUD FMR
                      • Census ACS
```

## Agent Communication Flow

```
Property Search Workflow:
─────────────────────────────

User Request
    │
    ▼
Orchestration Agent
    │
    ├─► Data Ingestion Agent ──► External APIs ──► Raw Listings
    │                                  │
    │                                  ▼
    ├─► Listing Analysis Agent ◄──── Listings ──► Risk Scores
    │                                  │
    │                                  ▼
    ├─► Compliance Agent ◄───────── Listings ──► Compliant Set
    │                │                │
    │                └──► Knowledge Graph (FHA Rules)
    │                                  │
    │                                  ▼
    ├─► Commute Agent ◄────────────── Listings ──► Commute Scores
    │                │
    │                └──► GTFS Data / Maps API
    │                                  │
    │                                  ▼
    ├─► Ranking Agent ◄──────────── Scored Listings ──► Ranked List
    │                │
    │                └──► User Preferences
    │                                  │
    │                                  ▼
    └─► Explanation Agent ◄────── Ranked List ──► Explanations
                                      │
                                      ▼
                            [Human Review Checkpoint]
                                      │
                                      ▼
                               Return to User
```

## Data Flow Architecture

```
┌─────────────┐
│   Sources   │
└──────┬──────┘
       │
       ├─► Zillow ZORI (Market Rent Data)
       ├─► Redfin (Rental Trends)
       ├─► Columbia GIS (Property/Zoning Data)
       ├─► COMET GTFS (Transit Schedules)
       ├─► HUD (Fair Market Rents)
       └─► Census ACS (Demographics)
       │
       ▼
┌─────────────────────┐
│  Ingestion Layer    │
│  • Fetch            │
│  • Clean            │
│  • Deduplicate      │
│  • Normalize        │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Processing Layer   │
│  • Risk Analysis    │
│  • Feature Extract  │
│  • Scoring          │
│  • Matching         │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Knowledge Layer    │
│  • Rules Engine     │
│  • Graph Queries    │
│  • Compliance Check │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│   Storage Layer     │
│  • Firestore        │
│  • Cache (Redis)    │
│  • Logs             │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│   Presentation      │
│  • React Native     │
│  • Explanations     │
│  • Visualizations   │
└─────────────────────┘
```

## Agent Interaction Matrix

| Agent                  | Depends On                                | Output To                           |
|------------------------|-------------------------------------------|-------------------------------------|
| Data Ingestion         | External APIs                             | All Analysis Agents                 |
| Knowledge Graph        | -                                         | Compliance, Matching, Ranking       |
| Listing Analysis       | Data Ingestion                            | Ranking, Compliance                 |
| Image Analysis         | Data Ingestion                            | Listing Analysis                    |
| Roommate Matching      | Survey Ingestion, Knowledge Graph         | Explanation                         |
| Ranking & Scoring      | Listing Analysis, Commute, Compliance     | Orchestrator                        |
| Commute Scoring        | Data Ingestion, Knowledge Graph (GTFS)    | Ranking                             |
| Route Planning         | Ranking, Knowledge Graph (Transit)        | Orchestrator                        |
| Compliance & Safety    | Listing Analysis, Knowledge Graph (FHA)   | Ranking, Orchestrator               |
| Explanation            | All Decision Agents                       | User Interface                      |
| Feedback & Learning    | User Interface                            | All Agents (weight updates)         |
| Orchestration          | All Agents                                | User Interface                      |

## Technology Stack Mapping

```
┌──────────────────────────────────────────────────────────┐
│                      Frontend                             │
│  • React Native (cross-platform mobile)                   │
│  • Expo (dev tooling)                                     │
│  • React Navigation (routing)                             │
│  • Firebase SDK (auth, realtime updates)                  │
└───────────────────────┬──────────────────────────────────┘
                        │ HTTP/WebSocket
                        ▼
┌──────────────────────────────────────────────────────────┐
│                   Backend Services                        │
│  • Python 3.9+ (agent logic)                              │
│  • Flask/FastAPI (REST API)                               │
│  • Google Cloud Functions (serverless)                    │
│  • Vercel (hosting/deployment)                            │
└───────────────────────┬──────────────────────────────────┘
                        │
         ┌──────────────┼──────────────┐
         ▼              ▼              ▼
┌──────────────┐ ┌─────────────┐ ┌──────────────┐
│   Firebase   │ │   ML/NLP    │ │     APIs     │
│              │ │             │ │              │
│ • Firestore  │ │ • NLTK      │ │ • Google Maps│
│ • Auth       │ │ • sklearn   │ │ • Transit API│
│ • Storage    │ │ • NetworkX  │ │ • Census API │
└──────────────┘ └─────────────┘ └──────────────┘
```

## Deployment Architecture

```
Production Environment:
──────────────────────

┌───────────────────────────────────────────────────┐
│              Content Delivery Network             │
│                    (Firebase)                     │
└────────────────────┬──────────────────────────────┘
                     │
                     ▼
┌───────────────────────────────────────────────────┐
│            Load Balancer / API Gateway            │
│                 (Google Cloud)                     │
└────────────┬──────────────────────┬────────────────┘
             │                      │
             ▼                      ▼
┌─────────────────────┐  ┌─────────────────────────┐
│   Agent Services    │  │   Static Services        │
│   (Cloud Functions) │  │   (Vercel)               │
│                     │  │                          │
│  • Orchestrator     │  │  • Landing Page          │
│  • Data Ingest      │  │  • Docs                  │
│  • Analysis         │  │  • Admin Panel           │
│  • Matching         │  │                          │
│  • Ranking          │  │                          │
└──────────┬──────────┘  └──────────────────────────┘
           │
           ▼
┌───────────────────────────────────────────────────┐
│              Data & Storage Layer                 │
│                                                   │
│  ┌─────────────┐  ┌──────────┐  ┌─────────────┐ │
│  │  Firestore  │  │  Redis   │  │   BigQuery  │ │
│  │  (primary)  │  │  (cache) │  │  (analytics)│ │
│  └─────────────┘  └──────────┘  └─────────────┘ │
└───────────────────────────────────────────────────┘
```

## Security & Compliance

```
Security Layers:
───────────────

┌────────────────────────────────────────────┐
│          Authentication Layer               │
│  • Firebase Auth                            │
│  • .edu email verification                  │
│  • OAuth for social login                   │
└───────────────┬────────────────────────────┘
                │
                ▼
┌────────────────────────────────────────────┐
│          Authorization Layer                │
│  • Role-based access (student/landlord)     │
│  • API key rotation                         │
│  • Rate limiting                            │
└───────────────┬────────────────────────────┘
                │
                ▼
┌────────────────────────────────────────────┐
│          Data Protection Layer              │
│  • Encryption at rest (Firestore)           │
│  • Encryption in transit (TLS)              │
│  • PII anonymization                        │
└───────────────┬────────────────────────────┘
                │
                ▼
┌────────────────────────────────────────────┐
│          Compliance Layer                   │
│  • FHA rule enforcement                     │
│  • Audit logging                            │
│  • Human review checkpoints                 │
│  • Data retention policies                  │
└────────────────────────────────────────────┘
```

## Scalability Considerations

1. **Horizontal Scaling**: Cloud Functions auto-scale based on load
2. **Caching**: Redis for frequent queries (listings, transit data)
3. **Batch Processing**: Nightly updates for market data
4. **Edge Computing**: Deploy lightweight models to mobile (TF Lite)
5. **Database Sharding**: Partition by university/city
6. **Rate Limiting**: Per-user API quotas
7. **Async Processing**: Background jobs for matching, ranking
8. **CDN**: Static assets via Firebase Hosting

## Monitoring & Observability

```
Monitoring Stack:
────────────────

Google Cloud Monitoring
    ├─► Function Performance (latency, errors)
    ├─► API Usage Metrics
    └─► Cost Tracking

Firebase Analytics
    ├─► User Behavior (searches, matches)
    ├─► Conversion Funnels
    └─► A/B Testing

Custom Metrics
    ├─► Agent Performance (decision quality)
    ├─► Compliance Violations
    ├─► Human Review Rate
    └─► Match Acceptance Rate

Logging
    ├─► Structured logs (JSON)
    ├─► Audit trail (all decisions)
    └─► Error tracking (Sentry)
```

---

This architecture implements the C³AN framework with clear separation of concerns, neurosymbolic reasoning, and human-in-the-loop oversight.
