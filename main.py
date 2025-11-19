"""
Main entry point for RentConnect-C3AN Agent System
C³AN-Compliant: Registry-driven workflow execution

Architecture:
- Orchestrator: Reads rentconnect_agent_registry.json and routes data automatically
- No hardcoded routing logic - all workflows defined in registry
- Compact: ~50 lines vs 320+ lines of manual orchestration
"""

import logging
from orchestrator import Orchestrator
from config import CAMPUS_CONFIG

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize the registry-driven orchestrator
orchestrator = Orchestrator()


def example_property_search():
    """Example: Property Search & Ranking Workflow"""
    logger.info("=== Property Search Example ===")
    
    result = orchestrator.run_workflow("property_search", inputs={
        'sources': ['zillow_zori', 'columbia_gis'],
        'filters': {
            'location': CAMPUS_CONFIG['main_campus_location'],
            'radius_km': 5.0,
            'price_max': 2000
        },
        'preferences': {
            'weights': {
                'price': 0.35,
                'commute_time': 0.30,
                'safety_score': 0.20,
                'amenities_match': 0.10,
                'lease_suitability': 0.05
            }
        },
        'destination': (
            CAMPUS_CONFIG['main_campus_location']['lat'],
            CAMPUS_CONFIG['main_campus_location']['lon']
        )
    })
    
    # Display results
    listings = result['results'].get('ranked_listings', [])
    logger.info(f"✓ Ranked {len(listings)} properties")
    logger.info("\nTop 3 Properties:")
    for i, listing in enumerate(listings[:3], 1):
        logger.info(f"  #{i}: {listing.get('listing_id', 'N/A')}")
        logger.info(f"    Score: {listing.get('overall_score', 0):.2f}")
        logger.info(f"    Pareto optimal: {listing.get('is_pareto_optimal', False)}")


def example_roommate_matching():
    """Example: Roommate Matching Workflow"""
    logger.info("=== Roommate Matching Example ===")
    
    # Sample survey data
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
    
    result = orchestrator.run_workflow("roommate_matching", inputs={
        'surveys': surveys
    })
    
    matches = result['results'].get('matches', [])
    metrics = result['results'].get('fairness_metrics', {})
    
    logger.info(f"✓ Created {len(matches)} matches")
    logger.info(f"✓ Match rate: {metrics.get('match_rate', 0):.1%}")
    logger.info(f"✓ Mean compatibility: {metrics.get('mean_compatibility', 0):.2f}")
    
    logger.info("\nMatches:")
    for match in matches:
        logger.info(f"  Match {match['match_id']}:")
        logger.info(f"    Users: {', '.join(match['participants'])}")
        logger.info(f"    Compatibility: {match['compatibility_score']:.2f}")


def example_tour_planning():
    """Example: Tour Planning Workflow"""
    logger.info("=== Tour Planning Example ===")
    
    # Mock ranked listings
    properties = [
        {'listing_id': 'prop1', 'latitude': 33.995, 'longitude': -81.030, 'overall_score': 0.92},
        {'listing_id': 'prop2', 'latitude': 33.991, 'longitude': -81.025, 'overall_score': 0.88},
        {'listing_id': 'prop3', 'latitude': 33.998, 'longitude': -81.028, 'overall_score': 0.85}
    ]
    
    result = orchestrator.run_workflow("tour_planning", inputs={
        'ranked_listings': properties,
        'class_schedule': [
            {'start': '09:00', 'end': '10:30'},
            {'start': '14:00', 'end': '15:30'}
        ]
    })
    
    tour = result['results'].get('tour', [])
    feasible = result['results'].get('tour_feasible', False)
    
    logger.info(f"✓ Tour feasible: {feasible}")
    logger.info(f"✓ Total stops: {len(tour)}")
    
    logger.info("\nTour Schedule:")
    for i, stop in enumerate(tour, 1):
        logger.info(f"  Stop {i}: {stop['listing_id']}")
        logger.info(f"    Arrival: {stop['arrival_time']}")
        logger.info(f"    Viewing: {stop['viewing_duration']} min")


def example_feedback_learning():
    """Example: Feedback & Learning"""
    logger.info("=== Feedback & Learning Example ===")
    
    result = orchestrator.run_workflow("feedback_learning", inputs={
        'feedback': {
            'feedback_id': 'fb1',
            'type': 'rating',
            'user_id': 'alice',
            'rating': 5,
            'context': {
                'listing_id': 'prop1',
                'criteria_scores': {
                    'price': 0.9,
                    'commute_time': 0.8,
                    'safety_score': 0.85
                }
            }
        }
    })
    
    applied = result['results'].get('feedback_applied', False)
    prefs = result['results'].get('updated_preferences', {})
    
    logger.info(f"✓ Feedback applied: {applied}")
    logger.info(f"✓ Updated preferences: {prefs.get('weights', {})}")


def main():
    """Run all workflow examples"""
    logger.info("=" * 70)
    logger.info("RentConnect-C3AN Agent System - Registry-Driven Architecture")
    logger.info("Compact: ~50 lines vs 320+ (No hardcoded routing)")
    logger.info("=" * 70)
    logger.info("")
    
    try:
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
