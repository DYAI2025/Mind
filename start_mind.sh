#!/bin/bash

# Mind System - Unified Startup Script
# Starts the complete Mind knowledge sharing system with one command

echo "🧠 Mind System - Unified Startup"
echo "=================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found"
    exit 1
fi

# Install dependencies if needed
if [ ! -d "venv" ] && [ ! -f ".deps_installed" ]; then
    echo "📦 Installing Python dependencies..."
    pip install -r requirements.txt
    touch .deps_installed
fi

# Default options
VOICE=""
DASHBOARD=""
TUNNEL=""
ALL=""
PORT="8000"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --voice)
            VOICE="--voice"
            shift
            ;;
        --dashboard)
            DASHBOARD="--dashboard"
            shift
            ;;
        --tunnel)
            TUNNEL="--tunnel"
            shift
            ;;
        --all)
            ALL="--all"
            shift
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --voice      Start voice server"
            echo "  --dashboard  Start dashboard server"
            echo "  --tunnel     Setup public tunnel"
            echo "  --all        Start all components"
            echo "  --port PORT  API server port (default: 8000)"
            echo "  --help, -h   Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                    # Start API server only"
            echo "  $0 --all             # Start everything"
            echo "  $0 --voice --tunnel  # Start API + voice + tunnel"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Run the Python startup script
exec python3 mind_unified_startup.py --port "$PORT" $VOICE $DASHBOARD $TUNNEL $ALL