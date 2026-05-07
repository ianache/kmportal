"""MCP (Model Context Protocol) module for AI Agent Integration.

This module provides the MCP server that exposes knowledge base functionality
to external AI agents.

Exports:
    mcp: The FastMCP server instance
    get_mcp_app: Function to get the ASGI application
    MCPAuthMiddleware: Authentication middleware for MCP endpoints
"""

from .auth import MCPAuthMiddleware, check_domain_access, require_scope
from .server import get_mcp_app, mcp

__all__ = [
    "mcp",
    "get_mcp_app",
    "MCPAuthMiddleware",
    "require_scope",
    "check_domain_access",
]
