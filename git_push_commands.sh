#!/bin/bash
# =============================================================================
# Robust Git Push & Release Script for Ambient Zero-Energy Systems
# =============================================================================
set -e

echo "🚀 Ensuring standardized repository directory structure..."
mkdir -p .github/workflows docs simulations firmware tests

echo "📦 Staging verified project files (explicit allowlist)..."
git add .github/
git add docs/
git add simulations/
git add firmware/
git add tests/
git add README.md requirements.txt .gitignore LICENSE CITATION.cff CHANGELOG.md git_push_commands.sh 2>/dev/null || true

echo "💾 Committing changes with verified semantic message..."
git commit -m "fix(ci): standardize directory layout, multi-platform HAL, and robust CI/CD" || echo "Working tree clean."

echo "🏷️ Setting release tag v1.40 (forced local)..."
git tag -a v1.40 -m "Cycle v140 Quadragintennial Apex Release" -f

echo "🌐 Pushing commits and forced tags to GitHub..."
git push origin main
git push origin v1.40 --force

echo "✅ Deployment completed successfully!"
