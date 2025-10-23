"""
Listing Analyzer Tool

Description:
Analyzes rental listings for scam signals using pattern matching and price anomaly detection.
Extracts features from listing text (amenities, policies, lease terms) using NLP.
Provides risk scoring and verification signals for listings.

Input Streams:
- Listing data (title, description, price, contact info, photos)
- Market rate data (for price anomaly detection)
- Landlord verification status

Output Streams:
- Risk score (0-1, where 1 = high risk)
- Risk flags (list of detected warning signs)
- Extracted features (amenities, policies, lease terms)
- Verification status (verified/unverified/flagged)

Configuration:
See: config/tools_config.py
"""

from typing import Dict, List, Any, Optional
import re
import logging

logger = logging.getLogger(__name__)


class ListingAnalyzerTool:
    """
    Tool for scam detection and feature extraction from rental listings.
    
    This is a TOOL (not an agent) - provides analysis functions
    that agents can use when evaluating listings.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize listing analyzer tool.
        
        Args:
            config: Configuration with scam patterns and thresholds
        """
        self.config = config or {}
        self.risk_threshold = self.config.get('risk_threshold', 0.6)
        
        # Scam detection patterns
        self.urgent_patterns = [
            r'act (now|fast|quick)', r'going fast', r'won\'t last',
            r'must (decide|rent) (now|today)', r'limited time'
        ]
        
        self.payment_red_flags = [
            r'wire transfer', r'western union', r'moneygram',
            r'bitcoin', r'cryptocurrency', r'cash only',
            r'pay (before|without) seeing', r'deposit (before|without) viewing'
        ]
        
        self.contact_red_flags = [
            r'out of (country|state|town)', r'cannot show', r'no phone',
            r'email only', r'text only', r'overseas'
        ]
        
        logger.info("Listing analyzer tool initialized")
    
    def analyze_listing(
        self,
        listing: Dict,
        market_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Analyze listing for scams and extract features.
        
        Input Stream:
            - listing: Dict with title, description, price, contact, photos
            - market_data: Optional market rate data for price comparison
        
        Output Stream:
            - Dict with risk_score, risk_flags, features, verification_status
        
        Args:
            listing: Listing data dictionary
            market_data: Optional market rate statistics
            
        Returns:
            Analysis results with risk assessment and extracted features
        """
        listing_id = listing.get('listing_id', 'unknown')
        logger.debug(f"Analyzing listing {listing_id}")
        
        # Detect scam signals
        risk_score, risk_flags = self._detect_scam_signals(listing)
        
        # Check price anomalies
        if market_data:
            price_risk, price_flags = self._check_price_anomaly(listing, market_data)
            risk_score = max(risk_score, price_risk)
            risk_flags.extend(price_flags)
        
        # Extract features
        features = self._extract_features(listing)
        
        # Check verification status
        verification_status = self._check_verification(listing)
        
        # Overall assessment
        is_suspicious = risk_score >= self.risk_threshold
        
        return {
            'listing_id': listing_id,
            'risk_score': risk_score,
            'risk_flags': risk_flags,
            'features': features,
            'verification_status': verification_status,
            'is_suspicious': is_suspicious,
            'analysis_timestamp': listing.get('fetch_timestamp', '')
        }
    
    def _detect_scam_signals(self, listing: Dict) -> tuple[float, List[str]]:
        """
        Detect scam signals in listing text.
        
        Returns:
            (risk_score, list of risk flags)
        """
        flags = []
        text = f"{listing.get('title', '')} {listing.get('description', '')}".lower()
        
        # Check for urgent language
        for pattern in self.urgent_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                flags.append(f"Urgent language: {pattern}")
        
        # Check for payment red flags
        for pattern in self.payment_red_flags:
            if re.search(pattern, text, re.IGNORECASE):
                flags.append(f"Payment red flag: {pattern}")
        
        # Check for suspicious contact info
        for pattern in self.contact_red_flags:
            if re.search(pattern, text, re.IGNORECASE):
                flags.append(f"Suspicious contact: {pattern}")
        
        # Check for incomplete information
        required_fields = ['address', 'price', 'bedrooms', 'bathrooms']
        missing_fields = [f for f in required_fields if not listing.get(f)]
        if missing_fields:
            flags.append(f"Missing information: {', '.join(missing_fields)}")
        
        # Check photo count
        photo_count = len(listing.get('photos', []))
        if photo_count == 0:
            flags.append("No photos provided")
        elif photo_count < 3:
            flags.append("Very few photos (< 3)")
        
        # Calculate risk score (0-1 scale)
        base_score = min(len(flags) * 0.15, 1.0)
        
        # Higher weight for payment and contact red flags
        for flag in flags:
            if 'payment red flag' in flag.lower():
                base_score = min(base_score + 0.3, 1.0)
            elif 'suspicious contact' in flag.lower():
                base_score = min(base_score + 0.25, 1.0)
        
        return base_score, flags
    
    def _check_price_anomaly(
        self,
        listing: Dict,
        market_data: Dict
    ) -> tuple[float, List[str]]:
        """
        Check if price is anomalously low (too good to be true).
        
        Returns:
            (price_risk_score, price_flags)
        """
        flags = []
        price = listing.get('price', 0)
        median_rent = market_data.get('median_rent', 0)
        percentile_25 = market_data.get('percentile_25', 0)
        
        if median_rent == 0:
            return 0.0, flags
        
        # Check if significantly below market
        price_ratio = price / median_rent
        
        if price_ratio < 0.5:
            flags.append(f"Price extremely low: {price_ratio:.0%} of median")
            return 0.8, flags
        elif price_ratio < 0.7:
            flags.append(f"Price unusually low: {price_ratio:.0%} of median")
            return 0.4, flags
        elif price < percentile_25:
            flags.append(f"Price below 25th percentile")
            return 0.2, flags
        
        return 0.0, flags
    
    def _extract_features(self, listing: Dict) -> Dict[str, Any]:
        """
        Extract features from listing text using pattern matching.
        
        In production, would use NLP (spaCy/BERT) for better extraction.
        """
        text = f"{listing.get('title', '')} {listing.get('description', '')}".lower()
        
        # Extract amenities
        amenity_keywords = {
            'parking': r'parking|garage',
            'laundry': r'laundry|washer|dryer',
            'dishwasher': r'dishwasher',
            'air_conditioning': r'ac|air condition|central air',
            'heating': r'heat|heating|furnace',
            'pool': r'pool|swimming',
            'gym': r'gym|fitness|exercise',
            'security': r'security system|alarm|gated'
        }
        
        amenities = []
        for amenity, pattern in amenity_keywords.items():
            if re.search(pattern, text, re.IGNORECASE):
                amenities.append(amenity)
        
        # Extract policies
        pet_policy = 'unknown'
        if re.search(r'pet.{0,10}(friendly|welcome|allowed|ok)', text, re.IGNORECASE):
            pet_policy = 'pets_allowed'
        elif re.search(r'no.{0,5}pets?', text, re.IGNORECASE):
            pet_policy = 'no_pets'
        
        smoking_policy = 'unknown'
        if re.search(r'no.{0,5}smoking', text, re.IGNORECASE):
            smoking_policy = 'no_smoking'
        elif re.search(r'smoking.{0,10}(allowed|ok)', text, re.IGNORECASE):
            smoking_policy = 'smoking_allowed'
        
        # Extract lease terms
        lease_length = 'unknown'
        if re.search(r'12.{0,5}month', text, re.IGNORECASE):
            lease_length = '12_month'
        elif re.search(r'(6|six).{0,5}month', text, re.IGNORECASE):
            lease_length = '6_month'
        elif re.search(r'month.{0,5}to.{0,5}month', text, re.IGNORECASE):
            lease_length = 'month_to_month'
        
        return {
            'amenities': amenities,
            'pet_policy': pet_policy,
            'smoking_policy': smoking_policy,
            'lease_length': lease_length,
            'extracted_from': 'pattern_matching'
        }
    
    def _check_verification(self, listing: Dict) -> str:
        """
        Check landlord/listing verification status.
        
        Returns:
            Status: 'verified', 'unverified', or 'flagged'
        """
        landlord_id = listing.get('landlord_id')
        if not landlord_id:
            return 'unverified'
        
        # In production, check against landlord registry
        # For now, simulation based on landlord_id presence
        landlord_verified = listing.get('landlord_verified', False)
        
        if landlord_verified:
            return 'verified'
        else:
            return 'unverified'
    
    def batch_analyze(
        self,
        listings: List[Dict],
        market_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Analyze multiple listings in batch.
        
        Input Stream:
            - listings: List of listing dictionaries
            - market_data: Optional market rate data
        
        Output Stream:
            - Dict with analyzed_listings, suspicious_count, risk_distribution
        
        Args:
            listings: List of listing data dictionaries
            market_data: Optional market rate statistics
            
        Returns:
            Batch analysis results with statistics
        """
        logger.info(f"Batch analyzing {len(listings)} listings")
        
        analyzed_listings = []
        suspicious_count = 0
        risk_scores = []
        
        for listing in listings:
            analysis = self.analyze_listing(listing, market_data)
            analyzed_listings.append(analysis)
            
            if analysis['is_suspicious']:
                suspicious_count += 1
            
            risk_scores.append(analysis['risk_score'])
        
        # Calculate statistics
        avg_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0
        
        return {
            'analyzed_listings': analyzed_listings,
            'total_analyzed': len(listings),
            'suspicious_count': suspicious_count,
            'suspicious_rate': suspicious_count / len(listings) if listings else 0,
            'average_risk_score': avg_risk,
            'risk_distribution': {
                'low': len([s for s in risk_scores if s < 0.3]),
                'medium': len([s for s in risk_scores if 0.3 <= s < 0.6]),
                'high': len([s for s in risk_scores if s >= 0.6])
            }
        }


# Singleton instance (tool pattern)
listing_analyzer = ListingAnalyzerTool()
