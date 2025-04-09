#!/bin/bash

# Check for correct number of arguments
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <start_date> <end_date>"
    echo "Dates should be in YYYY-MM-DD format."
    exit 1
fi

start_date="$1"
end_date="$2"
script_to_run="process_day.sh"

# Validate the existence of the script to run
if [ ! -f "$script_to_run" ]; then
    echo "Error: Script '$script_to_run' not found."
    exit 1
fi

# Convert dates to seconds since epoch for comparison
start_sec=$(date -j -f "%Y-%m-%d" "$start_date" "+%s")
end_sec=$(date -j -f "%Y-%m-%d" "$end_date" "+%s")

# Check if start_date is before or equal to end_date
if [ "$start_sec" -gt "$end_sec" ]; then
    echo "Error: Start date must be before or equal to end date."
    exit 1
fi

# Loop through each day from start_date to end_date
current_date="$start_date"
while [ "$start_sec" -le "$end_sec" ]; do
    echo "Running process_day.sh for date: $current_date"
    bash "$script_to_run" "$current_date"  # Run process_day.sh with the current date as argument

    # Increment current_date by one day
    current_date=$(date -j -v+1d -f "%Y-%m-%d" "$current_date" "+%Y-%m-%d")
    start_sec=$(date -j -f "%Y-%m-%d" "$current_date" "+%s")
done