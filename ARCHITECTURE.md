# RentConnect-C3AN System Architecture

**Current Version**: Refactored (October 2024)  
**Architecture**: 3-Layer System (Preprocessing → Tools → Agents)  
**No Orchestration Agent**: Direct workflow coordination

---

## High-Level Architecture

<img width="467" height="972" alt="High-level drawio" src="https://github.com/user-attachments/assets/4aa2f1df-4139-45e0-9d14-a4e12fe2fb08" />


## Workflow Communication Flow

### Workflow 1: Property Search

```
User Request
    │
    ▼
┌──────────────────────────────────┐
│   DataIngestion.ingest_listings  │──► External APIs ──► Raw Listings
└──────────────┬───────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│   listing_analyzer.analyze       │──► Risk Scores + Features
│   compliance_checker.check       │──► Compliance Status
│   image_analyzer.analyze         │──► Image Quality
└──────────────┬───────────────────┘
               │
               ▼ (filtered listings)
┌──────────────────────────────────┐
│   ranking_scoring.rank()         │──► User Preferences ──► Ranked List
│   (multi-objective scoring)       │
└──────────────┬───────────────────┘
               │
               ▼
          Return to User
    (with explanations & scores)
```

### Workflow 2: Roommate Matching

```
User Surveys
    │
    ▼
┌──────────────────────────────────┐
│ SurveyIngestion.process_survey   │──► FHA Compliance Check
└──────────────┬───────────────────┘
               │
               ▼ (validated profiles)
┌──────────────────────────────────┐
│   roommate_matching.match()      │──► Stable Matching Algorithm
│   (Gale-Shapley variant)         │
└──────────────┬───────────────────┘
               │
               ▼
          Matched Pairs
    (with compatibility scores)
```

### Workflow 3: Tour Planning

```
Selected Properties + Class Schedule
    │
    ▼
┌──────────────────────────────────┐
│   route_planning.plan()          │──► Time Windows
│   (TSP with constraints)         │──► Travel Times
└──────────────┬───────────────────┘
               │
               ▼
         Optimized Tour
    (visit order + arrival times)
```

### Workflow 4: Feedback Learning

```
User Rating / Expert Correction
    │
    ▼
┌──────────────────────────────────┐
│   feedback_learning.process()    │──► Update Preferences
│   (drift detection + learning)   │──► Model Corrections
└──────────────┬───────────────────┘
               │
               ▼
       Updated User Profile
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

## Component Interaction Matrix

| Component              | Type          | Depends On                          | Output To                    |
|------------------------|---------------|-------------------------------------|------------------------------|
| DataIngestion          | Preprocessing | External APIs                       | Workflows, Tools             |
| SurveyIngestion        | Preprocessing | User Input                          | Agents (roommate_matching)   |
| knowledge_graph        | Tool          | -                                   | compliance_checker, Agents   |
| listing_analyzer       | Tool          | Listings                            | Workflows                    |
| image_analyzer         | Tool          | Listings                            | Workflows                    |
| compliance_checker     | Tool          | Listings, knowledge_graph           | Workflows                    |
| roommate_matching      | Agent         | SurveyIngestion                     | User Interface               |
| ranking_scoring        | Agent         | Listings, Tools                     | User Interface               |
| route_planning         | Agent         | Properties, Schedules               | User Interface               |
| feedback_learning      | Agent         | User Feedback                       | Config Updates               |

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
