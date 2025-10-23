# Route Planning Agent

## Description
Autonomous agent that plans optimal property viewing tours constrained by class schedules and time windows. Uses nearest-neighbor TSP heuristic to minimize travel time while respecting available time slots.

## Autonomy Level
**Medium**: Makes routing decisions autonomously but requests user confirmation for tight schedules (< 15 min buffer between viewings).

## Decision Authority
- Optimize visit sequence to minimize total travel time
- Schedule viewing times within available windows
- Reject infeasible tours (too many stops, insufficient time)
- Suggest alternative dates if schedule too tight

## Input Streams
1. **Property Selection** (from user):
   - List of listing IDs to visit
   - Property locations (lat, lon)
   
2. **Class Schedule** (from user):
   - Time blocks (start, end) where user is unavailable
   - Available windows for viewings
   
3. **Travel Estimates** (from ranking_scoring agent or Google Maps):
   - Travel times between properties
   - Transport mode (transit, drive, bike)

4. **Configuration** (from `config.agents_config`):
   - Default viewing duration (30 min)
   - Max stops per day
   - Travel time buffer

## Output Streams
1. **Optimized Route**:
   ```python
   {
       'tour_id': str,
       'date': str,
       'stops': [
           {
               'listing_id': str,
               'arrival_time': str,  # 'HH:MM'
               'departure_time': str,
               'viewing_duration': int,  # minutes
               'travel_to_next': int  # minutes
           }
       ],
       'total_duration': int,  # minutes
       'feasible': bool,
       'time_window_violations': int
   }
   ```

2. **Feasibility Report**:
   - Whether tour fits in available windows
   - Tight connections (< 15 min buffer)
   - Suggestions for improvement

3. **Explanations**:
   - Why this visit order
   - What time windows constrained the route

## Usage Example
```python
from src.agents.route_planning import route_planning

# Prepare input
properties_to_visit = [
    {'listing_id': 'p1', 'latitude': 33.99, 'longitude': -81.03},
    {'listing_id': 'p2', 'latitude': 34.00, 'longitude': -81.02}
]

class_schedule = [
    {'start': '09:00', 'end': '10:30'},  # Class 1
    {'start': '14:00', 'end': '15:30'}   # Class 2
]

# Plan route
result = route_planning.plan_route(properties_to_visit, class_schedule)

# Review tour
print(f"Feasible: {result['feasible']}")
for stop in result['stops']:
    print(f"{stop['arrival_time']}: Visit {stop['listing_id']}")
```

## C³AN Elements Implemented
- **Planning**: Constrained optimization (TSP with time windows)
- **Reasoning**: Scheduling constraints satisfaction
- **Grounding**: Real class schedules and travel times
- **Explainability**: Route rationale and alternative suggestions
- **Composability**: Uses ranking_scoring commute estimates

## Evaluation Metrics
See `evaluation.md` for detailed metric definitions.

## Configuration
See `config.py` for agent-specific settings (viewing duration, max stops, buffers).
