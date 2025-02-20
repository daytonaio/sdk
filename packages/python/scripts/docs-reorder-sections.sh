#!/bin/bash

# Check if a file argument is provided.
[ -z "$1" ] && echo "Usage: $0 <file.mdx>" && exit 1

FILE="$1"
TEMP_FILE=$(mktemp)       # Temporary file for front matter and introduction.
BODY_FILE=$(mktemp)       # Temporary file for the main body (sections).
LAST_SECTION_FILE=$(mktemp)  # Temporary file for the last section.
MIDDLE_FILE=$(mktemp)     # Temporary file for the remaining sections.

# Extract front matter and introduction (everything before the first anchor or section header).
awk '/^<a id=|^## / {exit} {print}' "$FILE" > "$TEMP_FILE"

# Extract the rest of the content (from the first anchor or section header to the end).
awk '/^<a id=|^## /,EOF' "$FILE" > "$BODY_FILE"

# Count the number of sections by matching lines starting with "## ".
SECTION_COUNT=$(grep -c "^## " "$BODY_FILE")
if [ "$SECTION_COUNT" -eq 0 ]; then
  echo "No sections found in the file!"
  rm -f "$TEMP_FILE" "$BODY_FILE"
  exit 1
fi

# If there's only one section, no reordering is necessary.
if [ "$SECTION_COUNT" -eq 1 ]; then
  echo "Only one section found, no reordering needed."
  cat "$TEMP_FILE" "$BODY_FILE" > "$FILE"
  rm -f "$TEMP_FILE" "$BODY_FILE"
  exit 0
fi

# Identify the starting line of the last section (using the last occurrence of a section header).
LAST_SECTION_START=$(grep -n "^## " "$BODY_FILE" | tail -n 1 | cut -d: -f1)

# Split the BODY_FILE:
#  - Everything before LAST_SECTION_START becomes the "middle" sections.
#  - Everything from LAST_SECTION_START to the end is the last section.
head -n $((LAST_SECTION_START - 1)) "$BODY_FILE" > "$MIDDLE_FILE"
tail -n +$LAST_SECTION_START "$BODY_FILE" > "$LAST_SECTION_FILE"

# Reconstruct the file:
#  1. Front matter and introduction.
#  2. The last section (moved to the top of the body).
#  3. The remaining sections.
{
  cat "$TEMP_FILE"
  cat "$LAST_SECTION_FILE"
  cat "$MIDDLE_FILE"
} > "$FILE"

# Cleanup temporary files.
rm -f "$TEMP_FILE" "$BODY_FILE" "$LAST_SECTION_FILE" "$MIDDLE_FILE"

echo "Successfully reordered sections in $FILE."
