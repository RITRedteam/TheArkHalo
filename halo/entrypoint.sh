#!/bin/sh

function cleanup() {
    # Delete all the old interfaces
    echo "Deleting interfaces"
    python3 cleanup.py
}

trap 'cleanup' SIGTERM

"${@}" &
python3 haloGenerate.py
exec nginx -g "daemon off;" &

#Wait
wait $!
