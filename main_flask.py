"""
Flask-based ScreenAgent Application
Entry point for the Flask-based refactored ScreenAgent
"""
import os
import sys
import signal
from typing import Optional

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from src.api.flask_app import create_app


def main():
    """Main entry point for Flask-based ScreenAgent"""
    print("🚀 Starting ScreenAgent Flask Application...")
    
    # Create Flask app
    try:
        app = create_app()
        print("✅ Flask application created successfully")
    except Exception as e:
        print(f"❌ Failed to create Flask application: {e}")
        return 1
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Get configuration from environment or use defaults
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 8000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"🌐 Starting server on {host}:{port}")
    print(f"📚 Swagger documentation available at: http://{host}:{port}/docs/")
    print(f"🔍 Debug mode: {'ON' if debug else 'OFF'}")
    print("Press Ctrl+C to stop")
    
    try:
        # Run Flask development server
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True,
            use_reloader=False  # Disable reloader to avoid double initialization
        )
    except KeyboardInterrupt:
        print("\n🛑 Received keyboard interrupt, shutting down...")
    except Exception as e:
        print(f"❌ Server error: {e}")
        return 1
    
    print("✅ ScreenAgent stopped successfully")
    return 0


if __name__ == '__main__':
    sys.exit(main())
