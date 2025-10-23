# Feedback & Learning Agent - Evaluation Metrics

## C³AN Foundation Elements

### 1. Instructability (Learning from Feedback)
**Metric**: **Incorporation Rate**
- **Definition**: Percentage of feedback successfully incorporated into system
- **Target**: ≥ 90% for valid feedback
- **Measurement**: `applied_feedback / total_valid_feedback`
- **Formula**: Count feedback items that updated models/preferences
- **Why it matters**: System must respond to user instructions

### 2. Adaptability (Preference Evolution)
**Metric**: **Improvement Rate**
- **Definition**: Percentage increase in user satisfaction after feedback integration
- **Target**: ≥ 10% improvement over baseline
- **Measurement**: Compare satisfaction before/after feedback period
- **Formula**: `(satisfaction_after - satisfaction_before) / satisfaction_before`
- **Why it matters**: Validates that learning improves recommendations

### 3. Explainability (Feedback Impact)
**Metric**: **Change Attribution**
- **Definition**: Percentage of system changes traceable to specific feedback
- **Target**: 100%
- **Measurement**: Each parameter change has logged feedback source
- **Formula**: `changes_with_attribution / total_changes`
- **Why it matters**: Users need to understand why system behavior changed

### 4. Safety (Correction Validation)
**Metric**: **Expert Verification Rate**
- **Definition**: Percentage of high-impact corrections reviewed by experts
- **Target**: 100% for corrections with impact > 0.5
- **Measurement**: Count corrections requiring/receiving expert review
- **Formula**: `expert_reviewed_corrections / high_impact_corrections`
- **Why it matters**: Prevents malicious or erroneous feedback from harming system

### 5. Composability (Multi-Agent Updates)
**Metric**: **Cross-Agent Propagation**
- **Definition**: Success rate of feedback updates across dependent agents
- **Target**: ≥ 95%
- **Measurement**: Track if preference changes reach all affected agents
- **Formula**: `successful_propagations / total_propagations`
- **Why it matters**: Feedback must update entire system, not just one agent

## Domain-Specific Metrics

### Feedback Quality
**Metric**: **Signal-to-Noise Ratio**
- **Purpose**: Distinguish actionable feedback from random noise
- **Measurement**: Variance of feedback vs. variance of random baseline
- **Target**: SNR ≥ 2.0
- **Why it matters**: Low SNR means feedback is unreliable or users inconsistent

**Metric**: **Confidence Distribution**
- **Purpose**: Ensure feedback has adequate confidence scores
- **Measurement**: Histogram of feedback confidence scores
- **Target**: Median confidence ≥ 0.70
- **Why it matters**: Low-confidence feedback should not drive changes

### Preference Drift Detection
**Metric**: **Drift Detection Latency**
- **Definition**: Time (feedback items) to detect significant preference change
- **Target**: ≤ 20 feedback items (window size)
- **Measurement**: Count items from change to detection
- **Formula**: Use sliding window variance detection
- **Why it matters**: Faster detection = quicker adaptation

**Metric**: **False Positive Rate (Drift)**
- **Definition**: Percentage of drift alerts that are false alarms
- **Target**: ≤ 10%
- **Measurement**: Track alerts where user confirms no preference change
- **Why it matters**: Too many false alarms reduce trust

### Learning Effectiveness
**Metric**: **Weight Convergence**
- **Purpose**: Measure how quickly preferences stabilize
- **Measurement**: Rate of change in preference weights over time
- **Target**: Exponential decay (rapid initial learning, then stabilization)
- **Why it matters**: Weights should converge, not oscillate indefinitely

**Metric**: **Correction Impact**
- **Purpose**: Measure how much corrections improve model accuracy
- **Measurement**: Error rate before/after correction
- **Target**: ≥ 20% error reduction for addressed issues
- **Why it matters**: Validates corrections are effective

## Performance Metrics

### Feedback Processing Latency
- **Metric**: Time from feedback submission to system update
- **Target**: < 1 second for ratings, < 5 seconds for corrections
- **Measurement**: Log processing time

### Storage Efficiency
- **Metric**: Feedback database size growth rate
- **Target**: Linear growth (efficient storage)
- **Measurement**: Bytes per feedback item

## Safety & Validation Metrics

### Rejection Rate
- **Metric**: Percentage of feedback rejected (low confidence, contradictory)
- **Target**: 5-15% (some filtering necessary, but not excessive)
- **Measurement**: `rejected_feedback / total_feedback`

### Rollback Rate
- **Metric**: Percentage of applied changes later rolled back
- **Target**: < 2% (rare)
- **Measurement**: Count parameter rollbacks
- **Why it matters**: High rollback rate indicates poor feedback quality or validation

## Evaluation Workflow

### 1. Unit Tests
- Test rating aggregation logic
- Test preference weight updates
- Test drift detection algorithm
- Test correction application

### 2. Integration Tests
- End-to-end: feedback → updated agents
- Test with 10, 50, 100 feedback items
- Verify propagation to dependent agents

### 3. Simulation Testing
- Inject synthetic feedback patterns (drift, noise)
- Test drift detection sensitivity
- Validate learning rate convergence

### 4. A/B Testing (Production)
- Compare users with/without feedback learning enabled
- Measure satisfaction improvement
- Track system stability (no degradation from bad feedback)

## Red Flags (Triggers for Investigation)
1. **Incorporation Rate < 80%**: System not applying feedback, check validation logic
2. **Improvement Rate < 0%**: Feedback making recommendations worse, review feedback quality
3. **Expert Verification < 100%**: High-impact changes bypassing safety checks
4. **Drift False Positive > 20%**: Detection too sensitive, tune threshold
5. **Rollback Rate > 5%**: Poor feedback validation or malicious users

## Reporting Dashboard
- **Real-time**: Feedback queue length, processing latency
- **Daily**: Incorporation rate, preference weight changes
- **Weekly**: Improvement rate, drift detections
- **Monthly**: Correction impact analysis, expert review audit

## User Experience Metrics

### Feedback Participation Rate
- **Metric**: Percentage of users providing feedback
- **Target**: ≥ 30% active participation
- **Measurement**: `users_providing_feedback / total_active_users`

### Perceived Responsiveness
- **Metric**: User perception that system "learns" from them
- **Target**: ≥ 4.0 / 5.0 on survey question
- **Collection**: Post-interaction survey

## Long-Term Learning Metrics

### Cumulative Improvement
- **Metric**: Satisfaction trajectory over 6 months
- **Target**: Monotonically increasing (or flat if already optimal)
- **Measurement**: Plot mean satisfaction over time

### Population-Level Trends
- **Metric**: Aggregate preference shifts (e.g., safety becoming more important)
- **Purpose**: Update default weights to match population
- **Measurement**: Analyze mean weights across all users quarterly
