#!/bin/bash
# iMessage Monitor for OpenClaw
# Continuously watches for new iMessages and processes them

while true; do
    echo "Starting iMessage monitoring..."
    imsg watch --chat-id 1 --attachments
    echo "iMessage monitor stopped, restarting in 5 seconds..."
    sleep 5
done