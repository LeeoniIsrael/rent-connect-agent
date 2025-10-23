# Ranking & Scoring Agent

## Description
Autonomous agent that ranks rental properties using multi-objective optimization with user-tunable weights. Identifies Pareto-optimal (non-dominated) listings where no other property is better in all criteria. Provides transparent score breakdowns for explainability.

## Autonomy Level
**High**: Makes final ranking decisions with user-provided weights. Requests human review for properties with extreme scores (e.g., suspiciously low price + high scam risk).

## Decision Authority
- Rank properties by weighted multi-criteria score
- Identify Pareto-optimal listings
- Filter out non-viable options (hard constraint violations)
- Trigger alerts for anomalous properties

## Input Streams
1. **Listing Data** (from `DataIngestion` preprocessing):
   - Property details (price, location, amenities, lease terms)
   - Cleaned and deduplicated records
   - Market rate context (ZORI data)

2. **Analysis Results** (from tools):
   - Risk scores (from `listing_analyzer`)
   - Compliance status (from `compliance_checker`)
   - Safety scores (from `compliance_checker`)
   - Commute times (computed internally or from external API)

3. **User Preferences**:
   - Criteria weights (price, commute, safety, amenities, lease)
   - Hard constraints (max price, max commute, min safety)
   - Priority destination (campus, workplace)

4. **Configuration** (from `config.agents_config`):
   - Default criteria weights
   - Commute mode parameters
   - Pareto optimality detection settings

## Output Streams
1. **Ranked Listings**:
   ```python
   {
       'listing_id': str,
       'overall_score': float,  # 0-1, weighted combination
       'rank': int,
       'is_pareto_optimal': bool,
       'criteria_scores': {
           'price': float,
           'commute_time': float,
           'safety_score': float,
           'amenities_match': float,
           'lease_suitability': float
       },
       'score_breakdown': str  # Explanation
   }
   ```

2. **Pareto Frontier**:
   - List of non-dominated property IDs
   - Trade-off explanations ("Property A has better price but worse commute than Property B")

3. **Explanations**:
   - Why top properties ranked highly
   - What criteria each property excels/struggles in
   - Trade-off analysis

## Usage Example
```python
from src.agents.ranking_scoring import ranking_scoring

# Prepare input
listings = [...]  # From DataIngestion
user_preferences = {
    'weights': {'price': 0.4, 'commute_time': 0.3, 'safety_score': 0.3},
    'hard_constraints': {'max_price': 1500, 'max_commute': 45}
}

# Run ranking
result = ranking_scoring.rank(listings, user_preferences)

# Review top listings
for listing in result.ranked_listings[:10]:
    print(f"Rank {listing['rank']}: {listing['listing_id']} (score: {listing['overall_score']:.2f})")
    print(f"Pareto optimal: {listing['is_pareto_optimal']}")
    print(f"Breakdown: {listing['score_breakdown']}")
```

## C³AN Elements Implemented
- **Reasoning**: Multi-objective optimization
- **Instructability**: User-tunable weights
- **Explainability**: Score breakdowns and trade-off analysis
- **Grounding**: Real market data (ZORI, commute times)
- **Composability**: Uses `DataIngestion`, `listing_analyzer`, `compliance_checker`

## Evaluation Metrics
See `evaluation.md` for detailed metric definitions.

## Configuration
See `config.py` for agent-specific settings (default weights, commute parameters).
