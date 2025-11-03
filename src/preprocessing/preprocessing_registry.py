"""
Preprocessing Registry for RentConnect-C3AN System

Central registry for all preprocessing components that ingest, clean, and prepare
data before it's consumed by agents and tools.
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum


logger = logging.getLogger(__name__)


class PreprocessorType(Enum):
    """Classification of preprocessor types"""
    DATA_INGESTION = "data_ingestion"      # Collects data from external sources
    SURVEY_PROCESSING = "survey_processing"  # Processes user input/surveys
    DATA_CLEANING = "data_cleaning"        # Cleans and normalizes data
    DATA_VALIDATION = "data_validation"    # Validates data quality


class DataSource(Enum):
    """Data source types"""
    API = "api"
    FILE = "file"
    DATABASE = "database"
    USER_INPUT = "user_input"
    STREAM = "stream"


@dataclass
class PreprocessorInputSchema:
    """Schema for preprocessor inputs"""
    name: str
    type: str
    description: str
    source: DataSource
    required: bool = True
    validation_rules: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PreprocessorOutputSchema:
    """Schema for preprocessor outputs"""
    name: str
    type: str
    description: str
    structure: Dict[str, Any] = field(default_factory=dict)
    quality_guarantees: List[str] = field(default_factory=list)


@dataclass
class PreprocessorMetadata:
    """Complete metadata for a registered preprocessor"""
    # Identity
    preprocessor_id: str
    name: str
    description: str
    version: str
    
    # Classification
    preprocessor_type: PreprocessorType
    data_sources: List[DataSource]
    
    # Interface
    input_schemas: List[PreprocessorInputSchema]
    output_schemas: List[PreprocessorOutputSchema]
    
    # Data Quality
    data_quality_checks: List[str] = field(default_factory=list)
    deduplication_enabled: bool = False
    normalization_enabled: bool = False
    validation_enabled: bool = False
    
    # Implementation
    module_path: str = ""
    class_name: str = ""
    singleton_instance: str = ""
    
    # Configuration
    config_module: str = ""
    
    # Dependencies
    external_apis: List[str] = field(default_factory=list)
    requires_credentials: bool = False
    
    # Performance
    avg_latency_ms: int = 0
    max_batch_size: int = 100
    supports_streaming: bool = False
    cache_enabled: bool = False
    cache_ttl_seconds: int = 0
    
    # Consumers
    consumed_by: List[str] = field(default_factory=list)  # Agent/tool IDs
    
    # Documentation
    readme_path: str = ""
    example_usage: str = ""


class PreprocessingRegistry:
    """
    Central registry for all preprocessing components in RentConnect-C3AN.
    Preprocessors ingest and prepare data for agents and tools.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._preprocessors: Dict[str, PreprocessorMetadata] = {}
        self._initialize_registry()
    
    def _initialize_registry(self):
        """Initialize registry with all system preprocessors"""
        self._register_data_ingestion()
        self._register_survey_ingestion()
        
        self.logger.info(f"Preprocessing registry initialized with {len(self._preprocessors)} components")
    
    def _register_data_ingestion(self):
        """Register the Data Ingestion Preprocessor"""
        preprocessor = PreprocessorMetadata(
            preprocessor_id="data_ingestion",
            name="Data Ingestion",
            description="Collects rental listings, transit data, and safety information from multiple external sources",
            version="1.0.0",
            
            preprocessor_type=PreprocessorType.DATA_INGESTION,
            data_sources=[
                DataSource.API,
                DataSource.FILE
            ],
            
            input_schemas=[
                PreprocessorInputSchema(
                    name="sources",
                    type="List[str]",
                    description="List of data sources to ingest from",
                    source=DataSource.API,
                    required=False,
                    validation_rules={
                        "valid_sources": [
                            "zillow_zori",
                            "redfin",
                            "columbia_gis",
                            "comet_gtfs",
                            "hud_fmr",
                            "census_acs"
                        ]
                    }
                ),
                PreprocessorInputSchema(
                    name="filters",
                    type="Dict[str, Any]",
                    description="Filters for data collection (location, date range, etc.)",
                    source=DataSource.USER_INPUT,
                    required=False
                )
            ],
            
            output_schemas=[
                PreprocessorOutputSchema(
                    name="listings",
                    type="List[Dict[str, Any]]",
                    description="Cleaned and normalized property listings",
                    structure={
                        "listing_id": "str",
                        "price": "float",
                        "bedrooms": "int",
                        "bathrooms": "float",
                        "address": "str",
                        "latitude": "float",
                        "longitude": "float",
                        "description": "str",
                        "amenities": ["str"],
                        "lease_length_months": "int",
                        "security_deposit": "float",
                        "available_date": "str",
                        "source": "str",
                        "ingestion_timestamp": "str"
                    },
                    quality_guarantees=[
                        "No duplicate listings",
                        "All required fields present",
                        "Price normalized to monthly rent",
                        "Coordinates validated",
                        "Text cleaned (no HTML, special chars)"
                    ]
                ),
                PreprocessorOutputSchema(
                    name="transit_data",
                    type="Dict[str, Any]",
                    description="Transit stops, routes, and schedules",
                    structure={
                        "stops": [{
                            "stop_id": "str",
                            "name": "str",
                            "latitude": "float",
                            "longitude": "float"
                        }],
                        "routes": [{
                            "route_id": "str",
                            "name": "str",
                            "stops": ["stop_id"]
                        }],
                        "schedules": {
                            "route_id": {
                                "stop_id": ["arrival_time"]
                            }
                        }
                    },
                    quality_guarantees=[
                        "GTFS format validated",
                        "No orphaned stops",
                        "Valid coordinates"
                    ]
                ),
                PreprocessorOutputSchema(
                    name="market_data",
                    type="Dict[str, Any]",
                    description="Market rent statistics by area",
                    structure={
                        "area_id": {
                            "median_rent": "float",
                            "percentile_25": "float",
                            "percentile_75": "float",
                            "sample_size": "int",
                            "last_updated": "str"
                        }
                    },
                    quality_guarantees=[
                        "Statistical outliers removed",
                        "Minimum sample size enforced"
                    ]
                )
            ],
            
            data_quality_checks=[
                "Duplicate detection (by address + price)",
                "Required field validation",
                "Coordinate range validation",
                "Price anomaly detection",
                "Text sanitization"
            ],
            
            deduplication_enabled=True,
            normalization_enabled=True,
            validation_enabled=True,
            
            module_path="src.preprocessing.data_ingestion",
            class_name="DataIngestionPreprocessor",
            singleton_instance="data_ingestion",
            
            config_module="config.preprocessing_config",
            
            external_apis=[
                "zillow_zori_api",
                "redfin_api",
                "columbia_gis_api",
                "comet_gtfs_feed",
                "hud_fmr_api",
                "census_acs_api"
            ],
            requires_credentials=True,
            
            avg_latency_ms=5000,
            max_batch_size=1000,
            supports_streaming=False,
            cache_enabled=True,
            cache_ttl_seconds=3600,
            
            consumed_by=[
                "ranking_scoring",
                "listing_analyzer",
                "compliance_checker"
            ],
            
            readme_path="src/preprocessing/README.md",
            example_usage="""
from src.preprocessing.data_ingestion import data_ingestion

# Ingest listings from all sources
result = data_ingestion.ingest_listings(
    sources=['zillow_zori', 'redfin'],
    filters={'city': 'Columbia', 'state': 'SC'}
)

listings = result['listings']
print(f"Ingested {len(listings)} listings")

# Ingest transit data
transit = data_ingestion.ingest_transit_data(source='comet_gtfs')
print(f"Loaded {len(transit['stops'])} transit stops")
"""
        )
        
        self._preprocessors[preprocessor.preprocessor_id] = preprocessor
    
    def _register_survey_ingestion(self):
        """Register the Survey Ingestion Preprocessor"""
        preprocessor = PreprocessorMetadata(
            preprocessor_id="survey_ingestion",
            name="Survey Ingestion",
            description="Processes roommate preference surveys with FHA compliance validation",
            version="1.0.0",
            
            preprocessor_type=PreprocessorType.SURVEY_PROCESSING,
            data_sources=[DataSource.USER_INPUT],
            
            input_schemas=[
                PreprocessorInputSchema(
                    name="survey_response",
                    type="Dict[str, Any]",
                    description="Raw survey response from user",
                    source=DataSource.USER_INPUT,
                    required=True,
                    validation_rules={
                        "required_sections": [
                            "hard_constraints",
                            "soft_preferences",
                            "personality_scores",
                            "budget"
                        ]
                    }
                )
            ],
            
            output_schemas=[
                PreprocessorOutputSchema(
                    name="profile",
                    type="Dict[str, Any]",
                    description="Validated and structured roommate profile",
                    structure={
                        "user_id": "str",
                        "hard_constraints": {
                            "smoking": "bool",
                            "has_pets": "bool",
                            "allows_pets": "bool",
                            "quiet_hours": "(start_hour, end_hour)",
                            "budget_range": "(min, max)"
                        },
                        "soft_preferences": {
                            "cleanliness": "int (1-5)",
                            "social_level": "int (1-5)",
                            "schedule": "str (morning/evening/flexible)"
                        },
                        "personality": {
                            "conscientiousness": "int (1-5)",
                            "agreeableness": "int (1-5)",
                            "extraversion": "int (1-5)",
                            "openness": "int (1-5)",
                            "neuroticism": "int (1-5)"
                        },
                        "compliance_status": {
                            "fha_compliant": "bool",
                            "blocked_preferences": ["preference_1"],
                            "warnings": ["warning_1"]
                        }
                    },
                    quality_guarantees=[
                        "FHA compliance validated",
                        "No discriminatory preferences",
                        "All scores in valid ranges",
                        "Budget ranges validated"
                    ]
                )
            ],
            
            data_quality_checks=[
                "FHA compliance check (no protected class preferences)",
                "Score range validation (1-5 scales)",
                "Budget range validation",
                "Required field completeness"
            ],
            
            deduplication_enabled=False,
            normalization_enabled=True,
            validation_enabled=True,
            
            module_path="src.preprocessing.survey_ingestion",
            class_name="SurveyIngestionPreprocessor",
            singleton_instance="survey_ingestion",
            
            config_module="config.preprocessing_config",
            
            external_apis=[],
            requires_credentials=False,
            
            avg_latency_ms=100,
            max_batch_size=50,
            supports_streaming=False,
            cache_enabled=False,  # User data should not be cached
            cache_ttl_seconds=0,
            
            consumed_by=[
                "roommate_matching",
                "knowledge_graph"
            ],
            
            readme_path="src/preprocessing/README.md",
            example_usage="""
from src.preprocessing.survey_ingestion import survey_ingestion

survey = {
    'user_id': 'u1',
    'hard_constraints': {
        'smoking': False,
        'has_pets': True,
        'allows_pets': True,
        'quiet_hours': (22, 7),
        'budget_range': (800, 1200)
    },
    'soft_preferences': {
        'cleanliness': 4,
        'social_level': 3,
        'schedule': 'flexible'
    },
    'personality': {
        'conscientiousness': 4,
        'agreeableness': 5,
        'extraversion': 3,
        'openness': 4,
        'neuroticism': 2
    }
}

profile = survey_ingestion.process_survey(survey)

if profile['compliance_status']['fha_compliant']:
    print("Profile is FHA compliant")
else:
    print(f"Blocked preferences: {profile['compliance_status']['blocked_preferences']}")
"""
        )
        
        self._preprocessors[preprocessor.preprocessor_id] = preprocessor
    
    # Registry Query Methods
    
    def get_preprocessor(self, preprocessor_id: str) -> Optional[PreprocessorMetadata]:
        """Retrieve preprocessor metadata by ID"""
        return self._preprocessors.get(preprocessor_id)
    
    def list_preprocessors(self, preprocessor_type: Optional[PreprocessorType] = None) -> List[PreprocessorMetadata]:
        """List all preprocessors, optionally filtered by type"""
        if preprocessor_type:
            return [p for p in self._preprocessors.values() if p.preprocessor_type == preprocessor_type]
        return list(self._preprocessors.values())
    
    def find_preprocessors_by_source(self, data_source: DataSource) -> List[PreprocessorMetadata]:
        """Find preprocessors that handle a specific data source"""
        return [p for p in self._preprocessors.values() if data_source in p.data_sources]
    
    def get_preprocessor_instance(self, preprocessor_id: str) -> Optional[Any]:
        """
        Dynamically import and return the preprocessor singleton instance.
        Returns None if preprocessor not found or import fails.
        """
        preprocessor = self.get_preprocessor(preprocessor_id)
        if not preprocessor:
            self.logger.error(f"Preprocessor {preprocessor_id} not found in registry")
            return None
        
        try:
            module = __import__(preprocessor.module_path, fromlist=[preprocessor.singleton_instance])
            instance = getattr(module, preprocessor.singleton_instance)
            return instance
        except (ImportError, AttributeError) as e:
            self.logger.error(f"Failed to import preprocessor {preprocessor_id}: {e}")
            return None
    
    def validate_preprocessor_available(self, preprocessor_id: str) -> bool:
        """Check if preprocessor is registered and available"""
        return preprocessor_id in self._preprocessors
    
    def generate_registry_report(self) -> str:
        """Generate human-readable registry report"""
        report = "=" * 80 + "\n"
        report += "RENTCONNECT-C3AN PREPROCESSING REGISTRY REPORT\n"
        report += "=" * 80 + "\n\n"
        
        report += f"Total Registered Preprocessors: {len(self._preprocessors)}\n\n"
        
        for preprocessor_type in PreprocessorType:
            preprocessors = self.list_preprocessors(preprocessor_type)
            if preprocessors:
                report += f"\n{preprocessor_type.value.upper()} PREPROCESSORS ({len(preprocessors)}):\n"
                report += "-" * 80 + "\n"
                for prep in preprocessors:
                    report += f"  • {prep.name} (ID: {prep.preprocessor_id})\n"
                    report += f"    Version: {prep.version}\n"
                    report += f"    Data Sources: {', '.join(s.value for s in prep.data_sources)}\n"
                    report += f"    Quality Checks: {len(prep.data_quality_checks)}\n"
                    report += f"    Deduplication: {'Yes' if prep.deduplication_enabled else 'No'}\n"
                    report += f"    Consumed By: {', '.join(prep.consumed_by)}\n"
                    report += "\n"
        
        return report


# Global singleton instance
preprocessing_registry = PreprocessingRegistry()
