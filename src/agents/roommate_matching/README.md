# Roommate Matching Agent

## Description
Autonomous agent that performs stable matching between roommate seekers with constraint satisfaction and fairness guarantees. Uses a Gale-Shapley variant algorithm to ensure no two people prefer each other over their assigned matches while respecting hard constraints (smoking, pets, quiet hours, budget) and optimizing soft preferences (personality, cleanliness, social level).

## Autonomy Level
**High**: Makes final matching decisions without human intervention for normal cases. Requests human review for matches below quality threshold (< 0.5 compatibility).

## Decision Authority
- Match two or more people into roommate groups
- Reject candidates that violate hard constraints
- Optimize group compositions for multi-bedroom units
- Trigger fairness audits when variance exceeds threshold

## Input Streams
1. **Survey Data** (from `SurveyIngestion` preprocessing):
   - User profiles with constraints and preferences
   - Personality scores (Big Five: OCEAN)
   - Budget ranges and location preferences
   - Hard constraints (binary: smoking, pets, quiet hours)
   - Soft preferences (weighted: cleanliness, social level, schedule)

2. **Listing Context** (from `listing_analyzer` tool):
   - Available multi-bedroom units
   - Unit capacities (2-4 bedrooms)
   - Lease requirements

3. **Configuration** (from `config.agents_config`):
   - Matching algorithm parameters
   - Weight distributions for preferences/personality
   - Fairness constraints (min match rate, max variance)
   - Group matching settings

## Output Streams
1. **Matches**:
   ```python
   {
       'match_id': str,
       'participants': [{'user_id': str, 'profile': dict}],
       'compatibility_score': float,  # 0-1, weighted overall
       'shared_constraints': dict,
       'personality_alignment': dict,
       'fairness_metrics': {
           'match_quality_rank': int,  # 1 = best match
           'variance_from_mean': float
       }
   }
   ```

2. **Explanations**:
   - Why these people were matched
   - What constraints they share
   - Personality compatibility breakdown
   - Alternative matches considered

3. **Fairness Report**:
   - Overall match rate (% of people matched)
   - Quality variance across demographic groups
   - Blocking pairs count (should be 0 for stable match)

## Usage Example
```python
from src.agents.roommate_matching import roommate_matching

# Process survey data
profiles = [
    {'user_id': 'u1', 'constraints': {...}, 'preferences': {...}},
    {'user_id': 'u2', 'constraints': {...}, 'preferences': {...}}
]

# Run matching
result = roommate_matching.match(profiles)

# Check stability
assert result['blocking_pairs'] == 0

# Review matches
for match in result['matches']:
    print(f"Match {match['match_id']}: {match['participants']}")
    print(f"Compatibility: {match['compatibility_score']:.2f}")
```

## C³AN Elements Implemented
- **Reasoning**: Constraint satisfaction problem solving
- **Planning**: Optimization of match quality across entire cohort
- **Alignment**: Fairness guarantees (match rate, quality distribution)
- **Explainability**: Match explanations with factor breakdowns
- **Safety**: FHA compliance (no discriminatory matching)
- **Composability**: Uses `SurveyIngestion` preprocessing and `knowledge_graph` tool

## Evaluation Metrics
See `evaluation.md` for detailed metric definitions and measurement methods.

## Configuration
See `config.py` for agent-specific settings (algorithm parameters, weights, fairness thresholds).
