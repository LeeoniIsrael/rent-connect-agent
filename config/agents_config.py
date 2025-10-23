"""
Agent Configuration
Settings for the 4 decision-making agents:
- Roommate Matching Agent
- Ranking & Scoring Agent
- Route Planning Agent
- Feedback & Learning Agent
"""

# Roommate Matching Agent settings
ROOMMATE_MATCHING_CONFIG = {
    'algorithm': 'gale_shapley_with_constraints',
    'max_candidates_per_person': 20,
    'hard_constraint_weight': float('inf'),  # Must satisfy hard constraints
    
    'soft_preference_weights': {
        'cleanliness': 0.25,
        'social_level': 0.20,
        'schedule_compatibility': 0.15
    },
    
    'personality_weights': {  # Big Five
        'conscientiousness': 0.15,
        'agreeableness': 0.10,
        'extraversion': 0.08,
        'openness': 0.05,
        'neuroticism': 0.02
    },
    
    'fairness_constraints': {
        'min_match_rate': 0.80,  # At least 80% get matched
        'max_quality_variance': 0.15  # Matches should be fairly distributed
    },
    
    'group_matching': {
        'enable': True,
        'max_group_size': 4,
        'min_group_compatibility': 0.60
    }
}

# Ranking & Scoring Agent settings
RANKING_SCORING_CONFIG = {
    'default_criteria_weights': {
        'price': 0.30,
        'commute_time': 0.25,
        'safety_score': 0.20,
        'amenities_match': 0.15,
        'lease_suitability': 0.10
    },
    
    'min_weight_per_criterion': 0.0,
    'max_weight_per_criterion': 0.5,  # No single factor dominates
    
    'commute_config': {
        'transport_modes': ['walk', 'transit', 'bike', 'drive'],
        'mode_speeds': {  # km/h
            'walk': 5,
            'bike': 15,
            'transit': 20,
            'drive': 40
        },
        'transit_wait_time_avg': 10,  # minutes
        'drive_parking_time_avg': 5,  # minutes
        'max_commute_time': 60  # minutes
    },
    
    'pareto_optimal_detection': True,
    'max_results': 50,
    'enable_explanations': True
}

# Route Planning Agent settings
ROUTE_PLANNING_CONFIG = {
    'algorithm': 'nearest_neighbor_tsp',
    'default_viewing_duration': 30,  # minutes per property
    'travel_time_buffer': 10,  # minutes safety buffer
    'max_stops_per_day': 8,
    'max_tour_duration': 480,  # minutes (8 hours)
    
    'transport_mode': 'transit',  # default mode for route planning
    'respect_class_schedule': True,
    'min_break_duration': 30,  # minutes between viewings
    
    'optimization_objective': 'minimize_total_time',  # or 'maximize_viewings'
    'enable_gtfs_integration': False  # Set True when GTFS data available
}

# Feedback & Learning Agent settings
FEEDBACK_LEARNING_CONFIG = {
    'feedback_types': ['rating', 'correction', 'preference_update'],
    
    'rating_config': {
        'scale': [1, 2, 3, 4, 5],
        'min_ratings_before_update': 5,
        'learning_rate': 0.1
    },
    
    'correction_config': {
        'require_expert_verification': True,
        'min_confidence_for_auto_apply': 0.8,
        'correction_categories': [
            'scam_detection', 'price_accuracy', 'amenity_info',
            'safety_score', 'commute_estimate'
        ]
    },
    
    'preference_update_config': {
        'allow_real_time_updates': True,
        'update_strategy': 'weighted_average',  # or 'replace'
        'decay_factor': 0.95  # older preferences decay slowly
    },
    
    'drift_detection': {
        'enable': True,
        'window_size': 100,  # feedback items to analyze
        'threshold': 0.2  # 20% change triggers alert
    },
    
    'evaluation_metrics': {
        'track_improvement_rate': True,
        'track_incorporation_rate': True,
        'track_user_satisfaction': True
    }
}

# Human-in-the-Loop settings (applies to all agents)
HITL_CONFIG = {
    'enable': True,
    'review_checkpoints': {
        'high_risk_listings': True,  # Listings flagged with risk > 0.7
        'policy_violations': True,    # Any FHA/lease law violations
        'low_match_quality': True,    # Roommate matches < 0.5 compatibility
        'safety_concerns': True       # Properties with safety score < 0.4
    },
    'approval_workflow': {
        'require_expert_review': True,
        'timeout_seconds': 3600,  # 1 hour to review
        'auto_approve_on_timeout': False
    },
    'override_capability': {
        'allow_expert_override': True,
        'log_override_reasons': True
    }
}
