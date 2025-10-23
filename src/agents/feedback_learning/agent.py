"""
Feedback & Learning Agent
Processes user and expert feedback to improve system over time.

Input Streams:
- User ratings (explicit feedback)
- Corrections (expert feedback)
- Implicit feedback (clicks, bookings)
- Configuration (from config.agents_config)

Output Streams:
- Updated preferences
- Model corrections
- Drift alerts
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from collections import deque
import statistics

from .config import (
    FEEDBACK_TYPES,
    RATING_CONFIG,
    CORRECTION_CONFIG,
    PREFERENCE_UPDATE_CONFIG,
    DRIFT_DETECTION,
    EVALUATION_METRICS
)

logger = logging.getLogger(__name__)


@dataclass
class FeedbackResult:
    """Output from feedback processing"""
    feedback_id: str
    applied: bool
    impact_summary: str
    updated_components: List[str]
    drift_detected: bool


class FeedbackLearningAgent:
    """
    Autonomous agent for learning from user and expert feedback.
    Adapts system behavior to user preferences over time.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.feedback_types = FEEDBACK_TYPES
        self.rating_config = RATING_CONFIG
        self.correction_config = CORRECTION_CONFIG
        self.preference_config = PREFERENCE_UPDATE_CONFIG
        self.drift_config = DRIFT_DETECTION
        self.evaluation_config = EVALUATION_METRICS
        
        # In-memory storage (production: use database)
        self.user_preferences = {}  # user_id -> preferences dict
        self.feedback_history = {}  # user_id -> deque of recent feedback
        self.correction_log = []    # List of applied corrections
        
    def process_feedback(self, feedback: Dict[str, Any]) -> FeedbackResult:
        """
        Main processing method - autonomous decision point.
        
        Args:
            feedback: Feedback data with type, user_id, content
            
        Returns:
            FeedbackResult with application status and impact
        """
        feedback_id = feedback.get('feedback_id', f"fb_{id(feedback)}")
        feedback_type = feedback.get('type')
        
        self.logger.info(f"Processing feedback {feedback_id} of type {feedback_type}")
        
        # Route to appropriate handler
        if feedback_type == 'rating':
            return self._process_rating(feedback_id, feedback)
        elif feedback_type == 'correction':
            return self._process_correction(feedback_id, feedback)
        elif feedback_type == 'preference_update':
            return self._process_preference_update(feedback_id, feedback)
        else:
            self.logger.warning(f"Unknown feedback type: {feedback_type}")
            return FeedbackResult(
                feedback_id=feedback_id,
                applied=False,
                impact_summary="Unknown feedback type",
                updated_components=[],
                drift_detected=False
            )
    
    def _process_rating(self, feedback_id: str, feedback: Dict[str, Any]) -> FeedbackResult:
        """
        Process rating feedback (1-5 stars).
        Updates user preference weights based on what they liked/disliked.
        """
        user_id = feedback['user_id']
        rating = feedback['rating']
        context = feedback.get('context', {})
        
        # Initialize user history if needed
        if user_id not in self.feedback_history:
            self.feedback_history[user_id] = deque(maxlen=self.drift_config['window_size'])
        
        # Add to history
        self.feedback_history[user_id].append({
            'rating': rating,
            'context': context
        })
        
        # Check if enough ratings to update
        if len(self.feedback_history[user_id]) < self.rating_config['min_ratings_before_update']:
            self.logger.info(f"Not enough ratings yet for {user_id}, need {self.rating_config['min_ratings_before_update']}")
            return FeedbackResult(
                feedback_id=feedback_id,
                applied=False,
                impact_summary="Insufficient ratings to update preferences",
                updated_components=[],
                drift_detected=False
            )
        
        # Detect drift
        drift_detected = False
        if self.drift_config['enable']:
            drift_detected = self._detect_drift(user_id)
        
        # Update preferences based on ratings
        updated_prefs = self._update_preferences_from_ratings(user_id, context, rating)
        
        return FeedbackResult(
            feedback_id=feedback_id,
            applied=True,
            impact_summary=f"Updated preferences for {user_id} based on {rating}-star rating",
            updated_components=['user_preferences'],
            drift_detected=drift_detected
        )
    
    def _process_correction(self, feedback_id: str, feedback: Dict[str, Any]) -> FeedbackResult:
        """
        Process correction feedback from experts.
        Updates models (scam detection, price estimates, etc.)
        """
        target = feedback['target']
        expert_confidence = feedback.get('expert_confidence', 0.0)
        
        # Check if expert verification required
        if self.correction_config['require_expert_verification']:
            if expert_confidence < self.correction_config['min_confidence_for_auto_apply']:
                self.logger.warning(f"Correction confidence too low: {expert_confidence}")
                return FeedbackResult(
                    feedback_id=feedback_id,
                    applied=False,
                    impact_summary="Requires higher expert confidence",
                    updated_components=[],
                    drift_detected=False
                )
        
        # Apply correction to target model
        applied = self._apply_correction(target, feedback)
        
        if applied:
            self.correction_log.append({
                'feedback_id': feedback_id,
                'target': target,
                'feedback': feedback
            })
        
        return FeedbackResult(
            feedback_id=feedback_id,
            applied=applied,
            impact_summary=f"Correction applied to {target}" if applied else "Correction rejected",
            updated_components=[target] if applied else [],
            drift_detected=False
        )
    
    def _process_preference_update(self, feedback_id: str, feedback: Dict[str, Any]) -> FeedbackResult:
        """
        Process explicit preference updates (user changes weights).
        Directly updates user preferences.
        """
        user_id = feedback['user_id']
        new_weights = feedback['new_weights']
        
        # Validate weights
        if not self._validate_weights(new_weights):
            self.logger.warning(f"Invalid weights for {user_id}: {new_weights}")
            return FeedbackResult(
                feedback_id=feedback_id,
                applied=False,
                impact_summary="Invalid weights (must sum to 1.0)",
                updated_components=[],
                drift_detected=False
            )
        
        # Update preferences
        old_weights = self.user_preferences.get(user_id, {}).get('weights', {})
        
        if self.preference_config['update_strategy'] == 'weighted_average':
            # Blend old and new weights
            decay = self.preference_config['decay_factor']
            blended_weights = {
                k: decay * old_weights.get(k, 0) + (1 - decay) * new_weights.get(k, 0)
                for k in new_weights
            }
            self.user_preferences[user_id] = {'weights': blended_weights}
        else:
            # Replace
            self.user_preferences[user_id] = {'weights': new_weights}
        
        return FeedbackResult(
            feedback_id=feedback_id,
            applied=True,
            impact_summary=f"Preferences updated for {user_id}",
            updated_components=['user_preferences'],
            drift_detected=False
        )
    
    def _update_preferences_from_ratings(
        self,
        user_id: str,
        context: Dict[str, Any],
        rating: int
    ) -> Dict[str, Any]:
        """
        Infer preference changes from ratings.
        If high rating, increase weight on criteria that were good.
        """
        # Simplified: adjust weights based on what was strong/weak in rated item
        criteria_scores = context.get('criteria_scores', {})
        
        if not criteria_scores:
            return self.user_preferences.get(user_id, {})
        
        # Get current weights or defaults
        from config.agents_config import RANKING_SCORING_CONFIG
        current_weights = self.user_preferences.get(user_id, {}).get('weights', RANKING_SCORING_CONFIG['default_criteria_weights'].copy())
        
        # Adjust weights based on rating
        learning_rate = self.rating_config['learning_rate']
        
        if rating >= 4:
            # Positive feedback: boost criteria that were already strong
            for criterion, score in criteria_scores.items():
                if score > 0.7:  # Was a strong criterion
                    current_weights[criterion] = min(1.0, current_weights.get(criterion, 0) + learning_rate * 0.1)
        elif rating <= 2:
            # Negative feedback: reduce criteria that were weak
            for criterion, score in criteria_scores.items():
                if score < 0.5:  # Was a weak criterion
                    current_weights[criterion] = max(0.0, current_weights.get(criterion, 0) - learning_rate * 0.1)
        
        # Normalize weights
        total = sum(current_weights.values())
        if total > 0:
            current_weights = {k: v / total for k, v in current_weights.items()}
        
        self.user_preferences[user_id] = {'weights': current_weights}
        
        return self.user_preferences[user_id]
    
    def _apply_correction(self, target: str, feedback: Dict[str, Any]) -> bool:
        """
        Apply correction to target model.
        Placeholder for production ML pipeline.
        """
        self.logger.info(f"Applying correction to {target}")
        
        # Placeholder: In production, this would:
        # 1. Update model training data
        # 2. Retrain model (or update online)
        # 3. Deploy updated model
        
        # For now, just log the correction
        return True
    
    def _detect_drift(self, user_id: str) -> bool:
        """
        Detect if user preferences have drifted significantly.
        Uses sliding window variance.
        """
        if not self.drift_config['enable']:
            return False
        
        history = self.feedback_history.get(user_id, deque())
        
        if len(history) < self.drift_config['window_size']:
            return False
        
        # Extract ratings from history
        ratings = [item['rating'] for item in history]
        
        # Split into two halves and compare
        mid = len(ratings) // 2
        first_half = ratings[:mid]
        second_half = ratings[mid:]
        
        # Compare means
        mean1 = statistics.mean(first_half)
        mean2 = statistics.mean(second_half)
        
        change = abs(mean2 - mean1) / (mean1 + 0.01)  # Avoid div by zero
        
        if change > self.drift_config['threshold']:
            self.logger.info(f"Drift detected for {user_id}: {change:.2f} change")
            return True
        
        return False
    
    def _validate_weights(self, weights: Dict[str, float]) -> bool:
        """Validate that weights are valid (sum to 1.0)"""
        total = sum(weights.values())
        return 0.99 <= total <= 1.01
    
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Retrieve current preferences for a user"""
        if user_id in self.user_preferences:
            return self.user_preferences[user_id]
        
        # Return defaults
        from config.agents_config import RANKING_SCORING_CONFIG
        return {'weights': RANKING_SCORING_CONFIG['default_criteria_weights'].copy()}
    
    def get_correction_stats(self) -> Dict[str, Any]:
        """Get statistics about applied corrections"""
        if not self.correction_log:
            return {'total_corrections': 0}
        
        targets = [c['target'] for c in self.correction_log]
        target_counts = {t: targets.count(t) for t in set(targets)}
        
        return {
            'total_corrections': len(self.correction_log),
            'by_target': target_counts
        }


# Singleton instance (lowercase variable name)
feedback_learning = FeedbackLearningAgent()
