"""
Survey Ingestion Preprocessing Module

Description:
Collects and validates roommate preference surveys from students. Extracts hard 
constraints (binary requirements), soft preferences (weighted factors), and personality 
traits. Enforces Fair Housing Act compliance by blocking discriminatory preferences.
Not an agent - preprocessing pipeline for survey data.

Input Streams:
- Raw survey responses (JSON/form data)
- Student profile information
- Personality test scores (Big Five)

Output Streams:
- Structured roommate profiles
- Hard constraints (smoking, pets, quiet hours, budget)
- Soft preferences (cleanliness, social level, schedule)
- Personality scores (conscientiousness, agreeableness, etc.)
- FHA compliance status

Configuration:
See: config/preprocessing_config.py
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SurveyIngestion:
    """
    Preprocessing module for roommate survey collection and validation.
    
    This is NOT an agent - it's a preprocessing step that validates and 
    structures survey data before matching algorithms run.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize survey ingestion module.
        
        Args:
            config: Configuration with FHA protected classes and rules
        """
        self.config = config or {}
        self.fha_protected_classes = self.config.get('fha_protected_classes', [
            'race', 'color', 'national_origin', 'religion',
            'sex', 'familial_status', 'disability'
        ])
        logger.info("SurveyIngestion preprocessing module initialized")
    
    def process_survey(self, survey_data: Dict) -> Dict[str, Any]:
        """
        Process roommate preference survey.
        
        Input Stream:
            - survey_data: Raw survey responses with preferences and personality data
        
        Output Stream:
            - Dict with profile, hard_constraints, soft_preferences, 
              personality_scores, fha_compliant flag, violations list
        
        Args:
            survey_data: Dictionary containing survey responses
            
        Returns:
            Dictionary containing:
                - profile: Basic student info (student_id, name, contact)
                - hard_constraints: Binary requirements
                - soft_preferences: Weighted preferences
                - personality_scores: Big Five trait scores
                - fha_compliant: Boolean compliance status
                - violations: List of any FHA violations found
        """
        student_id = survey_data.get('student_id')
        logger.info(f"Processing survey for student {student_id}")
        
        # Extract profile information
        profile = {
            'student_id': student_id,
            'name': survey_data.get('name'),
            'email': survey_data.get('email'),
            'phone': survey_data.get('phone'),
            'timestamp': datetime.now().isoformat()
        }
        
        # Extract hard constraints (binary requirements)
        hard_constraints = self._extract_hard_constraints(survey_data)
        
        # Extract soft preferences (weighted factors)
        soft_preferences = self._extract_soft_preferences(survey_data)
        
        # Extract personality scores
        personality_scores = self._extract_personality(survey_data)
        
        # Check FHA compliance
        fha_compliant, violations = self._check_fha_compliance(survey_data)
        
        if not fha_compliant:
            logger.warning(f"FHA violations found in survey for {student_id}: {violations}")
        
        return {
            'profile': profile,
            'hard_constraints': hard_constraints,
            'soft_preferences': soft_preferences,
            'personality_scores': personality_scores,
            'fha_compliant': fha_compliant,
            'violations': violations,
            'processed_timestamp': datetime.now().isoformat()
        }
    
    def _extract_hard_constraints(self, survey_data: Dict) -> Dict[str, Any]:
        """
        Extract binary requirements (must match).
        
        Hard constraints are non-negotiable requirements:
        - smoking: yes/no
        - pets: yes/no/no_preference
        - has_pets: boolean (do they currently have pets)
        - allows_pets: boolean (would they accept a roommate with pets)
        - quiet_hours: tuple (start_hour, end_hour) for quiet time
        - budget_range: tuple (min, max) budget range
        """
        # Convert quiet_hours from boolean to tuple format
        quiet_hours_bool = survey_data.get('quiet_hours', False)
        if isinstance(quiet_hours_bool, bool):
            quiet_hours = (22, 7) if quiet_hours_bool else (23, 8)  # Default ranges
        else:
            quiet_hours = quiet_hours_bool  # Already a tuple
        
        # Handle pets - convert to has_pets and allows_pets
        pets = survey_data.get('pets', 'no_preference')
        if pets == 'yes':
            has_pets = True
            allows_pets = True
        elif pets == 'no':
            has_pets = False
            allows_pets = True  # Doesn't have but okay with roommate having
        else:  # no_preference
            has_pets = False
            allows_pets = True
        
        # Convert smoking from yes/no to boolean
        smoking_str = survey_data.get('smoking', 'no')
        smoking = (smoking_str == 'yes')
        
        return {
            'smoking': smoking,
            'has_pets': has_pets,
            'allows_pets': allows_pets,
            'quiet_hours': quiet_hours,
            'budget_range': (
                float(survey_data.get('budget_min', 0)),
                float(survey_data.get('budget_max', 2000))
            )
        }
    
    def _extract_soft_preferences(self, survey_data: Dict) -> Dict[str, float]:
        """
        Extract weighted preferences (nice to match, but flexible).
        
        Soft preferences are scored on 0-1 scale:
        - cleanliness: 0 (messy) to 1 (very clean)
        - social_level: 0 (introverted) to 1 (extroverted)
        - schedule: 0 (night owl) to 1 (early bird)
        """
        return {
            'cleanliness': self._normalize_score(survey_data.get('cleanliness', 5), 1, 10),
            'social_level': self._normalize_score(survey_data.get('social_level', 5), 1, 10),
            'schedule': self._normalize_score(survey_data.get('schedule', 5), 1, 10)
        }
    
    def _extract_personality(self, survey_data: Dict) -> Dict[str, float]:
        """
        Extract Big Five personality trait scores.
        
        Big Five traits (0-1 scale):
        - conscientiousness: organized, responsible
        - agreeableness: cooperative, compassionate
        - extraversion: outgoing, energetic
        - openness: creative, curious
        - neuroticism: anxious, moody
        """
        personality = survey_data.get('personality', {})
        
        return {
            'conscientiousness': float(personality.get('conscientiousness', 0.5)),
            'agreeableness': float(personality.get('agreeableness', 0.5)),
            'extraversion': float(personality.get('extraversion', 0.5)),
            'openness': float(personality.get('openness', 0.5)),
            'neuroticism': float(personality.get('neuroticism', 0.5))
        }
    
    def _check_fha_compliance(self, survey_data: Dict) -> tuple[bool, List[str]]:
        """
        Check survey for Fair Housing Act violations.
        
        Blocks discriminatory preferences based on protected classes:
        - race, color, national origin
        - religion
        - sex/gender
        - familial status (children)
        - disability
        
        Returns:
            (compliant: bool, violations: List[str])
        """
        violations = []
        
        # Check for prohibited preference fields
        for protected_class in self.fha_protected_classes:
            if protected_class in survey_data:
                violations.append(f"Discriminatory preference based on {protected_class}")
        
        # Check free-text fields for discriminatory language
        text_fields = ['additional_preferences', 'notes', 'description']
        prohibited_keywords = [
            'race', 'ethnic', 'religion', 'christian', 'muslim', 'jewish',
            'male only', 'female only', 'gender', 'children', 'kids',
            'disabled', 'disability', 'handicap'
        ]
        
        for field in text_fields:
            text = str(survey_data.get(field, '')).lower()
            for keyword in prohibited_keywords:
                if keyword in text:
                    violations.append(f"Discriminatory language '{keyword}' in {field}")
        
        compliant = len(violations) == 0
        
        return compliant, violations
    
    def _normalize_score(self, value: float, min_val: float, max_val: float) -> float:
        """Normalize score to 0-1 range"""
        if max_val == min_val:
            return 0.5
        return (value - min_val) / (max_val - min_val)
    
    def batch_process_surveys(self, surveys: List[Dict]) -> Dict[str, Any]:
        """
        Process multiple surveys in batch.
        
        Input Stream:
            - surveys: List of raw survey dictionaries
        
        Output Stream:
            - Dict with processed_profiles, compliant_count, violation_summary
        
        Args:
            surveys: List of survey data dictionaries
            
        Returns:
            Dictionary with batch processing results and statistics
        """
        logger.info(f"Batch processing {len(surveys)} surveys")
        
        processed_profiles = []
        compliant_count = 0
        violation_summary = {}
        
        for survey in surveys:
            result = self.process_survey(survey)
            processed_profiles.append(result)
            
            if result['fha_compliant']:
                compliant_count += 1
            
            # Aggregate violations
            for violation in result['violations']:
                violation_summary[violation] = violation_summary.get(violation, 0) + 1
        
        return {
            'processed_profiles': processed_profiles,
            'total_processed': len(surveys),
            'compliant_count': compliant_count,
            'violation_count': len(surveys) - compliant_count,
            'compliance_rate': compliant_count / len(surveys) if surveys else 0,
            'violation_summary': violation_summary,
            'batch_timestamp': datetime.now().isoformat()
        }
