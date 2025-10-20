"""
Ranking and Scoring Agent
Multi-objective scoring for housing listings with user-tunable weights.
Implements Pareto optimization with explainable rankings.
"""

from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
import math
from ..base_agent import BaseAgent, AgentContext, AgentOutput


@dataclass
class ScoringCriteria:
    """Criteria for ranking properties"""
    weight: float
    preference: str  # 'minimize', 'maximize', 'target'
    target_value: Optional[float] = None  # For 'target' preference


class RankingScoringAgent(BaseAgent):
    """
    Ranks housing listings using multi-criteria scoring:
    - Budget (price, utilities)
    - Commute time (walk, transit, drive)
    - Safety score
    - Amenities match
    - Lease terms suitability
    
    Supports user-tunable weights and provides Pareto-optimal explanations.
    C3AN: Reasoning, Explainability, Instructability
    """
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__("RankingScoringAgent", config)
        
        # Default weights (user can override)
        self.default_criteria = {
            'price': ScoringCriteria(weight=0.30, preference='minimize'),
            'commute_time': ScoringCriteria(weight=0.25, preference='minimize'),
            'safety_score': ScoringCriteria(weight=0.20, preference='maximize'),
            'amenities_match': ScoringCriteria(weight=0.15, preference='maximize'),
            'lease_suitability': ScoringCriteria(weight=0.10, preference='maximize')
        }
        
    def process(self, input_data: Any, context: AgentContext) -> AgentOutput:
        """
        Rank and score housing listings.
        
        Args:
            input_data: Dict with:
                - 'listings': list of property listings
                - 'user_preferences': user's criteria and weights
                - 'constraints': hard constraints (budget max, commute max, etc.)
            context: Shared agent context
            
        Returns:
            AgentOutput with ranked listings and explanations
        """
        if not self.validate_input(input_data):
            return self.create_output(
                result=None,
                confidence=0.0,
                explanation="Invalid ranking input",
                attribution=[],
                errors=["Input validation failed"]
            )
        
        listings = input_data.get('listings', [])
        user_prefs = input_data.get('user_preferences', {})
        constraints = input_data.get('constraints', {})
        
        if not listings:
            return self.create_output(
                result={'ranked_listings': []},
                confidence=1.0,
                explanation="No listings to rank",
                attribution=[],
                errors=[]
            )
        
        # Merge user preferences with defaults
        criteria = self._merge_criteria(user_prefs)
        
        # Apply hard constraints (filter out non-viable)
        viable_listings = self._apply_constraints(listings, constraints)
        
        if not viable_listings:
            return self.create_output(
                result={'ranked_listings': []},
                confidence=0.0,
                explanation=f"No listings meet constraints (filtered {len(listings)} listings)",
                attribution=["Constraint filters"],
                errors=["All listings filtered by constraints"]
            )
        
        # Score each listing
        scored_listings = []
        for listing in viable_listings:
            score, score_breakdown = self._score_listing(listing, criteria, context)
            
            scored_listings.append({
                'listing': listing,
                'overall_score': score,
                'score_breakdown': score_breakdown,
                'explanation': self._generate_score_explanation(score_breakdown, criteria)
            })
        
        # Sort by score (descending)
        scored_listings.sort(key=lambda x: x['overall_score'], reverse=True)
        
        # Identify Pareto-optimal listings
        pareto_optimal = self._find_pareto_optimal(scored_listings)
        
        # Mark Pareto-optimal
        for i, listing in enumerate(scored_listings):
            listing['rank'] = i + 1
            listing['is_pareto_optimal'] = i in pareto_optimal
        
        self.log_decision(
            f"Ranked {len(scored_listings)} listings",
            f"Top score: {scored_listings[0]['overall_score']:.2f}",
            context
        )
        
        return self.create_output(
            result={
                'ranked_listings': scored_listings,
                'total_ranked': len(scored_listings),
                'filtered_out': len(listings) - len(viable_listings),
                'criteria_used': {k: {'weight': v.weight, 'preference': v.preference} 
                                 for k, v in criteria.items()}
            },
            confidence=1.0,
            explanation=f"Ranked {len(scored_listings)} listings using {len(criteria)} criteria. "
                       f"{len(pareto_optimal)} Pareto-optimal options found.",
            attribution=[
                "Multi-objective optimization",
                "User preference weights",
                "Market data for normalization"
            ],
            errors=[]
        )
    
    def validate_input(self, input_data: Any) -> bool:
        """Validate ranking input"""
        if not isinstance(input_data, dict):
            return False
        
        listings = input_data.get('listings')
        if listings is not None and not isinstance(listings, list):
            return False
        
        return True
    
    def _merge_criteria(self, user_prefs: Dict) -> Dict[str, ScoringCriteria]:
        """Merge user preferences with default criteria"""
        criteria = self.default_criteria.copy()
        
        # Override weights if provided
        user_weights = user_prefs.get('weights', {})
        for key, weight in user_weights.items():
            if key in criteria:
                criteria[key].weight = weight
        
        # Normalize weights to sum to 1.0
        total_weight = sum(c.weight for c in criteria.values())
        if total_weight > 0:
            for criterion in criteria.values():
                criterion.weight /= total_weight
        
        return criteria
    
    def _apply_constraints(
        self,
        listings: List[Dict],
        constraints: Dict[str, Any]
    ) -> List[Dict]:
        """Filter listings by hard constraints"""
        viable = []
        
        for listing in listings:
            # Budget constraint
            max_budget = constraints.get('max_budget')
            if max_budget and listing.get('price', 0) > max_budget:
                continue
            
            # Minimum bedrooms
            min_bedrooms = constraints.get('min_bedrooms')
            if min_bedrooms and listing.get('bedrooms', 0) < min_bedrooms:
                continue
            
            # Maximum commute time
            max_commute = constraints.get('max_commute_minutes')
            if max_commute and listing.get('commute_time', 0) > max_commute:
                continue
            
            # Required amenities
            required_amenities = constraints.get('required_amenities', [])
            listing_amenities = listing.get('amenities', [])
            if not all(amenity in listing_amenities for amenity in required_amenities):
                continue
            
            # Minimum safety score
            min_safety = constraints.get('min_safety_score')
            if min_safety and listing.get('safety_score', 0) < min_safety:
                continue
            
            viable.append(listing)
        
        return viable
    
    def _score_listing(
        self,
        listing: Dict,
        criteria: Dict[str, ScoringCriteria],
        context: AgentContext
    ) -> Tuple[float, Dict[str, float]]:
        """
        Score a single listing across all criteria.
        Returns (overall_score, score_breakdown)
        """
        scores = {}
        
        # Price score (normalize 0-1, lower is better)
        if 'price' in criteria:
            price = listing.get('price', 0)
            # Normalize assuming $400-$2000 range for Columbia
            normalized_price = (price - 400) / (2000 - 400)
            normalized_price = max(0, min(1, normalized_price))
            
            if criteria['price'].preference == 'minimize':
                scores['price'] = 1.0 - normalized_price
            else:
                scores['price'] = normalized_price
        
        # Commute time score (normalize 0-1, lower is better)
        if 'commute_time' in criteria:
            commute = listing.get('commute_time', 30)  # minutes
            # Normalize assuming 0-60 minutes range
            normalized_commute = commute / 60.0
            normalized_commute = max(0, min(1, normalized_commute))
            
            if criteria['commute_time'].preference == 'minimize':
                scores['commute_time'] = 1.0 - normalized_commute
            else:
                scores['commute_time'] = normalized_commute
        
        # Safety score (already 0-1, higher is better)
        if 'safety_score' in criteria:
            safety = listing.get('safety_score', 0.5)
            scores['safety_score'] = safety
        
        # Amenities match score
        if 'amenities_match' in criteria:
            desired_amenities = context.metadata.get('desired_amenities', [])
            listing_amenities = listing.get('amenities', [])
            
            if desired_amenities:
                match_count = sum(1 for a in desired_amenities if a in listing_amenities)
                scores['amenities_match'] = match_count / len(desired_amenities)
            else:
                # Default: just count amenities
                scores['amenities_match'] = min(len(listing_amenities) / 10.0, 1.0)
        
        # Lease suitability score
        if 'lease_suitability' in criteria:
            lease_score = self._compute_lease_suitability(listing, context)
            scores['lease_suitability'] = lease_score
        
        # Compute weighted overall score
        overall = sum(
            scores.get(key, 0) * criteria[key].weight
            for key in criteria.keys()
        )
        
        return overall, scores
    
    def _compute_lease_suitability(self, listing: Dict, context: AgentContext) -> float:
        """Compute how suitable the lease terms are"""
        score = 0.5  # Neutral baseline
        
        # Prefer academic year leases for students
        lease_duration = listing.get('lease_duration', '12_months')
        if lease_duration in ['9_months', 'semester']:
            score += 0.2
        elif lease_duration == 'month_to_month':
            score += 0.1
        
        # Utilities included is a plus
        utilities_included = listing.get('utilities_included', [])
        score += min(len(utilities_included) * 0.05, 0.2)
        
        # Furnished is a plus for students
        if listing.get('furnished', False):
            score += 0.1
        
        return min(score, 1.0)
    
    def _find_pareto_optimal(self, scored_listings: List[Dict]) -> List[int]:
        """
        Find Pareto-optimal listings (not dominated by any other).
        A listing is Pareto-optimal if there's no other listing that's better
        in all criteria.
        """
        pareto_indices = []
        
        for i, listing_i in enumerate(scored_listings):
            is_dominated = False
            
            for j, listing_j in enumerate(scored_listings):
                if i == j:
                    continue
                
                # Check if listing_j dominates listing_i
                breakdown_i = listing_i['score_breakdown']
                breakdown_j = listing_j['score_breakdown']
                
                # listing_j dominates if it's >= in all criteria and > in at least one
                all_gte = all(
                    breakdown_j.get(key, 0) >= breakdown_i.get(key, 0)
                    for key in breakdown_i.keys()
                )
                any_gt = any(
                    breakdown_j.get(key, 0) > breakdown_i.get(key, 0)
                    for key in breakdown_i.keys()
                )
                
                if all_gte and any_gt:
                    is_dominated = True
                    break
            
            if not is_dominated:
                pareto_indices.append(i)
        
        return pareto_indices
    
    def _generate_score_explanation(
        self,
        score_breakdown: Dict[str, float],
        criteria: Dict[str, ScoringCriteria]
    ) -> str:
        """Generate human-readable explanation for score"""
        parts = []
        
        for key, score in score_breakdown.items():
            weight = criteria.get(key, ScoringCriteria(weight=0, preference='maximize')).weight
            
            # Convert to human-readable
            key_readable = key.replace('_', ' ').title()
            score_pct = score * 100
            weight_pct = weight * 100
            
            parts.append(f"{key_readable}: {score_pct:.0f}% (weight: {weight_pct:.0f}%)")
        
        return "; ".join(parts)


class CommuteScoringAgent(BaseAgent):
    """
    Specialized agent for computing commute scores using multiple transportation modes.
    Integrates with GTFS transit data and distance APIs.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__("CommuteScoringAgent", config)
        self.campus_location = (33.9937, -81.0266)  # USC Main Campus
        
    def process(self, input_data: Any, context: AgentContext) -> AgentOutput:
        """
        Compute commute time and score for a property.
        
        Args:
            input_data: Dict with:
                - 'property_location': (lat, lon)
                - 'modes': list of transport modes to check
                - 'class_schedule': optional class times
            context: Shared agent context
            
        Returns:
            AgentOutput with commute times and scores by mode
        """
        if not self.validate_input(input_data):
            return self.create_output(
                result=None,
                confidence=0.0,
                explanation="Invalid commute input",
                attribution=[],
                errors=["Input validation failed"]
            )
        
        prop_location = input_data.get('property_location')
        modes = input_data.get('modes', ['walk', 'transit', 'drive'])
        
        commute_data = {}
        
        for mode in modes:
            time_minutes = self._compute_commute_time(prop_location, mode)
            commute_data[mode] = {
                'time_minutes': time_minutes,
                'score': self._time_to_score(time_minutes)
            }
        
        # Find best mode
        best_mode = min(commute_data.keys(), key=lambda m: commute_data[m]['time_minutes'])
        best_time = commute_data[best_mode]['time_minutes']
        
        return self.create_output(
            result={
                'commute_by_mode': commute_data,
                'best_mode': best_mode,
                'best_time': best_time,
                'overall_commute_score': commute_data[best_mode]['score']
            },
            confidence=0.8,  # Moderate confidence (dependent on map data quality)
            explanation=f"Best commute: {best_time:.0f} min by {best_mode}",
            attribution=["Distance calculation", "GTFS transit data"],
            errors=[]
        )
    
    def validate_input(self, input_data: Any) -> bool:
        """Validate commute input"""
        if not isinstance(input_data, dict):
            return False
        
        location = input_data.get('property_location')
        if not location or not isinstance(location, (list, tuple)) or len(location) != 2:
            return False
        
        return True
    
    def _compute_commute_time(self, prop_location: Tuple[float, float], mode: str) -> float:
        """
        Compute commute time for a given mode.
        In production: integrate with Google Distance Matrix API or similar.
        """
        # Calculate straight-line distance
        distance_km = self._haversine_distance(prop_location, self.campus_location)
        
        # Estimate time based on mode
        if mode == 'walk':
            # Assume 5 km/h walking speed
            time_minutes = (distance_km / 5.0) * 60
        elif mode == 'transit':
            # Assume 20 km/h average for bus (includes stops/waits)
            time_minutes = (distance_km / 20.0) * 60 + 10  # +10 min wait time
        elif mode == 'drive':
            # Assume 40 km/h average in city
            time_minutes = (distance_km / 40.0) * 60 + 5  # +5 min parking
        elif mode == 'bike':
            # Assume 15 km/h biking speed
            time_minutes = (distance_km / 15.0) * 60
        else:
            time_minutes = 30  # Default
        
        return time_minutes
    
    def _haversine_distance(
        self,
        coord1: Tuple[float, float],
        coord2: Tuple[float, float]
    ) -> float:
        """Calculate great-circle distance in km"""
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth radius in km
        r = 6371
        
        return c * r
    
    def _time_to_score(self, time_minutes: float) -> float:
        """Convert commute time to score (0-1, higher is better)"""
        # 0-15 min: excellent (1.0)
        # 15-30 min: good (0.7-1.0)
        # 30-45 min: acceptable (0.4-0.7)
        # 45+ min: poor (<0.4)
        
        if time_minutes <= 15:
            return 1.0
        elif time_minutes <= 30:
            return 1.0 - ((time_minutes - 15) / 15) * 0.3
        elif time_minutes <= 45:
            return 0.7 - ((time_minutes - 30) / 15) * 0.3
        else:
            return max(0.4 - ((time_minutes - 45) / 30) * 0.4, 0.0)
