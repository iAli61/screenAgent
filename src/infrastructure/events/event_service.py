"""
Event Service Implementation
Provides event publishing and subscription capabilities
"""
import asyncio
import uuid
from typing import Dict, List, Callable, Any, Type, Optional
import logging

from src.domain.interfaces.event_service import IEventService
from src.domain.events.screenshot_captured import BaseDomainEvent


class EventService(IEventService):
    """Concrete implementation of event service"""
    
    def __init__(self):
        self._subscribers: Dict[str, Callable] = {}  # subscription_id -> handler
        self._type_subscribers: Dict[Type[BaseDomainEvent], List[str]] = {}  # event_type -> subscription_ids
        self._event_history: List[BaseDomainEvent] = []
        self._logger = logging.getLogger(__name__)
    
    async def publish(self, event: BaseDomainEvent) -> None:
        """Publish an event to all subscribers"""
        try:
            event_type = type(event)
            subscription_ids = self._type_subscribers.get(event_type, [])
            
            # Add to history
            self._event_history.append(event)
            
            self._logger.debug(f"Publishing event {event_type.__name__} to {len(subscription_ids)} subscribers")
            
            # Call all subscribers asynchronously
            tasks = []
            for subscription_id in subscription_ids:
                if subscription_id in self._subscribers:
                    handler = self._subscribers[subscription_id]
                    if asyncio.iscoroutinefunction(handler):
                        tasks.append(handler(event))
                    else:
                        # Run sync functions in thread pool
                        tasks.append(asyncio.to_thread(handler, event))
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
                
        except Exception as e:
            self._logger.error(f"Error publishing event {type(event).__name__}: {e}")
    
    async def publish_batch(self, events: List[BaseDomainEvent]) -> None:
        """Publish multiple events as a batch"""
        try:
            # Publish each event in sequence
            for event in events:
                await self.publish(event)
        except Exception as e:
            self._logger.error(f"Error publishing event batch: {e}")
    
    def subscribe(self, event_type: Type[BaseDomainEvent], handler: Callable[[BaseDomainEvent], None]) -> str:
        """Subscribe to an event type"""
        try:
            subscription_id = str(uuid.uuid4())
            
            # Store handler
            self._subscribers[subscription_id] = handler
            
            # Add to type mapping
            if event_type not in self._type_subscribers:
                self._type_subscribers[event_type] = []
            
            self._type_subscribers[event_type].append(subscription_id)
            
            self._logger.debug(f"Subscribed handler to {event_type.__name__} with ID {subscription_id}")
            return subscription_id
            
        except Exception as e:
            self._logger.error(f"Error subscribing to event {event_type.__name__}: {e}")
            return ""
    
    def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from domain events"""
        try:
            if subscription_id not in self._subscribers:
                return False
            
            # Remove from subscribers
            del self._subscribers[subscription_id]
            
            # Remove from type mappings
            for event_type, sub_ids in self._type_subscribers.items():
                if subscription_id in sub_ids:
                    sub_ids.remove(subscription_id)
                    break
            
            self._logger.debug(f"Unsubscribed {subscription_id}")
            return True
                
        except Exception as e:
            self._logger.error(f"Error unsubscribing {subscription_id}: {e}")
            return False
    
    def get_event_history(
        self, 
        event_type: Optional[Type[BaseDomainEvent]] = None,
        limit: Optional[int] = None
    ) -> List[BaseDomainEvent]:
        """Get history of published events"""
        try:
            events = self._event_history
            
            # Filter by event type if specified
            if event_type:
                events = [e for e in events if isinstance(e, event_type)]
            
            # Apply limit if specified
            if limit:
                events = events[-limit:]
            
            return events
            
        except Exception as e:
            self._logger.error(f"Error getting event history: {e}")
            return []
    
    async def clear_event_history(self) -> None:
        """Clear event history"""
        try:
            self._event_history.clear()
            self._logger.debug("Cleared event history")
        except Exception as e:
            self._logger.error(f"Error clearing event history: {e}")
    
    def clear_subscribers(self, event_type: Optional[Type[BaseDomainEvent]] = None) -> None:
        """Clear subscribers for an event type or all events"""
        try:
            if event_type:
                # Clear subscribers for specific event type
                if event_type in self._type_subscribers:
                    subscription_ids = self._type_subscribers[event_type]
                    for sub_id in subscription_ids:
                        self._subscribers.pop(sub_id, None)
                    del self._type_subscribers[event_type]
                self._logger.debug(f"Cleared subscribers for {event_type.__name__}")
            else:
                # Clear all subscribers
                self._subscribers.clear()
                self._type_subscribers.clear()
                self._logger.debug("Cleared all event subscribers")
                
        except Exception as e:
            self._logger.error(f"Error clearing subscribers: {e}")
    
    def get_subscriber_count(self, event_type: Type[BaseDomainEvent]) -> int:
        """Get the number of subscribers for an event type"""
        return len(self._type_subscribers.get(event_type, []))


# Optional import for base event
try:
    from typing import Optional
except ImportError:
    pass
