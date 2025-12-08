import json
import logging
import os
from confluent_kafka import Producer
from typing import Optional, Dict, Any
import asyncio

from autostack_engine.utils.database.mongo_client import connect_to_database

logger = logging.getLogger(__name__)

class BaseTopic:
    """
    Base class for handling Kafka topic messages.
    """
    topic_name: Optional[str] = None  # Set in subclass

    def __init__(self):
        if not self.topic_name:
            raise ValueError("topic_name must be defined in the subclass")
        self._producer = None
        self._executor = None  # Thread pool executor for synchronous operations
        self._loop = asyncio.new_event_loop()
        
    
            
    def _get_producer(self) -> Producer:
        """
        Get or create Kafka producer instance.
        """
        if not self._producer:
            broker_url = os.getenv("KAFKA_BROKER_URL", "localhost:9092")
            self._producer = Producer({
                'bootstrap.servers': broker_url,
                'client.id': f'{self.topic_name}_producer'
            })
            self._executor = asyncio.get_event_loop().run_in_executor
        return self._producer

    async def produce(self, value: Any, key: Optional[str] = None, headers: Optional[Dict[str, str]] = None):
        """
        Produce a message to this topic asynchronously.

        :param value: The message value (will be JSON-serialized if not a string)
        :param key: The message key (string)
        :param headers: Optional headers (dict)
        """
        producer = self._get_producer()

        # Serialize value to JSON if it's not a string
        if not isinstance(value, str):
            value = json.dumps(value)

        # Prepare headers
        kafka_headers = None
        if headers and isinstance(headers, dict):
            kafka_headers = [(str(k), str(v).encode('utf-8')) for k, v in headers.items()]

        def delivery_report(err, msg):
            if err:
                logger.error(f"Message delivery failed: {err}")
            else:
                logger.info(f"Message delivered to {msg.topic()} [{msg.partition()}] @ offset {msg.offset()}")

        def produce_sync():
            """Synchronous produce function to run in a thread pool."""
            producer.produce(
                topic=self.topic_name,
                value=value.encode('utf-8'),
                key=key.encode('utf-8') if key else None,
                headers=kafka_headers,
                callback=delivery_report
            )
            producer.flush()

        # Run the synchronous produce operation in a thread pool
        await self._executor(None, produce_sync)

    def consume(self, message):
        """
        Process incoming Kafka message.
        """
        try:
            key = message.key()
            value = message.value()
            key = key.decode('utf-8') if key else None
            value = value.decode('utf-8') if value else None
            
            logger.info(f"[{self.topic_name.upper()}] Received message: Key={key}")
            
            # Check if process_message is a coroutine and run it appropriately
            if asyncio.iscoroutinefunction(self.process_message):
                # For async methods, run them in the event loop
                self._loop.run_until_complete(self.process_message(key, value))
            else:
                # For sync methods, just call them directly
                self.process_message(key, value)
                
        except Exception as e:
            logger.error(f"[{self.topic_name.upper()}] Error processing message: {e}")

    def process_message(self, key: Optional[str], value: Optional[str]):
        """
        Override this method in subclasses to handle message processing.
        """
        raise NotImplementedError("Subclasses must implement process_message")

    def close_producer(self):
        """
        Close the producer connection.
        """
        if self._producer:
            self._producer.flush()
            self._producer = None
            logger.info(f"[{self.topic_name.upper()}] Producer closed")