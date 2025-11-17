"""
Agent Registry for RentConnect-C3AN System

Central registry for all agents in the system, maintaining metadata about:
- Agent capabilities and interfaces
- Input/output schemas
- Autonomy levels and decision authority
- C³AN elements implemented
- Configuration requirements

This registry enables dynamic agent discovery, validation, and orchestration.
"""

import logging
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum


logger = logging.getLogger(__name__)


class AgentType(Enum):
    """Classification of agent types"""
    DECISION_MAKER = "decision_maker"  # Makes autonomous decisions
    ANALYZER = "analyzer"              # Analyzes data, provides insights
    MATCHER = "matcher"                # Matches/pairs entities
    PLANNER = "planner"               # Plans sequences/routes
    LEARNER = "learner"               # Learns from feedback
    PREPROCESSOR = "preprocessor"      # Ingests/cleans data
    VALIDATOR = "validator"           # Validates compliance/safety


class AutonomyLevel(Enum):
    """Level of autonomy for agent decision-making"""
    LOW = "low"           # Requires approval for all decisions
    MEDIUM = "medium"     # Autonomous for routine, approval for edge cases
    HIGH = "high"         # Fully autonomous with exception handling
    FULL = "full"         # Completely autonomous, no human oversight


class C3ANElement(Enum):
    """C³AN Framework Elements"""
    CUSTOM = "custom"
    COMPACT = "compact"
    COMPOSITE = "composite"
    REASONING = "reasoning"
    PLANNING = "planning"
    INSTRUCTABILITY = "instructability"
    EXPLAINABILITY = "explainability"
    GROUNDING = "grounding"
    ALIGNMENT = "alignment"
    SAFETY = "safety"
    RELIABILITY = "reliability"
    ATTRIBUTION = "attribution"
    ADAPTABILITY = "adaptability"
    INTERPRETABILITY = "interpretability"


@dataclass
class InputSchema:
    """Schema definition for agent inputs"""
    name: str
    type: str  # e.g., 'List[Dict]', 'Dict[str, Any]', 'str'
    description: str
    required: bool = True
    default: Any = None
    validation_rules: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OutputSchema:
    """Schema definition for agent outputs"""
    name: str
    type: str
    description: str
    structure: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentMetadata:
    """Complete metadata for a registered agent"""
    # Identity
    agent_id: str
    name: str
    description: str
    version: str
    
    # Classification
    agent_type: AgentType
    autonomy_level: AutonomyLevel
    
    # Capabilities
    decision_authority: List[str]
    c3an_elements: List[C3ANElement]
    
    # Interface
    input_schemas: List[InputSchema]
    output_schemas: List[OutputSchema]
    
    # Dependencies
    depends_on: List[str] = field(default_factory=list)  # Other agent IDs or tools
    provides_to: List[str] = field(default_factory=list)  # Agents that consume this output
    
    # Configuration
    config_module: str = ""
    config_class: Optional[str] = None
    
    # Implementation
    module_path: str = ""
    class_name: str = ""
    singleton_instance: str = ""  # Variable name of singleton
    
    # Evaluation
    evaluation_metrics: List[str] = field(default_factory=list)
    sla_requirements: Dict[str, Any] = field(default_factory=dict)
    
    # Operational
    max_retries: int = 3
    timeout_seconds: int = 30
    requires_human_review: bool = False
    review_conditions: List[str] = field(default_factory=list)
    
    # Documentation
    readme_path: str = ""
    evaluation_doc_path: str = ""
    example_usage: str = ""


class AgentRegistry:
    """
    Central registry for all agents in the RentConnect-C3AN system.
    Provides agent discovery, validation, and metadata management.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._agents: Dict[str, AgentMetadata] = {}
        self._initialize_registry()
    
    def _initialize_registry(self):
        """Initialize registry with all system agents"""
        
        # Register all agents
        self._register_ranking_scoring_agent()
        self._register_roommate_matching_agent()
        self._register_route_planning_agent()
        self._register_feedback_learning_agent()
        
        self.logger.info(f"Agent registry initialized with {len(self._agents)} agents")
    
    def _register_ranking_scoring_agent(self):
        """Register the Ranking & Scoring Agent"""
        agent = AgentMetadata(
            agent_id="ranking_scoring",
            name="Ranking & Scoring Agent",
            description="Multi-objective property ranking with Pareto optimality detection and explainable score breakdowns",
            version="1.0.0",
            
            agent_type=AgentType.DECISION_MAKER,
            autonomy_level=AutonomyLevel.HIGH,
            
            decision_authority=[
                "Rank properties by weighted multi-criteria score",
                "Identify Pareto-optimal listings",
                "Filter out non-viable options (hard constraint violations)",
                "Trigger alerts for anomalous properties"
            ],
            
            c3an_elements=[
                C3ANElement.CUSTOM,
                C3ANElement.COMPOSITE,
                C3ANElement.REASONING,
                C3ANElement.INSTRUCTABILITY,
                C3ANElement.EXPLAINABILITY,
                C3ANElement.GROUNDING
            ],
            
            input_schemas=[
                InputSchema(
                    name="listings",
                    type="List[Dict[str, Any]]",
                    description="Property listings with details (price, location, amenities, lease terms)",
                    required=True,
                    validation_rules={
                        "min_items": 1,
                        "required_fields": ["listing_id", "price", "latitude", "longitude"]
                    }
                ),
                InputSchema(
                    name="user_preferences",
                    type="Optional[Dict[str, Any]]",
                    description="User criteria weights and hard constraints",
                    required=False,
                    default=None,
                    validation_rules={
                        "weights_sum_to_one": True,
                        "valid_criteria": ["price", "commute_time", "safety_score", "amenities_match", "lease_suitability"]
                    }
                ),
                InputSchema(
                    name="destination",
                    type="Optional[Tuple[float, float]]",
                    description="(latitude, longitude) for commute calculation",
                    required=False,
                    default=None,
                    validation_rules={
                        "lat_range": [-90, 90],
                        "lon_range": [-180, 180]
                    }
                )
            ],
            
            output_schemas=[
                OutputSchema(
                    name="ranked_listings",
                    type="List[Dict[str, Any]]",
                    description="Ranked listings with scores and explanations",
                    structure={
                        "listing_id": "str",
                        "overall_score": "float (0-1)",
                        "rank": "int",
                        "is_pareto_optimal": "bool",
                        "criteria_scores": {
                            "price": "float (0-1)",
                            "commute_time": "float (0-1)",
                            "safety_score": "float (0-1)",
                            "amenities_match": "float (0-1)",
                            "lease_suitability": "float (0-1)"
                        },
                        "score_breakdown": "str (explanation)"
                    }
                ),
                OutputSchema(
                    name="pareto_frontier",
                    type="List[str]",
                    description="List of non-dominated property IDs",
                    structure={"property_ids": ["listing_id_1", "listing_id_2", "..."]}
                ),
                OutputSchema(
                    name="explanations",
                    type="Dict[str, str]",
                    description="Natural language explanations for rankings",
                    structure={"listing_id": "explanation text"}
                ),
                OutputSchema(
                    name="stats",
                    type="Dict[str, Any]",
                    description="Statistical summary of rankings",
                    structure={
                        "total_listings": "int",
                        "mean_score": "float",
                        "min_score": "float",
                        "max_score": "float",
                        "std_score": "float"
                    }
                )
            ],
            
            depends_on=[
                "data_ingestion",  # Preprocessor
                "listing_analyzer",  # Tool
                "compliance_checker",  # Tool
                "knowledge_graph"  # Tool
            ],
            
            provides_to=[
                "route_planning",
                "explanation_agent"
            ],
            
            config_module="src.agents.ranking_scoring.config",
            config_class=None,
            
            module_path="src.agents.ranking_scoring.agent",
            class_name="RankingScoringAgent",
            singleton_instance="ranking_scoring",
            
            evaluation_metrics=[
                "ranking_quality",
                "pareto_accuracy",
                "explanation_quality",
                "user_satisfaction",
                "response_time"
            ],
            
            sla_requirements={
                "max_response_time_ms": 2000,
                "min_ranking_quality": 0.8,
                "min_pareto_accuracy": 0.95
            },
            
            max_retries=3,
            timeout_seconds=30,
            requires_human_review=True,
            review_conditions=[
                "property with extreme scores (suspiciously low price + high scam risk)",
                "no properties meet hard constraints",
                "all properties have overall_score < 0.3"
            ],
            
            readme_path="src/agents/ranking_scoring/README.md",
            evaluation_doc_path="src/agents/ranking_scoring/evaluation.md",
            example_usage="""
from src.agents.ranking_scoring import ranking_scoring

listings = [...]  # From DataIngestion
user_preferences = {
    'weights': {'price': 0.4, 'commute_time': 0.3, 'safety_score': 0.3},
    'hard_constraints': {'max_price': 1500, 'max_commute': 45}
}

result = ranking_scoring.rank(listings, user_preferences)

for listing in result.ranked_listings[:10]:
    print(f"Rank {listing['rank']}: {listing['listing_id']} (score: {listing['overall_score']:.2f})")
"""
        )
        
        self._agents[agent.agent_id] = agent
    
    def _register_roommate_matching_agent(self):
        """Register the Roommate Matching Agent"""
        agent = AgentMetadata(
            agent_id="roommate_matching",
            name="Roommate Matching Agent",
            description="Stable matching with constraint satisfaction and fairness guarantees using Gale-Shapley variant",
            version="1.0.0",
            
            agent_type=AgentType.MATCHER,
            autonomy_level=AutonomyLevel.HIGH,
            
            decision_authority=[
                "Match two or more people into roommate groups",
                "Reject candidates that violate hard constraints",
                "Optimize group compositions for multi-bedroom units",
                "Trigger fairness audits when variance exceeds threshold"
            ],
            
            c3an_elements=[
                C3ANElement.CUSTOM,
                C3ANElement.COMPOSITE,
                C3ANElement.REASONING,
                C3ANElement.PLANNING,
                C3ANElement.ALIGNMENT,
                C3ANElement.EXPLAINABILITY,
                C3ANElement.SAFETY
            ],
            
            input_schemas=[
                InputSchema(
                    name="profiles",
                    type="List[Dict[str, Any]]",
                    description="User profiles with constraints, preferences, and personality scores",
                    required=True,
                    validation_rules={
                        "min_items": 2,
                        "required_fields": ["user_id", "hard_constraints", "soft_preferences", "personality"]
                    }
                ),
                InputSchema(
                    name="listing_context",
                    type="Optional[List[Dict[str, Any]]]",
                    description="Available multi-bedroom units",
                    required=False,
                    validation_rules={
                        "required_fields": ["listing_id", "bedrooms", "capacity"]
                    }
                )
            ],
            
            output_schemas=[
                OutputSchema(
                    name="matches",
                    type="List[Dict[str, Any]]",
                    description="Matched roommate pairs/groups with compatibility scores",
                    structure={
                        "match_id": "str",
                        "participants": ["user_id_1", "user_id_2"],
                        "compatibility_score": "float (0-1)",
                        "shared_constraints": {
                            "smoking": "bool",
                            "pets": "bool",
                            "quiet_hours": "(start, end)",
                            "budget_overlap": "(min, max)"
                        },
                        "personality_alignment": {
                            "conscientiousness": "float (0-1)",
                            "agreeableness": "float (0-1)",
                            "extraversion": "float (0-1)",
                            "openness": "float (0-1)",
                            "neuroticism": "float (0-1)"
                        }
                    }
                ),
                OutputSchema(
                    name="unmatched",
                    type="List[str]",
                    description="List of user IDs that could not be matched",
                    structure=["user_id_1", "user_id_2", "..."]
                ),
                OutputSchema(
                    name="blocking_pairs",
                    type="int",
                    description="Count of blocking pairs (should be 0 for stable matching)",
                    structure={"count": "int"}
                ),
                OutputSchema(
                    name="fairness_metrics",
                    type="Dict[str, float]",
                    description="Fairness statistics",
                    structure={
                        "match_rate": "float (0-1)",
                        "quality_variance": "float",
                        "mean_compatibility": "float (0-1)",
                        "median_compatibility": "float (0-1)"
                    }
                ),
                OutputSchema(
                    name="explanations",
                    type="Dict[str, str]",
                    description="Natural language explanations for matches",
                    structure={"match_id": "explanation text"}
                )
            ],
            
            depends_on=[
                "survey_ingestion",  # Preprocessor
                "knowledge_graph",   # Tool (FHA rules)
                "listing_analyzer"   # Tool
            ],
            
            provides_to=[
                "explanation_agent"
            ],
            
            config_module="src.agents.roommate_matching.config",
            config_class=None,
            
            module_path="src.agents.roommate_matching.agent",
            class_name="RoommateMatchingAgent",
            singleton_instance="roommate_matching",
            
            evaluation_metrics=[
                "match_rate",
                "compatibility_score",
                "stability",
                "fairness_variance",
                "user_acceptance_rate"
            ],
            
            sla_requirements={
                "min_match_rate": 0.7,
                "min_stability": 1.0,  # No blocking pairs
                "max_fairness_variance": 0.2,
                "max_response_time_ms": 3000
            },
            
            max_retries=3,
            timeout_seconds=45,
            requires_human_review=True,
            review_conditions=[
                "compatibility_score < 0.5",
                "match_rate < 0.5",
                "fairness_variance > 0.3"
            ],
            
            readme_path="src/agents/roommate_matching/README.md",
            evaluation_doc_path="src/agents/roommate_matching/evaluation.md",
            example_usage="""
from src.agents.roommate_matching import roommate_matching

profiles = [
    {'user_id': 'u1', 'hard_constraints': {...}, 'soft_preferences': {...}, 'personality': {...}},
    {'user_id': 'u2', 'hard_constraints': {...}, 'soft_preferences': {...}, 'personality': {...}}
]

result = roommate_matching.match(profiles)

assert result.blocking_pairs == 0  # Stable matching

for match in result.matches:
    print(f"Match {match['match_id']}: {match['participants']} (score: {match['compatibility_score']:.2f})")
"""
        )
        
        self._agents[agent.agent_id] = agent
    
    def _register_route_planning_agent(self):
        """Register the Route Planning Agent"""
        agent = AgentMetadata(
            agent_id="route_planning",
            name="Route Planning Agent",
            description="Time-windowed tour planning using nearest-neighbor TSP heuristic with class schedule constraints",
            version="1.0.0",
            
            agent_type=AgentType.PLANNER,
            autonomy_level=AutonomyLevel.MEDIUM,
            
            decision_authority=[
                "Optimize visit sequence to minimize total travel time",
                "Schedule viewing times within available windows",
                "Reject infeasible tours (too many stops, insufficient time)",
                "Suggest alternative dates if schedule too tight"
            ],
            
            c3an_elements=[
                C3ANElement.CUSTOM,
                C3ANElement.COMPOSITE,
                C3ANElement.PLANNING,
                C3ANElement.REASONING,
                C3ANElement.GROUNDING,
                C3ANElement.EXPLAINABILITY
            ],
            
            input_schemas=[
                InputSchema(
                    name="properties",
                    type="List[Dict[str, Any]]",
                    description="Properties to visit with locations",
                    required=True,
                    validation_rules={
                        "min_items": 1,
                        "max_items": 10,
                        "required_fields": ["listing_id", "latitude", "longitude"]
                    }
                ),
                InputSchema(
                    name="class_schedule",
                    type="Optional[List[Dict[str, str]]]",
                    description="Unavailable time blocks with start/end times",
                    required=False,
                    validation_rules={
                        "required_fields": ["start", "end"],
                        "time_format": "HH:MM"
                    }
                ),
                InputSchema(
                    name="start_time",
                    type="Optional[str]",
                    description="Preferred start time in HH:MM format",
                    required=False,
                    validation_rules={
                        "time_format": "HH:MM",
                        "range": "08:00-20:00"
                    }
                )
            ],
            
            output_schemas=[
                OutputSchema(
                    name="tour",
                    type="RouteResult",
                    description="Optimized tour with scheduled stops",
                    structure={
                        "tour_id": "str",
                        "stops": [{
                            "listing_id": "str",
                            "arrival_time": "str (HH:MM)",
                            "departure_time": "str (HH:MM)",
                            "viewing_duration": "int (minutes)",
                            "travel_to_next": "int (minutes)",
                            "location": "(latitude, longitude)"
                        }],
                        "total_duration": "int (minutes)",
                        "feasible": "bool",
                        "time_window_violations": "int",
                        "explanation": "str"
                    }
                )
            ],
            
            depends_on=[
                "ranking_scoring",  # For commute estimates
                "google_maps_api"   # For real travel times (production)
            ],
            
            provides_to=[
                "explanation_agent"
            ],
            
            config_module="src.agents.route_planning.config",
            config_class=None,
            
            module_path="src.agents.route_planning.agent",
            class_name="RoutePlanningAgent",
            singleton_instance="route_planning",
            
            evaluation_metrics=[
                "tour_optimality",
                "feasibility_rate",
                "time_window_adherence",
                "total_travel_time",
                "user_satisfaction"
            ],
            
            sla_requirements={
                "max_response_time_ms": 1500,
                "min_feasibility_rate": 0.85,
                "max_tour_duration_minutes": 360
            },
            
            max_retries=3,
            timeout_seconds=20,
            requires_human_review=True,
            review_conditions=[
                "tight_connections < 15 min buffer",
                "time_window_violations > 0",
                "total_duration > max_tour_duration"
            ],
            
            readme_path="src/agents/route_planning/README.md",
            evaluation_doc_path="src/agents/route_planning/evaluation.md",
            example_usage="""
from src.agents.route_planning import route_planning

properties = [
    {'listing_id': 'p1', 'latitude': 33.99, 'longitude': -81.03},
    {'listing_id': 'p2', 'latitude': 34.00, 'longitude': -81.02}
]

class_schedule = [
    {'start': '09:00', 'end': '10:30'},
    {'start': '14:00', 'end': '15:30'}
]

result = route_planning.plan_route(properties, class_schedule)

print(f"Feasible: {result.feasible}")
for stop in result.stops:
    print(f"{stop['arrival_time']}: Visit {stop['listing_id']}")
"""
        )
        
        self._agents[agent.agent_id] = agent
    
    def _register_feedback_learning_agent(self):
        """Register the Feedback & Learning Agent"""
        agent = AgentMetadata(
            agent_id="feedback_learning",
            name="Feedback & Learning Agent",
            description="Processes user and expert feedback to improve system recommendations through preference adaptation and model corrections",
            version="1.0.0",
            
            agent_type=AgentType.LEARNER,
            autonomy_level=AutonomyLevel.MEDIUM,
            
            decision_authority=[
                "Update user preference weights based on ratings",
                "Apply expert corrections to models (with verification)",
                "Detect preference drift and trigger re-profiling",
                "Reject low-confidence feedback (< 0.8 confidence score)"
            ],
            
            c3an_elements=[
                C3ANElement.CUSTOM,
                C3ANElement.COMPOSITE,
                C3ANElement.INSTRUCTABILITY,
                C3ANElement.ADAPTABILITY,
                C3ANElement.EXPLAINABILITY,
                C3ANElement.SAFETY
            ],
            
            input_schemas=[
                InputSchema(
                    name="feedback",
                    type="Dict[str, Any]",
                    description="Feedback data with type, user_id, and content",
                    required=True,
                    validation_rules={
                        "required_fields": ["type", "user_id"],
                        "valid_types": ["rating", "correction", "preference_update"]
                    }
                ),
                InputSchema(
                    name="rating",
                    type="int",
                    description="Rating value (1-5 stars)",
                    required=False,
                    validation_rules={
                        "min": 1,
                        "max": 5
                    }
                ),
                InputSchema(
                    name="context",
                    type="Dict[str, Any]",
                    description="Context of rated item (listing_id, rank, criteria_scores)",
                    required=False
                ),
                InputSchema(
                    name="expert_confidence",
                    type="float",
                    description="Expert confidence score for corrections",
                    required=False,
                    validation_rules={
                        "min": 0.0,
                        "max": 1.0
                    }
                )
            ],
            
            output_schemas=[
                OutputSchema(
                    name="result",
                    type="FeedbackResult",
                    description="Result of feedback processing",
                    structure={
                        "feedback_id": "str",
                        "applied": "bool",
                        "impact_summary": "str",
                        "updated_components": ["component_name_1", "component_name_2"],
                        "drift_detected": "bool"
                    }
                ),
                OutputSchema(
                    name="updated_preferences",
                    type="Dict[str, float]",
                    description="Updated user preference weights",
                    structure={
                        "user_id": "str",
                        "old_weights": {"criterion": "float"},
                        "new_weights": {"criterion": "float"},
                        "confidence": "float",
                        "reason": "str"
                    }
                )
            ],
            
            depends_on=[
                "ranking_scoring",  # Updates preferences for
                "roommate_matching",  # Updates preferences for
                "listing_analyzer"  # Applies corrections to
            ],
            
            provides_to=[
                "all_agents"  # Can update any agent's parameters
            ],
            
            config_module="src.agents.feedback_learning.config",
            config_class=None,
            
            module_path="src.agents.feedback_learning.agent",
            class_name="FeedbackLearningAgent",
            singleton_instance="feedback_learning",
            
            evaluation_metrics=[
                "feedback_processing_accuracy",
                "preference_drift_detection_rate",
                "model_correction_impact",
                "user_satisfaction_improvement",
                "learning_convergence_speed"
            ],
            
            sla_requirements={
                "max_response_time_ms": 1000,
                "min_drift_detection_accuracy": 0.85,
                "min_correction_confidence": 0.8
            },
            
            max_retries=2,
            timeout_seconds=15,
            requires_human_review=True,
            review_conditions=[
                "expert_confidence < 0.8 for corrections",
                "major preference drift detected",
                "correction targets critical model"
            ],
            
            readme_path="src/agents/feedback_learning/README.md",
            evaluation_doc_path="src/agents/feedback_learning/evaluation.md",
            example_usage="""
from src.agents.feedback_learning import feedback_learning

# Process rating feedback
rating_feedback = {
    'user_id': 'u1',
    'type': 'rating',
    'rating': 5,
    'context': {'listing_id': 'p1', 'rank': 2}
}

result = feedback_learning.process_feedback(rating_feedback)

# Process expert correction
correction_feedback = {
    'type': 'correction',
    'target': 'scam_detector',
    'listing_id': 'p2',
    'corrected_risk_score': 0.9,
    'expert_confidence': 0.95
}

result = feedback_learning.process_feedback(correction_feedback)
"""
        )
        
        self._agents[agent.agent_id] = agent
    
    # Registry Query Methods
    
    def get_agent(self, agent_id: str) -> Optional[AgentMetadata]:
        """Retrieve agent metadata by ID"""
        return self._agents.get(agent_id)
    
    def list_agents(self, agent_type: Optional[AgentType] = None) -> List[AgentMetadata]:
        """List all agents, optionally filtered by type"""
        if agent_type:
            return [a for a in self._agents.values() if a.agent_type == agent_type]
        return list(self._agents.values())
    
    def find_agents_by_capability(self, c3an_element: C3ANElement) -> List[AgentMetadata]:
        """Find agents that implement a specific C³AN element"""
        return [a for a in self._agents.values() if c3an_element in a.c3an_elements]
    
    def get_dependencies(self, agent_id: str) -> List[str]:
        """Get list of dependencies for an agent"""
        agent = self.get_agent(agent_id)
        return agent.depends_on if agent else []
    
    def get_consumers(self, agent_id: str) -> List[str]:
        """Get list of agents that consume this agent's output"""
        agent = self.get_agent(agent_id)
        return agent.provides_to if agent else []
    
    def validate_agent_available(self, agent_id: str) -> bool:
        """Check if agent is registered and available"""
        return agent_id in self._agents
    
    def get_agent_instance(self, agent_id: str) -> Optional[Any]:
        """
        Dynamically import and return the agent singleton instance.
        Returns None if agent not found or import fails.
        """
        agent = self.get_agent(agent_id)
        if not agent:
            self.logger.error(f"Agent {agent_id} not found in registry")
            return None
        
        try:
            # Dynamic import
            module = __import__(agent.module_path, fromlist=[agent.singleton_instance])
            instance = getattr(module, agent.singleton_instance)
            return instance
        except (ImportError, AttributeError) as e:
            self.logger.error(f"Failed to import agent {agent_id}: {e}")
            return None
    
    def get_execution_order(self, required_agents: List[str]) -> List[str]:
        """
        Determine execution order based on dependencies.
        Returns topologically sorted list of agent IDs.
        """
        # Build dependency graph
        graph = {aid: self.get_dependencies(aid) for aid in required_agents}
        
        # Topological sort (Kahn's algorithm)
        in_degree = {aid: 0 for aid in required_agents}
        for aid in required_agents:
            for dep in graph[aid]:
                if dep in in_degree:
                    in_degree[dep] += 1
        
        queue = [aid for aid in required_agents if in_degree[aid] == 0]
        result = []
        
        while queue:
            current = queue.pop(0)
            result.append(current)
            
            for aid in required_agents:
                if current in graph[aid]:
                    in_degree[aid] -= 1
                    if in_degree[aid] == 0:
                        queue.append(aid)
        
        if len(result) != len(required_agents):
            self.logger.warning("Circular dependency detected in agent execution order")
        
        return result
    
    def generate_registry_report(self) -> str:
        """Generate human-readable registry report"""
        report = "=" * 80 + "\n"
        report += "RENTCONNECT-C3AN AGENT REGISTRY REPORT\n"
        report += "=" * 80 + "\n\n"
        
        report += f"Total Registered Agents: {len(self._agents)}\n\n"
        
        # Group by type
        for agent_type in AgentType:
            agents = self.list_agents(agent_type)
            if agents:
                report += f"\n{agent_type.value.upper()} AGENTS ({len(agents)}):\n"
                report += "-" * 80 + "\n"
                for agent in agents:
                    report += f"  • {agent.name} (ID: {agent.agent_id})\n"
                    report += f"    Autonomy: {agent.autonomy_level.value}\n"
                    report += f"    Version: {agent.version}\n"
                    report += f"    C³AN Elements: {', '.join(e.value for e in agent.c3an_elements)}\n"
                    report += f"    Dependencies: {', '.join(agent.depends_on) if agent.depends_on else 'None'}\n"
                    report += "\n"
        
        return report


# Global singleton instance
agent_registry = AgentRegistry()
