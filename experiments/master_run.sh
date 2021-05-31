#!/bin/bash
SECONDS=0
for mid in {1000..1002} # [a,b]
do
	for kf in {0..4} # [a,b]
	do
		config="--mid $mid --kf $kf"
		script="python train_model.py $config"
		echo "$script"
		#eval "$script"
	done
done
mins=$((SECONDS/60))
echo echo "Time Elapsed : ${mins} minutes"