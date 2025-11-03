# RentConnect-C3AN Registry System

A comprehensive registry system for managing agents, tools, and preprocessors in the RentConnect-C3AN multi-agent system. The registry provides centralized metadata management, component discovery, dependency tracking, and workflow orchestration.

## Overview

The registry system consists of three specialized registries and a unified manager:

1. **Agent Registry** (`src/agents/agent_registry.py`) - Manages autonomous decision-making agents
2. **Tool Registry** (`src/tools/tool_registry.py`) - Manages stateless service tools
3. **Preprocessing Registry** (`src/preprocessing/preprocessing_registry.py`) - Manages data ingestion components
4. **Registry Manager** (`src/registry_manager.py`) - Unified interface across all registries

## What is an Agent Registry?

An **agent registry** is a design pattern used in multi-agent systems to:

- **Catalog available agents** with their capabilities and interfaces
- **Enable dynamic discovery** so orchestrators can find suitable agents
- **Manage metadata** including inputs, outputs, dependencies, and configurations
- **Support validation** of workflows and component availability
- **Facilitate orchestration** by providing execution order and dependency graphs
- **Document interfaces** for integration and development

Think of it as a "phone book" or "service catalog" for your agent system.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Registry Manager (Unified)                  │
│  • Cross-registry queries                                │
│  • Workflow management                                   │
│  • Dependency analysis                                   │
└───────────────┬─────────────┬──────────────┬────────────┘
                │             │              │
    ┌───────────▼───┐  ┌──────▼──────┐  ┌──▼───────────┐
    │ Agent Registry│  │Tool Registry│  │Preprocessing │
    │               │  │             │  │  Registry    │
    │ • 4 Agents    │  │ • 4 Tools   │  │ • 2 Prepro.  │
    └───────────────┘  └─────────────┘  └──────────────┘
```

## Component Structure

### Agent Registry

**Manages**: Autonomous agents that make decisions
- Ranking & Scoring Agent
- Roommate Matching Agent
- Route Planning Agent
- Feedback & Learning Agent

**Metadata Includes**:
- Identity (ID, name, version)
- Classification (type, autonomy level)
- Capabilities (decision authority, C³AN elements)
- Interface (input/output schemas)
- Dependencies and consumers
- Configuration and SLA requirements
- Human review conditions

### Tool Registry

**Manages**: Stateless service tools
- Listing Analyzer (scam detection, feature extraction)
- Image Analyzer (photo quality, authenticity)
- Compliance Checker (FHA, SC laws, safety)
- Knowledge Graph (rules, entities, queries)

**Metadata Includes**:
- Identity and classification
- Capabilities (specific tool functions)
- Interface schemas
- Performance metrics (latency, caching)
- External API dependencies

### Preprocessing Registry

**Manages**: Data ingestion and preparation
- Data Ingestion (external sources)
- Survey Ingestion (user input processing)

**Metadata Includes**:
- Data sources and types
- Quality guarantees
- Deduplication/normalization settings
- Batch processing capabilities

## Usage Examples

### 1. Discover Components

```python
from src.registry_manager import registry_manager

# Get all components
components = registry_manager.get_all_components()
print(f"Agents: {components['agents']}")
print(f"Tools: {components['tools']}")
print(f"Preprocessors: {components['preprocessors']}")

# Find specific component
result = registry_manager.find_component("ranking_scoring")
print(f"Type: {result['type']}")
print(f"Name: {result['metadata'].name}")
```

### 2. Query Agent Capabilities

```python
from src.agents.agent_registry import agent_registry, C3ANElement

# Find agents that implement explainability
agents = agent_registry.find_agents_by_capability(C3ANElement.EXPLAINABILITY)
for agent in agents:
    print(f"{agent.name}: {agent.autonomy_level.value}")

# Get agent metadata
agent = agent_registry.get_agent("ranking_scoring")
print(f"Decision Authority: {agent.decision_authority}")
print(f"Input Schemas: {len(agent.input_schemas)}")
```

### 3. Validate Workflows

```python
from src.registry_manager import registry_manager

# Validate specific workflow
result = registry_manager.validate_workflow("property_search")
if result['valid']:
    print("✓ Workflow is valid")
else:
    print(f"✗ Issues: {result['issues']}")

# Validate all workflows
all_results = registry_manager.validate_all_workflows()
for wf_id, result in all_results.items():
    status = "✓" if result['valid'] else "✗"
    print(f"{status} {wf_id}")
```

### 4. Analyze Dependencies

```python
from src.registry_manager import registry_manager

# Get dependencies for an agent
deps = registry_manager.get_all_dependencies("ranking_scoring")
print(f"Dependencies: {deps}")

# Get execution order
workflow = registry_manager.workflows["property_search"]
print(f"Execution order: {workflow.execution_order}")
```

### 5. Get Component Instances

```python
from src.registry_manager import registry_manager

# Get runtime instance of any component
ranking_agent = registry_manager.get_component_instance("ranking_scoring")
compliance_tool = registry_manager.get_component_instance("compliance_checker")

# Use the instance
if ranking_agent:
    result = ranking_agent.rank(listings, user_preferences)
```

### 6. Generate Reports

```python
from src.registry_manager import registry_manager

# System summary report
print(registry_manager.generate_system_report())

# Full detailed report (all registries)
print(registry_manager.generate_full_report())

# Individual registry reports
print(registry_manager.agent_registry.generate_registry_report())
print(registry_manager.tool_registry.generate_registry_report())
print(registry_manager.preprocessing_registry.generate_registry_report())
```

## Workflows

The registry defines standard workflows:

### 1. Property Search
**Steps**: Data Ingestion → Listing Analysis → Image Analysis → Compliance Check → Ranking

### 2. Roommate Matching
**Steps**: Survey Ingestion → Knowledge Graph (FHA check) → Matching

### 3. Tour Planning
**Steps**: Ranking → Route Planning

### 4. Feedback Learning
**Steps**: Feedback Processing → Preference Updates

## Schema Definitions

### Agent Input Schema
```python
InputSchema(
    name="listings",
    type="List[Dict[str, Any]]",
    description="Property listings with details",
    required=True,
    validation_rules={
        "min_items": 1,
        "required_fields": ["listing_id", "price", "latitude", "longitude"]
    }
)
```

### Agent Output Schema
```python
OutputSchema(
    name="ranked_listings",
    type="List[Dict[str, Any]]",
    description="Ranked listings with scores",
    structure={
        "listing_id": "str",
        "overall_score": "float (0-1)",
        "rank": "int",
        "criteria_scores": {...}
    }
)
```

## Running the Demo

Run the demonstration script to see the registry in action:

```bash
cd /path/to/rent-connect-agent
python demo_registries.py
```

The demo showcases:
- Component discovery
- Agent capabilities
- Tool discovery
- Workflow validation
- Dependency analysis
- Execution planning
- Metadata inspection
- Usage examples
- Registry reports

## Benefits

### 1. **Dynamic Discovery**
Orchestrators can discover available agents/tools at runtime without hardcoding.

### 2. **Validation**
Validate workflows before execution to ensure all dependencies are available.

### 3. **Documentation**
Registry serves as living documentation of system capabilities.

### 4. **Dependency Management**
Automatic dependency resolution and execution ordering.

### 5. **Metadata-Driven**
All component information in structured, queryable format.

### 6. **Extensibility**
Easy to add new agents/tools by registering metadata.

### 7. **Testing**
Simplifies testing by providing component mocks and validation.

## Integration with Orchestration

The registry integrates with orchestration systems (from your diagram):

```python
# Orchestration flow using registry
from src.registry_manager import registry_manager

# 1. Validate workflow
validation = registry_manager.validate_workflow("property_search")
if not validation['valid']:
    raise Exception(f"Invalid workflow: {validation['issues']}")

# 2. Get execution plan
plan = registry_manager.get_workflow_execution_plan("property_search")

# 3. Execute each step
for step in plan:
    component = registry_manager.get_component_instance(step['component_id'])
    result = component.process(input_data)  # Execute
    input_data = result  # Pass to next step

# 4. Evaluation & verification
evaluator.assess(result)
```

## Adding New Components

### Register a New Agent

```python
def _register_my_agent(self):
    agent = AgentMetadata(
        agent_id="my_agent",
        name="My Agent",
        description="Does something useful",
        version="1.0.0",
        agent_type=AgentType.DECISION_MAKER,
        autonomy_level=AutonomyLevel.HIGH,
        decision_authority=["Make specific decisions"],
        c3an_elements=[C3ANElement.REASONING, C3ANElement.EXPLAINABILITY],
        input_schemas=[...],
        output_schemas=[...],
        module_path="src.agents.my_agent.agent",
        class_name="MyAgent",
        singleton_instance="my_agent"
    )
    self._agents[agent.agent_id] = agent
```

### Register a New Tool

```python
def _register_my_tool(self):
    tool = ToolMetadata(
        tool_id="my_tool",
        name="My Tool",
        description="Provides specific capability",
        version="1.0.0",
        tool_type=ToolType.ANALYZER,
        capabilities=[ToolCapability.CUSTOM_CAPABILITY],
        input_schemas=[...],
        output_schemas=[...],
        module_path="src.tools.my_tool",
        class_name="MyTool",
        singleton_instance="my_tool"
    )
    self._tools[tool.tool_id] = tool
```

## C³AN Element Coverage

The registry tracks which agents implement each C³AN framework element:

- **Custom**: All agents (domain-specific)
- **Compact**: Efficient implementations
- **Composite**: Multi-agent coordination
- **Reasoning**: Logical inference
- **Planning**: Sequential optimization
- **Instructability**: User-tunable parameters
- **Explainability**: Decision explanations
- **Grounding**: Real-world data
- **Alignment**: Fairness, compliance
- **Safety**: Risk mitigation
- **Reliability**: Error handling
- **Attribution**: Source tracking
- **Adaptability**: Learning from feedback
- **Interpretability**: Transparent logic

Query coverage:
```python
coverage = registry_manager.get_c3an_coverage()
print(f"Explainability: {coverage['explainability']}")
# Output: ['ranking_scoring', 'roommate_matching', 'route_planning', 'feedback_learning']
```

## File Structure

```
rent-connect-agent/
├── src/
│   ├── agents/
│   │   ├── agent_registry.py          # Agent registry
│   │   ├── ranking_scoring/
│   │   ├── roommate_matching/
│   │   ├── route_planning/
│   │   └── feedback_learning/
│   ├── tools/
│   │   └── tool_registry.py           # Tool registry
│   ├── preprocessing/
│   │   └── preprocessing_registry.py  # Preprocessing registry
│   └── registry_manager.py            # Unified manager
├── demo_registries.py                  # Demonstration script
└── REGISTRY_SYSTEM.md                  # This file
```

## Future Enhancements

1. **Persistence**: Save/load registry from database
2. **Versioning**: Track agent/tool versions and compatibility
3. **Health Checks**: Monitor component availability
4. **Performance Metrics**: Track actual latency, success rates
5. **A/B Testing**: Support multiple versions of same agent
6. **Auto-Discovery**: Scan codebase for new components
7. **Contract Validation**: Verify input/output contracts at runtime
8. **Capability Matching**: Auto-select agents for new tasks

## References

- [Multi-Agent System Design Patterns](https://en.wikipedia.org/wiki/Multi-agent_system)
- [Service Registry Pattern](https://microservices.io/patterns/service-registry.html)
- [Agent Architectures](https://www.aaai.org/Papers/Symposia/Spring/1999/SS-99-06/SS99-06-001.pdf)

---

**Last Updated**: October 29, 2025  
**Version**: 1.0.0  
**Contact**: RentConnect-C3AN Development Team
