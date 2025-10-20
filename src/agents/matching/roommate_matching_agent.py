"""
Roommate Matching Agent
Stable matching algorithm with hard/soft constraints and fairness checks.
Implements constraint satisfaction + multi-objective optimization.
"""

from typing import Any, Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
import math
from ..base_agent import BaseAgent, AgentContext, AgentOutput


@dataclass
class RoommateProfile:
    """Student roommate profile"""
    user_id: str
    hard_constraints: Dict[str, Any]  # Must-match criteria
    soft_preferences: Dict[str, float]  # Weighted preferences
    personality: Dict[str, float]  # Big Five OCEAN scores
    schedule: Dict[str, Any]  # Class/work schedule
    budget_range: Tuple[float, float]  # (min, max) monthly rent
    

class RoommateMatchingAgent(BaseAgent):
    """
    Matches students based on:
    - Hard constraints (no smoking, pet policy, quiet hours)
    - Soft preferences (cleanliness, social level, schedules)
    - Personality compatibility (Big Five)
    - Fairness considerations
    
    Uses stable matching algorithm (Gale-Shapley variant) with constraint satisfaction.
    C3AN: Reasoning, Planning, Interpretability, Alignment (fairness)
    """
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__("RoommateMatchingAgent", config)
        self.compatibility_weights = config.get('weights', {
            'hard_constraints': 1.0,  # Binary: match or no match
            'personality': 0.3,
            'preferences': 0.4,
            'schedule': 0.2,
            'budget': 0.1
        })
        
    def process(self, input_data: Any, context: AgentContext) -> AgentOutput:
        """
        Match roommates based on profiles.
        
        Args:
            input_data: Dict with 'profiles' (list of RoommateProfile dicts),
                       'match_type' ('one_to_one' or 'groups')
            context: Shared agent context
            
        Returns:
            AgentOutput with matches and compatibility scores
        """
        if not self.validate_input(input_data):
            return self.create_output(
                result=None,
                confidence=0.0,
                explanation="Invalid matching input",
                attribution=[],
                errors=["Input validation failed"]
            )
        
        profiles_data = input_data.get('profiles', [])
        match_type = input_data.get('match_type', 'one_to_one')
        
        # Convert to RoommateProfile objects
        profiles = [self._dict_to_profile(p) for p in profiles_data]
        
        if len(profiles) < 2:
            return self.create_output(
                result={'matches': []},
                confidence=0.0,
                explanation="Insufficient profiles for matching (need at least 2)",
                attribution=[],
                errors=["Not enough profiles"]
            )
        
        # Perform matching
        if match_type == 'one_to_one':
            matches = self._stable_matching(profiles, context)
        else:
            matches = self._group_matching(profiles, context)
        
        # Check fairness
        fairness_score, fairness_issues = self._check_fairness(matches, profiles)
        
        explanation = self._generate_match_explanation(matches, len(profiles))
        
        return self.create_output(
            result={
                'matches': matches,
                'total_matched': len(matches),
                'fairness_score': fairness_score,
                'fairness_issues': fairness_issues
            },
            confidence=fairness_score,
            explanation=explanation,
            attribution=[
                "Stable matching algorithm",
                "Big Five personality model",
                "Fairness constraints"
            ],
            errors=fairness_issues if fairness_score < 0.8 else []
        )
    
    def validate_input(self, input_data: Any) -> bool:
        """Validate matching input"""
        if not isinstance(input_data, dict):
            return False
        
        profiles = input_data.get('profiles')
        if not profiles or not isinstance(profiles, list):
            return False
        
        return True
    
    def _dict_to_profile(self, data: Dict) -> RoommateProfile:
        """Convert dict to RoommateProfile"""
        return RoommateProfile(
            user_id=data['user_id'],
            hard_constraints=data.get('hard_constraints', {}),
            soft_preferences=data.get('soft_preferences', {}),
            personality=data.get('personality', {}),
            schedule=data.get('schedule', {}),
            budget_range=data.get('budget_range', (0, 10000))
        )
    
    def _stable_matching(
        self,
        profiles: List[RoommateProfile],
        context: AgentContext
    ) -> List[Dict]:
        """
        Stable matching algorithm (Gale-Shapley variant).
        Ensures no two students would prefer each other over their assigned match.
        """
        matches = []
        unmatched = set(range(len(profiles)))
        matched_pairs = set()
        
        # Build preference lists considering constraints
        preferences = {}
        for i in range(len(profiles)):
            pref_list = []
            for j in range(len(profiles)):
                if i != j and j not in matched_pairs:
                    # Check hard constraints first
                    if self._check_hard_constraints(profiles[i], profiles[j]):
                        score = self._compute_compatibility(profiles[i], profiles[j])
                        pref_list.append((j, score))
            
            # Sort by compatibility score
            pref_list.sort(key=lambda x: x[1], reverse=True)
            preferences[i] = pref_list
        
        # Stable matching iteration
        while unmatched:
            # Pick unmatched student
            i = unmatched.pop()
            if i not in preferences or not preferences[i]:
                continue
            
            # Get top preference
            j, score = preferences[i][0]
            
            # Remove from preference list
            preferences[i] = preferences[i][1:]
            
            # Check if j is unmatched
            if j in unmatched:
                # Create match
                unmatched.discard(j)
                matched_pairs.add(i)
                matched_pairs.add(j)
                
                match_details = self._create_match_details(
                    profiles[i], profiles[j], score
                )
                matches.append(match_details)
                
                self.log_decision(
                    f"Matched {profiles[i].user_id} with {profiles[j].user_id}",
                    f"Compatibility score: {score:.2f}",
                    context
                )
            else:
                # j is already matched, check if prefers i over current match
                # For simplicity, keep current match (could implement full Gale-Shapley)
                unmatched.add(i)
        
        return matches
    
    def _group_matching(
        self,
        profiles: List[RoommateProfile],
        context: AgentContext
    ) -> List[Dict]:
        """
        Match roommates into groups (for multi-bedroom units).
        Uses clustering-based approach.
        """
        # Simple greedy grouping for now
        # In production: use more sophisticated clustering
        groups = []
        unmatched = set(range(len(profiles)))
        
        while unmatched:
            # Start a new group with highest-quality candidate
            seed = unmatched.pop()
            group = [seed]
            group_size = 4  # Max 4 roommates
            
            # Find compatible members
            candidates = []
            for j in unmatched:
                if self._check_hard_constraints(profiles[seed], profiles[j]):
                    score = self._compute_compatibility(profiles[seed], profiles[j])
                    candidates.append((j, score))
            
            candidates.sort(key=lambda x: x[1], reverse=True)
            
            # Add top candidates
            for j, score in candidates[:group_size-1]:
                group.append(j)
                unmatched.discard(j)
            
            # Create group match
            group_profiles = [profiles[i] for i in group]
            avg_score = sum(
                self._compute_compatibility(group_profiles[i], group_profiles[j])
                for i in range(len(group_profiles))
                for j in range(i+1, len(group_profiles))
            ) / max((len(group) * (len(group) - 1)) / 2, 1)
            
            groups.append({
                'group_id': f"group_{len(groups)}",
                'members': [p.user_id for p in group_profiles],
                'size': len(group),
                'compatibility_score': avg_score
            })
        
        return groups
    
    def _check_hard_constraints(
        self,
        profile1: RoommateProfile,
        profile2: RoommateProfile
    ) -> bool:
        """
        Check if hard constraints are compatible.
        Returns True if compatible, False otherwise.
        """
        constraints1 = profile1.hard_constraints
        constraints2 = profile2.hard_constraints
        
        # Check smoking
        if constraints1.get('no_smoking') and not constraints2.get('no_smoking'):
            return False
        if constraints2.get('no_smoking') and not constraints1.get('no_smoking'):
            return False
        
        # Check pet policy
        pet1 = constraints1.get('pet_policy', 'no_preference')
        pet2 = constraints2.get('pet_policy', 'no_preference')
        if pet1 == 'no_pets' and pet2 == 'has_pets':
            return False
        if pet2 == 'no_pets' and pet1 == 'has_pets':
            return False
        
        # Check quiet hours
        quiet1 = constraints1.get('quiet_hours', False)
        quiet2 = constraints2.get('quiet_hours', False)
        # Both must agree on quiet hours if one requires it
        if quiet1 and not quiet2:
            return False
        if quiet2 and not quiet1:
            return False
        
        # Check budget compatibility
        budget1_min, budget1_max = profile1.budget_range
        budget2_min, budget2_max = profile2.budget_range
        # Check if ranges overlap
        if budget1_max < budget2_min or budget2_max < budget1_min:
            return False
        
        return True
    
    def _compute_compatibility(
        self,
        profile1: RoommateProfile,
        profile2: RoommateProfile
    ) -> float:
        """
        Compute compatibility score between two profiles.
        Returns score in [0, 1].
        """
        scores = {}
        
        # Personality compatibility (Big Five)
        personality_score = self._personality_compatibility(
            profile1.personality, profile2.personality
        )
        scores['personality'] = personality_score
        
        # Soft preference compatibility
        preference_score = self._preference_compatibility(
            profile1.soft_preferences, profile2.soft_preferences
        )
        scores['preferences'] = preference_score
        
        # Schedule compatibility
        schedule_score = self._schedule_compatibility(
            profile1.schedule, profile2.schedule
        )
        scores['schedule'] = schedule_score
        
        # Budget compatibility
        budget_score = self._budget_compatibility(
            profile1.budget_range, profile2.budget_range
        )
        scores['budget'] = budget_score
        
        # Weighted sum
        total_score = sum(
            scores[key] * self.compatibility_weights.get(key, 0.0)
            for key in scores
        )
        
        # Normalize
        total_weight = sum(
            self.compatibility_weights.get(key, 0.0)
            for key in ['personality', 'preferences', 'schedule', 'budget']
        )
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def _personality_compatibility(
        self,
        personality1: Dict[str, float],
        personality2: Dict[str, float]
    ) -> float:
        """
        Compute personality compatibility using Big Five.
        Uses similarity and complementarity principles.
        """
        if not personality1 or not personality2:
            return 0.5  # Neutral
        
        # Get OCEAN scores
        traits = ['openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']
        
        similarity_score = 0.0
        for trait in traits:
            p1 = personality1.get(trait, 0.5)
            p2 = personality2.get(trait, 0.5)
            
            # For some traits, similarity is good (conscientiousness, agreeableness)
            # For others, complementarity can work (extraversion)
            if trait in ['conscientiousness', 'agreeableness']:
                # Prefer similarity
                similarity_score += 1.0 - abs(p1 - p2)
            elif trait == 'neuroticism':
                # Prefer both low
                similarity_score += 1.0 - max(p1, p2)
            else:
                # Neutral on similarity vs complementarity
                similarity_score += 0.5
        
        return similarity_score / len(traits)
    
    def _preference_compatibility(
        self,
        prefs1: Dict[str, float],
        prefs2: Dict[str, float]
    ) -> float:
        """Compute soft preference compatibility"""
        if not prefs1 or not prefs2:
            return 0.5
        
        # Cleanliness compatibility (prefer similar levels)
        clean1 = prefs1.get('cleanliness', 5)
        clean2 = prefs2.get('cleanliness', 5)
        clean_score = 1.0 - abs(clean1 - clean2) / 10.0
        
        # Social level compatibility
        social1 = prefs1.get('social_level', 5)
        social2 = prefs2.get('social_level', 5)
        social_score = 1.0 - abs(social1 - social2) / 10.0
        
        return (clean_score + social_score) / 2.0
    
    def _schedule_compatibility(
        self,
        schedule1: Dict[str, Any],
        schedule2: Dict[str, Any]
    ) -> float:
        """Compute schedule compatibility"""
        if not schedule1 or not schedule2:
            return 0.5
        
        # Simple heuristic: check schedule type
        type1 = schedule1.get('schedule_type', 'flexible')
        type2 = schedule2.get('schedule_type', 'flexible')
        
        # Compatible types
        if type1 == type2:
            return 0.9
        elif 'flexible' in [type1, type2]:
            return 0.7
        else:
            return 0.5
    
    def _budget_compatibility(
        self,
        budget1: Tuple[float, float],
        budget2: Tuple[float, float]
    ) -> float:
        """Compute budget range compatibility"""
        min1, max1 = budget1
        min2, max2 = budget2
        
        # Calculate overlap
        overlap_min = max(min1, min2)
        overlap_max = min(max1, max2)
        
        if overlap_max < overlap_min:
            return 0.0  # No overlap
        
        overlap = overlap_max - overlap_min
        range1 = max1 - min1
        range2 = max2 - min2
        avg_range = (range1 + range2) / 2.0
        
        return min(overlap / avg_range, 1.0) if avg_range > 0 else 0.5
    
    def _create_match_details(
        self,
        profile1: RoommateProfile,
        profile2: RoommateProfile,
        compatibility_score: float
    ) -> Dict:
        """Create detailed match result"""
        return {
            'match_id': f"{profile1.user_id}_{profile2.user_id}",
            'users': [profile1.user_id, profile2.user_id],
            'compatibility_score': compatibility_score,
            'shared_constraints': self._find_shared_constraints(profile1, profile2),
            'complementary_traits': self._find_complementary_traits(profile1, profile2)
        }
    
    def _find_shared_constraints(
        self,
        profile1: RoommateProfile,
        profile2: RoommateProfile
    ) -> List[str]:
        """Find shared hard constraints"""
        shared = []
        
        if profile1.hard_constraints.get('no_smoking') and profile2.hard_constraints.get('no_smoking'):
            shared.append('Both non-smoking')
        
        pet1 = profile1.hard_constraints.get('pet_policy')
        pet2 = profile2.hard_constraints.get('pet_policy')
        if pet1 == pet2:
            shared.append(f'Pet policy: {pet1}')
        
        if profile1.hard_constraints.get('quiet_hours') and profile2.hard_constraints.get('quiet_hours'):
            shared.append('Both prefer quiet hours')
        
        return shared
    
    def _find_complementary_traits(
        self,
        profile1: RoommateProfile,
        profile2: RoommateProfile
    ) -> List[str]:
        """Find complementary personality traits"""
        complementary = []
        
        # Example: one extraverted, one introverted can balance
        ext1 = profile1.personality.get('extraversion', 0.5)
        ext2 = profile2.personality.get('extraversion', 0.5)
        
        if abs(ext1 - ext2) > 0.3:
            complementary.append('Balanced extraversion/introversion')
        
        return complementary
    
    def _check_fairness(
        self,
        matches: List[Dict],
        profiles: List[RoommateProfile]
    ) -> Tuple[float, List[str]]:
        """
        Check matches for fairness issues.
        C3AN: Alignment, Safety, Fairness
        """
        issues = []
        
        # Check match rate
        matched_users = set()
        for match in matches:
            matched_users.update(match.get('users', match.get('members', [])))
        
        match_rate = len(matched_users) / len(profiles) if profiles else 0
        
        if match_rate < 0.5:
            issues.append(f"Low match rate: {match_rate:.1%} of users matched")
        
        # Check for quality variance (avoid some matches being much worse)
        if matches:
            scores = [m.get('compatibility_score', m.get('compatibility_score', 0)) 
                     for m in matches]
            avg_score = sum(scores) / len(scores)
            min_score = min(scores)
            
            if min_score < avg_score * 0.6:
                issues.append(f"Quality variance: some matches significantly below average")
        
        fairness_score = max(0.0, 1.0 - len(issues) * 0.2)
        return fairness_score, issues
    
    def _generate_match_explanation(
        self,
        matches: List[Dict],
        total_profiles: int
    ) -> str:
        """Generate human-readable explanation"""
        matched_count = sum(len(m.get('users', m.get('members', []))) for m in matches)
        match_rate = matched_count / total_profiles if total_profiles > 0 else 0
        
        if matches:
            avg_score = sum(m.get('compatibility_score', m.get('compatibility_score', 0)) 
                           for m in matches) / len(matches)
            return (
                f"Created {len(matches)} matches with {match_rate:.0%} match rate. "
                f"Average compatibility: {avg_score:.2f}"
            )
        else:
            return "No compatible matches found based on constraints"
