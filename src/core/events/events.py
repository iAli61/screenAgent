"""
Event system for ScreenAgent component communication
Part of Phase 1.3 - ROI Monitor Module Refactoring
"""
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, TypeVar, Generic
from dataclasses import dataclass
from enum import Enum
import time
import threading
import uuid


class EventType(Enum):
    """Types of events in the system"""
    SCREENSHOT_CAPTURED = "screenshot_captured"
    ROI_CHANGED = "roi_changed"
    MONITORING_STARTED = "monitoring_started"
    MONITORING_STOPPED = "monitoring_stopped"
    CHANGE_DETECTED = "change_detected"
    ERROR_OCCURRED = "error_occurred"
    CONFIG_UPDATED = "config_updated"
    SYSTEM_STATUS_CHANGED = "system_status_changed"


@dataclass
class BaseEvent:
    """Base event class"""
    event_id: str
    event_type: EventType
    timestamp: float
    source: str
    data: Dict[str, Any]
    
    def __post_init__(self):
        if not self.event_id:
            self.event_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = time.time()


@dataclass
class ScreenshotCapturedEvent(BaseEvent):
    """Event fired when a screenshot is captured"""
    
    def __init__(self, source: str, screenshot_data: bytes, roi: tuple, 
                 method: str, capture_time: float, **kwargs):
        super().__init__(
            event_id=kwargs.get('event_id', ''),
            event_type=EventType.SCREENSHOT_CAPTURED,
            timestamp=kwargs.get('timestamp', 0),
            source=source,
            data={
                'screenshot_data': screenshot_data,
                'roi': roi,
                'method': method,
                'capture_time': capture_time,
                'size': len(screenshot_data),
                **kwargs
            }
        )
    
    @property
    def screenshot_data(self) -> bytes:
        return self.data['screenshot_data']
    
    @property
    def roi(self) -> tuple:
        return self.data['roi']
    
    @property
    def method(self) -> str:
        return self.data['method']


@dataclass
class ChangeDetectedEvent(BaseEvent):
    """Event fired when changes are detected"""
    
    def __init__(self, source: str, change_result, screenshot_data: bytes, 
                 roi: tuple, **kwargs):
        super().__init__(
            event_id=kwargs.get('event_id', ''),
            event_type=EventType.CHANGE_DETECTED,
            timestamp=kwargs.get('timestamp', 0),
            source=source,
            data={
                'change_result': change_result,
                'screenshot_data': screenshot_data,
                'roi': roi,
                'confidence': change_result.confidence,
                'change_score': change_result.change_score,
                'method': change_result.method,
                **kwargs
            }
        )
    
    @property
    def change_result(self):
        return self.data['change_result']
    
    @property
    def screenshot_data(self) -> bytes:
        return self.data['screenshot_data']
    
    @property
    def confidence(self) -> float:
        return self.data['confidence']


@dataclass
class MonitoringStatusEvent(BaseEvent):
    """Event fired when monitoring status changes"""
    
    def __init__(self, source: str, status: str, roi: Optional[tuple] = None, **kwargs):
        super().__init__(
            event_id=kwargs.get('event_id', ''),
            event_type=EventType.MONITORING_STARTED if status == 'started' else EventType.MONITORING_STOPPED,
            timestamp=kwargs.get('timestamp', 0),
            source=source,
            data={
                'status': status,
                'roi': roi,
                **kwargs
            }
        )
    
    @property
    def status(self) -> str:
        return self.data['status']
    
    @property
    def roi(self) -> Optional[tuple]:
        return self.data.get('roi')


@dataclass
class ErrorEvent(BaseEvent):
    """Event fired when errors occur"""
    
    def __init__(self, source: str, error: Exception, context: str, **kwargs):
        super().__init__(
            event_id=kwargs.get('event_id', ''),
            event_type=EventType.ERROR_OCCURRED,
            timestamp=kwargs.get('timestamp', 0),
            source=source,
            data={
                'error': str(error),
                'error_type': type(error).__name__,
                'context': context,
                **kwargs
            }
        )
    
    @property
    def error(self) -> str:
        return self.data['error']
    
    @property
    def context(self) -> str:
        return self.data['context']


EventHandlerType = Callable[[BaseEvent], None]


class EventDispatcher:
    """Central event dispatcher for the application"""
    
    def __init__(self):
        self._handlers: Dict[EventType, List[EventHandlerType]] = {}
        self._global_handlers: List[EventHandlerType] = []
        self._event_history: List[BaseEvent] = []
        self._max_history = 1000
        self._lock = threading.Lock()
        self._middleware: List[Callable[[BaseEvent], BaseEvent]] = []
    
    def subscribe(self, event_type: EventType, handler: EventHandlerType) -> None:
        """Subscribe to a specific event type"""
        with self._lock:
            if event_type not in self._handlers:
                self._handlers[event_type] = []
            self._handlers[event_type].append(handler)
    
    def subscribe_global(self, handler: EventHandlerType) -> None:
        """Subscribe to all events"""
        with self._lock:
            self._global_handlers.append(handler)
    
    def unsubscribe(self, event_type: EventType, handler: EventHandlerType) -> None:
        """Unsubscribe from a specific event type"""
        with self._lock:
            if event_type in self._handlers and handler in self._handlers[event_type]:
                self._handlers[event_type].remove(handler)
    
    def unsubscribe_global(self, handler: EventHandlerType) -> None:
        """Unsubscribe from all events"""
        with self._lock:
            if handler in self._global_handlers:
                self._global_handlers.remove(handler)
    
    def add_middleware(self, middleware: Callable[[BaseEvent], BaseEvent]) -> None:
        """Add middleware to process events before dispatching"""
        with self._lock:
            self._middleware.append(middleware)
    
    def emit(self, event: BaseEvent) -> None:
        """Emit an event to all subscribers"""
        # Apply middleware
        processed_event = event
        for middleware in self._middleware:
            try:
                processed_event = middleware(processed_event)
            except Exception as e:
                print(f"⚠️  Event middleware error: {e}")
        
        # Store in history
        with self._lock:
            self._event_history.append(processed_event)
            if len(self._event_history) > self._max_history:
                self._event_history.pop(0)
        
        # Dispatch to specific handlers
        handlers = []
        with self._lock:
            if processed_event.event_type in self._handlers:
                handlers.extend(self._handlers[processed_event.event_type])
            handlers.extend(self._global_handlers)
        
        # Call handlers outside of lock to avoid deadlocks
        for handler in handlers:
            try:
                handler(processed_event)
            except Exception as e:
                print(f"⚠️  Event handler error: {e}")
    
    def get_event_history(self, event_type: Optional[EventType] = None, 
                         limit: Optional[int] = None) -> List[BaseEvent]:
        """Get event history, optionally filtered by type"""
        with self._lock:
            events = self._event_history.copy()
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if limit:
            events = events[-limit:]
        
        return events
    
    def clear_history(self) -> None:
        """Clear event history"""
        with self._lock:
            self._event_history.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get event dispatcher statistics"""
        with self._lock:
            total_handlers = sum(len(handlers) for handlers in self._handlers.values())
            total_handlers += len(self._global_handlers)
            
            event_counts = {}
            for event in self._event_history:
                event_type = event.event_type.value
                event_counts[event_type] = event_counts.get(event_type, 0) + 1
            
            return {
                'total_handlers': total_handlers,
                'event_type_handlers': {et.value: len(handlers) for et, handlers in self._handlers.items()},
                'global_handlers': len(self._global_handlers),
                'history_size': len(self._event_history),
                'event_counts': event_counts,
                'middleware_count': len(self._middleware)
            }


# Global event dispatcher instance
_global_dispatcher: Optional[EventDispatcher] = None


def get_event_dispatcher() -> EventDispatcher:
    """Get the global event dispatcher instance"""
    global _global_dispatcher
    if _global_dispatcher is None:
        _global_dispatcher = EventDispatcher()
    return _global_dispatcher


def emit_event(event: BaseEvent) -> None:
    """Emit an event using the global dispatcher"""
    get_event_dispatcher().emit(event)


def subscribe_to_events(event_type: EventType, handler: EventHandlerType) -> None:
    """Subscribe to events using the global dispatcher"""
    get_event_dispatcher().subscribe(event_type, handler)


def subscribe_to_all_events(handler: EventHandlerType) -> None:
    """Subscribe to all events using the global dispatcher"""
    get_event_dispatcher().subscribe_global(handler)


# Middleware examples
def logging_middleware(event: BaseEvent) -> BaseEvent:
    """Middleware to log all events"""
    print(f"📡 Event: {event.event_type.value} from {event.source} at {event.timestamp}")
    return event


def debug_middleware(event: BaseEvent) -> BaseEvent:
    """Middleware to add debug information"""
    event.data['debug_info'] = {
        'thread_id': threading.current_thread().ident,
        'process_time': time.process_time()
    }
    return event
