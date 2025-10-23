"""
Compliance Checker Tool

Description:
Checks listings and advertisements against Fair Housing Act regulations and
SC lease disclosure requirements. Performs rule-based pattern matching to
detect discriminatory language and missing required disclosures.

Input Streams:
- Listing data (title, description, requirements, policies)
- Check types (fha, lease_disclosure, safety)
- Landlord information

Output Streams:
- Compliant flag (boolean)
- Violations list (with rule citations)
- Warnings list (non-blocking issues)
- Safety score (0-1)

Configuration:
See: config/tools_config.py
"""

from typing import Dict, List, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class ComplianceCheckerTool:
    """
    Tool for compliance checking against housing regulations.
    
    This is a TOOL (not an agent) - provides compliance verification
    functions that agents can use when evaluating listings.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize compliance checker tool.
        
        Args:
            config: Configuration with FHA rules and prohibited language
        """
        self.config = config or {}
        
        # Fair Housing Act prohibited language
        self.fha_prohibited = self.config.get('fha_prohibited_language', [
            'adults only', 'no children', 'christian home', 'muslim home', 'jewish home',
            'male only', 'female only', 'no section 8', 'perfect for singles',
            'no disabled', 'able-bodied only', 'mature tenants', 'no kids'
        ])
        
        # Protected classes under FHA
        self.protected_classes = self.config.get('fha_protected_classes', [
            'race', 'color', 'national_origin', 'religion',
            'sex', 'familial_status', 'disability'
        ])
        
        logger.info("Compliance checker tool initialized")
    
    def check_compliance(
        self,
        listing: Dict,
        check_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Check listing compliance against regulations.
        
        Input Stream:
            - listing: Listing data with title, description, requirements
            - check_types: List of checks to perform ['fha', 'safety', 'landlord']
        
        Output Stream:
            - Dict with compliant flag, violations, warnings, safety_score
        
        Args:
            listing: Listing data dictionary
            check_types: Types of checks to perform (default: all)
            
        Returns:
            Compliance check results
        """
        check_types = check_types or ['fha', 'safety', 'landlord']
        listing_id = listing.get('listing_id', 'unknown')
        
        logger.debug(f"Checking compliance for listing {listing_id}")
        
        results = {
            'listing_id': listing_id,
            'compliant': True,
            'violations': [],
            'warnings': [],
            'safety_score': 0.5,
            'checks_performed': check_types
        }
        
        # Fair Housing Act checks
        if 'fha' in check_types:
            fha_violations = self._check_fha_compliance(listing)
            results['violations'].extend(fha_violations)
            if fha_violations:
                results['compliant'] = False
        
        # Safety checks
        if 'safety' in check_types:
            safety_score, safety_warnings = self._check_safety(listing)
            results['safety_score'] = safety_score
            results['warnings'].extend(safety_warnings)
        
        # Landlord verification
        if 'landlord' in check_types:
            landlord_warnings = self._check_landlord(listing)
            results['warnings'].extend(landlord_warnings)
        
        # SC lease disclosure checks
        if 'lease_disclosure' in check_types:
            disclosure_violations = self._check_lease_disclosure(listing)
            results['violations'].extend(disclosure_violations)
            if disclosure_violations:
                results['compliant'] = False
        
        return results
    
    def _check_fha_compliance(self, listing: Dict) -> List[str]:
        """
        Check Fair Housing Act compliance.
        
        Detects discriminatory language based on protected classes:
        - Race, Color, National Origin
        - Religion
        - Sex/Gender
        - Familial Status (children)
        - Disability
        
        Returns:
            List of FHA violation descriptions
        """
        violations = []
        
        # Combine text fields
        text_fields = ['title', 'description', 'requirements', 'tenant_preferences']
        combined_text = ' '.join([
            str(listing.get(field, '')) for field in text_fields
        ]).lower()
        
        # Check for prohibited phrases
        for phrase in self.fha_prohibited:
            if phrase.lower() in combined_text:
                violations.append(
                    f"FHA violation: discriminatory language '{phrase}' "
                    f"(violates Fair Housing Act protected class requirements)"
                )
        
        # Check for explicit protected class mentions
        protected_keywords = {
            'race': ['white', 'black', 'asian', 'hispanic', 'latino', 'race'],
            'religion': ['christian', 'muslim', 'jewish', 'religious', 'church'],
            'familial_status': ['children', 'kids', 'family', 'adults only'],
            'sex': ['male only', 'female only', 'men only', 'women only'],
            'disability': ['disabled', 'handicap', 'wheelchair', 'able-bodied']
        }
        
        for protected_class, keywords in protected_keywords.items():
            for keyword in keywords:
                if keyword in combined_text and 'no' in combined_text:
                    violations.append(
                        f"FHA violation: possible discrimination based on {protected_class} "
                        f"(keyword: '{keyword}')"
                    )
        
        return violations
    
    def _check_safety(self, listing: Dict) -> Tuple[float, List[str]]:
        """
        Check safety features and location safety.
        
        Returns:
            (safety_score, warnings)
        """
        warnings = []
        score = 0.7  # Default moderate safety score
        
        # Check for security features (positive indicators)
        security_features = ['security_system', 'gated', 'doorman', 'cameras', 'alarm']
        features = listing.get('amenities', [])
        
        security_count = sum(1 for feature in security_features if feature in features)
        if security_count >= 2:
            score += 0.2
        elif security_count == 1:
            score += 0.1
        
        # Check description for safety concerns
        description = listing.get('description', '').lower()
        safety_concerns = ['high crime', 'unsafe', 'dangerous', 'caution']
        
        for concern in safety_concerns:
            if concern in description:
                warnings.append(f"Safety concern mentioned: '{concern}'")
                score -= 0.2
        
        # Check if building inspection/code compliance mentioned
        if 'inspected' in description or 'code compliant' in description:
            score += 0.05
        
        # Ensure score stays in 0-1 range
        score = max(0.0, min(1.0, score))
        
        return score, warnings
    
    def _check_landlord(self, listing: Dict) -> List[str]:
        """
        Check landlord verification and history.
        
        Returns:
            List of warnings about landlord
        """
        warnings = []
        
        landlord_id = listing.get('landlord_id')
        if not landlord_id:
            warnings.append("Landlord not identified")
        
        landlord_verified = listing.get('landlord_verified', False)
        if not landlord_verified:
            warnings.append("Landlord not verified in registry")
        
        # Check for negative reviews (if available)
        landlord_rating = listing.get('landlord_rating', 0)
        if landlord_rating > 0 and landlord_rating < 3.0:
            warnings.append(f"Low landlord rating: {landlord_rating}/5.0")
        
        return warnings
    
    def _check_lease_disclosure(self, listing: Dict) -> List[str]:
        """
        Check SC lease disclosure requirements.
        
        South Carolina requires landlords to disclose:
        - Lead paint (for pre-1978 buildings)
        - Mold issues
        - Property conditions
        
        Returns:
            List of disclosure violations
        """
        violations = []
        
        # Check for required disclosures
        required_disclosures = ['lead_paint_disclosure', 'mold_disclosure']
        year_built = listing.get('year_built', 2000)
        
        # Lead paint disclosure required for pre-1978 buildings
        if year_built < 1978 and not listing.get('lead_paint_disclosure'):
            violations.append(
                "Missing required lead paint disclosure (pre-1978 building)"
            )
        
        # Check if lease terms are clearly stated
        if not listing.get('lease_length'):
            violations.append("Lease length not specified")
        
        if not listing.get('security_deposit_amount'):
            violations.append("Security deposit amount not disclosed")
        
        return violations
    
    def batch_check(
        self,
        listings: List[Dict],
        check_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Check compliance for multiple listings in batch.
        
        Input Stream:
            - listings: List of listing dictionaries
            - check_types: Types of checks to perform
        
        Output Stream:
            - Dict with checked_listings, compliance_rate, violation_summary
        
        Args:
            listings: List of listing data dictionaries
            check_types: Types of checks to perform
            
        Returns:
            Batch compliance check results
        """
        logger.info(f"Batch checking compliance for {len(listings)} listings")
        
        checked_listings = []
        compliant_count = 0
        all_violations = []
        all_warnings = []
        
        for listing in listings:
            result = self.check_compliance(listing, check_types)
            checked_listings.append(result)
            
            if result['compliant']:
                compliant_count += 1
            
            all_violations.extend(result['violations'])
            all_warnings.extend(result['warnings'])
        
        # Aggregate violation types
        violation_types = {}
        for violation in all_violations:
            vtype = violation.split(':')[0] if ':' in violation else violation
            violation_types[vtype] = violation_types.get(vtype, 0) + 1
        
        return {
            'checked_listings': checked_listings,
            'total_checked': len(listings),
            'compliant_count': compliant_count,
            'violation_count': len(listings) - compliant_count,
            'compliance_rate': compliant_count / len(listings) if listings else 0,
            'violation_types': violation_types,
            'total_violations': len(all_violations),
            'total_warnings': len(all_warnings)
        }


# Singleton instance (tool pattern)
compliance_checker = ComplianceCheckerTool()
