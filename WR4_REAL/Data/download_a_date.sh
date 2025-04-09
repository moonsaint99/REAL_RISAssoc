#!/bin/bash

# Ensure the correct number of arguments is passed (just one date)
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 YYYY-MM-DD"
    exit 1
fi

# Store the date argument
DATE=$1
DIR_DATE=$(echo "$DATE" | sed 's/-//g')

cd vel

# Run the Python script with the date argument
echo "Running Python script with date: $DATE"
python3 iris_waveform_XH_vel.py $DATE

# After running Python script, run sac_csv_gen.sh
# Pass the dynamically formatted directory as the argument
echo "Running sac_csv_gen.sh with target directory: $DIR_DATE"
./sac_csv_gen.sh ./$DIR_DATE  # Adjust the path as necessary

# Run the first Perl script with the date argument
echo "Running first Perl script with date: $DATE"
perl SACH_O.pl $DATE

# Run the second Perl script with the date argument
#echo "Running second Perl script with date: $DATE"
#cd ..
#perl transferWA.pl $DATE