#!/bin/bash

# Jupiter MCP DXT Build Script
# This script builds the DXT extension file for distribution

set -e  # Exit on any error

echo "🚀 Building Jupiter MCP Desktop Extension (DXT)"
echo "================================================"

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: This script must be run from the jupiter-mcp root directory"
    exit 1
fi

# Check if dxt directory exists
if [ ! -d "dxt" ]; then
    echo "❌ Error: dxt directory not found. Please ensure the DXT structure is set up."
    exit 1
fi

# Get git hash for unique versioning
GIT_HASH=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
if [ "$GIT_HASH" = "unknown" ]; then
    echo "⚠️  Warning: Could not get git hash, using 'unknown'"
fi

# Get version from pyproject.toml
VERSION=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/' 2>/dev/null || echo "0.1.0")
if [ -z "$VERSION" ]; then
    echo "❌ Error: Could not extract version from pyproject.toml"
    exit 1
fi

echo "📦 Building DXT with git hash: $GIT_HASH"
echo "📋 Version: $VERSION"

# Change to dxt directory
cd dxt

# Check if dxt command is available
if ! command -v dxt &> /dev/null; then
    echo "❌ Error: dxt command not found. Installing..."
    if command -v npm &> /dev/null; then
        npm install -g @anthropic-ai/dxt
    else
        echo "❌ Error: npm not found. Please install Node.js and npm first."
        exit 1
    fi
fi

echo "🔨 Building DXT package..."

# Build the DXT package
if ! dxt pack; then
    echo "❌ Error: Failed to build DXT package"
    exit 1
fi

# Create filename with git hash
DXT_FILENAME="jupiter-mcp-${GIT_HASH}.dxt"

# Move and rename the generated file
if [ -f "dxt.dxt" ]; then
    mv dxt.dxt "../${DXT_FILENAME}"
    echo "✅ DXT built successfully: ${DXT_FILENAME}"
else
    echo "❌ Error: dxt.dxt not found after build"
    exit 1
fi

# Return to root directory
cd ..

# Get file size for reporting
if [ -f "${DXT_FILENAME}" ]; then
    FILE_SIZE=$(du -h "${DXT_FILENAME}" | cut -f1)
    echo ""
    echo "📊 Build Summary:"
    echo "   📁 File: ${DXT_FILENAME}"
    echo "   📏 Size: ${FILE_SIZE}"
    echo "   🔢 Version: ${VERSION}"
    echo "   🎯 Git Hash: ${GIT_HASH}"
    echo ""
    echo "🔍 Verifying DXT file..."

    # Show contents using unzip (DXT files are ZIP archives)
    if command -v unzip &> /dev/null; then
        echo "📋 Contents:"
        unzip -l "${DXT_FILENAME}" | grep -E '\.(py|json|md|png)$' | awk '{printf "        %8s  %s  %s   %s\n", $1, $2, $3, $4}'
    fi

    echo ""
    echo "🎉 Build complete! You can now distribute: ${DXT_FILENAME}"
    echo ""
    echo "📥 Installation instructions:"
    echo "   1. Download ${DXT_FILENAME}"
    echo "   2. Double-click to install in Claude Desktop"
    echo "   3. Configure with .env file or direct input"
    echo ""
    echo "📚 See dxt/README.md for detailed installation guide"
else
    echo "❌ Error: Failed to create ${DXT_FILENAME}"
    exit 1
fi

# Clean up any old DXT files (keep only the 3 most recent)
echo "🧹 Cleaning up old DXT files..."
ls -t jupiter-mcp-*.dxt 2>/dev/null | tail -n +4 | xargs -r rm -f
echo "   Kept 3 most recent DXT files"
