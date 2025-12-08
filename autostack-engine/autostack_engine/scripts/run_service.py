#!/usr/bin/env python3
"""
Script to run individual microservices.
"""
import os
import sys
import argparse
import uvicorn

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

SERVICE_CONFIG = {
    'user': {
        'module': 'services.user_service.main:app',
        'port': int(os.getenv('USER_SERVICE_PORT', 8001)),
        'name': 'User Service'
    },
    'order': {
        'module': 'services.order_service.main:app',
        'port': int(os.getenv('ORDER_SERVICE_PORT', 8002)),
        'name': 'Order Service'
    },
    'inventory': {
        'module': 'services.inventory_service.main:app',
        'port': int(os.getenv('INVENTORY_SERVICE_PORT', 8003)),
        'name': 'Inventory Service'
    }
}

def main():
    """Run a specific microservice."""
    parser = argparse.ArgumentParser(description='Run individual microservice')
    parser.add_argument(
        'service',
        choices=['user', 'order', 'inventory'],
        help='Service to run'
    )
    parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='Host to bind to'
    )
    parser.add_argument(
        '--port',
        type=int,
        help='Port to bind to (overrides default)'
    )
    parser.add_argument(
        '--no-reload',
        action='store_true',
        help='Disable auto-reload'
    )
    
    args = parser.parse_args()
    
    if args.service not in SERVICE_CONFIG:
        print(f"Unknown service: {args.service}")
        sys.exit(1)
    
    config = SERVICE_CONFIG[args.service]
    port = args.port or config['port']
    
    print(f"Starting {config['name']} on {args.host}:{port}")
    
    try:
        uvicorn.run(
            config['module'],
            host=args.host,
            port=port,
            reload=not args.no_reload,
            log_level="info"
        )
    except Exception as e:
        print(f"Error starting service: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()