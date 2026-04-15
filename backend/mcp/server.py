"""
MCP server — registers all tools used by agents.
In this implementation, MCP tools are Python functions called directly by agents.
(Full MCP server protocol would require mcp library and separate process.)
"""

import logging
from typing import Dict, Any, Callable

logger = logging.getLogger(__name__)

# Tool registry
_tool_registry: Dict[str, Callable] = {}


def register_tool(name: str, func: Callable):
    """Register a tool in the MCP registry."""
    _tool_registry[name] = func
    logger.debug(f"Registered MCP tool: {name}")


def get_tool(name: str) -> Callable:
    """Get a registered tool by name."""
    if name not in _tool_registry:
        raise KeyError(f"MCP tool not found: {name}")
    return _tool_registry[name]


def list_tools():
    """List all registered tool names."""
    return list(_tool_registry.keys())


def initialize_all_tools():
    """Register all tools from all MCP tool modules."""
    from backend.mcp import intake_tools, ocr_tools, credit_tools, rules_tools, policy_tools, delivery_tools

    # Intake tools
    register_tool("validate_pan_format", intake_tools.validate_pan_format)
    register_tool("check_blacklist_db", intake_tools.check_blacklist_db)
    register_tool("check_duplicate_application", intake_tools.check_duplicate_application)

    # OCR tools
    register_tool("preprocess_image", ocr_tools.preprocess_image)
    register_tool("run_ocr", ocr_tools.run_ocr)
    register_tool("parse_pan_fields", ocr_tools.parse_pan_fields)
    register_tool("parse_salary_fields", ocr_tools.parse_salary_fields)

    # Credit tools
    register_tool("load_xgboost_model", credit_tools.load_xgboost_model)
    register_tool("predict_default_probability", credit_tools.predict_default_probability)
    register_tool("generate_shap_values", credit_tools.generate_shap_values)

    # Rules tools
    register_tool("check_age_rule", rules_tools.check_age_rule)
    register_tool("check_income_rule", rules_tools.check_income_rule)
    register_tool("check_foir_rule", rules_tools.check_foir_rule)
    register_tool("check_bureau_score_rule", rules_tools.check_bureau_score_rule)

    # Policy tools
    register_tool("search_policy_index", policy_tools.search_policy_index)
    register_tool("rank_policy_clauses", policy_tools.rank_policy_clauses)

    # Delivery tools
    register_tool("save_result_to_db", delivery_tools.save_result_to_db)
    register_tool("update_application_status", delivery_tools.update_application_status)

    logger.info(f"Registered {len(_tool_registry)} MCP tools")