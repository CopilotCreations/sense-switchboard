#!/usr/bin/env python3
"""
Synesthesia Simulator - Application Entry Point

This script starts the Synesthesia Simulator web application.
It serves both the frontend and backend components.

Usage:
    python run.py [--host HOST] [--port PORT] [--debug]

Options:
    --host HOST    Host to bind to (default: 127.0.0.1)
    --port PORT    Port to bind to (default: 5000)
    --debug        Enable debug mode
"""

import argparse
import os
import sys

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from backend.server import create_app


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(
        description='Synesthesia Simulator - Multi-sensory web experience',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python run.py                    # Start with defaults (localhost:5000)
    python run.py --port 8080        # Start on port 8080
    python run.py --host 0.0.0.0     # Allow external connections
    python run.py --debug            # Enable debug mode
        """
    )
    
    parser.add_argument(
        '--host',
        default='127.0.0.1',
        help='Host to bind to (default: 127.0.0.1)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Port to bind to (default: 5000)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode'
    )
    
    args = parser.parse_args()
    
    # Create the Flask application
    app = create_app()
    
    # Print startup message
    print("=" * 60)
    print("  Synesthesia Simulator")
    print("  Multi-sensory web experience")
    print("=" * 60)
    print(f"\n  Starting server at http://{args.host}:{args.port}")
    print(f"  Debug mode: {'enabled' if args.debug else 'disabled'}")
    print("\n  Press Ctrl+C to stop the server\n")
    print("=" * 60)
    
    # Run the application
    try:
        app.run(host=args.host, port=args.port, debug=args.debug)
    except KeyboardInterrupt:
        print("\n\nShutting down server...")
        sys.exit(0)


if __name__ == '__main__':
    main()
