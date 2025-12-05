#!/bin/sh

echo "Background scheduler started"

while true; do

    current_hour=$(date +%H)
    current_minute=$(date +%M)

    if [ "$current_hour" = "03" ]; then
        echo "[$(date)] Running flushexpiredtokens..."
        python manage.py flushexpiredtokens
        echo "[$(date)] Task completed"

        # wait until hour 03:00 is passed
        sleep 3600
    fi

    current_seconds_since_midnight=$((current_hour * 3600 + current_minute *60))
    # reminder: 24h = 86400 secs, 3h = 10800
    seconds_until_next_run=$((86400 - current_seconds_since_midnight + 10800))

    echo "[$(date)] Next run in approximately $((seconds_until_next_run / 3600)) hours"
    sleep $seconds_until_next_run
done

