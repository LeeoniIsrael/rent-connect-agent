"""
C³AN-Compliant Orchestrator
Registry-driven workflow execution engine
"""

import json
import logging
from typing import Dict, Any, List
from pathlib import Path

logger = logging.getLogger(__name__)


class Orchestrator:
    """
    Generic workflow executor that reads agent registry and routes data automatically.
    This is the "Compact" promise of C³AN - no hardcoded routing logic.
    """
    
    def __init__(self, registry_path: str = "rentconnect_agent_registry.json"):
        """Load registry and build routing map"""
        self.registry_path = Path(registry_path)
        self.registry = self._load_registry()
        self.agents = self._build_agent_map()
        self.workflows = self._define_workflows()
    
    def _load_registry(self) -> Dict[str, Any]:
        """Load agent registry from JSON"""
        with open(self.registry_path, 'r') as f:
            return json.load(f)
    
    def _build_agent_map(self) -> Dict[str, Any]:
        """Build map of agent_id -> agent instance"""
        # Import actual agent implementations
        from src.preprocessing import DataIngestion, SurveyIngestion
        from src.tools import listing_analyzer, compliance_checker, knowledge_graph
        from src.agents import roommate_matching, ranking_scoring, route_planning, feedback_learning
        
        return {
            "data-ingestion-agent": DataIngestion(),
            "survey-ingestion-agent": SurveyIngestion(),
            "listing-analyzer-agent": listing_analyzer,
            "compliance-checker-agent": compliance_checker,
            "knowledge-graph-agent": knowledge_graph,
            "ranking-scoring-agent": ranking_scoring,
            "roommate-matching-agent": roommate_matching,
            "route-planning-agent": route_planning,
            "feedback-learning-agent": feedback_learning
        }
    
    def _define_workflows(self) -> Dict[str, List[str]]:
        """Define workflow execution chains (could also come from JSON)"""
        return {
            "property_search": [
                "data-ingestion-agent",
                "listing-analyzer-agent",
                "compliance-checker-agent",
                "ranking-scoring-agent"
            ],
            "roommate_matching": [
                "survey-ingestion-agent",
                "knowledge-graph-agent",
                "roommate-matching-agent"
            ],
            "tour_planning": [
                "ranking-scoring-agent",
                "route-planning-agent"
            ],
            "feedback_learning": [
                "feedback-learning-agent"
            ]
        }
    
    def run_workflow(self, workflow_name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a workflow by routing data through agents based on registry definitions.
        
        Args:
            workflow_name: Name of workflow (e.g., "property_search")
            inputs: Initial input data
        
        Returns:
            Final workflow result
        """
        if workflow_name not in self.workflows:
            raise ValueError(f"Unknown workflow: {workflow_name}")
        
        logger.info(f"=== Executing Workflow: {workflow_name} ===")
        
        # Get the execution chain
        chain = self.workflows[workflow_name]
        
        # Route data through the chain
        data = inputs
        execution_trace = []
        
        for agent_id in chain:
            logger.info(f"→ Calling {agent_id}")
            
            # Get agent instance
            agent = self.agents.get(agent_id)
            if not agent:
                logger.warning(f"Agent {agent_id} not found, skipping")
                continue
            
            # Route based on agent type
            try:
                if agent_id == "data-ingestion-agent":
                    result = agent.ingest_listings(
                        sources=data.get('sources', ['zillow_zori']),
                        filters=data.get('filters', {})
                    )
                    data['listings'] = result.get('records', [])
                
                elif agent_id == "survey-ingestion-agent":
                    # Process multiple surveys
                    surveys = data.get('surveys', [])
                    profiles = [agent.process_survey(s) for s in surveys]
                    data['user_profiles'] = profiles
                
                elif agent_id == "listing-analyzer-agent":
                    # Analyze each listing
                    listings = data.get('listings', [])
                    for listing in listings:
                        risk = agent.analyze_listing(listing)
                        listing['risk_score'] = risk['risk_score']
                
                elif agent_id == "compliance-checker-agent":
                    # Check compliance for each listing
                    listings = data.get('listings', [])
                    for listing in listings:
                        compliance = agent.check_compliance(listing)
                        listing['safety_score'] = compliance['safety_score']
                        listing['compliant'] = compliance['compliant']
                
                elif agent_id == "knowledge-graph-agent":
                    # Query knowledge graph
                    query = data.get('kg_query', 'FHA rules')
                    result = agent.query(query)
                    data['kg_results'] = result
                
                elif agent_id == "ranking-scoring-agent":
                    # Rank properties
                    listings = data.get('listings', [])
                    preferences = data.get('preferences', {})
                    destination = data.get('destination')
                    
                    result = agent.rank(listings, preferences, destination)
                    data['ranked_listings'] = result.ranked_listings
                    data['pareto_frontier'] = result.pareto_frontier
                
                elif agent_id == "roommate-matching-agent":
                    # Match roommates
                    profiles = data.get('user_profiles', [])
                    
                    # Transform to expected format
                    formatted_profiles = []
                    for p in profiles:
                        formatted_profiles.append({
                            'user_id': p['profile']['student_id'],
                            'hard_constraints': p['hard_constraints'],
                            'soft_preferences': p['soft_preferences'],
                            'personality': p['personality_scores']
                        })
                    
                    result = agent.match(formatted_profiles)
                    data['matches'] = result.matches
                    data['fairness_metrics'] = result.fairness_metrics
                
                elif agent_id == "route-planning-agent":
                    # Plan tour route
                    properties = data.get('ranked_listings', [])[:3]  # Top 3
                    schedule = data.get('class_schedule', [])
                    
                    # Extract coordinates
                    properties_to_visit = [
                        {
                            'listing_id': p['listing_id'],
                            'latitude': p.get('latitude', 33.995),
                            'longitude': p.get('longitude', -81.030)
                        }
                        for p in properties
                    ]
                    
                    result = agent.plan_route(properties_to_visit, schedule)
                    data['tour'] = result.stops
                    data['tour_feasible'] = result.feasible
                
                elif agent_id == "feedback-learning-agent":
                    # Process feedback
                    feedback = data.get('feedback', {})
                    result = agent.process_feedback(feedback)
                    data['feedback_applied'] = result.applied
                    data['updated_preferences'] = agent.get_user_preferences(feedback.get('user_id', 'default'))
                
                execution_trace.append(agent_id)
                
            except Exception as e:
                logger.error(f"Error in {agent_id}: {e}")
                continue
        
        logger.info(f"✓ Workflow complete. Executed {len(execution_trace)} agents\n")
        
        return {
            "workflow": workflow_name,
            "status": "success",
            "execution_trace": execution_trace,
            "results": data
        }
