#!/bin/bash

# Script to replace example ARNs with placeholders to avoid Code Defender issues

echo "Replacing example ARNs with placeholders..."

# Replace account IDs in ARNs with placeholder
find . -name "*.py" -o -name "*.md" | xargs sed -i '' 's/123456789012/ACCOUNT-ID/g'

# Replace specific example ARNs with placeholders
find . -name "*.py" -o -name "*.md" | xargs sed -i '' 's/arn:aws:cloudformation:us-east-1:123456789012:generatedtemplate\/abcdef12-3456-7890-abcd-ef1234567890/arn:aws:cloudformation:REGION:ACCOUNT-ID:generatedtemplate\/TEMPLATE-ID/g'

find . -name "*.py" -o -name "*.md" | xargs sed -i '' 's/arn:aws:cloudformation:us-east-1:ACCOUNT-ID:stack\/test-stack\/12345/arn:aws:cloudformation:REGION:ACCOUNT-ID:stack\/STACK-NAME\/STACK-ID/g'

# Keep AWS managed policy ARNs as they are (these are public and safe)
echo "Completed ARN replacement"

# Show what was changed
echo "=== Changes made ==="
git diff --name-only
