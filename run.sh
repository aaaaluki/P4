#!/bin/sh

# 0 true, else false
DO_FINAL=1
THRESHOLD_VARNAME="UMBRAL"

# Check arguments
[[ $# -lt 1 ]] && echo "Enter the feature as the first argument!" && exit 1

# Run all the training, classification and verification
for FEAT in "$@"; do
    # Set and display feature
    export FEAT=$1
    echo $FEAT"  ----------------------------------------"

    # Create logfile
    LOGFILE=run_spkid_$FEAT.log
    rm $LOGFILE 2> /dev/null
    touch $LOGFILE

    # Comment / Uncomment commands to run
    time run_spkid $FEAT | tee -a $LOGFILE
    time run_spkid train | tee -a $LOGFILE
    time run_spkid trainworld | tee -a $LOGFILE
    time run_spkid test | tee -a $LOGFILE
    time run_spkid verify | tee -a $LOGFILE
    time run_spkid verifyerr | tee -a $LOGFILE
    time run_spkid classerr | tee -a $LOGFILE

    # Change threshold and run finalclass and final verif
    [[ $DO_FINAL -ne 0 ]] && continue

    # For the threshold i'm assuming it will be one digit number followed
    # with many decimal places. So we'll only take 5 decimal places
    THRESHOLD=$(grep "THR:" $LOGFILE | cut -d " " -f 2 | head -c 7)

    # Find and replace old threshold with sed
    sed -i -e "s/$THRESHOLD_VARNAME=[\.0-9]* *# ${FEAT^^}/$THRESHOLD_VARNAME=$THRESHOLD  # ${FEAT^^}/g" $(readlink -f $(which run_spkid))

    # Run the final classification and verification
    time run_spkid finalclass | tee -a $LOGFILE
    time run_spkid finalverif | tee -a $LOGFILE

    head -1 $LOGFILE; tail -1 $LOGFILE
done
