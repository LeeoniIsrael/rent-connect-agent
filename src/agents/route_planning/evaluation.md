# Route Planning Agent - Evaluation Metrics

## C³AN Foundation Elements

### 1. Planning (Constrained Optimization)
**Metric**: **Time Window Compliance Rate**
- **Definition**: Percentage of scheduled viewings that fit within available time windows
- **Target**: 100% (mandatory - no conflicts with classes)
- **Measurement**: Count violations where viewing overlaps with class
- **Formula**: `(total_viewings - violations) / total_viewings`
- **Why it matters**: Agent must respect user's class schedule constraints

### 2. Reasoning (Scheduling Logic)
**Metric**: **Route Optimality**
- **Definition**: Percentage improvement over random ordering
- **Target**: ≥ 30% reduction in total travel time vs. random
- **Measurement**: Compare agent's route with random permutations
- **Formula**: `(random_time - agent_time) / random_time`
- **Why it matters**: Better routes save time and reduce fatigue

**Metric**: **Optimal TSP Gap**
- **Definition**: Percentage difference from true optimal TSP solution
- **Target**: ≤ 20% (nearest-neighbor is approximate algorithm)
- **Measurement**: Compare with exact TSP solver (for small instances)
- **Formula**: `(agent_solution - optimal_solution) / optimal_solution`
- **Why it matters**: Measures solution quality for algorithmic improvements

### 3. Grounding (Real-World Feasibility)
**Metric**: **Tour Completion Rate**
- **Definition**: Percentage of requested viewings successfully scheduled
- **Target**: ≥ 80%
- **Measurement**: `scheduled_viewings / requested_viewings`
- **Formula**: Count viewings that fit in available time
- **Why it matters**: Low completion means schedule too tight or algorithm ineffective

### 4. Explainability (Decision Transparency)
**Metric**: **Explanation Completeness**
- **Definition**: Percentage of route decisions with documented rationale
- **Target**: 100%
- **Measurement**: Check if each stop has arrival time, travel justification, window assignment
- **Formula**: `stops_with_complete_explanation / total_stops`
- **Why it matters**: Users need to understand why certain order was chosen

### 5. Composability (Integration Quality)
**Metric**: **Travel Time Accuracy**
- **Definition**: Accuracy of travel time estimates used in planning
- **Target**: MAE ≤ 5 minutes (when using real APIs)
- **Measurement**: Compare planned vs. actual travel times
- **Formula**: `mean(|planned_time - actual_time|)`
- **Why it matters**: Inaccurate estimates cause schedule violations

## Domain-Specific Metrics

### Schedule Efficiency
**Metric**: **Time Utilization Rate**
- **Purpose**: Measure how well agent uses available time
- **Measurement**: `(viewing_time + travel_time) / available_time`
- **Target**: 0.60 - 0.85 (60-85% utilization)
- **Why it matters**: Too low = wasted time, too high = no buffer for delays

**Metric**: **Buffer Adequacy**
- **Purpose**: Ensure adequate time between viewings
- **Measurement**: Percentage of transitions with ≥ MIN_BREAK_DURATION buffer
- **Target**: ≥ 90%
- **Why it matters**: Tight schedules stress users and cause missed appointments

### Robustness
**Metric**: **Feasibility Rate**
- **Purpose**: Percentage of tour requests that produce feasible schedules
- **Measurement**: `feasible_tours / total_tour_requests`
- **Target**: ≥ 85%
- **Why it matters**: Frequent infeasibility frustrates users

**Metric**: **Delay Tolerance**
- **Purpose**: How much delay can tour absorb before schedule violation
- **Measurement**: Minimum delay (minutes) to cause time window violation
- **Target**: ≥ 15 minutes slack
- **Why it matters**: Real-world delays are inevitable

### Multi-Day Planning
**Metric**: **Day Distribution Quality**
- **Purpose**: When splitting across multiple days, measure load balance
- **Measurement**: Std dev of viewings per day
- **Target**: ≤ 1.5 (fairly balanced)
- **Why it matters**: Avoid exhausting days followed by empty days

## Performance Metrics

### Computational Efficiency
- **Metric**: Planning time for N stops
- **Target**: < 1 second for 10 stops, < 5 seconds for 20 stops
- **Measurement**: Log execution time

### Algorithm Complexity
- **Metric**: Scaling behavior
- **Expected**: O(N²) for nearest-neighbor TSP
- **Measurement**: Plot runtime vs. N

## Safety & User Experience Metrics

### HITL Trigger Rate
- **Metric**: Percentage of tours requiring human confirmation
- **Target**: 10-20% (tight schedules only)
- **Measurement**: Count tours with buffer < 15 minutes

### User Satisfaction
- **Metric**: Post-tour feedback ratings
- **Target**: ≥ 4.0 / 5.0 stars
- **Collection**: Survey after tour completion

## Evaluation Workflow

### 1. Unit Tests
- Test time window overlap detection
- Test nearest-neighbor algorithm
- Test travel time calculation
- Test feasibility checking

### 2. Integration Tests
- End-to-end: properties + schedule → route
- Test with 3, 5, 10, 15 stops
- Test with varying class schedules (sparse, dense)

### 3. Simulation Testing
- Inject random delays (5-15 min) to test robustness
- Test multi-day scenarios
- Test with real USC class schedules

### 4. A/B Testing (Production)
- Compare user satisfaction vs. baseline (manual scheduling)
- Measure tour completion rate (did they visit all properties?)
- Track no-show rate (indication of bad scheduling)

## Red Flags (Triggers for Investigation)
1. **Time Window Violations > 0**: Critical bug - must respect schedule
2. **Completion Rate < 70%**: Algorithm too conservative or poor heuristic
3. **Buffer Adequacy < 80%**: Schedules too tight, risking delays
4. **TSP Gap > 50%**: Algorithm performing poorly, consider better heuristic
5. **HITL Rate > 30%**: Too many marginal schedules, tighten feasibility checks

## Reporting Dashboard
- **Real-time**: Current tour plan for active users
- **Daily**: Completion rate, time window compliance, buffer adequacy
- **Weekly**: Route optimality trend, user satisfaction
- **Monthly**: Algorithm performance audit (TSP gap), delay tolerance analysis

## Improvement Strategies
- **For low route optimality**: Use 2-opt or genetic algorithms instead of nearest-neighbor
- **For low completion rate**: Suggest fewer viewings or more available time
- **For tight buffers**: Increase MIN_BREAK_DURATION or reduce MAX_STOPS_PER_DAY
- **For GTFS integration**: Use real-time transit schedules to improve accuracy
