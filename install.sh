#!/bin/bash
#
# Installation helper for Electrum Seed tools
# This script helps set up the environment correctly
#

set -e

echo "============================================================"
echo "Electrum Seed Tools - Installation Helper"
echo "============================================================"
echo ""

# Check if we're in an Electrum directory
if [ -d "electrum" ] && [ -f "electrum/mnemonic.py" ]; then
    echo "✓ Electrum directory structure detected"
    echo "  You're already in the right place!"
    echo ""
    
    # Check if tools are present
    if [ -f "electrum_seed_gen.py" ]; then
        echo "✓ Seed tools already installed"
        echo ""
        echo "You can run:"
        echo "  python3 electrum_seed_gen.py"
        echo "  python3 electrum_seed_recovery.py"
        echo "  python3 setup_check.py"
        exit 0
    else
        echo "✗ Seed tools not found"
        echo ""
        echo "Please copy the tools to this directory:"
        echo "  cp /path/to/Electrum-seed/*.py ."
        exit 1
    fi
fi

echo "Setting up Electrum with seed tools..."
echo ""

# Step 1: Clone Electrum if not present
if [ ! -d "electrum" ]; then
    echo "Step 1: Cloning Electrum..."
    git clone https://github.com/spesmilo/electrum.git
    echo "✓ Electrum cloned"
else
    echo "Step 1: Electrum directory exists"
fi
echo ""

# Step 2: Enter Electrum directory
cd electrum

# Step 3: Install Electrum
echo "Step 2: Installing Electrum..."
if command -v pip3 &> /dev/null; then
    pip3 install --user -e .
elif command -v pip &> /dev/null; then
    pip install --user -e .
else
    echo "✗ pip not found. Please install Python pip first."
    exit 1
fi
echo "✓ Electrum installed"
echo ""

# Step 4: Copy tools if this script is in Electrum-seed repo
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [ -f "$SCRIPT_DIR/electrum_seed_gen.py" ]; then
    echo "Step 3: Copying seed tools..."
    cp "$SCRIPT_DIR"/*.py .
    chmod +x *.py
    echo "✓ Tools copied"
else
    echo "Step 3: Please copy seed tools manually:"
    echo "  cp /path/to/Electrum-seed/*.py ."
    echo "  chmod +x *.py"
fi
echo ""

# Step 5: Verify installation
echo "Step 4: Verifying installation..."
if command -v python3 &> /dev/null; then
    python3 setup_check.py
else
    python setup_check.py
fi

echo ""
echo "============================================================"
echo "Setup complete!"
echo "============================================================"
echo ""
echo "You can now run:"
echo "  python3 electrum_seed_gen.py        # Generate/validate seeds"
echo "  python3 electrum_seed_recovery.py   # Recover mixed up seeds"
echo "  python3 batch_seed_test.py          # Batch test seeds"
echo ""
