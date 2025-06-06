#!/bin/bash

echo "Checking for remaining merge conflict markers..."

# Search for merge conflict markers in all files
CONFLICTS=$(grep -r "<<<<<<< HEAD\|=======\|>>>>>>>" --include="*.*" .)

if [ -z "$CONFLICTS" ]; then
    echo "✅ No merge conflict markers found. All conflicts have been resolved!"
else
    echo "❌ Found merge conflict markers in the following files:"
    echo "$CONFLICTS"
fi