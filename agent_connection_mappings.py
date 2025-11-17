"""
Agent Connection Mappings
Complete reference for how agents connect to each other
"""

AGENT_CONNECTIONS = {
    # Source agent -> Target agents (with data streams)
    
    "data-ingestion-agent": {
        "outputs": {
            "cleaned_listings": ["listing-analyzer-agent", "compliance-checker-agent", "ranking-scoring-agent"],
            "transit_data": ["route-planning-agent"]
        },
        "connections": [
            {
                "target": "listing-analyzer-agent",
                "data_stream": "cleaned_listings",
                "description": "Send raw listing data for scam detection and feature extraction"
            },
            {
                "target": "compliance-checker-agent",
                "data_stream": "cleaned_listings",
                "description": "Send listing data for FHA and safety compliance checks"
            },
            {
                "target": "ranking-scoring-agent",
                "data_stream": "cleaned_listings",
                "description": "Provide base listing data for ranking"
            }
        ]
    },
    
    "survey-ingestion-agent": {
        "outputs": {
            "validated_profile": ["roommate-matching-agent"]
        },
        "connections": [
            {
                "target": "roommate-matching-agent",
                "data_stream": "validated_profile",
                "description": "Send FHA-compliant user profiles for matching"
            }
        ]
    },
    
    "listing-analyzer-agent": {
        "outputs": {
            "risk_score": ["ranking-scoring-agent"],
            "extracted_features": ["ranking-scoring-agent"]
        },
        "connections": [
            {
                "target": "ranking-scoring-agent",
                "data_stream": "risk_score, extracted_features",
                "description": "Provide analyzed listing features and risk assessment"
            }
        ]
    },
    
    "image-analyzer-agent": {
        "outputs": {
            "quality_score": ["ranking-scoring-agent"]
        },
        "connections": [
            {
                "target": "ranking-scoring-agent",
                "data_stream": "quality_score",
                "description": "Provide image quality and authenticity metrics"
            }
        ]
    },
    
    "compliance-checker-agent": {
        "outputs": {
            "compliance_status": ["ranking-scoring-agent"],
            "safety_score": ["ranking-scoring-agent"]
        },
        "connections": [
            {
                "target": "ranking-scoring-agent",
                "data_stream": "compliance_status, safety_score",
                "description": "Provide compliance validation and safety metrics"
            }
        ]
    },
    
    "knowledge-graph-agent": {
        "outputs": {
            "query_results": ["roommate-matching-agent", "compliance-checker-agent"]
        },
        "connections": [
            {
                "target": "roommate-matching-agent",
                "data_stream": "query_results",
                "description": "Provide FHA rules for fair matching"
            },
            {
                "target": "compliance-checker-agent",
                "data_stream": "query_results",
                "description": "Provide legal requirements for compliance checks"
            }
        ]
    },
    
    "ranking-scoring-agent": {
        "outputs": {
            "ranked_listings": ["route-planning-agent"],
            "overall_scores": ["feedback-learning-agent"]
        },
        "connections": [
            {
                "target": "route-planning-agent",
                "data_stream": "ranked_listings",
                "description": "Send top-ranked properties for tour planning"
            },
            {
                "target": "feedback-learning-agent",
                "data_stream": "overall_scores",
                "description": "Send scoring results for preference learning"
            }
        ]
    },
    
    "roommate-matching-agent": {
        "outputs": {
            "matches": ["feedback-learning-agent"],
            "compatibility_scores": ["feedback-learning-agent"]
        },
        "connections": [
            {
                "target": "feedback-learning-agent",
                "data_stream": "matches, compatibility_scores",
                "description": "Send matching results for learning from user feedback"
            }
        ]
    },
    
    "route-planning-agent": {
        "outputs": {
            "optimized_route": ["feedback-learning-agent"],
            "feasibility_status": []
        },
        "connections": [
            {
                "target": "feedback-learning-agent",
                "data_stream": "optimized_route",
                "description": "Send route plans for learning tour preferences"
            }
        ]
    },
    
    "feedback-learning-agent": {
        "outputs": {
            "updated_preferences": ["ranking-scoring-agent", "roommate-matching-agent", "route-planning-agent"]
        },
        "connections": [
            {
                "target": "ranking-scoring-agent",
                "data_stream": "updated_preferences",
                "description": "Send learned preferences to improve ranking"
            },
            {
                "target": "roommate-matching-agent",
                "data_stream": "updated_preferences",
                "description": "Send learned preferences to improve matching"
            },
            {
                "target": "route-planning-agent",
                "data_stream": "updated_preferences",
                "description": "Send learned preferences to improve routing"
            }
        ]
    },
    
    "orchestration-agent": {
        "outputs": {
            "workflow_result": [],
            "execution_status": []
        },
        "connections": [
            {
                "target": "all-agents",
                "data_stream": "control_signals",
                "description": "Coordinates workflow execution across all agents"
            }
        ]
    }
}


WORKFLOW_PATHS = {
    "property_search": {
        "description": "Find and rank rental properties",
        "sequence": [
            "data-ingestion-agent",
            "listing-analyzer-agent",
            "image-analyzer-agent",
            "compliance-checker-agent",
            "ranking-scoring-agent"
        ],
        "parallel_stages": {
            "stage_2": ["listing-analyzer-agent", "image-analyzer-agent", "compliance-checker-agent"]
        },
        "data_flow": [
            "data-ingestion → listing-analyzer",
            "data-ingestion → compliance-checker",
            "listing-analyzer → ranking",
            "image-analyzer → ranking",
            "compliance-checker → ranking"
        ]
    },
    
    "roommate_matching": {
        "description": "Match compatible roommates",
        "sequence": [
            "survey-ingestion-agent",
            "knowledge-graph-agent",
            "roommate-matching-agent"
        ],
        "parallel_stages": {},
        "data_flow": [
            "survey-ingestion → roommate-matching",
            "knowledge-graph → roommate-matching"
        ]
    },
    
    "tour_planning": {
        "description": "Plan optimal property tour route",
        "sequence": [
            "ranking-scoring-agent",
            "route-planning-agent"
        ],
        "parallel_stages": {},
        "data_flow": [
            "ranking → route-planning"
        ]
    },
    
    "feedback_learning": {
        "description": "Learn from user interactions",
        "sequence": [
            "any-decision-agent",
            "feedback-learning-agent",
            "any-decision-agent"
        ],
        "parallel_stages": {},
        "data_flow": [
            "decision-agents → feedback-learning",
            "feedback-learning → decision-agents (updated preferences)"
        ],
        "is_loop": True
    }
}


DATA_STREAM_SCHEMAS = {
    "cleaned_listings": {
        "type": "array",
        "items": {
            "listing_id": "string",
            "price": "number",
            "bedrooms": "number",
            "latitude": "number",
            "longitude": "number",
            "address": "string",
            "description": "string",
            "amenities": "array"
        }
    },
    
    "validated_profile": {
        "type": "object",
        "fields": {
            "user_id": "string",
            "hard_constraints": "object",
            "soft_preferences": "object",
            "personality": "object",
            "compliance_status": "object"
        }
    },
    
    "risk_score": {
        "type": "number",
        "range": [0, 1],
        "description": "Scam risk probability"
    },
    
    "ranked_listings": {
        "type": "array",
        "items": {
            "listing_id": "string",
            "overall_score": "number",
            "rank": "number",
            "criteria_scores": "object"
        }
    },
    
    "matches": {
        "type": "array",
        "items": {
            "match_id": "string",
            "participants": "array",
            "compatibility_score": "number"
        }
    },
    
    "optimized_route": {
        "type": "array",
        "items": {
            "listing_id": "string",
            "arrival_time": "string",
            "viewing_duration": "number"
        }
    }
}


def print_connection_map():
    """Print visual connection map"""
    print("\n" + "="*80)
    print("AGENT CONNECTION MAP")
    print("="*80)
    
    for agent_id, details in AGENT_CONNECTIONS.items():
        print(f"\n{agent_id}:")
        for conn in details["connections"]:
            if conn["target"] != "all-agents":
                print(f"  → {conn['target']}")
                print(f"     Data: {conn['data_stream']}")
                print(f"     Purpose: {conn['description']}")


def print_workflow_paths():
    """Print workflow execution paths"""
    print("\n" + "="*80)
    print("WORKFLOW EXECUTION PATHS")
    print("="*80)
    
    for workflow_id, details in WORKFLOW_PATHS.items():
        print(f"\n{workflow_id.upper()}: {details['description']}")
        print(f"Sequence: {' → '.join(details['sequence'])}")
        print("Data Flow:")
        for flow in details["data_flow"]:
            print(f"  • {flow}")


def get_agent_inputs(agent_id):
    """Get all agents that send data to the specified agent"""
    inputs = []
    for source_agent, details in AGENT_CONNECTIONS.items():
        for conn in details["connections"]:
            if conn["target"] == agent_id or conn["target"] == "all-agents":
                inputs.append({
                    "source": source_agent,
                    "data_stream": conn["data_stream"],
                    "description": conn["description"]
                })
    return inputs


def get_agent_outputs(agent_id):
    """Get all agents that receive data from the specified agent"""
    if agent_id in AGENT_CONNECTIONS:
        return AGENT_CONNECTIONS[agent_id]["connections"]
    return []


def trace_data_path(start_agent, end_agent):
    """Find path between two agents"""
    visited = set()
    queue = [(start_agent, [start_agent])]
    
    while queue:
        current, path = queue.pop(0)
        
        if current == end_agent:
            return path
        
        if current in visited:
            continue
        
        visited.add(current)
        
        if current in AGENT_CONNECTIONS:
            for conn in AGENT_CONNECTIONS[current]["connections"]:
                if conn["target"] not in visited:
                    queue.append((conn["target"], path + [conn["target"]]))
    
    return None


if __name__ == "__main__":
    print_connection_map()
    print_workflow_paths()
    
    print("\n" + "="*80)
    print("EXAMPLE QUERIES")
    print("="*80)
    
    # Example 1: What feeds into ranking?
    print("\n1. What agents send data to ranking-scoring-agent?")
    inputs = get_agent_inputs("ranking-scoring-agent")
    for inp in inputs:
        print(f"   • {inp['source']} → {inp['data_stream']}")
    
    # Example 2: What does data ingestion feed?
    print("\n2. What agents receive data from data-ingestion-agent?")
    outputs = get_agent_outputs("data-ingestion-agent")
    for out in outputs:
        print(f"   • {out['target']} ← {out['data_stream']}")
    
    # Example 3: Path tracing
    print("\n3. Path from data-ingestion-agent to route-planning-agent:")
    path = trace_data_path("data-ingestion-agent", "route-planning-agent")
    if path:
        print(f"   {' → '.join(path)}")
    
    print("\n" + "="*80 + "\n")
