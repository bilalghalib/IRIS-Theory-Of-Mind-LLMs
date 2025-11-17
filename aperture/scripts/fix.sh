#!/bin/bash
# Auto-fix formatting and linting issues

set -e

echo "🔧 Auto-fixing code issues..."

echo ""
echo "1️⃣ Running ruff with --fix..."
ruff check . --fix

echo ""
echo "2️⃣ Running black (formatter)..."
black .

echo ""
echo "✅ Auto-fix complete! Run ./scripts/lint.sh to verify."
