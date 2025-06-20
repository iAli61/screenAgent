"""
Event system module

This module provides event-driven communication between components
with typed events and subscription management.
"""

from .events import (
    BaseEvent,
    EventType,
    EventDispatcher,
    ScreenshotCapturedEvent,
    ChangeDetectedEvent,
    MonitoringStatusEvent,
    ErrorEvent,
    EventHandlerType,
    emit_event,
    subscribe_to_events,
    subscribe_to_all_events,
    get_event_dispatcher
)

__all__ = [
    'BaseEvent',
    'EventType',
    'EventDispatcher',
    'ScreenshotCapturedEvent',
    'ChangeDetectedEvent',
    'MonitoringStatusEvent', 
    'ErrorEvent',
    'EventHandlerType',
    'emit_event',
    'subscribe_to_events',
    'subscribe_to_all_events',
    'get_event_dispatcher'
]
