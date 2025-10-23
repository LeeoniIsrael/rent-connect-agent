"""
Roommate Matching Agent Configuration
Agent-specific settings (imports from main config)
"""

from config.agents_config import ROOMMATE_MATCHING_CONFIG

# Re-export for agent use
ALGORITHM = ROOMMATE_MATCHING_CONFIG['algorithm']
MAX_CANDIDATES = ROOMMATE_MATCHING_CONFIG['max_candidates_per_person']
HARD_CONSTRAINT_WEIGHT = ROOMMATE_MATCHING_CONFIG['hard_constraint_weight']
SOFT_PREFERENCE_WEIGHTS = ROOMMATE_MATCHING_CONFIG['soft_preference_weights']
PERSONALITY_WEIGHTS = ROOMMATE_MATCHING_CONFIG['personality_weights']
FAIRNESS_CONSTRAINTS = ROOMMATE_MATCHING_CONFIG['fairness_constraints']
GROUP_MATCHING = ROOMMATE_MATCHING_CONFIG['group_matching']

# Validation
assert sum(SOFT_PREFERENCE_WEIGHTS.values()) + sum(PERSONALITY_WEIGHTS.values()) <= 1.0, \
    "Total weight must not exceed 1.0"
