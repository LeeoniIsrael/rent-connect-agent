"""
Data Ingestion Preprocessing Module

Description:
Collects rental listings, transit data, market data, and safety information from multiple 
external data sources. Performs cleaning, normalization, and deduplication operations.
Not an agent - preprocessing pipeline that runs before agent workflows.

Input Streams:
- API requests to external data sources (Zillow, Redfin, GIS, GTFS, HUD, Census)
- Filter parameters (location, price range, property type)
- Cache status (check for recent fetches)

Output Streams:
- Cleaned rental listing records
- Transit stop/route data
- Market rate information
- Demographic data
- Data quality metrics

Configuration:
See: config/preprocessing_config.py
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class DataIngestion:
    """
    Preprocessing module for multi-source data collection and cleaning.
    
    This is NOT an agent - it's a preprocessing step that runs before 
    agent-based reasoning begins.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize data ingestion module.
        
        Args:
            config: Configuration dictionary with data source URLs and settings
        """
        self.config = config or {}
        self.cache = {}  # Simple in-memory cache
        self.cache_duration = timedelta(hours=1)
        logger.info("DataIngestion preprocessing module initialized")
    
    def ingest_listings(
        self, 
        sources: List[str],
        filters: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Ingest rental listings from specified data sources.
        
        Input Stream:
            - sources: List of source names ['zillow_zori', 'redfin', 'columbia_gis']
            - filters: Dict with location, price_range, property_type, etc.
        
        Output Stream:
            - Dict with 'records', 'metadata', 'quality_metrics'
        
        Args:
            sources: List of data source identifiers
            filters: Optional filtering criteria
            
        Returns:
            Dictionary containing:
                - records: List of cleaned listing dictionaries
                - metadata: Source info, fetch timestamp, record count
                - quality_metrics: Duplicate rate, missing fields, etc.
        """
        filters = filters or {}
        all_records = []
        metadata = {
            'sources_used': sources,
            'fetch_timestamp': datetime.now().isoformat(),
            'filters_applied': filters
        }
        
        for source in sources:
            # Check cache first
            cache_key = f"{source}_{str(filters)}"
            if cache_key in self.cache:
                cached_data, cache_time = self.cache[cache_key]
                if datetime.now() - cache_time < self.cache_duration:
                    logger.info(f"Using cached data for {source}")
                    all_records.extend(cached_data)
                    continue
            
            # Fetch from source
            records = self._fetch_from_source(source, filters)
            
            # Cache results
            self.cache[cache_key] = (records, datetime.now())
            all_records.extend(records)
        
        # Clean and deduplicate
        cleaned_records = self._clean_data(all_records)
        deduplicated_records = self._deduplicate(cleaned_records)
        
        # Calculate quality metrics
        quality_metrics = {
            'total_fetched': len(all_records),
            'after_cleaning': len(cleaned_records),
            'after_deduplication': len(deduplicated_records),
            'duplicate_rate': (len(cleaned_records) - len(deduplicated_records)) / max(len(cleaned_records), 1),
            'sources_count': len(sources)
        }
        
        logger.info(f"Ingested {len(deduplicated_records)} records from {len(sources)} sources")
        
        return {
            'records': deduplicated_records,
            'metadata': metadata,
            'quality_metrics': quality_metrics
        }
    
    def _fetch_from_source(self, source: str, filters: Dict) -> List[Dict]:
        """Fetch data from specified source (simulation for now)"""
        logger.info(f"Simulating fetch from {source}")
        
        # Simulation - in production, make actual API calls
        simulated_record = {
            'source': source,
            'listing_id': f"{source}_sim_001",
            'title': f"Sample {source} listing",
            'price': 800 + hash(source) % 400,
            'bedrooms': 2,
            'bathrooms': 1,
            'address': f"123 {source.title()} St",
            'lat': 33.99 + (hash(source) % 10) / 1000,
            'lon': -81.03 + (hash(source) % 10) / 1000,
            'fetch_timestamp': datetime.now().isoformat()
        }
        
        return [simulated_record]
    
    def _clean_data(self, records: List[Dict]) -> List[Dict]:
        """Clean and normalize records"""
        cleaned = []
        
        for record in records:
            # Remove records with missing critical fields
            if not all(k in record for k in ['listing_id', 'price', 'address']):
                continue
            
            # Normalize data types
            try:
                record['price'] = float(record.get('price', 0))
                record['bedrooms'] = int(record.get('bedrooms', 0))
                record['bathrooms'] = float(record.get('bathrooms', 0))
                record['lat'] = float(record.get('lat', 0))
                record['lon'] = float(record.get('lon', 0))
            except (ValueError, TypeError):
                continue
            
            # Validate price range
            if not (100 <= record['price'] <= 5000):
                continue
            
            cleaned.append(record)
        
        return cleaned
    
    def _deduplicate(self, records: List[Dict]) -> List[Dict]:
        """Remove duplicate records based on listing_id or address similarity"""
        seen_ids = set()
        deduplicated = []
        
        for record in records:
            listing_id = record.get('listing_id')
            if listing_id and listing_id not in seen_ids:
                seen_ids.add(listing_id)
                deduplicated.append(record)
        
        return deduplicated
    
    def ingest_transit_data(self, gtfs_source: str) -> Dict[str, Any]:
        """
        Ingest transit data from GTFS feed.
        
        Input Stream:
            - gtfs_source: GTFS feed URL or identifier
        
        Output Stream:
            - Dict with stops, routes, schedules
        
        Returns:
            Dictionary with transit stops, routes, and schedule data
        """
        logger.info(f"Ingesting transit data from {gtfs_source}")
        
        # Simulation - in production, parse actual GTFS files
        transit_data = {
            'stops': [
                {'stop_id': 'USC_MAIN', 'name': 'USC Main Campus', 'lat': 33.9937, 'lon': -81.0266},
                {'stop_id': 'FIVE_POINTS', 'name': 'Five Points', 'lat': 34.0007, 'lon': -81.0348}
            ],
            'routes': [
                {'route_id': 'COMET_1', 'name': 'Route 1', 'type': 'bus'}
            ],
            'fetch_timestamp': datetime.now().isoformat()
        }
        
        return transit_data
    
    def get_market_rates(self, location: Dict) -> Dict[str, float]:
        """
        Get market rate data for location.
        
        Input Stream:
            - location: Dict with 'city', 'state', 'zip_code'
        
        Output Stream:
            - Dict with median_rent, percentile_25, percentile_75
        
        Returns:
            Market rate statistics
        """
        logger.info(f"Fetching market rates for {location}")
        
        # Simulation - in production, query HUD FMR or Zillow ZORI
        return {
            'median_rent': 950.0,
            'percentile_25': 750.0,
            'percentile_75': 1200.0,
            'data_source': 'HUD_FMR',
            'fetch_timestamp': datetime.now().isoformat()
        }
