"""
Main entry point for RentConnect-C3AN Agent System
Example usage and API endpoints
"""

import logging
import logging.config
from datetime import datetime
import uuid

from src.agents.orchestration.orchestration_agent import OrchestrationAgent
from src.agents.base_agent import AgentContext
from config import AGENT_CONFIG, LOGGING_CONFIG, CAMPUS_CONFIG

# Setup logging
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)


def create_context(user_id: str = None, metadata: dict = None) -> AgentContext:
    """Helper to create agent context"""
    return AgentContext(
        session_id=str(uuid.uuid4()),
        user_id=user_id or "anonymous",
        timestamp=datetime.utcnow(),
        metadata=metadata or {}
    )


def example_property_search():
    """Example: Property Search & Ranking Workflow"""
    logger.info("=== Property Search Example ===")
    
    # Initialize orchestrator
    orchestrator = OrchestrationAgent(config=AGENT_CONFIG)
    
    # Create context
    context = create_context(
        user_id="student123",
        metadata={
            'desired_amenities': ['parking', 'ac', 'laundry', 'wifi'],
            'student_verified': True
        }
    )
    
    # Run property search
    result = orchestrator.process(
        {
            'workflow': 'property_search',
            'workflow_input': {
                'data_sources': ['zillow_zori', 'columbia_gis'],
                'filters': {
                    'city': 'Columbia',
                    'state': 'SC',
                    'near_location': CAMPUS_CONFIG['main_campus_location']
                },
                'preferences': {
                    'weights': {
                        'price': 0.35,
                        'commute_time': 0.30,
                        'safety_score': 0.20,
                        'amenities_match': 0.15
                    }
                },
                'constraints': {
                    'max_budget': 1000,
                    'min_bedrooms': 1,
                    'max_commute_minutes': 30,
                    'required_amenities': ['ac']
                }
            },
            'human_review': True
        },
        context
    )
    
    if result.result:
        logger.info(f"✓ Search complete: {result.explanation}")
        logger.info(f"  - Total found: {result.result['total_found']}")
        logger.info(f"  - Total ranked: {result.result['total_ranked']}")
        
        # Show top 3
        for listing in result.result['ranked_listings'][:3]:
            logger.info(f"  #{listing['rank']}: Score {listing['overall_score']:.2f}")
            logger.info(f"    {listing.get('explanation', '')[:100]}...")
    else:
        logger.error(f"✗ Search failed: {result.errors}")


def example_roommate_matching():
    """Example: Roommate Matching Workflow"""
    logger.info("=== Roommate Matching Example ===")
    
    orchestrator = OrchestrationAgent(config=AGENT_CONFIG)
    context = create_context(user_id="matching_service")
    
    # Sample profiles
    profiles = [
        {
            'user_id': 'alice',
            'hard_constraints': {
                'no_smoking': True,
                'pet_policy': 'no_pets',
                'quiet_hours': True
            },
            'soft_preferences': {
                'cleanliness': 8,
                'social_level': 5,
                'schedule_match': 'morning_person'
            },
            'personality': {
                'openness': 0.7,
                'conscientiousness': 0.8,
                'extraversion': 0.4,
                'agreeableness': 0.8,
                'neuroticism': 0.3
            },
            'budget_range': (600, 900)
        },
        {
            'user_id': 'bob',
            'hard_constraints': {
                'no_smoking': True,
                'pet_policy': 'no_pets',
                'quiet_hours': True
            },
            'soft_preferences': {
                'cleanliness': 7,
                'social_level': 6,
                'schedule_match': 'morning_person'
            },
            'personality': {
                'openness': 0.6,
                'conscientiousness': 0.7,
                'extraversion': 0.5,
                'agreeableness': 0.7,
                'neuroticism': 0.4
            },
            'budget_range': (650, 950)
        },
        {
            'user_id': 'charlie',
            'hard_constraints': {
                'no_smoking': False,
                'pet_policy': 'cats_ok',
                'quiet_hours': False
            },
            'soft_preferences': {
                'cleanliness': 5,
                'social_level': 8,
                'schedule_match': 'night_owl'
            },
            'personality': {
                'openness': 0.8,
                'conscientiousness': 0.5,
                'extraversion': 0.8,
                'agreeableness': 0.6,
                'neuroticism': 0.5
            },
            'budget_range': (500, 800)
        }
    ]
    
    result = orchestrator.process(
        {
            'workflow': 'roommate_matching',
            'workflow_input': {
                'profiles': profiles,
                'match_type': 'one_to_one'
            },
            'human_review': False
        },
        context
    )
    
    if result.result:
        logger.info(f"✓ Matching complete: {result.explanation}")
        matches = result.result['matches']
        
        for match in matches:
            users = match.get('users', [])
            score = match.get('compatibility_score', 0)
            logger.info(f"  Match: {' & '.join(users)} - Score: {score:.2f}")
            logger.info(f"    Shared: {', '.join(match.get('shared_constraints', []))}")
    else:
        logger.error(f"✗ Matching failed: {result.errors}")


def example_tour_planning():
    """Example: Tour Planning Workflow"""
    logger.info("=== Tour Planning Example ===")
    
    orchestrator = OrchestrationAgent(config=AGENT_CONFIG)
    context = create_context(user_id="student456")
    
    # Sample class schedule
    base_date = datetime(2025, 10, 20)
    class_schedule = [
        {
            'name': 'CSCI 101',
            'start_time': base_date.replace(hour=9, minute=30),
            'end_time': base_date.replace(hour=10, minute=45)
        },
        {
            'name': 'MATH 141',
            'start_time': base_date.replace(hour=13, minute=0),
            'end_time': base_date.replace(hour=14, minute=15)
        }
    ]
    
    # Sample properties to visit
    properties = [
        {
            'listing_id': 'prop1',
            'address': '123 Main St',
            'lat': 33.995,
            'lon': -81.030
        },
        {
            'listing_id': 'prop2',
            'address': '456 College Ave',
            'lat': 33.991,
            'lon': -81.025
        },
        {
            'listing_id': 'prop3',
            'address': '789 University Way',
            'lat': 33.998,
            'lon': -81.028
        }
    ]
    
    result = orchestrator.process(
        {
            'workflow': 'tour_planning',
            'workflow_input': {
                'properties': properties,
                'class_schedule': class_schedule,
                'tour_date': base_date,
                'start_location': CAMPUS_CONFIG['main_campus_location']
            },
            'human_review': False
        },
        context
    )
    
    if result.result:
        logger.info(f"✓ Tour planned: {result.explanation}")
        route = result.result['route']
        
        for stop in route:
            prop = stop['property']
            arrival = stop.get('arrival_time', 'TBD')
            logger.info(f"  → {prop.get('address')} at {arrival}")
    else:
        logger.error(f"✗ Tour planning failed: {result.errors}")


def main():
    """Run all examples"""
    logger.info("Starting RentConnect-C3AN Agent System Examples")
    logger.info("=" * 60)
    
    try:
        # Run examples
        example_property_search()
        print("\n")
        
        example_roommate_matching()
        print("\n")
        
        example_tour_planning()
        print("\n")
        
        logger.info("=" * 60)
        logger.info("All examples completed successfully!")
        
    except Exception as e:
        logger.error(f"Error running examples: {e}", exc_info=True)


if __name__ == "__main__":
    main()
