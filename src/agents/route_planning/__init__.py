"""
Route Planning Agent Package
Exports the singleton agent instance
"""

from .agent import route_planning, RoutePlanningAgent, RouteResult

__all__ = ['route_planning', 'RoutePlanningAgent', 'RouteResult']
