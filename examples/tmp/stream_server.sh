#!/bin/bash

# Create a named pipe
PIPE=/tmp/ws_pipe
rm -f "$PIPE"
mkfifo "$PIPE"

# Start a loop that writes 1..7 forever to the pipe
(
  while true; do
    for i in {1..7}; do
      echo "$i"
      sleep 1
    done
  done
) > "$PIPE" &

# Start websocat in server mode, reading from the named pipe
websocat -s 1234 < "$PIPE"