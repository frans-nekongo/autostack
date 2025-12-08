#!/usr/bin/env python3
"""
Script to run the API Gateway.
"""
import os
import sys
import uvicorn

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def main():
    """Run the API Gateway."""
    port = int(os.getenv("GATEWAY_PORT", 8020))
    host = os.getenv("GATEWAY_HOST", "0.0.0.0")
    
    print(f"Starting API Gateway on {host}:{port}")
    
    uvicorn.run(
        "gateway.main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()