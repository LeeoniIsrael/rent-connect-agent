"""
RentConnect-C3AN Agent System
4 Decision-Making Agents for Student Housing & Roommate Matching

The system has been refactored from 14 agents to 4 real agents:
- Only components making autonomous decisions are agents
- Data collection = preprocessing modules
- Analysis/lookup = tools
- Decision-making = agents

Agents:
1. roommate_matching: Stable matching with constraint satisfaction
2. ranking_scoring: Multi-objective property ranking
3. route_planning: Time-windowed tour optimization
4. feedback_learning: Learning from user/expert feedback
"""

# Export singleton agent instances (lowercase variables)
from .roommate_matching import roommate_matching, RoommateMatchingAgent, MatchResult
from .ranking_scoring import ranking_scoring, RankingScoringAgent, RankingResult
from .route_planning import route_planning, RoutePlanningAgent, RouteResult
from .feedback_learning import feedback_learning, FeedbackLearningAgent, FeedbackResult

__all__ = [
    # Singleton instances (for direct use)
    'roommate_matching',
    'ranking_scoring',
    'route_planning',
    'feedback_learning',
    
    # Classes (for testing/instantiation)
    'RoommateMatchingAgent',
    'RankingScoringAgent',
    'RoutePlanningAgent',
    'FeedbackLearningAgent',
    
    # Result types
    'MatchResult',
    'RankingResult',
    'RouteResult',
    'FeedbackResult'
]
