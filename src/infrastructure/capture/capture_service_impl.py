"""
Capture Service Implementation
Simple implementation using chain of responsibility pattern
"""
import asyncio
from typing import Optional, Tuple, Dict, Any

from src.domain.interfaces.capture_service import ICaptureService, CaptureResult
from src.domain.value_objects.coordinates import Rectangle
from .capture_chain import CaptureChainBuilder


class CaptureServiceImpl(ICaptureService):
    """Implementation of capture service using capture chain"""
    
    def __init__(self):
        self._capture_chain = None
        self._initialized = False
    
    async def capture_full_screen(
        self, 
        monitor_id: Optional[int] = None
    ) -> CaptureResult:
        """Capture full screen screenshot"""
        if not self._initialized:
            if not self.initialize():
                return CaptureResult(False, error="Capture service not initialized")
        
        try:
            # Run capture in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            
            def capture_sync():
                return self._capture_chain.capture_full_screen()
            
            result = await loop.run_in_executor(None, capture_sync)
            
            if result.success and result.data:
                return CaptureResult(
                    success=True,
                    data=result.data,
                    metadata=result.metadata
                )
            else:
                return CaptureResult(
                    success=False,
                    error=result.error or "Unknown capture error"
                )
                
        except Exception as e:
            return CaptureResult(False, error=f"Capture error: {e}")
    
    async def capture_region(
        self, 
        region: Rectangle,
        monitor_id: Optional[int] = None
    ) -> CaptureResult:
        """Capture screenshot of specific region"""
        if not self._initialized:
            if not self.initialize():
                return CaptureResult(False, error="Capture service not initialized")
        
        try:
            # Convert Rectangle to ROI tuple
            roi = (region.left, region.top, region.right, region.bottom)
            
            # Run capture in thread pool
            loop = asyncio.get_event_loop()
            
            def capture_sync():
                return self._capture_chain.capture_roi(roi)
            
            result = await loop.run_in_executor(None, capture_sync)
            
            if result.success and result.data:
                return CaptureResult(
                    success=True,
                    data=result.data,
                    metadata=result.metadata
                )
            else:
                return CaptureResult(
                    success=False,
                    error=result.error or "Unknown capture error"
                )
                
        except Exception as e:
            return CaptureResult(False, error=f"Region capture error: {e}")
    
    async def capture_roi(
        self, 
        roi: Tuple[int, int, int, int]
    ) -> CaptureResult:
        """Capture screenshot of specific ROI coordinates"""
        if not self._initialized:
            if not self.initialize():
                return CaptureResult(False, error="Capture service not initialized")
        
        try:
            # Run capture in thread pool
            loop = asyncio.get_event_loop()
            
            def capture_sync():
                return self._capture_chain.capture_roi(roi)
            
            result = await loop.run_in_executor(None, capture_sync)
            
            if result.success and result.data:
                return CaptureResult(
                    success=True,
                    data=result.data,
                    metadata=result.metadata
                )
            else:
                return CaptureResult(
                    success=False,
                    error=result.error or "Unknown capture error"
                )
                
        except Exception as e:
            return CaptureResult(False, error=f"ROI capture error: {e}")
    
    def initialize(self) -> bool:
        """Initialize the capture service"""
        try:
            print("🔧 Initializing capture service...")
            builder = CaptureChainBuilder()
            
            # Check if we're in WSL
            import os
            is_wsl = False
            
            if 'WSL_DISTRO_NAME' in os.environ:
                is_wsl = True
                print("✓ Detected WSL environment: {}".format(os.environ.get('WSL_DISTRO_NAME')))
            else:
                try:
                    with open('/proc/version', 'r') as f:
                        content = f.read().lower()
                        if 'microsoft' in content or 'wsl' in content:
                            is_wsl = True
                            print("✓ Detected WSL environment from /proc/version")
                except Exception:
                    pass
            
            if is_wsl:
                print("ℹ️ Using WSL-specific capture methods")
            
            self._capture_chain = builder.build_chain()
            self._initialized = True
            print("✅ Capture service initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize capture service: {e}")
            return False
    
    def cleanup(self) -> None:
        """Clean up capture service resources"""
        try:
            if self._capture_chain:
                self._capture_chain.cleanup()
            self._initialized = False
        except Exception as e:
            print(f"⚠️  Error during capture service cleanup: {e}")
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get capabilities of the capture service"""
        if not self._initialized or not self._capture_chain:
            return {"initialized": False}
        
        try:
            return self._capture_chain.get_capabilities()
        except Exception as e:
            return {"error": str(e), "initialized": self._initialized}
