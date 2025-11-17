"""
Unified Registry Manager for RentConnect-C3AN System

Provides a single interface to access all registries (agents, tools, preprocessors)
and perform cross-registry queries and validations.
"""

import logging
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass

from src.agents.agent_registry import agent_registry, AgentType, C3ANElement
from src.tools.tool_registry import tool_registry, ToolType, ToolCapability
from src.preprocessing.preprocessing_registry import preprocessing_registry, PreprocessorType


logger = logging.getLogger(__name__)


@dataclass
class WorkflowDefinition:
    """Definition of a workflow that uses multiple components"""
    workflow_id: str
    name: str
    description: str
    preprocessors: List[str]  # Preprocessor IDs
    tools: List[str]          # Tool IDs
    agents: List[str]         # Agent IDs
    execution_order: List[str]  # Component IDs in execution order


class RegistryManager:
    """
    Unified manager for all component registries.
    Provides cross-registry queries, validation, and workflow management.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.agent_registry = agent_registry
        self.tool_registry = tool_registry
        self.preprocessing_registry = preprocessing_registry
        self.workflows: Dict[str, WorkflowDefinition] = {}
        self._initialize_workflows()
    
    def _initialize_workflows(self):
        """Define standard workflows"""
        
        # Property Search Workflow
        self.workflows["property_search"] = WorkflowDefinition(
            workflow_id="property_search",
            name="Property Search",
            description="End-to-end property search, analysis, and ranking",
            preprocessors=["data_ingestion"],
            tools=["listing_analyzer", "image_analyzer", "compliance_checker", "knowledge_graph"],
            agents=["ranking_scoring"],
            execution_order=[
                "data_ingestion",
                "listing_analyzer",
                "image_analyzer",
                "compliance_checker",
                "ranking_scoring"
            ]
        )
        
        # Roommate Matching Workflow
        self.workflows["roommate_matching"] = WorkflowDefinition(
            workflow_id="roommate_matching",
            name="Roommate Matching",
            description="Survey processing and stable roommate matching",
            preprocessors=["survey_ingestion"],
            tools=["knowledge_graph"],
            agents=["roommate_matching"],
            execution_order=[
                "survey_ingestion",
                "knowledge_graph",
                "roommate_matching"
            ]
        )
        
        # Tour Planning Workflow
        self.workflows["tour_planning"] = WorkflowDefinition(
            workflow_id="tour_planning",
            name="Tour Planning",
            description="Property selection and time-windowed tour planning",
            preprocessors=[],
            tools=[],
            agents=["ranking_scoring", "route_planning"],
            execution_order=[
                "ranking_scoring",
                "route_planning"
            ]
        )
        
        # Feedback Learning Workflow
        self.workflows["feedback_learning"] = WorkflowDefinition(
            workflow_id="feedback_learning",
            name="Feedback Learning",
            description="Process user feedback and update system",
            preprocessors=[],
            tools=[],
            agents=["feedback_learning"],
            execution_order=["feedback_learning"]
        )
    
    # Component Discovery
    
    def get_all_components(self) -> Dict[str, List[str]]:
        """Get all registered component IDs by category"""
        return {
            "agents": list(self.agent_registry._agents.keys()),
            "tools": list(self.tool_registry._tools.keys()),
            "preprocessors": list(self.preprocessing_registry._preprocessors.keys())
        }
    
    def find_component(self, component_id: str) -> Optional[Dict[str, Any]]:
        """Find a component across all registries"""
        # Try agent registry
        agent = self.agent_registry.get_agent(component_id)
        if agent:
            return {"type": "agent", "metadata": agent}
        
        # Try tool registry
        tool = self.tool_registry.get_tool(component_id)
        if tool:
            return {"type": "tool", "metadata": tool}
        
        # Try preprocessing registry
        preprocessor = self.preprocessing_registry.get_preprocessor(component_id)
        if preprocessor:
            return {"type": "preprocessor", "metadata": preprocessor}
        
        return None
    
    def get_component_instance(self, component_id: str) -> Optional[Any]:
        """Get runtime instance of any component"""
        # Try each registry
        instance = self.agent_registry.get_agent_instance(component_id)
        if instance:
            return instance
        
        instance = self.tool_registry.get_tool_instance(component_id)
        if instance:
            return instance
        
        instance = self.preprocessing_registry.get_preprocessor_instance(component_id)
        if instance:
            return instance
        
        return None
    
    # Dependency Analysis
    
    def get_all_dependencies(self, component_id: str) -> Set[str]:
        """Get all dependencies (transitive) for a component"""
        dependencies = set()
        to_process = [component_id]
        processed = set()
        
        while to_process:
            current = to_process.pop(0)
            if current in processed:
                continue
            processed.add(current)
            
            # Get direct dependencies
            component = self.find_component(current)
            if not component:
                continue
            
            metadata = component["metadata"]
            
            # Add dependencies based on component type
            if component["type"] == "agent":
                deps = metadata.depends_on
            elif component["type"] == "tool":
                deps = []  # Tools don't have component dependencies
            elif component["type"] == "preprocessor":
                deps = []  # Preprocessors don't have component dependencies
            else:
                deps = []
            
            for dep in deps:
                if dep not in processed:
                    dependencies.add(dep)
                    to_process.append(dep)
        
        return dependencies
    
    def get_dependency_graph(self) -> Dict[str, List[str]]:
        """Build full dependency graph for all components"""
        graph = {}
        
        for agent_id in self.agent_registry._agents.keys():
            agent = self.agent_registry.get_agent(agent_id)
            graph[agent_id] = agent.depends_on if agent else []
        
        return graph
    
    # Validation
    
    def validate_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Validate that all workflow components are available"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return {"valid": False, "error": f"Workflow {workflow_id} not found"}
        
        issues = []
        
        # Check preprocessors
        for prep_id in workflow.preprocessors:
            if not self.preprocessing_registry.validate_preprocessor_available(prep_id):
                issues.append(f"Preprocessor '{prep_id}' not available")
        
        # Check tools
        for tool_id in workflow.tools:
            if not self.tool_registry.validate_tool_available(tool_id):
                issues.append(f"Tool '{tool_id}' not available")
        
        # Check agents
        for agent_id in workflow.agents:
            if not self.agent_registry.validate_agent_available(agent_id):
                issues.append(f"Agent '{agent_id}' not available")
        
        return {
            "valid": len(issues) == 0,
            "workflow_id": workflow_id,
            "issues": issues
        }
    
    def validate_all_workflows(self) -> Dict[str, Dict[str, Any]]:
        """Validate all defined workflows"""
        results = {}
        for workflow_id in self.workflows.keys():
            results[workflow_id] = self.validate_workflow(workflow_id)
        return results
    
    # Capability Queries
    
    def find_components_by_c3an_element(self, element: C3ANElement) -> List[str]:
        """Find all agents that implement a C³AN element"""
        agents = self.agent_registry.find_agents_by_capability(element)
        return [a.agent_id for a in agents]
    
    def find_tools_by_capability(self, capability: ToolCapability) -> List[str]:
        """Find all tools that provide a capability"""
        tools = self.tool_registry.find_tools_by_capability(capability)
        return [t.tool_id for t in tools]
    
    def get_c3an_coverage(self) -> Dict[str, List[str]]:
        """Get coverage of C³AN elements across all agents"""
        coverage = {}
        for element in C3ANElement:
            agent_ids = self.find_components_by_c3an_element(element)
            if agent_ids:
                coverage[element.value] = agent_ids
        return coverage
    
    # Reporting
    
    def generate_system_report(self) -> str:
        """Generate comprehensive system report"""
        report = "=" * 80 + "\n"
        report += "RENTCONNECT-C3AN SYSTEM REGISTRY REPORT\n"
        report += "=" * 80 + "\n\n"
        
        # Component counts
        components = self.get_all_components()
        report += "COMPONENT INVENTORY:\n"
        report += f"  Agents: {len(components['agents'])}\n"
        report += f"  Tools: {len(components['tools'])}\n"
        report += f"  Preprocessors: {len(components['preprocessors'])}\n"
        report += f"  Total: {sum(len(v) for v in components.values())}\n\n"
        
        # Workflows
        report += f"WORKFLOWS: {len(self.workflows)}\n"
        for wf in self.workflows.values():
            report += f"  • {wf.name}\n"
            report += f"    Components: {len(wf.execution_order)}\n"
        report += "\n"
        
        # C³AN Coverage
        report += "C³AN ELEMENT COVERAGE:\n"
        coverage = self.get_c3an_coverage()
        for element, agents in coverage.items():
            report += f"  • {element}: {len(agents)} agents\n"
        report += "\n"
        
        # Workflow Validation
        report += "WORKFLOW VALIDATION:\n"
        validation = self.validate_all_workflows()
        for wf_id, result in validation.items():
            status = "✓ VALID" if result["valid"] else "✗ INVALID"
            report += f"  • {wf_id}: {status}\n"
            if result["issues"]:
                for issue in result["issues"]:
                    report += f"      - {issue}\n"
        report += "\n"
        
        return report
    
    def generate_full_report(self) -> str:
        """Generate full detailed report including all sub-registries"""
        report = self.generate_system_report()
        report += "\n" + "=" * 80 + "\n\n"
        report += self.agent_registry.generate_registry_report()
        report += "\n" + "=" * 80 + "\n\n"
        report += self.tool_registry.generate_registry_report()
        report += "\n" + "=" * 80 + "\n\n"
        report += self.preprocessing_registry.generate_registry_report()
        return report
    
    # Workflow Execution Helpers
    
    def get_workflow_execution_plan(self, workflow_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get detailed execution plan for a workflow"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return None
        
        plan = []
        for component_id in workflow.execution_order:
            component = self.find_component(component_id)
            if component:
                plan.append({
                    "component_id": component_id,
                    "component_type": component["type"],
                    "name": component["metadata"].name,
                    "dependencies": self.get_all_dependencies(component_id)
                })
        
        return plan


# Global singleton instance
registry_manager = RegistryManager()
