"""
Feedback & Learning Agent Package
Exports the singleton agent instance
"""

from .agent import feedback_learning, FeedbackLearningAgent, FeedbackResult

__all__ = ['feedback_learning', 'FeedbackLearningAgent', 'FeedbackResult']
