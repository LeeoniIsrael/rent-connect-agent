# RentConnect-C3AN Refactoring Guide

## Overview

This document outlines the comprehensive refactoring of the RentConnect-C3AN system based on new architectural requirements. The refactoring reorganizes the system into **Preprocessing → Tools → Agents** pipeline.

---

## Architectural Changes

### Old Structure (14 Agents)
```
src/agents/
├── base_agent.py
├── ingestion/ (2 agents)
├── knowledge/ (1 agent)
├── analysis/ (2 agents)
├── matching/ (1 agent)
├── ranking/ (2 agents)
├── planning/ (2 agents)
├── explanation/ (2 agents)
└── orchestration/ (1 agent)
```

### New Structure (4 Agents + Preprocessing + Tools)
```
src/
├── preprocessing/          # Data collection (not agents)
│   ├── data_ingestion.py   ✅ COMPLETED
│   └── survey_ingestion.py ✅ COMPLETED
├── tools/                  # Analysis utilities (not agents)
│   ├── knowledge_graph.py  ✅ COMPLETED
│   ├── listing_analyzer.py  ⏳ TODO
│   ├── image_analyzer.py    ⏳ TODO
│   └── compliance_checker.py ⏳ TODO
└── agents/                 # Decision-making only
    ├── roommate_matching/   ⏳ TODO (restructure)
    ├── ranking_scoring/     ⏳ TODO (restructure)
    ├── route_planning/      ⏳ TODO (restructure)
    └── feedback_learning/   ⏳ TODO (restructure)
```

---

## Layer-by-Layer Changes

### 1. Data Collection Layer → Preprocessing ✅

**Changed:**
- ❌ `DataIngestionAgent` → ✅ `preprocessing/data_ingestion.py`
- ❌ `RoommateSurveyIngestionAgent` → ✅ `preprocessing/survey_ingestion.py`

**Rationale:** These are data pipelines, not decision-makers. They clean and normalize data before agents process it.

**Implementation Status:** ✅ COMPLETED

**What Was Added:**
- Class-based preprocessing modules (not agents)
- Input/output stream documentation
- Configuration references
- Detailed docstrings

---

### 2. Knowledge & Analysis Layer → Tools

**Changed:**
- ❌ `KnowledgeGraphAgent` → ✅ `tools/knowledge_graph.py` (singleton pattern)
- ❌ `ListingAnalysisAgent` → ⏳ `tools/listing_analyzer.py`
- ❌ `ImageAnalysisAgent` → ⏳ `tools/image_analyzer.py`

**Rationale:** These provide lookup/analysis services to agents. They don't make autonomous decisions.

**Implementation Status:** 
- ✅ `knowledge_graph.py` completed
- ⏳ `listing_analyzer.py` needs creation
- ⏳ `image_analyzer.py` needs creation

**What's Needed:**
Each tool file needs:
```python
class ToolNameTool:
    \"\"\"
    Description: What it does
    
    Input Streams:
    - List of inputs
    
    Output Streams:
    - List of outputs
    
    Configuration:
    See: config/tools_config.py
    \"\"\"
    
    def __init__(self, config):
        pass
    
    def tool_method(self, input_data):
        \"\"\"
        Input Stream: ...
        Output Stream: ...
        \"\"\"
        pass

# Singleton instance
tool_name = ToolNameTool()
```

---

### 3. Decision-Making Layer → Keep as Agents ✅

**Unchanged (but needs restructuring):**
- ✅ `RoommateMatchingAgent` 
- ✅ `RankingScoringAgent`
- ✅ `RoutePlanningAgent`

**Rationale:** These make complex decisions using constraints, optimization, and reasoning. They are true agents.

**Implementation Status:** ⏳ Need restructuring

**What Each Agent Needs:**

#### A. Directory Structure
```
src/agents/roommate_matching/
├── __init__.py
├── agent.py              # Main agent class
├── config.py             # Agent-specific configuration
├── README.md             # Agent documentation
└── evaluation.md         # Evaluation metrics
```

#### B. Agent File Template (`agent.py`)
```python
\"\"\"
Agent Name

Description:
Full description of what this agent does.

Input Streams:
- Input 1
- Input 2

Output Streams:
- Output 1
- Output 2

Evaluation Metrics:
See: evaluation.md for detailed metrics
\"\"\"

class AgentName(BaseAgent):
    # All logic in class
    pass

# Variable instance (lowercase)
agent_name = AgentName()
```

#### C. Config File Template (`config.py`)
```python
\"\"\"Configuration for AgentName\"\"\"

AGENT_CONFIG = {
    'name': 'agent_name',
    'version': '1.0.0',
    'parameters': {
        # Agent-specific params
    }
}
```

#### D. README Template (`README.md`)
```markdown
# Agent Name

## Description
What this agent does

## Input Streams
- Stream 1: Description
- Stream 2: Description

## Output Streams
- Stream 1: Description

## Configuration
See config.py

## Usage
```python
from src.agents.agent_name import agent_name
result = agent_name.process(input_data, context)
```

## Evaluation
See evaluation.md
```

#### E. Evaluation Template (`evaluation.md`)
```markdown
# Agent Name - Evaluation Metrics

## Chosen Metrics

### Metric 1: [Name]
- **Why chosen**: Explanation
- **How to measure**: Method
- **Target value**: Goal
- **Why explainable**: How to justify to stakeholders

## C³AN Elements Used
- Element 1: How used
- Element 2: How used
```

---

### 4. Compliance & Safety Layer → Tool

**Changed:**
- ❌ `ComplianceSafetyAgent` → ⏳ `tools/compliance_checker.py`

**Rationale:** Compliance checking is a utility service (rule matching), not decision-making.

**Implementation Status:** ⏳ TODO

---

### 5. Learning & Orchestration Layer → Keep Feedback, Remove Orchestration

**Changed:**
- ✅ Keep `FeedbackLearningAgent` (needs restructuring)
- ❌ Remove `OrchestrationAgent` (logic moves to `main.py`)

**Rationale:** 
- Feedback agent learns and adapts = true agent behavior
- Orchestration is just workflow management = not an agent

**Implementation Status:** ⏳ TODO

---

## Required Changes Checklist

### Completed ✅
- [x] Create `src/preprocessing/` directory
- [x] Create `preprocessing/data_ingestion.py` with DataIngestion class
- [x] Create `preprocessing/survey_ingestion.py` with SurveyIngestion class
- [x] Create `src/tools/` directory
- [x] Create `tools/knowledge_graph.py` with knowledge_graph singleton

### High Priority ⏳
- [ ] Create `tools/listing_analyzer.py` with listing_analyzer singleton
- [ ] Create `tools/image_analyzer.py` with image_analyzer singleton
- [ ] Create `tools/compliance_checker.py` with compliance_checker singleton
- [ ] Create `config/preprocessing_config.py`
- [ ] Create `config/tools_config.py`
- [ ] Create `config/agents_config.py`

### Medium Priority ⏳
- [ ] Restructure `agents/roommate_matching/`:
  - [ ] Create directory structure
  - [ ] Add README.md
  - [ ] Add config.py
  - [ ] Add evaluation.md
  - [ ] Update agent.py with streams
  - [ ] Create singleton variable
  
- [ ] Restructure `agents/ranking_scoring/`:
  - [ ] Create directory structure
  - [ ] Add README.md
  - [ ] Add config.py
  - [ ] Add evaluation.md
  - [ ] Update agent.py with streams
  - [ ] Create singleton variable

- [ ] Restructure `agents/route_planning/`:
  - [ ] Create directory structure
  - [ ] Add README.md
  - [ ] Add config.py
  - [ ] Add evaluation.md
  - [ ] Update agent.py with streams
  - [ ] Create singleton variable

- [ ] Restructure `agents/feedback_learning/`:
  - [ ] Create directory structure
  - [ ] Add README.md
  - [ ] Add config.py
  - [ ] Add evaluation.md
  - [ ] Update agent.py with streams
  - [ ] Create singleton variable

### Low Priority ⏳
- [ ] Remove `src/agents/orchestration/orchestration_agent.py`
- [ ] Update `main.py` with direct workflow management
- [ ] Update `README.md` with new architecture
- [ ] Update `ARCHITECTURE.md` with new diagrams
- [ ] Update `AGENTS.md` to reflect 4 agents + preprocessing + tools
- [ ] Update `requirements.txt` if needed
- [ ] Update `config.py` to split into separate configs

---

## Evaluation Metrics Guide

For each of the 4 agents, you need to choose **appropriate, explainable** evaluation metrics from the C³AN framework.

### C³AN Elements (14 Foundation Elements)
1. **Grounding** - Connection to real data
2. **Reasoning** - Logical inference
3. **Planning** - Sequential decision-making
4. **Instructability** - Following user preferences
5. **Compactness** - Efficiency
6. **Explainability** - Transparent decisions
7. **Interpretability** - Human-understandable
8. **Attribution** - Source tracking
9. **Safety** - Risk mitigation
10. **Alignment** - Values compliance (FHA)
11. **Reliability** - Consistent performance
12. **Transparency** - Open process
13. **Adaptability** - Learning from feedback
14. **Composability** - Module integration

### Agent-Specific Evaluation Recommendations

#### 1. Roommate Matching Agent

**Primary Metrics:**
- **Stability Score** (Reasoning): % of matches that are stable (no two prefer each other over assigned)
  - Why: Measures quality of constraint satisfaction algorithm
  - How: Count blocking pairs / total possible pairs
  - Explainable: "0% blocking pairs means no one wants to trade partners"

- **Fairness Score** (Alignment): Variance in match quality across demographic groups
  - Why: Ensures FHA compliance and equitable outcomes
  - How: Calculate std dev of compatibility scores by group
  - Explainable: "All groups get similar quality matches"

- **Hard Constraint Satisfaction Rate** (Reliability): % of matches with 100% constraint agreement
  - Why: Measures if binary requirements (smoking, pets) are met
  - How: Count matches with no constraint violations / total matches
  - Explainable: "All required preferences are matched"

#### 2. Ranking & Scoring Agent

**Primary Metrics:**
- **Pareto Efficiency Rate** (Reasoning): % of top-N listings that are Pareto-optimal
  - Why: Measures multi-objective optimization quality
  - How: Count non-dominated solutions in top results
  - Explainable: "These listings offer best trade-offs across criteria"

- **Preference Alignment Score** (Instructability): Correlation between user weights and top results
  - Why: Measures if agent respects user priorities
  - How: Spearman correlation of user weights vs. result rankings
  - Explainable: "Results match what you said was important"

- **Score Explainability Coverage** (Explainability): % of score attributable to documented criteria
  - Why: Transparency in scoring breakdown
  - How: Sum of weight * criterion_score / total_score
  - Explainable: "We can show you exactly why each property scored as it did"

#### 3. Route Planning Agent

**Primary Metrics:**
- **Time Window Compliance** (Planning): % of tours that fit within class schedule
  - Why: Measures constraint satisfaction in scheduling
  - How: Count tours with 0 conflicts / total tours
  - Explainable: "All property visits happen when you're free"

- **Route Optimality Gap** (Compactness): % difference from optimal TSP solution
  - Why: Measures efficiency of heuristic algorithm
  - How: (heuristic_time - optimal_time) / optimal_time
  - Explainable: "Route is within X% of theoretically perfect"

- **Tour Completion Rate** (Reliability): % of properties scheduled vs. requested
  - Why: Measures if agent can accommodate all requests
  - How: Count scheduled properties / requested properties
  - Explainable: "We fit 8 out of 10 requested properties into your schedule"

#### 4. Feedback Learning Agent

**Primary Metrics:**
- **Recommendation Improvement Rate** (Adaptability): % increase in user satisfaction after feedback
  - Why: Measures learning effectiveness
  - How: (avg_rating_after - avg_rating_before) / avg_rating_before
  - Explainable: "Your ratings improved our recommendations by X%"

- **Preference Drift Detection** (Instructability): Time to detect significant user preference changes
  - Why: Responsiveness to changing needs
  - How: Number of ratings until preference shift detected
  - Explainable: "We noticed your priorities changed after 5 ratings"

- **Feedback Incorporation Rate** (Reliability): % of user corrections applied to model
  - Why: Measures if system actually learns
  - How: Count corrections in next recommendations / total corrections
  - Explainable: "We applied 9 out of 10 of your corrections"

---

## Implementation Priority

### Phase 1: Complete Tools (Week 1)
1. Finish all tool implementations
2. Create config files for preprocessing and tools
3. Test tools independently

### Phase 2: Restructure Agents (Week 2)
1. Create directory structures for 4 agents
2. Add READMEs, configs, evaluation docs
3. Update agent code with stream documentation
4. Create singleton variables

### Phase 3: Update Main Workflow (Week 3)
1. Remove orchestration agent
2. Update main.py with direct workflow calls
3. Test end-to-end workflows

### Phase 4: Documentation (Week 4)
1. Update all markdown docs
2. Create migration guide
3. Update quickstart
4. Record demo video

---

## Migration Impact

### Breaking Changes
- Import paths changed for all converted components
- Agent initialization pattern changed (singleton variables)
- Workflow execution no longer uses OrchestrationAgent

### Backward Compatibility
- Base agent interface unchanged
- AgentContext and AgentOutput remain same
- Config structure similar (just split into multiple files)

---

## Testing Strategy

### Unit Tests
- Test each preprocessing module independently
- Test each tool function
- Test each agent in isolation

### Integration Tests
- Test preprocessing → tool → agent pipelines
- Test full workflows without orchestration agent
- Test config loading from split files

### Evaluation Tests
- Measure chosen metrics on sample data
- Validate metric calculations
- Test metric explainability

---

## Next Steps

**Immediate (Today):**
1. Finish creating remaining tool files
2. Create config directory with split configs
3. Start restructuring first agent (roommate_matching)

**This Week:**
1. Complete all agent restructuring
2. Update main.py workflow
3. Test each component

**Next Week:**
1. Update all documentation
2. Run full integration tests
3. Measure evaluation metrics

---

**Status:** 20% Complete (2/10 major tasks done)  
**Next Task:** Create listing_analyzer, image_analyzer, compliance_checker tools  
**Estimated Completion:** 4 weeks for full refactoring

