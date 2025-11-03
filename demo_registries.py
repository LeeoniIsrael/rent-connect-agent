"""
Registry Demonstration Script

This script demonstrates the functionality of the RentConnect-C3AN registry system,
showcasing agent, tool, and preprocessor discovery, validation, and management.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.registry_manager import registry_manager
from src.agents.agent_registry import AgentType, C3ANElement
from src.tools.tool_registry import ToolCapability
from src.preprocessing.preprocessing_registry import DataSource


def print_section(title: str):
    """Print section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def demo_component_discovery():
    """Demonstrate component discovery across registries"""
    print_section("COMPONENT DISCOVERY")
    
    components = registry_manager.get_all_components()
    
    print("📋 All Registered Components:")
    for category, items in components.items():
        print(f"\n  {category.upper()} ({len(items)}):")
        for item in items:
            print(f"    • {item}")
    
    # Find specific component
    print("\n\n🔍 Finding component 'ranking_scoring':")
    result = registry_manager.find_component("ranking_scoring")
    if result:
        metadata = result["metadata"]
        print(f"  Type: {result['type']}")
        print(f"  Name: {metadata.name}")
        print(f"  Description: {metadata.description}")
        print(f"  Version: {metadata.version}")


def demo_agent_capabilities():
    """Demonstrate agent capability queries"""
    print_section("AGENT CAPABILITIES")
    
    # List agents by type
    print("🤖 Agents by Type:")
    for agent_type in AgentType:
        agents = registry_manager.agent_registry.list_agents(agent_type)
        if agents:
            print(f"\n  {agent_type.value.upper()}:")
            for agent in agents:
                print(f"    • {agent.name}")
                print(f"      Autonomy: {agent.autonomy_level.value}")
                print(f"      Decision Authority: {len(agent.decision_authority)} capabilities")
    
    # C³AN element coverage
    print("\n\n🎯 C³AN Element Coverage:")
    coverage = registry_manager.get_c3an_coverage()
    for element, agent_ids in sorted(coverage.items()):
        print(f"  {element}: {', '.join(agent_ids)}")


def demo_tool_discovery():
    """Demonstrate tool discovery and capabilities"""
    print_section("TOOL CAPABILITIES")
    
    print("🔧 Tools by Capability:")
    for capability in ToolCapability:
        tool_ids = registry_manager.find_tools_by_capability(capability)
        if tool_ids:
            print(f"\n  {capability.value}:")
            for tool_id in tool_ids:
                tool = registry_manager.tool_registry.get_tool(tool_id)
                if tool:
                    print(f"    • {tool.name}")
                    print(f"      Latency: {tool.avg_latency_ms}ms")
                    print(f"      Cache: {'Enabled' if tool.cache_enabled else 'Disabled'}")


def demo_workflow_validation():
    """Demonstrate workflow validation"""
    print_section("WORKFLOW VALIDATION")
    
    print("📝 Defined Workflows:")
    for wf_id, workflow in registry_manager.workflows.items():
        print(f"\n  {workflow.name} (ID: {wf_id}):")
        print(f"    Description: {workflow.description}")
        print(f"    Preprocessors: {len(workflow.preprocessors)}")
        print(f"    Tools: {len(workflow.tools)}")
        print(f"    Agents: {len(workflow.agents)}")
        print(f"    Execution Steps: {len(workflow.execution_order)}")
    
    print("\n\n✓ Validation Results:")
    validation = registry_manager.validate_all_workflows()
    for wf_id, result in validation.items():
        status = "✓ VALID" if result["valid"] else "✗ INVALID"
        print(f"  {wf_id}: {status}")
        if result["issues"]:
            for issue in result["issues"]:
                print(f"    - {issue}")


def demo_dependency_analysis():
    """Demonstrate dependency analysis"""
    print_section("DEPENDENCY ANALYSIS")
    
    print("🔗 Component Dependencies:")
    
    # Analyze ranking_scoring agent
    agent_id = "ranking_scoring"
    print(f"\n  {agent_id}:")
    agent = registry_manager.agent_registry.get_agent(agent_id)
    if agent:
        print(f"    Direct dependencies: {', '.join(agent.depends_on)}")
        all_deps = registry_manager.get_all_dependencies(agent_id)
        print(f"    All dependencies: {', '.join(all_deps)}")
        print(f"    Provides to: {', '.join(agent.provides_to)}")
    
    # Analyze roommate_matching agent
    agent_id = "roommate_matching"
    print(f"\n  {agent_id}:")
    agent = registry_manager.agent_registry.get_agent(agent_id)
    if agent:
        print(f"    Direct dependencies: {', '.join(agent.depends_on)}")
        all_deps = registry_manager.get_all_dependencies(agent_id)
        print(f"    All dependencies: {', '.join(all_deps)}")
        print(f"    Provides to: {', '.join(agent.provides_to)}")


def demo_execution_planning():
    """Demonstrate workflow execution planning"""
    print_section("EXECUTION PLANNING")
    
    workflow_id = "property_search"
    print(f"📊 Execution Plan for '{workflow_id}':")
    
    plan = registry_manager.get_workflow_execution_plan(workflow_id)
    if plan:
        for i, step in enumerate(plan, 1):
            print(f"\n  Step {i}: {step['name']}")
            print(f"    ID: {step['component_id']}")
            print(f"    Type: {step['component_type']}")
            if step['dependencies']:
                print(f"    Requires: {', '.join(step['dependencies'])}")


def demo_metadata_inspection():
    """Demonstrate detailed metadata inspection"""
    print_section("METADATA INSPECTION")
    
    # Inspect agent metadata
    agent_id = "ranking_scoring"
    print(f"🔍 Detailed Metadata for Agent '{agent_id}':")
    agent = registry_manager.agent_registry.get_agent(agent_id)
    
    if agent:
        print(f"\n  IDENTITY:")
        print(f"    Name: {agent.name}")
        print(f"    Version: {agent.version}")
        print(f"    Type: {agent.agent_type.value}")
        print(f"    Autonomy: {agent.autonomy_level.value}")
        
        print(f"\n  INPUT SCHEMAS ({len(agent.input_schemas)}):")
        for schema in agent.input_schemas:
            required = "required" if schema.required else "optional"
            print(f"    • {schema.name} ({schema.type}) - {required}")
            print(f"      {schema.description}")
        
        print(f"\n  OUTPUT SCHEMAS ({len(agent.output_schemas)}):")
        for schema in agent.output_schemas:
            print(f"    • {schema.name} ({schema.type})")
            print(f"      {schema.description}")
        
        print(f"\n  C³AN ELEMENTS ({len(agent.c3an_elements)}):")
        for element in agent.c3an_elements:
            print(f"    • {element.value}")
        
        print(f"\n  PERFORMANCE:")
        print(f"    Max Response Time: {agent.sla_requirements.get('max_response_time_ms', 'N/A')}ms")
        print(f"    Timeout: {agent.timeout_seconds}s")
        print(f"    Max Retries: {agent.max_retries}")
        print(f"    Human Review: {agent.requires_human_review}")
        
        if agent.review_conditions:
            print(f"\n  REVIEW CONDITIONS:")
            for condition in agent.review_conditions:
                print(f"    • {condition}")


def demo_usage_examples():
    """Demonstrate usage examples"""
    print_section("USAGE EXAMPLES")
    
    print("📚 Example Usage from Registry:\n")
    
    # Get agent example
    agent = registry_manager.agent_registry.get_agent("ranking_scoring")
    if agent and agent.example_usage:
        print("Example: Using Ranking & Scoring Agent")
        print("-" * 80)
        print(agent.example_usage)


def generate_reports():
    """Generate and display registry reports"""
    print_section("REGISTRY REPORTS")
    
    print("📊 System Summary Report:\n")
    print(registry_manager.generate_system_report())
    
    # Optionally generate full report (commented out as it's very long)
    # print("\n\n📄 Full Detailed Report:\n")
    # print(registry_manager.generate_full_report())


def main():
    """Run all demonstrations"""
    print("\n" + "=" * 80)
    print("  RENTCONNECT-C3AN REGISTRY SYSTEM DEMONSTRATION")
    print("=" * 80)
    
    try:
        demo_component_discovery()
        demo_agent_capabilities()
        demo_tool_discovery()
        demo_workflow_validation()
        demo_dependency_analysis()
        demo_execution_planning()
        demo_metadata_inspection()
        demo_usage_examples()
        generate_reports()
        
        print("\n" + "=" * 80)
        print("  ✓ DEMONSTRATION COMPLETE")
        print("=" * 80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
