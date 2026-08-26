"""
Entry point for running BookMyShow MCP (Model Context Protocol) Server.
Run using: python mcp_server.py
"""

from bms_scraper.mcp_server import mcp, run_server

if __name__ == "__main__":
    run_server()
