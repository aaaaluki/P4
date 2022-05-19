#!/bin/sh

[[ $# -lt 1 ]] && echo "Enter the feature as the first argument!" && exit 1

FINAL=0
if [ $# -ge 2 ]; then
    FINAL=${2^^}
    if [[ "FINALS" =~ ^$TYPE ]]; then
        FINAL=1
    fi
fi

# Run all the training, classification and verification
export FEAT=$1
time run_spkid $FEAT train trainworld test verify | tee run_spkid_$FEAT.log
time run_spkid verifyerr classerr | tee -a run_spkid_$FEAT.log | tail

[[ $FINAL -eq 1 ]] && time run_spkid finalclass finalverif

