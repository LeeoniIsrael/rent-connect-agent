"""
Tool Registry for RentConnect-C3AN System

Central registry for all tools (analyzers, validators, knowledge graphs) that
agents use to perform their functions. Tools are stateless services that provide
specific capabilities without autonomy.
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum


logger = logging.getLogger(__name__)


class ToolType(Enum):
    """Classification of tool types"""
    ANALYZER = "analyzer"          # Analyzes data (risk, features, quality)
    VALIDATOR = "validator"        # Validates compliance, safety
    KNOWLEDGE_BASE = "knowledge"   # Stores and queries knowledge
    INTEGRATOR = "integrator"      # Integrates with external services


class ToolCapability(Enum):
    """Specific capabilities tools provide"""
    SCAM_DETECTION = "scam_detection"
    FEATURE_EXTRACTION = "feature_extraction"
    IMAGE_ANALYSIS = "image_analysis"
    COMPLIANCE_CHECK = "compliance_check"
    SAFETY_SCORING = "safety_scoring"
    KNOWLEDGE_QUERY = "knowledge_query"
    RULE_REASONING = "rule_reasoning"
    VERIFICATION = "verification"


@dataclass
class ToolInputSchema:
    """Schema for tool inputs"""
    name: str
    type: str
    description: str
    required: bool = True
    validation_rules: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolOutputSchema:
    """Schema for tool outputs"""
    name: str
    type: str
    description: str
    structure: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolMetadata:
    """Complete metadata for a registered tool"""
    # Identity
    tool_id: str
    name: str
    description: str
    version: str
    
    # Classification
    tool_type: ToolType
    capabilities: List[ToolCapability]
    
    # Interface
    input_schemas: List[ToolInputSchema]
    output_schemas: List[ToolOutputSchema]
    
    # Implementation
    module_path: str
    class_name: str
    singleton_instance: str
    is_stateless: bool = True
    
    # Configuration
    config_module: str = ""
    
    # Dependencies
    external_apis: List[str] = field(default_factory=list)
    requires_credentials: bool = False
    
    # Performance
    avg_latency_ms: int = 0
    max_latency_ms: int = 0
    cache_enabled: bool = False
    cache_ttl_seconds: int = 0
    
    # Documentation
    readme_path: str = ""
    example_usage: str = ""


class ToolRegistry:
    """
    Central registry for all tools in the RentConnect-C3AN system.
    Tools are stateless services that provide capabilities to agents.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._tools: Dict[str, ToolMetadata] = {}
        self._initialize_registry()
    
    def _initialize_registry(self):
        """Initialize registry with all system tools"""
        self._register_listing_analyzer()
        self._register_image_analyzer()
        self._register_compliance_checker()
        self._register_knowledge_graph()
        
        self.logger.info(f"Tool registry initialized with {len(self._tools)} tools")
    
    def _register_listing_analyzer(self):
        """Register the Listing Analyzer Tool"""
        tool = ToolMetadata(
            tool_id="listing_analyzer",
            name="Listing Analyzer",
            description="Neural component for scam detection, feature extraction, and price anomaly detection",
            version="1.0.0",
            
            tool_type=ToolType.ANALYZER,
            capabilities=[
                ToolCapability.SCAM_DETECTION,
                ToolCapability.FEATURE_EXTRACTION,
                ToolCapability.VERIFICATION
            ],
            
            input_schemas=[
                ToolInputSchema(
                    name="listing",
                    type="Dict[str, Any]",
                    description="Property listing with text description and metadata",
                    required=True,
                    validation_rules={
                        "required_fields": ["listing_id", "description", "price"]
                    }
                ),
                ToolInputSchema(
                    name="market_data",
                    type="Optional[Dict[str, Any]]",
                    description="Market rate context for price anomaly detection",
                    required=False
                )
            ],
            
            output_schemas=[
                ToolOutputSchema(
                    name="analysis_result",
                    type="Dict[str, Any]",
                    description="Scam risk score and extracted features",
                    structure={
                        "risk_score": "float (0-1)",
                        "risk_flags": ["flag_1", "flag_2"],
                        "scam_patterns": {
                            "urgent_language": "bool",
                            "payment_red_flags": "bool",
                            "suspicious_contact": "bool",
                            "too_good_to_be_true": "bool"
                        },
                        "extracted_features": {
                            "amenities": ["amenity_1", "amenity_2"],
                            "policies": ["policy_1"],
                            "lease_terms": {}
                        },
                        "verification_status": "str (verified/unverified/suspicious)"
                    }
                )
            ],
            
            module_path="src.tools.listing_analyzer",
            class_name="ListingAnalyzer",
            singleton_instance="listing_analyzer",
            is_stateless=True,
            
            config_module="config.tools_config",
            
            external_apis=["zillow_zori", "redfin"],
            requires_credentials=False,
            
            avg_latency_ms=150,
            max_latency_ms=500,
            cache_enabled=True,
            cache_ttl_seconds=3600,
            
            readme_path="src/tools/README.md",
            example_usage="""
from src.tools.listing_analyzer import listing_analyzer

listing = {
    'listing_id': 'p1',
    'description': 'Beautiful 2BR apartment near campus',
    'price': 1200
}

result = listing_analyzer.analyze(listing)
print(f"Risk score: {result['risk_score']:.2f}")
print(f"Verification: {result['verification_status']}")
"""
        )
        
        self._tools[tool.tool_id] = tool
    
    def _register_image_analyzer(self):
        """Register the Image Analyzer Tool"""
        tool = ToolMetadata(
            tool_id="image_analyzer",
            name="Image Analyzer",
            description="Computer vision tool for photo quality assessment and authenticity detection",
            version="1.0.0",
            
            tool_type=ToolType.ANALYZER,
            capabilities=[
                ToolCapability.IMAGE_ANALYSIS,
                ToolCapability.VERIFICATION
            ],
            
            input_schemas=[
                ToolInputSchema(
                    name="image_urls",
                    type="List[str]",
                    description="URLs of property photos to analyze",
                    required=True,
                    validation_rules={
                        "min_items": 1,
                        "url_format": True
                    }
                )
            ],
            
            output_schemas=[
                ToolOutputSchema(
                    name="analysis_result",
                    type="Dict[str, Any]",
                    description="Image quality and authenticity assessment",
                    structure={
                        "overall_quality_score": "float (0-1)",
                        "photo_count": "int",
                        "authenticity_flags": {
                            "stock_photos_detected": "bool",
                            "low_quality_images": "bool",
                            "insufficient_coverage": "bool"
                        },
                        "per_image_scores": [{
                            "url": "str",
                            "quality_score": "float (0-1)",
                            "is_stock_photo": "bool"
                        }]
                    }
                )
            ],
            
            module_path="src.tools.image_analyzer",
            class_name="ImageAnalyzer",
            singleton_instance="image_analyzer",
            is_stateless=True,
            
            config_module="config.tools_config",
            
            external_apis=["mobilenet", "efficientnet_lite"],
            requires_credentials=False,
            
            avg_latency_ms=300,
            max_latency_ms=1000,
            cache_enabled=True,
            cache_ttl_seconds=7200,
            
            readme_path="src/tools/README.md",
            example_usage="""
from src.tools.image_analyzer import image_analyzer

image_urls = [
    'https://example.com/photo1.jpg',
    'https://example.com/photo2.jpg'
]

result = image_analyzer.analyze(image_urls)
print(f"Quality score: {result['overall_quality_score']:.2f}")
print(f"Stock photos: {result['authenticity_flags']['stock_photos_detected']}")
"""
        )
        
        self._tools[tool.tool_id] = tool
    
    def _register_compliance_checker(self):
        """Register the Compliance Checker Tool"""
        tool = ToolMetadata(
            tool_id="compliance_checker",
            name="Compliance Checker",
            description="Validates listings against Fair Housing Act, SC lease laws, and safety requirements",
            version="1.0.0",
            
            tool_type=ToolType.VALIDATOR,
            capabilities=[
                ToolCapability.COMPLIANCE_CHECK,
                ToolCapability.SAFETY_SCORING,
                ToolCapability.RULE_REASONING
            ],
            
            input_schemas=[
                ToolInputSchema(
                    name="listing",
                    type="Dict[str, Any]",
                    description="Property listing to validate",
                    required=True,
                    validation_rules={
                        "required_fields": ["listing_id", "description", "address"]
                    }
                ),
                ToolInputSchema(
                    name="check_types",
                    type="List[str]",
                    description="Types of compliance checks to perform",
                    required=False,
                    validation_rules={
                        "valid_values": ["fha", "sc_lease", "safety", "landlord"]
                    }
                )
            ],
            
            output_schemas=[
                ToolOutputSchema(
                    name="compliance_result",
                    type="Dict[str, Any]",
                    description="Compliance status and violations",
                    structure={
                        "compliant": "bool",
                        "violations": [{
                            "type": "str (fha/sc_lease/safety)",
                            "severity": "str (critical/major/minor)",
                            "description": "str",
                            "rule_reference": "str"
                        }],
                        "warnings": ["warning_1", "warning_2"],
                        "safety_score": "float (0-1)",
                        "safety_breakdown": {
                            "crime_data": "float",
                            "property_features": "float",
                            "landlord_verification": "bool"
                        }
                    }
                )
            ],
            
            module_path="src.tools.compliance_checker",
            class_name="ComplianceChecker",
            singleton_instance="compliance_checker",
            is_stateless=True,
            
            config_module="config.tools_config",
            
            external_apis=["columbia_gis", "crime_api"],
            requires_credentials=True,
            
            avg_latency_ms=200,
            max_latency_ms=800,
            cache_enabled=False,  # Compliance must be checked fresh
            cache_ttl_seconds=0,
            
            readme_path="src/tools/README.md",
            example_usage="""
from src.tools.compliance_checker import compliance_checker

listing = {
    'listing_id': 'p1',
    'description': 'Nice apartment',
    'address': '123 Main St'
}

result = compliance_checker.check(listing, check_types=['fha', 'safety'])
print(f"Compliant: {result['compliant']}")
print(f"Safety score: {result['safety_score']:.2f}")
for violation in result['violations']:
    print(f"  - {violation['severity']}: {violation['description']}")
"""
        )
        
        self._tools[tool.tool_id] = tool
    
    def _register_knowledge_graph(self):
        """Register the Knowledge Graph Tool"""
        tool = ToolMetadata(
            tool_id="knowledge_graph",
            name="Knowledge Graph",
            description="Symbolic knowledge base for rules (FHA, SC laws), entities (properties, landlords), and relationships",
            version="1.0.0",
            
            tool_type=ToolType.KNOWLEDGE_BASE,
            capabilities=[
                ToolCapability.KNOWLEDGE_QUERY,
                ToolCapability.RULE_REASONING,
                ToolCapability.COMPLIANCE_CHECK
            ],
            
            input_schemas=[
                ToolInputSchema(
                    name="query_type",
                    type="str",
                    description="Type of query (entity/relation/rule/compliance)",
                    required=True,
                    validation_rules={
                        "valid_values": ["entity", "relation", "rule", "compliance", "neighbors"]
                    }
                ),
                ToolInputSchema(
                    name="filters",
                    type="Dict[str, Any]",
                    description="Query filters (entity_type, property_name, etc.)",
                    required=False
                ),
                ToolInputSchema(
                    name="entity_id",
                    type="Optional[str]",
                    description="Entity ID for relation/neighbor queries",
                    required=False
                )
            ],
            
            output_schemas=[
                ToolOutputSchema(
                    name="query_result",
                    type="Dict[str, Any]",
                    description="Query results with entities, relations, or rules",
                    structure={
                        "entities": [{
                            "entity_id": "str",
                            "entity_type": "str",
                            "properties": {}
                        }],
                        "relations": [{
                            "source": "str",
                            "relation_type": "str",
                            "target": "str"
                        }],
                        "rules": [{
                            "rule_id": "str",
                            "rule_text": "str",
                            "source": "str (FHA/SC_LAW)"
                        }],
                        "explanations": ["explanation_1"]
                    }
                )
            ],
            
            module_path="src.tools.knowledge_graph",
            class_name="KnowledgeGraph",
            singleton_instance="knowledge_graph",
            is_stateless=False,  # Maintains state
            
            config_module="config.tools_config",
            
            external_apis=[],
            requires_credentials=False,
            
            avg_latency_ms=50,
            max_latency_ms=200,
            cache_enabled=True,
            cache_ttl_seconds=1800,
            
            readme_path="src/tools/README.md",
            example_usage="""
from src.tools.knowledge_graph import knowledge_graph

# Query FHA rules
rules = knowledge_graph.query(
    query_type='rule',
    filters={'source': 'FHA', 'topic': 'protected_classes'}
)

# Check compliance
compliance = knowledge_graph.check_compliance(
    listing_description='Nice apartment for families',
    rule_type='fha'
)
print(f"Compliant: {compliance['compliant']}")
"""
        )
        
        self._tools[tool.tool_id] = tool
    
    # Registry Query Methods
    
    def get_tool(self, tool_id: str) -> Optional[ToolMetadata]:
        """Retrieve tool metadata by ID"""
        return self._tools.get(tool_id)
    
    def list_tools(self, tool_type: Optional[ToolType] = None) -> List[ToolMetadata]:
        """List all tools, optionally filtered by type"""
        if tool_type:
            return [t for t in self._tools.values() if t.tool_type == tool_type]
        return list(self._tools.values())
    
    def find_tools_by_capability(self, capability: ToolCapability) -> List[ToolMetadata]:
        """Find tools that provide a specific capability"""
        return [t for t in self._tools.values() if capability in t.capabilities]
    
    def get_tool_instance(self, tool_id: str) -> Optional[Any]:
        """
        Dynamically import and return the tool singleton instance.
        Returns None if tool not found or import fails.
        """
        tool = self.get_tool(tool_id)
        if not tool:
            self.logger.error(f"Tool {tool_id} not found in registry")
            return None
        
        try:
            module = __import__(tool.module_path, fromlist=[tool.singleton_instance])
            instance = getattr(module, tool.singleton_instance)
            return instance
        except (ImportError, AttributeError) as e:
            self.logger.error(f"Failed to import tool {tool_id}: {e}")
            return None
    
    def validate_tool_available(self, tool_id: str) -> bool:
        """Check if tool is registered and available"""
        return tool_id in self._tools
    
    def generate_registry_report(self) -> str:
        """Generate human-readable registry report"""
        report = "=" * 80 + "\n"
        report += "RENTCONNECT-C3AN TOOL REGISTRY REPORT\n"
        report += "=" * 80 + "\n\n"
        
        report += f"Total Registered Tools: {len(self._tools)}\n\n"
        
        for tool_type in ToolType:
            tools = self.list_tools(tool_type)
            if tools:
                report += f"\n{tool_type.value.upper()} TOOLS ({len(tools)}):\n"
                report += "-" * 80 + "\n"
                for tool in tools:
                    report += f"  • {tool.name} (ID: {tool.tool_id})\n"
                    report += f"    Version: {tool.version}\n"
                    report += f"    Capabilities: {', '.join(c.value for c in tool.capabilities)}\n"
                    report += f"    Avg Latency: {tool.avg_latency_ms}ms\n"
                    report += f"    Cache: {'Enabled' if tool.cache_enabled else 'Disabled'}\n"
                    report += "\n"
        
        return report


# Global singleton instance
tool_registry = ToolRegistry()
