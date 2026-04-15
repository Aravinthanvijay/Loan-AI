"""Agents package - 6 sequential loan processing agents."""

from .agent1_intake import IntakeAgent
from .agent2_document import DocumentAgent
from .agent3_credit import CreditAgent
from .agent4_rules import RulesAgent
from .agent5_policy import PolicyAgent
from .agent6_decision import DecisionAgent

__all__ = [
    "IntakeAgent",
    "DocumentAgent",
    "CreditAgent",
    "RulesAgent",
    "PolicyAgent",
    "DecisionAgent",
]