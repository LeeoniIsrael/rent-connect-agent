# RentConnect-C3AN: Neurosymbolic Student Housing & Roommate Orchestration

![C3AN Compliant](https://img.shields.io/badge/C3AN-Custom%20%7C%20Compact%20%7C%20Composite-blue)
![Python](https://img.shields.io/badge/Python-3.9%2B-green)
![React Native](https://img.shields.io/badge/React%20Native-0.72-61dafb)

## Overview

RentConnect-C3AN is a neurosymbolic mobile platform that helps university students find safe, affordable off-campus housing and compatible roommates. It implements the **C³AN (Custom, Compact, and Composite AI Systems)** framework with:

- **Neural modules**: Parse messy listings, images, and preferences
- **Symbolic knowledge graph**: Encodes Fair Housing rules, campus zones, lease constraints, transit data
- **Composite planning**: Multi-objective ranking, stable matching, time-windowed routing
- **Human-in-the-loop**: Trust and safety review checkpoints

### C³AN Foundation Elements Implemented

✅ **Reliability & Consistency**: Deterministic pipelines, property deduplication  
✅ **Alignment & Safety**: FHA-aware filters, prohibited criteria blocking  
✅ **Grounding & Attribution**: Link outputs to real sources and rules  
✅ **Interpretability & Explainability**: User-facing rationales with drill-downs  
✅ **Reasoning & Planning**: Multi-criteria scoring, constraint satisfaction, route optimization  
✅ **Instructability**: User-tunable weights without retraining  

## Refactored Architecture (October 2024)

**Principle**: "Only things making autonomous decisions are agents"

### System Layers

```
┌─────────────────────────────────────────┐
│         USER INPUT / FEEDBACK           │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│     PREPROCESSING LAYER                 │
│  • DataIngestion (multi-source)         │
│  • SurveyIngestion (FHA-compliant)      │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         TOOLS LAYER                     │
│  • knowledge_graph (symbolic KB)        │
│  • listing_analyzer (scam detection)    │
│  • image_analyzer (photo quality)       │
│  • compliance_checker (FHA/SC laws)     │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      AGENT LAYER (Decision-Makers)      │
│  1. roommate_matching                   │
│  2. ranking_scoring                     │
│  3. route_planning                      │
│  4. feedback_learning                   │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│     WORKFLOWS (Direct Coordination)     │
│  • Property Search                      │
│  • Roommate Matching                    │
│  • Tour Planning                        │
└─────────────────────────────────────────┘
```

### 4 Decision-Making Agents

1. **Roommate Matching Agent** (`roommate_matching`)
   - Stable matching with constraint satisfaction (Gale-Shapley variant)
   - Hard constraints: smoking, pets, quiet hours, budget
   - Soft preferences: cleanliness, social level, schedule
   - Personality: Big Five (OCEAN) compatibility
   - **C³AN Metrics**: Stability Score (95%), Fairness Score (≤0.15 variance), Hard Constraint Satisfaction (100%)

2. **Ranking & Scoring Agent** (`ranking_scoring`)
   - Multi-objective property ranking with Pareto optimality
   - Criteria: price, commute, safety, amenities, lease terms
   - User-tunable weights (instructability)
   - **C³AN Metrics**: Pareto Efficiency (≥70% in top-10), Weight Correlation (r≥0.80), Score Attributability (100%)

3. **Route Planning Agent** (`route_planning`)
   - Time-windowed tour planning around class schedules
   - Nearest-neighbor TSP heuristic
   - Multi-modal transit optimization
   - **C³AN Metrics**: Time Window Compliance (100%), Route Optimality (≥30% vs random), Tour Completion (≥80%)

4. **Feedback & Learning Agent** (`feedback_learning`)
   - Learns from user ratings and expert corrections
   - Preference drift detection
   - Expert-verified high-impact updates
   - **C³AN Metrics**: Incorporation Rate (≥90%), Improvement Rate (≥10%), Expert Verification (100% for high-impact)

## Project Structure

```
rent-connect-agent/
├── src/
│   ├── preprocessing/           # Data collection & cleaning
│   │   ├── data_ingestion.py   # Multi-source listings (Zillow, Redfin, GIS)
│   │   └── survey_ingestion.py # FHA-compliant survey processing
│   ├── tools/                   # Analysis & lookup utilities (singletons)
│   │   ├── knowledge_graph.py  # Symbolic KB (FHA rules, campus zones)
│   │   ├── listing_analyzer.py # Scam detection, feature extraction
│   │   ├── image_analyzer.py   # Photo quality & authenticity
│   │   └── compliance_checker.py # FHA & SC lease law compliance
│   └── agents/                  # 4 decision-making agents
│       ├── roommate_matching/   # Stable matching agent
│       │   ├── README.md       # Full documentation
│       │   ├── config.py       # Agent-specific settings
│       │   ├── evaluation.md   # C³AN metrics definitions
│       │   └── agent.py        # Implementation
│       ├── ranking_scoring/     # Multi-objective ranking
│       ├── route_planning/      # Time-windowed tour planning
│       └── feedback_learning/   # Learning from feedback
├── config/                      # Configuration layer
│   ├── preprocessing_config.py  # Data ingestion settings
│   ├── tools_config.py         # Tool parameters
│   └── agents_config.py        # Agent settings + HITL
├── tests/                       # Unit & integration tests
├── main.py                      # Workflow examples (no orchestration)
├── test_system.py              # Quick verification script
├── HOW_TO_RUN.md               # Simple usage guide
├── QUICK_START.md              # Detailed examples
├── IMPLEMENTATION_SUMMARY.md   # Refactoring documentation
└── REFACTORING_GUIDE.md        # Migration details
```

## Quick Start

### 1. Test the System
```bash
python test_system.py
```

### 2. Run Example Workflows
```bash
python main.py
```

### 3. Use in Your Code
```python
from src.agents import roommate_matching, ranking_scoring

# Match roommates
profiles = [...]  # User survey data
result = roommate_matching.match(profiles)

# Rank properties  
listings = [...]  # Rental listings
result = ranking_scoring.rank(listings, user_preferences, destination)
```

See `HOW_TO_RUN.md` for more examples.

## Key Features
│       │   └── knowledge_graph_agent.py     # Knowledge graph & rules
│       ├── analysis/
│       │   └── listing_analysis_agent.py    # Scam detection, risk scoring
│       ├── matching/
│       │   └── roommate_matching_agent.py   # Stable matching algorithm
│       ├── ranking/
│       │   └── ranking_agent.py             # Multi-criteria scoring
│       ├── planning/
│       │   └── route_planning_agent.py      # Tour planning, compliance
│       ├── explanation/
│       │   └── explanation_agent.py         # Explainability & feedback
│       └── orchestration/
│           └── orchestration_agent.py       # Workflow orchestrator
├── requirements.txt                          # Python dependencies
├── package.json                              # React Native dependencies
└── README.md                                 # This file
```

## Dataset Sources

### Core Housing Data
- **Zillow ZORI**: Market rent benchmarks
- **Redfin Rental Market**: Multifamily trends
- **USA Housing Listings (Kaggle)**: Prototype data
- **Craigslist Rentals (Kaggle)**: NLP training data

### Columbia/USC Context
- **City of Columbia Open Data**: Zoning, neighborhoods, code enforcement
- **Richland County GIS**: Parcels, addresses, zoning
- **COMET GTFS**: Transit routes and schedules

### Compliance & Affordability
- **HUD Fair Market Rents**: Affordability benchmarks
- **Census ACS**: Demographics, housing, income
- **Big Five Personality Test**: Roommate compatibility training

## Key Workflows

### 1. Property Search & Ranking
```
Ingest Listings → Risk Analysis → Compliance Check → Commute Scoring → 
Multi-Criteria Ranking → Explanation Generation → [Human Review]
```

### 2. Roommate Matching
```
Survey Ingestion → FHA Compliance Check → Stable Matching → 
Fairness Validation → Explanation Generation → [Human Review]
```

### 3. Tour Planning
```
Select Properties → Load Class Schedule → Route Optimization → 
Time Window Validation → Explanation Generation
```

### 4. Listing Verification
```
Risk Analysis → Compliance Check → Image Analysis → 
Verification Report → [Human Review if flagged]
```

## Installation

### Backend (Python)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your Firebase credentials, API keys, etc.
```

### Frontend (React Native)

```bash
# Install Node dependencies
npm install

# Start Expo development server
npm start

# Run on device
npm run ios     # iOS
npm run android # Android
```

## Usage Examples

### Initialize Orchestration Agent

```python
from src.agents.orchestration.orchestration_agent import OrchestrationAgent
from src.agents.base_agent import AgentContext
from datetime import datetime
import uuid

# Create orchestrator
orchestrator = OrchestrationAgent()

# Create context
context = AgentContext(
    session_id=str(uuid.uuid4()),
    user_id="student123",
    timestamp=datetime.utcnow(),
    metadata={'desired_amenities': ['parking', 'ac', 'laundry']}
)

# Run property search workflow
result = orchestrator.process(
    {
        'workflow': 'property_search',
        'workflow_input': {
            'data_sources': ['zillow_zori', 'columbia_gis'],
            'filters': {'city': 'Columbia', 'state': 'SC'},
            'preferences': {
                'weights': {
                    'price': 0.35,
                    'commute_time': 0.30,
                    'safety_score': 0.20,
                    'amenities_match': 0.15
                }
            },
            'constraints': {
                'max_budget': 1000,
                'min_bedrooms': 1,
                'max_commute_minutes': 30
            }
        },
        'human_review': True
    },
    context
)

print(f"Found {result.result['total_ranked']} ranked listings")
for listing in result.result['ranked_listings'][:3]:
    print(f"  #{listing['rank']}: {listing['listing'].get('address')} - Score: {listing['overall_score']:.2f}")
```

### Roommate Matching

```python
# Run roommate matching workflow
result = orchestrator.process(
    {
        'workflow': 'roommate_matching',
        'workflow_input': {
            'profiles': [
                {
                    'user_id': 'student1',
                    'hard_constraints': {'no_smoking': True, 'pet_policy': 'no_pets'},
                    'soft_preferences': {'cleanliness': 8, 'social_level': 6},
                    'personality': {'conscientiousness': 0.7, 'agreeableness': 0.8},
                    'budget_range': (600, 900)
                },
                {
                    'user_id': 'student2',
                    'hard_constraints': {'no_smoking': True, 'pet_policy': 'no_pets'},
                    'soft_preferences': {'cleanliness': 7, 'social_level': 5},
                    'personality': {'conscientiousness': 0.8, 'agreeableness': 0.7},
                    'budget_range': (650, 950)
                }
            ],
            'match_type': 'one_to_one'
        },
        'human_review': False
    },
    context
)

print(f"Created {len(result.result['matches'])} matches")
```

## C³AN Compliance Features

### Custom
- **Student-specific**: .edu verification, academic year leases, cosigner flows
- **USC-local**: Campus zones, COMET transit integration, Columbia safety data

### Compact
- **Lightweight models**: Distilled NLP, edge-friendly scoring
- **Domain-scoped KG**: Focused knowledge graph for fast reasoning
- **Server-side batching**: Optimize API calls and computations

### Composite
- **Neurosymbolic**: Neural feature extraction + symbolic rule enforcement
- **Multi-agent orchestration**: Specialized agents coordinated by orchestrator
- **Human-in-the-loop**: Review checkpoints for critical decisions

## Testing

```bash
# Run Python tests
pytest tests/ -v --cov=src

# Run React Native tests
npm test
```

## Deployment

### Backend Services
```bash
# Deploy to Google Cloud Functions
gcloud functions deploy rentconnect-api \
  --runtime python39 \
  --trigger-http \
  --entry-point api_handler

# Or deploy to Vercel
vercel deploy
```

### Mobile App
```bash
# Build for production
expo build:ios
expo build:android
```

## Fair Housing Compliance

This system implements Fair Housing Act safeguards:
- ✅ Blocks discriminatory filters (race, religion, national origin, etc.)
- ✅ Screens listing text for prohibited language
- ✅ Flags potentially discriminatory preferences
- ✅ Provides transparent appeals process
- ✅ Audit logs for all decisions

## Metrics & Monitoring

Key metrics tracked:
- **Lease conversion rate**: % of searches leading to signed leases
- **Days to decision**: Time from search to lease signing
- **Fraud detection**: False positive/negative rates for scam detection
- **Match acceptance**: % of roommate matches accepted
- **Tour efficiency**: Properties visited per available time window

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## License

MIT License - See [LICENSE](LICENSE) for details.

## References

1. **C³AN Framework**: [Link to C3AN paper]
2. **Fair Housing Act**: 42 U.S.C. § 3601-3619
3. **Stable Matching**: Gale-Shapley Algorithm
4. **Datasets**: See "Dataset Sources" section above

## Contact

For questions or support, contact the RentConnect team:
- **Developer**: Leeon Israel
- **Project**: RentConnect-C3AN
- **Institution**: University of South Carolina (USC)

---

**Built with C³AN principles: Custom, Compact, and Composite AI for trustworthy student housing.**
