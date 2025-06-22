#!/bin/bash

# ScreenAgent React Frontend Setup Script
# This script sets up the React frontend development environment

set -e  # Exit on any error

echo "🚀 Setting up ScreenAgent React Frontend..."
echo "================================================"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    echo "   Visit: https://nodejs.org/"
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2)
REQUIRED_VERSION="18.0.0"

if ! printf '%s\n%s\n' "$REQUIRED_VERSION" "$NODE_VERSION" | sort -V -C; then
    echo "❌ Node.js version $NODE_VERSION is too old. Please upgrade to Node.js 18+."
    exit 1
fi

echo "✅ Node.js version: $NODE_VERSION"

# Navigate to frontend directory
FRONTEND_DIR="/home/alibina/repo/screenAgent/frontend"

if [ ! -d "$FRONTEND_DIR" ]; then
    echo "❌ Frontend directory not found: $FRONTEND_DIR"
    exit 1
fi

echo "📂 Navigating to frontend directory..."
cd "$FRONTEND_DIR"

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Check if installation was successful
if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully!"
else
    echo "❌ Failed to install dependencies. Please check the error messages above."
    exit 1
fi

# Create .env file if it doesn't exist
ENV_FILE="$FRONTEND_DIR/.env"
if [ ! -f "$ENV_FILE" ]; then
    echo "📝 Creating .env file..."
    cat > "$ENV_FILE" << EOL
# React Frontend Environment Variables
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000
EOL
    echo "✅ Created .env file with default settings"
fi

# Create a simple test script
TEST_SCRIPT="$FRONTEND_DIR/test-setup.js"
cat > "$TEST_SCRIPT" << 'EOL'
// Simple test to verify setup
console.log('🧪 Testing React frontend setup...');
console.log('✅ Node.js is working');
console.log('✅ npm dependencies are installed');
console.log('✅ Setup completed successfully!');
console.log('');
console.log('Next steps:');
console.log('1. Start the Python backend: cd .. && python main.py');
console.log('2. Start the React frontend: npm run dev');
console.log('3. Open http://localhost:3000 in your browser');
EOL

node "$TEST_SCRIPT"
rm "$TEST_SCRIPT"

echo ""
echo "🎉 React Frontend Setup Complete!"
echo "================================================"
echo ""
echo "📋 Next Steps:"
echo "1. Start the Python backend (in a separate terminal):"
echo "   cd /home/alibina/repo/screenAgent"
echo "   python main.py"
echo ""
echo "2. Start the React frontend (in this terminal):"
echo "   npm run dev"
echo ""
echo "3. Open your browser to:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo ""
echo "📚 Documentation:"
echo "   Setup Guide: /home/alibina/repo/screenAgent/docs/react_setup_guide.md"
echo "   Refactoring Plan: /home/alibina/repo/screenAgent/docs/frontend_refactoring_todo.md"
echo ""
echo "🛠️ Development Commands:"
echo "   npm run dev        - Start development server"
echo "   npm run build      - Build for production"
echo "   npm run lint       - Run linting"
echo "   npm run test       - Run tests"
echo ""
echo "Happy coding! 🚀"
