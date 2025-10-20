"""
Configuration for RentConnect-C3AN Agent System
"""

import os
from typing import Dict, Any

# Environment variables
FIREBASE_PROJECT_ID = os.getenv('FIREBASE_PROJECT_ID', 'rentconnect-dev')
FIREBASE_API_KEY = os.getenv('FIREBASE_API_KEY', '')

# API Keys
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY', '')
ZILLOW_API_KEY = os.getenv('ZILLOW_API_KEY', '')

# Agent Configuration
AGENT_CONFIG: Dict[str, Any] = {
    'data_ingestion': {
        'cache_ttl_minutes': 60,
        'max_records_per_source': 1000
    },
    'knowledge_graph': {
        'max_entities': 10000,
        'max_relations': 50000
    },
    'listing_analysis': {
        'risk_threshold_high': 0.7,
        'risk_threshold_moderate': 0.4,
        'scam_patterns_file': 'data/scam_patterns.json'
    },
    'roommate_matching': {
        'weights': {
            'hard_constraints': 1.0,
            'personality': 0.3,
            'preferences': 0.4,
            'schedule': 0.2,
            'budget': 0.1
        },
        'min_compatibility_score': 0.5
    },
    'ranking_scoring': {
        'default_weights': {
            'price': 0.30,
            'commute_time': 0.25,
            'safety_score': 0.20,
            'amenities_match': 0.15,
            'lease_suitability': 0.10
        }
    },
    'route_planning': {
        'default_viewing_duration_minutes': 30,
        'travel_buffer_minutes': 15,
        'max_properties_per_day': 8
    },
    'compliance_safety': {
        'enable_fha_checks': True,
        'enable_safety_checks': True,
        'enable_landlord_verification': True
    },
    'explanation': {
        'max_explanation_length': 500,
        'include_technical_details': False
    },
    'feedback_learning': {
        'enable_learning': True,
        'min_feedback_count': 10
    }
}

# Campus Configuration (USC Columbia)
CAMPUS_CONFIG = {
    'name': 'University of South Carolina',
    'main_campus_location': {
        'lat': 33.9937,
        'lon': -81.0266
    },
    'search_radius_km': 5.0,
    'transit_system': 'COMET',
    'gtfs_feed_url': 'https://www.transit.land/feeds/f-dnn3-thecomet~sc~us'
}

# Data Source URLs
DATA_SOURCES = {
    'zillow_zori': 'https://www.zillow.com/research/data/',
    'redfin_rental': 'https://www.redfin.com/news/data-center/rental-market-data/',
    'columbia_gis': 'https://gis.columbiasc.gov/',
    'comet_gtfs': 'https://www.transit.land/feeds/f-dnn3-thecomet~sc~us',
    'hud_fmr': 'https://www.huduser.gov/portal/datasets/fmr.html',
    'census_acs': 'https://api.census.gov/data'
}

# Fair Housing Act Rules
FHA_PROTECTED_CLASSES = [
    'race', 'color', 'national_origin', 'religion',
    'sex', 'familial_status', 'disability'
]

FHA_PROHIBITED_LANGUAGE = [
    'adults only', 'no children', 'christian home', 'muslim home', 'jewish home',
    'male only', 'female only', 'no section 8', 'perfect for singles',
    'no disabled', 'able-bodied only'
]

# Logging Configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'standard',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'formatter': 'standard',
            'filename': 'logs/rentconnect.log'
        }
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True
        }
    }
}

# Feature Flags
FEATURE_FLAGS = {
    'enable_neural_models': True,  # Use neural models for analysis
    'enable_image_analysis': False,  # Enable image analysis (requires CV models)
    'enable_human_review': True,  # Require human review for critical decisions
    'enable_feedback_learning': True,  # Learn from user feedback
    'enable_route_optimization': True,  # Use advanced route optimization
    'enable_price_predictions': False  # Predict future prices (requires trained model)
}

# Performance Settings
PERFORMANCE_CONFIG = {
    'max_concurrent_agents': 5,
    'request_timeout_seconds': 30,
    'cache_enabled': True,
    'batch_processing_enabled': True,
    'batch_size': 50
}
