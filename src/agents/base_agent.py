"""
Base Agent Class for RentConnect-C3AN
Implements C3AN foundation elements: Reliability, Alignment, Safety, Explainability
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging
import uuid


@dataclass
class AgentContext:
    """Shared context across all agents"""
    session_id: str
    user_id: Optional[str]
    timestamp: datetime
    metadata: Dict[str, Any]


@dataclass
class AgentOutput:
    """Standardized agent output with explainability"""
    agent_name: str
    result: Any
    confidence: float
    explanation: str
    attribution: List[str]  # Sources/rules used
    errors: List[str]
    timestamp: datetime
    
    
class BaseAgent(ABC):
    """
    Abstract base class for all RentConnect-C3AN agents.
    Enforces C3AN principles: Custom, Compact, Composite.
    """
    
    def __init__(self, agent_name: str, config: Optional[Dict] = None):
        self.agent_name = agent_name
        self.config = config or {}
        self.logger = logging.getLogger(agent_name)
        self._setup_logging()
        
    def _setup_logging(self):
        """Configure agent-specific logging"""
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            f'[{self.agent_name}] %(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        
    @abstractmethod
    def process(self, input_data: Any, context: AgentContext) -> AgentOutput:
        """
        Main processing method - must be implemented by each agent.
        
        Args:
            input_data: Input specific to the agent
            context: Shared context across agents
            
        Returns:
            AgentOutput with results, explanation, and attribution
        """
        pass
    
    @abstractmethod
    def validate_input(self, input_data: Any) -> bool:
        """Validate input data before processing"""
        pass
    
    def create_output(
        self,
        result: Any,
        confidence: float,
        explanation: str,
        attribution: List[str],
        errors: Optional[List[str]] = None
    ) -> AgentOutput:
        """Helper to create standardized output"""
        return AgentOutput(
            agent_name=self.agent_name,
            result=result,
            confidence=confidence,
            explanation=explanation,
            attribution=attribution,
            errors=errors or [],
            timestamp=datetime.utcnow()
        )
    
    def log_decision(self, decision: str, reasoning: str, context: AgentContext):
        """Log decisions for audit trail (C3AN: Reliability & Safety)"""
        self.logger.info(
            f"Decision: {decision} | Reasoning: {reasoning} | "
            f"Session: {context.session_id}"
        )
        
    def check_safety_constraints(self, data: Any) -> tuple[bool, List[str]]:
        """
        Safety checks before processing (C3AN: Safety & Alignment)
        Returns (is_safe, violations)
        """
        violations = []
        
        # Implement safety checks based on agent type
        # Override in subclasses for specific safety rules
        
        return len(violations) == 0, violations
