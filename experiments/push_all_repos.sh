#!/bin/bash
# PUSH ALL!!! is a bash
strings=(
astro-lightcurves-classifier
astro-light-curveshandler
fuzzy-tools
fuzzy-torch
)
echo "PUSHING ALL GITS:"
for i in "${strings[@]}"; do
	echo ""
	echo ">>> $i"
	cd "$i"
	#ls
	git add .
	git commit -m "$1"
	git push origin master
	cd ..
done
