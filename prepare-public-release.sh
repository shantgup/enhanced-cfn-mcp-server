#!/bin/bash

# Enhanced CloudFormation MCP Server - Public Release Preparation Script
# This script removes internal/sensitive content before public GitHub release

set -e

echo "🧹 Preparing Enhanced CloudFormation MCP Server for public release..."

# Remove internal documentation
echo "📝 Removing internal documentation..."
rm -f docs/archive/BRAZIL_SETUP_GUIDE.md

# Update package metadata for public release
echo "📦 Updating package metadata..."
sed -i.bak 's|https://github.com/your-username/enhanced-cfn-mcp-server|https://github.com/shantgup/enhanced-cfn-mcp-server|g' pyproject.toml README.md CONTRIBUTING.md

echo ""
echo "✅ Public release preparation complete!"
echo "🎉 Ready for public GitHub release!"
