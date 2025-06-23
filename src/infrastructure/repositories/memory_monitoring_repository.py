"""
Memory Monitoring Repository Implementation
In-memory storage for monitoring session entities
"""
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from src.domain.repositories.monitoring_repository import IMonitoringRepository
from src.domain.entities.monitoring_session import MonitoringSession


class MemoryMonitoringRepository(IMonitoringRepository):
    """In-memory implementation of monitoring repository"""
    
    def __init__(self):
        self._sessions: Dict[str, MonitoringSession] = {}
        self._lock = asyncio.Lock()
    
    async def create(self, session: MonitoringSession) -> MonitoringSession:
        """Create a new monitoring session record"""
        async with self._lock:
            self._sessions[session.session_id] = session
            return session
    
    async def get_by_id(self, session_id: str) -> Optional[MonitoringSession]:
        """Get monitoring session by ID"""
        async with self._lock:
            return self._sessions.get(session_id)
    
    async def update(self, session: MonitoringSession) -> MonitoringSession:
        """Update existing monitoring session record"""
        async with self._lock:
            self._sessions[session.session_id] = session
            return session
    
    async def delete(self, session_id: str) -> bool:
        """Delete monitoring session by ID"""
        async with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
                return True
            return False
    
    async def get_all(self) -> List[MonitoringSession]:
        """Get all monitoring sessions"""
        async with self._lock:
            return list(self._sessions.values())
    
    async def get_active_sessions(self) -> List[MonitoringSession]:
        """Get all active monitoring sessions"""
        async with self._lock:
            return [
                session for session in self._sessions.values()
                if session.status == "active"
            ]
    
    async def get_by_roi_region(self, roi_id: str) -> List[MonitoringSession]:
        """Get monitoring sessions by ROI region ID"""
        async with self._lock:
            return [
                session for session in self._sessions.values()
                if hasattr(session, 'roi_region_id') and session.roi_region_id == roi_id
            ]
    
    async def get_sessions_in_range(
        self, 
        start_time: datetime, 
        end_time: datetime
    ) -> List[MonitoringSession]:
        """Get monitoring sessions within time range"""
        async with self._lock:
            return [
                session for session in self._sessions.values()
                if start_time <= session.start_time <= end_time
            ]
    
    async def get_session_statistics(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a monitoring session"""
        async with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return None
            
            # Basic statistics - can be enhanced later
            return {
                "session_id": session_id,
                "duration": (session.end_time - session.start_time).total_seconds() if session.end_time else None,
                "change_count": getattr(session, 'change_count', 0),
                "screenshot_count": getattr(session, 'screenshot_count', 0),
                "status": session.status
            }
    
    async def update_session_statistics(
        self, 
        session_id: str, 
        statistics: Dict[str, Any]
    ) -> bool:
        """Update statistics for a monitoring session"""
        async with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return False
            
            # Update session with statistics
            for key, value in statistics.items():
                if hasattr(session, key):
                    setattr(session, key, value)
            
            return True
    
    async def cleanup_old_sessions(self, max_age_days: int = 30) -> int:
        """Clean up old monitoring sessions"""
        async with self._lock:
            cutoff_time = datetime.now() - timedelta(days=max_age_days)
            old_sessions = [
                session_id for session_id, session in self._sessions.items()
                if session.start_time < cutoff_time
            ]
            
            for session_id in old_sessions:
                del self._sessions[session_id]
            
            return len(old_sessions)
    
    # Additional methods required by IMonitoringRepository interface
    async def save(self, session: MonitoringSession) -> MonitoringSession:
        """Save or update monitoring session (alias for create/update)"""
        async with self._lock:
            self._sessions[session.session_id] = session
            return session
    
    async def find_by_id(self, session_id: str) -> Optional[MonitoringSession]:
        """Find monitoring session by ID (alias for get_by_id)"""
        return await self.get_by_id(session_id)
    
    async def list_all(
        self, 
        limit: Optional[int] = None, 
        offset: int = 0
    ) -> List[MonitoringSession]:
        """List all monitoring sessions with pagination"""
        async with self._lock:
            sessions = list(self._sessions.values())
            
            # Apply offset
            if offset > 0:
                sessions = sessions[offset:]
            
            # Apply limit
            if limit is not None:
                sessions = sessions[:limit]
            
            return sessions
    
    async def find_by_status(self, status: str) -> List[MonitoringSession]:
        """Find monitoring sessions by status"""
        async with self._lock:
            return [
                session for session in self._sessions.values()
                if session.status == status
            ]
    
    async def find_by_roi(self, roi_id: str) -> List[MonitoringSession]:
        """Find monitoring sessions by ROI region ID (alias for get_by_roi_region)"""
        return await self.get_by_roi_region(roi_id)
    
    async def find_active_sessions(self) -> List[MonitoringSession]:
        """Find all active monitoring sessions (alias for get_active_sessions)"""
        return await self.get_active_sessions()
    
    async def find_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[MonitoringSession]:
        """Find monitoring sessions within date range (alias for get_sessions_in_range)"""
        return await self.get_sessions_in_range(start_date, end_date)
    
    async def find_completed_sessions(
        self, 
        max_age_days: Optional[int] = None
    ) -> List[MonitoringSession]:
        """Find completed monitoring sessions"""
        async with self._lock:
            completed = [
                session for session in self._sessions.values()
                if session.status in ['stopped', 'completed', 'error']
            ]
            
            if max_age_days is not None:
                cutoff_date = datetime.now() - timedelta(days=max_age_days)
                completed = [
                    session for session in completed
                    if session.start_time >= cutoff_date
                ]
            
            return completed
    
    async def get_roi_session_count(self, roi_id: str) -> int:
        """Get count of sessions for a specific ROI"""
        async with self._lock:
            count = sum(
                1 for session in self._sessions.values()
                if hasattr(session, 'roi_region_id') and session.roi_region_id == roi_id
            )
            return count
    
    async def get_total_monitoring_time(self) -> float:
        """Get total monitoring time across all sessions"""
        async with self._lock:
            total_time = 0.0
            for session in self._sessions.values():
                if hasattr(session, 'end_time') and session.end_time:
                    # For completed sessions, calculate actual duration
                    duration = (session.end_time - session.start_time).total_seconds()
                else:
                    # For active sessions, calculate current duration
                    duration = (datetime.now() - session.start_time).total_seconds()
                
                total_time += duration
            
            return total_time
    
    async def find_by_criteria(self, criteria: Dict[str, Any]) -> List[MonitoringSession]:
        """Find monitoring sessions matching criteria"""
        async with self._lock:
            sessions = list(self._sessions.values())
            
            # Filter by criteria
            for key, value in criteria.items():
                if key == 'status':
                    sessions = [s for s in sessions if s.status == value]
                elif key == 'roi_id':
                    sessions = [s for s in sessions if hasattr(s, 'roi_region_id') and s.roi_region_id == value]
                elif key == 'active':
                    if value:
                        sessions = [s for s in sessions if s.status == 'active']
                    else:
                        sessions = [s for s in sessions if s.status != 'active']
                elif key == 'limit':
                    sessions = sessions[:value]
                elif key == 'start_after':
                    sessions = [s for s in sessions if s.start_time >= value]
                elif key == 'start_before':
                    sessions = [s for s in sessions if s.start_time <= value]
            
            return sessions
