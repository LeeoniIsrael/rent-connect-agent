"""
Ranking & Scoring Agent
Multi-objective property ranking with Pareto optimality detection.

Input Streams:
- Listing data (from DataIngestion preprocessing)
- Analysis results (from listing_analyzer, compliance_checker tools)
- User preferences (criteria weights, hard constraints)
- Configuration (from config.agents_config)

Output Streams:
- Ranked listings with overall scores
- Pareto-optimal flags
- Score breakdowns and explanations
"""

import logging
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
import math

from .config import (
    DEFAULT_CRITERIA_WEIGHTS,
    MIN_WEIGHT_PER_CRITERION,
    MAX_WEIGHT_PER_CRITERION,
    COMMUTE_CONFIG,
    PARETO_OPTIMAL_DETECTION,
    MAX_RESULTS,
    ENABLE_EXPLANATIONS
)

logger = logging.getLogger(__name__)


@dataclass
class RankingResult:
    """Output from ranking process"""
    ranked_listings: List[Dict[str, Any]]
    pareto_frontier: List[str]
    explanations: Dict[str, str]
    stats: Dict[str, Any]


class RankingScoringAgent:
    """
    Autonomous agent for multi-objective property ranking.
    Identifies Pareto-optimal listings and provides explainable scores.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.default_weights = DEFAULT_CRITERIA_WEIGHTS
        self.min_weight = MIN_WEIGHT_PER_CRITERION
        self.max_weight = MAX_WEIGHT_PER_CRITERION
        self.commute_config = COMMUTE_CONFIG
        self.enable_pareto = PARETO_OPTIMAL_DETECTION
        self.max_results = MAX_RESULTS
        self.enable_explanations = ENABLE_EXPLANATIONS
        
    def rank(
        self,
        listings: List[Dict[str, Any]],
        user_preferences: Optional[Dict[str, Any]] = None,
        destination: Optional[Tuple[float, float]] = None
    ) -> RankingResult:
        """
        Main ranking method - autonomous decision point.
        
        Args:
            listings: Property listings (from DataIngestion)
            user_preferences: User criteria weights and constraints
            destination: (lat, lon) for commute calculation
            
        Returns:
            RankingResult with ranked listings and explanations
        """
        self.logger.info(f"Starting ranking for {len(listings)} listings")
        
        # Parse user preferences or use defaults
        weights = self._parse_weights(user_preferences)
        hard_constraints = self._parse_hard_constraints(user_preferences)
        
        # Apply hard constraints (filter out non-viable)
        viable_listings = self._apply_hard_constraints(listings, hard_constraints)
        self.logger.info(f"{len(viable_listings)} listings passed hard constraints")
        
        # Compute criterion scores for each listing
        scored_listings = self._compute_all_scores(viable_listings, destination)
        
        # Compute weighted overall scores
        ranked_listings = self._compute_overall_scores(scored_listings, weights)
        
        # Identify Pareto-optimal listings
        pareto_frontier = []
        if self.enable_pareto:
            pareto_frontier = self._identify_pareto_frontier(ranked_listings)
        
        # Generate explanations
        explanations = {}
        if self.enable_explanations:
            explanations = self._generate_explanations(ranked_listings, weights)
        
        # Sort by overall score (descending)
        ranked_listings.sort(key=lambda x: x['overall_score'], reverse=True)
        
        # Assign ranks
        for i, listing in enumerate(ranked_listings[:self.max_results]):
            listing['rank'] = i + 1
            listing['is_pareto_optimal'] = listing['listing_id'] in pareto_frontier
        
        # Compute statistics
        stats = self._compute_stats(ranked_listings)
        
        self.logger.info(f"Ranking complete: {len(ranked_listings)} results, {len(pareto_frontier)} Pareto-optimal")
        
        return RankingResult(
            ranked_listings=ranked_listings[:self.max_results],
            pareto_frontier=pareto_frontier,
            explanations=explanations,
            stats=stats
        )
    
    def _parse_weights(self, user_preferences: Optional[Dict[str, Any]]) -> Dict[str, float]:
        """Parse and validate user-provided weights or use defaults"""
        if not user_preferences or 'weights' not in user_preferences:
            return self.default_weights.copy()
        
        weights = user_preferences['weights']
        
        # Validate weights sum to 1.0
        total = sum(weights.values())
        if not (0.99 <= total <= 1.01):
            self.logger.warning(f"Weights sum to {total}, normalizing")
            weights = {k: v / total for k, v in weights.items()}
        
        # Validate weight ranges
        for criterion, weight in weights.items():
            if not (self.min_weight <= weight <= self.max_weight):
                self.logger.warning(f"Weight for {criterion} out of range: {weight}")
        
        return weights
    
    def _parse_hard_constraints(self, user_preferences: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Parse hard constraints (must satisfy)"""
        if not user_preferences or 'hard_constraints' not in user_preferences:
            return {}
        
        return user_preferences['hard_constraints']
    
    def _apply_hard_constraints(self, listings: List[Dict[str, Any]], constraints: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter listings that don't meet hard constraints"""
        if not constraints:
            return listings
        
        viable = []
        for listing in listings:
            if self._meets_hard_constraints(listing, constraints):
                viable.append(listing)
        
        return viable
    
    def _meets_hard_constraints(self, listing: Dict[str, Any], constraints: Dict[str, Any]) -> bool:
        """Check if listing meets all hard constraints"""
        # Max price
        if 'max_price' in constraints:
            price = listing.get('price', float('inf'))
            if price > constraints['max_price']:
                return False
        
        # Min bedrooms
        if 'min_bedrooms' in constraints:
            bedrooms = listing.get('bedrooms', 0)
            if bedrooms < constraints['min_bedrooms']:
                return False
        
        # Max commute (requires destination)
        if 'max_commute' in constraints and 'commute_time' in listing:
            if listing['commute_time'] > constraints['max_commute']:
                return False
        
        # Min safety score
        if 'min_safety' in constraints:
            safety = listing.get('safety_score', 0)
            if safety < constraints['min_safety']:
                return False
        
        return True
    
    def _compute_all_scores(self, listings: List[Dict[str, Any]], destination: Optional[Tuple[float, float]]) -> List[Dict[str, Any]]:
        """Compute criterion scores for all listings"""
        # Collect all values for normalization
        prices = [l.get('price', 0) for l in listings]
        commutes = []
        safety_scores = [l.get('safety_score', 0.5) for l in listings]
        
        # Compute commute times if destination provided
        if destination:
            for listing in listings:
                lat = listing.get('latitude')
                lon = listing.get('longitude')
                if lat and lon:
                    commute_time = self._compute_commute_time((lat, lon), destination)
                    listing['commute_time'] = commute_time
                    commutes.append(commute_time)
                else:
                    listing['commute_time'] = 999  # Unknown = worst
                    commutes.append(999)
        else:
            commutes = [l.get('commute_time', 60) for l in listings]
        
        # Normalize scores (0-1 scale)
        min_price, max_price = min(prices), max(prices)
        min_commute, max_commute = min(commutes), max(commutes)
        
        for listing in listings:
            # Price score (lower is better, so invert)
            price = listing.get('price', max_price)
            price_score = 1.0 - ((price - min_price) / (max_price - min_price + 1)) if max_price > min_price else 0.5
            
            # Commute score (lower is better, so invert)
            commute = listing.get('commute_time', max_commute)
            commute_score = 1.0 - ((commute - min_commute) / (max_commute - min_commute + 1)) if max_commute > min_commute else 0.5
            
            # Safety score (already 0-1)
            safety_score = listing.get('safety_score', 0.5)
            
            # Amenities match score (computed from listing features)
            amenities_score = self._compute_amenities_score(listing)
            
            # Lease suitability score
            lease_score = self._compute_lease_score(listing)
            
            listing['criteria_scores'] = {
                'price': price_score,
                'commute_time': commute_score,
                'safety_score': safety_score,
                'amenities_match': amenities_score,
                'lease_suitability': lease_score
            }
        
        return listings
    
    def _compute_commute_time(self, origin: Tuple[float, float], destination: Tuple[float, float]) -> float:
        """
        Compute commute time between origin and destination.
        Uses Haversine distance + mode speeds (simplified).
        Production: Use Google Distance Matrix API.
        """
        lat1, lon1 = origin
        lat2, lon2 = destination
        
        # Haversine distance (km)
        R = 6371  # Earth radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        
        # Compute time for each mode
        modes = self.commute_config['transport_modes']
        speeds = self.commute_config['mode_speeds']
        times = {}
        
        for mode in modes:
            base_time = (distance / speeds[mode]) * 60  # minutes
            
            # Add wait/parking time
            if mode == 'transit':
                base_time += self.commute_config['transit_wait_time_avg']
            elif mode == 'drive':
                base_time += self.commute_config['drive_parking_time_avg']
            
            times[mode] = base_time
        
        # Return best mode time
        return min(times.values())
    
    def _compute_amenities_score(self, listing: Dict[str, Any]) -> float:
        """
        Compute amenities match score (0-1).
        Simplified: check presence of common amenities.
        """
        amenities = listing.get('amenities', [])
        if not amenities:
            return 0.5  # Neutral if no data
        
        # Common desired amenities
        desired = ['parking', 'laundry', 'wifi', 'gym', 'pool', 'dishwasher']
        matches = sum(1 for a in desired if a in amenities)
        
        return matches / len(desired)
    
    def _compute_lease_score(self, listing: Dict[str, Any]) -> float:
        """
        Compute lease suitability score (0-1).
        Simplified: check if lease terms are reasonable.
        """
        # Lease length (prefer 12 months)
        lease_months = listing.get('lease_length_months', 12)
        length_score = 1.0 if lease_months == 12 else 0.7 if 9 <= lease_months <= 15 else 0.5
        
        # Security deposit (prefer <= 1 month rent)
        deposit = listing.get('security_deposit', 0)
        rent = listing.get('price', 1)
        deposit_score = 1.0 if deposit <= rent else 0.5
        
        # Average
        return (length_score + deposit_score) / 2
    
    def _compute_overall_scores(self, listings: List[Dict[str, Any]], weights: Dict[str, float]) -> List[Dict[str, Any]]:
        """Compute weighted overall scores"""
        for listing in listings:
            scores = listing['criteria_scores']
            overall = sum(scores[criterion] * weights[criterion] for criterion in weights)
            listing['overall_score'] = overall
        
        return listings
    
    def _identify_pareto_frontier(self, listings: List[Dict[str, Any]]) -> List[str]:
        """
        Identify Pareto-optimal listings (non-dominated).
        A listing is Pareto-optimal if no other listing is better in ALL criteria.
        """
        pareto = []
        
        for i, listing_a in enumerate(listings):
            scores_a = listing_a['criteria_scores']
            dominated = False
            
            for j, listing_b in enumerate(listings):
                if i == j:
                    continue
                
                scores_b = listing_b['criteria_scores']
                
                # Check if B dominates A (B >= A in all criteria, B > A in at least one)
                all_geq = all(scores_b[c] >= scores_a[c] for c in scores_a)
                any_greater = any(scores_b[c] > scores_a[c] for c in scores_a)
                
                if all_geq and any_greater:
                    dominated = True
                    break
            
            if not dominated:
                pareto.append(listing_a['listing_id'])
        
        return pareto
    
    def _generate_explanations(self, listings: List[Dict[str, Any]], weights: Dict[str, float]) -> Dict[str, str]:
        """Generate natural language explanations for rankings"""
        explanations = {}
        
        for listing in listings:
            lid = listing['listing_id']
            scores = listing['criteria_scores']
            overall = listing['overall_score']
            
            # Find best and worst criteria
            best_criterion = max(scores, key=scores.get)
            worst_criterion = min(scores, key=scores.get)
            
            explanation = (
                f"Overall score: {overall:.2f}. "
                f"Strongest: {best_criterion} ({scores[best_criterion]:.2f}). "
                f"Weakest: {worst_criterion} ({scores[worst_criterion]:.2f}). "
                f"Breakdown: "
            )
            
            breakdown = ", ".join(
                f"{criterion}={scores[criterion]:.2f} (weight {weights[criterion]:.2f})"
                for criterion in scores
            )
            explanation += breakdown
            
            explanations[lid] = explanation
        
        return explanations
    
    def _compute_stats(self, listings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compute statistics about rankings"""
        if not listings:
            return {}
        
        scores = [l['overall_score'] for l in listings]
        
        return {
            'total_listings': len(listings),
            'mean_score': sum(scores) / len(scores),
            'min_score': min(scores),
            'max_score': max(scores),
            'std_score': (sum((s - sum(scores)/len(scores))**2 for s in scores) / len(scores))**0.5
        }


# Singleton instance (lowercase variable name)
ranking_scoring = RankingScoringAgent()
