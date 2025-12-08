import os
import signal
import sys
import time
import importlib
import logging
from confluent_kafka import Consumer
from typing import List, Optional

logger = logging.getLogger(__name__)

class ConsumerManager:
    """
    Manages Kafka consumers for multiple topics.
    """
    
    def __init__(self, group_id: str = "autostack-group"):
        self.group_id = group_id
        self.consumer = None
        self.topic_instances = []
        self.running = False

    def load_topic_classes(self, topic_class_paths: List[str]) -> List:
        """
        Dynamically load topic classes from import paths.
        """
        topic_instances = []
        
        for path in topic_class_paths:
            try:
                module_path, class_name = path.rsplit('.', 1)
                module = importlib.import_module(module_path)
                topic_class = getattr(module, class_name)
                instance = topic_class()
                topic_instances.append(instance)
                logger.info(f"Loaded topic: {instance.topic_name}")
            except Exception as e:
                logger.error(f"Failed to load topic {path}: {e}")
        
        return topic_instances

    def start_consuming(self, topic_class_paths: List[str]):
        """
        Start consuming messages from specified topics.
        """
        self.topic_instances = self.load_topic_classes(topic_class_paths)
        
        if not self.topic_instances:
            logger.error("No valid topic classes found.")
            return

        topic_names = [topic.topic_name for topic in self.topic_instances]
        
        broker_url = os.getenv("KAFKA_BROKER_URL", "localhost:9092")
        conf = {
            'bootstrap.servers': broker_url,
            'group.id': self.group_id,
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': True
        }

        self.consumer = Consumer(conf)
        self.consumer.subscribe(topic_names)
        logger.info(f"Subscribed to topics: {topic_names}")

        # Set up signal handlers
        signal.signal(signal.SIGINT, self._shutdown)
        signal.signal(signal.SIGTERM, self._shutdown)

        self.running = True
        self._consume_loop()

    def _consume_loop(self):
        """
        Main consumption loop.
        """
        try:
            while self.running:
                msg = self.consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                if msg.error():
                    logger.error(f"Kafka error: {msg.error()}")
                    continue
                
                # Find matching topic handler
                for topic in self.topic_instances:
                    if msg.topic() == topic.topic_name:
                        topic.consume(msg)
                        break
                        
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        finally:
            self._cleanup()

    def _shutdown(self, signalnum, frame):
        """
        Graceful shutdown handler.
        """
        logger.info('Shutting down consumer...')
        self.running = False

    def _cleanup(self):
        """
        Clean up resources.
        """
        if self.consumer:
            self.consumer.close()
            logger.info("Consumer closed")
        
        # Close producers in topic instances
        for topic in self.topic_instances:
            topic.close_producer()

    def stop(self):
        """
        Stop the consumer.
        """
        self.running = False