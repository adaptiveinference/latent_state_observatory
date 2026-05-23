#!/bin/bash

REPO=$(git rev-parse --show-toplevel)
echo $REPO

# Set up output directory
STUDY=$REPO/studies/STUDY_MLP_fixed_depth
DATE=$(date  +%Y.%m.%d_%H.%M%p)
OUTDIR=$STUDY/logs/$DATE
mkdir -p $OUTDIR


# Run experiment
python3 $STUDY/run.py --cached 0 --outdir $OUTDIR > $OUTDIR/run.log




