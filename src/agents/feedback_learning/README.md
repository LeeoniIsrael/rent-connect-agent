# Feedback & Learning Agent

## Description
Autonomous agent that learns from user and expert feedback to improve system recommendations over time. Processes ratings, corrections, and preference updates to adapt agent behaviors.

## Autonomy Level
**Medium**: Applies feedback automatically for low-risk updates (preference weights), requests expert review for high-impact changes (model corrections).

## Decision Authority
- Update user preference weights based on ratings
- Apply expert corrections to models (with verification)
- Detect preference drift and trigger re-profiling
- Reject low-confidence feedback (< 0.8 confidence score)

## Input Streams
1. **User Ratings** (explicit feedback):
   - Rating (1-5 stars) on recommendations
   - Feedback text (optional)
   - Context (what was rated: listing, match, route)

2. **Corrections** (expert feedback):
   - Error reports (scam not detected, price inaccurate, amenity missing)
   - Corrected values
   - Expert confidence score

3. **Implicit Feedback** (behavioral):
   - Click-through rates
   - Saved listings
   - Tour bookings
   - Time spent viewing

4. **Configuration** (from `config.agents_config`):
   - Learning rate
   - Minimum feedback threshold
   - Drift detection parameters

## Output Streams
1. **Updated Preferences**:
   ```python
   {
       'user_id': str,
       'old_weights': Dict[str, float],
       'new_weights': Dict[str, float],
       'confidence': float,
       'reason': str
   }
   ```

2. **Model Corrections**:
   ```python
   {
       'correction_id': str,
       'target': str,  # 'scam_detector', 'price_model', etc.
       'correction_type': str,
       'applied': bool,
       'impact_estimate': float
   }
   ```

3. **Drift Alerts**:
   - User preference changes detected
   - Suggest re-running survey
   - Explain what changed

## Usage Example
```python
from src.agents.feedback_learning import feedback_learning

# User rates a recommendation
rating_feedback = {
    'user_id': 'u1',
    'type': 'rating',
    'rating': 5,
    'context': {'listing_id': 'p1', 'rank': 2}
}

result = feedback_learning.process_feedback(rating_feedback)

# Expert corrects scam detection
correction_feedback = {
    'type': 'correction',
    'target': 'scam_detector',
    'listing_id': 'p2',
    'corrected_risk_score': 0.9,
    'expert_confidence': 0.95
}

result = feedback_learning.process_feedback(correction_feedback)
```

## C³AN Elements Implemented
- **Instructability**: Learns from user instructions (ratings, corrections)
- **Adaptability**: Adjusts to preference changes over time
- **Explainability**: Documents why changes were made
- **Safety**: Requires expert verification for high-impact corrections
- **Composability**: Updates other agents' parameters

## Evaluation Metrics
See `evaluation.md` for detailed metric definitions.

## Configuration
See `config.py` for agent-specific settings (learning rates, thresholds, drift detection).
