"""
Preprocessing Configuration
Settings for data ingestion and survey processing modules
"""

# Data source URLs and endpoints
DATA_SOURCES = {
    'zillow_zori': 'https://www.zillow.com/research/data/',
    'redfin_rental': 'https://www.redfin.com/news/data-center/rental-market-data/',
    'columbia_gis': 'https://gis.columbiasc.gov/',
    'comet_gtfs': 'https://www.transit.land/feeds/f-dnn3-thecomet~sc~us',
    'hud_fmr': 'https://www.huduser.gov/portal/datasets/fmr.html',
    'census_acs': 'https://api.census.gov/data'
}

# Data ingestion settings
DATA_INGESTION_CONFIG = {
    'cache_duration_hours': 1,
    'max_concurrent_fetches': 5,
    'request_timeout_seconds': 30,
    'retry_attempts': 3,
    'retry_delay_seconds': 2
}

# Data quality thresholds
DATA_QUALITY_CONFIG = {
    'min_price': 100,
    'max_price': 5000,
    'required_fields': ['listing_id', 'price', 'address'],
    'deduplication_method': 'listing_id'  # or 'address_similarity'
}

# Survey processing settings
SURVEY_INGESTION_CONFIG = {
    'fha_protected_classes': [
        'race', 'color', 'national_origin', 'religion',
        'sex', 'familial_status', 'disability'
    ],
    'score_normalization': {
        'cleanliness': {'min': 1, 'max': 10},
        'social_level': {'min': 1, 'max': 10},
        'schedule': {'min': 1, 'max': 10}
    },
    'required_survey_fields': ['student_id', 'name', 'email'],
    'personality_defaults': {
        'conscientiousness': 0.5,
        'agreeableness': 0.5,
        'extraversion': 0.5,
        'openness': 0.5,
        'neuroticism': 0.5
    }
}

# Budget ranges
BUDGET_CONFIG = {
    'default_min': 0,
    'default_max': 2000,
    'currency': 'USD'
}
