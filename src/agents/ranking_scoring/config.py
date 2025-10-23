"""
Ranking & Scoring Agent Configuration
Agent-specific settings (imports from main config)
"""

from config.agents_config import RANKING_SCORING_CONFIG

# Re-export for agent use
DEFAULT_CRITERIA_WEIGHTS = RANKING_SCORING_CONFIG['default_criteria_weights']
MIN_WEIGHT_PER_CRITERION = RANKING_SCORING_CONFIG['min_weight_per_criterion']
MAX_WEIGHT_PER_CRITERION = RANKING_SCORING_CONFIG['max_weight_per_criterion']
COMMUTE_CONFIG = RANKING_SCORING_CONFIG['commute_config']
PARETO_OPTIMAL_DETECTION = RANKING_SCORING_CONFIG['pareto_optimal_detection']
MAX_RESULTS = RANKING_SCORING_CONFIG['max_results']
ENABLE_EXPLANATIONS = RANKING_SCORING_CONFIG['enable_explanations']

# Validation
assert sum(DEFAULT_CRITERIA_WEIGHTS.values()) == 1.0, \
    "Default weights must sum to 1.0"
