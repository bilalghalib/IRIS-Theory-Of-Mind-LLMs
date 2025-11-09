#!/bin/bash
# Lint and format check script for Aperture

set -e  # Exit on error

echo "🔍 Running linters and formatters..."

echo ""
echo "1️⃣ Running ruff (linter)..."
ruff check . || exit 1

echo ""
echo "2️⃣ Running black (formatter check)..."
black --check . || exit 1

echo ""
echo "3️⃣ Running mypy (type checker)..."
mypy . --ignore-missing-imports || exit 1

echo ""
echo "✅ All checks passed!"
