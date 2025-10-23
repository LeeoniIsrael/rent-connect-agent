"""
Tools Configuration
Settings for knowledge graph, listing analyzer, image analyzer, and compliance checker
"""

# Knowledge Graph settings
KNOWLEDGE_GRAPH_CONFIG = {
    'max_entities': 10000,
    'max_relations': 50000,
    'enable_caching': True,
    'cache_ttl_seconds': 3600
}

# Listing Analyzer settings
LISTING_ANALYZER_CONFIG = {
    'risk_threshold': 0.6,  # 0-1 scale, above this = suspicious
    'min_photo_count': 3,
    'price_anomaly_threshold': 0.5,  # 50% below median = red flag
    'enable_ml_models': False,  # Set to True when trained models available
    'ml_model_path': None
}

# Image Analyzer settings
IMAGE_ANALYZER_CONFIG = {
    'min_resolution': 640,  # pixels
    'min_photo_count': 3,
    'quality_threshold': 0.5,  # 0-1 scale
    'enable_cv_models': False,  # Set to True for production CV models
    'cv_model_type': 'mobilenet_v2',  # or 'efficientnet_lite'
    'stock_photo_detection': True
}

# Compliance Checker settings
COMPLIANCE_CHECKER_CONFIG = {
    'fha_protected_classes': [
        'race', 'color', 'national_origin', 'religion',
        'sex', 'familial_status', 'disability'
    ],
    'fha_prohibited_language': [
        'adults only', 'no children', 'christian home', 'muslim home', 'jewish home',
        'male only', 'female only', 'no section 8', 'perfect for singles',
        'no disabled', 'able-bodied only', 'mature tenants', 'no kids'
    ],
    'safety_score_default': 0.7,
    'required_disclosures_sc': [
        'lead_paint_disclosure',  # for pre-1978 buildings
        'mold_disclosure',
        'lease_length',
        'security_deposit_amount'
    ]
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
