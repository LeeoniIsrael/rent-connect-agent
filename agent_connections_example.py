"""
Agent Connection Examples
Demonstrates how agents connect and pass data to each other
"""

import json
from system_implementation import (
    DataIngestionAgent,
    ListingAnalyzerAgent,
    ComplianceCheckerAgent,
    RankingScoringAgent,
    SurveyIngestionAgent,
    KnowledgeGraphAgent,
    RoommateMatchingAgent,
    RoutePlanningAgent
)


def example_1_data_pipeline():
    """
    Connection: Data Ingestion → Listing Analyzer → Compliance Checker → Ranking
    """
    print("\n" + "="*60)
    print("EXAMPLE 1: DATA ANALYSIS PIPELINE")
    print("="*60)
    
    # Step 1: Data Ingestion
    print("\n[1] Data Ingestion Agent")
    ingestion = DataIngestionAgent()
    ingestion_result = ingestion.process({
        "data_sources": ["zillow"],
        "filters": {"city": "Columbia", "max_price": 1500}
    })
    listings = ingestion_result.data["cleaned_listings"]
    print(f"    Output: {len(listings)} listings collected")
    
    # Step 2: Listing Analyzer (receives listings from step 1)
    print("\n[2] Listing Analyzer Agent")
    print(f"    Input: {len(listings)} listings from Data Ingestion")
    analyzer = ListingAnalyzerAgent()
    analysis_result = analyzer.process({
        "listing_data": listings  # ← DATA CONNECTION from step 1
    })
    analyzed = analysis_result.data["analyzed_listings"]
    print(f"    Output: {len(analyzed)} listings analyzed")
    
    # Step 3: Compliance Checker (receives original listings)
    print("\n[3] Compliance Checker Agent")
    print(f"    Input: {len(listings)} listings from Data Ingestion")
    compliance = ComplianceCheckerAgent()
    compliance_result = compliance.process({
        "listing_data": listings  # ← DATA CONNECTION from step 1
    })
    compliance_data = compliance_result.data["compliance_results"]
    print(f"    Output: {len(compliance_data)} compliance checks")
    
    # Step 4: Ranking (receives all previous data)
    print("\n[4] Ranking Scoring Agent")
    print(f"    Input: Listings + Analysis + Compliance data")
    ranking = RankingScoringAgent()
    ranking_result = ranking.process({
        "listings": listings,  # ← DATA CONNECTION from step 1
        "user_preferences": {"weights": {"price": 0.4, "commute": 0.3}}
    })
    ranked = ranking_result.data["ranked_listings"]
    print(f"    Output: {len(ranked)} properties ranked")
    
    print("\n✓ Pipeline complete: Data → Analysis → Compliance → Ranking")
    print(f"  Top property: {ranked[0]['listing_id']} (score: {ranked[0]['overall_score']})")


def example_2_roommate_pipeline():
    """
    Connection: Survey Ingestion → Knowledge Graph → Roommate Matching
    """
    print("\n" + "="*60)
    print("EXAMPLE 2: ROOMMATE MATCHING PIPELINE")
    print("="*60)
    
    # Step 1: Survey Ingestion (multiple users)
    print("\n[1] Survey Ingestion Agent")
    survey_agent = SurveyIngestionAgent()
    
    user_surveys = [
        {"user_id": "alice", "hard_constraints": {"smoking": False}},
        {"user_id": "bob", "hard_constraints": {"smoking": False}}
    ]
    
    profiles = []
    for survey in user_surveys:
        result = survey_agent.process({"survey_response": survey})
        profiles.append(result.data["validated_profile"])
    print(f"    Output: {len(profiles)} validated profiles")
    
    # Step 2: Knowledge Graph (get FHA rules)
    print("\n[2] Knowledge Graph Agent")
    kg = KnowledgeGraphAgent()
    kg_result = kg.process({
        "query_type": "rule",
        "filters": {"source": "FHA"}
    })
    rules = kg_result.data["query_results"]
    print(f"    Output: Retrieved {len(rules)} rule categories")
    
    # Step 3: Roommate Matching (receives profiles from step 1)
    print("\n[3] Roommate Matching Agent")
    print(f"    Input: {len(profiles)} profiles from Survey Ingestion")
    matcher = RoommateMatchingAgent()
    match_result = matcher.process({
        "user_profiles": profiles  # ← DATA CONNECTION from step 1
    })
    matches = match_result.data["matches"]
    print(f"    Output: {len(matches)} matches created")
    
    print("\n✓ Pipeline complete: Survey → Knowledge Graph → Matching")
    for match in matches:
        print(f"  Match: {match['participants'][0]} ↔ {match['participants'][1]} "
              f"(compatibility: {match['compatibility_score']})")


def example_3_tour_pipeline():
    """
    Connection: Ranking → Route Planning
    """
    print("\n" + "="*60)
    print("EXAMPLE 3: TOUR PLANNING PIPELINE")
    print("="*60)
    
    # Mock ranked properties
    mock_listings = [
        {"listing_id": "prop_A", "latitude": 33.99, "longitude": -81.03, "price": 1200},
        {"listing_id": "prop_B", "latitude": 34.00, "longitude": -81.02, "price": 1250},
        {"listing_id": "prop_C", "latitude": 34.01, "longitude": -81.01, "price": 1300}
    ]
    
    # Step 1: Ranking
    print("\n[1] Ranking Scoring Agent")
    ranking = RankingScoringAgent()
    ranking_result = ranking.process({
        "listings": mock_listings,
        "user_preferences": {"weights": {"price": 0.5}}
    })
    ranked = ranking_result.data["ranked_listings"]
    print(f"    Output: {len(ranked)} properties ranked")
    
    # Step 2: Route Planning (receives top N from ranking)
    print("\n[2] Route Planning Agent")
    top_properties = ranked[:3]  # Top 3
    print(f"    Input: Top {len(top_properties)} properties from Ranking")
    
    planner = RoutePlanningAgent()
    route_result = planner.process({
        "properties_to_visit": top_properties,  # ← DATA CONNECTION from step 1
        "class_schedule": []
    })
    route = route_result.data["optimized_route"]
    print(f"    Output: {len(route)} stops planned")
    
    print("\n✓ Pipeline complete: Ranking → Route Planning")
    for stop in route:
        print(f"  Stop: {stop['listing_id']} at {stop['arrival_time']}")


def example_4_data_flow_visualization():
    """
    Show complete data flow structure
    """
    print("\n" + "="*60)
    print("EXAMPLE 4: DATA FLOW VISUALIZATION")
    print("="*60)
    
    flows = {
        "Property Search Flow": [
            "data-ingestion-agent → listing-analyzer-agent",
            "data-ingestion-agent → compliance-checker-agent",
            "listing-analyzer-agent → ranking-scoring-agent",
            "compliance-checker-agent → ranking-scoring-agent"
        ],
        "Roommate Matching Flow": [
            "survey-ingestion-agent → roommate-matching-agent",
            "knowledge-graph-agent → roommate-matching-agent"
        ],
        "Tour Planning Flow": [
            "ranking-scoring-agent → route-planning-agent"
        ],
        "Feedback Loop": [
            "ranking-scoring-agent → feedback-learning-agent",
            "roommate-matching-agent → feedback-learning-agent",
            "route-planning-agent → feedback-learning-agent"
        ]
    }
    
    for flow_name, connections in flows.items():
        print(f"\n{flow_name}:")
        for conn in connections:
            print(f"  {conn}")


def show_agent_registry_info():
    """
    Display information from the agent registry
    """
    print("\n" + "="*60)
    print("AGENT REGISTRY INFORMATION")
    print("="*60)
    
    with open('rentconnect_agent_registry.json', 'r') as f:
        registry = json.load(f)
    
    print(f"\nRegistry Version: {registry['metadata']['version']}")
    print(f"Total Agents: {len(registry['agents'])}")
    print(f"Protocols: {', '.join(registry['global_protocols'])}")
    
    print("\nAgent Connections (based on input/output streams):")
    
    for agent in registry['agents']:
        outputs = agent.get('output_data_streams', {}).get('mandatory', [])
        if outputs:
            print(f"\n{agent['name']}:")
            print(f"  Outputs: {', '.join(outputs)}")
            
            # Find which agents consume these outputs
            consumers = []
            for other_agent in registry['agents']:
                inputs = other_agent.get('input_data_streams', {}).get('mandatory', []) + \
                        other_agent.get('input_data_streams', {}).get('optional', [])
                if any(output in inputs for output in outputs):
                    consumers.append(other_agent['name'])
            
            if consumers:
                print(f"  Consumed by: {', '.join(consumers)}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("RENTCONNECT AGENT CONNECTIONS EXAMPLES")
    print("="*60)
    
    # Run all examples
    example_1_data_pipeline()
    example_2_roommate_pipeline()
    example_3_tour_pipeline()
    example_4_data_flow_visualization()
    show_agent_registry_info()
    
    print("\n" + "="*60)
    print("ALL EXAMPLES COMPLETED")
    print("="*60 + "\n")
