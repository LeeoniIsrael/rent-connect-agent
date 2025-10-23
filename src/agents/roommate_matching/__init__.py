"""
Roommate Matching Agent Package
Exports the singleton agent instance
"""

from .agent import roommate_matching, RoommateMatchingAgent, MatchResult

__all__ = ['roommate_matching', 'RoommateMatchingAgent', 'MatchResult']
