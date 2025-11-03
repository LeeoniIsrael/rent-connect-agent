# Registry System Quick Reference

## What is an Agent Registry?

An **agent registry** is a centralized catalog that maintains metadata about all agents, tools, and components in a multi-agent system. It enables:

- **Dynamic Discovery**: Find available agents by capability
- **Dependency Management**: Track component dependencies
- **Interface Documentation**: Schema definitions for inputs/outputs
- **Workflow Orchestration**: Plan and validate execution sequences
- **Metadata Management**: Store configuration and performance requirements

Think of it like a "service catalog" or "phone book" for your AI agents.

## Key Concepts

### 1. Agent Metadata
Complete information about each agent:
- **Identity**: ID, name, version, description
- **Classification**: Type (decision-maker, planner, matcher, learner)
- **Autonomy Level**: How much human oversight needed
- **Capabilities**: What decisions it can make
- **Interface**: Input/output schemas with validation rules
- **Dependencies**: What components it needs
- **Configuration**: Settings, timeouts, retry policies
- **SLA Requirements**: Performance guarantees

### 2. Registry Types

| Registry | Manages | Components |
|----------|---------|------------|
| **Agent Registry** | Autonomous decision-makers | Ranking, Matching, Planning, Learning |
| **Tool Registry** | Stateless services | Analyzers, Validators, Knowledge Base |
| **Preprocessing Registry** | Data ingestion | Data Ingestion, Survey Processing |

### 3. Component Types

**Agents** (Autonomous)
- Make decisions without constant oversight
- Have configurable autonomy levels
- Implement C³AN framework elements
- Examples: Ranking Agent, Matching Agent

**Tools** (Stateless)
- Provide specific capabilities to agents
- No autonomous decision-making
- Examples: Scam Detector, Compliance Checker

**Preprocessors** (Data Preparation)
- Ingest and clean data
- Quality guarantees (deduplication, normalization)
- Examples: Data Ingestion, Survey Processing

## Quick Start

### Import the Registry Manager
```python
from src.registry_manager import registry_manager
```

### Common Operations

```python
# 1. List all components
components = registry_manager.get_all_components()
# Returns: {"agents": [...], "tools": [...], "preprocessors": [...]}

# 2. Find a specific component
result = registry_manager.find_component("ranking_scoring")
# Returns: {"type": "agent", "metadata": AgentMetadata(...)}

# 3. Get component instance
agent = registry_manager.get_component_instance("ranking_scoring")
# Returns: The actual agent object you can call

# 4. Validate a workflow
validation = registry_manager.validate_workflow("property_search")
# Returns: {"valid": True/False, "issues": [...]}

# 5. Get execution plan
plan = registry_manager.get_workflow_execution_plan("property_search")
# Returns: List of steps with dependencies

# 6. Analyze dependencies
deps = registry_manager.get_all_dependencies("ranking_scoring")
# Returns: Set of all component IDs this agent needs

# 7. Generate report
print(registry_manager.generate_system_report())
```

## Registry Queries

### By Agent Type
```python
from src.agents.agent_registry import agent_registry, AgentType

# Get all decision-makers
agents = agent_registry.list_agents(AgentType.DECISION_MAKER)
```

### By C³AN Element
```python
from src.agents.agent_registry import C3ANElement

# Find agents with explainability
agents = agent_registry.find_agents_by_capability(C3ANElement.EXPLAINABILITY)
```

### By Tool Capability
```python
from src.tools.tool_registry import tool_registry, ToolCapability

# Find scam detection tools
tools = tool_registry.find_tools_by_capability(ToolCapability.SCAM_DETECTION)
```

### By Data Source
```python
from src.preprocessing.preprocessing_registry import preprocessing_registry, DataSource

# Find API-based preprocessors
preps = preprocessing_registry.find_preprocessors_by_source(DataSource.API)
```

## Registered Components

### Agents (4)
1. **ranking_scoring** - Multi-objective property ranking
2. **roommate_matching** - Stable matching with constraints
3. **route_planning** - Time-windowed tour optimization
4. **feedback_learning** - User/expert feedback processing

### Tools (4)
1. **listing_analyzer** - Scam detection, feature extraction
2. **image_analyzer** - Photo quality, authenticity
3. **compliance_checker** - FHA, SC laws, safety validation
4. **knowledge_graph** - Rules engine, entity queries

### Preprocessors (2)
1. **data_ingestion** - Multi-source data collection
2. **survey_ingestion** - FHA-compliant survey processing

## Workflows

### 1. Property Search
```
data_ingestion → listing_analyzer → image_analyzer → 
compliance_checker → ranking_scoring
```

### 2. Roommate Matching
```
survey_ingestion → knowledge_graph → roommate_matching
```

### 3. Tour Planning
```
ranking_scoring → route_planning
```

### 4. Feedback Learning
```
feedback_learning (standalone)
```

## Schema Structure

### Input Schema
```python
InputSchema(
    name="listings",                    # Parameter name
    type="List[Dict[str, Any]]",       # Python type
    description="Property listings",    # Human-readable
    required=True,                      # Is it required?
    validation_rules={                  # Validation
        "min_items": 1,
        "required_fields": ["id", "price"]
    }
)
```

### Output Schema
```python
OutputSchema(
    name="ranked_listings",
    type="List[Dict[str, Any]]",
    description="Ranked properties",
    structure={                         # Expected structure
        "listing_id": "str",
        "score": "float (0-1)",
        "rank": "int"
    }
)
```

## Agent Metadata Example

```python
AgentMetadata(
    agent_id="ranking_scoring",
    name="Ranking & Scoring Agent",
    version="1.0.0",
    agent_type=AgentType.DECISION_MAKER,
    autonomy_level=AutonomyLevel.HIGH,
    
    decision_authority=[
        "Rank properties by score",
        "Filter non-viable options",
        "Identify Pareto-optimal listings"
    ],
    
    c3an_elements=[
        C3ANElement.REASONING,
        C3ANElement.EXPLAINABILITY,
        C3ANElement.INSTRUCTABILITY
    ],
    
    input_schemas=[...],
    output_schemas=[...],
    
    depends_on=["data_ingestion", "listing_analyzer"],
    provides_to=["route_planning"],
    
    module_path="src.agents.ranking_scoring.agent",
    singleton_instance="ranking_scoring"
)
```

## Running the Demo

```bash
cd /path/to/rent-connect-agent
python demo_registries.py
```

Demonstrates:
- Component discovery
- Capability queries
- Workflow validation
- Dependency analysis
- Execution planning
- Metadata inspection
- Report generation

## Common Use Cases

### 1. Before Running a Workflow
```python
# Validate all components are available
validation = registry_manager.validate_workflow("property_search")
if not validation['valid']:
    raise Exception(f"Missing: {validation['issues']}")
```

### 2. Dynamic Agent Selection
```python
# Find agents that can explain decisions
explainable_agents = agent_registry.find_agents_by_capability(
    C3ANElement.EXPLAINABILITY
)
agent = explainable_agents[0]  # Pick one
```

### 3. Dependency Resolution
```python
# Get execution order
workflow = registry_manager.workflows["property_search"]
for component_id in workflow.execution_order:
    instance = registry_manager.get_component_instance(component_id)
    result = instance.process(data)
    data = result  # Pass to next
```

### 4. Component Information
```python
# Get details about any component
agent = agent_registry.get_agent("ranking_scoring")
print(f"Autonomy: {agent.autonomy_level.value}")
print(f"Max latency: {agent.sla_requirements['max_response_time_ms']}ms")
print(f"Human review: {agent.requires_human_review}")
```

## Key Benefits

✅ **Discovery**: Find components by capability  
✅ **Validation**: Check workflows before execution  
✅ **Documentation**: Living docs with schemas  
✅ **Dependencies**: Automatic resolution  
✅ **Flexibility**: Easy to add new components  
✅ **Testing**: Simplifies mocking and validation  
✅ **Orchestration**: Plan execution sequences  
✅ **Monitoring**: Track component health  

## Files

```
src/
├── agents/agent_registry.py           # Agent metadata
├── tools/tool_registry.py             # Tool metadata  
├── preprocessing/preprocessing_registry.py  # Preprocessor metadata
└── registry_manager.py                # Unified interface

demo_registries.py                     # Demo script
REGISTRY_SYSTEM.md                     # Full documentation
REGISTRY_QUICK_REF.md                  # This file
```

## Next Steps

1. Run `python demo_registries.py` to see it in action
2. Read `REGISTRY_SYSTEM.md` for detailed documentation
3. Explore individual registries in the source code
4. Try adding your own agent/tool to the registry

---

**Quick Reference Version**: 1.0.0  
**Last Updated**: October 29, 2025
