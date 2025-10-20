"""
Orchestration Agent
Coordinates all agents and manages workflow execution.
Implements composite reasoning with human-in-the-loop review.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import uuid
from ..base_agent import BaseAgent, AgentContext, AgentOutput

# Import all agents
from ..ingestion.data_ingestion_agent import DataIngestionAgent, RoommateSurveyIngestionAgent
from ..knowledge.knowledge_graph_agent import KnowledgeGraphAgent
from ..analysis.listing_analysis_agent import ListingAnalysisAgent, ImageAnalysisAgent
from ..matching.roommate_matching_agent import RoommateMatchingAgent
from ..ranking.ranking_agent import RankingScoringAgent, CommuteScoringAgent
from ..planning.route_planning_agent import RoutePlanningAgent, ComplianceSafetyAgent
from ..explanation.explanation_agent import ExplanationAgent, FeedbackLearningAgent


class OrchestrationAgent(BaseAgent):
    """
    Main orchestrator for RentConnect-C3AN.
    Coordinates workflows:
    1. Property search & ranking
    2. Roommate matching
    3. Tour planning
    4. Compliance checking
    5. Explanation generation
    
    Implements human-in-the-loop for critical decisions.
    C3AN: Composite reasoning, Planning, Safety (human oversight)
    """
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__("OrchestrationAgent", config)
        
        # Initialize all agents
        self.agents = {
            'data_ingestion': DataIngestionAgent(config),
            'survey_ingestion': RoommateSurveyIngestionAgent(config),
            'knowledge_graph': KnowledgeGraphAgent(config),
            'listing_analysis': ListingAnalysisAgent(config),
            'image_analysis': ImageAnalysisAgent(config),
            'roommate_matching': RoommateMatchingAgent(config),
            'ranking_scoring': RankingScoringAgent(config),
            'commute_scoring': CommuteScoringAgent(config),
            'route_planning': RoutePlanningAgent(config),
            'compliance_safety': ComplianceSafetyAgent(config),
            'explanation': ExplanationAgent(config),
            'feedback_learning': FeedbackLearningAgent(config)
        }
        
        # Workflow definitions
        self.workflows = {
            'property_search': self._workflow_property_search,
            'roommate_matching': self._workflow_roommate_matching,
            'tour_planning': self._workflow_tour_planning,
            'listing_verification': self._workflow_listing_verification
        }
        
    def process(self, input_data: Any, context: AgentContext) -> AgentOutput:
        """
        Execute a workflow.
        
        Args:
            input_data: Dict with:
                - 'workflow': workflow name
                - 'workflow_input': input for the workflow
                - 'human_review': whether to require human approval for critical steps
        """
        if not self.validate_input(input_data):
            return self.create_output(
                result=None, confidence=0.0, explanation="Invalid input",
                attribution=[], errors=["Validation failed"]
            )
        
        workflow_name = input_data.get('workflow')
        workflow_input = input_data.get('workflow_input', {})
        human_review = input_data.get('human_review', True)
        
        if workflow_name not in self.workflows:
            return self.create_output(
                result=None, confidence=0.0,
                explanation=f"Unknown workflow: {workflow_name}",
                attribution=[], errors=[f"Workflow '{workflow_name}' not found"]
            )
        
        # Execute workflow
        workflow_func = self.workflows[workflow_name]
        result = workflow_func(workflow_input, context, human_review)
        
        return result
    
    def validate_input(self, input_data: Any) -> bool:
        return isinstance(input_data, dict) and 'workflow' in input_data
    
    def _workflow_property_search(
        self,
        workflow_input: Dict,
        context: AgentContext,
        human_review: bool
    ) -> AgentOutput:
        """
        Workflow: Property Search & Ranking
        Steps:
        1. Ingest listings from sources
        2. Analyze listings for risk
        3. Check compliance
        4. Compute commute scores
        5. Rank listings
        6. Generate explanations
        """
        self.logger.info("Starting property_search workflow")
        
        steps_completed = []
        errors = []
        
        # Step 1: Ingest listings
        ingestion_result = self.agents['data_ingestion'].process(
            {
                'sources': workflow_input.get('data_sources', ['zillow_zori', 'redfin_rental']),
                'filters': workflow_input.get('filters', {})
            },
            context
        )
        steps_completed.append("Data ingestion")
        
        if ingestion_result.errors:
            errors.extend(ingestion_result.errors)
        
        # Get listings
        ingested_data = ingestion_result.result or {}
        all_listings = []
        for source, listings in ingested_data.items():
            all_listings.extend(listings)
        
        # Step 2: Analyze listings
        analyzed_listings = []
        for listing in all_listings:
            analysis_result = self.agents['listing_analysis'].process(
                {'listing': listing, 'check_types': ['scam', 'price', 'features']},
                context
            )
            
            if analysis_result.result:
                listing_data = listing.copy()
                listing_data['analysis'] = analysis_result.result
                analyzed_listings.append(listing_data)
        
        steps_completed.append(f"Listing analysis ({len(analyzed_listings)} listings)")
        
        # Step 3: Compliance check
        compliant_listings = []
        for listing in analyzed_listings:
            compliance_result = self.agents['compliance_safety'].process(
                {'listing': listing, 'check_types': ['fha', 'safety']},
                context
            )
            
            if compliance_result.result and compliance_result.result.get('compliant'):
                listing['compliance'] = compliance_result.result
                compliant_listings.append(listing)
        
        steps_completed.append(f"Compliance check (passed: {len(compliant_listings)})")
        
        # Step 4: Compute commute scores
        user_location = workflow_input.get('user_location', (33.9937, -81.0266))
        for listing in compliant_listings:
            if 'lat' in listing and 'lon' in listing:
                commute_result = self.agents['commute_scoring'].process(
                    {
                        'property_location': (listing['lat'], listing['lon']),
                        'modes': ['walk', 'transit', 'drive']
                    },
                    context
                )
                
                if commute_result.result:
                    listing['commute'] = commute_result.result
                    listing['commute_time'] = commute_result.result.get('best_time', 30)
        
        steps_completed.append("Commute scoring")
        
        # Step 5: Rank listings
        ranking_result = self.agents['ranking_scoring'].process(
            {
                'listings': compliant_listings,
                'user_preferences': workflow_input.get('preferences', {}),
                'constraints': workflow_input.get('constraints', {})
            },
            context
        )
        
        steps_completed.append("Ranking")
        
        # Step 6: Generate explanations for top listings
        ranked_listings = ranking_result.result.get('ranked_listings', [])
        for listing in ranked_listings[:5]:  # Top 5
            explanation_result = self.agents['explanation'].process(
                {
                    'decision_type': 'ranking',
                    'decision_data': listing,
                    'explanation_level': 'detailed'
                },
                context
            )
            
            if explanation_result.result:
                listing['explanation_text'] = explanation_result.result['explanation']
        
        steps_completed.append("Explanation generation")
        
        # Human review checkpoint (if enabled)
        if human_review and len(ranked_listings) > 0:
            self.log_decision(
                "Property search complete - awaiting human review",
                f"Found {len(ranked_listings)} ranked properties",
                context
            )
            steps_completed.append("Human review checkpoint")
        
        # Final result
        return self.create_output(
            result={
                'ranked_listings': ranked_listings[:20],  # Top 20
                'total_found': len(all_listings),
                'total_analyzed': len(analyzed_listings),
                'total_compliant': len(compliant_listings),
                'total_ranked': len(ranked_listings),
                'workflow_steps': steps_completed
            },
            confidence=0.9,
            explanation=f"Property search complete: {len(ranked_listings)} listings ranked",
            attribution=["Data sources", "Risk analysis", "Compliance checks", "Multi-criteria ranking"],
            errors=errors
        )
    
    def _workflow_roommate_matching(
        self,
        workflow_input: Dict,
        context: AgentContext,
        human_review: bool
    ) -> AgentOutput:
        """
        Workflow: Roommate Matching
        Steps:
        1. Ingest roommate surveys
        2. Check Fair Housing compliance
        3. Perform matching
        4. Generate explanations
        """
        self.logger.info("Starting roommate_matching workflow")
        
        steps_completed = []
        
        # Step 1: Ingest surveys (assumed already done, load profiles)
        profiles = workflow_input.get('profiles', [])
        steps_completed.append(f"Loaded {len(profiles)} profiles")
        
        # Step 2: Compliance check on profiles
        compliant_profiles = []
        for profile in profiles:
            # Check via knowledge graph
            kg_result = self.agents['knowledge_graph'].process(
                {
                    'operation': 'check_rule',
                    'data': profile,
                    'rule_ids': ['fha_protected_classes']
                },
                context
            )
            
            if kg_result.result and kg_result.result.get('compliant'):
                compliant_profiles.append(profile)
        
        steps_completed.append(f"Compliance check (passed: {len(compliant_profiles)})")
        
        # Step 3: Perform matching
        matching_result = self.agents['roommate_matching'].process(
            {
                'profiles': compliant_profiles,
                'match_type': workflow_input.get('match_type', 'one_to_one')
            },
            context
        )
        
        matches = matching_result.result.get('matches', [])
        steps_completed.append(f"Matching ({len(matches)} matches)")
        
        # Step 4: Generate explanations
        for match in matches:
            explanation_result = self.agents['explanation'].process(
                {
                    'decision_type': 'match',
                    'decision_data': match,
                    'explanation_level': 'detailed'
                },
                context
            )
            
            if explanation_result.result:
                match['explanation_text'] = explanation_result.result['explanation']
        
        steps_completed.append("Explanation generation")
        
        # Human review checkpoint
        if human_review and len(matches) > 0:
            self.log_decision(
                "Roommate matching complete - awaiting human review",
                f"Found {len(matches)} matches",
                context
            )
            steps_completed.append("Human review checkpoint")
        
        return self.create_output(
            result={
                'matches': matches,
                'total_profiles': len(profiles),
                'compliant_profiles': len(compliant_profiles),
                'workflow_steps': steps_completed
            },
            confidence=matching_result.confidence,
            explanation=f"Roommate matching complete: {len(matches)} matches",
            attribution=matching_result.attribution,
            errors=matching_result.errors
        )
    
    def _workflow_tour_planning(
        self,
        workflow_input: Dict,
        context: AgentContext,
        human_review: bool
    ) -> AgentOutput:
        """
        Workflow: Tour Planning
        Steps:
        1. Get selected properties
        2. Get student class schedule
        3. Plan optimal route
        4. Generate explanation
        """
        self.logger.info("Starting tour_planning workflow")
        
        steps_completed = []
        
        # Step 1: Get properties
        properties = workflow_input.get('properties', [])
        steps_completed.append(f"Selected {len(properties)} properties")
        
        # Step 2: Get schedule
        class_schedule = workflow_input.get('class_schedule', [])
        steps_completed.append(f"Loaded schedule ({len(class_schedule)} classes)")
        
        # Step 3: Plan route
        route_result = self.agents['route_planning'].process(
            {
                'properties': properties,
                'class_schedule': class_schedule,
                'date': workflow_input.get('tour_date'),
                'start_location': workflow_input.get('start_location')
            },
            context
        )
        
        route = route_result.result.get('route', [])
        steps_completed.append(f"Route planned ({len(route)} stops)")
        
        # Step 4: Generate explanation
        explanation_result = self.agents['explanation'].process(
            {
                'decision_type': 'route',
                'decision_data': route_result.result,
                'explanation_level': 'detailed'
            },
            context
        )
        
        explanation_text = ""
        if explanation_result.result:
            explanation_text = explanation_result.result['explanation']
        
        steps_completed.append("Explanation generation")
        
        return self.create_output(
            result={
                'route': route,
                'time_windows': route_result.result.get('time_windows', []),
                'explanation_text': explanation_text,
                'workflow_steps': steps_completed
            },
            confidence=route_result.confidence,
            explanation=f"Tour planned: {len(route)} properties",
            attribution=route_result.attribution,
            errors=route_result.errors
        )
    
    def _workflow_listing_verification(
        self,
        workflow_input: Dict,
        context: AgentContext,
        human_review: bool
    ) -> AgentOutput:
        """
        Workflow: Listing Verification (for landlords/admins)
        Steps:
        1. Analyze listing for risks
        2. Check compliance
        3. Analyze images
        4. Generate verification report
        """
        self.logger.info("Starting listing_verification workflow")
        
        steps_completed = []
        
        listing = workflow_input.get('listing', {})
        
        # Step 1: Risk analysis
        risk_result = self.agents['listing_analysis'].process(
            {'listing': listing, 'check_types': ['scam', 'price', 'features']},
            context
        )
        steps_completed.append("Risk analysis")
        
        # Step 2: Compliance check
        compliance_result = self.agents['compliance_safety'].process(
            {'listing': listing, 'check_types': ['fha', 'safety', 'landlord']},
            context
        )
        steps_completed.append("Compliance check")
        
        # Step 3: Image analysis
        images = listing.get('images', [])
        image_result = self.agents['image_analysis'].process(
            {'images': images},
            context
        )
        steps_completed.append("Image analysis")
        
        # Step 4: Generate report
        verification_report = {
            'listing_id': listing.get('listing_id'),
            'risk_assessment': risk_result.result,
            'compliance': compliance_result.result,
            'image_analysis': image_result.result,
            'overall_status': 'pending_review',
            'requires_human_review': False
        }
        
        # Determine if human review needed
        if risk_result.result and risk_result.result.get('risk_score', 0) > 0.5:
            verification_report['requires_human_review'] = True
            verification_report['review_reason'] = "High risk score detected"
        
        if compliance_result.result and not compliance_result.result.get('compliant'):
            verification_report['requires_human_review'] = True
            verification_report['review_reason'] = "Compliance violations detected"
        
        steps_completed.append("Verification report generated")
        
        if human_review or verification_report['requires_human_review']:
            self.log_decision(
                "Listing verification complete - human review required",
                verification_report.get('review_reason', 'Standard review'),
                context
            )
            steps_completed.append("Human review required")
        
        return self.create_output(
            result={
                'verification_report': verification_report,
                'workflow_steps': steps_completed
            },
            confidence=0.8,
            explanation=f"Verification complete for listing {listing.get('listing_id')}",
            attribution=["Risk analysis", "Compliance checks", "Image analysis"],
            errors=[]
        )
    
    def get_agent_status(self) -> Dict[str, str]:
        """Get status of all agents"""
        return {
            name: "active" for name in self.agents.keys()
        }
    
    def execute_human_review(
        self,
        decision_id: str,
        approved: bool,
        feedback: Optional[str] = None
    ) -> Dict:
        """
        Execute human review decision.
        C3AN: Human-in-the-loop, Safety
        """
        self.logger.info(f"Human review: {decision_id} - {'Approved' if approved else 'Rejected'}")
        
        return {
            'decision_id': decision_id,
            'approved': approved,
            'feedback': feedback,
            'timestamp': datetime.utcnow().isoformat()
        }
