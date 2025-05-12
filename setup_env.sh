#!/bin/bash

set -e

echo "🔧 Setting up environment..."

# 1. Create Python virtual environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created."
else
    echo "ℹ️ Virtual environment already exists."
fi

# 2. Activate the environment
source venv/bin/activate

# 3. Upgrade pip and install Python packages
pip install --upgrade pip
pip install mutagen

echo "✅ Python packages installed."

# 4. Install Homebrew if not already installed
if ! command -v brew &> /dev/null; then
    echo "🍺 Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo "✅ Homebrew already installed."
fi

# 5. Install audio tools via Homebrew
brew install ffmpeg shntool cuetools mac

# 6. Create symlink for cuetag if missing
if [ ! -f /usr/local/bin/cuetag ]; then
    ln -s "$(brew --prefix)/bin/cuetag" /usr/local/bin/cuetag
    echo "🔗 Created symlink for cuetag"
fi

echo "✅ All tools installed and ready!"
