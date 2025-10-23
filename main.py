"""
Main entry point for RentConnect-C3AN Agent System
Refactored Architecture: Preprocessing → Tools → Agents → Workflows

New Structure (No Orchestration Agent):
- Preprocessing: Data collection and cleaning
- Tools: Analysis and lookup utilities
- Agents: 4 decision-making agents
- Workflows: Direct agent coordination
"""

import logging
from datetime import datetime

# Import preprocessing modules
from src.preprocessing import DataIngestion, SurveyIngestion

# Import tools (singletons)
from src.tools import knowledge_graph, listing_analyzer, compliance_checker

# Import agents (singletons)
from src.agents import (
    roommate_matching,
    ranking_scoring,
    route_planning,
    feedback_learning
)

# Import configurations
from config import CAMPUS_CONFIG

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def example_property_search():
    """Example: Property Search & Ranking Workflow (Refactored)"""
    logger.info("=== Property Search Example ===")
    
    # Step 1: Collect data (Preprocessing)
    data_ingestion = DataIngestion()
    
    logger.info("Collecting rental listings...")
    result = data_ingestion.ingest_listings(
        sources=['zillow_zori', 'columbia_gis'],
        filters={
            'location': CAMPUS_CONFIG['main_campus_location'],
            'radius_km': 5.0,
            'price_max': 2000
        }
    )
    
    listings = result.get('records', [])
    logger.info(f"✓ Collected {len(listings)} listings")
    
    # Step 2: Analyze listings (Tools)
    logger.info("Analyzing listings for scams and compliance...")
    safe_listings = []
    
    for listing in listings[:10]:  # Limit to 10 for demo
        # Check for scams
        risk = listing_analyzer.analyze_listing(listing)
        
        if risk['risk_score'] < 0.7:  # Not high-risk
            # Check compliance
            compliance = compliance_checker.check_compliance(listing)
            
            if compliance['compliant']:
                listing['safety_score'] = compliance['safety_score']
                safe_listings.append(listing)
    
    logger.info(f"✓ {len(safe_listings)} safe, compliant listings")
    
    # Step 3: Rank properties (Agent Decision)
    logger.info("Ranking properties...")
    
    user_preferences = {
        'weights': {
            'price': 0.35,
            'commute_time': 0.30,
            'safety_score': 0.20,
            'amenities_match': 0.10,
            'lease_suitability': 0.05
        },
        'hard_constraints': {
            'max_price': 1500,
            'max_commute': 45,
            'min_safety': 0.6
        }
    }
    
    destination = (
        CAMPUS_CONFIG['main_campus_location']['lat'],
        CAMPUS_CONFIG['main_campus_location']['lon']
    )
    
    result = ranking_scoring.rank(safe_listings, user_preferences, destination)
    
    logger.info(f"✓ Ranked {len(result.ranked_listings)} properties")
    logger.info(f"✓ Pareto-optimal properties: {len(result.pareto_frontier)}")
    
    # Show top 3
    logger.info("\nTop 3 Properties:")
    for listing in result.ranked_listings[:3]:
        logger.info(f"  #{listing['rank']}: {listing['listing_id']}")
        logger.info(f"    Score: {listing['overall_score']:.2f}")
        logger.info(f"    Pareto optimal: {listing['is_pareto_optimal']}")
        if listing['listing_id'] in result.explanations:
            logger.info(f"    {result.explanations[listing['listing_id']][:100]}...")


def example_roommate_matching():
    """Example: Roommate Matching Workflow (Refactored)"""
    logger.info("=== Roommate Matching Example ===")
    
    # Step 1: Process surveys (Preprocessing)
    survey_ingestion = SurveyIngestion()
    
    # Sample survey data (matching SurveyIngestion.process_survey() expected format)
    surveys = [
        {
            'student_id': 'alice',
            'name': 'Alice Smith',
            'email': 'alice@email.com',
            'smoking': 'no',
            'pets': 'yes',
            'quiet_hours': True,
            'budget_min': 800,
            'budget_max': 1200,
            'cleanliness': 8,
            'social_level': 6,
            'schedule': 7,
            'conscientiousness': 4,
            'agreeableness': 4,
            'extraversion': 3,
            'openness': 4,
            'neuroticism': 2
        },
        {
            'student_id': 'bob',
            'name': 'Bob Jones',
            'email': 'bob@email.com',
            'smoking': 'no',
            'pets': 'yes',
            'quiet_hours': True,
            'budget_min': 900,
            'budget_max': 1300,
            'cleanliness': 8,
            'social_level': 6,
            'schedule': 6,
            'conscientiousness': 4,
            'agreeableness': 5,
            'extraversion': 4,
            'openness': 3,
            'neuroticism': 2
        },
        {
            'student_id': 'charlie',
            'name': 'Charlie Brown',
            'email': 'charlie@email.com',
            'smoking': 'yes',
            'pets': 'yes',
            'quiet_hours': False,
            'budget_min': 700,
            'budget_max': 1000,
            'cleanliness': 6,
            'social_level': 8,
            'schedule': 3,
            'conscientiousness': 3,
            'agreeableness': 4,
            'extraversion': 5,
            'openness': 5,
            'neuroticism': 3
        }
    ]
    
    logger.info("Processing roommate surveys...")
    processed_surveys = [survey_ingestion.process_survey(s) for s in surveys]
    logger.info(f"✓ Processed {len(processed_surveys)} profiles")
    
    # Transform to format expected by RoommateMatching agent
    profiles = []
    for survey in processed_surveys:
        profiles.append({
            'user_id': survey['profile']['student_id'],
            'hard_constraints': survey['hard_constraints'],
            'soft_preferences': survey['soft_preferences'],
            'personality': survey['personality_scores']
        })
    
    # Step 2: Match roommates (Agent Decision)
    logger.info("Matching roommates...")
    result = roommate_matching.match(profiles)
    
    logger.info(f"✓ Created {len(result.matches)} matches")
    logger.info(f"✓ Unmatched: {len(result.unmatched)} users")
    logger.info(f"✓ Blocking pairs: {result.blocking_pairs} (should be 0)")
    logger.info(f"✓ Match rate: {result.fairness_metrics['match_rate']:.1%}")
    logger.info(f"✓ Mean compatibility: {result.fairness_metrics['mean_compatibility']:.2f}")
    
    # Show matches
    logger.info("\nMatches:")
    for match in result.matches:
        logger.info(f"  Match {match['match_id']}:")
        logger.info(f"    Users: {', '.join(match['participants'])}")
        logger.info(f"    Compatibility: {match['compatibility_score']:.2f}")
        logger.info(f"    Shared: {match['shared_constraints']}")


def example_tour_planning():
    """Example: Tour Planning Workflow (Refactored)"""
    logger.info("=== Tour Planning Example ===")
    
    # Sample properties to visit (from previous ranking)
    properties_to_visit = [
        {'listing_id': 'prop1', 'latitude': 33.995, 'longitude': -81.030},
        {'listing_id': 'prop2', 'latitude': 33.991, 'longitude': -81.025},
        {'listing_id': 'prop3', 'latitude': 33.998, 'longitude': -81.028}
    ]
    
    # Sample class schedule
    class_schedule = [
        {'start': '09:00', 'end': '10:30'},  # Morning class
        {'start': '14:00', 'end': '15:30'}   # Afternoon class
    ]
    
    logger.info("Planning property viewing tour...")
    result = route_planning.plan_route(properties_to_visit, class_schedule)
    
    logger.info(f"✓ Tour feasible: {result.feasible}")
    logger.info(f"✓ Total stops: {len(result.stops)}")
    logger.info(f"✓ Total duration: {result.total_duration} minutes")
    logger.info(f"✓ Time window violations: {result.time_window_violations}")
    
    # Show route
    logger.info("\nTour Schedule:")
    for i, stop in enumerate(result.stops, 1):
        logger.info(f"  Stop {i}: {stop['listing_id']}")
        logger.info(f"    Arrival: {stop['arrival_time']}")
        logger.info(f"    Departure: {stop['departure_time']}")
        logger.info(f"    Viewing: {stop['viewing_duration']} min")


def example_feedback_learning():
    """Example: Feedback & Learning (Refactored)"""
    logger.info("=== Feedback & Learning Example ===")
    
    # Example 1: User rates a recommendation
    logger.info("Processing user rating feedback...")
    
    rating_feedback = {
        'feedback_id': 'fb1',
        'type': 'rating',
        'user_id': 'alice',
        'rating': 5,
        'context': {
            'listing_id': 'prop1',
            'criteria_scores': {
                'price': 0.9,
                'commute_time': 0.8,
                'safety_score': 0.85,
                'amenities_match': 0.7,
                'lease_suitability': 0.8
            }
        }
    }
    
    result = feedback_learning.process_feedback(rating_feedback)
    logger.info(f"✓ Feedback applied: {result.applied}")
    logger.info(f"✓ Impact: {result.impact_summary}")
    logger.info(f"✓ Drift detected: {result.drift_detected}")
    
    # Example 2: Expert correction
    logger.info("\nProcessing expert correction...")
    
    correction_feedback = {
        'feedback_id': 'fb2',
        'type': 'correction',
        'target': 'scam_detector',
        'listing_id': 'prop2',
        'corrected_risk_score': 0.95,
        'expert_confidence': 0.90
    }
    
    result = feedback_learning.process_feedback(correction_feedback)
    logger.info(f"✓ Correction applied: {result.applied}")
    logger.info(f"✓ Impact: {result.impact_summary}")
    
    # Show updated preferences
    updated_prefs = feedback_learning.get_user_preferences('alice')
    logger.info(f"\nUpdated preferences for alice:")
    logger.info(f"  Weights: {updated_prefs['weights']}")


def main():
    """Run all workflow examples"""
    logger.info("=" * 70)
    logger.info("RentConnect-C3AN Agent System - Refactored Architecture")
    logger.info("4 Agents + Preprocessing + Tools (No Orchestration)")
    logger.info("=" * 70)
    logger.info("")
    
    try:
        # Run workflow examples
        example_property_search()
        print("\n")
        
        example_roommate_matching()
        print("\n")
        
        example_tour_planning()
        print("\n")
        
        example_feedback_learning()
        print("\n")
        
        logger.info("=" * 70)
        logger.info("✅ All workflow examples completed successfully!")
        logger.info("=" * 70)
        
    except Exception as e:
        logger.error(f"❌ Error running examples: {e}", exc_info=True)


if __name__ == "__main__":
    main()
