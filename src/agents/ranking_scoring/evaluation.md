# Ranking & Scoring Agent - Evaluation Metrics

## C³AN Foundation Elements

### 1. Reasoning (Multi-Objective Optimization)
**Metric**: **Pareto Efficiency Rate**
- **Definition**: Percentage of top-N recommendations that are Pareto-optimal (non-dominated)
- **Target**: ≥ 70% of top-10 should be on Pareto frontier
- **Measurement**: Count non-dominated listings in top-N
- **Formula**: `pareto_optimal_in_top_N / N`
- **Why it matters**: Ensures diverse, high-quality recommendations (not all optimizing same criterion)

### 2. Instructability (Preference Alignment)
**Metric**: **Weight Correlation Score**
- **Definition**: Correlation between user weights and actual ranking outcomes
- **Target**: Pearson r ≥ 0.80
- **Measurement**: Correlate user's weight vector with score component magnitudes in top results
- **Formula**: `pearson_correlation(user_weights, score_contributions)`
- **Why it matters**: Agent must respect user preferences, not impose its own

### 3. Explainability (Decision Transparency)
**Metric**: **Score Attributability**
- **Definition**: Percentage of overall score that can be traced to specific criteria
- **Target**: 100% (all score components documented)
- **Measurement**: Verify each listing has complete score breakdown
- **Formula**: `sum(criteria_scores * weights) == overall_score`
- **Why it matters**: Users must understand why a property ranked highly

### 4. Grounding (Real-World Accuracy)
**Metric**: **Commute Time Accuracy**
- **Definition**: Mean absolute error between estimated and actual commute times
- **Target**: ≤ 5 minutes (when using real-time APIs)
- **Measurement**: Compare agent estimates with Google Maps API
- **Formula**: `mean(|estimated_time - actual_time|)`
- **Why it matters**: Inaccurate commute estimates lead to bad decisions

**Metric**: **Price Normalization Accuracy**
- **Definition**: Correlation between agent's price scores and market-adjusted prices
- **Target**: r ≥ 0.90
- **Measurement**: Compare agent's price scoring with ZORI-adjusted prices
- **Why it matters**: Must account for market variations (downtown vs. suburbs)

### 5. Composability (Integration Quality)
**Metric**: **Tool Integration Success Rate**
- **Definition**: Percentage of listings with complete analysis (risk, compliance, safety)
- **Target**: ≥ 98%
- **Measurement**: Check if all tool outputs are present
- **Formula**: `listings_with_complete_analysis / total_listings`
- **Why it matters**: Agent depends on tool outputs for accurate ranking

## Domain-Specific Metrics

### Ranking Quality
**Metric**: **Top-K Diversity**
- **Purpose**: Ensure top recommendations aren't too similar
- **Measurement**: Average pairwise distance (in feature space) among top-K
- **Target**: ≥ 0.5 (normalized Euclidean distance)
- **Why it matters**: Users want options, not 10 identical apartments

**Metric**: **User Satisfaction Correlation**
- **Purpose**: Validate rankings match real user choices
- **Measurement**: Correlation between agent's rank and user's actual selection
- **Target**: Spearman ρ ≥ 0.70
- **Collection Method**: Track which listings users click/save/tour

### Commute Scoring
**Metric**: **Multi-Modal Coverage**
- **Purpose**: Ensure all transport modes are considered
- **Measurement**: Percentage of rankings using best mode (not just defaulting to one)
- **Target**: ≥ 90% select optimal mode
- **Why it matters**: Walking might be better than transit for some locations

### Anomaly Detection
**Metric**: **HITL Trigger Accuracy**
- **Purpose**: Validate when agent requests human review
- **Measurement**: Precision/recall of anomaly detection
- **Target**: Precision ≥ 0.80, Recall ≥ 0.70
- **Why it matters**: Too many false positives annoy users, too many misses allow scams

## Performance Metrics

### Computational Efficiency
- **Metric**: Ranking latency for N listings
- **Target**: < 500ms for 100 listings, < 2s for 1000 listings
- **Measurement**: Log execution time

### Memory Usage
- **Metric**: Peak memory during ranking
- **Target**: < 200 MB for 1000 listings
- **Measurement**: Memory profiler

## Safety & Compliance Metrics

### Risk Filter Effectiveness
- **Metric**: Percentage of high-risk listings (risk > 0.7) filtered out
- **Target**: 100% (none should appear in top-50)
- **Measurement**: Check risk scores in ranked results

### Compliance Integration
- **Metric**: Percentage of non-compliant listings flagged
- **Target**: 100% (automatic pass-through from compliance_checker)
- **Measurement**: Verify compliance status is preserved

## Evaluation Workflow

### 1. Unit Tests
- Test score normalization (each criterion 0-1)
- Test weight application (sum to 1.0)
- Test Pareto frontier detection
- Test commute time calculation

### 2. Integration Tests
- End-to-end: listings → ranked results
- Test with 10, 100, 500 listings
- Verify tool integration (risk, compliance, safety)

### 3. A/B Testing (Production)
- Compare user satisfaction vs. baseline ranking
- Measure click-through rate on top-10
- Track booking rate from recommendations

### 4. Sensitivity Analysis
- Vary weights, measure rank changes
- Ensure rankings are stable (small weight change = small rank change)

## Red Flags (Triggers for Investigation)
1. **Pareto Rate < 50%**: Algorithm not exploring trade-offs
2. **Weight Correlation < 0.70**: Not respecting user preferences
3. **High-Risk Listings in Top-50**: Safety filter failed
4. **Commute MAE > 10 minutes**: Inaccurate estimates harming UX
5. **Top-K Diversity < 0.3**: Recommendations too homogeneous

## Reporting Dashboard
- **Real-time**: Current ranking for active users
- **Daily**: Pareto rate, weight correlation, top-K diversity
- **Weekly**: User satisfaction correlation, A/B test results
- **Monthly**: Commute accuracy audit, safety filter effectiveness

## User Feedback Integration
- **Explicit**: Ratings on recommendations (1-5 stars)
- **Implicit**: Click-through, saved listings, tour bookings
- **Correction**: User-reported errors in commute/price/amenities
- **Adaptation**: Update default weights based on population trends
