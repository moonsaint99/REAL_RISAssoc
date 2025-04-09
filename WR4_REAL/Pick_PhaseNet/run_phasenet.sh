#!/usr/bin/bash -w

#step 1#
#run phasenet (new version, July 2021)
#"conda activate phasenet" #manually do this in your command line
#make sure you have installed phasenet under this env
#to roughly estimate magnitude, here I include amplitude output using data afterremoving responses.
#If you use raw data, please re-calculate mag after you get event catalog.

echo "step 1: run PhaseNet"
python ../../src/PhaseNet/phasenet/predict.py --mode=pred --model_dir=../../src/PhaseNet/model/190703-214543 --data_dir=../Data/vel/20141128 --data_list=../Data/vel/20141128.csv --format=sac --amplitude --batch_size=1
#picks.csv was generated by phasenet

#step 2#
#separate P and S picks
echo "step 2: split P and S picks"
python picksplit.py


#step 3#
#create REAL format pick files
echo "Create REAL format pick files"
../../bin/pick2real -Ptemp.p -Stemp.s
rm temp.p temp.s
