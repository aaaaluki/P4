#!/bin/sh

[[ $# -lt 1 ]] && echo "Enter the feature as the first argument!" && exit 1

# Run all the training, classification and verification
for FEAT in "$@"; do
    export FEAT=$1
    echo $FEAT"  ----------------------------------------"
    time run_spkid $FEAT train trainworld test verify | tee run_spkid_$FEAT.log
    time run_spkid verifyerr classerr | tee -a run_spkid_$FEAT.log | tail
done
