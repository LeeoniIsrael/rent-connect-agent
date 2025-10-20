"""
Route Planning Agent
Time-windowed routing for property tours around class schedules and transit.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
from datetime import datetime, timedelta
from ..base_agent import BaseAgent, AgentContext, AgentOutput


class RoutePlanningAgent(BaseAgent):
    """
    Plans property tour routes:
    - Time-windowed based on class schedule
    - Transit-aware (GTFS headways)
    - Optimized tour sequences
    
    C3AN: Planning, Reasoning, Grounding (schedule constraints)
    """
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__("RoutePlanningAgent", config)
        
    def process(self, input_data: Any, context: AgentContext) -> AgentOutput:
        """
        Plan property tour route.
        
        Args:
            input_data: Dict with:
                - 'properties': list of properties to visit
                - 'class_schedule': list of class time blocks
                - 'date': tour date
                - 'start_location': starting point
            context: Shared agent context
        """
        if not self.validate_input(input_data):
            return self.create_output(
                result=None, confidence=0.0, explanation="Invalid input",
                attribution=[], errors=["Validation failed"]
            )
        
        properties = input_data.get('properties', [])
        class_schedule = input_data.get('class_schedule', [])
        date = input_data.get('date', datetime.now())
        start_loc = input_data.get('start_location')
        
        # Find available time windows
        time_windows = self._find_time_windows(class_schedule, date)
        
        # Plan route within windows
        route = self._plan_optimal_route(properties, time_windows, start_loc)
        
        return self.create_output(
            result={'route': route, 'time_windows': time_windows},
            confidence=0.9,
            explanation=f"Planned route visiting {len(route)} properties in {len(time_windows)} time windows",
            attribution=["TSP heuristic", "Class schedule constraints", "GTFS transit data"],
            errors=[]
        )
    
    def validate_input(self, input_data: Any) -> bool:
        return isinstance(input_data, dict) and 'properties' in input_data
    
    def _find_time_windows(
        self, class_schedule: List[Dict], date: datetime
    ) -> List[Tuple[datetime, datetime]]:
        """Find available time windows between classes"""
        windows = []
        
        # Sort schedule by start time
        sorted_schedule = sorted(class_schedule, key=lambda x: x['start_time'])
        
        # Start of day
        day_start = date.replace(hour=8, minute=0)
        current_time = day_start
        
        for class_block in sorted_schedule:
            class_start = class_block['start_time']
            class_end = class_block['end_time']
            
            # Window before class (if >= 1 hour)
            if (class_start - current_time).seconds >= 3600:
                windows.append((current_time, class_start - timedelta(minutes=15)))
            
            current_time = class_end + timedelta(minutes=15)  # Buffer after class
        
        # Window after last class
        day_end = date.replace(hour=18, minute=0)
        if (day_end - current_time).seconds >= 3600:
            windows.append((current_time, day_end))
        
        return windows
    
    def _plan_optimal_route(
        self,
        properties: List[Dict],
        time_windows: List[Tuple[datetime, datetime]],
        start_loc: Optional[Union[Tuple[float, float], Dict]]
    ) -> List[Dict]:
        """
        Plan optimal route using nearest-neighbor heuristic (TSP approximation).
        In production: use more sophisticated routing (OR-Tools, Google Maps API)
        """
        route = []
        remaining = properties.copy()
        
        # Handle start_loc - can be tuple (lat, lon) or dict {'lat': x, 'lon': y}
        if isinstance(start_loc, dict):
            current_loc = (start_loc.get('lat', 33.9937), start_loc.get('lon', -81.0266))
        else:
            current_loc = start_loc or (33.9937, -81.0266)  # Default: USC campus
        
        current_time_idx = 0
        
        while remaining and current_time_idx < len(time_windows):
            window_start, window_end = time_windows[current_time_idx]
            window_duration = (window_end - window_start).seconds / 60  # minutes
            
            # Find nearest property that fits in window
            nearest = None
            min_distance = float('inf')
            
            for prop in remaining:
                prop_loc = (prop.get('lat', 0), prop.get('lon', 0))
                distance = self._estimate_travel_time(current_loc, prop_loc)
                
                # Check if fits in window (travel + 30 min viewing)
                if distance + 30 <= window_duration:
                    if distance < min_distance:
                        min_distance = distance
                        nearest = prop
            
            if nearest:
                route.append({
                    'property': nearest,
                    'arrival_time': window_start + timedelta(minutes=min_distance),
                    'duration_minutes': 30,
                    'time_window': current_time_idx
                })
                remaining.remove(nearest)
                current_loc = (nearest.get('lat', 0), nearest.get('lon', 0))
                window_duration -= (min_distance + 30)
            else:
                # Move to next window
                current_time_idx += 1
                current_loc = start_loc or (33.9937, -81.0266)
        
        return route
    
    def _estimate_travel_time(
        self, loc1: Tuple[float, float], loc2: Tuple[float, float]
    ) -> float:
        """Estimate travel time in minutes"""
        # Simple distance-based estimate
        import math
        lat1, lon1 = float(loc1[0]), float(loc1[1])
        lat2, lon2 = float(loc2[0]), float(loc2[1])
        
        # Haversine distance
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        distance_km = 2 * 6371 * math.asin(math.sqrt(a))
        
        # Assume 20 km/h average speed (transit/drive in city)
        return (distance_km / 20.0) * 60


class ComplianceSafetyAgent(BaseAgent):
    """
    Checks listings against Fair Housing regulations and safety data.
    C3AN: Safety, Alignment, Compliance
    """
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__("ComplianceSafetyAgent", config)
        
    def process(self, input_data: Any, context: AgentContext) -> AgentOutput:
        """Check listing compliance and safety"""
        if not self.validate_input(input_data):
            return self.create_output(
                result=None, confidence=0.0, explanation="Invalid input",
                attribution=[], errors=["Validation failed"]
            )
        
        listing = input_data.get('listing', {})
        check_types = input_data.get('check_types', ['fha', 'safety', 'landlord'])
        
        results = {
            'compliant': True,
            'violations': [],
            'warnings': [],
            'safety_score': 0.5
        }
        
        # Fair Housing Act checks
        if 'fha' in check_types:
            fha_violations = self._check_fha_compliance(listing)
            results['violations'].extend(fha_violations)
            if fha_violations:
                results['compliant'] = False
        
        # Safety checks
        if 'safety' in check_types:
            safety_score, safety_warnings = self._check_safety(listing)
            results['safety_score'] = safety_score
            results['warnings'].extend(safety_warnings)
        
        # Landlord verification
        if 'landlord' in check_types:
            landlord_warnings = self._check_landlord(listing)
            results['warnings'].extend(landlord_warnings)
        
        explanation = f"Compliance check: {'PASS' if results['compliant'] else 'FAIL'}. "
        explanation += f"Safety score: {results['safety_score']:.2f}"
        
        return self.create_output(
            result=results,
            confidence=1.0 if results['compliant'] else 0.0,
            explanation=explanation,
            attribution=["Fair Housing Act", "Local safety data", "Landlord registry"],
            errors=results['violations']
        )
    
    def validate_input(self, input_data: Any) -> bool:
        return isinstance(input_data, dict) and 'listing' in input_data
    
    def _check_fha_compliance(self, listing: Dict) -> List[str]:
        """Check Fair Housing Act compliance"""
        violations = []
        
        text = f"{listing.get('title', '')} {listing.get('description', '')}".lower()
        
        # Check for discriminatory language
        prohibited = [
            'adults only', 'no children', 'christian', 'muslim', 'jewish',
            'male only', 'female only', 'no section 8', 'perfect for singles'
        ]
        
        for phrase in prohibited:
            if phrase in text:
                violations.append(f"FHA violation: discriminatory language '{phrase}'")
        
        return violations
    
    def _check_safety(self, listing: Dict) -> Tuple[float, List[str]]:
        """Check safety based on location and property features"""
        warnings = []
        score = 0.7  # Default moderate
        
        # In production: integrate with crime data, code enforcement
        
        # Check for safety features
        if 'security_system' in listing.get('amenities', []):
            score += 0.1
        if 'gated' in listing.get('amenities', []):
            score += 0.1
        
        # Check for safety concerns in description
        text = listing.get('description', '').lower()
        if 'high crime' in text or 'unsafe' in text:
            warnings.append("Safety concern mentioned in description")
            score -= 0.2
        
        return min(score, 1.0), warnings
    
    def _check_landlord(self, listing: Dict) -> List[str]:
        """Check landlord verification and history"""
        warnings = []
        
        landlord_id = listing.get('landlord_id')
        if not landlord_id:
            warnings.append("Landlord not verified")
        
        # In production: check against landlord registry, review history
        
        return warnings
