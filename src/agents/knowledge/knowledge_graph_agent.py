"""
Knowledge Graph Agent
Stores and manages symbolic knowledge: Fair Housing rules, campus zones, 
transit data, landlord policies, lease constraints.
Implements C3AN: Reasoning, Grounding, Explainability
"""

from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import json
from ..base_agent import BaseAgent, AgentContext, AgentOutput


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
    """Types of relationships in the knowledge graph"""
    OWNS = "owns"
    HAS_AMENITY = "has_amenity"
    NEAR_TRANSIT = "near_transit"
    NEAR_CAMPUS = "near_campus"
    HAS_SAFETY_EVENT = "has_safety_event"
    SUBJECT_TO_RULE = "subject_to_rule"
    REQUIRES_COSIGNER = "requires_cosigner"
    ALLOWS_PETS = "allows_pets"
    HAS_LEASE_TERM = "has_lease_term"


@dataclass
class Entity:
    """Knowledge graph entity"""
    id: str
    entity_type: EntityType
    properties: Dict[str, Any]
    
    
@dataclass
class Relation:
    """Knowledge graph relation"""
    source_id: str
    relation_type: RelationType
    target_id: str
    properties: Dict[str, Any]


class KnowledgeGraphAgent(BaseAgent):
    """
    Manages structured world knowledge as a graph.
    Enables symbolic reasoning, rule enforcement, and explainable queries.
    C3AN: Reasoning, Grounding, Explainability, Interpretability
    """
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__("KnowledgeGraphAgent", config)
        self.entities: Dict[str, Entity] = {}
        self.relations: List[Relation] = []
        self.policy_rules: Dict[str, Dict] = {}
        self._initialize_knowledge_base()
        
    def _initialize_knowledge_base(self):
        """Initialize core knowledge: Fair Housing rules, campus zones, etc."""
        
        # Fair Housing Act rules
        self._add_policy_rules()
        
        # Campus zones (USC Columbia)
        self._add_campus_zones()
        
        # Lease term taxonomies
        self._add_lease_taxonomies()
        
    def _add_policy_rules(self):
        """Add Fair Housing Act and compliance rules"""
        
        self.policy_rules = {
            'fha_protected_classes': {
                'rule_id': 'FHA_001',
                'description': 'Fair Housing Act protected classes',
                'protected_attributes': [
                    'race', 'color', 'national_origin', 'religion',
                    'sex', 'familial_status', 'disability'
                ],
                'enforcement': 'blocking',  # Block violations
                'source': 'Fair Housing Act (42 U.S.C. § 3601-3619)'
            },
            'fha_advertising': {
                'rule_id': 'FHA_002',
                'description': 'Fair Housing advertising requirements',
                'prohibited_language': [
                    'adults only', 'no children', 'Christian home',
                    'perfect for singles', 'gender-specific pronouns in ads'
                ],
                'enforcement': 'warning',
                'source': 'Fair Housing Act § 3604(c)'
            },
            'lease_disclosure_sc': {
                'rule_id': 'SC_LEASE_001',
                'description': 'South Carolina lease disclosure requirements',
                'required_disclosures': [
                    'security_deposit_terms', 'late_fee_policy',
                    'maintenance_responsibilities', 'entry_notice_period'
                ],
                'enforcement': 'validation',
                'source': 'SC Code § 27-40-410'
            },
            'student_lease_terms': {
                'rule_id': 'CAMPUS_001',
                'description': 'Typical student lease constraints',
                'common_terms': {
                    'lease_duration': ['9-month', '12-month', 'semester'],
                    'cosigner_requirements': 'often_required',
                    'utilities_included': ['varies'],
                    'parking_availability': 'property_specific'
                },
                'enforcement': 'informational'
            }
        }
        
        # Add rules as entities
        for rule_id, rule_data in self.policy_rules.items():
            self.add_entity(
                entity_id=rule_id,
                entity_type=EntityType.POLICY_RULE,
                properties=rule_data
            )
    
    def _add_campus_zones(self):
        """Add USC Columbia campus zones and buildings"""
        
        campus_buildings = [
            {
                'id': 'USC_MAIN_CAMPUS',
                'name': 'USC Main Campus',
                'lat': 33.9937,
                'lon': -81.0266,
                'type': 'campus_zone'
            },
            {
                'id': 'THOMAS_COOPER_LIBRARY',
                'name': 'Thomas Cooper Library',
                'lat': 33.9946,
                'lon': -81.0279,
                'type': 'building'
            },
            {
                'id': 'RUSSELL_HOUSE',
                'name': 'Russell House University Union',
                'lat': 33.9937,
                'lon': -81.0280,
                'type': 'building'
            }
        ]
        
        for building in campus_buildings:
            self.add_entity(
                entity_id=building['id'],
                entity_type=EntityType.CAMPUS_BUILDING,
                properties=building
            )
    
    def _add_lease_taxonomies(self):
        """Add lease term and amenity taxonomies"""
        
        amenity_taxonomy = [
            'AC', 'Heating', 'Parking', 'Laundry_In_Unit', 'Laundry_On_Site',
            'Dishwasher', 'Washer_Dryer', 'Furnished', 'Utilities_Included',
            'WiFi_Included', 'Pet_Friendly', 'Balcony', 'Pool', 'Gym', 'Storage'
        ]
        
        for amenity in amenity_taxonomy:
            self.add_entity(
                entity_id=f"AMENITY_{amenity.upper()}",
                entity_type=EntityType.AMENITY,
                properties={'name': amenity, 'category': 'amenity'}
            )
    
    def process(self, input_data: Any, context: AgentContext) -> AgentOutput:
        """
        Query or update the knowledge graph.
        
        Args:
            input_data: Dict with 'operation' (query/add/update), 'data', 'query_params'
            context: Shared agent context
            
        Returns:
            AgentOutput with query results or operation status
        """
        if not self.validate_input(input_data):
            return self.create_output(
                result=None,
                confidence=0.0,
                explanation="Invalid input",
                attribution=[],
                errors=["Input validation failed"]
            )
        
        operation = input_data.get('operation', 'query')
        
        if operation == 'query':
            return self._handle_query(input_data, context)
        elif operation == 'add':
            return self._handle_add(input_data, context)
        elif operation == 'update':
            return self._handle_update(input_data, context)
        elif operation == 'check_rule':
            return self._handle_rule_check(input_data, context)
        else:
            return self.create_output(
                result=None,
                confidence=0.0,
                explanation=f"Unknown operation: {operation}",
                attribution=[],
                errors=[f"Operation '{operation}' not supported"]
            )
    
    def validate_input(self, input_data: Any) -> bool:
        """Validate knowledge graph operation input"""
        return isinstance(input_data, dict) and 'operation' in input_data
    
    def add_entity(
        self,
        entity_id: str,
        entity_type: EntityType,
        properties: Dict[str, Any]
    ) -> bool:
        """Add an entity to the knowledge graph"""
        if entity_id in self.entities:
            self.logger.warning(f"Entity {entity_id} already exists")
            return False
        
        entity = Entity(
            id=entity_id,
            entity_type=entity_type,
            properties=properties
        )
        self.entities[entity_id] = entity
        return True
    
    def add_relation(
        self,
        source_id: str,
        relation_type: RelationType,
        target_id: str,
        properties: Optional[Dict] = None
    ) -> bool:
        """Add a relation between entities"""
        if source_id not in self.entities or target_id not in self.entities:
            self.logger.error(f"Cannot create relation: entity not found")
            return False
        
        relation = Relation(
            source_id=source_id,
            relation_type=relation_type,
            target_id=target_id,
            properties=properties or {}
        )
        self.relations.append(relation)
        return True
    
    def query_entities(
        self,
        entity_type: Optional[EntityType] = None,
        filters: Optional[Dict] = None
    ) -> List[Entity]:
        """Query entities with optional filters"""
        results = list(self.entities.values())
        
        if entity_type:
            results = [e for e in results if e.entity_type == entity_type]
        
        if filters:
            for key, value in filters.items():
                results = [
                    e for e in results
                    if key in e.properties and e.properties[key] == value
                ]
        
        return results
    
    def query_relations(
        self,
        source_id: Optional[str] = None,
        relation_type: Optional[RelationType] = None,
        target_id: Optional[str] = None
    ) -> List[Relation]:
        """Query relations with optional filters"""
        results = self.relations
        
        if source_id:
            results = [r for r in results if r.source_id == source_id]
        if relation_type:
            results = [r for r in results if r.relation_type == relation_type]
        if target_id:
            results = [r for r in results if r.target_id == target_id]
        
        return results
    
    def find_neighbors(
        self,
        entity_id: str,
        relation_type: Optional[RelationType] = None,
        max_hops: int = 1
    ) -> List[Entity]:
        """Find neighboring entities in the graph"""
        if entity_id not in self.entities:
            return []
        
        neighbors = set()
        current_level = {entity_id}
        
        for _ in range(max_hops):
            next_level = set()
            
            for entity in current_level:
                # Find outgoing relations
                outgoing = self.query_relations(source_id=entity, relation_type=relation_type)
                for rel in outgoing:
                    next_level.add(rel.target_id)
                    neighbors.add(rel.target_id)
                
                # Find incoming relations
                incoming = self.query_relations(target_id=entity, relation_type=relation_type)
                for rel in incoming:
                    next_level.add(rel.source_id)
                    neighbors.add(rel.source_id)
            
            current_level = next_level
        
        return [self.entities[eid] for eid in neighbors if eid in self.entities]
    
    def check_policy_compliance(
        self,
        data: Dict[str, Any],
        rule_ids: Optional[List[str]] = None
    ) -> Tuple[bool, List[str], List[str]]:
        """
        Check data against policy rules.
        Returns (is_compliant, violations, warnings)
        C3AN: Alignment, Safety, Compliance
        """
        violations = []
        warnings = []
        
        rules_to_check = rule_ids or list(self.policy_rules.keys())
        
        for rule_id in rules_to_check:
            if rule_id not in self.policy_rules:
                continue
            
            rule = self.policy_rules[rule_id]
            
            if rule_id == 'fha_protected_classes':
                # Check for protected attributes in filters/preferences
                protected = rule['protected_attributes']
                for attr in protected:
                    if attr in data or f"{attr}_preference" in data:
                        violations.append(
                            f"Fair Housing violation: Cannot filter by {attr}"
                        )
            
            elif rule_id == 'fha_advertising':
                # Check listing descriptions for prohibited language
                text = data.get('description', '').lower()
                for phrase in rule['prohibited_language']:
                    if phrase.lower() in text:
                        warnings.append(
                            f"Advertising concern: '{phrase}' may violate Fair Housing"
                        )
        
        is_compliant = len(violations) == 0
        return is_compliant, violations, warnings
    
    def get_explanation_for_rule(self, rule_id: str) -> str:
        """
        Get human-readable explanation for a policy rule.
        C3AN: Explainability, Interpretability
        """
        if rule_id not in self.policy_rules:
            return f"Unknown rule: {rule_id}"
        
        rule = self.policy_rules[rule_id]
        return f"{rule['description']} (Source: {rule['source']})"
    
    def _handle_query(self, input_data: Dict, context: AgentContext) -> AgentOutput:
        """Handle query operation"""
        query_type = input_data.get('query_type', 'entities')
        params = input_data.get('query_params', {})
        
        if query_type == 'entities':
            entity_type_str = params.get('entity_type')
            entity_type = EntityType(entity_type_str) if entity_type_str else None
            filters = params.get('filters')
            
            results = self.query_entities(entity_type, filters)
            
            return self.create_output(
                result=[{'id': e.id, 'type': e.entity_type.value, 'properties': e.properties} 
                        for e in results],
                confidence=1.0,
                explanation=f"Found {len(results)} entities",
                attribution=["Knowledge Graph"],
                errors=[]
            )
        
        elif query_type == 'neighbors':
            entity_id = params.get('entity_id')
            relation_type_str = params.get('relation_type')
            relation_type = RelationType(relation_type_str) if relation_type_str else None
            max_hops = params.get('max_hops', 1)
            
            neighbors = self.find_neighbors(entity_id, relation_type, max_hops)
            
            return self.create_output(
                result=[{'id': e.id, 'type': e.entity_type.value, 'properties': e.properties}
                        for e in neighbors],
                confidence=1.0,
                explanation=f"Found {len(neighbors)} neighbors for {entity_id}",
                attribution=["Knowledge Graph"],
                errors=[]
            )
        
        else:
            return self.create_output(
                result=None,
                confidence=0.0,
                explanation=f"Unknown query type: {query_type}",
                attribution=[],
                errors=[f"Query type '{query_type}' not supported"]
            )
    
    def _handle_add(self, input_data: Dict, context: AgentContext) -> AgentOutput:
        """Handle add operation"""
        entity_data = input_data.get('data', {})
        
        success = self.add_entity(
            entity_id=entity_data['id'],
            entity_type=EntityType(entity_data['type']),
            properties=entity_data.get('properties', {})
        )
        
        if success:
            return self.create_output(
                result={'status': 'added', 'entity_id': entity_data['id']},
                confidence=1.0,
                explanation=f"Added entity {entity_data['id']}",
                attribution=["Knowledge Graph"],
                errors=[]
            )
        else:
            return self.create_output(
                result=None,
                confidence=0.0,
                explanation=f"Failed to add entity {entity_data['id']}",
                attribution=[],
                errors=["Entity already exists or invalid data"]
            )
    
    def _handle_update(self, input_data: Dict, context: AgentContext) -> AgentOutput:
        """Handle update operation"""
        entity_id = input_data.get('entity_id')
        updates = input_data.get('updates', {})
        
        if entity_id not in self.entities:
            return self.create_output(
                result=None,
                confidence=0.0,
                explanation=f"Entity {entity_id} not found",
                attribution=[],
                errors=["Entity not found"]
            )
        
        self.entities[entity_id].properties.update(updates)
        
        return self.create_output(
            result={'status': 'updated', 'entity_id': entity_id},
            confidence=1.0,
            explanation=f"Updated entity {entity_id}",
            attribution=["Knowledge Graph"],
            errors=[]
        )
    
    def _handle_rule_check(self, input_data: Dict, context: AgentContext) -> AgentOutput:
        """Handle policy rule compliance check"""
        data_to_check = input_data.get('data', {})
        rule_ids = input_data.get('rule_ids')
        
        is_compliant, violations, warnings = self.check_policy_compliance(
            data_to_check, rule_ids
        )
        
        explanation_parts = []
        if violations:
            explanation_parts.append(f"{len(violations)} violation(s)")
        if warnings:
            explanation_parts.append(f"{len(warnings)} warning(s)")
        if not violations and not warnings:
            explanation_parts.append("All checks passed")
        
        return self.create_output(
            result={
                'compliant': is_compliant,
                'violations': violations,
                'warnings': warnings
            },
            confidence=1.0 if is_compliant else 0.0,
            explanation=", ".join(explanation_parts),
            attribution=[self.policy_rules[rid]['source'] 
                        for rid in (rule_ids or self.policy_rules.keys())],
            errors=violations
        )
