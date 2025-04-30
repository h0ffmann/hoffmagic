#!/bin/bash

# HoffMagic Blog Application Master Bootstrap Script
# This script runs all bootstrap scripts in sequence

set -e  # Exit on any error

echo "=== HoffMagic Blog Application Master Bootstrap ==="

# Run script1.sh (Initial Setup)
echo "Running script1.sh - Initial Setup..."
bash script1.sh

# Run script2.sh (Core Application Files)
echo "Running script2.sh - Core Application Files..."
bash script2.sh

# Run script3.sh (API Routes and Services)
echo "Running script3.sh - API Routes and Services..."
bash script3.sh

# Run script4.sh (Templates and Deployment Files)
echo "Running script4.sh - Templates and Deployment Files..."
bash script4.sh

# Run bootstrap_missing.sh (Missing Files)
echo "Running bootstrap_missing.sh - Creating Missing Files..."
bash bootstrap_missing.sh

echo "All bootstrap scripts have been executed successfully."
echo "HoffMagic blog application setup is complete!"
echo ""
echo "You can now run the application in development mode:"
echo "  python -m venv .venv"
echo "  source .venv/bin/activate"
echo "  pip install -e ."
echo "  uvicorn hoffmagic.main:app --reload"
echo ""
echo "Or using Docker:"
echo "  docker-compose up"
echo ""
echo "Happy blogging with HoffMagic!"
