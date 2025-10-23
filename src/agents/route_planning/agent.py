"""
Route Planning Agent
Time-windowed tour planning with TSP optimization.

Input Streams:
- Property selections (from user)
- Class schedule (from user)
- Travel estimates (from ranking_scoring or Google Maps)
- Configuration (from config.agents_config)

Output Streams:
- Optimized tour route with arrival times
- Feasibility report
- Explanations (why this order)
"""

import logging
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
import math
from datetime import datetime, timedelta

from .config import (
    ALGORITHM,
    DEFAULT_VIEWING_DURATION,
    TRAVEL_TIME_BUFFER,
    MAX_STOPS_PER_DAY,
    MAX_TOUR_DURATION,
    TRANSPORT_MODE,
    RESPECT_CLASS_SCHEDULE,
    MIN_BREAK_DURATION,
    OPTIMIZATION_OBJECTIVE
)

logger = logging.getLogger(__name__)


@dataclass
class RouteResult:
    """Output from route planning"""
    tour_id: str
    stops: List[Dict[str, Any]]
    total_duration: int
    feasible: bool
    time_window_violations: int
    explanation: str


class RoutePlanningAgent:
    """
    Autonomous agent for property viewing tour optimization.
    Uses nearest-neighbor TSP with time window constraints.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.algorithm = ALGORITHM
        self.viewing_duration = DEFAULT_VIEWING_DURATION
        self.travel_buffer = TRAVEL_TIME_BUFFER
        self.max_stops = MAX_STOPS_PER_DAY
        self.max_duration = MAX_TOUR_DURATION
        self.transport_mode = TRANSPORT_MODE
        self.respect_schedule = RESPECT_CLASS_SCHEDULE
        self.min_break = MIN_BREAK_DURATION
        self.objective = OPTIMIZATION_OBJECTIVE
        
    def plan_route(
        self,
        properties: List[Dict[str, Any]],
        class_schedule: Optional[List[Dict[str, str]]] = None,
        start_time: Optional[str] = None
    ) -> RouteResult:
        """
        Main planning method - autonomous decision point.
        
        Args:
            properties: List of properties to visit (with locations)
            class_schedule: List of unavailable time blocks [{'start': 'HH:MM', 'end': 'HH:MM'}]
            start_time: Preferred start time ('HH:MM')
            
        Returns:
            RouteResult with optimized tour
        """
        self.logger.info(f"Planning route for {len(properties)} properties")
        
        # Validate input
        if len(properties) > self.max_stops:
            self.logger.warning(f"Too many stops ({len(properties)} > {self.max_stops})")
            properties = properties[:self.max_stops]
        
        # Extract available time windows
        time_windows = self._extract_time_windows(class_schedule)
        
        # Build distance matrix
        distance_matrix = self._build_distance_matrix(properties)
        
        # Run TSP algorithm
        route_order = self._nearest_neighbor_tsp(distance_matrix)
        
        # Schedule viewings in time windows
        scheduled_stops = self._schedule_viewings(
            properties,
            route_order,
            distance_matrix,
            time_windows,
            start_time
        )
        
        # Validate feasibility
        feasible, violations = self._check_feasibility(scheduled_stops, time_windows)
        
        # Calculate total duration
        total_duration = self._calculate_total_duration(scheduled_stops)
        
        # Generate explanation
        explanation = self._generate_explanation(scheduled_stops, route_order, feasible)
        
        self.logger.info(f"Route planning complete: {len(scheduled_stops)} stops, feasible={feasible}")
        
        return RouteResult(
            tour_id=f"tour_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            stops=scheduled_stops,
            total_duration=total_duration,
            feasible=feasible,
            time_window_violations=violations,
            explanation=explanation
        )
    
    def _extract_time_windows(self, class_schedule: Optional[List[Dict[str, str]]]) -> List[Tuple[int, int]]:
        """
        Extract available time windows from class schedule.
        Returns list of (start_minute, end_minute) tuples.
        """
        if not class_schedule or not self.respect_schedule:
            # Default: 8 AM to 8 PM
            return [(8 * 60, 20 * 60)]
        
        # Parse class times
        busy_periods = []
        for block in class_schedule:
            start_str = block['start']
            end_str = block['end']
            start_min = self._time_to_minutes(start_str)
            end_min = self._time_to_minutes(end_str)
            busy_periods.append((start_min, end_min))
        
        # Sort by start time
        busy_periods.sort()
        
        # Find gaps (available windows)
        available = []
        day_start = 8 * 60  # 8 AM
        day_end = 20 * 60   # 8 PM
        
        current = day_start
        for start, end in busy_periods:
            if current < start:
                available.append((current, start))
            current = max(current, end)
        
        if current < day_end:
            available.append((current, day_end))
        
        return available if available else [(day_start, day_end)]
    
    def _time_to_minutes(self, time_str: str) -> int:
        """Convert 'HH:MM' to minutes since midnight"""
        hours, minutes = map(int, time_str.split(':'))
        return hours * 60 + minutes
    
    def _minutes_to_time(self, minutes: int) -> str:
        """Convert minutes since midnight to 'HH:MM'"""
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours:02d}:{mins:02d}"
    
    def _build_distance_matrix(self, properties: List[Dict[str, Any]]) -> List[List[float]]:
        """Build distance/time matrix between all properties"""
        n = len(properties)
        matrix = [[0.0] * n for _ in range(n)]
        
        for i in range(n):
            for j in range(i+1, n):
                # Compute travel time (Haversine distance / mode speed)
                time = self._compute_travel_time(
                    (properties[i]['latitude'], properties[i]['longitude']),
                    (properties[j]['latitude'], properties[j]['longitude'])
                )
                matrix[i][j] = time
                matrix[j][i] = time  # Symmetric
        
        return matrix
    
    def _compute_travel_time(self, origin: Tuple[float, float], destination: Tuple[float, float]) -> float:
        """Compute travel time (minutes) between two locations"""
        lat1, lon1 = origin
        lat2, lon2 = destination
        
        # Haversine distance (km)
        R = 6371
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        
        # Mode speeds (km/h) from config
        from config.agents_config import RANKING_SCORING_CONFIG
        speeds = RANKING_SCORING_CONFIG['commute_config']['mode_speeds']
        
        # Time (minutes)
        speed = speeds.get(self.transport_mode, 20)
        time = (distance / speed) * 60
        
        return time + self.travel_buffer
    
    def _nearest_neighbor_tsp(self, distance_matrix: List[List[float]]) -> List[int]:
        """
        Nearest-neighbor TSP heuristic.
        Returns visit order (list of indices).
        """
        n = len(distance_matrix)
        if n == 0:
            return []
        
        visited = [False] * n
        route = [0]  # Start at first property
        visited[0] = True
        
        for _ in range(n - 1):
            current = route[-1]
            best_next = -1
            best_dist = float('inf')
            
            for j in range(n):
                if not visited[j] and distance_matrix[current][j] < best_dist:
                    best_dist = distance_matrix[current][j]
                    best_next = j
            
            if best_next != -1:
                route.append(best_next)
                visited[best_next] = True
        
        return route
    
    def _schedule_viewings(
        self,
        properties: List[Dict[str, Any]],
        route_order: List[int],
        distance_matrix: List[List[float]],
        time_windows: List[Tuple[int, int]],
        start_time: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Schedule viewings in optimal route order within time windows"""
        stops = []
        
        # Determine starting time
        if start_time:
            current_time = self._time_to_minutes(start_time)
        else:
            # Start at beginning of first available window
            current_time = time_windows[0][0] if time_windows else 8 * 60
        
        for i, prop_idx in enumerate(route_order):
            prop = properties[prop_idx]
            
            # Find suitable time window
            window_idx = self._find_suitable_window(
                current_time,
                self.viewing_duration,
                time_windows
            )
            
            if window_idx == -1:
                # No suitable window found, skip this property
                self.logger.warning(f"Could not schedule property {prop['listing_id']}")
                continue
            
            # Schedule viewing
            arrival_time = max(current_time, time_windows[window_idx][0])
            departure_time = arrival_time + self.viewing_duration
            
            # Travel time to next stop
            travel_to_next = 0
            if i < len(route_order) - 1:
                next_idx = route_order[i + 1]
                travel_to_next = distance_matrix[prop_idx][next_idx]
            
            stop = {
                'listing_id': prop['listing_id'],
                'arrival_time': self._minutes_to_time(arrival_time),
                'departure_time': self._minutes_to_time(departure_time),
                'viewing_duration': self.viewing_duration,
                'travel_to_next': int(travel_to_next),
                'location': (prop['latitude'], prop['longitude'])
            }
            stops.append(stop)
            
            # Update current time
            current_time = departure_time + travel_to_next + self.min_break
        
        return stops
    
    def _find_suitable_window(
        self,
        desired_time: int,
        duration: int,
        time_windows: List[Tuple[int, int]]
    ) -> int:
        """Find time window that can accommodate viewing at desired time"""
        for i, (start, end) in enumerate(time_windows):
            if desired_time >= start and desired_time + duration <= end:
                return i
        
        # Try to fit in next available window
        for i, (start, end) in enumerate(time_windows):
            if start >= desired_time and start + duration <= end:
                return i
        
        return -1  # No suitable window
    
    def _check_feasibility(
        self,
        stops: List[Dict[str, Any]],
        time_windows: List[Tuple[int, int]]
    ) -> Tuple[bool, int]:
        """Check if tour is feasible (no time window violations)"""
        violations = 0
        
        for stop in stops:
            arrival = self._time_to_minutes(stop['arrival_time'])
            departure = self._time_to_minutes(stop['departure_time'])
            
            # Check if viewing fits in any window
            fits = False
            for start, end in time_windows:
                if arrival >= start and departure <= end:
                    fits = True
                    break
            
            if not fits:
                violations += 1
        
        return violations == 0, violations
    
    def _calculate_total_duration(self, stops: List[Dict[str, Any]]) -> int:
        """Calculate total tour duration in minutes"""
        if not stops:
            return 0
        
        start = self._time_to_minutes(stops[0]['arrival_time'])
        end = self._time_to_minutes(stops[-1]['departure_time'])
        
        return end - start
    
    def _generate_explanation(
        self,
        stops: List[Dict[str, Any]],
        route_order: List[int],
        feasible: bool
    ) -> str:
        """Generate natural language explanation of route"""
        if not stops:
            return "No feasible tour found within available time windows."
        
        explanation = f"Planned {len(stops)}-stop tour using nearest-neighbor algorithm. "
        
        if feasible:
            explanation += f"Tour is feasible, total duration {self._calculate_total_duration(stops)} minutes. "
        else:
            explanation += "WARNING: Some viewings conflict with class schedule. "
        
        explanation += f"Visit order: {' → '.join(stop['listing_id'] for stop in stops)}. "
        
        # Explain optimization
        total_travel = sum(stop['travel_to_next'] for stop in stops)
        explanation += f"Total travel time: {int(total_travel)} minutes."
        
        return explanation


# Singleton instance (lowercase variable name)
route_planning = RoutePlanningAgent()
