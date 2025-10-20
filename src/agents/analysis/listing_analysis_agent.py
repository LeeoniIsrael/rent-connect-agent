"""
Listing Analysis Agent
Neural component for scam detection, image analysis, and feature extraction.
Uses lightweight models for C3AN compactness.
"""

from typing import Any, Dict, List, Optional, Tuple
import re
from datetime import datetime
from ..base_agent import BaseAgent, AgentContext, AgentOutput


class ListingAnalysisAgent(BaseAgent):
    """
    Analyzes rental listings for:
    - Scam/anomaly detection (text and image patterns)
    - Feature extraction (amenities, policies)
    - Price anomaly detection
    - Landlord verification signals
    
    C3AN: Safety, Reliability, Grounding, Explainability
    """
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__("ListingAnalysisAgent", config)
        self.scam_patterns = self._load_scam_patterns()
        self.price_ranges = {}  # For anomaly detection
        
    def _load_scam_patterns(self) -> Dict[str, List[str]]:
        """Load known scam patterns and red flags"""
        return {
            'urgent_language': [
                r'urgent', r'must act now', r'limited time',
                r'going fast', r'won\'t last'
            ],
            'payment_red_flags': [
                r'wire transfer', r'western union', r'moneygram',
                r'bitcoin', r'cryptocurrency', r'gift card',
                r'cashiers check', r'pay before viewing'
            ],
            'suspicious_contact': [
                r'out of country', r'overseas', r'currently abroad',
                r'email only', r'no phone', r'text only'
            ],
            'too_good_to_be_true': [
                r'below market', r'unbelievable price', r'steal',
                r'amazing deal', r'must see'
            ],
            'incomplete_info': [
                r'no address provided', r'location varies',
                r'multiple locations'
            ]
        }
    
    def process(self, input_data: Any, context: AgentContext) -> AgentOutput:
        """
        Analyze a rental listing for risk factors and extract features.
        
        Args:
            input_data: Dict with 'listing' (listing data), 'check_types' (optional)
            context: Shared agent context
            
        Returns:
            AgentOutput with risk score, flags, and extracted features
        """
        if not self.validate_input(input_data):
            return self.create_output(
                result=None,
                confidence=0.0,
                explanation="Invalid listing data",
                attribution=[],
                errors=["Listing validation failed"]
            )
        
        listing = input_data.get('listing', {})
        check_types = input_data.get('check_types', ['scam', 'price', 'features'])
        
        analysis_results = {
            'listing_id': listing.get('listing_id'),
            'risk_score': 0.0,
            'risk_flags': [],
            'warnings': [],
            'extracted_features': {},
            'verification_status': 'unverified'
        }
        
        attribution = []
        
        # Scam detection
        if 'scam' in check_types:
            scam_score, scam_flags = self._detect_scam_signals(listing)
            analysis_results['risk_score'] += scam_score
            analysis_results['risk_flags'].extend(scam_flags)
            attribution.append("Scam pattern database")
        
        # Price anomaly detection
        if 'price' in check_types:
            price_risk, price_flags = self._check_price_anomaly(listing)
            analysis_results['risk_score'] += price_risk
            if price_flags:
                analysis_results['warnings'].extend(price_flags)
            attribution.append("Market price data")
        
        # Feature extraction
        if 'features' in check_types:
            features = self._extract_features(listing)
            analysis_results['extracted_features'] = features
            attribution.append("NLP feature extraction")
        
        # Landlord verification signals
        verification = self._check_verification_signals(listing)
        analysis_results['verification_status'] = verification
        attribution.append("Verification criteria")
        
        # Normalize risk score (0-1)
        analysis_results['risk_score'] = min(analysis_results['risk_score'], 1.0)
        
        # Generate explanation
        if analysis_results['risk_score'] > 0.7:
            explanation = f"HIGH RISK listing (score: {analysis_results['risk_score']:.2f}). Manual review recommended."
        elif analysis_results['risk_score'] > 0.4:
            explanation = f"MODERATE RISK listing (score: {analysis_results['risk_score']:.2f}). Caution advised."
        else:
            explanation = f"LOW RISK listing (score: {analysis_results['risk_score']:.2f}). Standard checks passed."
        
        confidence = 1.0 - analysis_results['risk_score']
        
        self.log_decision(
            f"Analyzed listing {listing.get('listing_id')}",
            f"Risk score: {analysis_results['risk_score']:.2f}, Flags: {len(analysis_results['risk_flags'])}",
            context
        )
        
        return self.create_output(
            result=analysis_results,
            confidence=confidence,
            explanation=explanation,
            attribution=attribution,
            errors=[]
        )
    
    def validate_input(self, input_data: Any) -> bool:
        """Validate listing input"""
        if not isinstance(input_data, dict):
            return False
        
        listing = input_data.get('listing')
        if not listing or not isinstance(listing, dict):
            return False
        
        # Must have at least description or title
        return 'description' in listing or 'title' in listing
    
    def _detect_scam_signals(self, listing: Dict) -> Tuple[float, List[str]]:
        """
        Detect scam signals in listing text.
        Returns (risk_score, flags)
        """
        text = f"{listing.get('title', '')} {listing.get('description', '')}".lower()
        flags = []
        risk_score = 0.0
        
        # Check each pattern category
        for category, patterns in self.scam_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    flags.append(f"Scam indicator ({category}): matched '{pattern}'")
                    # Weight different categories
                    if category == 'payment_red_flags':
                        risk_score += 0.3
                    elif category == 'urgent_language':
                        risk_score += 0.1
                    elif category == 'suspicious_contact':
                        risk_score += 0.2
                    elif category == 'too_good_to_be_true':
                        risk_score += 0.15
                    else:
                        risk_score += 0.1
        
        # Check for missing critical information
        required_fields = ['address', 'price', 'bedrooms', 'contact']
        missing = [f for f in required_fields if not listing.get(f)]
        if missing:
            flags.append(f"Missing critical fields: {', '.join(missing)}")
            risk_score += 0.1 * len(missing)
        
        # Check for duplicate/scraped content (simple heuristic)
        if 'listing_id' not in listing and 'source' not in listing:
            flags.append("No source attribution - possible scrape")
            risk_score += 0.1
        
        return risk_score, flags
    
    def _check_price_anomaly(self, listing: Dict) -> Tuple[float, List[str]]:
        """
        Check if price is anomalous compared to market data.
        Returns (risk_score, warnings)
        """
        price = listing.get('price', 0)
        bedrooms = listing.get('bedrooms', 1)
        location = listing.get('city', 'unknown')
        
        warnings = []
        risk = 0.0
        
        if price <= 0:
            warnings.append("Invalid price: $0 or negative")
            return 0.2, warnings
        
        # Get expected price range (in production, use market data)
        # For Columbia, SC near USC - rough estimates
        expected_ranges = {
            1: (400, 900),
            2: (600, 1400),
            3: (800, 1800),
            4: (1000, 2200)
        }
        
        if bedrooms in expected_ranges:
            min_price, max_price = expected_ranges[bedrooms]
            
            if price < min_price * 0.5:
                warnings.append(
                    f"Price ${price} is significantly below market "
                    f"(expected ${min_price}-${max_price} for {bedrooms}br)"
                )
                risk = 0.3  # Too good to be true
            elif price > max_price * 1.5:
                warnings.append(
                    f"Price ${price} is significantly above market "
                    f"(expected ${min_price}-${max_price} for {bedrooms}br)"
                )
                risk = 0.1  # Overpriced, less risky but noteworthy
        
        return risk, warnings
    
    def _extract_features(self, listing: Dict) -> Dict[str, Any]:
        """
        Extract structured features from listing text using NLP.
        In production, use lightweight NLP models (distilled BERT, etc.)
        """
        text = f"{listing.get('title', '')} {listing.get('description', '')}".lower()
        
        features = {
            'amenities': [],
            'policies': {},
            'lease_terms': {},
            'utilities': []
        }
        
        # Extract amenities
        amenity_keywords = {
            'parking': ['parking', 'garage', 'carport'],
            'laundry': ['laundry', 'washer', 'dryer', 'w/d'],
            'ac': ['ac', 'air conditioning', 'central air'],
            'heating': ['heat', 'heating', 'furnace'],
            'dishwasher': ['dishwasher'],
            'furnished': ['furnished', 'furniture included'],
            'pets': ['pet friendly', 'pets allowed', 'dogs ok', 'cats ok'],
            'pool': ['pool', 'swimming'],
            'gym': ['gym', 'fitness', 'workout'],
            'wifi': ['wifi', 'internet included']
        }
        
        for amenity, keywords in amenity_keywords.items():
            if any(kw in text for kw in keywords):
                features['amenities'].append(amenity)
        
        # Extract policies
        if 'no smoking' in text or 'non-smoking' in text:
            features['policies']['smoking'] = 'no_smoking'
        elif 'smoking allowed' in text:
            features['policies']['smoking'] = 'allowed'
        
        if 'pet friendly' in text or 'pets allowed' in text:
            features['policies']['pets'] = 'allowed'
        elif 'no pets' in text:
            features['policies']['pets'] = 'not_allowed'
        
        # Extract lease terms
        if 'month to month' in text or 'm2m' in text:
            features['lease_terms']['type'] = 'month_to_month'
        elif '12 month' in text or 'year lease' in text:
            features['lease_terms']['duration'] = '12_months'
        elif '9 month' in text:
            features['lease_terms']['duration'] = '9_months'
        
        if 'cosigner' in text or 'co-signer' in text:
            features['lease_terms']['cosigner_required'] = True
        
        # Extract utilities
        utility_keywords = ['water', 'electric', 'gas', 'trash', 'sewer', 'internet']
        for utility in utility_keywords:
            if f"{utility} included" in text or f"includes {utility}" in text:
                features['utilities'].append(utility)
        
        return features
    
    def _check_verification_signals(self, listing: Dict) -> str:
        """
        Check for landlord/property verification signals.
        Returns verification status: verified, partial, unverified
        """
        # Check for verification indicators
        has_landlord_id = listing.get('landlord_id') is not None
        has_property_docs = listing.get('property_documents') is not None
        has_verified_contact = listing.get('contact_verified', False)
        has_photos = listing.get('photos') and len(listing.get('photos', [])) > 0
        has_address = listing.get('address') is not None
        
        verification_score = sum([
            has_landlord_id,
            has_property_docs,
            has_verified_contact,
            has_photos,
            has_address
        ])
        
        if verification_score >= 4:
            return 'verified'
        elif verification_score >= 2:
            return 'partial'
        else:
            return 'unverified'


class ImageAnalysisAgent(BaseAgent):
    """
    Analyzes listing images for quality and authenticity.
    Uses lightweight CV models for C3AN compactness.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__("ImageAnalysisAgent", config)
        
    def process(self, input_data: Any, context: AgentContext) -> AgentOutput:
        """
        Analyze listing images.
        
        Args:
            input_data: Dict with 'images' (list of image URLs/paths)
            context: Shared agent context
            
        Returns:
            AgentOutput with image analysis results
        """
        if not self.validate_input(input_data):
            return self.create_output(
                result=None,
                confidence=0.0,
                explanation="Invalid image data",
                attribution=[],
                errors=["Image validation failed"]
            )
        
        images = input_data.get('images', [])
        
        results = {
            'total_images': len(images),
            'quality_score': 0.0,
            'flags': [],
            'detected_features': []
        }
        
        if len(images) == 0:
            results['flags'].append("No images provided")
            results['quality_score'] = 0.0
        else:
            # In production, use lightweight CV model (MobileNet, EfficientNet-Lite)
            # For now, simple heuristics
            results['quality_score'] = min(0.5 + (len(images) * 0.1), 1.0)
            
            # Check for stock photo patterns (placeholder)
            # In production: use image similarity/reverse image search
            if len(images) < 3:
                results['flags'].append("Limited photos available")
        
        explanation = f"Analyzed {len(images)} images, quality score: {results['quality_score']:.2f}"
        
        return self.create_output(
            result=results,
            confidence=results['quality_score'],
            explanation=explanation,
            attribution=["Image analysis model"],
            errors=[]
        )
    
    def validate_input(self, input_data: Any) -> bool:
        """Validate image input"""
        return isinstance(input_data, dict) and 'images' in input_data
