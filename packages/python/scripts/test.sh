#!/bin/bash

# Get short SHA in hex
SHORT_SHA=$(git rev-parse --short HEAD)
echo "Short SHA (hex): $SHORT_SHA"

# Convert to decimal and print
DECIMAL_SHA=$(printf "%u\n" 0x$SHORT_SHA)
echo "Short SHA (decimal): $DECIMAL_SHA"
