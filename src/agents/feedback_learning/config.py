"""
Feedback & Learning Agent Configuration
Agent-specific settings (imports from main config)
"""

from config.agents_config import FEEDBACK_LEARNING_CONFIG

# Re-export for agent use
FEEDBACK_TYPES = FEEDBACK_LEARNING_CONFIG['feedback_types']
RATING_CONFIG = FEEDBACK_LEARNING_CONFIG['rating_config']
CORRECTION_CONFIG = FEEDBACK_LEARNING_CONFIG['correction_config']
PREFERENCE_UPDATE_CONFIG = FEEDBACK_LEARNING_CONFIG['preference_update_config']
DRIFT_DETECTION = FEEDBACK_LEARNING_CONFIG['drift_detection']
EVALUATION_METRICS = FEEDBACK_LEARNING_CONFIG['evaluation_metrics']
