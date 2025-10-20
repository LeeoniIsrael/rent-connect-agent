"""
Data Ingestion Agent
Collects and cleans property listings, roommate surveys, and safety data from multiple sources.
Sources: Zillow ZORI, Redfin, Kaggle datasets, Craigslist, Columbia GIS, COMET GTFS
"""

from typing import Any, Dict, List, Optional
import requests
from datetime import datetime
from ..base_agent import BaseAgent, AgentContext, AgentOutput


class DataSource:
    """Represents a data source with extraction logic"""
    def __init__(self, name: str, url: str, source_type: str):
        self.name = name
        self.url = url
        self.source_type = source_type  # 'api', 'csv', 'json', 'gtfs', 'gis'
        

class DataIngestionAgent(BaseAgent):
    """
    Ingests housing listings, roommate surveys, safety data, and transit info.
    Implements C3AN: Grounding (real data sources), Reliability (dedup), Attribution
    """
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__("DataIngestionAgent", config)
        self.sources = self._initialize_sources()
        self.cache = {}  # Simple cache for recent data
        
    def _initialize_sources(self) -> Dict[str, DataSource]:
        """Initialize all data sources"""
        return {
            'zillow_zori': DataSource(
                'Zillow ZORI',
                'https://www.zillow.com/research/data/',
                'csv'
            ),
            'redfin_rental': DataSource(
                'Redfin Rental Market',
                'https://www.redfin.com/news/data-center/rental-market-data/',
                'csv'
            ),
            'columbia_gis': DataSource(
                'Columbia SC GIS',
                'https://gis.columbiasc.gov/',
                'gis'
            ),
            'comet_gtfs': DataSource(
                'COMET Transit GTFS',
                'https://www.transit.land/feeds/f-dnn3-thecomet~sc~us',
                'gtfs'
            ),
            'hud_fmr': DataSource(
                'HUD Fair Market Rents',
                'https://www.huduser.gov/portal/datasets/fmr.html',
                'api'
            ),
            'census_acs': DataSource(
                'Census ACS',
                'https://www.census.gov/programs-surveys/acs/data/data-via-api.html',
                'api'
            )
        }
    
    def process(self, input_data: Any, context: AgentContext) -> AgentOutput:
        """
        Ingest data from specified sources.
        
        Args:
            input_data: Dict with 'sources' (list of source names) and 'filters' (optional)
            context: Shared agent context
            
        Returns:
            AgentOutput with ingested and cleaned data
        """
        if not self.validate_input(input_data):
            return self.create_output(
                result=None,
                confidence=0.0,
                explanation="Invalid input data",
                attribution=[],
                errors=["Input validation failed"]
            )
        
        sources_to_fetch = input_data.get('sources', list(self.sources.keys()))
        filters = input_data.get('filters', {})
        
        ingested_data = {}
        attribution = []
        errors = []
        
        for source_name in sources_to_fetch:
            if source_name not in self.sources:
                errors.append(f"Unknown source: {source_name}")
                continue
                
            try:
                data = self._fetch_from_source(source_name, filters, context)
                cleaned_data = self._clean_data(data, source_name)
                deduplicated_data = self._deduplicate(cleaned_data, source_name)
                
                ingested_data[source_name] = deduplicated_data
                attribution.append(f"{self.sources[source_name].name} ({len(deduplicated_data)} records)")
                
                self.log_decision(
                    f"Ingested {len(deduplicated_data)} records from {source_name}",
                    f"Applied filters: {filters}",
                    context
                )
                
            except Exception as e:
                errors.append(f"Error fetching {source_name}: {str(e)}")
                self.logger.error(f"Failed to fetch {source_name}: {e}")
        
        confidence = len(ingested_data) / len(sources_to_fetch) if sources_to_fetch else 0.0
        
        return self.create_output(
            result=ingested_data,
            confidence=confidence,
            explanation=f"Ingested data from {len(ingested_data)} sources: {', '.join(ingested_data.keys())}",
            attribution=attribution,
            errors=errors
        )
    
    def validate_input(self, input_data: Any) -> bool:
        """Validate ingestion request"""
        if not isinstance(input_data, dict):
            return False
        
        # Check if sources is a list if provided
        if 'sources' in input_data and not isinstance(input_data['sources'], list):
            return False
            
        return True
    
    def _fetch_from_source(
        self,
        source_name: str,
        filters: Dict,
        context: AgentContext
    ) -> List[Dict]:
        """
        Fetch data from a specific source.
        In production, this would make actual API calls or file reads.
        """
        source = self.sources[source_name]
        
        # Check cache first (C3AN: Efficiency/Compactness)
        cache_key = f"{source_name}_{hash(str(filters))}"
        if cache_key in self.cache:
            self.logger.info(f"Cache hit for {source_name}")
            return self.cache[cache_key]
        
        # Simulate data fetching based on source type
        # In production, replace with actual API calls
        data = self._simulate_fetch(source, filters)
        
        # Cache the result
        self.cache[cache_key] = data
        
        return data
    
    def _simulate_fetch(self, source: DataSource, filters: Dict) -> List[Dict]:
        """
        Simulate data fetching.
        In production, replace with actual implementation.
        """
        # This is a placeholder - implement actual fetching logic
        self.logger.info(f"Simulating fetch from {source.name}")
        
        if source.source_type == 'gtfs':
            # Simulate GTFS transit data
            return [
                {
                    'stop_id': 'STOP_001',
                    'stop_name': 'USC Campus Center',
                    'stop_lat': 33.9937,
                    'stop_lon': -81.0266,
                    'routes': ['Route_1', 'Route_3']
                }
            ]
        elif source.source_type == 'gis':
            # Simulate GIS property data
            return [
                {
                    'parcel_id': 'P12345',
                    'address': '123 Main St, Columbia, SC',
                    'lat': 33.9937,
                    'lon': -81.0266,
                    'zoning': 'Residential'
                }
            ]
        else:
            # Simulate rental listings
            return [
                {
                    'listing_id': 'L001',
                    'address': '456 College Ave, Columbia, SC',
                    'price': 800,
                    'bedrooms': 2,
                    'bathrooms': 1,
                    'amenities': ['AC', 'Parking', 'Laundry']
                }
            ]
    
    def _clean_data(self, data: List[Dict], source_name: str) -> List[Dict]:
        """
        Clean and normalize data from different sources.
        C3AN: Reliability & Consistency
        """
        cleaned = []
        
        for record in data:
            # Remove null/empty values
            cleaned_record = {k: v for k, v in record.items() if v is not None and v != ''}
            
            # Add metadata
            cleaned_record['_source'] = source_name
            cleaned_record['_ingested_at'] = datetime.utcnow().isoformat()
            
            # Normalize field names (lowercase, underscores)
            normalized_record = {
                k.lower().replace(' ', '_'): v
                for k, v in cleaned_record.items()
            }
            
            cleaned.append(normalized_record)
        
        return cleaned
    
    def _deduplicate(self, data: List[Dict], source_name: str) -> List[Dict]:
        """
        Remove duplicate records.
        C3AN: Reliability & Consistency
        """
        # Simple deduplication based on ID fields
        id_fields = ['listing_id', 'parcel_id', 'stop_id', 'property_id']
        
        seen = set()
        deduplicated = []
        
        for record in data:
            # Find ID field
            record_id = None
            for field in id_fields:
                if field in record:
                    record_id = record[field]
                    break
            
            if record_id is None:
                # Generate ID from key fields if no ID exists
                record_id = hash(str(sorted(record.items())))
            
            if record_id not in seen:
                seen.add(record_id)
                deduplicated.append(record)
        
        removed = len(data) - len(deduplicated)
        if removed > 0:
            self.logger.info(f"Removed {removed} duplicate records from {source_name}")
        
        return deduplicated


class RoommateSurveyIngestionAgent(BaseAgent):
    """
    Specialized agent for ingesting roommate preference surveys.
    Handles Big Five personality data and student preferences.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__("RoommateSurveyIngestionAgent", config)
        
    def process(self, input_data: Any, context: AgentContext) -> AgentOutput:
        """Process roommate survey responses"""
        if not self.validate_input(input_data):
            return self.create_output(
                result=None,
                confidence=0.0,
                explanation="Invalid survey data",
                attribution=[],
                errors=["Survey validation failed"]
            )
        
        # Extract survey responses
        survey_data = input_data.get('survey_responses', {})
        user_id = input_data.get('user_id')
        
        # Parse preferences
        preferences = self._parse_preferences(survey_data)
        
        # Validate Fair Housing compliance (no discriminatory preferences)
        is_compliant, violations = self._check_fha_compliance(preferences)
        
        if not is_compliant:
            return self.create_output(
                result=None,
                confidence=0.0,
                explanation="Survey contains Fair Housing Act violations",
                attribution=["Fair Housing Act"],
                errors=violations
            )
        
        return self.create_output(
            result={
                'user_id': user_id,
                'preferences': preferences,
                'timestamp': datetime.utcnow().isoformat()
            },
            confidence=1.0,
            explanation="Survey processed successfully",
            attribution=["User survey input"],
            errors=[]
        )
    
    def validate_input(self, input_data: Any) -> bool:
        """Validate survey input"""
        if not isinstance(input_data, dict):
            return False
        return 'survey_responses' in input_data and 'user_id' in input_data
    
    def _parse_preferences(self, survey_data: Dict) -> Dict:
        """Parse survey responses into structured preferences"""
        return {
            'hard_constraints': {
                'no_smoking': survey_data.get('smoking_preference') == 'no_smoking',
                'pet_policy': survey_data.get('pet_preference', 'no_preference'),
                'quiet_hours': survey_data.get('quiet_hours', False)
            },
            'soft_preferences': {
                'cleanliness': survey_data.get('cleanliness_scale', 5),  # 1-10
                'social_level': survey_data.get('social_scale', 5),
                'schedule_match': survey_data.get('schedule_type', 'flexible')
            },
            'personality': {
                'openness': survey_data.get('openness', 0.5),
                'conscientiousness': survey_data.get('conscientiousness', 0.5),
                'extraversion': survey_data.get('extraversion', 0.5),
                'agreeableness': survey_data.get('agreeableness', 0.5),
                'neuroticism': survey_data.get('neuroticism', 0.5)
            }
        }
    
    def _check_fha_compliance(self, preferences: Dict) -> tuple[bool, List[str]]:
        """
        Check preferences against Fair Housing Act.
        C3AN: Alignment, Safety, Compliance
        """
        violations = []
        
        # Check for prohibited criteria (race, religion, national origin, etc.)
        prohibited_keys = ['race', 'religion', 'national_origin', 'familial_status', 
                          'disability', 'sex', 'gender', 'age']
        
        for key in prohibited_keys:
            if key in preferences.get('hard_constraints', {}):
                violations.append(f"Prohibited criterion: {key}")
            if key in preferences.get('soft_preferences', {}):
                violations.append(f"Prohibited criterion: {key}")
        
        return len(violations) == 0, violations
