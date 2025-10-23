"""
Knowledge Graph Tool

Description:
Stores and queries symbolic knowledge including Fair Housing Act rules, SC lease laws,
campus buildings/zones, amenity taxonomies, and transit routes. Provides fast lookups
for policy compliance checking and rule-based reasoning.

Input Streams:
- Query parameters (entity_type, filters, relation queries)
- New entities/relations to add
- Policy compliance checks

Output Streams:
- Query results (entities matching criteria)
- Compliance verdicts (compliant/non-compliant with rule citations)
- Rule explanations (why a rule applies)
- Graph traversal results (neighbors, paths)

Configuration:
See: config/tools_config.py
"""

from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class EntityType(Enum):
    """Types of entities in the knowledge graph"""
    PROPERTY = "property"
    LANDLORD = "landlord"
    AMENITY = "amenity"
    TRANSIT_STOP = "transit_stop"
    CAMPUS_BUILDING = "campus_building"
    SAFETY_EVENT = "safety_event"
    POLICY_RULE = "policy_rule"
    STUDENT = "student"
    LEASE_TERM = "lease_term"


class RelationType(Enum):
    """Types of relations between entities"""
    OWNS = "owns"
    HAS_AMENITY = "has_amenity"
    NEAR_TRANSIT = "near_transit"
    SUBJECT_TO_RULE = "subject_to_rule"
    VIOLATES_RULE = "violates_rule"
    LOCATED_IN = "located_in"
    CONNECTS_TO = "connects_to"


@dataclass
class Entity:
    """Knowledge graph entity"""
    entity_id: str
    entity_type: EntityType
    properties: Dict[str, Any]


@dataclass
class Relation:
    """Knowledge graph relation"""
    source_id: str
    relation_type: RelationType
    target_id: str
    properties: Optional[Dict[str, Any]] = None


class KnowledgeGraphTool:
    """
    Tool for symbolic knowledge storage and rule-based reasoning.
    
    This is a TOOL (not an agent) - provides knowledge lookup and 
    compliance checking functions for agents to use.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize knowledge graph tool.
        
        Args:
            config: Configuration with initial entities and rules
        """
        self.config = config or {}
        self.entities: Dict[str, Entity] = {}
        self.relations: List[Relation] = []
        
        # Load initial knowledge
        self._load_fha_rules()
        self._load_campus_zones()
        
        logger.info("Knowledge graph tool initialized")
    
    def query_entities(
        self,
        entity_type: Optional[EntityType] = None,
        filters: Optional[Dict] = None
    ) -> List[Entity]:
        """
        Query entities by type and filters.
        
        Input Stream:
            - entity_type: Optional filter by EntityType
            - filters: Dict with property filters
        
        Output Stream:
            - List of matching Entity objects
        
        Args:
            entity_type: Filter by entity type
            filters: Property filters (e.g., {'campus': 'USC', 'active': True})
            
        Returns:
            List of entities matching criteria
        """
        results = []
        filters = filters or {}
        
        for entity in self.entities.values():
            # Type filter
            if entity_type and entity.entity_type != entity_type:
                continue
            
            # Property filters
            match = True
            for key, value in filters.items():
                if entity.properties.get(key) != value:
                    match = False
                    break
            
            if match:
                results.append(entity)
        
        logger.debug(f"Query returned {len(results)} entities")
        return results
    
    def add_entity(self, entity: Entity) -> None:
        """Add entity to graph"""
        self.entities[entity.entity_id] = entity
        logger.debug(f"Added entity {entity.entity_id}")
    
    def add_relation(self, relation: Relation) -> None:
        """Add relation to graph"""
        self.relations.append(relation)
        logger.debug(f"Added relation {relation.relation_type} from {relation.source_id} to {relation.target_id}")
    
    def find_neighbors(
        self,
        entity_id: str,
        relation_type: Optional[RelationType] = None
    ) -> List[Entity]:
        """
        Find entities connected to given entity.
        
        Input Stream:
            - entity_id: Source entity ID
            - relation_type: Optional filter by RelationType
        
        Output Stream:
            - List of connected Entity objects
        
        Args:
            entity_id: Entity to find neighbors for
            relation_type: Optional filter by relation type
            
        Returns:
            List of neighboring entities
        """
        neighbor_ids = set()
        
        for relation in self.relations:
            if relation.source_id == entity_id:
                if relation_type is None or relation.relation_type == relation_type:
                    neighbor_ids.add(relation.target_id)
        
        neighbors = [self.entities[nid] for nid in neighbor_ids if nid in self.entities]
        return neighbors
    
    def check_policy_compliance(
        self,
        entity: Dict,
        policy_type: str
    ) -> Dict[str, Any]:
        """
        Check if entity complies with policy rules.
        
        Input Stream:
            - entity: Entity data to check (listing, advertisement, etc.)
            - policy_type: Type of policy ('fha', 'lease_disclosure', 'safety')
        
        Output Stream:
            - Dict with compliant (bool), violations (list), rules_checked (list)
        
        Args:
            entity: Entity data dictionary
            policy_type: Policy category to check
            
        Returns:
            Dictionary with compliance result and rule citations
        """
        violations = []
        rules_checked = []
        
        # Get relevant policy rules
        policy_rules = self.query_entities(
            entity_type=EntityType.POLICY_RULE,
            filters={'policy_type': policy_type}
        )
        
        for rule in policy_rules:
            rules_checked.append(rule.properties.get('rule_name'))
            
            # Check rule condition
            if self._check_rule_condition(entity, rule):
                violations.append({
                    'rule_name': rule.properties.get('rule_name'),
                    'rule_text': rule.properties.get('rule_text'),
                    'severity': rule.properties.get('severity', 'medium')
                })
        
        compliant = len(violations) == 0
        
        return {
            'compliant': compliant,
            'violations': violations,
            'rules_checked': rules_checked,
            'policy_type': policy_type
        }
    
    def get_rule_explanation(self, rule_name: str) -> Optional[str]:
        """
        Get explanation for a specific rule.
        
        Input Stream:
            - rule_name: Name/ID of the rule
        
        Output Stream:
            - String explanation or None
        
        Args:
            rule_name: Rule identifier
            
        Returns:
            Rule explanation text or None if not found
        """
        rules = self.query_entities(
            entity_type=EntityType.POLICY_RULE,
            filters={'rule_name': rule_name}
        )
        
        if rules:
            return rules[0].properties.get('explanation')
        return None
    
    def _check_rule_condition(self, entity: Dict, rule: Entity) -> bool:
        """Check if entity violates rule condition"""
        rule_props = rule.properties
        condition_type = rule_props.get('condition_type')
        
        if condition_type == 'contains_text':
            # Check if entity text contains prohibited keywords
            text_fields = ['title', 'description', 'requirements']
            prohibited_keywords = rule_props.get('prohibited_keywords', [])
            
            for field in text_fields:
                text = str(entity.get(field, '')).lower()
                for keyword in prohibited_keywords:
                    if keyword.lower() in text:
                        return True
        
        elif condition_type == 'missing_disclosure':
            # Check if required disclosure is present
            required_field = rule_props.get('required_field')
            if required_field and not entity.get(required_field):
                return True
        
        return False
    
    def _load_fha_rules(self):
        """Load Fair Housing Act rules"""
        fha_rules = [
            {
                'rule_name': 'FHA_NO_RACE_DISCRIMINATION',
                'rule_text': 'Advertisements cannot express preference based on race or color',
                'policy_type': 'fha',
                'condition_type': 'contains_text',
                'prohibited_keywords': ['white only', 'no minorities', 'caucasian preferred'],
                'severity': 'high',
                'explanation': 'Fair Housing Act prohibits discrimination based on race or color in housing advertisements'
            },
            {
                'rule_name': 'FHA_NO_RELIGION_DISCRIMINATION',
                'rule_text': 'Advertisements cannot express preference based on religion',
                'policy_type': 'fha',
                'condition_type': 'contains_text',
                'prohibited_keywords': ['christian only', 'muslim only', 'jewish only', 'religious preference'],
                'severity': 'high',
                'explanation': 'Fair Housing Act prohibits discrimination based on religion in housing advertisements'
            },
            {
                'rule_name': 'FHA_NO_FAMILIAL_STATUS',
                'rule_text': 'Advertisements cannot discriminate based on familial status',
                'policy_type': 'fha',
                'condition_type': 'contains_text',
                'prohibited_keywords': ['adults only', 'no children', 'no kids', 'mature tenants'],
                'severity': 'high',
                'explanation': 'Fair Housing Act prohibits discrimination based on familial status (presence of children)'
            }
        ]
        
        for idx, rule_data in enumerate(fha_rules):
            entity = Entity(
                entity_id=f"fha_rule_{idx}",
                entity_type=EntityType.POLICY_RULE,
                properties=rule_data
            )
            self.add_entity(entity)
    
    def _load_campus_zones(self):
        """Load USC campus building/zone data"""
        campus_buildings = [
            {'name': 'Swearingen Engineering Center', 'lat': 33.9947, 'lon': -81.0291, 'type': 'academic'},
            {'name': 'Thomas Cooper Library', 'lat': 33.9952, 'lon': -81.0292, 'type': 'library'},
            {'name': 'Strom Thurmond Wellness Center', 'lat': 33.9980, 'lon': -81.0260, 'type': 'recreation'}
        ]
        
        for idx, building in enumerate(campus_buildings):
            entity = Entity(
                entity_id=f"campus_building_{idx}",
                entity_type=EntityType.CAMPUS_BUILDING,
                properties=building
            )
            self.add_entity(entity)


# Create singleton instance (tool pattern)
knowledge_graph = KnowledgeGraphTool()
