# RentConnect-C3AN Quick Start Guide

## Prerequisites

- Python 3.9 or higher
- Node.js 16+ and npm
- Firebase account (for Auth & Firestore)
- Git

## Installation (5 minutes)

### 1. Clone and Setup

```bash
git clone <your-repo-url> rentconnect-c3an
cd rentconnect-c3an
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv venv

# Activate (Mac/Linux)
source venv/bin/activate

# Activate (Windows)
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Edit .env with your API keys
```

### 3. Frontend Setup

```bash
# Install Node dependencies
npm install

# For iOS development (Mac only)
cd ios && pod install && cd ..
```

### 4. Configuration

Edit `config.py` with your settings:
- Firebase credentials
- API keys (Google Maps, Census, etc.)
- Campus configuration (if not USC)

## Running Examples (2 minutes)

### Test All Agents

```bash
python main.py
```

This runs three example workflows:
1. Property Search & Ranking
2. Roommate Matching
3. Tour Planning

Expected output:
```
=== Property Search Example ===
✓ Search complete: Property search complete: 10 listings ranked
  - Total found: 50
  - Total ranked: 10
  #1: Score 0.85
  ...

=== Roommate Matching Example ===
✓ Matching complete: Roommate matching complete: 1 matches
  Match: alice & bob - Score: 0.82
  ...

=== Tour Planning Example ===
✓ Tour planned: Tour planned: 3 properties
  → 123 Main St at 2025-10-20 11:00:00
  ...
```

## Individual Agent Testing

### Test Data Ingestion

```python
from src.agents.ingestion.data_ingestion_agent import DataIngestionAgent
from src.agents.base_agent import AgentContext
from datetime import datetime
import uuid

agent = DataIngestionAgent()
context = AgentContext(
    session_id=str(uuid.uuid4()),
    user_id="test_user",
    timestamp=datetime.utcnow(),
    metadata={}
)

result = agent.process(
    {
        'sources': ['zillow_zori', 'columbia_gis'],
        'filters': {'city': 'Columbia', 'state': 'SC'}
    },
    context
)

print(f"Ingested: {result.explanation}")
```

### Test Listing Analysis

```python
from src.agents.analysis.listing_analysis_agent import ListingAnalysisAgent

agent = ListingAnalysisAgent()

result = agent.process(
    {
        'listing': {
            'listing_id': 'TEST001',
            'title': 'Great apartment near campus',
            'description': 'Wire transfer only. Out of country currently.',
            'price': 500,
            'bedrooms': 2,
            'address': '123 Main St, Columbia, SC'
        },
        'check_types': ['scam', 'price', 'features']
    },
    context
)

print(f"Risk Score: {result.result['risk_score']:.2f}")
print(f"Flags: {result.result['risk_flags']}")
```

### Test Roommate Matching

```python
from src.agents.matching.roommate_matching_agent import RoommateMatchingAgent

agent = RoommateMatchingAgent()

profiles = [
    {
        'user_id': 'alice',
        'hard_constraints': {'no_smoking': True},
        'soft_preferences': {'cleanliness': 8},
        'personality': {'conscientiousness': 0.7},
        'budget_range': (600, 900)
    },
    {
        'user_id': 'bob',
        'hard_constraints': {'no_smoking': True},
        'soft_preferences': {'cleanliness': 7},
        'personality': {'conscientiousness': 0.8},
        'budget_range': (650, 950)
    }
]

result = agent.process(
    {'profiles': profiles, 'match_type': 'one_to_one'},
    context
)

print(f"Matches: {len(result.result['matches'])}")
```

## Running the Mobile App

### Start Expo Dev Server

```bash
npm start
```

### Run on Device

```bash
# iOS (requires Xcode)
npm run ios

# Android (requires Android Studio)
npm run android

# Web browser
npm run web
```

### Expo Go App

1. Install Expo Go on your phone (iOS/Android)
2. Scan QR code from terminal
3. App will load on your device

## Common Issues & Solutions

### Issue: Import errors for agents

**Solution**: Make sure you're in the virtual environment and installed dependencies:
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Issue: Firebase connection errors

**Solution**: Check `.env` file has correct Firebase credentials:
```
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_API_KEY=your-api-key
```

### Issue: "Module not found" in Python

**Solution**: Add project root to PYTHONPATH:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Issue: Expo won't start

**Solution**: Clear cache and reinstall:
```bash
rm -rf node_modules
npm install
expo start --clear
```

## Next Steps

### 1. Connect Real Data Sources

Replace simulation in `data_ingestion_agent.py` with actual API calls:

```python
def _simulate_fetch(self, source: DataSource, filters: Dict) -> List[Dict]:
    # Replace with:
    response = requests.get(source.url, params=filters)
    return response.json()
```

### 2. Train ML Models

- Collect labeled data for scam detection
- Train classification model (sklearn, PyTorch)
- Export to TensorFlow Lite for mobile
- Update `listing_analysis_agent.py` to use trained model

### 3. Integrate Firebase

Update `config.py` with Firebase credentials and implement:
- User authentication
- Firestore for storing listings, matches, user profiles
- Cloud Storage for images

### 4. Add Real Transit Data

Fetch GTFS data in `data_ingestion_agent.py`:

```python
import gtfs_kit as gk

feed = gk.read_feed('path/to/gtfs.zip', dist_units='km')
stops = feed.stops
routes = feed.routes
```

### 5. Deploy to Cloud

```bash
# Deploy backend to Google Cloud Functions
gcloud functions deploy rentconnect-orchestrator \
  --runtime python39 \
  --trigger-http \
  --allow-unauthenticated

# Or deploy to Vercel
vercel deploy
```

### 6. Build Mobile App

```bash
# Build for iOS
expo build:ios

# Build for Android
expo build:android
```

## Testing

### Run Unit Tests

```bash
pytest tests/ -v --cov=src
```

### Run Integration Tests

```bash
pytest tests/integration/ -v
```

### Lint Code

```bash
# Python
black src/
flake8 src/

# JavaScript
npm run lint
```

## Documentation

- **README.md** - Project overview and setup
- **ARCHITECTURE.md** - System architecture and design
- **API_DOCS.md** - API endpoints (create this next)
- **CONTRIBUTING.md** - Contribution guidelines (create this next)

## Support

For issues:
1. Check documentation
2. Search existing issues
3. Create new issue with reproduction steps

## Development Workflow

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes and test locally
3. Run tests: `pytest tests/`
4. Commit: `git commit -m "Add your feature"`
5. Push: `git push origin feature/your-feature`
6. Create Pull Request

## Performance Tips

- Enable caching in `config.py` (`PERFORMANCE_CONFIG['cache_enabled'] = True`)
- Use batch processing for large datasets
- Deploy models to edge (TensorFlow Lite) for mobile inference
- Implement Redis for frequent queries
- Use Cloud Functions for serverless scaling

## Monitoring

Check agent performance:

```python
from src.agents.orchestration.orchestration_agent import OrchestrationAgent

orchestrator = OrchestrationAgent()
status = orchestrator.get_agent_status()
print(status)
# {'data_ingestion': 'active', 'knowledge_graph': 'active', ...}
```

---

**You're all set! 🚀**

Start with `python main.py` to see the agents in action, then customize for your use case.
