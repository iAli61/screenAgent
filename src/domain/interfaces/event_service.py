"""
Event Service Interface
Defines the contract for event handling and publishing
"""
from abc import ABC, abstractmethod
from typing import Callable, List, Optional, Dict, Any, Type, Awaitable
from asyncio import Queue

from ..events.screenshot_captured import BaseDomainEvent


EventHandler = Callable[[BaseDomainEvent], Awaitable[None]]


class IEventService(ABC):
    """Interface for domain event handling"""
    
    @abstractmethod
    async def publish(self, event: BaseDomainEvent) -> None:
        """
        Publish domain event to all subscribers
        
        Args:
            event: Domain event to publish
        """
        pass
    
    @abstractmethod
    def subscribe(
        self, 
        event_type: Type[BaseDomainEvent], 
        handler: EventHandler
    ) -> str:
        """
        Subscribe to domain events of specific type
        
        Args:
            event_type: Type of event to subscribe to
            handler: Event handler function
            
        Returns:
            Subscription ID for later unsubscribing
        """
        pass
    
    @abstractmethod
    def unsubscribe(self, subscription_id: str) -> bool:
        """
        Unsubscribe from domain events
        
        Args:
            subscription_id: ID returned from subscribe()
            
        Returns:
            True if unsubscribed successfully, False otherwise
        """
        pass
    
    @abstractmethod
    async def publish_batch(self, events: List[BaseDomainEvent]) -> None:
        """
        Publish multiple events as a batch
        
        Args:
            events: List of domain events to publish
        """
        pass
    
    @abstractmethod
    def get_event_history(
        self, 
        event_type: Optional[Type[BaseDomainEvent]] = None,
        limit: Optional[int] = None
    ) -> List[BaseDomainEvent]:
        """
        Get history of published events
        
        Args:
            event_type: Optional filter by event type
            limit: Maximum number of events to return
            
        Returns:
            List of domain events
        """
        pass
    
    @abstractmethod
    async def clear_event_history(self) -> None:
        """Clear event history"""
        pass


class INotificationService(ABC):
    """Interface for external notifications"""
    
    @abstractmethod
    async def send_notification(
        self, 
        title: str,
        message: str,
        severity: str = "info",
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send notification to external systems
        
        Args:
            title: Notification title
            message: Notification message
            severity: Severity level (info, warning, error)
            metadata: Optional metadata
            
        Returns:
            True if sent successfully, False otherwise
        """
        pass
    
    @abstractmethod
    async def send_webhook(
        self, 
        url: str,
        payload: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Send webhook notification
        
        Args:
            url: Webhook URL
            payload: JSON payload to send
            headers: Optional HTTP headers
            
        Returns:
            True if sent successfully, False otherwise
        """
        pass
    
    @abstractmethod
    async def send_email(
        self, 
        to_addresses: List[str],
        subject: str,
        body: str,
        attachments: Optional[List[str]] = None
    ) -> bool:
        """
        Send email notification
        
        Args:
            to_addresses: List of recipient email addresses
            subject: Email subject
            body: Email body
            attachments: Optional file attachments
            
        Returns:
            True if sent successfully, False otherwise
        """
        pass
