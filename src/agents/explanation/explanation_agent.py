"""
Explanation Agent
Generates clear, traceable explanations for all system decisions.
C3AN: Explainability, Interpretability, Attribution
"""

from typing import Any, Dict, List, Optional
from ..base_agent import BaseAgent, AgentContext, AgentOutput


class ExplanationAgent(BaseAgent):
    """
    Generates explanations for:
    - Rankings and scores
    - Roommate matches
    - Route plans
    - Compliance decisions
    - Risk assessments
    """
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__("ExplanationAgent", config)
        
    def process(self, input_data: Any, context: AgentContext) -> AgentOutput:
        """
        Generate explanation for a decision.
        
        Args:
            input_data: Dict with:
                - 'decision_type': type of decision to explain
                - 'decision_data': the decision details
                - 'explanation_level': 'brief', 'detailed', 'technical'
        """
        if not self.validate_input(input_data):
            return self.create_output(
                result=None, confidence=0.0, explanation="Invalid input",
                attribution=[], errors=["Validation failed"]
            )
        
        decision_type = input_data.get('decision_type')
        decision_data = input_data.get('decision_data', {})
        level = input_data.get('explanation_level', 'detailed')
        
        if decision_type == 'ranking':
            explanation = self._explain_ranking(decision_data, level)
        elif decision_type == 'match':
            explanation = self._explain_match(decision_data, level)
        elif decision_type == 'risk':
            explanation = self._explain_risk(decision_data, level)
        elif decision_type == 'route':
            explanation = self._explain_route(decision_data, level)
        else:
            explanation = "Unknown decision type"
        
        return self.create_output(
            result={'explanation': explanation},
            confidence=1.0,
            explanation=explanation[:200] + "..." if len(explanation) > 200 else explanation,
            attribution=["Decision traceback", "Rule references"],
            errors=[]
        )
    
    def validate_input(self, input_data: Any) -> bool:
        return isinstance(input_data, dict) and 'decision_type' in input_data
    
    def _explain_ranking(self, data: Dict, level: str) -> str:
        """Explain property ranking"""
        rank = data.get('rank', 0)
        score = data.get('overall_score', 0)
        breakdown = data.get('score_breakdown', {})
        
        if level == 'brief':
            return f"Ranked #{rank} with overall score {score:.2f}"
        
        parts = [f"This property ranked #{rank} with overall score {score:.2f}/1.0."]
        parts.append("\n\nScore breakdown:")
        
        for criterion, score_val in breakdown.items():
            parts.append(f"  • {criterion.replace('_', ' ').title()}: {score_val:.2f}")
        
        if data.get('is_pareto_optimal'):
            parts.append("\n✓ This is a Pareto-optimal option (no other property is strictly better in all criteria).")
        
        return "\n".join(parts)
    
    def _explain_match(self, data: Dict, level: str) -> str:
        """Explain roommate match"""
        users = data.get('users', [])
        score = data.get('compatibility_score', 0)
        shared = data.get('shared_constraints', [])
        
        if level == 'brief':
            return f"Matched with compatibility score {score:.2f}"
        
        parts = [f"Roommate match between {' and '.join(users)} with {score:.2f} compatibility."]
        
        if shared:
            parts.append("\n\nShared preferences:")
            for item in shared:
                parts.append(f"  • {item}")
        
        parts.append("\n\nThis match respects all hard constraints and optimizes soft preferences.")
        
        return "\n".join(parts)
    
    def _explain_risk(self, data: Dict, level: str) -> str:
        """Explain risk assessment"""
        risk_score = data.get('risk_score', 0)
        flags = data.get('risk_flags', [])
        
        if level == 'brief':
            return f"Risk score: {risk_score:.2f}"
        
        parts = [f"Risk assessment: {risk_score:.2f}/1.0"]
        
        if risk_score < 0.3:
            parts.append("(LOW RISK)")
        elif risk_score < 0.7:
            parts.append("(MODERATE RISK)")
        else:
            parts.append("(HIGH RISK)")
        
        if flags:
            parts.append("\n\nRisk factors identified:")
            for flag in flags[:5]:  # Top 5
                parts.append(f"  ⚠ {flag}")
        
        return "\n".join(parts)
    
    def _explain_route(self, data: Dict, level: str) -> str:
        """Explain tour route"""
        route = data.get('route', [])
        
        if level == 'brief':
            return f"Route with {len(route)} stops"
        
        parts = [f"Tour route visiting {len(route)} properties:"]
        
        for i, stop in enumerate(route[:5], 1):  # First 5
            arrival = stop.get('arrival_time', 'TBD')
            parts.append(f"  {i}. {stop['property'].get('address', 'Unknown')} at {arrival}")
        
        if len(route) > 5:
            parts.append(f"  ... and {len(route) - 5} more properties")
        
        return "\n".join(parts)


class FeedbackLearningAgent(BaseAgent):
    """
    Learns from user feedback and expert corrections.
    Updates recommendations over time.
    C3AN: Instructability, Adaptation
    """
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__("FeedbackLearningAgent", config)
        self.feedback_log = []
        
    def process(self, input_data: Any, context: AgentContext) -> AgentOutput:
        """
        Process user feedback.
        
        Args:
            input_data: Dict with:
                - 'feedback_type': 'rating', 'correction', 'preference_update'
                - 'target_id': ID of item being rated (listing, match, etc.)
                - 'feedback_value': rating, correction details, etc.
        """
        if not self.validate_input(input_data):
            return self.create_output(
                result=None, confidence=0.0, explanation="Invalid input",
                attribution=[], errors=["Validation failed"]
            )
        
        feedback_type = input_data.get('feedback_type')
        target_id = input_data.get('target_id')
        feedback_value = input_data.get('feedback_value')
        
        # Store feedback
        self.feedback_log.append({
            'type': feedback_type,
            'target': target_id,
            'value': feedback_value,
            'timestamp': context.timestamp,
            'user_id': context.user_id
        })
        
        # Process based on type
        if feedback_type == 'rating':
            result = self._process_rating(target_id, feedback_value, context)
        elif feedback_type == 'correction':
            result = self._process_correction(target_id, feedback_value, context)
        elif feedback_type == 'preference_update':
            result = self._process_preference_update(feedback_value, context)
        else:
            result = {'status': 'unknown_type'}
        
        return self.create_output(
            result=result,
            confidence=1.0,
            explanation=f"Processed {feedback_type} feedback for {target_id}",
            attribution=["User feedback"],
            errors=[]
        )
    
    def validate_input(self, input_data: Any) -> bool:
        return (isinstance(input_data, dict) and 
                'feedback_type' in input_data and 
                'target_id' in input_data)
    
    def _process_rating(self, target_id: str, rating: float, context: AgentContext) -> Dict:
        """Process a rating (1-5 stars)"""
        # In production: update ML model weights, recommendation scores
        self.log_decision(
            f"Received rating {rating} for {target_id}",
            "Will adjust future recommendations",
            context
        )
        
        return {
            'status': 'rating_recorded',
            'target_id': target_id,
            'rating': rating
        }
    
    def _process_correction(self, target_id: str, correction: Dict, context: AgentContext) -> Dict:
        """Process an expert correction"""
        # In production: retrain model, update rules
        self.log_decision(
            f"Received correction for {target_id}",
            f"Correction: {correction}",
            context
        )
        
        return {
            'status': 'correction_applied',
            'target_id': target_id
        }
    
    def _process_preference_update(self, preferences: Dict, context: AgentContext) -> Dict:
        """Update user preferences"""
        # In production: update user profile, re-rank recommendations
        self.log_decision(
            "User preferences updated",
            f"New preferences: {preferences}",
            context
        )
        
        return {
            'status': 'preferences_updated',
            'preferences': preferences
        }
