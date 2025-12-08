#!/usr/bin/env python3
"""
Script to run Kafka consumers for all services.
"""
import os
import sys
import argparse
import logging

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from utils.kafka.consumer_manager import ConsumerManager

# Define all available topic classes
ALL_TOPIC_CLASSES = [
    'services.component.topics.components_create.ComponentsCreateTopic',
    'services.environment.topics.development_create.DevelopmentCreateTopic',
    'services.environment.topics.production_create.ProductionCreateTopic',
    'services.infrastructure.topics.infrastructure_provision.InfrastructureProvisioningTopic',
    'services.orchestration.topics.orchestration.OrchestrationTopic',
    'services.project.topics.project_created.ProjectCreatedTopic',
]

# Define service-specific topic groups
SERVICE_TOPICS = {
    'component': [
        'services.component.topics.components_create.ComponentsCreateTopic',
    ],
    'environment': [
        'services.environment.topics.development_create.DevelopmentCreateTopic',
        'services.environment.topics.production_create.ProductionCreateTopic',
        'services.environment.topics.technologies_create.TechnologiesCreateTopic',
    ],
    'infrastructure': [
        'services.infrastructure.topics.infrastructure_provision.InfrastructureProvisioningTopic',
        # 'services.infrastructure_service.topics.infrastructure_status.InfrastructureStatusTopic',
    ],
    'orchestration': [
        # 'services.orchestration_service.topics.deployment_completed.DeploymentCompleted',
        # 'services.orchestration_service.topics.orchestration_commands.OrchestrationCommands',
        'services.orchestration.topics.orchestration.OrchestrationTopic',
    ],
    'project': [
         'services.project.topics.project_created.ProjectCreatedTopic',
    ],
}

def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main():
    """Main function to run consumers."""
    setup_logging()
    
    parser = argparse.ArgumentParser(description='Run Kafka consumers')
    parser.add_argument(
        '--services',
        nargs='+',
        choices=['component', 'environment', 'infrastructure',  'orchestration', 'project', 'all'],
        default=['all'],
        help='Services to run consumers for'
    )
    parser.add_argument(
        '--group-id',
        default='microservices-consumers',
        help='Consumer group ID'
    )
    parser.add_argument(
        '--list-topics',
        action='store_true',
        help='List available topics and exit'
    )
    
    args = parser.parse_args()
    
    if args.list_topics:
        print("Available services and their topics:")
        for service, topics in SERVICE_TOPICS.items():
            print(f"\n{service.upper()} SERVICE:")
            for topic in topics:
                print(f"  - {topic}")
        return
    
    # Determine which topics to consume
    if 'all' in args.services:
        topic_classes = ALL_TOPIC_CLASSES
    else:
        topic_classes = []
        for service in args.services:
            topic_classes.extend(SERVICE_TOPICS.get(service, []))
    
    if not topic_classes:
        print("No topics selected to consume from.")
        return
    
    print(f"Starting consumers for services: {args.services}")
    print(f"Consumer group: {args.group_id}")
    print(f"Topics: {len(topic_classes)}")
    
    # Start consuming
    consumer_manager = ConsumerManager(group_id=args.group_id)
    
    try:
        consumer_manager.start_consuming(topic_classes)
    except KeyboardInterrupt:
        print("\nShutting down consumers...")
    except Exception as e:
        print(f"Error running consumers: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()