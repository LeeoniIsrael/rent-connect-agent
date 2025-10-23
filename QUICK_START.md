# Quick Start Guide - Refactored System

## Installation
```bash
pip install -r requirements.txt
```

## Basic Usage

### 1. Data Ingestion (Preprocessing)
```python
from src.preprocessing import DataIngestion, SurveyIngestion

# Collect rental listings
data_ingestion = DataIngestion()
listings = data_ingestion.ingest_listings(
    location={'lat': 33.9937, 'lon': -81.0266},
    radius_km=5.0
)

# Process roommate surveys
survey_ingestion = SurveyIngestion()
profiles = survey_ingestion.process_survey(survey_data)
```

### 2. Analysis Tools
```python
from src.tools import listing_analyzer, compliance_checker, knowledge_graph

# Analyze listing for scams
risk_result = listing_analyzer.analyze_listing(listing)
print(f"Risk score: {risk_result['risk_score']}")

# Check compliance
compliance_result = compliance_checker.check_compliance(listing)
print(f"FHA compliant: {compliance_result['compliant']}")

# Query knowledge base
fha_rules = knowledge_graph.query_entities(entity_type='policy_rule')
```

### 3. Decision-Making Agents

#### Roommate Matching
```python
from src.agents import roommate_matching

# Match roommates
result = roommate_matching.match(profiles)

# Review matches
for match in result.matches:
    print(f"Match: {match['participants']}")
    print(f"Compatibility: {match['compatibility_score']:.2f}")
    print(f"Explanation: {result.explanations[match['match_id']]}")

# Check stability
print(f"Blocking pairs: {result.blocking_pairs}")  # Should be 0
```

#### Property Ranking
```python
from src.agents import ranking_scoring

# Define user preferences
user_prefs = {
    'weights': {
        'price': 0.35,
        'commute_time': 0.30,
        'safety_score': 0.20,
        'amenities_match': 0.10,
        'lease_suitability': 0.05
    },
    'hard_constraints': {
        'max_price': 1500,
        'max_commute': 45,
        'min_safety': 0.6
    }
}

# Rank properties
destination = (33.9937, -81.0266)  # USC campus
result = ranking_scoring.rank(listings, user_prefs, destination)

# Review top properties
for listing in result.ranked_listings[:5]:
    print(f"Rank {listing['rank']}: {listing['listing_id']}")
    print(f"Score: {listing['overall_score']:.2f}")
    print(f"Pareto optimal: {listing['is_pareto_optimal']}")
    print(f"Breakdown: {listing['score_breakdown']}")
```

#### Route Planning
```python
from src.agents import route_planning

# Select properties to visit
properties_to_visit = [
    {'listing_id': 'p1', 'latitude': 33.99, 'longitude': -81.03},
    {'listing_id': 'p2', 'latitude': 34.00, 'longitude': -81.02},
    {'listing_id': 'p3', 'latitude': 33.98, 'longitude': -81.04}
]

# Define class schedule
class_schedule = [
    {'start': '09:00', 'end': '10:30'},  # Morning class
    {'start': '14:00', 'end': '15:30'}   # Afternoon class
]

# Plan optimal tour
result = route_planning.plan_route(properties_to_visit, class_schedule)

# Review tour
print(f"Tour feasible: {result.feasible}")
print(f"Total duration: {result.total_duration} minutes")
for stop in result.stops:
    print(f"{stop['arrival_time']}: Visit {stop['listing_id']} (viewing: {stop['viewing_duration']} min)")
```

#### Feedback Learning
```python
from src.agents import feedback_learning

# User rates a recommendation
rating_feedback = {
    'feedback_id': 'fb1',
    'type': 'rating',
    'user_id': 'u1',
    'rating': 5,
    'context': {
        'listing_id': 'p1',
        'criteria_scores': {
            'price': 0.9,
            'commute_time': 0.8,
            'safety_score': 0.85
        }
    }
}

result = feedback_learning.process_feedback(rating_feedback)
print(f"Feedback applied: {result.applied}")
print(f"Impact: {result.impact_summary}")

# Expert correction
correction_feedback = {
    'feedback_id': 'fb2',
    'type': 'correction',
    'target': 'scam_detector',
    'listing_id': 'p2',
    'corrected_risk_score': 0.95,
    'expert_confidence': 0.90
}

result = feedback_learning.process_feedback(correction_feedback)
print(f"Correction applied: {result.applied}")

# Retrieve updated preferences
prefs = feedback_learning.get_user_preferences('u1')
print(f"Updated weights: {prefs['weights']}")
```

## Configuration

### Adjust Agent Settings
```python
# Edit config/agents_config.py to change default behaviors

# Example: Change ranking criteria weights
RANKING_SCORING_CONFIG = {
    'default_criteria_weights': {
        'price': 0.40,           # Increase price importance
        'commute_time': 0.25,
        'safety_score': 0.20,
        'amenities_match': 0.10,
        'lease_suitability': 0.05
    }
}

# Example: Change matching algorithm fairness threshold
ROOMMATE_MATCHING_CONFIG = {
    'fairness_constraints': {
        'min_match_rate': 0.85,      # Increase from 0.80
        'max_quality_variance': 0.12  # Decrease from 0.15 (stricter)
    }
}
```

### Adjust Tool Settings
```python
# Edit config/tools_config.py

# Example: Change scam detection threshold
LISTING_ANALYZER_CONFIG = {
    'risk_threshold': 0.7,  # Increase from 0.6 (stricter)
    'price_anomaly_threshold': 0.4  # Decrease from 0.5 (more sensitive)
}
```

## Complete Workflow Example

```python
from src.preprocessing import DataIngestion, SurveyIngestion
from src.tools import listing_analyzer, compliance_checker
from src.agents import roommate_matching, ranking_scoring, route_planning

# Step 1: Collect data
data_ingestion = DataIngestion()
listings = data_ingestion.ingest_listings(
    location={'lat': 33.9937, 'lon': -81.0266},
    radius_km=5.0
)

# Step 2: Analyze listings
analyzed_listings = []
for listing in listings:
    # Check for scams
    risk = listing_analyzer.analyze_listing(listing)
    if risk['risk_score'] < 0.7:  # Not high-risk
        # Check compliance
        compliance = compliance_checker.check_compliance(listing)
        if compliance['compliant']:
            listing['safety_score'] = compliance['safety_score']
            analyzed_listings.append(listing)

print(f"Filtered {len(analyzed_listings)} safe, compliant listings")

# Step 3: Rank properties
user_prefs = {'weights': {'price': 0.35, 'commute_time': 0.30, 'safety_score': 0.35}}
ranked = ranking_scoring.rank(analyzed_listings, user_prefs, destination=(33.9937, -81.0266))

# Step 4: Select top properties for tour
top_5 = ranked.ranked_listings[:5]

# Step 5: Plan viewing tour
properties_to_visit = [
    {'listing_id': p['listing_id'], 'latitude': p['latitude'], 'longitude': p['longitude']}
    for p in top_5
]
class_schedule = [{'start': '09:00', 'end': '10:30'}, {'start': '14:00', 'end': '15:30'}]
tour = route_planning.plan_route(properties_to_visit, class_schedule)

print(f"Tour planned: {len(tour.stops)} stops, feasible={tour.feasible}")

# Step 6: Process roommate surveys (parallel workflow)
survey_ingestion = SurveyIngestion()
survey_data = [...]  # User survey responses
profiles = [survey_ingestion.process_survey(s) for s in survey_data]

# Match roommates
matches = roommate_matching.match(profiles)
print(f"Created {len(matches.matches)} roommate matches")
```

## Testing

### Unit Tests
```python
# Test preprocessing
from src.preprocessing import DataIngestion

data_ingestion = DataIngestion()
listings = data_ingestion.ingest_listings({'lat': 33.9937, 'lon': -81.0266}, 5.0)
assert len(listings) > 0, "Should return listings"

# Test tools
from src.tools import listing_analyzer

result = listing_analyzer.analyze_listing({'price': 500, 'description': 'Great apartment'})
assert 0 <= result['risk_score'] <= 1, "Risk score should be 0-1"

# Test agents
from src.agents import ranking_scoring

listings = [{'listing_id': 'p1', 'price': 1000, 'latitude': 33.99, 'longitude': -81.03}]
result = ranking_scoring.rank(listings)
assert len(result.ranked_listings) > 0, "Should return ranked listings"
```

### Integration Tests
```python
# Full pipeline test
from src.preprocessing import DataIngestion
from src.tools import listing_analyzer
from src.agents import ranking_scoring

# Ingest
listings = DataIngestion().ingest_listings({'lat': 33.9937, 'lon': -81.0266}, 5.0)

# Analyze
for listing in listings:
    risk = listing_analyzer.analyze_listing(listing)
    listing['risk_score'] = risk['risk_score']

# Rank
result = ranking_scoring.rank(listings, destination=(33.9937, -81.0266))
assert len(result.ranked_listings) > 0, "End-to-end should work"
```

## Troubleshooting

### Import Errors
```python
# If you get import errors, ensure you're running from project root:
import sys
sys.path.append('/path/to/rent-connect-agent')

# Or install as package:
pip install -e .
```

### Configuration Not Found
```python
# Ensure config/ is in Python path
from config import RANKING_SCORING_CONFIG
print(RANKING_SCORING_CONFIG)
```

### Agents Not Making Decisions
```python
# Check if data has required fields
listing = {'listing_id': 'p1', 'price': 1000, 'latitude': 33.99, 'longitude': -81.03}
# Missing fields may cause silent failures - check logs

# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Next Steps

1. **Connect Real Data**: Update `preprocessing_config.py` with API credentials
2. **Train Models**: Replace placeholder scam detection with trained classifier
3. **Deploy**: Set up Firebase backend and Cloud Functions
4. **Monitor**: Use evaluation metrics to track system performance

## Documentation

- **Architecture**: See `ARCHITECTURE.md`
- **Agents**: See `AGENTS.md` (to be updated)
- **Refactoring**: See `REFACTORING_GUIDE.md`
- **Implementation**: See `IMPLEMENTATION_SUMMARY.md`
- **Per-Agent Docs**: See `src/agents/<agent_name>/README.md`

---

**Happy Coding!** 🚀
