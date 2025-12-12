"""RabbitMQ utilities for publishing and consuming events."""
import os
import json
import time
import logging
from typing import Any, Dict, Optional, Callable
import pika
from pika.exceptions import AMQPConnectionError, ChannelClosedByBroker

from shared.config import RABBITMQ_URL

logger = logging.getLogger(__name__)

_connection: Optional[pika.BlockingConnection] = None
_channel: Optional[pika.channel.Channel] = None


def get_rabbitmq_connection():
    """Get or create RabbitMQ connection."""
    global _connection, _channel
    
    if _connection is None or _connection.is_closed:
        try:
            parameters = pika.URLParameters(RABBITMQ_URL)
            _connection = pika.BlockingConnection(parameters)
            _channel = _connection.channel()
            
            # Declare exchange for all events
            _channel.exchange_declare(
                exchange='vidsage_events',
                exchange_type='topic',
                durable=True
            )
            
            logger.info("✅ Connected to RabbitMQ")
        except AMQPConnectionError as e:
            logger.error(f"❌ Failed to connect to RabbitMQ: {e}")
            raise
    
    return _connection, _channel


def publish_event(event_type: str, payload: Dict[str, Any]) -> None:
    """
    Publish an event to RabbitMQ.
    
    Args:
        event_type: Event type (e.g., 'video.submitted', 'transcript.downloaded')
        payload: Event payload as dict
    """
    try:
        _, channel = get_rabbitmq_connection()
        
        message = {
            "event_type": event_type,
            "payload": payload
        }
        
        channel.basic_publish(
            exchange='vidsage_events',
            routing_key=event_type,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
                content_type='application/json'
            )
        )
        
        logger.info(f"📤 Published event: {event_type}")
    except Exception as e:
        logger.error(f"❌ Failed to publish event {event_type}: {e}")
        raise


def consume_events(
    event_types: list[str],
    callback: Callable[[str, Dict[str, Any]], None],
    queue_name: str
) -> None:
    """
    Consume events from RabbitMQ.
    
    Args:
        event_types: List of event types to listen for
        callback: Function to call for each event (event_type, payload)
        queue_name: Name of the queue to consume from
    """
    try:
        _, channel = get_rabbitmq_connection()
        
        # Declare queue
        channel.queue_declare(queue=queue_name, durable=True)
        
        # Bind queue to exchange for each event type
        for event_type in event_types:
            channel.queue_bind(
                exchange='vidsage_events',
                queue=queue_name,
                routing_key=event_type
            )
        
        # Set QoS to process one message at a time
        channel.basic_qos(prefetch_count=1)
        
        def on_message(ch, method, properties, body):
            try:
                message = json.loads(body)
                event_type = message.get("event_type")
                payload = message.get("payload", {})
                
                # Call the callback
                callback(event_type, payload)
                
                # Acknowledge the message
                ch.basic_ack(delivery_tag=method.delivery_tag)
                
            except Exception as e:
                logger.error(f"❌ Error processing message: {e}")
                # Reject and requeue the message
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        
        channel.basic_consume(
            queue=queue_name,
            on_message_callback=on_message
        )
        
        logger.info(f"👂 Listening for events: {event_types} on queue: {queue_name}")
        channel.start_consuming()
        
    except KeyboardInterrupt:
        logger.info("🛑 Stopping consumer...")
        if channel:
            channel.stop_consuming()
    except Exception as e:
        logger.error(f"❌ Consumer error: {e}")
        raise


def close_connection():
    """Close RabbitMQ connection."""
    global _connection
    if _connection and not _connection.is_closed:
        _connection.close()
        logger.info("👋 RabbitMQ connection closed")
