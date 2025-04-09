#!/bin/bash

# Ensure the correct number of arguments is passed (just one date)
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 YYYY-MM-DD"
    exit 1
fi

# Store the date argument
DATE=$1
DIR_DATE=$(echo "$DATE" | sed 's/-//g')

cd Data
#echo "Downloading and pre-processing data for $DATE"
#sh download_a_date.sh $DATE

cd ../Pick
echo "Picking for $DATE"
python3 trigger_p_amp.py $DATE &
python3 trigger_s_amp.py $DATE &
wait

cd ../REAL
echo "Running REAL for $DATE"
perl runREAL_STALTA.pl $DATE

echo "Appending outputs to main output files"
cat catalog_sel.txt >> ./cat_output/catalog_sel.txt
cat phase_sel.txt >> ./cat_output/phase_sel.txt
cat hypolocSA.dat >> ./cat_output/hypolocSA.dat
cat hypophase.dat >> ./cat_output/hypophase.dat
cd ..


echo "End of script."