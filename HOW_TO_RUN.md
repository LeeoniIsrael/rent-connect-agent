# How to Run - Super Simple 🚀

## Quick Test (Verify Everything Works)

```bash
python test_system.py
```

This tests all 4 agents with mock data. You should see ✅ checkmarks for everything.

---

## Run Your Own Code

### 1. Match Roommates
```python
from src.agents import roommate_matching

profiles = [
    {
        'user_id': 'alice',
        'hard_constraints': {'smoking': False, 'has_pets': False, 'allows_pets': True, 
                            'quiet_hours': (22, 7), 'budget_range': (800, 1200)},
        'soft_preferences': {'cleanliness': 4, 'social_level': 3, 'schedule': 'flexible'},
        'personality': {'conscientiousness': 4, 'agreeableness': 4, 'extraversion': 3, 
                       'openness': 4, 'neuroticism': 2}
    },
    {
        'user_id': 'bob',
        'hard_constraints': {'smoking': False, 'has_pets': False, 'allows_pets': True, 
                            'quiet_hours': (23, 8), 'budget_range': (900, 1300)},
        'soft_preferences': {'cleanliness': 4, 'social_level': 3, 'schedule': 'flexible'},
        'personality': {'conscientiousness': 4, 'agreeableness': 5, 'extraversion': 4, 
                       'openness': 3, 'neuroticism': 2}
    }
]

result = roommate_matching.match(profiles)
print(f"Matches: {len(result.matches)}")
print(f"Compatibility: {result.matches[0]['compatibility_score']:.2f}")
```

### 2. Rank Properties
```python
from src.agents import ranking_scoring

listings = [
    {'listing_id': 'apt1', 'price': 1000, 'latitude': 33.99, 'longitude': -81.03,
     'safety_score': 0.8, 'amenities': ['parking', 'laundry'], 
     'lease_length_months': 12, 'security_deposit': 1000, 'bedrooms': 2},
    {'listing_id': 'apt2', 'price': 1200, 'latitude': 34.00, 'longitude': -81.02,
     'safety_score': 0.9, 'amenities': ['parking', 'laundry', 'gym'], 
     'lease_length_months': 12, 'security_deposit': 1200, 'bedrooms': 2}
]

destination = (33.9937, -81.0266)  # USC campus
result = ranking_scoring.rank(listings, destination=destination)

print(f"Top property: {result.ranked_listings[0]['listing_id']}")
print(f"Score: {result.ranked_listings[0]['overall_score']:.2f}")
```

### 3. Analyze a Listing for Scams
```python
from src.tools import listing_analyzer

listing = {
    'listing_id': 'test1',
    'price': 500,  # Suspiciously low
    'description': 'Amazing apartment! Wire transfer only, must act NOW!',
    'contact_info': 'Out of country, email only'
}

result = listing_analyzer.analyze_listing(listing)
print(f"Risk score: {result['risk_score']:.2f}")
print(f"Risk flags: {result['risk_flags']}")
```

### 4. Check FHA Compliance
```python
from src.tools import compliance_checker

listing = {
    'listing_id': 'test1',
    'description': 'Great apartment near campus',
    'landlord_id': 'landlord1'
}

result = compliance_checker.check_compliance(listing)
print(f"Compliant: {result['compliant']}")
print(f"Safety score: {result['safety_score']:.2f}")
```

---

## Create Your Own Script

Create a file `my_test.py`:

```python
from src.agents import roommate_matching, ranking_scoring

# Your code here...
```

Run it:
```bash
python my_test.py
```

---

## File Structure

```
rent-connect-agent/
├── src/
│   ├── preprocessing/    # Data collection modules
│   ├── tools/            # Analysis tools (singletons)
│   └── agents/           # 4 decision-making agents
├── config/               # All configuration files
├── test_system.py        # Run this to test everything
├── QUICK_START.md        # Detailed examples
└── HOW_TO_RUN.md         # This file (super simple guide)
```

---

## That's It! 🎉

You now have:
- ✅ 4 working agents (roommate matching, ranking, route planning, feedback learning)
- ✅ 4 analysis tools (knowledge graph, listing analyzer, image analyzer, compliance checker)
- ✅ 2 preprocessing modules (data ingestion, survey ingestion)
- ✅ Clean, documented code with C³AN metrics

**Just run**: `python test_system.py` to verify everything works!
