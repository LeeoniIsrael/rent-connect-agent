# Roommate Matching Agent - Evaluation Metrics

## C³AN Foundation Elements

### 1. Reasoning (Constraint Satisfaction)
**Metric**: **Hard Constraint Satisfaction Rate**
- **Definition**: Percentage of hard constraints (smoking, pets, quiet hours, budget) satisfied in final matches
- **Target**: 100% (mandatory)
- **Measurement**: Count constraint violations in matched pairs
- **Formula**: `(total_constraints - violations) / total_constraints`
- **Why it matters**: Ensures no incompatible roommates are matched (e.g., smoker with non-smoker)

### 2. Planning (Multi-Objective Optimization)
**Metric**: **Stability Score**
- **Definition**: Percentage of matches with zero blocking pairs (no two people prefer each other over their assigned matches)
- **Target**: ≥ 95%
- **Measurement**: Run blocking pair detection algorithm after matching
- **Formula**: `matches_with_no_blocking_pairs / total_matches`
- **Why it matters**: Stable matches are less likely to dissolve, reducing churn

### 3. Alignment (Fairness)
**Metric**: **Fairness Score (Match Quality Variance)**
- **Definition**: Standard deviation of compatibility scores across all matches, normalized
- **Target**: ≤ 0.15 (low variance = fair distribution)
- **Measurement**: Calculate std dev of all match scores
- **Formula**: `std_dev(compatibility_scores) / mean(compatibility_scores)`
- **Why it matters**: Prevents some users getting great matches while others get poor ones

**Metric**: **Match Rate**
- **Definition**: Percentage of participants who are successfully matched
- **Target**: ≥ 80%
- **Measurement**: `matched_users / total_users`
- **Why it matters**: High unmatch rate indicates algorithm failure or insufficient pool

### 4. Explainability (Decision Transparency)
**Metric**: **Explanation Completeness**
- **Definition**: Percentage of match decisions with full factor breakdowns (constraints + preferences + personality)
- **Target**: 100%
- **Measurement**: Check if each match includes all explanation components
- **Formula**: `matches_with_complete_explanations / total_matches`
- **Why it matters**: Users need to understand why they were paired with someone

### 5. Composability (Integration Quality)
**Metric**: **Data Flow Success Rate**
- **Definition**: Percentage of surveys successfully processed through entire pipeline (SurveyIngestion → Agent)
- **Target**: ≥ 98%
- **Measurement**: Track survey processing failures
- **Formula**: `successful_surveys / total_surveys`
- **Why it matters**: Agent depends on clean preprocessing data

## Domain-Specific Metrics

### Compatibility Score Distribution
- **Purpose**: Ensure matches are high-quality, not just stable
- **Measurement**: Mean and median compatibility scores
- **Target**: Mean ≥ 0.65, Median ≥ 0.70
- **Histogram Analysis**: Most matches should be in 0.6-0.9 range

### Group Matching Success (Multi-Bedroom)
- **Purpose**: Measure agent's ability to form 3-4 person groups
- **Measurement**: Success rate for group requests
- **Target**: ≥ 70% of group requests filled
- **Formula**: `successful_group_matches / group_match_requests`

### Personality Alignment
- **Purpose**: Assess Big Five compatibility in matches
- **Measurement**: Average personality score difference within matches
- **Target**: ≤ 1.5 points (on 5-point scale) across all Big Five dimensions
- **Why it matters**: Personality mismatches cause friction even if preferences align

## Performance Metrics

### Computational Efficiency
- **Metric**: Time to match N users
- **Target**: O(N²) complexity, < 5 seconds for 100 users
- **Measurement**: Log execution time

### Memory Usage
- **Metric**: Peak memory during matching
- **Target**: < 500 MB for 1000 users
- **Measurement**: Memory profiler

## Safety & Compliance Metrics

### FHA Compliance Rate
- **Metric**: Percentage of matches checked for discriminatory patterns
- **Target**: 100% (mandatory)
- **Measurement**: Verify no protected class preferences influenced matches
- **Audit Trail**: Log all constraint checks

### Human Review Trigger Rate
- **Metric**: Percentage of matches requiring human review (compatibility < 0.5)
- **Target**: < 5% (low-quality matches should be rare)
- **Measurement**: Count HITL triggers

## Evaluation Workflow

### 1. Unit Tests
- Test constraint satisfaction logic
- Test personality scoring
- Test fairness calculation
- Test blocking pair detection

### 2. Integration Tests
- End-to-end: surveys → matches
- Test with 10, 50, 100, 500 users
- Verify fairness across demographic groups

### 3. A/B Testing (Production)
- Compare match stability vs. baseline
- Measure user satisfaction (post-match surveys)
- Track roommate arrangement longevity

### 4. Fairness Audits
- Stratify by protected classes (anonymized)
- Ensure no statistical discrimination
- Generate fairness reports quarterly

## Red Flags (Triggers for Investigation)
1. **Hard Constraint Violations**: Any violation = critical bug
2. **Match Rate < 70%**: Algorithm tuning needed or insufficient data
3. **Fairness Score > 0.20**: Some users getting systematically worse matches
4. **Stability Score < 90%**: Blocking pairs indicate poor optimization
5. **Human Review Rate > 10%**: Too many low-quality matches

## Reporting Dashboard
- **Real-time**: Current match rate, stability score
- **Daily**: Compatibility score histogram, fairness variance
- **Weekly**: Trend analysis, A/B test results
- **Quarterly**: Fairness audit report, FHA compliance report
