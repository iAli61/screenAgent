"""
Monitoring Service Implementation
Concrete implementation of ROI monitoring operations
"""
import asyncio
import uuid
from typing import List, Optional, Dict, Any, Callable
from datetime import datetime
import logging

from src.domain.interfaces.monitoring_service import IMonitoringService
from src.domain.interfaces.screenshot_service import IScreenshotService
from src.domain.interfaces.analysis_service import IAnalysisService
from src.domain.interfaces.storage_service import IRepository
from src.domain.interfaces.event_service import IEventService
from src.domain.entities.roi_region import ROIRegion
from src.domain.entities.monitoring_session import MonitoringSession
from src.domain.entities.screenshot import Screenshot
from src.domain.events.monitoring_started import (
    MonitoringStarted, MonitoringStopped, MonitoringPaused, 
    MonitoringResumed, ChangeDetected, MonitoringError
)


logger = logging.getLogger(__name__)


class MonitoringService(IMonitoringService):
    """Concrete implementation of monitoring service"""
    
    def __init__(
        self,
        screenshot_service: IScreenshotService,
        analysis_service: IAnalysisService,
        session_repository: IRepository[MonitoringSession],
        event_service: IEventService
    ):
        self._screenshot_service = screenshot_service
        self._analysis_service = analysis_service
        self._session_repository = session_repository
        self._event_service = event_service
        self._active_sessions: Dict[str, asyncio.Task] = {}
        
    async def start_monitoring(
        self, 
        roi: ROIRegion,
        change_threshold: float = 20.0,
        check_interval: float = 0.5,
        on_change_callback: Optional[Callable] = None
    ) -> MonitoringSession:
        """Start monitoring an ROI region for changes"""
        try:
            session_id = str(uuid.uuid4())
            
            # Create monitoring session
            session = MonitoringSession(
                id=session_id,
                roi_region=roi,
                start_time=datetime.now(),
                status="running",
                change_threshold=change_threshold,
                check_interval=check_interval,
                screenshots_captured=0,
                changes_detected=0
            )
            
            # Save session to repository
            await self._session_repository.create(session)
            
            # Start monitoring task
            monitoring_task = asyncio.create_task(
                self._monitor_roi_loop(session, on_change_callback)
            )
            self._active_sessions[session_id] = monitoring_task
            
            # Publish event
            event = MonitoringStarted(
                session_id=session_id,
                roi_id=roi.id,
                roi_coordinates=(roi.coordinates.x, roi.coordinates.y, 
                               roi.coordinates.width, roi.coordinates.height),
                change_threshold=change_threshold,
                check_interval=check_interval
            )
            await self._event_service.publish(event)
            
            logger.info(f"Started monitoring session: {session_id} for ROI: {roi.id}")
            return session
            
        except Exception as e:
            logger.error(f"Failed to start monitoring for ROI {roi.id}: {e}")
            raise
    
    async def stop_monitoring(self, session_id: str) -> bool:
        """Stop monitoring session"""
        try:
            session = await self._session_repository.get_by_id(session_id)
            if not session:
                logger.warning(f"Session not found: {session_id}")
                return False
            
            # Cancel monitoring task
            if session_id in self._active_sessions:
                task = self._active_sessions[session_id]
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                del self._active_sessions[session_id]
            
            # Update session status
            session.status = "stopped"
            session.end_time = datetime.now()
            await self._session_repository.update(session)
            
            # Publish event
            duration = (session.end_time - session.start_time).total_seconds() if session.end_time else 0
            event = MonitoringStopped(
                session_id=session_id,
                roi_id=session.roi_region.id,
                duration_seconds=duration,
                screenshots_captured=session.screenshots_captured,
                changes_detected=session.changes_detected,
                reason="manual"
            )
            await self._event_service.publish(event)
            
            logger.info(f"Stopped monitoring session: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop monitoring session {session_id}: {e}")
            return False
    
    async def pause_monitoring(self, session_id: str) -> bool:
        """Pause monitoring session"""
        try:
            session = await self._session_repository.get_by_id(session_id)
            if not session or session.status != "running":
                return False
            
            session.status = "paused"
            await self._session_repository.update(session)
            
            # Publish event
            event = MonitoringPaused(
                session_id=session_id,
                roi_id=session.roi_region.id,
                reason="manual"
            )
            await self._event_service.publish(event)
            
            logger.info(f"Paused monitoring session: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to pause monitoring session {session_id}: {e}")
            return False
    
    async def resume_monitoring(self, session_id: str) -> bool:
        """Resume monitoring session"""
        try:
            session = await self._session_repository.get_by_id(session_id)
            if not session or session.status != "paused":
                return False
            
            session.status = "running"
            await self._session_repository.update(session)
            
            # Publish event
            event = MonitoringResumed(
                session_id=session_id,
                roi_id=session.roi_region.id
            )
            await self._event_service.publish(event)
            
            logger.info(f"Resumed monitoring session: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to resume monitoring session {session_id}: {e}")
            return False
    
    async def update_monitoring_config(
        self, 
        session_id: str,
        change_threshold: Optional[float] = None,
        check_interval: Optional[float] = None
    ) -> bool:
        """Update monitoring configuration"""
        try:
            session = await self._session_repository.get_by_id(session_id)
            if not session:
                return False
            
            if change_threshold is not None:
                session.change_threshold = change_threshold
            if check_interval is not None:
                session.check_interval = check_interval
            
            await self._session_repository.update(session)
            
            logger.info(f"Updated monitoring config for session: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update monitoring config {session_id}: {e}")
            return False
    
    async def get_monitoring_session(self, session_id: str) -> Optional[MonitoringSession]:
        """Get monitoring session by ID"""
        try:
            return await self._session_repository.get_by_id(session_id)
        except Exception as e:
            logger.error(f"Failed to get monitoring session {session_id}: {e}")
            return None
    
    async def list_active_sessions(self) -> List[MonitoringSession]:
        """List all active monitoring sessions"""
        try:
            criteria = {"status": "running"}
            return await self._session_repository.find_by_criteria(criteria)
        except Exception as e:
            logger.error(f"Failed to list active sessions: {e}")
            return []
    
    async def get_session_screenshots(
        self, 
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Screenshot]:
        """Get screenshots captured during monitoring session"""
        try:
            return await self._screenshot_service.list_screenshots(
                session_id=session_id, 
                limit=limit
            )
        except Exception as e:
            logger.error(f"Failed to get session screenshots {session_id}: {e}")
            return []
    
    async def get_change_history(
        self, 
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get change detection history for session"""
        try:
            # TODO: Implement change history retrieval
            # For now, return empty list
            return []
        except Exception as e:
            logger.error(f"Failed to get change history {session_id}: {e}")
            return []
    
    async def cleanup_completed_sessions(self, max_age_days: int = 7) -> int:
        """Clean up completed monitoring sessions"""
        try:
            # TODO: Implement cleanup logic
            logger.info(f"Cleanup completed, would clean sessions older than {max_age_days} days")
            return 0
        except Exception as e:
            logger.error(f"Failed to cleanup sessions: {e}")
            return 0
    
    async def _monitor_roi_loop(
        self, 
        session: MonitoringSession, 
        on_change_callback: Optional[Callable]
    ) -> None:
        """Main monitoring loop for ROI region"""
        reference_screenshot = None
        
        try:
            while session.status == "running":
                if session.status == "paused":
                    await asyncio.sleep(1.0)
                    continue
                
                # Capture current screenshot
                current_screenshot = await self._screenshot_service.capture_roi(
                    session.roi_region,
                    metadata={"session_id": session.id}
                )
                
                session.screenshots_captured += 1
                
                # Compare with reference if available
                if reference_screenshot:
                    changes_detected, change_score = await self._analysis_service.detect_changes(
                        reference_screenshot,
                        current_screenshot,
                        threshold=session.change_threshold,
                        region=session.roi_region
                    )
                    
                    if changes_detected:
                        session.changes_detected += 1
                        
                        # Publish change event
                        event = ChangeDetected(
                            session_id=session.id,
                            roi_id=session.roi_region.id,
                            change_score=change_score,
                            threshold=session.change_threshold,
                            screenshot_triggered=True,
                            screenshot_id=current_screenshot.id
                        )
                        await self._event_service.publish(event)
                        
                        # Call change callback if provided
                        if on_change_callback:
                            try:
                                await on_change_callback(session, current_screenshot, change_score)
                            except Exception as e:
                                logger.error(f"Error in change callback: {e}")
                        
                        # Update reference screenshot
                        reference_screenshot = current_screenshot
                else:
                    # Set initial reference
                    reference_screenshot = current_screenshot
                
                # Update session in repository
                await self._session_repository.update(session)
                
                # Wait for next check
                await asyncio.sleep(session.check_interval)
                
        except asyncio.CancelledError:
            logger.info(f"Monitoring loop cancelled for session: {session.id}")
            raise
        except Exception as e:
            logger.error(f"Error in monitoring loop for session {session.id}: {e}")
            
            # Publish error event
            error_event = MonitoringError(
                session_id=session.id,
                roi_id=session.roi_region.id,
                error_type="monitoring_loop_error",
                error_message=str(e),
                is_recoverable=False
            )
            await self._event_service.publish(error_event)
            
            # Update session status
            session.status = "error"
            session.end_time = datetime.now()
            await self._session_repository.update(session)
