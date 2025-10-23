"""
Route Planning Agent Configuration
Agent-specific settings (imports from main config)
"""

from config.agents_config import ROUTE_PLANNING_CONFIG

# Re-export for agent use
ALGORITHM = ROUTE_PLANNING_CONFIG['algorithm']
DEFAULT_VIEWING_DURATION = ROUTE_PLANNING_CONFIG['default_viewing_duration']
TRAVEL_TIME_BUFFER = ROUTE_PLANNING_CONFIG['travel_time_buffer']
MAX_STOPS_PER_DAY = ROUTE_PLANNING_CONFIG['max_stops_per_day']
MAX_TOUR_DURATION = ROUTE_PLANNING_CONFIG['max_tour_duration']
TRANSPORT_MODE = ROUTE_PLANNING_CONFIG['transport_mode']
RESPECT_CLASS_SCHEDULE = ROUTE_PLANNING_CONFIG['respect_class_schedule']
MIN_BREAK_DURATION = ROUTE_PLANNING_CONFIG['min_break_duration']
OPTIMIZATION_OBJECTIVE = ROUTE_PLANNING_CONFIG['optimization_objective']
ENABLE_GTFS_INTEGRATION = ROUTE_PLANNING_CONFIG['enable_gtfs_integration']
