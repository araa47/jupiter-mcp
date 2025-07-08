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

# Get version from pyproject.toml
VERSION=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/' 2>/dev/null || echo "0.1.0")
if [ -z "$VERSION" ]; then
    echo "❌ Error: Could not extract version from pyproject.toml"
    exit 1
fi

echo "📦 Building DXT for version: $VERSION"

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

# Return to root directory
cd ..

# Create the latest DXT file
LATEST_FILENAME="jupiter-mcp-latest.dxt"

# Move and rename the generated file
if [ -f "dxt/dxt.dxt" ]; then
    mv "dxt/dxt.dxt" "${LATEST_FILENAME}"
    echo "✅ DXT built successfully: ${LATEST_FILENAME}"
else
    echo "❌ Error: dxt.dxt not found after build"
    exit 1
fi

# Get file size for reporting
if [ -f "${LATEST_FILENAME}" ]; then
    FILE_SIZE=$(du -h "${LATEST_FILENAME}" | cut -f1)
    echo ""
    echo "📊 Build Summary:"
    echo "   📁 File: ${LATEST_FILENAME}"
    echo "   📏 Size: ${FILE_SIZE}"
    echo "   🔢 Version: ${VERSION}"
    echo ""
    echo "🔍 Verifying DXT file..."

    # Show contents using unzip (DXT files are ZIP archives)
    if command -v unzip &> /dev/null; then
        echo "📋 Contents:"
        unzip -l "${LATEST_FILENAME}" | grep -E '\.(py|json|md|png)$' | awk '{printf "        %8s  %s  %s   %s\n", $1, $2, $3, $4}'
    fi

    echo ""
    echo "🎉 Build complete! You can now distribute: ${LATEST_FILENAME}"
    echo ""
    echo "📥 Installation instructions:"
    echo "   1. Download ${LATEST_FILENAME}"
    echo "   2. Double-click to install in Claude Desktop"
    echo "   3. Configure with .env file"
    echo ""
    echo "📚 See dxt/README.md for detailed installation guide"
else
    echo "❌ Error: Failed to create ${LATEST_FILENAME}"
    exit 1
fi
